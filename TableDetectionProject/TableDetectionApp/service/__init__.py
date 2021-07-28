from .getImageService import get_image
from .saveImageService import save_image
from .getTableService import table_exists


services = {
    "GET_IMAGE": get_image,
    "GET_TABLES": table_exists,
    "SAVE_IMAGE": save_image,
}


def get_service(service, *args):
    return services.get(service)(*args)
