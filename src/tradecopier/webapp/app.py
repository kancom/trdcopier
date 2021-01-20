from typing import Optional

from flask import Flask, Response, request
from flask_injector import FlaskInjector
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session
from tradecopier.webapp import bootstrap_app
from tradecopier.webapp.blueprints.main import (RouterBoundaryWeb,
                                                main_blueprint)


def create_app() -> Flask:

    app = Flask(__name__)

    app.register_blueprint(main_blueprint, url_prefix="/routes")

    app.config["SECRET_KEY"] = "super-secret"
    app.config["DEBUG"] = True
    app_context = bootstrap_app()
    FlaskInjector(app, modules=[RouterBoundaryWeb()], injector=app_context.injector)
    app.injector = app_context.injector
    return app
