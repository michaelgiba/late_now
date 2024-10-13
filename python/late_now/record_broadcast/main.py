import argparse
from ._types import (
    RecordBroadcastOptions,
    new_broadcast_context,
)
from ._scene_track import record_scene_track
from ._image_track import record_image_track
from ._audio_track import record_audio_track
from ._compositing import composite_scene


def _parse_args():
    parser = argparse.ArgumentParser(description="Record a broadcast")
    parser.add_argument(
        "--output-uri",
        type=str,
        help="URI to the output file path for the video",
        required=True,
    )
    parser.add_argument(
        "--input-tar-path",
        type=str,
        help="Path to the broadcast tar file",
        required=True,
    )
    args = parser.parse_args()
    return RecordBroadcastOptions(
        output_uri=args.output_uri,
        input_tar_path=args.input_tar_path,
    )


def main():
    options = _parse_args()

    with new_broadcast_context(options) as context:
        audio_track, subtitle_track = record_audio_track(context)
        composite_scene(
            context,
            scene_track=record_scene_track(context),
            image_track=record_image_track(context),
            audio_track=audio_track,
            subtitle_track=subtitle_track,
        )


if __name__ == "__main__":
    main()
