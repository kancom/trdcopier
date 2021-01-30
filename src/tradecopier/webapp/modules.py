import injector
from flask import Flask
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session


class Db(injector.Module):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    # @injector.singleton
    @injector.provider
    def connection(self) -> Connection:
        return self._engine.connect()

    # @injector.singleton
    @injector.provider
    def session(self, connection: Connection) -> Session:
        return Session(bind=connection)


# class BabelMod(injector.Module):
#     def __init__(self, app: Flask):
#         self._app = app

#     @injector.singleton
#     @injector.provider
#     def babel(self) -> Babel:
#         return Babel(self._app)


# class FlaskLoginMod(injector.Module):
#     def __init__(self, app: Flask):
#         self._app = app

#     @injector.singleton
#     @injector.provider
#     def login(self) -> LoginManager:
#         return LoginManager(self._app)
