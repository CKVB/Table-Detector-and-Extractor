from .getImageService import get_image
from .cropImageService import crop_image
from .saveImageService import save_image
from .getColumnService import get_columns


services = {
    "GET_IMAGE": get_image,
    "CROP_IMAGE": crop_image,
    "SAVE_IMAGE": save_image,
    "GET_COLUMNS": get_columns,
}


def get_service(service, *args):
    return services.get(service)(*args)
