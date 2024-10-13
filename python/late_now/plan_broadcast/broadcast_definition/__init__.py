from late_now.plan_broadcast._types import (
    BroadcastCameraCut,
    BroadcastDefintion,
    BroadcastParameters,
    PackagedShowSegment,
    ResourceStagingArea,
    SequenceDefinition,
    SequenceType,
    IntroParameters,
)
import json


def _broadcast_camera_cut(i):
    # TODO: Reenable this when compositing properly removes the TV
    # Panel for the persona shots.
    # if i == 0:
    #     return "fly_in"
    # elif i % 5 == 0:
    #     # choose randomly between side_left and side_right
    #     # return random.choice(["persona", "side_right"])
    #     return "persona"
    # else:
    return "main"


def _create_intro_sequence(
    packaged_segment: PackagedShowSegment,
    staging_area: ResourceStagingArea,
) -> SequenceDefinition:
    total_duration = packaged_segment.audio_generation.total_duration_sec
    return SequenceDefinition(
        type=SequenceType.INTRO,
        parameters=IntroParameters(
            text=packaged_segment.title,
            image=packaged_segment.relative_image_path,
            audio=packaged_segment.audio_generation.relative_audio_path,
        ),
        duration_sec=total_duration,
    )


def _create_broadcast_sequence(
    packaged_segment: PackagedShowSegment,
    staging_area: ResourceStagingArea,
) -> SequenceDefinition:
    length_of_audio = packaged_segment.audio_generation.total_duration_sec

    camera_cuts_and_durations = []
    for i, audio_fragment in enumerate(
        packaged_segment.audio_generation.audio_fragments
    ):
        camera_cut = _broadcast_camera_cut(i)
        camera_cuts_and_durations.append((camera_cut, audio_fragment.duration_sec))

    return SequenceDefinition(
        type=SequenceType.BROADCAST,
        parameters=BroadcastParameters(
            text=packaged_segment.title,
            image=packaged_segment.relative_image_path,
            audio=packaged_segment.audio_generation.relative_audio_path,
            character_to_animation=packaged_segment.character_name_to_relative_animation_path,
            full_text_transcript=packaged_segment.segment.plain_text(),
            camera_cuts=[
                BroadcastCameraCut(
                    camera=camera_name,
                    duration_sec=duration_sec,
                )
                for camera_name, duration_sec in camera_cuts_and_durations
            ],
        ),
        duration_sec=length_of_audio,
    )


def _packaged_segment_to_sequence(
    packaged_segment: PackagedShowSegment,
    staging_area: ResourceStagingArea,
) -> SequenceDefinition:
    if packaged_segment.segment.sequence_type == SequenceType.INTRO:
        return _create_intro_sequence(packaged_segment, staging_area)
    elif packaged_segment.segment.sequence_type == SequenceType.BROADCAST:
        return _create_broadcast_sequence(packaged_segment, staging_area)

    raise ValueError(f"Unknown sequence type: {packaged_segment.segment.sequence_type}")


def _packaged_segments_to_broadcast_definition(
    packaged_segments: list[PackagedShowSegment],
    staging_area: ResourceStagingArea,
) -> BroadcastDefintion:
    title = "Late Night with Walter Spanks"

    sequence_definitions = []
    for packaged_segment in packaged_segments:
        sequence_definitions.append(
            _packaged_segment_to_sequence(packaged_segment, staging_area)
        )

    return BroadcastDefintion(
        title=title,
        sequences=sequence_definitions,
    )


def create_broadcast_definition_bundle(
    packaged_segments: list[PackagedShowSegment],
    staging_area: ResourceStagingArea,
    output_tar_path: str,
) -> str:
    broadcast_definition = _packaged_segments_to_broadcast_definition(
        packaged_segments, staging_area
    )

    with open(staging_area.broadcast_definition_path(), "w") as f:
        json.dump(broadcast_definition.to_json(), f)

    staging_area.bundle(output_tar_path)
