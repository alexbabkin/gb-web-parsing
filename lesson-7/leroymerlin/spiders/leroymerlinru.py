# -*- coding: utf-8 -*-
import scrapy
from items import LeroymerlinItem
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(
            '//a[@class = "paginator-button next-paginator-button"]').extract_first()
        product_links = response.xpath('//div[@class="product-name"]/a')
        for link in product_links:
            yield response.follow(link, callback=self.handle_producr_data)
        yield response.follow(next_page, callback=self.parse)

    def handle_producr_data(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//h1[@slot="title"]/text()')
        loader.add_xpath('photos', '//img[@alt="product image"]/@src')
        loader.add_xpath('params', '//div[@class="def-list__group"]/*/text()')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        yield loader.load_item()


