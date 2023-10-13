from typing import Tuple
import base64
import time
import os

from flask import jsonify


def create_sn():
    return time.time_ns() // (10 ** 6)


def my_makedirs(name: str, task_id: str = ""):
    """
    根据给到的文件夹路径，按任务id创建文件夹
    :param name:
    :param task_id: 任务id
    :return:
    """
    path = os.path.join(name, task_id)
    os.makedirs(path, exist_ok=True)
    return path


def image2base64(image):
    with open(image, 'rb') as f:
        b64encode = base64.b64encode(f.read())
        b64_encode = f"data:image/png;base64,{b64encode.decode()}"
    return b64_encode


def base64_to_image(base64_encod_str: str, save_path: str):
    if "data:image" in base64_encod_str:
        base64_encod_str = base64_encod_str.split(",")[-1]
    img_b64decode = base64.b64decode(base64_encod_str)
    # 保存图片
    with open(save_path, 'wb') as png:
        png.write(img_b64decode)


def create_response(data: dict, code: int = 200, message: str = "success"):
    data = {
        "code": code,
        "message": message,
        "data": data
    }
    return jsonify(data)


def list_full_path(directory):
    """
    以绝对路径列出文件夹下所有文件
    :param directory:
    :return:
    """
    return [os.path.join(directory, file) for file in os.listdir(directory)]


def cut_image(image, max_px: int):
    """
    根据图片尺寸与给定的最大边尺寸，等比例缩放图片至8的整数倍尺寸(sd生图宽高需求)
    :param image:
    :param max_px:
    :return:
    """
    # 宽图
    if image.width > image.height:
        width = max_px
        rito = image.width / image.height
        height = round(max_px / rito)
        while height % 8 != 0:
            height += 1
    # 长图
    elif image.height > image.width:
        rito = image.height / image.width
        width = round(max_px / rito)
        while width % 8 != 0:
            width += 1
        height = max_px
    else:
        width = height = max_px
    return width, height
