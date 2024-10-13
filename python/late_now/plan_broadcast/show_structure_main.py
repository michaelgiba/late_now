import json
import argparse
from typing import List

from late_now.plan_broadcast._types import ShowSegment
from late_now.plan_broadcast.segments import (
    news_article,
    ContentQueue,
    segment_from_rough_script,
)


def _segments_from_news_articles(article_links: List[str]) -> List[ShowSegment]:
    content_queue = ContentQueue(article_links=article_links)
    show_structure = []
    for article_text in content_queue.consume_news_articles(1):
        print(article_text)
        show_structure.append(
            news_article.produce_segment_from_news_input(
                news_article.NewsArticleSegmentInput(article_text)
            )
        )
    return show_structure


def create_show_structure(args):
    show_structure = []
    if args.article_links:
        show_structure.extend(_segments_from_news_articles(args.article_links))
    if args.rough_script_path:
        with open(args.rough_script_path, "r") as script_file:
            rough_script = script_file.read()
        show_structure.append(segment_from_rough_script(rough_script))

    # Write show structure to output file
    with open(args.output_structure_path, "w") as f:
        json.dump([segment.to_dict() for segment in show_structure], f)


def _parse_args():
    parser = argparse.ArgumentParser(description="Create show structure")
    parser.add_argument(
        "--article-links",
        type=str,
        nargs="+",
        help="Links to articles to include in the broadcast",
    )
    parser.add_argument(
        "--rough-script-path",
        type=str,
        help="Path to the rough script file",
    )
    parser.add_argument(
        "--output-structure-path",
        type=str,
        required=True,
        help="Path to output the show structure",
    )
    args = parser.parse_args()

    if not args.article_links and not args.rough_script_path:
        parser.error("Either --article-links or --rough-script-path must be provided")

    return args


def main():
    args = _parse_args()
    create_show_structure(args)


if __name__ == "__main__":
    main()
