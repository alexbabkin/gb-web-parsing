# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksparserItem(scrapy.Item):
    _id = scrapy.Field()
    book_title = scrapy.Field()
    book_price = scrapy.Field()
