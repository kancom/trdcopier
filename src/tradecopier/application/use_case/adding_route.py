import abc
from typing import Any, Dict, List, Optional
from uuid import UUID

from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (RouteStatus,
                                                          TerminalIdLen,
                                                          TerminalType)
from tradecopier.application.repositories.route_repo import RouteRepo
from tradecopier.application.repositories.terminal_repo import TerminalRepo


class AddingRouteBoundary(metaclass=abc.ABCMeta):
    result: List[Dict[str, Any]] = []

    @abc.abstractmethod
    def present(self, result: Dict[str, Any]):
        pass


class AddingRouteUseCase:
    def __init__(
        self,
        *,
        route_repo: RouteRepo,
        terminal_repo: TerminalRepo,
        boundary: AddingRouteBoundary,
    ):

        self._route_repo = route_repo
        self._terminal_repo = terminal_repo
        self._boundary = boundary

    def execute(self, sources: List[str], destinations: List[str]):
        for source, destination in zip(sources, destinations):
            src_terminal_id = None
            src_is_tail = False
            dst_terminal_id = None
            dst_is_tail = False
            try:
                if len(source) == TerminalIdLen:
                    try:
                        src_terminal_id = UUID(source)
                    except:
                        raise ValueError(f"Can't interpret src:{source} as UUID")
                elif len(source) == 12:
                    src_is_tail = True
                assert (
                    src_is_tail or src_terminal_id is not None
                ), "incorrectly formed source"
                if len(destination) == TerminalIdLen:
                    try:
                        dst_terminal_id = UUID(destination)
                    except:
                        raise ValueError(f"Can't interpret dst:{destination} as UUID")
                elif len(destination) == 12:
                    dst_is_tail = True
                assert (
                    dst_is_tail or dst_terminal_id is not None
                ), "incorrectly formed destination"
                assert (
                    src_terminal_id is not None or dst_terminal_id is not None
                ), "both terminals are passed as tail"
            except Exception as e:
                self._boundary.present({"error": str(e)})
                continue

            source_terminal: Optional[Terminal] = None
            destination_terminal: Optional[Terminal] = None
            route_status: Optional[RouteStatus] = None
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
                self._boundary.present({"error": "Source or Destination wasn't found"})
                continue
            src_routes = self._route_repo.get_by_terminal_id(
                destination_terminal.terminal_id, term_type=TerminalType.SOURCE
            )
            dst_routes = self._route_repo.get_by_terminal_id(
                source_terminal.terminal_id, term_type=TerminalType.DESTINATION
            )
            try:
                assert (
                    len(src_routes) == 0
                ), f"{destination_terminal.str_id} has type SOURCE and can't be used as destination"
                assert (
                    len(dst_routes) == 0
                ), f"{source_terminal.str_id} has type DESTINATION and can't be used as source"
                assert (
                    source_terminal.terminal_id != destination_terminal.terminal_id
                ), "The same terminal can't be used as both src and dst"
                assert route_status is not None, "Can't identify route status"
                route = Route(
                    source=source_terminal,
                    destination=destination_terminal,
                    status=route_status,
                )
            except Exception as e:
                self._boundary.present({"error": str(e)})
                continue
            self._route_repo.save(route)
