from pymongo import MongoClient
import json
import re

client = MongoClient("localhost", 27017)
collection = client["Julyedu"]["subject1"]


def resetFileTitle(file_name):
    fileName = re.sub('[\/:*?"<>|]', '-', file_name)  # 去掉非法字符
    return fileName


# all_type = {}

all_type = {}

with open("./json_all_type.txt", "r", encoding="utf8") as f:
    all_type.update(json.load(f))
    print(all_type)

category = all_type['category']

# for b_class in category:
#     # b_class_name = b_class['name']
#     # # 一级标题
#     # f.write("# " + b_class_name + "\r\n")
#     for s_calss in b_class["son"]:
#         s_class_name = s_calss['kp_name']
#         file_name = resetFileTitle(s_class_name)
#         with open(file_name + ".txt", "a+", encoding="utf8") as f:
#             # 一级标题
#             f.write("# " + s_class_name + "\r\n")
#             # 内容
#             s_class_kp_id = s_calss["kp_id"]
#             if s_class_kp_id != 23:
#                 i = 1
#                 for item in collection.find({'kp_id': s_class_kp_id}, {'ques': 1, 'analysis': 1}):
#                     ques = item["ques"]
#                     analysis = item["analysis"]
#                     # 二级标题问题内容
#                     f.write("## " + str(i) + "." + ques + "\r\n")
#                     f.write(analysis + "\r\n")
#                     i = i + 1


def save_file(title, item, i):
    with open("机器学习" + str(title) + ".txt", "a+", encoding="utf8") as f:
        # 一级标题
        if title == 1:
            f.write("# " + "机器学习" + "\r\n")

        ques = item["ques"]
        analysis = item["analysis"]
        # 二级标题问题内容
        f.write("## " + str(i) + "." + ques + "\r\n")
        f.write(analysis + "\r\n")


size = 40
title = 1
i = 1
for item in collection.find({'kp_id': 23}, {'ques': 1, 'analysis': 1}):
    if 40 < i <= 80:
        title = 2
    elif 80 < i <= 120:
        title = 3
    elif 120 < i <= 140:
        title = 4
        save_file(title, item, i)
    elif 140 < i:
        title = 5
        save_file(title, item, i)
    i = i + 1
