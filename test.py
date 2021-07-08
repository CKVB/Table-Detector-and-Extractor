import cv2
import numpy as np
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

file = args.file

im1 = cv2.imread(file, 0)
im = cv2.imread(file)

height, width = im1.shape

threshold = 10
start_x, start_y = threshold*2, threshold
end_x, end_y = height-threshold, width-threshold

im1 = im1[start_x: end_x, start_y: end_y]
im = im[start_x: end_x, start_y: end_y]

ret, thresh_value = cv2.threshold(im1, 180, 255, cv2.THRESH_BINARY_INV)

kernel = np.ones((5, 5), np.uint8)
dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if w > 250 and h > 120:     
        cv2.rectangle(im, (x, y), (x+w, y+h), (0, 0, 255), 2)

scale = 50

height = int(height*scale/100)
width = int(width*scale/100)

im = cv2.resize(im, (width, height))
        
cv2.imshow("IMG", im)
cv2.waitKey(0)
