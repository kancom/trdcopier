import datetime

import pytest
from domain.value_objects import CustomerType
from factories import CustomerFactory


def test_customer(terminals):
    expired = [
        CustomerFactory(expire_at=datetime.datetime.now() - datetime.timedelta(days=1)),
        CustomerFactory(active=False),
    ]
    assert all([x.is_active is False for x in expired])
    active = [
        CustomerFactory(
            expire_at=datetime.datetime.now() - datetime.timedelta(days=1),
            customer_type=CustomerType.SILVER,
        ),
        CustomerFactory(customer_type=CustomerType.GOLD),
    ]
    assert all([x.is_active is True for x in active])
    customer = CustomerFactory()
    for t in terminals * 2:
        customer.add_source(t)
    assert len(terminals) == len(customer.sources)
    terminals[0].active = False
    with pytest.raises(AssertionError, match="terminal must be active"):
        customer.add_source(terminals[0])
    with pytest.raises(AssertionError, match="terminal loop schema"):
        customer.add_destination(terminals[-1])
