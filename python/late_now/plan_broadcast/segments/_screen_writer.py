import re
from late_now.plan_broadcast._types import (
    ShowSegment,
    SegmentDetailedScript,
    SegmentScriptLine,
    SequenceType,
)
from late_now.llm_util import prompt_screenwriter
import json

SOUND_EFFECTS = {
    "APPLAUSE",
    "LAUGHTER",
    "CROWD_AWW",
    "CROWD_OOH",
}
SOUND_EFFECTS_PATTERN = re.compile(
    r"\|(?P<sound_effect_type>.+)\((?P<duration_seconds>\d+)\)\|"
)


SCREENWRITER_SYSTEM_PROMPT = """
You are a screenwriter. You are responsible for creating a structured script for a show.
You are provided plain text content from a late night show and are responsible for reformatting
it into a structured script. Respond with the formatted script, change NOTHING about the content
of the script.

Each line of the output is either dialog or a placeholder for a sound effect. 
Dialog lines should be JSON data all on one line with the following format:

{{"speaker": "<name of the speaker>", "text": "*...insert character speech or tokens in backets like [cough]...*", "body_motion": "*describe the motion of the speaker's body. i.e moving hands.*"}}


Sound effect lines should be special lines with one of the following options:

|APPLAUSE(<num_seconds>)| - for audience applause
|CROWD_AWW(<num_seconds>)| - for audience 'aww' sound
|CROWD_OOH(<num_seconds>)| - for audience 'ooh' sound
|LAUGHTER(<num_seconds>)| - for audience laughter
    
Input:
{input_description}

Example Output:
|LAUGHTER(1)|
WALTER: Good evening, ladies and gentlemen.
|APPLAUSE(3)|
WALTER: We have a great show for you tonight.


Ok now I will provide the input, provide script as output and NO other commentary or acknowledgements.
"""


def _create_detailed_script(script_raw: str) -> SegmentDetailedScript:
    script_lines = []
    for line in script_raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        elif match := SOUND_EFFECTS_PATTERN.match(line):
            sound_effect_name = match.group("sound_effect_type")
            if sound_effect_name not in SOUND_EFFECTS:
                raise ValueError(f"Invalid sound effect: {sound_effect_name}")

            duration_seconds = int(match.group("duration_seconds"))
            script_lines.append(
                SegmentScriptLine(
                    line_type="sound",
                    content={
                        "sound_effect": sound_effect_name,
                        "duration_seconds": duration_seconds,
                    },
                )
            )
        elif line.startswith("{"):
            try:
                json_data = json.loads(line)
                speaker = json_data.get("speaker")
                text = json_data.get("text")
                motion = json_data.get("body_motion")
                if speaker is None or text is None:
                    raise ValueError("Invalid JSON line: {}".format(line))
                script_lines.append(
                    SegmentScriptLine(
                        line_type="dialog",
                        content={
                            "speaker": speaker,
                            "text": text,
                            "body_motion": motion,
                        },
                    )
                )
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON line: {line}")
        else:
            raise ValueError(f"Invalid line: {line}")

    return SegmentDetailedScript(lines=script_lines)


def segment_from_walter_content(
    *,
    source_material: str,
    walter_generated_content: str,
) -> ShowSegment:
    script_raw = prompt_screenwriter(
        walter_generated_content,
        screenwriter_system_prompt=SCREENWRITER_SYSTEM_PROMPT.format(
            input_description="...freeform plain text from the host..."
        ),
    )
    detailed_script = _create_detailed_script(script_raw)
    return ShowSegment(
        sequence_type=SequenceType.BROADCAST,
        source_material=source_material.to_dict(),
        detailed_script=detailed_script,
    )


def segment_from_rough_script(rough_script: str) -> ShowSegment:
    script_raw = prompt_screenwriter(
        rough_script,
        screenwriter_system_prompt=SCREENWRITER_SYSTEM_PROMPT.format(
            input_description="...rough script.."
        ),
    )
    detailed_script = _create_detailed_script(script_raw)
    return ShowSegment(
        sequence_type=SequenceType.BROADCAST,
        source_material=rough_script,
        detailed_script=detailed_script,
    )
