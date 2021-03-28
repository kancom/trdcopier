from typing import Any, Dict

from .domain.entities.order import Order
from .domain.entities.rule import (ComplexRule, Expression, FilterRule,
                                   TransformRule)
from .domain.entities.terminal import Terminal
from .repositories.route_repo import RouteRepo
from .repositories.rule_repo import RuleRepo
from .repositories.terminal_repo import TerminalRepo
from .use_case.adding_route import AddingRouteBoundary, AddingRouteUseCase

__all__ = [
    "AddingRouteUseCase",
    "AddingRoutePresenter",
    "ComplexRule",
    "TerminalRepo",
    "RouteRepo",
    "RuleRepo",
    "Terminal",
    "FilterRule",
    "TransformRule",
    "Expression",
    "Order",
]


class AddingRoutePresenter(AddingRouteBoundary):
    def present(self, result: Dict[str, Any]):
        self.result.append(result)
