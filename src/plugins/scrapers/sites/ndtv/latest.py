from src.plugins.scrapers.base import BaseScraper
from bs4 import BeautifulSoup, Comment


class NdtvLatestScraper(BaseScraper):
    """Scraper for ndtv latest"""

    def __init__(self):
        super().__init__("https://www.ndtv.com")

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        el_articles = soup.select(".NwsLstPg-a-li")

        articles = []

        for el_article in el_articles:
            # Find the first image inside the <li> and extract the src
            img_tag = el_article.find("img")
            img_src = img_tag["src"] if img_tag else None

            # Extract the article link from <a> inside <h2>
            h2_tag = el_article.find("h2")
            a_tag = h2_tag.find("a") if h2_tag else None
            article_link = a_tag["href"] if a_tag else None
            article_title = a_tag.get_text(strip=True) if a_tag else None

            # Find the <nav> tag inside the <li> and get the date from the first <li> inside <ul>
            nav_tag = el_article.find("nav")
            date = None
            if nav_tag:
                first_li = nav_tag.find("ul").find("li") if nav_tag.find(
                    "ul") else None
                date = first_li.get_text(strip=True) if first_li else None

            # Store the extracted data in a dictionary
            articles.append({
                "image": img_src,
                "link": article_link,
                "title": article_title,
                "date": date
            })

        return [article for article in articles if article.get("link")]
