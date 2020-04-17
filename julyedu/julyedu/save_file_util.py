import os


def save_file(content, dir_name, name):
    with open(dir_name + '/' + name, "wb") as f:
        f.write(content)


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
