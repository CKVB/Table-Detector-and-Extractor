import os
import cv2
from flask import request
from .resizeImageService import resize_image

APP_ROOT = os.path.dirname(os.path.abspath(__file__)).split("service")[0]


def save_image(*args):

    image, = args

    image = resize_image(image)
    image_path = os.path.join(APP_ROOT, "static", "image.jpg")
    cv2.imwrite(image_path, image)
    image_url = request.host_url + "static/image.jpg"
    return {"image_url": image_url}, 200
