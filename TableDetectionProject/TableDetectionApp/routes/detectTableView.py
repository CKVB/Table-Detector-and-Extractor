from ..service import get_service


def detect_table():
    
    image_info = get_service("GET_IMAGE")

    debug = True

    if image_info[-1] == 200:
        image, image_copy, status = image_info
        
        cropped_image, cropped_image_copy = get_service("CROP_IMAGE", image, image_copy)
        
        table_info = get_service("GET_TABLES", cropped_image, cropped_image_copy, debug)
        
        if table_info is not None:
            cropped_image_copy, table_data = table_info
            image_url = get_service("SAVE_IMAGE", cropped_image_copy)
            return {"image_url": image_url, "tables": table_data}, 200
        else:
            return {"message": "table structure not found."}, 404
    else:
        return image_info
