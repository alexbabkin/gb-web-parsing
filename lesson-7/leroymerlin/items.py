# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Compose


def parse_param_names(params):
    return {k: v.replace('\n', '').strip() for k, v in params.items()}


def handle_params(params):
    key, value = '', ''
    params_dict = {}
    for n in range(0, len(params)):
        if n % 2 == 0:
            key = params[n]
        else:
            params_dict[key] = params[n]
    return params_dict


def parse_price(value_str):
    value_str = value_str.replace(' ', '')
    try:
        return float(value_str)
    except ValueError:
        print(f'Cannot convert price str {value_str} to number')


class LeroymerlinItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    params = scrapy.Field(input_processor=Compose(handle_params, parse_param_names))
    url = scrapy.Field()
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(parse_price))
