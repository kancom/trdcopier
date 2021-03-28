import operator
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from tradecopier.application import (Order, RouteRepo, RuleRepo, Terminal,
                                     TerminalRepo)
from tradecopier.application.domain.entities.rule import (ComplexRule,
                                                          FilterRule,
                                                          TransformRule)
from tradecopier.application.domain.value_objects import (
    TerminalIdLen, TerminalType, type_filter_operation_map,
    type_transform_operation_map)
from tradecopier.restapi.deps import Container
from tradecopier.restapi.dto.objects import (PeerTerminalId, PermittedRules,
                                             RoutePeer, RoutesPresenter,
                                             RuleDTO, Rules)

from .auth import get_current_active_terminal

router = APIRouter()


@router.get("/permitted_rules", response_model=PermittedRules)
def permitted_rules():
    result = PermittedRules(
        transform_operation_map={
            f"{str(k)}:{int(k)}": [str(l) for l in v]
            for k, v in type_transform_operation_map.items()
        },
        filter_operation_map={
            str(k): [f"{str(l)}:{int(l)}" for l in v]
            for k, v in type_filter_operation_map.items()
        },
        fields=Order.get_field_type_mapping(),
        enums=Order.get_enums(),
    )
    return result


@router.get("/rules", response_model=Rules)
@inject
def rules(
    terminal: Terminal = Depends(get_current_active_terminal),
    rule_repo: RuleRepo = Depends(Provide[Container.rule_repo]),
):
    def fill_single_rule(nb, rule):
        nb += 1
        rule_type = "filter" if isinstance(rule, FilterRule) else "transform"
        field = rule.applies_to
        operator = rule.operator
        value = rule.value
        return RuleDTO(
            number=nb, rule_type=rule_type, operator=operator, field=field, value=value
        )

    rules = rule_repo.get(terminal.terminal_id)
    result: Rules = Rules()
    if isinstance(rules, ComplexRule):
        for nb, rule in enumerate(rules.generator()):
            result.rules.append(fill_single_rule(nb, rule))
    elif isinstance(rules, (FilterRule, TransformRule)):
        result.rules.append(fill_single_rule(0, rules))
    return result


@router.get("/peer", response_model=str)
@inject
def peer_terminal(
    terminal_id: PeerTerminalId = Depends(PeerTerminalId),
    terminal: Terminal = Depends(get_current_active_terminal),
    terminal_repo: TerminalRepo = Depends(Provide[Container.terminal_repo]),
):
    if len(terminal_id.identifier) == TerminalIdLen:
        peer_terminal = terminal_repo.get(uuid.UUID(terminal_id.identifier))
    elif len(terminal_id.identifier) == 12:
        peer_terminal = terminal_repo.get_by_tail(terminal_id.identifier)
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="invalid identifier"
        )
    if peer_terminal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no terminal found"
        )
    return peer_terminal.str_id


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
