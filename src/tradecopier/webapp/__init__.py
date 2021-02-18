import os
from dataclasses import dataclass
from typing import Any, Dict

import dotenv
import injector
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from tradecopier.application import WebApp
from tradecopier.infrastructure import WebAppInfra
from tradecopier.webapp.modules import Db


@dataclass
class AppContext:
    injector: injector.Injector


def bootstrap_app(app: Flask) -> AppContext:
    config_path = os.environ.get(
        "CONFIG_PATH",
        os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, ".env"
        ),
    )
    assert dotenv.load_dotenv(dotenv_path=config_path)
    engine = create_engine(os.environ["DB_DSN"])
    dependency_injector = _setup_dependency_injection(app, engine)

    _create_db_schema(engine)  # TEMPORARY

    return AppContext(dependency_injector)


def _setup_dependency_injection(app: Flask, engine: Engine) -> injector.Injector:
    return injector.Injector(
        [
            Db(engine),
            WebApp(),
            WebAppInfra(),
        ],
        auto_bind=False,
    )


def _create_db_schema(engine: Engine) -> None:
    from tradecopier.infrastructure.repositories.sql_model import (
        RouteModel, RuleModel, TerminalModel, metadata)

    # TODO: Use migrations for that
    metadata.create_all(engine)
