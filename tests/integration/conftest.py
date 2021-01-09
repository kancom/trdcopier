import pytest
from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.schema import CreateTable, DropTable
from tradecopier.infrastructure.repositories.sql_model import (RouterModel,
                                                               TerminalModel)


@pytest.fixture(scope="session")
def sql_conn():
    engine = create_engine("sqlite:///testdb.db", echo=True)
    db_conn = engine.connect()
    yield db_conn


@pytest.fixture(scope="session")
def create_table_by_model(sql_conn):
    def inner(model):
        creation_sql = CreateTable(model)
        sql_conn.execute(creation_sql)

    return inner


@pytest.fixture(scope="session")
def drop_table_by_model(sql_conn):
    def inner(model):
        creation_sql = DropTable(model)
        sql_conn.execute(creation_sql)

    return inner


@pytest.fixture(scope="session")
def create_table(create_table_by_model, drop_table_by_model):
    def inner(table_model):
        # try:
        create_table_by_model(table_model)
        # except OperationalError as e:
        #     drop_table_by_model(table_model)
        #     # raise Exception(str(e)) from e
        yield
        drop_table_by_model(table_model)

    return inner


@pytest.fixture(scope="session")
def terminal_table(create_table_by_model, drop_table_by_model):
    table_model = TerminalModel
    try:
        create_table_by_model(table_model)
    except OperationalError as e:
        drop_table_by_model(table_model)
        raise Exception(str(e)) from e
    yield
    drop_table_by_model(table_model)


@pytest.fixture(scope="session")
def router_table(create_table_by_model, drop_table_by_model):
    table_model = RouterModel
    try:
        create_table_by_model(table_model)
    except OperationalError as e:
        drop_table_by_model(table_model)
        raise Exception(str(e)) from e
    yield
    drop_table_by_model(table_model)
