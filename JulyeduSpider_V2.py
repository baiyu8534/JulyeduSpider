import requests
import copy
import json
import re

import datetime
from pymongo import MongoClient
import random

from lxml import etree
import json
import time
from queue import Queue
import threading

from utils.breakSlideIdCode import getSlideIDCodeAndBreak
#todo 要解决的问题，当请求线程多的时候，一次5个，比如现在出现验证码了，请求了5个页面
#这5个页面返回的html都是验证码的
# 现在有一个在破解验证码，已经请求到数据的，要进行解析了，拿到的还是有验证码的页面，就又去解析了
# 应该验证码破解后，重新获取队列里全部的页面，一进获取的html都删了
# 请求和数据处理不同步，导致验证码破解后，html里还有没有处理的验证码html



"""
V1 遗留问题解决
# FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFf
# 不行！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
# 还是会有重复的！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
# FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFfff
# 擦，把请求和数据处理放一起就行了
# 这样，每次请求了直接判断是不是验证码。
# 就不会出现验证码已经出现了而且破解了，html页面处理线程还从队列中获取到以前没来得及处理的有验证码的html页面

# 这样把请求和html处理放一起，既可以避免，请求到的数据处理不及时，而造成的逻辑混乱。
# 验证码已经处理了，但是数据处理线程发生了延后，拿到的数据还是出现验证码的页面
# 应该请求后，拿到html直接判断，有验证码出现并且正在破解了，
# 就直接把这个请求丢回请求url队列里，终止操作，不用去做剩下的数据解析，这样下次重新请求，验证码就是破解的了

V2总结

现在我能想到的还有一种可能，就是event的set和clear再同一个线程中
放到其他线程去破解验证码

"""



IS_NOT_ID_CODE = threading.Event()
IS_NOT_ID_CODE.set()

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


