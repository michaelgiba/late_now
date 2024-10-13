from late_now.plan_broadcast._types import (
    PackagedShowSegment,
    ShowSegment,
    ResourceStagingArea,
)
from late_now.plan_broadcast.packaging._image_generation import image_for_segment
from late_now.plan_broadcast.packaging._audio_generation import audio_for_segment
from late_now.plan_broadcast.packaging._animation_generation import (
    animation_for_segment,
)
import os
from late_now.llm_util import prompt_general_llm


def _make_title(show_segment: ShowSegment) -> str:
    prompt = f"""
        Given the following content from the weird late night show
        create a catchy title with no more than 6 words. Respond with the title and nothing else.
        
        Input: {show_segment.plain_text()!r}.
    """
    return prompt_general_llm(prompt)


def package_segment(
    show_segment: ShowSegment, staging_area: ResourceStagingArea
) -> PackagedShowSegment:
    title = _make_title(show_segment)
    audio_generation = audio_for_segment(show_segment, staging_area=staging_area)
    image_abs_path = image_for_segment(show_segment, staging_area=staging_area)
    character_name_to_animation_path = animation_for_segment(
        show_segment, staging_area=staging_area, audio_generation=audio_generation
    )

    return PackagedShowSegment(
        title=title,
        segment=show_segment,
        audio_generation=audio_generation,
        relative_image_path=os.path.relpath(image_abs_path, staging_area.tmpdir),
        character_name_to_relative_animation_path=character_name_to_animation_path,
    )
