import injector
from sqlalchemy.engine import Connection
from tradecopier.application.repositories.route_repo import RouteRepo
from tradecopier.application.repositories.rule_repo import RuleRepo
from tradecopier.application.repositories.terminal_repo import TerminalRepo
from tradecopier.infrastructure.repositories.route_repo import \
    SqlAlchemyRouteRepo
from tradecopier.infrastructure.repositories.rule_repo import \
    SqlAlchemyRuleRepo
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo


class WebAppInfra(injector.Module):
    @injector.provider
    def terminal_repo(self, conn: Connection) -> TerminalRepo:
        return SqlAlchemyTerminalRepo(conn)

    @injector.provider
    def route_repo(self, conn: Connection) -> RouteRepo:
        return SqlAlchemyRouteRepo(conn)

    @injector.provider
    def rule_repo(self, conn: Connection) -> RuleRepo:
        return SqlAlchemyRuleRepo(conn)
