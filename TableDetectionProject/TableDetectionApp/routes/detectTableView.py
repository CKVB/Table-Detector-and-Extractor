from ..service import get_service
from flask import current_app


def detect_table():
    
    image_info = get_service("GET_IMAGE")

    debug = False

    if image_info[-1] == 200:
        image_gray, image_copy, status = image_info
        
        table_info = get_service("GET_TABLES", image_gray, image_copy, debug)

        if table_info is not None:
            image_copy, table_data = table_info
            image_url = get_service("SAVE_IMAGE", image_copy)
            return {"image_url": image_url, "tables": table_data}, 200
        else:
            current_app.logger.warning("Table structure not found.")
            return {"message": "table structure not found."}, 404
    else:
        return image_info
