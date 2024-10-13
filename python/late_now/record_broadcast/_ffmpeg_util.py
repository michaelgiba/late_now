import subprocess


def probe_length_in_seconds(absolute_path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            absolute_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return float(result.stdout)


def combine_frames_into_gif(
    frame_directory: str, output_file: str, framerate: int = 30
):
    if not output_file.lower().endswith(".gif"):
        output_file += ".gif"

    command = [
        "ffmpeg",
        "-framerate",
        str(framerate),
        "-i",
        f"{frame_directory}/frame_%d.png",
        "-filter_complex",
        "[0:v] split [a][b];[a] palettegen=reserve_transparent=on:transparency_color=ffffff [p];[b][p] paletteuse",
        "-loop",
        "0",
        output_file,
    ]

    try:
        result = subprocess.run(command, check=True, stderr=subprocess.PIPE, text=True)
        print(f"GIF created successfully: {output_file}")
        print(f"FFmpeg output:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed with return code: {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        raise RuntimeError("FFmpeg command failed. See error output above.")
