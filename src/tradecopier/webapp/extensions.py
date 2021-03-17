from flask import Flask, current_app, request
from flask_babel import Babel
from flask_bootstrap import Bootstrap as TwitterBootsrap

babel = Babel()
bootstrap = TwitterBootsrap()


def setup_extension(app: Flask):
    babel.init_app(app)
    bootstrap.init_app(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])
