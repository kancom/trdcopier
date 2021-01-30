from functools import wraps

import flask_injector
import injector
from flask import (Blueprint, flash, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
from flask_babel import _
from tradecopier.application import AddingRouteUseCase
from tradecopier.application.domain.value_objects import TerminalId
from tradecopier.application.repositories.router_repo import RouterRepo
from tradecopier.application.use_case.adding_route import AddingRouteBoundary
from tradecopier.infrastructure.repositories.router_repo import Router
from tradecopier.infrastructure.repositories.terminal_repo import TerminalRepo
from tradecopier.webapp.forms.config import AddTerminalForm
from tradecopier.webapp.forms.login import LoginForm

main_blueprint = Blueprint("main_blueprint", __name__)

sess_user_key = "terminal_id"
sess_user_status = "customer_type"
sess_user_exp = "customer_exp"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if sess_user_key not in session or session[sess_user_key] is None:
            return redirect(url_for("main_blueprint.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


class AddingRoutePresenter(AddingRouteBoundary):
    def present(self, router: Router):
        pass


class RouterBoundaryWeb(injector.Module):
    @injector.provider
    @flask_injector.request
    def adding_route_boundary(self) -> AddingRouteBoundary:
        return AddingRoutePresenter()


@main_blueprint.route("/", methods=["GET", "POST"])
@injector.inject
def login(term_repo: TerminalRepo):
    form = LoginForm()
    if form.validate_on_submit():
        terminal_id = form.terminal_id.data
        terminal = term_repo.get(terminal_id)
        if terminal is not None and terminal.is_active:
            session[sess_user_key] = str(terminal_id)
            session[sess_user_status] = str(terminal.customer_type)
            session[sess_user_exp] = terminal.expire_at
            return redirect(url_for("main_blueprint.config"))
        if terminal is None:
            flash(_("Terminal wasn't found. Check your terminal id"))
        elif not terminal.is_active:
            flash(_("Your Terminal is no longer active"))
    return render_template("login.html", form=form)


@main_blueprint.route("/logout", methods=("GET",))
@login_required
def logout():
    del session[sess_user_key]
    return redirect(url_for("main_blueprint.login"))


@main_blueprint.route("/config", methods=["GET", "POST"])
@injector.inject
# @login_required
def config(router_repo: RouterRepo, use_case: AddingRouteUseCase):
    add_src_term_form = AddTerminalForm()
    add_dst_term_form = AddTerminalForm()
    src_terminal_id = session[sess_user_key]

    if add_dst_term_form.validate_on_submit():
        dst_terminal_id = add_dst_term_form.terminal_id.data
        use_case.execute(sources=[src_terminal_id], destinations=[dst_terminal_id])

    routers = router_repo.get_by_src_terminal(src_terminal_id)
    if len(routers) > 1:
        raise NotImplementedError("only one route per source supported now")
    if routers:
        router = routers[0]
        sources = []
        destinations = []
        for route in router.routes:
            source = {
                "terminal_id": route.source.terminal_id,
                "id": route.source.str_id,
                "brand": route.source.terminal_brand,
            }
            if source not in sources:
                sources.append(source)
            destination = {
                "terminal_id": route.destination.terminal_id,
                "id": route.destination.str_id,
                "brand": route.destination.terminal_brand,
            }
            if destination not in destinations:
                destinations.append(destination)
        return render_template(
            "config.html",
            sources=sources,
            destinations=destinations,
            nodes_nb=len(sources) + len(destinations),
            add_src_term_form=add_src_term_form,
            add_dst_term_form=add_dst_term_form,
        )
    return render_template(
        "config.html",
        add_src_term_form=add_src_term_form,
        add_dst_term_form=add_dst_term_form,
    )


@main_blueprint.route("/<terminal_id>", methods=["GET"])
@injector.inject
@login_required
def get_terminal(terminal_id: TerminalId, term_repo: TerminalRepo):
    terminal = term_repo.get(terminal_id)
    if terminal is not None:
        return make_response(jsonify(terminal.dict()))
    return make_response(jsonify("not found"), 404)
