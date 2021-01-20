import os
from dataclasses import dataclass

import dotenv
import injector
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from tradecopier.application import WebApp
from tradecopier.webapp.modules import Db


@dataclass
class AppContext:
    injector: injector.Injector


def bootstrap_app() -> AppContext:
    config_path = os.environ.get(
        "CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env_file"),
    )
    dotenv.load_dotenv(config_path)
    settings = {
        "payments.login": os.environ["PAYMENTS_LOGIN"],
    }
    engine = create_engine(os.environ["DB_DSN"])
    dependency_injector = _setup_dependency_injection(settings, engine)
    # _setup_orm_events(dependency_injector)

    _create_db_schema(engine)  # TEMPORARY

    return AppContext(dependency_injector)


def _setup_dependency_injection(settings: dict, engine: Engine) -> injector.Injector:
    return injector.Injector(
        [Db(engine), WebApp()],
        auto_bind=False,
    )


def _create_db_schema(engine: Engine) -> None:
    from tradecopier.infrastructure.repositories.sql_model import (
        FilterSetModel, RouterModel, TerminalModel, metadata)

    # TODO: Use migrations for that
    metadata.create_all(engine)
