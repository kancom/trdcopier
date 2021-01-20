
import injector
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session


class Db(injector.Module):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @injector.provider
    def connection(self) -> Connection:
        return self._engine.connect()

    @injector.provider
    def session(self, connection: Connection) -> Session:
        return Session(bind=connection)
