import injector
from tradecopier.application.repositories.router_repo import RouterRepo
from tradecopier.application.repositories.terminal_repo import TerminalRepo
from tradecopier.application.use_case.adding_route import (AddingRouteBoundary,
                                                           AddingRouteUseCase)

__all__ = ["AddingRouteUseCase", "WebApp"]


class WebApp(injector.Module):
    @injector.provider
    def adding_route_uc(
        self,
        router_repo: RouterRepo,
        terminal_repo: TerminalRepo,
        boundary: AddingRouteBoundary,
    ) -> AddingRouteUseCase:
        return AddingRouteUseCase(
            router_repo=router_repo, terminal_repo=terminal_repo, boundary=boundary
        )
