from .getImageService import get_image
from .cropImageService import crop_image
from .saveImageService import save_image
from .getTableService import table_exists


services = {
    "GET_IMAGE": get_image,
    "CROP_IMAGE": crop_image,
    "SAVE_IMAGE": save_image,
    "GET_TABLES": table_exists
}


def get_service(service, *args):
    return services.get(service)(*args)
