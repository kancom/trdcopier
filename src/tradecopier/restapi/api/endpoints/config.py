from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response, status
from tradecopier.application import (AddingRouteUseCase, ComplexRule,
                                     Expression, FilterRule, RouteRepo,
                                     RuleRepo, Terminal, TransformRule)
from tradecopier.application.domain.value_objects import (
    EntityNotFoundException, RouteId, RouteStatus, TerminalType)
from tradecopier.application.use_case.adding_route import AddingRouteBoundary
from tradecopier.restapi.deps import Container
from tradecopier.restapi.dto.objects import Rules

from ...dto.objects import RouteEndpoints
from .auth import get_current_active_terminal

router = APIRouter()


@router.post("/rules", status_code=status.HTTP_201_CREATED)
@inject
def set_rules(
    rules_dto: Rules,
    terminal: Terminal = Depends(get_current_active_terminal),
    rule_repo: RuleRepo = Depends(Provide(Container.rule_repo)),
):
    complex_rule = ComplexRule(terminal.terminal_id)
    for rule in rules_dto.rules:
        expr = Expression(field=rule.field, value=rule.value, operator=rule.operator)
        if rule.rule_type == "filter":
            complex_rule.push_rule(FilterRule(terminal.terminal_id, expr))
        elif rule.rule_type == "transform":
            complex_rule.push_rule(TransformRule(terminal.terminal_id, expr))
        else:
            raise ValueError("Unsupported rule type")
    rule_repo.save(complex_rule)


@router.post("/route", status_code=status.HTTP_201_CREATED)
@inject
def add_route(
    route_endpoints: RouteEndpoints,
    terminal: Terminal = Depends(get_current_active_terminal),
    route_repo: RouteRepo = Depends(Provide(Container.route_repo)),
    use_case: AddingRouteUseCase = Depends(Provide(Container.adding_route_uc)),
    uc_presenter: AddingRouteBoundary = Depends(
        Provide(Container.adding_route_presenter)
    ),
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
    elif len(src_routes) > 0:
        term_type = TerminalType.SOURCE

    source = str(route_endpoints.source)
    destination = str(route_endpoints.destination)

    if term_type == TerminalType.UNKNOWN and (
        source is not None and destination is not None
    ):
        use_case.execute(sources=[source], destinations=[destination])
        if len(uc_presenter.result):
            outcome = uc_presenter.result.pop()
            if "error" in outcome:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=outcome["error"],
                )
            return

    if term_type == TerminalType.SOURCE:
        source = str(terminal.terminal_id)
    elif term_type == TerminalType.DESTINATION:
        destination = str(terminal.terminal_id)
    if source is not None and destination is not None:
        use_case.execute(sources=[source], destinations=[destination])
    if len(uc_presenter.result):
        outcome = uc_presenter.result.pop()
        if "error" in outcome:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=outcome["error"],
            )
        return


@router.delete("/route/{route_id}", status_code=status.HTTP_200_OK)
@inject
def delete_route(
    route_id: RouteId,
    terminal: Terminal = Depends(get_current_active_terminal),
    route_repo: RouteRepo = Depends(Provide(Container.route_repo)),
):
    try:
        route = route_repo.get(route_id)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    route_status = route.status
    if route is not None:
        if terminal.terminal_id == route.source.terminal_id:
            if route_status == RouteStatus.SOURCE:
                route_repo.delete(route_id)
            elif route_status == RouteStatus.BOTH:
                route.status = RouteStatus.DESTINATION
                route_repo.save(route)
        elif terminal.terminal_id == route.destination.terminal_id:
            if route_status == RouteStatus.DESTINATION:
                route_repo.delete(route_id)
            elif route_status == RouteStatus.BOTH:
                route.status = RouteStatus.SOURCE
                route_repo.save(route)
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