class JulyeduSpider(object):
    """
    多线程爬虫,可以多线程爬取了。但是服务器限制了同意ip请求多少次后就出验证码
    所以提高的效率只是保存和页面数据提取还有同时拿到多个网页，效率是可以提高
    要想再次提高，用代理ip
    """

    def __init__(self):
        self.client = MongoClient("localhost", 27017)
        self.collection = self.client["Julyedu"]["test2"]
        # 用来记录请求json解析失败的网页url，可以手动解析
        self.error_json_url = []

        self.__temp_page_url_queue = Queue()
        self.__info_page_url_queue = Queue()
        self.__target_data_queue = Queue()

        # IS_NOT_ID_CODE = threading.Event()
        self.__is_running = threading.Event()
        # 初始化时肯定不是验证码
        # IS_NOT_ID_CODE.set()
        # 怎么才能知道都爬完了，是个问题，还是子线程都停了，让主线程停就行，这个就先不用了
        self.__is_running.set()

    def start_request(self):
        # 第一个页面只请求一次，就不开线程去做了
        user_agent = random.choice(USER_AGENTS_LIST)
        headers = {}
        headers["User-Agent"] = user_agent
        print("请求了-->>https://www.julyedu.com/question/index/type/1" + "\n")
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
                self.__temp_page_url_queue.put({"temp_url": url, "item": item_d})
                # sleep_random_time()
                # print('>>parse开始请求--->>', url)
                # print(item_d)
                # parse_temp_page(url, copy.deepcopy(item_d))

        # print(self.error_json_url)

    def request_temp_page(self):
        """
        请求临时网页，拿到分类下所有的题目的url
        :return:
        """
        while self.__is_running.isSet():
            data = self.__temp_page_url_queue.get()
            temp_url = data["temp_url"]
            item = data["item"]

            user_agent = random.choice(USER_AGENTS_LIST)
            headers = {}
            headers["User-Agent"] = user_agent
            # 每次请求之前先检查是不是验证码已经出现，出现就等待，验证码破解后再请求
            IS_NOT_ID_CODE.wait()
            print("请求了temp-->>{}  \n".format(temp_url))
            html_str = requests.get(temp_url, headers=headers).content.decode()
            # 不要整个的了 有可能出错，出错就一组题没有了

            json_data_str = re.findall(r',"list":(.*?);', html_str)
            if len(json_data_str) == 0:
                # 随机等待一下，要不有的线程同时判断都没验证码
                time.sleep(random.choice([0.2, 0.5, 0.7, 0.9]))
                if IS_NOT_ID_CODE.isSet():
                    # 如果没有验证码时，出了验证码就去破解
                    # 标志置为false，wait就会等待
                    IS_NOT_ID_CODE.clear()
                    print('111出验证码了')
                    getSlideIDCodeAndBreak(temp_url)
                    # 上面方法执行完毕，验证码就破解了，可以置为true了
                    # 重新请求
                    IS_NOT_ID_CODE.set()
                    time.sleep(random.choice([0.2, 0.5, 0.7, 0.9]))
                    IS_NOT_ID_CODE.wait()
                    self.__temp_page_url_queue.put({"temp_url": temp_url, "item": item})
                    self.__temp_page_url_queue.task_done()
                    return
                else:
                    # 有验证码时，出了验证码就直接等待一段时间，等验证码破解完毕去重新请求
                    IS_NOT_ID_CODE.wait()
                    self.__temp_page_url_queue.put({"temp_url": temp_url, "item": item})
                    self.__temp_page_url_queue.task_done()
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
                print("json 解析出错")
                print(temp_url)
                print(json_data_str)
                print(re.findall(r',"list":(.*?)}]};', html_str))
                self.error_json_url.append(temp_url)
                with open("error_json_str.txt", "a+", encoding='utf8') as f:
                    f.write(json_data_str + "\n")
            if len(json_data.keys()) != 0:
                for ques in json_data['list']:
                    item['ques_url'] = 'https://www.julyedu.com/question/big/kp_id/{}/ques_id/{}'.format(
                        ques['category_id'], ques['ques_id'])
                    # sleep_random_time()
                    # print('>>parse_temp_page开始请求--->>', item['ques_url'])
                    # parse_ques_page(item['ques_url'], copy.deepcopy(item))
                    self.__info_page_url_queue.put({"url": item['ques_url'], "item": copy.deepcopy(item)})

            self.__temp_page_url_queue.task_done()


    def request_info_page(self):
        """
        请求题目的url
        :return:
        """
        while self.__is_running.isSet():
            data = self.__info_page_url_queue.get()
            url = data["url"]
            item = data["item"]

            user_agent = random.choice(USER_AGENTS_LIST)
            headers = {}
            headers["User-Agent"] = user_agent
            # 请求之前先判断是否出现验证码了
            IS_NOT_ID_CODE.wait()
            print("请求了info-->>{}  \n".format(url))
            html_str = requests.get(url, headers=headers).content.decode()
            # print("拿到了网页")

            json_data_str = re.findall("var data = (.*?)}]};", html_str)
            if len(json_data_str) == 0:
                # 随机等待一下，要不有的线程同时判断都没验证码
                time.sleep(random.choice([0.2, 0.5, 0.7, 0.9]))
                # 标志置为false，wait就会等待
                if IS_NOT_ID_CODE.isSet():
                    IS_NOT_ID_CODE.clear()
                    print('222出验证码了')
                    getSlideIDCodeAndBreak(url)
                    # 上面方法执行完毕，验证码就破解了，可以置为true了
                    IS_NOT_ID_CODE.set()
                    time.sleep(random.choice([0.2, 0.5, 0.7, 0.9]))
                    IS_NOT_ID_CODE.wait()
                    self.__info_page_url_queue.put({"url": url, "item": item})
                    self.__info_page_url_queue.task_done()
                    return
                else:
                    IS_NOT_ID_CODE.wait()
                    self.__info_page_url_queue.put({"url": url, "item": item})
                    self.__info_page_url_queue.task_done()
                    return

            json_data_str = json_data_str[0] + "}]}"
            json_data_str = json_data_str.encode('raw_unicode_escape').decode('raw_unicode_escape')

            json_data = {}
            try:
                json_data = json.loads(json_data_str)

            except:
                print("json 解析出错")
                self.error_json_url.append(url)
                with open("error_json_str.txt", "a+", encoding='utf8') as f:
                    f.write(json_data_str + "\n")
            if len(json_data.keys()) != 0:
                item['ques_id'] = json_data['quesInfo']['id']
                item['ques'] = json_data['quesInfo']['ques'].encode('raw_unicode_escape').decode('raw_unicode_escape')
                item['analysis'] = json_data['quesInfo']['analysis'].encode('raw_unicode_escape').decode(
                    'raw_unicode_escape').replace(r'\/\/', '//').replace(r'\/', '/')
                item["catch_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.__target_data_queue.put(dict(item))

            self.__info_page_url_queue.task_done()

    def save_data(self):
        while self.__is_running.isSet():
            data = self.__target_data_queue.get()
            self.collection.insert(data)
            print('>>保存>>', data['ques'][:10])
            print('保存到mongodb里了')
            self.__target_data_queue.task_done()

    def run(self):
        self.start_request()
        thread_list = []
        # 1.获取临时网页
        for i in range(4):
            t_req_temp_page = threading.Thread(target=self.request_temp_page)
            thread_list.append(t_req_temp_page)
        # 3.获取题目详情网页
        for i in range(4):
            t_req_info_page = threading.Thread(target=self.request_info_page)
            thread_list.append(t_req_info_page)
        # 5.保存数据
        for i in range(16):
            t_save_data = threading.Thread(target=self.save_data)
            thread_list.append(t_save_data)

        for t in thread_list:
            # t.setDaemon(True)  # 把子线程设置为守护线程，该线程不重要主线程结束，子线程结束
            t.start()

        for q in [self.__temp_page_url_queue,
                  self.__info_page_url_queue,
                  self.__target_data_queue]:
            q.join()  # 让主线程等待阻塞，等待队列的任务完成之后再完成

        print("主线程结束")
        # print()


if __name__ == "__main__":
    spider = JulyeduSpider()
    spider.run()
