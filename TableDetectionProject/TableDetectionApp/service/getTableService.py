import cv2
import numpy as np
from .getCoordinates import get_lines


def table_exists(image_gray, image_copy, debug=False):
    ret, thresh_value = cv2.threshold(image_gray, 220, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    table_count = 0
    table_data = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 250 and h > 120:

            y_start, y_end = y, y+h
            x_start, x_end = x, x+w

            boundry = (x_start, y_start, x_end, y_end)

            try:
                temp_image = image_copy.copy()
                column_coordinates, updated_boundry = get_lines(temp_image, boundry, None, None, debug, "columns")
                x_start, y_start, x_end, y_end = map(int, updated_boundry)
            except Exception:
                return None
            else:
                try:
                    temp_image = image_copy.copy()
                    updated_xstart = updated_boundry[0]
                    updated_xend = updated_boundry[2]
                    row_coordinates = get_lines(temp_image, boundry, updated_xstart, updated_xend, debug, "rows")
                except Exception:
                    return None

                cv2.rectangle(image_copy, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)

                tables = {}
                tables["{}".format(table_count)] = {
                    "x_start": x_start,
                    "x_end": x_end,
                    "y_start": y_start,
                    "y_end": y_end,
                    "rows": row_coordinates,
                    "columns": column_coordinates
                }
                table_count += 1

                table_data.append(tables)

    if table_count:
        return image_copy, table_data
    return None
