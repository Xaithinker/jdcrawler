# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import configparser


class CartItemPipeline(object):
    """存储至monodb"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(r'dban_crawler\pipelines\mongodb.cfg')
        self.client = MongoClient(self.config['DEFAULT']['MONGODB_SERVER'], int(self.config['DEFAULT']['MONGODB_PORT']))
        self.db = self.client[f"{self.config['DEFAULT']['MONGODB_DB']}"]
        self.collection = self.db['cart_collection']
    
    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item
    
    def item_scraped(self, spider):
        print('Item has insert to mongoDB')
