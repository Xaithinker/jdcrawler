# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DbanCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class cartItem(scrapy.Item):
    p_name = scrapy.Field()
    props_txt = scrapy.Field()
    p_price = scrapy.Field()
    date = scrapy.Field()