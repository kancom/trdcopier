from typing import Any, Dict, List, Optional

import flask_injector
import injector

from .domain.entities.terminal import Terminal
from .repositories.route_repo import RouteRepo
from .repositories.terminal_repo import TerminalRepo
from .use_case.adding_route import AddingRouteBoundary, AddingRouteUseCase

__all__ = ["AddingRouteUseCase", "WebApp"]


class AddingRoutePresenter(AddingRouteBoundary):
    def present(self, result: Dict[str, Any]):
        self.result.append(result)


class RouteBoundaryWeb(injector.Module):
    @injector.provider
    @flask_injector.request
    def adding_route_boundary(self) -> AddingRouteBoundary:
        return AddingRoutePresenter()


class WebApp(injector.Module):
    @injector.provider
    def adding_route_uc(
        self,
        route_repo: RouteRepo,
        terminal_repo: TerminalRepo,
        boundary: AddingRouteBoundary,
    ) -> AddingRouteUseCase:
        return AddingRouteUseCase(
            route_repo=route_repo, terminal_repo=terminal_repo, boundary=boundary
        )
