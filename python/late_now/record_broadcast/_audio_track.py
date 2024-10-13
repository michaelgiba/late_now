import os
import subprocess
from ._types import (
    RecordBroadcastContext,
    Track,
)
from PIL import Image, ImageDraw, ImageFont
import pysrt
import whisper
from whisper.utils import WriteSRT
from late_now.record_broadcast._ffmpeg_util import (
    probe_length_in_seconds,
    combine_frames_into_gif,
)


def _concat_audio_ffmpeg(audio_files, output_file):
    audio_inputs = [term for file in audio_files for term in ["-i", file]]

    audio_channels = "".join(f"[{i}:0]" for i in range(len(audio_files)))
    # "[0:0][1:0]",
    command = [
        "ffmpeg",
        *audio_inputs,
        "-filter_complex",
        f"{audio_channels}concat=n={len(audio_files)}:v=0:a=1[out]",
        "-map",
        "[out]",
        "-ac",
        "1",
        output_file,
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg command failed: {e.returncode} - {e.stderr}")


def _concat_audio_tracks(context: RecordBroadcastContext) -> Track:
    definition = context.broadcast_definition()

    audio_files = []
    for sequence in definition["sequences"]:
        audio_parameter = sequence["parameters"]["audio"]
        audio_file = os.path.join(context.broadcast_directory(), audio_parameter)
        audio_files.append(audio_file)

    # Merge all audio files into one
    output_output_file = os.path.join(context.track_storage_path(), "full_audio.wav")
    _concat_audio_ffmpeg(audio_files, output_output_file)

    return Track(
        output_output_file, "audio", probe_length_in_seconds(output_output_file)
    )


# Parse the SRT file
def parse_srt(file_path):
    subs = pysrt.open(file_path)
    return [(sub.start.to_time(), sub.end.to_time(), sub.text) for sub in subs]


def _get_srt_data_from_track(
    context: RecordBroadcastContext, audio_track: Track, full_text_transcript: str
) -> str:
    whisper.load_model("base")
    model = whisper.load_model("base")
    result = model.transcribe(
        audio_track.absolute_path,
        initial_prompt=full_text_transcript,
        word_timestamps=True,
    )

    subtitles_dir = os.path.join(context.track_storage_path(), "subtitles")
    os.makedirs(subtitles_dir, exist_ok=True)

    files_in_dir = os.listdir(subtitles_dir)

    WriteSRT(
        subtitles_dir,
    )(
        result,
        audio_track.absolute_path,
        highlight_words=True,
        max_line_width=16,
        max_line_count=1,
    )

    files_in_dir_after = os.listdir(subtitles_dir)
    new_file = list(set(files_in_dir_after) - set(files_in_dir))[0]

    return os.path.join(subtitles_dir, new_file)


SCREEN_WIDTH = 376
SCREEN_HEIGHT = 812
HIGHLIGHT_COLOR = (255, 0, 0, 255)
FONT = ImageFont.truetype(
    "/usr/share/fonts/opentype/cantarell/Cantarell-ExtraBold.otf", 32
)
LEFT_MARGIN = 45
SUBTITLE_Y = 500
WORD_SPACE = 10
FPS = 30


def _render_text_frame(text, output_path: str):
    image = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 255, 0, 0))
    draw = ImageDraw.Draw(image)

    words = text.split(" ")
    current_position = LEFT_MARGIN

    for word in words:
        if word.startswith("<u>") and word.endswith("</u>"):
            word = word.removeprefix("<u>").removesuffix("</u>")
            draw.text(
                (current_position, SUBTITLE_Y), word, fill=HIGHLIGHT_COLOR, font=FONT
            )
        else:
            draw.text((current_position, SUBTITLE_Y), word, fill="white", font=FONT)

        # Use textbbox to get the word's width
        bbox = draw.textbbox((0, 0), word, font=FONT)
        word_width = bbox[2] - bbox[0]  # Calculate width from the bounding box

        # Move to the next word's position
        current_position += word_width + WORD_SPACE

    # Save the resulting image
    image.save(output_path)


def _time_to_milliseconds(time_obj):
    # Convert a datetime.time object to milliseconds
    return (
        time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    ) * 1000 + time_obj.microsecond // 1000


def _subtitle_track_from_audio_track(
    context: RecordBroadcastContext,
    audio_track: Track,
    full_text_transcript: str,
) -> Track:
    srt_file_path = _get_srt_data_from_track(context, audio_track, full_text_transcript)
    srt_file_data = parse_srt(srt_file_path)

    frame_number = 0

    sub_overlay_dir = os.path.join(context.track_storage_path(), "subtitle_overlay")
    os.makedirs(sub_overlay_dir, exist_ok=True)

    for start, end, text in srt_file_data:
        # Convert start and end time to milliseconds
        start_ms = _time_to_milliseconds(start)
        end_ms = _time_to_milliseconds(end)

        # Calculate duration in milliseconds
        duration_ms = end_ms - start_ms

        # Calculate number of frames for this subtitle (duration in ms converted to frames)
        num_frames = int((duration_ms / 1000) * FPS)

        for _ in range(num_frames):
            frame_path = os.path.join(sub_overlay_dir, f"frame_{frame_number}.png")
            _render_text_frame(text, frame_path)
            frame_number += 1

    overlay_output = os.path.join(sub_overlay_dir, "subtitles.gif")

    combine_frames_into_gif(sub_overlay_dir, overlay_output)
    return Track(overlay_output, "video", probe_length_in_seconds(overlay_output))


def record_audio_track(context: RecordBroadcastContext) -> tuple[Track, Track]:
    full_text_transcript_parts = []
    for sequence in context.broadcast_definition()["sequences"]:
        if "full_text_transcript" in sequence["parameters"]:
            full_text_transcript_parts.append(
                sequence["parameters"]["full_text_transcript"]
            )

    audio_track = _concat_audio_tracks(context)

    subtitle_track = _subtitle_track_from_audio_track(
        context, audio_track, "\n".join(full_text_transcript_parts)
    )
    return audio_track, subtitle_track
