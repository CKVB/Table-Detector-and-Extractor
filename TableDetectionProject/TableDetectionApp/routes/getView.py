from .indexView import index
from .detectTableView import detect_table


views = {
    "INDEX": index,
    "DETECT_TABLE": detect_table,
}


def get_view(view, *args):
    return views.get(view)(*args)
