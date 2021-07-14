import cv2
import numpy as np
from .getColumnService import get_columns
from .getRowService import get_rows


def table_exists(crop_image, crop_image_copy, debug=False):
    ret, thresh_value = cv2.threshold(crop_image, 180, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    table_count = 0
    table_data = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 250 and h > 120:
            temp_image = crop_image_copy.copy()

            temp_image = temp_image[y: y+h, x: x+w]

            column_coordinates = get_columns(temp_image, debug)

            row_coordinates = get_rows(temp_image, debug)

            cv2.rectangle(crop_image_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            table_count += 1

            tables = {}
            tables["table_{}".format(table_count)] = {
                "rows": row_coordinates,
                "columns": column_coordinates
            }

            table_data.append(tables)

    if table_count:
        return crop_image_copy, table_data
    return None
