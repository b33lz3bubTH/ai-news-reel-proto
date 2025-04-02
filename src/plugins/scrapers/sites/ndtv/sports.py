from src.plugins.scrapers.base import BaseScraper
from bs4 import BeautifulSoup, Comment


class NdtvSportsScraper(BaseScraper):
    """Scraper for NDTV News Articles"""

    def __init__(self):
        super().__init__("https://www.ndtv.com")

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        headline_comment = soup.find_all(string=lambda text: isinstance(
            text, Comment) and "Story Headline" in text)
        h1_tag = headline_comment[0].find_next_sibling("h1")
        headline = (h1_tag.text).strip()

        img_tag = soup.find(
            string=lambda text: isinstance(text, Comment) and "Story Content"
            in text).find_next("div").find("img")
        media = img_tag["src"]

        # Find <!-- Story Text --> comment, go to its parent <div>, and extract all <p> tags
        story_text_comment = soup.find(string=lambda text: isinstance(
            text, Comment) and "Story Text" in text)
        parent_div = story_text_comment.find_parent("div")
        paragraphs = parent_div.find_all("p")

        # Extract and print the text of each <p> tag (article links)
        article_links = [p_tag.text.strip() for p_tag in paragraphs]

        article_data = {
            "headline": headline,
            "media": media,
            "article_text": article_links,
        }
        return article_data
