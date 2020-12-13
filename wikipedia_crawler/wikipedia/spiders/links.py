import scrapy
import logging
from ..items import WikipediaItem

class WikipediaSpide(scrapy.Spider):
	name = "wiki_spider"
	allowed_domains = ["en.wikipedia.org"]

	def start_requests(self):
		url = "https://en.wikipedia.org/wiki/Main_Page"

		yield scrapy.Request(url=url, callback=self.parse)

	def parse_page(self, response, links):
		page = WikipediaItem()

		articles = [link.replace("/wiki/", "") for link in links] # Remove "wiki" from string
		articles = set(articles) # Remove duplicates

		page['page'] = response.url.split("/")[-1]
		page['links'] = articles
		page['size'] = len(articles)

		return page

	def parse(self, response):
		links = response.css("a::attr(href)").re(r"^(?!\/wiki\/\S+:\S+|\/wiki\/\S+#\S+)(\/wiki\/\S+)")
		main_article = response.url.split("/")[-1]
		
		yield self.parse_page(response, links) 
		
		# self.log("Processed page {}".format(main_article), level=logging.INFO)

		for page in links:
			url = response.urljoin(page)
			if url is not None:
				yield response.follow(url, callback=self.parse)