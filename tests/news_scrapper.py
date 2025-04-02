import sys
import os

# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.plugins.scrapers.sites.ndtv.latest import NdtvLatestScraper
from src.plugins.scrapers.sites.ndtv.article import NdtvNewsScraper
from src.plugins.scrapers.sites.ndtv.sports import NdtvSportsScraper


if __name__ == "__main__":
    #scrapper = NdtvLatestScraper()
    #data = scrapper.run("https://www.ndtv.com/latest#pfrom=home-ndtv_mainnavigation")

    #article = NdtvNewsScraper()

    #article_data = article.run("https://www.ndtv.com/india-news/fascinating-discovery-archaeologists-find-over-110-megaliths-in-kerala-see-pics-7986344")
    #print("article_data", article_data)
    #
    sports = NdtvSportsScraper()

    sports_data = sports.run("https://sports.ndtv.com/cricket/no-pilots-for-flight-david-warner-blasts-air-india-after-star-is-made-to-wait-for-hours-7986777")
    print("sports", sports_data)
