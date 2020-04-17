from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from selenium.webdriver import ActionChains
import random
# from save_file_util import *
import requests
import json
import time
# import pyquery
import time

from .breakSlideIdCodeWithOpenCV_v2 import get_slide_size

# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument("--enable-javascript")
# driver = webdriver.Chrome(options=chrome_options)


# 要加偏置 。。。。还有就行滑块的选择，直接点下面箭头和点拼图的图片不一样。。。
# 这个没有偏置主要是网页显示和下载图片的大小不一，要转换一下，+5是弥补乘小数的损失
BIAS = 5


def _is_element_exist_by_xpath(xpath_str, driver):
    try:
        driver.find_element_by_xpath(xpath_str)
        return True
    except:
        return False


def _get_imgae_and_save(image_url, name):
    image_content = requests.get(image_url).content
    with open('./' + name, "wb") as f:
        f.write(image_content)


def _slid_button(distance, driver):
    """
    根据缺口位置，移动滑块特定的距离distance
    :param diatance:
    :return:
    """
    # 获取滑块元素
    # button = driver.find_element_by_xpath('//div[@class="yidun_slider"]')
    button = driver.find_element_by_xpath('//img[contains(@class,"jigsaw")]')
    ActionChains(driver).click_and_hold(button).perform()
    time.sleep(0.5)
    track_list = _track(distance - 2)
    # print(track_list)
    for i in track_list:
        ActionChains(driver).move_by_offset(i, 0).perform()
    time.sleep(0.3)
    ActionChains(driver).release().perform()


def _track(distance):
    """
    规划移动的轨迹
    加速度用到random模块,随机选择给定的加速度
    :param distance:
    :return:
    """
    # 匀速移动
    # for i in range(distance):
    #     ActionChains(driver).move_by_offset(1, 0).perform()
    # ActionChains(driver).move_by_offset(distance-5, 0).perform()
    t = 1
    speed = 0
    current = 0
    mid = 3 / 5 * distance
    track_list = []
    while current < distance:
        if current < mid:
            a = random.choice([1, 2, 3])
            # a = 3
        else:
            a = random.choice([-1, -2, -3])
            # a = -4
        move_track = speed * t + 0.5 * a * t ** 2
        track_list.append(round(move_track))
        speed = speed + a * t
        current += move_track
    track_list.extend([1, 2, 2, 1, -1, -1, -3])
    # # 模拟人类来回移动了一小段
    # end_track = [1, 0] * 10 + [0] * 10 + [-1, 0] * 10
    # track_list.extend(end_track)
    # offset = sum(track_list) - distance
    # # 由于四舍五入带来的误差,这里需要补回来
    # if offset > 0:
    #     track_list.extend(offset * [-1, 0])
    # elif offset < 0:
    #     track_list.extend(offset * [1, 0])
    return track_list


def getSlideIDCodeAndBreak(url):
    print("出验证码的url",url)
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("--enable-javascript")
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    if ("var data = " in driver.page_source):
        # 验证码通过了
        driver.close()
    if (_is_element_exist_by_xpath('//img[contains(@class,"bg-img")]', driver)
            and _is_element_exist_by_xpath('//img[contains(@class,"jigsaw")]', driver)):
        target_img_url = driver.find_element_by_xpath('//img[contains(@class,"bg-img")]').get_attribute("src")
        slide_img_url = driver.find_element_by_xpath('//img[contains(@class,"jigsaw")]').get_attribute("src")
        if target_img_url != "None" and slide_img_url != "None":
            _get_imgae_and_save(target_img_url, "target.jpg")
            _get_imgae_and_save(slide_img_url, "slide.png")
        else:
            getSlideIDCodeAndBreak(url)
            return
        time.sleep(4)

        move_size = get_slide_size("./target.jpg", "./slide.png")

        _slid_button(move_size + BIAS, driver)
    else:
        # 如果网速慢没找到图片
        getSlideIDCodeAndBreak(url)
        return
    # target_img_url = driver.find_element_by_class_name("yidun_bg-img")
    # slide_img_url = driver.find_element_by_class_name("yidun_jigsaw")

    # dir(target_img_url)

    time.sleep(3)
    if ("var data = " in driver.page_source):
        driver.close()

    # 滑动位置不对，重新滑动
    while (_is_element_exist_by_xpath('//img[contains(@class,"bg-img")]', driver)
           and _is_element_exist_by_xpath('//img[contains(@class,"jigsaw")]', driver)):
        target_img_url = driver.find_element_by_xpath('//img[contains(@class,"bg-img")]').get_attribute("src")
        slide_img_url = driver.find_element_by_xpath('//img[contains(@class,"jigsaw")]').get_attribute("src")

        _get_imgae_and_save(target_img_url, "target.jpg")
        _get_imgae_and_save(slide_img_url, "slide.png")

        time.sleep(3)

        # if(driver.page_source)

        move_size = get_slide_size("./target.jpg", "./slide.png")

        _slid_button(move_size + BIAS, driver)

        time.sleep(3)
        if ("var data = " in driver.page_source):
            # 验证码通过了
            driver.close()
            return
        if ("失败过多，点此重试" in driver.page_source):
            # 点击刷新页面
            driver.find_element_by_class_name("yidun_tips").click()
            time.sleep(3)

    # driver.close()

# if __name__ == "__main__":
#     getSlideIDCodeAndBreak("https://www.julyedu.com/question/big/kp_id/27/ques_id/1431")
