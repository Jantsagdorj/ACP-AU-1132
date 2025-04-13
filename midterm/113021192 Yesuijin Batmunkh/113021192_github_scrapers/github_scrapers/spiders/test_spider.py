import scrapy

class TestSpider(scrapy.Spider):
    name = "test_spider"
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("span small::text").get(),
            }
