from late_now.plan_broadcast._types import (
    ShowSegment,
    ResourceStagingArea,
    AudioGeneration,
)
import json
from dataclasses import dataclass, asdict
from late_now.plan_broadcast.packaging._animation_generation._blendshapes import (
    BlendshapeData,
    generate_blendshapes,
)
from late_now.plan_broadcast.packaging._animation_generation._joints import (
    generate_bvh_poses,
)


@dataclass(frozen=True)
class AnimationData:
    fps: int
    absolute_start_time_sec: float
    blendshape_data: BlendshapeData
    bvh_data_strings: list[str]


def animation_for_segment(
    segment: ShowSegment,
    staging_area: ResourceStagingArea,
    audio_generation: AudioGeneration,
) -> dict[str, str]:
    character_name_to_animation_path = {}
    speech_fragments = []
    for fragment in audio_generation.audio_fragments:
        if fragment.audio_type == "speech":
            speech_fragments.append(fragment)

    if len(speech_fragments) == 0:
        return character_name_to_animation_path

    animation_data = AnimationData(
        fps=30,
        absolute_start_time_sec=0.0,
        blendshape_data=generate_blendshapes(speech_fragments, fps=30),
        bvh_data_strings=[
            generate_bvh_poses(
                speech_fragments,
                audio_generation.total_duration_sec,
            )
        ],
    )
    animation_data_path = staging_area.animation_path(ext="json")

    with open(animation_data_path, "w") as f:
        json.dump(asdict(animation_data), f)

    return {"walter": staging_area.to_relative(animation_data_path)}
