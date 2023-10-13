import cv2
import numpy as np
from PIL import Image
from typing import Tuple


def open_demo(binary, iterations=1):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=iterations)
    return binary


def mask_refine(img_mask: Image.Image):
    mask = np.asarray(img_mask)
    ret, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    mask = open_demo(mask)

    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.dilate(mask, kernel, 2)

    return Image.fromarray(mask)


def cross_cut(image_path, save_path):
    """
    十字切割图片为4份,默认保存格式为png
    :param image_path: 待切割的图片路径
    :param save_path: 切割完后保存的路径,需带上文件名,不加扩展名,如/home/test/test_image
    :return: 返回处理完后的图片列表
    """
    img = Image.open(image_path)
    size_image = img.size

    weight = int(size_image[0] // 2)
    height = int(size_image[1] // 2)

    result_list = list()
    i = 0
    for j in range(2):
        for k in range(2):
            box = (weight * k, height * j, weight * (k + 1), height * (j + 1))
            region = img.crop(box)
            filename = f"{save_path}_{i}.png"
            region.save(filename)
            result_list.append(filename)
            i += 1
    return result_list


def image_mix(img_entity, img_bg, mask):
    if len(mask.shape) == 2:
        mask = mask[:, :, None]
    mask = mask / 255.
    return (mask * img_entity + (1 - mask) * img_bg).astype(img_entity.dtype)


def mask_filter(mask: np.ndarray):
    ret, mask = cv2.threshold(mask, 220, 255, cv2.THRESH_BINARY)
    return open_demo(mask)


def edge_blur(image: np.ndarray, size=11):
    thresh = image[:, :, 3]
    image = image[:, :, :3]

    blurred_img = cv2.GaussianBlur(image, (size, size), 0)
    blurred_thresh = cv2.GaussianBlur(thresh, (size, size), 0)
    mask = np.zeros(image.shape, np.uint8)
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(mask, contours, -1, (255, 255, 255), 5)
    blur_img = np.where(mask == np.array([255, 255, 255]), blurred_img, image)

    return np.concatenate((blur_img, blurred_thresh[:, :, None]), axis=2)


def find_n0(data, thr=10):
    for st in range(len(data)):
        if data[st] > thr:
            return st
    return len(data)


def rfind_n0(data, thr=10):
    for st in range(len(data) - 1, 0, -1):
        if data[st] > thr:
            return st
    return 0


def find_bbox(mask):
    """
    查找一个二值图中白色区域的最小包围框
    :param mask:
    :return:
    """
    line = np.sum(mask, axis=0)
    col = np.sum(mask, axis=1)
    le, te, re, be = find_n0(line), find_n0(col), rfind_n0(line), rfind_n0(col)
    return le, te, re, be


def pad_to(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    if len(image.shape) == 2:
        h, w = image.shape
        rest_w, rest_h = size[0] - w, size[1] - h
        pad_w = (rest_w // 2, rest_w - rest_w // 2)
        pad_h = (rest_h // 2, rest_h - rest_h // 2)
        return np.pad(image, (pad_h, pad_w), 'constant')
    else:
        h, w = image.shape[:2]
        rest_w, rest_h = size[0] - w, size[1] - h
        pad_w = (rest_w // 2, rest_w - rest_w // 2)
        pad_h = (rest_h // 2, rest_h - rest_h // 2)
        return np.pad(image, (pad_h, pad_w, (0, 0)), 'constant')


def long_edge_resize(image: Image.Image, size: int) -> Image.Image:
    w, h = image.size
    rate = size / max(w, h)
    return image.resize((round(w * rate), round(h * rate)), Image.ANTIALIAS)


def find_object_in_image(x1, x2, x2_mask, scale_range=(0.6, 1.2), scale_steps=8):
    scales = np.linspace(scale_range[0], scale_range[1], scale_steps)

    # 在不同的尺度上执行模板匹配
    maxVal_all = -1
    bbox = None
    for scale in scales:
        # 根据尺度调整模板的大小
        resized_x2 = cv2.resize(x2, None, fx=scale, fy=scale)
        resized_x2_mask = cv2.resize(x2_mask, None, fx=scale, fy=scale)

        if resized_x2.shape[0] >= x1.shape[0] or resized_x2.shape[1] >= x1.shape[1]:
            break

        # 执行模板匹配
        result = cv2.matchTemplate(x1, resized_x2, cv2.TM_CCOEFF_NORMED, mask=resized_x2_mask)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)

        if maxVal > maxVal_all:
            maxVal_all = maxVal

            x, y = maxLoc
            h, w = resized_x2.shape[:2]
            # 对于原始图像x1上的位置，根据尺度scale来还原其在x2上的位置
            # x, y = int(x / scale), int(y / scale)
            # h, w = int(h / scale), int(w / scale)
            bbox = (x, y, h, w)

    return bbox


def remove_jagged_edges(alpha_channel, erode_size=(7, 7), kernel_size=(15, 15)):
    # Step 1: 使用中值滤波平滑透明通道
    # alpha_channel = img[:, :, 3]

    # alpha_channel_smoothed = cv2.medianBlur(alpha_channel, ksize=11)
    alpha_channel_smoothed = open_demo(alpha_channel, iterations=3)
    # kernel = np.ones((5, 5), dtype=np.uint8)
    # alpha_channel_smoothed = cv2.erode(alpha_channel_smoothed, (15, 15), iterations=5)
    # erode
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, erode_size)
    alpha_channel_smoothed = cv2.morphologyEx(alpha_channel_smoothed, cv2.MORPH_ERODE, kernel)

    # alpha_channel_smoothed = cv2.bilateralFilter(alpha_channel_smoothed, kernel_size[0], 75, 75)
    alpha_channel_smoothed = cv2.GaussianBlur(alpha_channel_smoothed, kernel_size, sigmaX=0)
    # _, alpha_channel_smoothed = cv2.threshold(src=alpha_channel_smoothed, thresh=180, maxval=255, type=cv2.THRESH_BINARY)

    # Step 2: 将平滑后的透明通道替换回原图
    return alpha_channel_smoothed
