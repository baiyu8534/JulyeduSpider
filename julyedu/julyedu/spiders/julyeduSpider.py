# -*- coding: utf-8 -*-
import scrapy
import random
import time
import re
import json
from pprint import pprint
import copy
import sys

import datetime
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
collection = client["Julyedu"]["subject"]


# def sleep_random_time():
#     time.sleep(random.randint(1, 2) + random.random())

# scrapy crawl julyeduSpider

class JulyeduspiderSpider(scrapy.Spider):
    name = 'julyeduSpider'
    allowed_domains = ['www.julyedu.com']
    start_urls = ['https://www.julyedu.com/question/index/type/1']

    def parse(self, response):
        json_data_str = re.findall("var cate = (.*?);", response.body.decode())

        json_data_str = json_data_str[0]
        json_data_str = json_data_str.encode('raw_unicode_escape').decode('raw_unicode_escape')
        # print(json_data_str)
        json_data = json.loads(json_data_str)
        for b_class in json_data['category']:
            item = {}
            item['b_class_name'] = b_class['name']
            for s_class in b_class['son']:
                item_d = copy.deepcopy(item)
                item_d['s_class_name'] = s_class['kp_name']
                item_d['ques_id'] = s_class['ques_id']
                item_d['ques_num'] = s_class['ques_num']
                item_d['kp_id'] = s_class['kp_id']
                # 这个url没用
                url = 'https://www.julyedu.com/question/big/kp_id/{}/ques_id/{}'.format(item_d['kp_id'],
                                                                                        item_d['ques_id'])
                # sleep_random_time()
                print('>>parse开始请求--->>', url)
                yield scrapy.Request(
                    url,
                    callback=self.parse_temp_page,
                    meta={"item": copy.deepcopy(item_d)}
                )

        pprint(list)
        # for url in big_class_urls:
        #     # 随机等待一端时间
        #     sleep_random_time()
        #     yield scrapy.Request(
        #         url,
        #         callback=self.parse_temp_page()
        #     )
        pass

    def parse_temp_page(self, response):
        """
        只是获取下所有题目的id就第一个页面多获取一次，这样代码省了好多事
        用页面上的数据，有这个分类下所有题目的id，直接for取请求，就不用找下一题的答案了
        :param response:
        :return:
        """
        item = response.meta["item"]
        json_data_str = re.findall("var data = (.*?);", response.body.decode())
        if len(json_data_str) == 0:
            print('出验证码了')
            # self.crawler.engine.close_spider(self, '验证码')
            time.sleep(5)
            yield scrapy.Request(
                response.request.url,
                callback=self.parse_ques_page,
                meta={"item": copy.deepcopy(item)}
            )
            # response.request.url
        json_data_str = json_data_str[0]
        json_data_str = json_data_str.encode('raw_unicode_escape').decode('raw_unicode_escape')
        json_data = json.loads(json_data_str)
        for ques in json_data['list']:
            item['ques_url'] = 'https://www.julyedu.com/question/big/kp_id/{}/ques_id/{}'.format(item['kp_id'],
                                                                                                 ques['ques_id'])
            # sleep_random_time()
            print('>>parse_temp_page开始请求--->>', item['ques_url'])
            yield scrapy.Request(
                item['ques_url'],
                callback=self.parse_ques_page,
                meta={"item": copy.deepcopy(item)}
            )

    def parse_ques_page(self, response):
        print("拿到了网页")
        item = response.meta["item"]
        json_data_str = re.findall("var data = (.*?);", response.body.decode())
        if len(json_data_str) == 0:
            print('出验证码了')
            self.crawler.engine.close_spider(self, '验证码')
        json_data_str = json_data_str[0]
        json_data_str = json_data_str.encode('raw_unicode_escape').decode('raw_unicode_escape')

        json_data = json.loads(json_data_str)
        item['ques'] = json_data['quesInfo']['ques'].encode('raw_unicode_escape').decode('raw_unicode_escape')
        item['analysis'] = json_data['quesInfo']['analysis'].encode('raw_unicode_escape').decode(
            'raw_unicode_escape').replace(r'\/\/', '//').replace(r'\/', '/')
        item["catch_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        collection.insert(dict(item))
        print('>>保存>>', item['ques'][:10])
        print('保存到mongodb里了')
        # yield item
