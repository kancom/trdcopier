import injector
from sqlalchemy.engine import Connection
from tradecopier.application.repositories.router_repo import RouterRepo
from tradecopier.application.repositories.terminal_repo import TerminalRepo
from tradecopier.infrastructure.repositories.router_repo import \
    SqlAlchemyRouterRepo
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo


class WebAppInfra(injector.Module):
    @injector.provider
    def terminal_repo(self, conn: Connection) -> TerminalRepo:
        return SqlAlchemyTerminalRepo(conn)

    @injector.provider
    def router_repo(self, conn: Connection) -> RouterRepo:
        return SqlAlchemyRouterRepo(conn)
