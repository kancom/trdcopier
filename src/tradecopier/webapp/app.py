import os

from flask import Flask
from flask_injector import FlaskInjector
from tradecopier.application import RouteBoundaryWeb
from tradecopier.webapp import bootstrap_app
from tradecopier.webapp.blueprints.main import main_blueprint
from tradecopier.webapp.extensions import setup_extension


def create_app() -> Flask:

    app = Flask(__name__)

    app.register_blueprint(main_blueprint, url_prefix="/routes")
    config_path = os.environ.get(
        "CONFIG_PATH",
        os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, ".env"
        ),
    )
    app.config.from_pyfile(config_path)
    setup_extension(app)
    app_context = bootstrap_app(app)
    FlaskInjector(app, modules=[RouteBoundaryWeb()], injector=app_context.injector)
    app.injector = app_context.injector
    return app
