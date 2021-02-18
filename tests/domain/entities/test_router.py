import pydantic
import pytest
from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.value_objects import CustomerType


def test_router(terminal_factory, mocker):
    terminals = terminal_factory.create_batch(4, customer_type=CustomerType.SILVER)
    inactive_t = terminal_factory(enabled=False)
    for idx in range(2):
        Route(source=terminals[idx], destination=terminals[idx + 2])
    with pytest.raises(
        pydantic.error_wrappers.ValidationError, match="destination must be active"
    ):
        Route(source=terminals[0], destination=inactive_t)
