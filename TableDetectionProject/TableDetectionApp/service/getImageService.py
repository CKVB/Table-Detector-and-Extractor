import cv2
import requests
import os
import numpy as np
from flask import request
from flask import current_app


def get_image():
    data = request.get_json()
    url = data["image_url"]

    if "http" in url:
        try:
            response = requests.get(url, stream=True).raw
        except Exception:
            current_app.logger.error("Invalid URL")
            return {"error": "invalid url."}, 400
        else:
            if response.status == 404:
                current_app.logger.error("File Not Found")
                return {"error": "file not found."}, 404
            image = np.asarray(bytearray(response.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            image = np.array(image)
    else:
        image_file_path = os.path.isfile(url)
        if image_file_path:
            image = cv2.imread(url)
        else:
            current_app.logger.error("File Not Found")
            return {"error": "file not found."}, 404
    image_copy = image.copy()
    try:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception:
        current_app.logger.error("Request not processable")
        return {"error": "request not processable."}, 422
    else:
        return image_gray, image_copy, 200
