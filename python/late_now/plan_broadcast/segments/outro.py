from late_now.llm_util import (
    prompt_walter,
)
from late_now.plan_broadcast._types import ShowSegment
from late_now.plan_broadcast.segments._screen_writer import segment_from_walter_content


def _outro_prompt() -> str:
    return """
    Your segments are ending, say some bizarre things before ending the show 
    on an unhinged note. You are Walter Spanks. """


def produce_segment() -> ShowSegment:
    prompt = _outro_prompt()
    response = prompt_walter(
        prompt,
        temperature=1.18,
    )
    return segment_from_walter_content(
        source_material="None. ",
        walter_generated_content=response,
    )
