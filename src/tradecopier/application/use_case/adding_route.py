import abc
from typing import List, Optional
from uuid import UUID

from tradecopier.application.domain.entities.router import Router
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (RouteStatus,
                                                          TerminalIdLen)
from tradecopier.application.repositories.router_repo import RouterRepo
from tradecopier.application.repositories.terminal_repo import TerminalRepo


class AddingRouteBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, router: Router):
        pass


class AddingRouteUseCase:
    def __init__(
        self,
        *,
        router_repo: RouterRepo,
        terminal_repo: TerminalRepo,
        boundary: AddingRouteBoundary
    ):

        self._router_repo = router_repo
        self._terminal_repo = terminal_repo
        self._boundary = boundary

    def execute(self, sources: List[str], destinations: List[str]):
        router = Router()
        for source, destination in zip(sources, destinations):
            src_terminal_id = None
            src_is_tail = False
            dst_terminal_id = None
            dst_is_tail = False
            if len(source) == TerminalIdLen:
                try:
                    src_terminal_id = UUID(source)
                except:
                    pass
            elif len(source) == 12:
                src_is_tail = True
            assert (
                src_is_tail or src_terminal_id is not None
            ), "incorrectly formed source"
            if len(destination) == TerminalIdLen:
                try:
                    dst_terminal_id = UUID(destination)
                except:
                    pass
            elif len(destination) == 12:
                dst_is_tail = True
            assert (
                dst_is_tail or dst_terminal_id is not None
            ), "incorrectly formed destination"
            assert (
                src_terminal_id is not None or dst_terminal_id is not None
            ), "both terminals are passed as tail"

            source_terminal: Optional[Terminal] = None
            destination_terminal: Optional[Terminal] = None
            route_status: RouteStatus
            if src_is_tail:
                source_terminal = self._terminal_repo.get_by_tail(source)
                route_status = RouteStatus.DESTINATION
            elif src_terminal_id is not None:
                source_terminal = self._terminal_repo.get(src_terminal_id)
            if dst_is_tail:
                destination_terminal = self._terminal_repo.get_by_tail(destination)
                route_status = RouteStatus.SOURCE
            elif dst_terminal_id is not None:
                destination_terminal = self._terminal_repo.get(dst_terminal_id)
            if src_terminal_id is not None and dst_terminal_id is not None:
                route_status = RouteStatus.BOTH

            if source_terminal is None or destination_terminal is None:
                continue
            router.add_route(
                source=source_terminal,
                destination=destination_terminal,
                status=route_status,
            )
        if len(router.routes) > 0:
            self._router_repo.save(router)
            self._boundary.present(router)
