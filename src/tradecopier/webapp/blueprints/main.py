from functools import wraps
from typing import List

import injector
from flask import (Blueprint, flash, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
from flask_babel import _
from flask_pydantic_spec import Response
from tradecopier.application import AddingRouteUseCase
from tradecopier.application.domain.entities.rule import (ComplexRule,
                                                          FilterRule,
                                                          TransformRule)
from tradecopier.application.domain.value_objects import (RouteStatus,
                                                          TerminalId,
                                                          TerminalType)
from tradecopier.application.repositories.route_repo import RouteRepo
from tradecopier.application.repositories.rule_repo import RuleRepo
from tradecopier.application.repositories.terminal_repo import TerminalRepo
from tradecopier.application.use_case.adding_route import AddingRouteBoundary
from tradecopier.webapp.forms.config import AddRouteForm, AddTerminalForm
from tradecopier.webapp.forms.login import LoginForm

from ..dto import config as cfgdto
from ..extensions import specs

main_blueprint = Blueprint("main_blueprint", __name__)

sess_user_key = "terminal_id"
sess_user_status = "customer_type"
sess_user_exp = "customer_exp"


def svg_generator(
    *,
    width: int,
    height: int,
    statuses: List[RouteStatus],
    term_type: TerminalType,
) -> str:
    def single_arr(src: bool):
        x_offset = 0 if src else width - third_x
        src_arrows = '<polyline points="{},{} {},{} {},{} {},{} {},{} {},{} " style="fill:lime;stroke:purple;stroke-width:5;" />'.format(
            x_offset + 0,
            center_y,  #
            x_offset + third_x - tick_sz,
            center_y,  #
            x_offset + third_x - tick_sz,
            center_y - tick_sz,  #
            x_offset + third_x,
            center_y,  #
            x_offset + third_x - tick_sz,
            center_y + tick_sz,  #
            x_offset + third_x - tick_sz,
            center_y,  #
        )
        return src_arrows

    svg = """<svg width="{}" height="{}">{{}}{{}}{{}}</svg>""".format(width, height)
    center_x = int(width / 2)
    center_y = int(height / 2)
    third_x = int(width / 3)
    third_y = int(height / 3)
    tick_sz = int(width / 25)
    peers_nb = len(statuses)
    vert_step = int(height / (peers_nb + 1))
    rect = """<rect x="{}" y="{}" rx="20" ry="20" width="{}" height="{}" style="fill:red; stroke:black; stroke-width:5; opacity:0.5" />""".format(
        center_x - third_x / 2, center_y - third_y / 2, third_x, third_y
    )
    src_arrows = ""
    dst_arrows = ""
    if term_type == TerminalType.SOURCE:
        src_arrows = single_arr(True)
        for idx in range(1, peers_nb + 1):
            x_offset = width - third_x
            dst_arrows += '<polyline points="{},{} {},{} {},{} {},{} {},{} {},{} " style="fill:lime;stroke:purple;stroke-width:5;{}" />'.format(
                x_offset + 0,
                center_y,  #
                x_offset + third_x - tick_sz,
                idx * vert_step,  #
                x_offset + third_x - tick_sz,
                idx * vert_step - tick_sz,  #
                x_offset + third_x,
                idx * vert_step,  #
                x_offset + third_x - tick_sz,
                idx * vert_step + tick_sz,  #
                x_offset + third_x - tick_sz,
                idx * vert_step,  #
                ""
                if statuses[idx - 1] == RouteStatus.BOTH
                else "stroke-linecap:round;stroke-dasharray:1,10",
            )
    else:
        dst_arrows = single_arr(False)
        for idx in range(1, peers_nb + 1):
            x_offset = 0
            src_arrows += '<polyline points="{},{} {},{} {},{} {},{} {},{} {},{} " style="fill:lime;stroke:purple;stroke-width:5;{}" />'.format(
                x_offset + 0,
                idx * vert_step,  #
                x_offset + third_x - tick_sz,
                center_y,  #
                x_offset + third_x - tick_sz,
                center_y - tick_sz,  #
                x_offset + third_x,
                center_y,  #
                x_offset + third_x - tick_sz,
                center_y + tick_sz,  #
                x_offset + third_x - tick_sz,
                center_y,  #
                ""
                if statuses[idx - 1] == RouteStatus.BOTH
                else "stroke-linecap:round;stroke-dasharray:1,10",
            )

    return svg.format(rect, src_arrows, dst_arrows)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if sess_user_key not in session or session[sess_user_key] is None:
            return redirect(url_for("main_blueprint.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@main_blueprint.route(
    "/delete",
    methods=["POST"],
)
@injector.inject
@specs.validate(body=cfgdto.DeleteRouteDTO, resp=Response("HTTP_404"))
@login_required
def delete(route_repo: RouteRepo):
    route_id = request.form["route_id"]
    route = route_repo.get(route_id)
    terminal_id = session[sess_user_key]
    route_status = route.status
    if route is not None:
        if terminal_id == str(route.source.terminal_id):
            if route_status == RouteStatus.SOURCE:
                route_repo.delete(route_id)
            elif route_status == RouteStatus.BOTH:
                route.status = RouteStatus.DESTINATION
                route_repo.save(route)
        elif terminal_id == str(route.destination.terminal_id):
            if route_status == RouteStatus.DESTINATION:
                route_repo.delete(route_id)
            elif route_status == RouteStatus.BOTH:
                route.status = RouteStatus.SOURCE
                route_repo.save(route)
    return redirect(url_for("main_blueprint.config"))


# @main_blueprint.route("/", methods=["GET", "POST"])
# @injector.inject
# def login(term_repo: TerminalRepo):
#     form = LoginForm()
#     if form.validate_on_submit():
#         terminal_id = form.terminal_id.data
#         terminal = term_repo.get(terminal_id)
#         if terminal is not None and terminal.is_active:
#             session[sess_user_key] = str(terminal_id)
#             session[sess_user_status] = str(terminal.customer_type)
#             session[sess_user_exp] = terminal.expire_at
#             return redirect(url_for("main_blueprint.config"))
#         if terminal is None:
#             flash(_("Terminal wasn't found. Check your terminal id"))
#         elif not terminal.is_active:
#             flash(_("Your Terminal is no longer active"))
#     return render_template("login.html", form=form)


@main_blueprint.route("/logout", methods=("GET",))
@login_required
def logout():
    del session[sess_user_key]
    return redirect(url_for("main_blueprint.login"))


@main_blueprint.route("/editexpr", methods=["GET", "POST"])
@injector.inject
@login_required
def edit_expr(rule_repo: RuleRepo):
    expressions: List[dict] = []
    terminal_id = session[sess_user_key]
    rules = rule_repo.get(terminal_id)
    if isinstance(rules, ComplexRule):
        for rule in rules.generator():
            rule_expr = rule.dict()
            expressions.append(
                {
                    "nb": len(expressions) + 1,
                    "type": "filter" if isinstance(rule, FilterRule) else "transform",
                    "field": rule_expr["field"],
                    "operator": rule_expr["operator"],
                    "value": rule_expr["value"],
                }
            )
    elif isinstance(rules, (FilterRule, TransformRule)):
        rule_expr = rules.dict()
        expressions.append(
            {
                "nb": len(expressions) + 1,
                "type": "filter" if isinstance(rule, FilterRule) else "transform",
                "field": rule_expr["field"],
                "operator": rule_expr["operator"],
                "value": rule_expr["value"],
            }
        )
    return render_template("editexpr.html", expressions=expressions)


@main_blueprint.route("/config", methods=["GET", "POST"])
@injector.inject
@login_required
def config(
    route_repo: RouteRepo,
    use_case: AddingRouteUseCase,
    uc_presenter: AddingRouteBoundary,
):
    add_term_form = AddTerminalForm()
    add_route_form = AddRouteForm()
    terminal_id = session[sess_user_key]
    term_type = TerminalType.UNKNOWN

    src_routes = route_repo.get_by_terminal_id(
        terminal_id, term_type=TerminalType.SOURCE
    )
    dst_routes = route_repo.get_by_terminal_id(
        terminal_id, term_type=TerminalType.DESTINATION
    )
    if len(dst_routes) > 0:
        term_type = TerminalType.DESTINATION
    elif len(src_routes) > 0:
        term_type = TerminalType.SOURCE

    if term_type == TerminalType.UNKNOWN:
        if add_route_form.validate_on_submit():
            source = add_route_form.src_terminal_id.data
            destination = add_route_form.dst_terminal_id.data
            use_case.execute(sources=[source], destinations=[destination])
            if len(uc_presenter.result):
                outcome = uc_presenter.result.pop()
                if "error" not in outcome:
                    return redirect(url_for("main_blueprint.config"))
                flash(outcome["error"], "error")
        return render_template("add_route.html", add_route_form=add_route_form)
    if add_term_form.validate_on_submit():
        if term_type == TerminalType.SOURCE:
            source = terminal_id
            destination = add_term_form.terminal_id.data
        elif term_type == TerminalType.DESTINATION:
            source = add_term_form.terminal_id.data
            destination = terminal_id
        use_case.execute(sources=[source], destinations=[destination])
        if len(uc_presenter.result):
            outcome = uc_presenter.result.pop()
            if "error" in outcome:
                flash(outcome["error"], "error")
        return redirect(url_for("main_blueprint.config"))

    if term_type == TerminalType.SOURCE:
        own_terminal = [src_routes[0].source]
        peers = [
            (
                {
                    "terminal_brand": route.destination.terminal_brand,
                    "terminal_id": route.destination.terminal_id
                    if route.status == RouteStatus.BOTH
                    else str(route.destination.terminal_id)[-12:],
                    "str_id": route.destination.str_id
                    if route.status == RouteStatus.BOTH
                    else "n/a",
                },
                {"status": route.status, "route_id": route.route_id},
            )
            for route in src_routes
        ]
    else:
        own_terminal = [dst_routes[0].destination]
        peers = [
            (
                {
                    "terminal_brand": route.destination.terminal_brand,
                    "terminal_id": route.destination.terminal_id
                    if route.status == RouteStatus.BOTH
                    else str(route.destination.terminal_id)[-12:],
                    "str_id": route.destination.str_id
                    if route.status == RouteStatus.BOTH
                    else "n/a",
                },
                {"status": route.status, "route_id": route.route_id},
            )
            for route in dst_routes
        ]
    svg = svg_generator(
        width=400,
        height=400,
        term_type=term_type,
        statuses=[peer[1]["status"] for peer in peers],
    )

    return render_template(
        "config.html",
        own_terminal=own_terminal,
        peers=peers,
        form=add_term_form,
        term_type=term_type,
        svg=svg,
    )


# @main_blueprint.route("/<terminal_id>", methods=["GET"])
# @injector.inject
# @login_required
# def get_terminal(terminal_id: TerminalId, term_repo: TerminalRepo):
#     terminal = term_repo.get(terminal_id)
#     if terminal is not None:
#         return make_response(jsonify(terminal.dict()))
#     return make_response(jsonify("not found"), 404)
