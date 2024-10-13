import os
import tempfile
import subprocess
from ._types import (
    RecordBroadcastContext,
    Track,
)
from late_now.record_broadcast._ffmpeg_util import probe_length_in_seconds


def _image_paths_and_durations(
    context: RecordBroadcastContext, broadcast_definition: dict
) -> list[tuple[str, float]]:
    image_path_and_duration_sec: tuple[str, float] = []
    for sequence in broadcast_definition["sequences"]:
        duration_sec = sequence["duration_sec"]
        image_path = sequence["parameters"]["image"]
        image_path_and_duration_sec.append(
            (
                os.path.join(context.broadcast_directory(), image_path),
                duration_sec,
            )
        )
    return image_path_and_duration_sec


def _video_from_images(
    image_paths_and_durations: list[tuple[str, float]], output_path: str
):
    with tempfile.TemporaryDirectory() as tmpdir:
        concat_file_path = os.path.join(tmpdir, "input.txt")

        # Write concat file content
        with open(concat_file_path, "w") as f:
            for image_path, duration in image_paths_and_durations:
                f.write(f"file '{image_path}'\n")
                f.write(f"duration {duration}\n")
                f.write(f"file '{image_path}'\n")  # Repeating the image file

        print(f"Concat file created at: {concat_file_path}")

        # FFmpeg command with concat demuxer and transparency preservation
        ffmpeg_args = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file_path,
            "-r",
            "30",  # Setting frame rate to 30 fps
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuva420p",  # Preserving transparency
            "-b:v",
            "80M",  # Bitrate setting
            "-auto-alt-ref",
            "0",  # Disable auto alt-ref frames
            output_path,
        ]

        # Run ffmpeg command with error checking
        try:
            subprocess.run(ffmpeg_args, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg command failed: {e}")

    return output_path


def record_image_track(context: RecordBroadcastContext) -> Track:
    image_paths_and_durations = _image_paths_and_durations(
        context, context.broadcast_definition()
    )

    track_output_dir = os.path.join(context.track_storage_path(), "images")
    os.makedirs(track_output_dir, exist_ok=True)
    track_output_path = os.path.join(track_output_dir, "images.webm")

    _video_from_images(image_paths_and_durations, track_output_path)

    return Track(
        absolute_path=track_output_path,
        track_type="video",
        duration_sec=probe_length_in_seconds(track_output_path),
    )
