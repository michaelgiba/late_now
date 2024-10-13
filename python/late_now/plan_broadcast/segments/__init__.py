from enum import Enum, auto
from late_now.plan_broadcast.segments import (
    monologue,
    news_article,
    outro,
    intro,
)
from late_now.plan_broadcast._content_queue import ContentQueue
from late_now.plan_broadcast.segments._screen_writer import segment_from_rough_script


class SegmentType(Enum):
    INTRO = auto()
    NEWS_ARTICLE = auto()
    MONOLOGUE = auto()
    OUTRO = auto()


__all__ = [
    "ContentQueue",
    "monologue",
    "news_article",
    "outro",
    "intro",
    "segment_from_rough_script",
    "SegmentType",
]
