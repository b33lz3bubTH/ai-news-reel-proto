import requests
from abc import ABC, abstractmethod
from fake_useragent import UserAgent

class BaseScraper(ABC):
    """Abstract Base Scraper to define a contract for all scrapers."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = self.get_headers()

    def get_headers(self):
        """Returns headers to avoid IP bans"""
        ua = UserAgent()
        return {
            "User-Agent": ua.random,  # Randomized User-Agent
            "Accept-Language": "en-US,en;q=0.5",  # Language preference
            "Referer": "https://www.google.com",  # Avoid direct referrer issues
            "DNT": "1",  # Do Not Track
            "Connection": "keep-alive",
        }

    @abstractmethod
    def parse(self, html: str) -> list[dict]:
        """Abstract method for parsing data from HTML."""
        pass

    def fetch_page(self, url: str):
        """Fetches the HTML content of a page."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def run(self, url: str):
        """Fetch and parse the page."""
        html = self.fetch_page(url)
        if html:
            return self.parse(html)
        return None
