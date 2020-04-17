from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import base64

from PIL import Image
import cv2 as cv

from io import BytesIO


def get_move_distance(new_gapimage, new_nogapimage):
    def compare_image(p1, p2):
        """
        比较图片的像素
        由于RGB图片一个像素点是三维的，所以循环三次
        :return:
        """
        for i in range(3):
            if abs(p1[i] - p2[i]) >= 50:
                return False
            return True

    for i in range(260):
        for j in range(116):
            gap_pixel = new_gapimage.getpixel((i, j))
            nogap_pixel = new_nogapimage.getpixel((i, j))
            if not compare_image(gap_pixel, nogap_pixel):
                return i


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
            a = random.choice([1, 1.5, 2, 2.3, 2.7, 3])
            # a = 3
        else:
            a = random.choice([-1, -2, -3])
            # a = -4
        move_track = speed * t + 0.5 * a * t ** 2
        track_list.append(round(move_track))
        speed = speed + a * t
        current += move_track
    # 正好模拟人滑动过头，把初始的偏置值划回去
    # 不能正好，最好加个随机数
    track_list.extend(
        [-3, -2, -2, -1, -0.5, -1, -1, -random.random(), random.random()])
    # 模拟人类来回移动了一小段
    # end_track = [1, 0] * 10 + [0] * 10 + [-1, 0] * 10
    # track_list.extend(end_track)
    # offset = sum(track_list) - distance
    # # 由于四舍五入带来的误差,这里需要补回来
    # if offset > 0:
    #     track_list.extend(offset * [-1, 0])
    # elif offset < 0:
    #     track_list.extend(offset * [1, 0])
    return track_list


def _slid_button(distance, driver):
    """
    根据缺口位置，移动滑块特定的距离distance
    :param diatance:
    :return:
    """
    # 获取滑块元素
    # button = driver.find_element_by_xpath('//div[@class="yidun_slider"]')
    # button = driver.find_element_by_xpath('//img[contains(@class,"jigsaw")]')
    button = driver.find_element_by_xpath('//div[@class="geetest_slider_button"]')
    ActionChains(driver).click_and_hold(button).perform()
    time.sleep(0.1)
    track_list = _track(distance - 2)
    # print(track_list)
    for i in track_list:
        ActionChains(driver).move_by_offset(i, 0).perform()
    time.sleep(0.1)
    ActionChains(driver).release().perform()


driver = webdriver.Chrome()
driver.get('https://www.feimaoyun.com/index.php/mem_lgi?new')  # 打开本地部署的极验滑动验证


def click(block):  # 自定义点击函数,模拟人工点击
    action = ActionChains(driver)
    action.click_and_hold(block).perform()
    time.sleep(random.randint(1, 10) / 10)
    action.release(block).perform()


btn_text = driver.find_element_by_id("tab-second")
click(btn_text)
# btn_text.click()
time.sleep(1)

btn = driver.find_element_by_xpath('//span[text() = "获取验证码"]')
# btn = driver.find_element_by_class_name('el-button basebtn el-button--primary is-plain')  # 到点击按钮
click(btn)  # 验证第一步,点击按钮进行验证
# btn.click()
time.sleep(5)

# 下面的js代码根据canvas文档说明而来
get_bg_JS = 'return document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL("image/png");'
get_slice_JS = 'return document.getElementsByClassName("geetest_canvas_slice geetest_absolute")[0].toDataURL("image/png");'
JS = 'return document.getElementsByClassName("geetest_canvas_fullbg geetest_fade geetest_absolute")[0].toDataURL("image/png");'
# 执行 JS 代码并拿到图片 base64 数据
im_bg_info = driver.execute_script(get_bg_JS)  # 执行js文件得到带图片信息的图片数据
im_bg_base64 = im_bg_info.split(',')[1]  # 拿到base64编码的图片信息
im_bg_bytes = base64.b64decode(im_bg_base64)  # 转为bytes类型
# with open('bg.png', 'wb') as f:  # 保存图片到本地
#     f.write(im_bg_bytes)

im_slice_info = driver.execute_script(get_slice_JS)  # 执行js文件得到带图片信息的图片数据
im_slice_base64 = im_slice_info.split(',')[1]  # 拿到base64编码的图片信息
im_slice_bytes = base64.b64decode(im_slice_base64)  # 转为bytes类型
with open('slice.png', 'wb') as f:  # 保存图片到本地
    f.write(im_slice_bytes)

im_info = driver.execute_script(JS)  # 执行js文件得到带图片信息的图片数据
im_base64 = im_info.split(',')[1]  # 拿到base64编码的图片信息
im_bytes = base64.b64decode(im_base64)  # 转为bytes类型
# with open('bg2.png', 'wb') as f:  # 保存图片到本地
#     f.write(im_bytes)

# move_x = get_move_distance(Image.open("./bg2.png"), Image.open("./bg.png"))
move_x = get_move_distance(Image.open(BytesIO(im_bytes)), Image.open(BytesIO(im_bg_bytes)))
print(move_x)
# img_target = cv.imread(BytesIO(im_bg_bytes))
# cv.rectangle(img_target, (move_x, 0), (move_x, img_target.shape[1]), (0, 0, 255), 2)
# cv.imshow('res', img_target)
# cv.waitKey(0)
# cv.destroyAllWindows()
time.sleep(1)
_slid_button(move_x, driver)
