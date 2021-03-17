from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from tradecopier.application import AddingRoutePresenter, AddingRouteUseCase
from tradecopier.infrastructure import (SqlAlchemyRouteRepo,
                                        SqlAlchemyRuleRepo,
                                        SqlAlchemyTerminalRepo)


class Db:
    def __init__(self, db_dsn: str) -> None:
        assert db_dsn is not None and len(db_dsn) > 5, f"dsn: {db_dsn}"
        self._engine = create_engine(db_dsn, echo=True)

    def connection(self) -> Connection:
        return self._engine.connect()

    # def session(self, connection: Connection) -> Session:
    #     return Session(bind=connection)


class Jwt_current_user:
    def __init__(self, secret_key: str):
        self._secret_key = secret_key

    def __call__(self):
        return "13121"


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(Db, db_dsn=config.db_dsn)

    route_repo = providers.Factory(
        SqlAlchemyRouteRepo, conn=db.provided.connection.call()
    )
    rule_repo = providers.Factory(
        SqlAlchemyRuleRepo, conn=db.provided.connection.call()
    )
    terminal_repo = providers.Factory(
        SqlAlchemyTerminalRepo, conn=db.provided.connection.call()
    )
    adding_route_presenter = providers.Factory(AddingRoutePresenter)
    adding_route_uc = providers.Factory(
        AddingRouteUseCase,
        route_repo=route_repo,
        terminal_repo=terminal_repo,
        boundary=adding_route_presenter,
    )
    current_user = providers.Factory(Jwt_current_user, config.secret_key)
