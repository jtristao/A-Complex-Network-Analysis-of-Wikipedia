import logging
import scrapy
import re

from ..items import WikipediaItem
from scrapy import Spider, Request


class WikipediaCategoriesSpider(Spider):
    name = "wiki_categories"
    allowed_domains = ["en.wikipedia.org"]

    custom_settings = {"JOBDIR": None, "LOG_LEVEL": "INFO"}
    start_url = "https://en.wikipedia.org/wiki/Wikipedia:Contents/Categories"
    base_url = "https://en.wikipedia.org/wiki/Category:{page}"

    categories = {
        "General reference": 1,
        "Culture and the arts": 2,
        "Geography and places": 3,
        "Health and fitness": 4,
        "History and events": 5,
        "Human activities": 6,
        "Mathematics and logic": 7,
        "Natural and physical sciences": 8,
        "People and self": 9,
        "Philosophy and thinking": 10,
        "Religion and belief systems": 11,
        "Society and social sciences": 12,
        "Technology and applied sciences": 13,
    }

    def start_requests(self):
        main_category = getattr(self, "category", "")

        yield Request(self.start_url, cb_kwargs={"main_category": main_category})

    def parse(self, response, main_category):
        if not main_category in self.categories:
            raise scrapy.exceptions.CloseSpider("Invalid category.")

        box = (
            "color:black;opacity:1;border:0px solid #A3BFB1;border-bottom:0px solid #A3BFB1"
            ";;box-sizing:border-box;text-align:left;padding:1em;;background:#F5FFFA;margin"
            ":0 0 10px;vertical-align:top;border-top-width:1px;padding-top:.3em;-moz-border"
            "-radius:0;-webkit-border-radius:0;border-radius:0"
        )

        indice = self.categories[main_category]

        sub_categories = list()
        sub_categories += response.xpath(
            '(//div[@style="{}"])[{}]//*[contains(string(), "Main categories: ")]//@href'.format(
                box, indice
            )
        ).getall()
        sub_categories += response.xpath(
            '(//div[@style="{}"])[{}]//div[@class="hlist"]//@href'.format(box, indice)
        ).getall()

        for category in sub_categories:
            category = re.findall(":(.[^\s]+)", category)[0]

            yield Request(self.base_url.format(page=category), callback=self.parse_category)

    def parse_category(self, response):
        # Build item:
        #   Collect the article content
        #   Collect the links on the category page

        # Crawl the categories (Leaf nodes)

        # Recurse to other sub_categories

        pass
