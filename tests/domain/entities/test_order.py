from tradecopier.application import Order


def test_fields_mapping():
    mappings = Order.get_field_type_mapping()
    assert type(mappings) == dict
    assert "TradeAction" in mappings["action"]
    assert mappings["symbol"] == "string"


def test_enuma():
    enums = Order.get_enums()
    assert type(enums) == dict
    assert len(enums["TradeAction"]) == 6
