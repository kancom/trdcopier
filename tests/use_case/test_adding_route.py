import uuid
from datetime import datetime

import pytest
from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.value_objects import (CustomerType,
                                                          RouteStatus)
from tradecopier.application.use_case.adding_route import AddingRouteUseCase


@pytest.fixture
def route_repo(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.repositories.route_repo.SqlAlchemyRouteRepo",
        autospec=True,
    )


@pytest.fixture
def term_repo(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.repositories.terminal_repo.SqlAlchemyTerminalRepo",
        autospec=True,
    )


@pytest.fixture
def get_uuid():
    return str(uuid.uuid4())


@pytest.fixture
def get_uuid_tail(get_uuid):
    return get_uuid[-12:]


def test_improper_uuids(
    mocker, get_uuid, get_uuid_tail, term_repo, route_repo, terminal_factory
):
    def save(check):
        def save(route):
            check(route)

        return save

    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        route_repo=route_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    sources = [get_uuid_tail]
    destinations = [get_uuid_tail]
    uc.execute(sources=sources, destinations=destinations)
    ar_bound.present.assert_called_with({"error": "both terminals are passed as tail"})

    sources = [get_uuid[2:]]
    uc.execute(sources=sources, destinations=destinations)
    ar_bound.present.assert_called_with({"error": "incorrectly formed source"})


def test_route_status(
    mocker, get_uuid, get_uuid_tail, term_repo, route_repo, terminal_factory
):
    sources = [get_uuid]
    destinations = [get_uuid_tail]
    route_repo.save.side_effect = lambda x: x.status == RouteStatus.SOURCE
    term_repo.get.side_effect = lambda x: terminal_factory(registered_at=datetime.now())
    term_repo.get_by_tail.side_effect = lambda x: terminal_factory(
        registered_at=datetime.now()
    )
    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        route_repo=route_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    uc.execute(sources=sources, destinations=destinations)


def test_same_uuids(
    mocker, get_uuid, get_uuid_tail, term_repo, route_repo, terminal_factory
):
    sources = [get_uuid]
    destinations = [get_uuid]
    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        route_repo=route_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    uc.execute(sources=sources, destinations=destinations)
    ar_bound.present.assert_called_with(
        {"error": "The same terminal can't be used as both src and dst"}
    )


def test_both_full_uuids(mocker, term_repo, route_repo, terminal_factory):
    def get(terminals):
        def wrapped(term_id):
            return [t for t in terminals if t.terminal_id == term_id][0]

        return wrapped

    terminals = terminal_factory.build_batch(2, customer_type=CustomerType.GOLD)
    term_repo.get.side_effect = get(terminals)
    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        route_repo=route_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    sources = [str(terminals[0].terminal_id)]
    destinations = [str(terminals[1].terminal_id)]
    uc.execute(sources=sources, destinations=destinations)
    assert not ar_bound.present.called


def test_one_full_uuids(mocker, term_repo, route_repo, terminal_factory):
    def get(terminals):
        def wrapped(term_id):
            return [t for t in terminals if str(term_id) in str(t.terminal_id)][0]

        return wrapped

    terminals = terminal_factory.build_batch(2, customer_type=CustomerType.GOLD)
    term_repo.get.side_effect = get(terminals)
    term_repo.get_by_tail.side_effect = get(terminals)
    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        route_repo=route_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    sources = [str(terminals[0].terminal_id)]
    destinations = [str(terminals[1].terminal_id)[-12:]]
    uc.execute(sources=sources, destinations=destinations)
    assert not ar_bound.present.called


def test_more_than_5_routes(mocker, term_repo, route_repo, terminal_factory):
    def get(terminals):
        def wrapped(term_id):
            return [t for t in terminals if t.terminal_id == term_id][0]

        return wrapped

    terminals = terminal_factory.build_batch(
        6, customer_type=CustomerType.BRONZE, registered_at=datetime.utcnow()
    )
    term_repo.get.side_effect = get(terminals)
    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        route_repo=route_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    sources = [str(terminals[0].terminal_id)]
    routes = []
    for dst in terminals[1:]:
        routes.append(
            Route(
                source=terminals[0],
                destination=dst,
                status=RouteStatus.BOTH,
            )
        )
    destinations = [str(terminals[1].terminal_id)]
    route_repo.get_by_terminal_id.return_value = routes
    uc.execute(sources=sources, destinations=destinations)
    ar_bound.present.assert_called_with({"error": "Too many routes"})
