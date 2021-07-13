import flask
from flask_swagger_ui import get_swaggerui_blueprint
from .routes.getView import get_view


swagger_url_prefix = "/swagger"
swagger_file_path = "/static/swagger_doc.yml"
swagger_api = get_swaggerui_blueprint(swagger_url_prefix, swagger_file_path)

table_api = flask.Blueprint("table_api", __name__)


@table_api.get("/")
def index():
    return flask.redirect("swagger")


@table_api.post("/detect_table")
def detect_table():
    return get_view("DETECT_TABLE")
