import cv2
import requests
import os
import numpy as np
from flask import request


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
