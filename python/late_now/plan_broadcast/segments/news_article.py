from dataclasses import dataclass
from late_now.llm_util import (
    prompt_walter,
)
from late_now.plan_broadcast._types import ShowSegment
from late_now.plan_broadcast.segments._screen_writer import segment_from_walter_content
from late_now.plan_broadcast._content_queue import NewsArticle


NUM_WORDS = 100


def _single_news_article_segment_prompt(article_text: str) -> str:
    return f"""
    Comment the provided news article on it as a late night show host would. 
    Keep your response under {NUM_WORDS} words. 
    The commentary is zaney, wild, unpredictable and contemporary adult humor.
    Provide general summary and specific facts from the article combined with funny commentary.
    If the article is about politics, remain apolitical and joke about either possible view point.
    
    Output (plain text):
    ...first summarize what the article and context in a sentence or two...

    Ok here is the article details:
    {article_text}"""


@dataclass
class NewsArticleSegmentInput:
    article: NewsArticle


def produce_segment_from_news_input(
    segment_input: NewsArticleSegmentInput,
) -> ShowSegment:
    prompt = _single_news_article_segment_prompt(segment_input.article)
    response = prompt_walter(prompt, temperature=1.15)
    return segment_from_walter_content(
        source_material=segment_input.article,
        walter_generated_content=response,
    )
