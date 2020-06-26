# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('192.168.19.48', 8080)
        self.mongo_base = client.books_labirint

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)


class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img, meta=item)  # Скачиваем фото и передает item через meta
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None, ):
        item_title = request.meta['title']
        return f'{item_title}/{ImagesPipeline.file_path(self, request, response, info)}'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
