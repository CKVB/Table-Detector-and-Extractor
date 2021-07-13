import numpy as np
import cv2
import os
from operator import itemgetter
from ..service import get_image, crop_image, save_image

APP_ROOT = os.path.dirname(os.path.abspath(__file__)).split("routes")[0]


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

            edges = cv2.Canny(vertical_lines, 150, 350, apertureSize=5)

            lines_v = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=120, maxLineGap=20)

            total_vertical_lines = []

            cnt = 0
            for line in lines_v:
                x1, y1, x2, y2 = line[0]
                cnt += 1
                points = (x1, y1, x2, y2)
                total_vertical_lines.append(points)
                # cv2.line(temp_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            total_vertical_lines = sorted(total_vertical_lines, key=itemgetter(0))
            required_vertical_lines = []
            print(total_vertical_lines)

            # for i in range(len(total_vertical_lines)):
            #     point1 = total_vertical_lines[i][0]
            #     for j in range(i+1, len(total_vertical_lines)):
            #         point2 = total_vertical_lines[j][0]
            #         if point2-point1 < 10:
            #             required_vertical_lines.add(total_vertical_lines[j])

            required_vertical_lines.append(total_vertical_lines[0])
            i, j = 0, 0 
            while i < len(total_vertical_lines):
                flag = 0
                point1 = total_vertical_lines[i][0]
                j = i + 1
                while j < len(total_vertical_lines):
                    point2 = total_vertical_lines[j][0]
                    if(point2-point1) > 10:
                        required_vertical_lines.append(total_vertical_lines[j])
                        i = j
                        flag = 1
                        break
                    j += 1
                if not flag:
                    i += 1

            # data = [(1, 293, 1, 2), (156, 291, 156, 4), (248, 290, 248, 3), (350, 291, 350, 4), (454, 291, 454, 4), (569, 290, 569, 6)]
            cnt2 = 0
            #required_vertical_lines = sorted(required_vertical_lines, key=itemgetter(0))
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
