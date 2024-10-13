from late_now.plan_broadcast._types import (
    ShowSegment,
    SegmentDetailedScript,
    SegmentScriptLine,
    SequenceType,
)


def produce_segment() -> ShowSegment:
    return ShowSegment(
        sequence_type=SequenceType.INTRO,
        source_material="",
        detailed_script=SegmentDetailedScript(
            lines=[
                SegmentScriptLine(
                    line_type="sound",
                    content={
                        "sound_effect": "INTRO_MUSIC",
                        "duration_seconds": 5.0,
                    },
                )
            ]
        ),
    )
