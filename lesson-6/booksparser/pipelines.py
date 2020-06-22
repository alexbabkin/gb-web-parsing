# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class BooksparserPipeline:
    def __init__(self):
        client = MongoClient('192.168.19.48', 8080)
        self.mongo_base = client.books_labirint

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
