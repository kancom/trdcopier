from tradecopier.application.domain.value_objects import CustomerType


def test_terminal(terminals):
    terminal = terminals[0]
    terminal.customer_type = CustomerType.SILVER
    assert terminal.is_active
