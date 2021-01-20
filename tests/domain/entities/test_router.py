import pytest
from tradecopier.application.domain.value_objects import CustomerType


def test_router(terminal_factory, router_factory, mocker):
    router = router_factory()
    terminals = terminal_factory.create_batch(4, customer_type=CustomerType.SILVER)
    inactive_t = terminal_factory(enabled=False)
    for idx in range(2):
        router.add_route(source=terminals[idx], destination=terminals[idx + 2])
    assert len(router.routes) == 2
    with pytest.raises(AssertionError, match="destination must be active"):
        router.add_route(source=terminals[0], destination=inactive_t)
    with pytest.raises(AssertionError, match="terminal loop schema"):
        router.add_route(source=terminals[2], destination=terminals[0])
