# encoding:utf-8
import cv2 as cv
import numpy as np
import requests
# from io import BytesIO
# from PIL import Image

'''
模板匹配
沃日，网上下的图片是480*240
网页上是400*200
我说tm的怎么对不上。。。
'''



# 对滑块进行二值化处理 因为图片是背景透明的了 所以不用二值化
def _handle_img1(image):
    kernel = np.ones((8, 8), np.uint8)  # 去滑块的前景噪声内核
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    width, heigth = gray.shape
    for h in range(heigth):
        for w in range(width):
            if gray[w, h] == 0:
                gray[w, h] = 96
    # cv.imshow('gray', gray)
    binary = cv.inRange(gray, 96, 96)
    res = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)  # 开运算去除白色噪点
    # cv.imshow('res', res)
    return res


# 模板匹配(用于寻找缺口有点误差)
def _template_match(img_target, img_template):
    # tpl = handle_img1(img_template) # 误差来源就在于滑块的背景图为白色
    tpl = cv.GaussianBlur(img_template, (3, 3), 0)
    tpl = cv.cvtColor(tpl, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(img_target, (3, 3), 0)  # 目标图高斯滤波
    gray = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
    # cv.imshow("gray", gray)
    # cv.imshow("tpl", tpl)
    # ret, target = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)  # 目标图二值化
    target = gray
    # cv.imshow("template", tpl)
    # cv.imshow("target", target)
    method = cv.TM_CCOEFF_NORMED
    width, height = tpl.shape[:2]
    result = cv.matchTemplate(target, tpl, method)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    left_up = max_loc
    right_down = (left_up[0] + height, left_up[1] + width)
    cv.rectangle(img_target, left_up, right_down, (0, 0, 255), 2)
    cv.imshow('res', img_target)
    # print(left_up)
    # print(right_down)
    return left_up[0]


if __name__ == '__main__':
    img0 = cv.imread('./target.jpg')
    img1 = cv.imread('./slide.png')
    # img0 = cv.imread('./testCV/test3.jpg')
    # img1 = cv.imread('./testCV/test3_s.png')
    _template_match(img0, img1)
    cv.waitKey(0)
    cv.destroyAllWindows()


def get_slide_size(target_img_path, slide_img_path):
    img0 = cv.imread(target_img_path)
    img1 = cv.imread(slide_img_path)
    move_size = _template_match(img0, img1)
    # 宽度装换，因为下载的图片和网页显示的图片大小不一样
    print(move_size)
    move_size =  move_size * (400 / 480)
    print(move_size)
    print("_________________")
    return move_size
