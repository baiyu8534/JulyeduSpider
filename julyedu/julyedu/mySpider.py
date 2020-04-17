import requests
import copy
import json
import re

import datetime
from pymongo import MongoClient
import random

from breakSlideIdCode import getSlideIDCodeAndBreak

client = MongoClient("localhost", 27017)
collection = client["Julyedu"]["subject1_test"]

USER_AGENTS_LIST = [
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Avant Browser/1.2.789rel1 (http://www.avantbrowser.com)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a",
    "Mozilla/2.02E (Win95; U)",
    "Mozilla/3.01Gold (Win95; I)",
    "Mozilla/4.8 [en] (Windows NT 5.1; U)",
    "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)",
    "HTC_Dream Mozilla/5.0 (Linux; U; Android 1.5; en-ca; Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.2; U; de-DE) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/234.40.1 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; sdk Build/CUPCAKE) AppleWebkit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; htc_bahamas Build/CRB17) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.1-update1; de-de; HTC Desire 1.19.161.5 Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Sprint APA9292KT Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; de-ch; HTC Hero Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; ADR6300 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; HTC Legend Build/cupcake) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 1.5; de-de; HTC Magic Build/PLAT-RC33) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1 FirePHP/0.3",
    "Mozilla/5.0 (Linux; U; Android 1.6; en-us; HTC_TATTOO_A3288 Build/DRC79) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.0; en-us; dream) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; T-Mobile G1 Build/CRB43) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari 525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-gb; T-Mobile_G2_Touch Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Droid Build/ESD20) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Droid Build/FRG22D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Milestone Build/ SHOLS_U2_01.03.1) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.0.1; de-de; Milestone Build/SHOLS_U2_01.14.0) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522  (KHTML, like Gecko) Safari/419.3",
    "Mozilla/5.0 (Linux; U; Android 1.1; en-gb; dream) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Droid Build/ESD20) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Sprint APA9292KT Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; ADR6300 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-ca; GT-P1000M Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 3.0.1; fr-fr; A500 Build/HRI66) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 1.6; es-es; SonyEricssonX10i Build/R1FA016) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.6; en-us; SonyEricssonX10i Build/R1AA056) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
]

error_json_url = []


def start_run():
    user_agent = random.choice(USER_AGENTS_LIST)
    headers = {}
    headers["User-Agent"] = user_agent
    html_str = requests.get("https://www.julyedu.com/question/index/type/1", headers=headers).content.decode()
    json_data_str = re.findall("var cate = (.*?);", html_str)

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
            # item_d['ques_id'] = s_class['ques_id']
            item_d['ques_num'] = s_class['ques_num']
            item_d['kp_id'] = s_class['kp_id']
            # 这个url没用
            url = 'https://www.julyedu.com/question/big/kp_id/{}/ques_id/{}'.format(item_d['kp_id'],
                                                                                    s_class['ques_id'])
            # sleep_random_time()
            print('>>parse开始请求--->>', url)
            # print(item_d)
            parse_temp_page(url, copy.deepcopy(item_d))

    print(error_json_url)


def parse_temp_page(url, item):
    """
            只是获取下所有题目的id就第一个页面多获取一次，这样代码省了好多事
            用页面上的数据，有这个分类下所有题目的id，直接for取请求，就不用找下一题的答案了
            :param response:
            :return:
            """
    user_agent = random.choice(USER_AGENTS_LIST)
    headers = {}
    headers["User-Agent"] = user_agent
    html_str = requests.get(url, headers=headers).content.decode()
    # 不要整个的了 有可能出错，出错就一组题没有了
    json_data_str = re.findall(r',"list":(.*?);', html_str)
    if len(json_data_str) == 0:
        print('111出验证码了')
        getSlideIDCodeAndBreak(url)
        parse_temp_page(url, item)
        return

    json_data_str = '{"list":' + json_data_str[0]
    # json_data_str = json_data_str.encode('raw_unicode_escape').decode('raw_unicode_escape')
    # print(json_data_str)
    # with open("json_str.txt", "a+", encoding='utf8') as f:
    #     f.write(json_data_str)
    json_data = {}
    try:
        json_data = json.loads(json_data_str)

    except:
        # 这里如果json解析出错 就整个一组题的id就拿不到了
        # todo 这里可以值去list的
        print("=================================")
        print("=================================")
        print("=================================")
        print("json 解析出错")
        print(url)
        print(json_data_str)
        print(re.findall(r',"list":(.*?)}]};', html_str))
        error_json_url.append(url)
        with open("error_json_str.txt", "a+", encoding='utf8') as f:
            f.write(json_data_str + "\n")
        print("=================================")
        print("=================================")
        print("=================================")
    if len(json_data.keys()) != 0:
        for ques in json_data['list']:
            item['ques_url'] = 'https://www.julyedu.com/question/big/kp_id/{}/ques_id/{}'.format(ques['category_id'],
                                                                                                 ques['ques_id'])
            # sleep_random_time()
            print('>>parse_temp_page开始请求--->>', item['ques_url'])
            parse_ques_page(item['ques_url'], copy.deepcopy(item))


def parse_ques_page(url, item):
    user_agent = random.choice(USER_AGENTS_LIST)
    headers = {}
    headers["User-Agent"] = user_agent
    html_str = requests.get(url, headers=headers).content.decode()
    print("拿到了网页")
    json_data_str = re.findall("var data = (.*?)}]};", html_str)
    if len(json_data_str) == 0:
        print('222出验证码了')
        getSlideIDCodeAndBreak(url)
        parse_ques_page(url, item)
        return
        # return 0
        # self.crawler.engine.close_spider(self, '验证码')
    json_data_str = json_data_str[0] + "}]}"
    json_data_str = json_data_str.encode('raw_unicode_escape').decode('raw_unicode_escape')

    json_data = {}
    try:
        json_data = json.loads(json_data_str)

    except:
        print("json 解析出错")
        error_json_url.append(url)
        with open("error_json_str.txt", "a+", encoding='utf8') as f:
            f.write(json_data_str + "\n")
    if len(json_data.keys()) != 0:
        item['ques_id'] = json_data['quesInfo']['id']
        item['ques'] = json_data['quesInfo']['ques'].encode('raw_unicode_escape').decode('raw_unicode_escape')
        item['analysis'] = json_data['quesInfo']['analysis'].encode('raw_unicode_escape').decode(
            'raw_unicode_escape').replace(r'\/\/', '//').replace(r'\/', '/')
        item["catch_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        collection.insert(dict(item))
        print('>>保存>>', item['ques'][:10])
        print('保存到mongodb里了')


if __name__ == "__main__":
    start_run()
