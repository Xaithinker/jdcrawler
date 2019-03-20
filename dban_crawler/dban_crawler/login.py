# -*- coding:utf-8 -*-

#-----------------------------------------------
# 版本 1.0
# 作者 xuuu
# ---------------------------------------------

import logging
import scrapy
from scrapy.http import Request
from PIL import Image, ImageDraw
import requests
from urllib.parse import urlparse
from lxml import etree
from io import BytesIO
import sys
import time
import math
import random
import re
import os

from .sett import setting, Settings
from .utils import randList

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CookieProcess(object):
    """
    使用二维码登陆, 保持Cookie.
    
    """
    session = requests.Session()
    __cookie = None
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, url=None, userAgent=None, proxies=None):
        self.url = url
        self.proxies = proxies
        self.headers = {
            'user-agent': userAgent
        }
        #self.session = CookieProcess.session
    
    @property
    def cookie(self):
        return self.__cookie

    def parse_login(self):
        try:
            self.session.get(self.url, headers=self.headers, proxies=self.proxies, hooks=dict(response=CookieProcess.parse_qr_code))
        except Exception as e:
            logger.error(f"Some errors occured. Reason: {e}")
    
    @staticmethod
    def is_201(text):
        match = re.search(r'201', text)
        if match and match.group(0) == '201':
            return True
        else:
            return False

    @staticmethod
    def is_203(text):
        match = re.search(r'203', text)
        if match and match.group(0) == '203':
            return True
        else:
            return False

    @staticmethod
    def is_200(text):
        match = re.search(r'200', text)
        if match and match.group(0) == '200':
            ticket_m = re.search('(?<=ticket" : ")(.?)+(?=")', text)
            return ticket_m.group(0)
        else:
            return False

    @staticmethod
    def parse_qr_code(r, *args, **kwargs):
        """parse the content and print the QR code"""

        root_node = etree.HTML(r.content.decode(r.encoding))
        qr_url_list = root_node.xpath(r'//div[@class="qrcode-img"]/img/@src') # ['//qr.m.jd.com/show?appid=133&size=147&t=']
        qr_url = 'http:'+qr_url_list[0][:-3] +'.jpg'

        def ticket_qr_code(url):
            resp = CookieProcess.session.get(url) # 'QRCodeKey',  'wlfstk_smdl'
            # show the QR
            f = BytesIO(resp.content)
            im = Image.open(f).convert("RGBA")
            logger.info("Opening the QR. Please scan it.")
            im.show(title="QR")

            # # 不断的check,类似浏览器的操作，直至扫描二维码
            while True:
                callback = math.floor(1e7 * random.random())
                payload = {'callback':'jQuery'+str(callback), 'appid': 133, 'token': resp.cookies['wlfstk_smdl'], '_': int(time.time() * 1000)}               
                check_resp = CookieProcess.session.get('https://qr.m.jd.com/check', params=payload, headers={'Host':'qr.m.jd.com','Referer':'https://passport.jd.com/new/login.aspx'})

                time.sleep(5)

                if CookieProcess.is_201(check_resp.text):
                    logger.info('msg: 二维码未扫描，请扫描二维码')
                    #print('二维码未扫描，请扫描二维码')
                    continue

                if CookieProcess.is_203(check_resp.text):
                    logger.warning('二维码过期，请重新扫描')
                    #print('二维码过期，请重新扫描')
                    logger.info('Ready to rerequest the QR url')
                    return ticket_qr_code(url)

                isTicket = CookieProcess.is_200(check_resp.text)
                if isTicket:
                    logger.info('Ready to get the ticket')
                    return isTicket
                
                else:
                    while True:
                        print("Please 'q' to quit or 'c' for Retries with risk")
                        char = sys.stdin.readline().strip('\n')
                        if char == 'q':
                            exit(-1)
                        if char == 'c':
                            return ticket_qr_code(url)
                        else:
                            print("Please input 'q' or 'c'")

        # get the ticket to next request
        ticket = ticket_qr_code(qr_url)

        def qrCodeTicketValidation(ticket):
            url = 'https://passport.jd.com/uc/qrCodeTicketValidation'
            headers = {
                'Referer': 'https://passport.jd.com/new/login.aspx',
                'Host': 'passport.jd.com'
            }
            payload = dict(t=ticket)
            resp = CookieProcess.session.get(url, headers=headers, params=payload)

            def isReturnCode_0(resp):
                code = resp.status_code
                if code == 200:
                    j = resp.json()
                    cookie = resp.cookies
                    return j['url'], cookie
                else:
                    print(f'Error Occured: {code}')
                    return False
            return isReturnCode_0(resp) # url 'https://www.jd.com

        url, set_cookies = qrCodeTicketValidation(ticket) # maybe set_cookies is the entrance to other urls

        CookieProcess.__cookie = set_cookies # 请求其他urls时，附带此cookie值
        # --------------------------use set_cookies--------------------------------------------------------

        # def loginJD(url, cookies): # 主页 jd.com
        #     #print(cookies)
        #     headers = {'Referer': 'https://passport.jd.com/new/login.aspx', 'Host': 'www.jd.com'}
        #     resp = CookieProcess.session.get(url, headers=headers, cookies=cookies)
        #     with open('01.html', 'w', encoding=resp.encoding) as f:
        #         f.write(resp.text)
        #     return True
        
        # loginJD(url, set_cookies)

class InitLogin():
    """处理登陆"""

    def __init__(self, *args, **kwargs):
        self.settings = Settings.copy(setting)
        self.login_url = self.settings['LOGINURL']
        self.user_agent = randList(self.settings['USERAGENTS'])
        self.__cookie = None

    def __login(self):
        """请求与处理响应"""
        self.init_login = CookieProcess(self.login_url, self.user_agent)
        self.init_login.parse_login() # 初始化Cookie
        self.__cookie = self.init_login.cookie # 提取Cookie

    @property
    def cookie(self):
        self.__login() # 获取Cookie时才处理登陆请求
        if self.__cookie:
            return dict(self.__cookie)
        else:
            return None

    def parse(self):
        """处理响应并进一步请求"""
        pass


login = InitLogin()