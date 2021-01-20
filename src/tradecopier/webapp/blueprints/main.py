import flask_injector
import injector
from flask import Blueprint, Response, abort, jsonify, make_response, request
from tradecopier.application.use_case.adding_route import AddingRouteBoundary
from tradecopier.infrastructure.repositories.router_repo import Router

main_blueprint = Blueprint("main_blueprint", __name__)


class AddingRoutePresenter(AddingRouteBoundary):
    def present(router: Router):
        pass


class RouterBoundaryWeb(injector.Module):
    @injector.provider
    @flask_injector.request
    def adding_route_boundary() -> AddingRouteBoundary:
        return AddingRoutePresenter()


@main_blueprint.route("/<str:terminal_id>", methods=["GET"])
def routes(terminal_id: str):
    pass
