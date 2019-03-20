#/usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import scrapy
from scrapy.http import Request, Response, TextResponse
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
from datetime import datetime
from ..items import cartItem
from .. import login
from ..utils import randList
from ..sett import setting, Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CartSpider(scrapy.Spider):
    name = "jd"
    start_urls = ['https://cart.jd.com/cart.action',]
    
    def __init__(self):
        self.settings = Settings.copy(setting)
        self.cookie = login.cookie
        self.user_agent = randList(self.settings['USERAGENTS'])
        self.headers = {'Host': 'cart.jd.com', 'Referer': 'https://www.jd.com/'}
        self.headers['User-Agent'] = self.user_agent

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=self.headers, cookies=self.cookie, callback=self.parse_information)
    

    def parse_information(self, response):
        with open('a.html', 'wb') as f:
            f.write(response.body)
        logger.info('成功存入a.html')
        
        item_selector = response.xpath('//div[@product="1"]')
        for selector in item_selector:
            yield self.parse_item(selector, response)

    def parse_item(self, selector, resposne):

        loader = ItemLoader(item=cartItem(), selector=selector)
        loader.add_xpath('p_name', './/div[@class="item-msg"]/div[@class="p-name"]/a/text()', MapCompose(lambda x: x.strip()))
        loader.add_xpath('props_txt', './/div[@class="props-txt"]/text()', MapCompose(lambda x: x.strip()))
        loader.add_xpath('p_price', './/p/strong/text()', MapCompose(lambda x: x.strip()))
        loader.add_value('date', datetime.now())
        return loader.load_item()