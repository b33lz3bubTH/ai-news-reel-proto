from src.plugins.scrapers.base import BaseScraper
from bs4 import BeautifulSoup

class NinetyNineAcresScraper(BaseScraper):
    """Scraper for 99acres"""

    def __init__(self):
        super().__init__("https://www.99acres.com")

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        sections = soup.select(".pageComponent > section")

        property_listings = []

        for section in sections:
            fields = {
                "title": "resBuy__propertyHeading",
                "location": "resBuy__locationName",
                "furnishing": "resBuy__furnished",
                "price": "resBuy__priceValWrap span",
                "area": "resBuy__area1Type",
                "deposit": "resBuy__area2TypePg",
                "description": "resBuy__descText",
                "posted_date": "resBuy__pbL1 span",
                "posted_by": "resBuy__pbL2",
            }

            # Extract data dynamically
            property_details = {}
            for key, class_name in fields.items():
                element = section.select_one(f".{class_name}")  # Select using the class name
                property_details[key] = element.get_text(strip=True) if element else "N/A"

            #property Link
            prop_href = section.find("a", class_="resBuy__propertyHeading")
            property_link = prop_href.get_attribute_list("href") if prop_href else "N/A"

            medias = section.select("img")
            property_details["medias"] = [img.get_attribute_list("src") for img in medias]

            property_details["link"] = property_link[0]
            property_listings.append(property_details)

        return property_listings
