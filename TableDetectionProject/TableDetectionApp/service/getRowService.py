import cv2
import os
import numpy as np
from operator import itemgetter


APP_ROOT = os.path.dirname(os.path.abspath(__file__)).split("service")[0]


def get_rows(*args):
    temp_image, debug = args
    kernel_len = np.array(temp_image).shape[1]//100
    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
    img_bin = cv2.bitwise_not(temp_image)
    image_horizantal = cv2.erode(img_bin, hor_kernel, iterations=5)
    horizantal_lines = cv2.dilate(image_horizantal, hor_kernel, iterations=5)
    edges = cv2.Canny(horizantal_lines, 150, 350, apertureSize=5)
    lines_h = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=120, maxLineGap=20)

    total_horizantal_lines = []
    cnt = 0
    for line in lines_h:
        x1, y1, x2, y2 = line[0]
        cnt += 1
        points = (x1, y1, x2, y2)
        total_horizantal_lines.append(points)

    total_horizantal_lines = sorted(total_horizantal_lines, key=itemgetter(1))
    required_horizantal_lines = []
    if debug:
        print(total_horizantal_lines)

    required_horizantal_lines.append(total_horizantal_lines[0])

    i, j = 0, 0 
    while i < len(total_horizantal_lines):
        flag = 0
        point1 = total_horizantal_lines[i][1]
        j = i + 1
        while j < len(total_horizantal_lines):
            point2 = total_horizantal_lines[j][1]
            if(point2-point1) > 10:
                required_horizantal_lines.append(total_horizantal_lines[j])
                i = j
                flag = 1
                break
            j += 1
        if not flag:
            i += 1

    cnt2 = 0
    if debug:
        print(required_horizantal_lines)
    for line in required_horizantal_lines:
        x1, y1, x2, y2 = line
        cnt2 += 1
        if debug:
            cv2.line(temp_image, (x1, y1), (x2, y2), (0, 0, 255), 5)
            cv2.imshow("IMG", temp_image)
            cv2.waitKey(0)

    rows = []
    for i in range(len(required_horizantal_lines)-1):
        line1, line2 = required_horizantal_lines[i], required_horizantal_lines[i+1]
        rows.append([(line1[1], line2[1]), (line1[0], line2[-2])])

    row_count = 0
    row_coordinates = []
    for row in rows:
        y_start, y_end = map(int, row[0])
        x_start, x_end = map(int, row[1])
        
        row_count += 1
        row_data = {}
        row_data["row_{}".format(row_count)] = {
            "x_start": x_start,
            "x_end": x_end,
            "y_start": y_start,
            "y_end": y_end
        }
        
        row_coordinates.append(row_data)

        if debug:
            temp_image2 = temp_image[y_start: y_end, x_start: x_end]
            cv2.imshow("ROW", temp_image2)
            cv2.waitKey(0)
    if debug:
        horizantal_image = os.path.join(APP_ROOT, "static", "horizantal.png")
        cv2.imwrite(horizantal_image, horizantal_lines)

    return row_coordinates
