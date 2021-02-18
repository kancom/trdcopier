from uuid import uuid4

import factory
import factory.fuzzy
from tradecopier.application.domain import value_objects as vo
from tradecopier.application.domain.entities import message as msg
from tradecopier.application.domain.entities.order import Order
from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.entities.rule import Expression, Rule
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (CustomerType,
                                                          FilterOperation)


def new_uuid():
    return factory.Sequence(lambda x: "d327d84f-3f11-11eb-b357-d4258bbc%04d" % x)


def new_uuid_tail():
    return factory.Sequence(lambda x: "d4258bbc%04d" % x)


class RuleFactory(factory.Factory):
    class Meta:
        model = Rule


class TerminalFactory(factory.Factory):
    name = factory.Faker("name")
    broker = factory.Faker("name")
    terminal_id = new_uuid()
    registered_at = factory.Faker("date_time_between", start_date="-2y")

    class Meta:
        model = Terminal


class RouteFactory(factory.Factory):
    route_id = factory.fuzzy.FuzzyInteger(1, 100)
    source = factory.SubFactory(TerminalFactory, customer_type=CustomerType.SILVER)
    destination = factory.SubFactory(TerminalFactory, customer_type=CustomerType.SILVER)

    class Meta:
        model = Route


class RegisterMessageFactory(factory.Factory):
    terminal_id = new_uuid()
    name = factory.Faker("name")
    broker = factory.Faker("name")

    class Meta:
        model = msg.RegisterMessage


class OrderFactory(factory.Factory):
    action = vo.TradeAction.DEAL
    symbol = "EURUSD"
    magic = factory.fuzzy.FuzzyInteger(1, 100)
    order_ticket = factory.fuzzy.FuzzyInteger(1, 100)
    volume = factory.fuzzy.FuzzyFloat(10)
    price = factory.fuzzy.FuzzyFloat(10, 50)
    order_type = vo.OrderType.ORDER_TYPE_BUY
    order_type_filling = vo.OrderTypeFilling.ORDER_FILLING_FOK
    type_time = vo.TypeTime.ORDER_TIME_DAY
    comment = factory.Faker("name")

    class Meta:
        model = Order


class TradeMessageFactory(factory.Factory):
    terminal_id = new_uuid()
    body = factory.SubFactory(OrderFactory)
    account_id = factory.fuzzy.FuzzyInteger(1, 100)

    class Meta:
        model = msg.InTradeMessage


class RegIncomingMessageFactory(factory.Factory):
    message = factory.SubFactory(RegisterMessageFactory)

    class Meta:
        model = msg.IncomingMessage


class OrdIncomingMessageFactory(factory.Factory):
    message = factory.SubFactory(TradeMessageFactory)

    class Meta:
        model = msg.IncomingMessage


class RuleExpressionFactory(factory.Factory):
    field = factory.fuzzy.FuzzyChoice(("price", "sl", "tp"))
    value = factory.fuzzy.FuzzyFloat(1, 100)
    operator = factory.fuzzy.FuzzyChoice([o for o in FilterOperation])

    class Meta:
        model = Expression
