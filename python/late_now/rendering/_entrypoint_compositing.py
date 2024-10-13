import bpy
import os
import json


def clear_all_sequences():
    print("Clearing existing sequences...")
    for sequence in bpy.context.scene.sequence_editor.sequences_all:
        bpy.context.scene.sequence_editor.sequences.remove(sequence)


def import_video(filepath):
    print(f"Importing video from {filepath}...")
    if not os.path.exists(filepath):
        print(f"Error: File does not exist: {filepath}")
        return None

    try:
        video_strip = bpy.context.scene.sequence_editor.sequences.new_movie(
            name="Video", filepath=filepath, channel=1, frame_start=1
        )
        print("Video imported successfully.")
        return video_strip
    except Exception as e:
        print(f"Error importing video: {str(e)}")
        return None


def import_audio(filepath):
    print(f"Importing audio from {filepath}...")
    if not os.path.exists(filepath):
        print(f"Error: File does not exist: {filepath}")
        return None

    try:
        audio_strip = bpy.context.scene.sequence_editor.sequences.new_sound(
            name="Audio", filepath=filepath, channel=2, frame_start=1
        )
        print("Audio imported successfully.")
        return audio_strip
    except Exception as e:
        print(f"Error importing audio: {str(e)}")
        return None


def set_render_settings(output_path):
    print("Setting render settings...")
    bpy.context.scene.render.fps = 30
    bpy.context.scene.render.resolution_x = 360
    bpy.context.scene.render.resolution_y = 812
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.image_settings.file_format = "FFMPEG"
    bpy.context.scene.render.ffmpeg.format = "MPEG4"
    bpy.context.scene.render.ffmpeg.codec = "H264"
    bpy.context.scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    bpy.context.scene.render.ffmpeg.audio_codec = "AAC"
    bpy.context.scene.render.ffmpeg.audio_bitrate = 192


def _setup_tv_video(image_track, final_frame_end):
    tv_imported_video = import_video(image_track["asset_path"])
    if not tv_imported_video:
        print("Failed to import video. Exiting.")
        return

    # Adjust image strip properties
    tv_imported_video.blend_type = "ALPHA_OVER"
    tv_imported_video.transform.offset_x = -76  # Adjust X position
    tv_imported_video.transform.offset_y = 200  # Adjust Y position

    # Use transform.scale instead of scale_x and scale_y
    tv_imported_video.transform.scale_x = 0.23  # Adjust X scale
    tv_imported_video.transform.scale_y = 0.23  # Adjust Y scale

    # Set the end frame of the image strip to match the video
    tv_imported_video.frame_final_end = final_frame_end
    return tv_imported_video


def _setup_subtitle_video(subtitle_track, final_frame_end):
    subtitle_strip = import_video(subtitle_track["asset_path"])
    if not subtitle_strip:
        print("Failed to import subtitle video. Exiting.")
        return

    # Set the end frame of the subtitle strip to match the video
    subtitle_strip.frame_final_end = final_frame_end

    # Move the subtitle track to a higher channel to ensure it's on top
    subtitle_strip.channel = 3

    return subtitle_strip


def _setup_audio(audio_track, final_frame_end):
    audio_imported = import_audio(audio_track["asset_path"])
    if not audio_imported:
        print("Failed to import audio. Exiting.")
        return

    # Set the audio strip to match the video
    audio_imported.frame_final_end = final_frame_end
    return audio_imported


def _load_compositing_index(composite_root) -> dict:
    compositing_index = os.path.join(composite_root, "index.json")
    if not os.path.exists(compositing_index):
        raise ValueError(
            f"Error: Compositing index file not found: {compositing_index}"
        )

    with open(compositing_index, "r") as f:
        return json.load(f)


def _setup_scene(scene_track):
    scene_imported_video = import_video(scene_track["asset_path"])
    if not scene_imported_video:
        print("Failed to import video. Exiting.")
        return
    return scene_imported_video


ENABLE_SUBTITLES = False


def main(
    *,
    composite_root: str,
    output_video_path: str,
):
    print("Starting script...")
    index_contents = _load_compositing_index(composite_root)
    scene_imported_video = _setup_scene(index_contents["scene_track"])
    _setup_tv_video(index_contents["image_track"], scene_imported_video.frame_final_end)
    if ENABLE_SUBTITLES:
        _setup_subtitle_video(
            index_contents["subtitle_track"], scene_imported_video.frame_final_end
        )
    _setup_audio(index_contents["audio_track"], scene_imported_video.frame_final_end)
    # Set the scene's end frame to match the video
    bpy.context.scene.frame_end = scene_imported_video.frame_final_end

    set_render_settings(output_video_path)

    # Set the scene to show the composited result
    for area in bpy.context.screen.areas:
        if area.type == "SEQUENCE_EDITOR":
            for space in area.spaces:
                if space.type == "SEQUENCE_EDITOR":
                    space.overlay_frame = True
                    space.preview_channels = 3  # Show both video and overlay

    # Adjust scene dimensions to match video
    bpy.context.scene.render.resolution_x = 360
    bpy.context.scene.render.resolution_y = 812

    print("Setup complete. You can now see the result in Blender's Video Sequencer.")
    print(f"The composited video will be saved to: {output_video_path}")

    # Render the animation
    print("Starting render...")
    bpy.ops.render.render(animation=True)

    print(f"Rendering complete. Output saved to: {output_video_path}")
    # Exit the Blender program
    import sys

    sys.exit(0)
