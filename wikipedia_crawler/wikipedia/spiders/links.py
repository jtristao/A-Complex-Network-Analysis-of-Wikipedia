import scrapy
import json
import os
import logging
from scrapy.spiders import  Rule
from scrapy.linkextractors import LinkExtractor

class WikipediaSpide(scrapy.Spider):
	name = "wiki_spider"
	allowed_domains = ["en.wikipedia.org"]

	def start_requests(self):
		url = "https://en.wikipedia.org/wiki/Main_Page"

		if not os.path.exists("Articles"):
			os.makedirs("Articles")

		yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		links = response.css("a::attr(href)").re(r"^(?!\/wiki\/\S+:\S+|\/wiki\/\S+#\S+)(\/wiki\/\S+)")

		articles = [link.replace("/wiki/", "") for link in links] # Remove "wiki" from string
		articles = set(articles) # Remove duplicates

		page = dict()
		page["articles"] = list(articles) # Json doesnt serialize sets
		page["size"] = len(articles)

		main_article = response.url.split("/")[-1]
		filename = "Articles/" + main_article + ".txt"
		with open(filename, "w") as file_pointer:
			json.dump(page, file_pointer)

		self.log("Processed page {} ({})".format(main_article, len(articles)), level=logging.INFO)

		for page in links:
			url = response.urljoin(page)
			if url is not None:
				yield response.follow(url, callback=self.parse)