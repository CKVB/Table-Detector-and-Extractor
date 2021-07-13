def crop_image(image, image_copy):

    height, width = image.shape

    threshold = 10
    start_x, start_y = threshold*2, threshold
    end_x, end_y = height-threshold, width-threshold

    crop_image = image[start_x: end_x, start_y: end_y]
    crop_image_copy = image_copy[start_x: end_x, start_y: end_y]

    return crop_image, crop_image_copy
