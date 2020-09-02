# A Complex Network Analysis of Wikipedia

A research project on Wikipedia article's structure and properties. For that, we model Wikipedia as a graph, such that every article is a node and every hyperlink between pages is an edge. We are initially interested in statistical properties such as degree distribution, average connectivity, transitivity, assortativity, diameter, etc. In a second moment, we are looking at preferential attachment and growth, relationships between fields of knowledge and clusters in the graph, among other aspects.

This project is based on the following papers:

    - Preferential attachment in the growth of social networks: The internet encyclopedia Wikipedia 
    (DOI: https://doi.org/10.1103/PhysRevE.74.036116)
    
    - Emergence of Scaling in Random Networks 
    (DOI: 10.1126/science.286.5439.509 )

    - The diameter of the world wide web 
    (DOI: 10.1038/43601)


## Crawling Wikipedia

Our goal is to capture the largest possible portion of Wikipedia's [6,151,996](https://en.wikipedia.org/wiki/Wikipedia:Statistics) article's written in English, as well as the links between then.

Every page has its default content: the menu, about Wikipedia section, options to contribute, tools, language options, and main content. There are different kinds of content as article, talk page, redirects, media file, category, gadget, template, etc. We are going to split those pages into two groups: articles and non-articles.

Looking at the page's Html and the links structure, the articles page follows the format ``https://en.wikipedia.org/wiki/ARTICLE_NAME``, where ARTICLE_NAME is the name of the article. The non-article pages follow the format ``https://en.wikipedia.org/wiki/TYPE:TYPE_NAME``, where TYPE its the kind of page and TYPE_NAME its a subcategory of that page.

    -Article : https://en.wikipedia.org/wiki/Article
    -Non article: https://en.wikipedia.org/wiki/Help:Disambiguation

Note: Disambiguation pages are considered an article page.

We then used Scrapy to crawl Wikipedia's pages. [Scrapy](en.wikipedia.org) is a free and open-source web-crawling framework written in Python, offering a nice and easy to use architecture, allowing us to access the pages and retrieve information. Scrapy deals with requests, parsing, parallelism, processing, and saving web content through its pipeline and spiders.

The crawler searched the English pages in the ``en.wikipedia.org`` domain. Initially, it creates a folder called "Articles" where the fully processed pages will be stored. After that, it will make a starting request at Wikipedia's main page at the current day and then select all article links and follow them recursively. At every new page, the links are selected and followed until no more links are left to be seen.

For every page, the links are selected from the Html source using the following regular expression ``` ^(?!\/wiki\/\S+:\S+|\/wiki\/\S+#\S+)(\/wiki\/\S+) ```. The links are placed in a list, which has the duplicate elements removed, the string cleansed and then placed in a JSON. The JSON is stored in a file whose name is the original page. The code can be found in [links.py](wikipedia_crawler/wikipedia/spiders/links.py).

To respect wikipedia's integrity, we avoided to make too many requests. In the [configuration file](wikipedia_crawler/wikipedia/settings), the spiders are configured to follow the wikipedia [robot.txt rules](https://pt.wikipedia.org/robots.txt).In the case of interruption, the process store its current state in the [cache folder](wikipedia_crawler/wikpedia/Caches) and can be later continued.

### Disadvantages

### Usage

The [script](wikipedia_crawler/wikipedia/spiders/links.py) can be used through the command line as:
    
* ` scrapy crawl wiki_spider `

It will use about 20Gb of storage and can take a few hundred hours(about 100 hours, with an average of 1000 pages per minute). If necessary, the script can be interrupter using Ctrl+C and later continued. It's necessary to wait for the program to save its context before stopping as pressing Ctrl+C multiple times will kill the process abruptly and will be needed to restart from scratch.

## Post Processing

The pages are edited by humans and as such are susceptible to mistakes. Some pages have the same content, but are stored with different names; some pages have multiple copies with different versions. In this section, we look to reduce this kind of error and cleanse our dataset.

## Building The Graph


## Files


## Dependencies
- [`Scrapy 2.3.0 `](https://scrapy.org/) module. Install with `pip install scrapy`.