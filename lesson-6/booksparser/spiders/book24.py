# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from booksparser.items import BooksparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%B8%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="catalog-pagination__item _text js-pagination-catalog-item"]/@href').extract_first()
        links = response.xpath('//a[@class="book__image-link js-item-element ddl_product_link"]/@href').extract()
        for link in links:
            yield response.follow(link, callback=self.handle_book_data)
        yield response.follow(next_page, callback=self.parse)

    def handle_book_data(self, response: HtmlResponse):
        book_title = response.xpath('//h1[@class="item-detail__title"]/text()').extract_first()
        price = response.xpath('//div[@class="item-actions__price"]//b/text()').extract_first()
        initial_price = response.xpath('//div[@class="item-actions__price-old"]/text()').extract_first()
        if initial_price is None:
            initial_price = price
        link = response.request.url
        author = response.xpath('//a[@class="item-tab__chars-link js-data-link"]/text()').extract_first()
        rating = response.xpath('//span[@class="rating__rate-value"]/text()').extract_first()
        yield BooksparserItem(book_title=book_title, book_price=price, book_initial_price=initial_price,
                              book_link=link, book_author=author, book_rating=rating)
