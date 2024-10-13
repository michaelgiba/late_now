from dataclasses import dataclass
from late_now.llm_util import prompt_walter
from late_now.plan_broadcast._types import ShowSegment
from late_now.plan_broadcast.segments._screen_writer import segment_from_walter_content


def _monologue_prompt(talking_points: list[str]) -> str:
    part_items = "\n".join(f"<point>{point}</point>" for point in talking_points)
    return f"""
    
    You are given a list of talking points as input and need to produce a monologue segment 
    which discusses them. This is in the middle of the show, not the intro or outro.
    Be extremely in character and unhinged as possible and but minimize political opinions:

    Input:
    <talking_points>
        <point>...</point>
    </talking_points>

    Output:
    ...casually ramble through the talking points that are most interesting to walter...
    ...walter is free to skip or ignore any points he finds boring and go off on tangents...

    Ok here is the input:
    <talking_points>
        {part_items}
    </talking_points>"""


@dataclass
class MonologueSegmentInput:
    talking_points: list[str]


def produce_segment(segment_input: MonologueSegmentInput) -> ShowSegment:
    prompt = _monologue_prompt(segment_input.talking_points)
    response = prompt_walter(
        prompt,
        temperature=1.18,
    )
    return segment_from_walter_content(
        source_material="\n".join(segment_input.talking_points),
        walter_generated_content=response,
    )
