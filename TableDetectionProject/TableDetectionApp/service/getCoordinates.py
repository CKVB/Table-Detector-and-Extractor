import cv2
import os
import numpy as np
from operator import itemgetter


APP_ROOT = os.path.dirname(os.path.abspath(__file__)).split("service")[0]


def get_lines(*args):
    temp_image, debug, line_type = args
    scale = 25
    if line_type == "rows":
        index = 1
        kernel_len = np.array(temp_image).shape[index]//scale
        kernel_size = (kernel_len, 1)
        color = (0, 0, 255)
    else:
        index = 0
        kernel_len = np.array(temp_image).shape[index]//scale
        kernel_size = (1, kernel_len)
        color = (0, 255, 0)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    img_bin = cv2.bitwise_not(temp_image)
    image_erode = cv2.erode(img_bin, kernel, iterations=5)
    image_lines = cv2.dilate(image_erode, kernel, iterations=5)
    edges = cv2.Canny(image_lines, 150, 350, apertureSize=3)

    if debug:
        cv2.imshow("edges", edges)
        cv2.waitKey(0)

    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=120, maxLineGap=20)

    total_lines = []

    for line in lines:
        x_start, y_start, x_end, y_end = line[0]
        points = (x_start, y_start, x_end, y_end)
        total_lines.append(points)

    total_lines = sorted(total_lines, key=itemgetter(index))  # row 1 column 0
   
    if debug:
        print(total_lines)

    required_lines = []
    required_lines.append(total_lines[0])

    i, j = 0, 0 
    while i < len(total_lines):
        flag = 0
        point1 = total_lines[i][index]  # row 1 column 0
        j = i + 1
        while j < len(total_lines):
            point2 = total_lines[j][index]  # row 1 column 0
            if(point2-point1) > 10:
                required_lines.append(total_lines[j])
                i = j
                flag = 1
                break
            j += 1
        if not flag:
            i += 1

    if debug:
        print(required_lines)
        for line in required_lines:
            x_start, y_start, x_end, y_end = line
            cv2.line(temp_image, (x_start, y_start), (x_end, y_end), color, 5)
            cv2.imshow("IMG", temp_image)
            cv2.waitKey(0)

    lines = []
    for i in range(len(required_lines)-1):
        line1, line2 = required_lines[i], required_lines[i+1]
        y_start, y_end = (line1[-1], line2[1])
        x_start, x_end = (line1[0], line2[-2] if line_type == "rows" else line2[0])
        lines.append([(y_start, y_end), (x_start, x_end)])

    coordinates = []

    for count, line in enumerate(lines):
        y_start, y_end = map(int, line[0])
        x_start, x_end = map(int, line[1])
        
        data = {}

        data["{}".format(count)] = {
            "x_start": x_start,
            "x_end": x_end,
            "y_start": y_start,
            "y_end": y_end
        }
        
        coordinates.append(data)

        if debug:
            temp_image2 = temp_image[y_start: y_end, x_start: x_end]
            cv2.imshow("ROW", temp_image2)
            cv2.waitKey(0)
            
    if debug:
        image = os.path.join(APP_ROOT, "static", f"{line_type}.png")
        cv2.imwrite(image, image_lines)

    return coordinates
