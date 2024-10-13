import os
import json
from ._types import (
    RecordBroadcastContext,
    Track,
)
from late_now.record_broadcast._ffmpeg_util import probe_length_in_seconds
from late_now.rendering.main import composite_blender


def _write_compositing_plan(
    context: RecordBroadcastContext,
    composite_root: str,
    scene_track: Track,
    image_track: Track,
    audio_track: Track,
    subtitle_track: Track,
):
    index_path = os.path.join(composite_root, "index.json")
    index_contents = {
        "scene_track": {
            "duration_sec": scene_track.duration_sec,
            "asset_path": scene_track.absolute_path,
        },
        "image_track": {
            "duration_sec": image_track.duration_sec,
            "asset_path": image_track.absolute_path,
        },
        "audio_track": {
            "duration_sec": audio_track.duration_sec,
            "asset_path": audio_track.absolute_path,
        },
        "subtitle_track": {
            "duration_sec": subtitle_track.duration_sec,
            "asset_path": subtitle_track.absolute_path,
        },
    }
    with open(index_path, "w") as f:
        json.dump(index_contents, f)


def composite_scene(
    context: RecordBroadcastContext,
    scene_track: Track,
    image_track: Track,
    audio_track: Track,
    subtitle_track: Track,
) -> Track:
    # create recording output dir if needed
    composite_root = os.path.join(context.track_storage_path(), "compositing")
    # Make dir
    os.makedirs(composite_root, exist_ok=True)

    _write_compositing_plan(
        context, composite_root, scene_track, image_track, audio_track, subtitle_track
    )

    composite_blender(
        composite_root=composite_root,
        output_video_path=context.options.output_uri,
    )
    return Track(
        absolute_path=context.options.output_uri,
        track_type="video",
        duration_sec=probe_length_in_seconds(context.options.output_uri),
    )
