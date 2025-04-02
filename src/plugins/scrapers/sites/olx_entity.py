from src.plugins.scrapers.base import BaseScraper
from bs4 import BeautifulSoup


class OlxEntityScraper(BaseScraper):
    """Scraper for olx.in"""

    def __init__(self):
        super().__init__("https://olx.in")

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        domtree_el_medias = soup.select(".slick-list img")

        medias = [
            domel_media.get_attribute_list("src")
            for domel_media in domtree_el_medias
        ]

        details_section = soup.find("div", attrs={"data-aut-id": "itemParams"})
        details_dict = {}
        if details_section:
            key_elements = details_section.find_all(
                "span",
                attrs={"data-aut-id": lambda x: x and x.startswith("key_")})
            value_elements = details_section.find_all(
                "span",
                attrs={"data-aut-id": lambda x: x and x.startswith("value_")})
        for key_el, value_el in zip(key_elements, value_elements):
            key = key_el.text.strip()
            value = value_el.text.strip()
            details_dict[key.lower()] = value

        description_section = soup.find(
            "div", attrs={"data-aut-id": "itemDescriptionContent"})
        description = "\n".join(p.text.strip()
                                for p in description_section.find_all("p"))

        profile_card = soup.find("div", attrs={"data-aut-id": "profileCard"})
        profile_link_tag = profile_card.find("a", rel="nofollow")

        profile_name = profile_link_tag["title"]
        profile_link = profile_link_tag["href"]

        dom_el_price = soup.find("span", attrs={
            "data-aut-id": "itemPrice"
        }).text.strip()
        dom_el_description = soup.find("h1",
                                       attrs={
                                           "data-aut-id": "itemTitle"
                                       }).text.strip()
        dom_el_location = soup.find("div",
                                    attrs={
                                        "data-aut-id": "itemLocation"
                                    }).find("span").text.strip()
        dom_el_date_posted = soup.find("div",
                                       attrs={
                                           "data-aut-id": "itemCreationDate"
                                       }).find("span").text.strip()

        return {
            "medias": medias,
            "prop_description": description,
            "lister": {
                "profile": profile_link,
                "title": profile_name
            },
            "post": {
                "price": dom_el_price,
                "description": dom_el_description,
                "location": dom_el_location,
                "date_posted": dom_el_date_posted,
            },**details_dict
        }
