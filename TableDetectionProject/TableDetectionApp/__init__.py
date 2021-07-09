import flask


def create_app(configuartion_file="settings.py"):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(configuartion_file)
    with app.app_context():
        from .views import table_api, swagger_api
        app.register_blueprint(table_api)
        app.register_blueprint(swagger_api)
        return app
