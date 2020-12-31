# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WikipediaItem(scrapy.Item):
    # define the fields for your item here like:

    page = scrapy.Field()  # str: Page name
    links = scrapy.Field()  # list: list of links
    size = scrapy.Field()  # int: number of links
    article = scrapy.Field()  # dict: Page content
