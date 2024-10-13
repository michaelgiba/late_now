import datetime as dt
import newspaper
import requests
from dataclasses import dataclass


@dataclass
class NewsArticle:
    title: str
    published_date: dt.datetime
    text: str

    def to_dict(self):
        return {
            "title": self.title,
            "published_date": (
                self.published_date.isoformat()
                if self.published_date
                else dt.datetime.now().isoformat()
            ),
            "text": self.text,
        }


def _scrape_link(link: str):
    """Fetches news articles from the specified sources."""
    try:
        article = newspaper.article(link)
        return NewsArticle(
            title=article.title,
            published_date=article.publish_date,
            text=article.text,
        )
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles from {link}: {e}")


class ContentQueue:
    def __init__(self, article_links: list[str] = None):
        self.article_links = article_links or []

    def consume_news_article(self) -> NewsArticle:
        """Pulls a single news article from the queue."""
        if self.article_links:
            return _scrape_link(self.article_links.pop(0))
        else:
            raise IndexError("No news articles available in the queue.")

    def consume_news_articles(self, n: int) -> list[NewsArticle]:
        """Pulls multiple news articles from the queue."""
        if n <= 0:
            raise ValueError("Number of articles must be positive.")

        articles = []
        while n > 0 and self.article_links:
            articles.append(self.consume_news_article())
            n -= 1
        return articles
