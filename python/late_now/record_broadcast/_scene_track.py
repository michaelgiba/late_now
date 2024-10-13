import os
import subprocess
from ._types import (
    RecordBroadcastContext,
    Track,
)

from late_now.rendering.main import render_blender
from late_now.record_broadcast._ffmpeg_util import probe_length_in_seconds


def _merge_frames_to_video(context: RecordBroadcastContext, frames_dir: str) -> str:
    scene_track_output_directory = os.path.join(context.track_storage_path(), "scene")
    os.makedirs(scene_track_output_directory, exist_ok=True)
    output_path = os.path.join(scene_track_output_directory, "output.webm")

    subprocess.run(
        [
            "ffmpeg",
            "-framerate",
            str(30),
            "-i",
            os.path.join(frames_dir, "frame_%04d.png"),
            "-c:v",
            "libvpx-vp9",
            "-b:v",
            "0",
            "-crf",
            "30",
            "-pix_fmt",
            "yuv420p",
            output_path,
        ]
    )

    # Delete all the PNG files in the frames directory
    png_files = os.path.join(frames_dir, "*.png")
    subprocess.run(["rm", png_files])

    return output_path


def record_scene_track(context: RecordBroadcastContext) -> Track:
    # create recording output dir if needed
    frames_output_dir = os.path.join(context.track_storage_path(), "scene")
    os.makedirs(frames_output_dir, exist_ok=True)

    render_blender(
        broadcast_root=context.broadcast_directory(),
        output_root=frames_output_dir,
        show_ui=True,
    )

    relative_path = _merge_frames_to_video(context, frames_output_dir)
    absolute_path = os.path.join(frames_output_dir, relative_path)

    return Track(
        absolute_path=absolute_path,
        track_type="video",
        duration_sec=probe_length_in_seconds(absolute_path),
    )
