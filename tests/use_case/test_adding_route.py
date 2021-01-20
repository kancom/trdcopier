import uuid
from datetime import datetime

import factories
import pytest
from tradecopier.application.domain.value_objects import RouteStatus
from tradecopier.application.use_case.adding_route import AddingRouteUseCase


@pytest.fixture
def router_repo(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.repositories.router_repo.SqlAlchemyRouterRepo",
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
    mocker, get_uuid, get_uuid_tail, term_repo, router_repo, terminal_factory
):
    def save(check):
        def save(router):
            check(router)

        return save

    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        router_repo=router_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    sources = [get_uuid_tail]
    destinations = [get_uuid_tail]
    with pytest.raises(AssertionError, match="both terminals are passed as tail"):
        uc.execute(sources=sources, destinations=destinations)

    sources = [get_uuid[2:]]
    with pytest.raises(AssertionError, match="incorrectly formed source"):
        uc.execute(sources=sources, destinations=destinations)


def test_route_status(
    mocker, get_uuid, get_uuid_tail, term_repo, router_repo, terminal_factory
):
    sources = [get_uuid]
    destinations = [get_uuid_tail]
    router_repo.save.side_effect = lambda x: x.routes[0].status == RouteStatus.SOURCE
    term_repo.get.side_effect = lambda x: terminal_factory(registered_at=datetime.now())
    term_repo.get_by_tail.side_effect = lambda x: terminal_factory(
        registered_at=datetime.now()
    )
    ar_bound = mocker.MagicMock()
    uc = AddingRouteUseCase(
        router_repo=router_repo, terminal_repo=term_repo, boundary=ar_bound
    )
    uc.execute(sources=sources, destinations=destinations)
