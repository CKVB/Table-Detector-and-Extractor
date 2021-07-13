import numpy as np
import cv2
import os
from ..service import get_service

APP_ROOT = os.path.dirname(os.path.abspath(__file__)).split("routes")[0]


def table_exists(crop_image, crop_image_copy):
    ret, thresh_value = cv2.threshold(crop_image, 180, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    table_count = 0
    debug = False

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 250 and h > 120:
            temp_image = crop_image_copy.copy()

            temp_image = temp_image[y: y+h, x: x+w]

            get_service("GET_COLUMNS", temp_image, debug)

            get_service("GET_ROWS", temp_image, debug)

            cv2.rectangle(crop_image_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            table_count += 1

    if table_count:
        return crop_image_copy
    return None


def detect_table():
    image_info = get_service("GET_IMAGE")
    if image_info[-1] == 200:
        image, image_copy, status = image_info
        cropped_image, cropped_image_copy = get_service("CROP_IMAGE", image, image_copy)
        table_info = table_exists(cropped_image, cropped_image_copy)
        if table_info is not None:
            return get_service("SAVE_IMAGE", cropped_image_copy)
        else:
            return {"message": "table structure not found."}, 404
    else:
        return image_info
