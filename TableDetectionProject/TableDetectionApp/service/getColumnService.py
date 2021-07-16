import cv2
import os
import numpy as np
from operator import itemgetter


APP_ROOT = os.path.dirname(os.path.abspath(__file__)).split("service")[0]


def get_columns(*args):
    temp_image, debug = args
    kernel_len = np.array(temp_image).shape[1]//100
    ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
    img_bin = cv2.bitwise_not(temp_image)
    image_vertical = cv2.erode(img_bin, ver_kernel, iterations=5)
    vertical_lines = cv2.dilate(image_vertical, ver_kernel, iterations=5)
    edges = cv2.Canny(vertical_lines, 150, 350, apertureSize=5)
    lines_v = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=120, maxLineGap=20)

    total_vertical_lines = []
    cnt = 0
    for line in lines_v:
        x1, y1, x2, y2 = line[0]
        cnt += 1
        points = (x1, y1, x2, y2)
        total_vertical_lines.append(points)

    total_vertical_lines = sorted(total_vertical_lines, key=itemgetter(0))
    required_vertical_lines = []
    if debug:
        print(total_vertical_lines)

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

    cnt2 = 0
    if debug:
        print(required_vertical_lines)
    for line in required_vertical_lines:
        x1, y1, x2, y2 = line
        cnt2 += 1
        if debug:
            cv2.line(temp_image, (x1, y1), (x2, y2), (0, 255, 0), 5)
            cv2.imshow("IMG", temp_image)
            cv2.waitKey(0)

    columns = []
    for i in range(len(required_vertical_lines)-1):
        line1, line2 = required_vertical_lines[i], required_vertical_lines[i+1]
        columns.append([(line1[-1], line1[1]), (line1[-2], line2[-2])])

    column_count = 0
    column_coordinates = []    

    for column in columns:
        y_start, y_end = map(int, column[0])
        x_start, x_end = map(int, column[1])

        column_count += 1
        column_data = {}

        column_data["column_{}".format(column_count)] = {
            "x_start": x_start,
            "x_end": x_end,
            "y_start": y_start,
            "y_end": y_end
        }

        column_coordinates.append(column_data)
        
        if debug:
            temp_image2 = temp_image[y_start: y_end, x_start: x_end]
            cv2.imshow("COL", temp_image2)
            cv2.waitKey(0)

    if debug:
        vertical_image = os.path.join(APP_ROOT, "static", "vertical.png")
        cv2.imwrite(vertical_image, vertical_lines)

    return column_coordinates
