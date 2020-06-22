# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from booksparser.items import BooksparserItem



class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%B8%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="pagination-next__text"]/@href').extract()[1]
        links = response.xpath('//a[@class="product-title-link"]/@href').extract()
        for link in links:
            yield response.follow(link, callback=self.handle_book_data)
        yield response.follow(next_page, callback=self.parse)

    def handle_book_data(self, response: HtmlResponse):
        book_title = response.xpath('//div[@class="prodtitle"]/h1/text()').extract_first()
        price = response.xpath('//span[@class="buying-pricenew-val-number"]/text()').extract_first()
        if price is None:
            price = response.xpath('//span[@class="buying-price-val-number"]/text()').extract_first()
        initial_price = response.xpath('//span[@class="buying-priceold-val-number"]/text()').extract_first()
        if initial_price is None:
            initial_price = price
        link = response.request.url
        author = response.xpath('//a[@data-event-label="author"]/text()').extract_first()
        rating = response.xpath('//div[@id="rate"]/text()').extract_first()
        yield BooksparserItem(book_title=book_title, book_price=price, book_initial_price=initial_price,
                              book_link=link, book_author=author, book_rating=rating)
