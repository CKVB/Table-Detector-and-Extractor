import numpy as np
import cv2
import os
import requests
from flask import request


APP_ROOT = os.path.dirname(os.path.abspath(__file__)).split("routes")[0]


def get_image():
    data = request.get_json()
    url = data["image_url"]

    if "http" in url:
        try:
            response = requests.get(url, stream=True).raw
        except Exception:
            return {"error": "invalid url."}, 400
        else:
            if response.status == 404:
                return {"error": "file not found."}, 404
            image = np.asarray(bytearray(response.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            image = np.array(image)
    else:
        image_file_path = os.path.isfile(url)
        if image_file_path:
            image = cv2.imread(url)
        else:
            return {"error": "file not found."}, 404
    image_copy = image.copy()
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception:
        return {"error": "request not processable."}, 422
    else:
        return image, image_copy, 200


def crop_image(image, image_copy):

    height, width = image.shape

    threshold = 10
    start_x, start_y = threshold*2, threshold
    end_x, end_y = height-threshold, width-threshold

    crop_image = image[start_x: end_x, start_y: end_y]
    crop_image_copy = image_copy[start_x: end_x, start_y: end_y]

    return crop_image, crop_image_copy


def table_exists(crop_image, crop_image_copy):
    ret, thresh_value = cv2.threshold(crop_image, 180, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    table_count = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 250 and h > 120:     
            cv2.rectangle(crop_image_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            table_count += 1

    if table_count:
        return crop_image_copy
    return None


def resize_image(image):
    scale = 50
    height, width, channels = image.shape
    height = int(height*scale/100)
    width = int(width*scale/100)
    image = cv2.resize(image, (width, height))
    return image


def save_image(image):
    image = resize_image(image)
    image_path = os.path.join(APP_ROOT, "static", "image.jpg")
    cv2.imwrite(image_path, image)
    image_url = request.host_url + "static/image.jpg"
    return {"image_url": image_url}, 200


def detect_table():
    image_info = get_image()
    if image_info[-1] == 200:
        image, image_copy, status = image_info
        cropped_image, cropped_image_copy = crop_image(image, image_copy)
        table_info = table_exists(cropped_image, cropped_image_copy)
        if table_info is not None:
            return save_image(cropped_image_copy)
        else:
            return {"message": "table structure not found."}, 404
    else:
        return image_info
