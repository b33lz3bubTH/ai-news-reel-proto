from src.plugins.scrapers.base import BaseScraper
from bs4 import BeautifulSoup


class NdtvNewsScraper(BaseScraper):
    """Scraper for NDTV News Articles"""

    def __init__(self):
        super().__init__("https://www.ndtv.com")

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")

        # Extract the headline
        el_headline_tag = soup.find("h1", {"itemprop": "headline"})
        headline = el_headline_tag.text if el_headline_tag else "No headline found"

        # Extract the article body div with itemprop="articleBody"
        el_article_body = soup.find("div", {"itemprop": "articleBody"})

        # Extract the first image inside this article body div
        img_tag = el_article_body.find("img") if el_article_body else None
        img_src = img_tag["src"] if img_tag else None

        # Join all <p> tags inside the article body to form the complete article text
        paragraphs = el_article_body.find_all("p") if el_article_body else []
        article_text = " ".join(p.text for p in paragraphs)

        article_data = {
            "headline": headline,
            "media": img_src,
            "article_text": article_text,
        }

        return article_data
