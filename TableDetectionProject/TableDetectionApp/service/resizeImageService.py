import cv2


def resize_image(image):
    scale = 81
    height, width, channels = image.shape
    height = int(height*scale/100)
    width = int(width*scale/100)
    image = cv2.resize(image, (width, height))
    return image
