import math

import pydantic
import pytest
from pydantic import ValidationError
from tradecopier.application.domain.entities.rule import (ComplexRule,
                                                          Expression,
                                                          FilterRule,
                                                          TransformRule)
from tradecopier.application.domain.value_objects import (FilterOperation,
                                                          OrderType,
                                                          TransformOperation)


def test_expression():
    with pytest.raises(
        ValidationError, match="field and operator can not be None simultaneously"
    ):
        Expression(field=None, value=None, operator=None)
    expr = Expression(field=None, value=None, operator=TransformOperation.REVERSE)
    assert expr.operator == TransformOperation.REVERSE
    assert expr.field == ""


def test_transform_reverse(trade_message_factory, terminal_factory):
    terminal = terminal_factory()
    te = Expression(field="", value="", operator=TransformOperation.REVERSE)
    tr = TransformRule(terminal.terminal_id, te)
    msg = trade_message_factory()
    sl_points = 3
    tp_points = 5
    msg.body.sl_points = sl_points
    msg.body.tp_points = tp_points
    msg.body.sl = msg.body.price - sl_points
    msg.body.tp = msg.body.price + tp_points
    assert msg.body.tp > msg.body.price > msg.body.sl
    transformed_msg = tr.apply(msg)
    assert (
        transformed_msg.body.tp < transformed_msg.body.price < transformed_msg.body.sl
    )
    assert transformed_msg.body.order_type == OrderType.ORDER_TYPE_SELL
    assert tr.applies_to == "not yet initialized"
    assert tr.operator is TransformOperation.REVERSE
    assert tr.value is None
    assert math.isclose(transformed_msg.body.sl - transformed_msg.body.price, sl_points)

    price = msg.body.price
    msg.body.price = 0
    transformed_msg = tr.apply(msg)
    assert math.isclose(price - transformed_msg.body.sl, sl_points)


def test_transform_append(trade_message_factory, terminal_factory):
    terminal = terminal_factory()
    add_text = "-test"
    te = Expression(field="comment", value=add_text, operator=TransformOperation.APPEND)
    tr = TransformRule(terminal.terminal_id, te)
    msg = trade_message_factory()
    transformed_msg = tr.apply(msg)
    assert add_text in transformed_msg.body.comment
    assert tr.applies_to == "comment"
    assert tr.operator == TransformOperation.APPEND
    assert tr.value == add_text


def test_filter_lt(trade_message_factory, terminal_factory):
    terminal = terminal_factory()
    f_value = 10
    fe = Expression(field="magic", value=f_value, operator=FilterOperation.LT)
    fr = FilterRule(terminal.terminal_id, fe)
    msgs = trade_message_factory.build_batch(5)
    for msg in msgs:
        if msg.body.magic < f_value:
            assert fr.apply(msg) is not None
        else:
            assert fr.apply(msg) is None
    assert fr.applies_to == "magic"
    assert fr.operator == FilterOperation.LT
    assert fr.value == f_value


def test_filter_eq(trade_message_factory, terminal_factory):
    terminal = terminal_factory()
    f_value = "EURUSD"
    fe = Expression(field="symbol", value=f_value, operator=FilterOperation.EQ)
    fr = FilterRule(terminal.terminal_id, fe)
    msg = trade_message_factory()
    assert fr.apply(msg) is not None
    fe = Expression(field="symbol", value=f_value, operator=FilterOperation.IN)
    fr = FilterRule(terminal.terminal_id, fe)
    assert fr.apply(msg) is not None
    fe = Expression(field="order_type", value=0, operator=FilterOperation.EQ)
    fr = FilterRule(terminal.terminal_id, fe)
    assert fr.apply(msg) is not None
    fe = Expression(field="order_type", value=1, operator=FilterOperation.EQ)
    fr = FilterRule(terminal.terminal_id, fe)
    assert fr.apply(msg) is None


def test_complex_rule(trade_message_factory, terminal_factory):
    terminal = terminal_factory()
    msg = trade_message_factory()
    cr = ComplexRule(terminal.terminal_id)
    add_text = "-test"
    te = Expression(field="comment", value=add_text, operator=TransformOperation.APPEND)
    tr = TransformRule(terminal.terminal_id, te)
    cr.push_rule(tr)
    fe = Expression(field="comment", value=add_text, operator=FilterOperation.IN)
    fr = FilterRule(terminal.terminal_id, fe)
    cr.push_rule(fr)
    assert cr.apply(msg) is not None
