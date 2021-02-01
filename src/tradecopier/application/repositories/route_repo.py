import abc
from typing import List

from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.value_objects import (RouteId, TerminalId,
                                                          TerminalType)


class RouteRepo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, route_id: RouteId) -> Route:
        pass

    @abc.abstractmethod
    def delete(self, route_id: RouteId) -> None:
        pass

    @abc.abstractmethod
    def save(self, route: Route) -> RouteId:
        pass

    @abc.abstractmethod
    def get_by_terminal_id(
        self, terminal_id: TerminalId, term_type: TerminalType
    ) -> List[Route]:
        pass
