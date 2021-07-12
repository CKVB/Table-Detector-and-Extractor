import numpy as np
import cv2
import os
import requests
from flask import request
from operator import itemgetter


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
            temp_image = crop_image.copy()

            temp_image = temp_image[y: y+h, x: x+w]
            cv2.imwrite("sample.png", temp_image)

            kernel_len = np.array(temp_image).shape[1]//100
            
            ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
            # hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
            
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

            img_bin = cv2.bitwise_not(temp_image)

            image_vertical = cv2.erode(img_bin, ver_kernel, iterations=5)
            vertical_lines = cv2.dilate(image_vertical, ver_kernel, iterations=5)

            # image_horizantal = cv2.erode(img_bin, hor_kernel, iterations=5)
            # horizantal_lines = cv2.dilate(image_horizantal, hor_kernel, iterations=5)

            kernel = np.ones((15, 1), np.uint8)
            morph = cv2.morphologyEx(vertical_lines, cv2.MORPH_OPEN, kernel)
            kernel = np.ones((17, 3), np.uint8)
            morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)

            edges = cv2.Canny(vertical_lines, 150, 350, apertureSize=5)

            lines_v = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=120, maxLineGap=20)

            total_vertical_lines = []

            cnt = 0
            for line in lines_v:
                x1, y1, x2, y2 = line[0]
                cnt += 1
                points = (x1, y1, x2, y2)
                total_vertical_lines.append(points)
                #cv2.line(temp_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            total_vertical_lines = sorted(total_vertical_lines, key=itemgetter(0))
            required_vertical_lines = []

            for i in range(len(total_vertical_lines)):
                point1 = total_vertical_lines[i][0]
                for j in range(i+1, len(total_vertical_lines)):
                    point2 = total_vertical_lines[j][0]
                    if point2-point1 < 10:
                        required_vertical_lines.append(total_vertical_lines[j])

            # data = [(1, 293, 1, 2), (156, 291, 156, 4), (248, 290, 248, 3), (350, 291, 350, 4), (454, 291, 454, 4), (569, 290, 569, 6)]
            cnt2 = 0
            print(required_vertical_lines)
            for line in required_vertical_lines:
                x1, y1, x2, y2 = line
                cnt2 += 1
                cv2.line(temp_image, (x1, y1), (x2, y2), (0, 255, 0), 10)

            print("Lines", cnt)
            print("Lines2", cnt2)
            cv2.imshow("IMG", temp_image)
            cv2.waitKey(0)
            
            # image_2 = cv2.erode(img_bin, hor_kernel, iterations=3)
            # horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)

            # horizontal_image = os.path.join(APP_ROOT, "static", "horizantal.png")
            vertical_image = os.path.join(APP_ROOT, "static", "vertical.png")

            # cv2.imwrite(horizontal_image, horizontal_lines)
            cv2.imwrite(vertical_image, vertical_lines)

            cv2.rectangle(crop_image_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            table_count += 1

    if table_count:
        return crop_image_copy
    return None


def resize_image(image):
    scale = 81
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
