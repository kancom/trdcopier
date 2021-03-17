import itertools
import operator

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response, status
from tradecopier.application import AddingRouteUseCase, RouteRepo, Terminal
from tradecopier.application.domain.value_objects import TerminalType
from tradecopier.restapi.deps import Container

from ...dto.objects import RoutePeer, RoutesPresenter
from .auth import get_current_active_terminal

router = APIRouter()


@router.get("/terminal", response_model=Terminal)
@inject
def current_terminal(
    terminal: Terminal = Depends(get_current_active_terminal),
):
    return terminal


@router.get("/routes", response_model=RoutesPresenter)
@inject
def routes(
    terminal: Terminal = Depends(get_current_active_terminal),
    route_repo: RouteRepo = Depends(Provide(Container.route_repo)),
):
    term_type = TerminalType.UNKNOWN
    src_routes = route_repo.get_by_terminal_id(
        terminal.terminal_id, term_type=TerminalType.SOURCE
    )
    dst_routes = route_repo.get_by_terminal_id(
        terminal.terminal_id, term_type=TerminalType.DESTINATION
    )
    if len(dst_routes) > 0:
        term_type = TerminalType.DESTINATION
        routes = dst_routes
        term_getter = operator.attrgetter("source")
    elif len(src_routes) > 0:
        term_type = TerminalType.SOURCE
        routes = src_routes
        term_getter = operator.attrgetter("destination")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no routes found"
        )

    peers = []
    for route in routes:
        peer_terminal: Terminal = term_getter(route)
        peer = RoutePeer(
            route_id=route.route_id,
            status=route.status,
            terminal_brand=peer_terminal.terminal_brand,
            verbose_name=peer_terminal.str_id,
        )
        peers.append(peer)
    presenter = RoutesPresenter(
        current_terminal=terminal,
        peers_type="sources"
        if term_type == TerminalType.DESTINATION
        else "destinations",
        peers=peers,
    )
    return presenter
