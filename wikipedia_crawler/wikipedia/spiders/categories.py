import logging
import scrapy
import re
import requests
import json

from ..items import WikipediaItem
from scrapy import Spider, Request
from lxml import html


class WikipediaCategoriesSpider(Spider):
    name = "wiki_categories"
    allowed_domains = ["en.wikipedia.org"]

    custom_settings = {"JOBDIR": "Categories Cache", "LOG_LEVEL": "INFO"}

    start_url = "https://en.wikipedia.org/wiki/Wikipedia:Contents/Categories"
    base_url = "https://en.wikipedia.org"
    api_url = (
        "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&"
        "exlimit=max&explaintext&titles={page}&redirects="
    )

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

            yield Request(self.base_url + "/wiki/Category:" + category, callback=self.parse_page)
            break

    def parse_page(self, response, level=0):
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        page_data = self.collect_page(response)

        is_leaf = "article" in page_data
        if not is_leaf:
            for category in page_data["links"]:
                print("\t" * level, self.base_url + "/wiki/" + category)

                yield Request(
                    self.base_url + "/wiki/" + category,
                    callback=self.parse_page,
                    cb_kwargs={"level": level + 1},
                )

                break

        yield page_data

    def collect_page(self, response):
        item = WikipediaItem()

        item["page"] = response.url.split("/")[-1]

        if "Category" in item["page"]:
            item["links"] = self.__get_category_links(response)
            item["size"] = self.__get_category_size(response)
        else:
            item["links"] = self.__get_article_links(response)
            item["size"] = len(item["links"])
            item["article"] = self.__get_article(response, item["page"])

        return item

    def __get_article(self, response, page_name):
        data = requests.get(self.api_url.format(page=page_name))
        data = json.loads(data.text)

        content = data.get("query").get("pages")
        key = list(content.keys())[0]

        article = content.get(key).get("extract")

        return article

    def __get_article_links(self, response):
        links = response.css("a::attr(href)").re(
            r"^(?!\/wiki\/\S+:\S+|\/wiki\/\S+#\S+)\/wiki\/(\S+)"
        )

        return links

    def __get_category_links(self, response):
        sub_categories = response.xpath('//div[@id="mw-subcategories"]//@href').re("/wiki/(\w+:.+)")
        categories = response.xpath('//div[@id="mw-pages"]//@href').re("/wiki/(.+)")

        next_page = response.xpath('//div[@id="mw-pages"]/a/@href').get()
        if next_page:
            resp = requests.get(self.base_url + next_page)
            selector = html.fromstring(resp.content)

            links = selector.xpath('//div[@id="mw-pages"]//@href')
            links = [link.replace("/wiki/", "") for link in links]

            categories += links

        to_remove = "Wikipedia:FAQ/Categorization#Why_might_a_category_list_not_be_up_to_date?"
        if to_remove in categories:
            categories.remove(to_remove)

        return sub_categories + categories

    def __get_category_size(self, response):
        sub_category_cnt = response.xpath('//div[@id="mw-subcategories"]//p').re(
            "out of[a-z A-Z]+(\d+)"
        )
        if sub_category_cnt:
            sub_category_cnt = int(sub_category_cnt[0])
        else:
            if response.xpath('//div[@id="mw-subcategories"]//p'):
                sub_category_cnt = 1
            else:
                sub_category_cnt = 0

        category_cnt = response.xpath('//div[@id="mw-pages"]//p').re("out of[a-z A-Z]+(\d+)")
        if category_cnt:
            category_cnt = int(category_cnt[0])
        else:
            category_cnt = 0

        return sub_category_cnt + category_cnt


# Comentar
# Documentar
# Testar

# Problems with repeated requests