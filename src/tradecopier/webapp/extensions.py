from flask import Flask, current_app, request
from flask_babel import Babel
from flask_bootstrap import Bootstrap as TwitterBootsrap
from flask_pydantic_spec import FlaskPydanticSpec

babel = Babel()
bootstrap = TwitterBootsrap()
specs = FlaskPydanticSpec("flask")


def setup_extension(app: Flask):
    babel.init_app(app)
    bootstrap.init_app(app)
    specs.register(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])
