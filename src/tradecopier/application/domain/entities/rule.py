import json
import operator
from decimal import Decimal
from typing import Generator, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, validator
from tradecopier.application.domain.entities.message import InTradeMessage
from tradecopier.application.domain.entities.order import Order
from tradecopier.application.domain.value_objects import (FilterOperation,
                                                          OrderType,
                                                          TerminalId,
                                                          TransformOperation)


class Expression(BaseModel):
    field: Union[str, None]
    value: Union[float, int, str, None]
    operator: Union[FilterOperation, TransformOperation, None]

    @validator("operator")
    def validate_operator(cls, v, values):
        if v is None and values["field"] is None:
            raise ValueError("field and operator can not be None simultaneously")
        if v == TransformOperation.REVERSE:
            values["field"] = ""
            values["value"] = ""
        return v


class Rule:
    terminal_id: TerminalId

    def __init__(self, terminal_id: TerminalId, expr: Optional[Expression]):
        self.terminal_id = terminal_id
        self._expr = expr

    def apply(self, message: InTradeMessage) -> Optional[InTradeMessage]:
        return message

    def dict(self):
        return self._expr.dict()

    @property
    def applies_to(self) -> str:
        return self._expr.field or "not yet initialized"

    @property
    def value(self):
        return self._expr.value

    @property
    def operator(self):
        return self._expr.operator


class TransformRule(Rule):
    def __eq__(self, other):
        if not isinstance(other, TransformRule):
            return False
        return (self.terminal_id == other.terminal_id) and (self._expr == other._expr)

    @property
    def value(self):
        if self._expr.operator == TransformOperation.REVERSE:
            return None
        return self._expr.value

    def apply(self, message: InTradeMessage) -> Optional[InTradeMessage]:
        if self._expr.field is not None:
            if self._expr.operator in (
                TransformOperation.ADD,
                TransformOperation.APPEND,
            ):
                field_value = getattr(message.body, self._expr.field)
                field_value = (
                    field_value + self._expr.value
                    if field_value is not None
                    else self._expr.value
                )
                setattr(message.body, self._expr.field, field_value)
                return message
            elif self._expr.operator == TransformOperation.MULTIPLY:
                field_value = getattr(message.body, self._expr.field)
                field_value = (
                    field_value * self._expr.value
                    if field_value is not None
                    else self._expr.value
                )
                setattr(message.body, self._expr.field, field_value)
                return message
            elif self._expr.operator == TransformOperation.SET:
                field_value = getattr(message.body, self._expr.field)
                field_value = self._expr.value
                setattr(message.body, self._expr.field, field_value)
                return message

        if self._expr.operator == TransformOperation.REVERSE:
            order_type = message.body.order_type
            if order_type in (
                OrderType.ORDER_TYPE_CLOSE_BY,
                OrderType.ORDER_TYPE_BUY_STOP_LIMIT,
                OrderType.ORDER_TYPE_SELL_STOP_LIMIT,
            ):
                logger.debug(f"Order type {order_type} is not supported")
            sl = message.body.sl
            tp = message.body.tp
            sl_points = message.body.sl_points
            tp_points = message.body.tp_points
            price = message.body.price
            if sl is not None and sl_points is None:
                raise ValueError(f"slL{sl}, but sl_points is None")
            if tp is not None and tp_points is None:
                raise ValueError(f"tp {tp}, but tp_points is None")
            if order_type in (
                OrderType.ORDER_TYPE_BUY,
                OrderType.ORDER_TYPE_BUY_LIMIT,
                OrderType.ORDER_TYPE_BUY_STOP,
            ):
                order_type = OrderType(int(order_type) + 1)  # buy -> sell
                if sl != 0 and sl_points is not None:
                    price = price if price != 0 else sl + sl_points
                    sl = price + sl_points
                if tp != 0 and tp_points is not None:
                    price = price if price != 0 else tp - tp_points
                    tp = price - tp_points
            else:  # sell -> buy
                order_type = OrderType(int(order_type) - 1)
                if sl != 0 and sl_points is not None:
                    price = price if price != 0 else sl - sl_points
                    sl = price - sl_points
                if tp != 0 and tp_points is not None:
                    price = price if price != 0 else tp + tp_points
                    tp = price + tp_points
            message.body.sl = sl
            message.body.tp = tp
            message.body.order_type = order_type
            return message
        return None


class FilterRule(Rule):
    op_map = {
        FilterOperation.LT: operator.lt,
        FilterOperation.LE: operator.le,
        FilterOperation.EQ: operator.eq,
        FilterOperation.GE: operator.ge,
        FilterOperation.GT: operator.gt,
        FilterOperation.NE: operator.ne,
    }

    @classmethod
    def examine(cls, expr: Expression) -> bool:
        schema = json.loads(Order.schema_json())
        properties = schema["properties"]
        definitions = schema.get("definitions")
        is_enum = False
        if expr.value in properties:
            descr = properties[expr.value]
            if "$ref" in descr:
                enum_class = descr["$ref"].split("/")[-1]
                descr = definitions[enum_class]
                is_enum = True
            field_type = descr["type"]
            if field_type == "string":
                return expr.operator in (
                    FilterOperation.EQ,
                    FilterOperation.NE,
                    FilterOperation.IN,
                )
            elif field_type == "number":
                return (
                    isinstance(expr.value, (float, Decimal))
                    and expr.operator != FilterOperation.IN
                )
            elif field_type == "integer":
                if not is_enum:
                    return (
                        isinstance(expr.value, int)
                        and expr.operator != FilterOperation.IN
                    )
                else:
                    return (
                        isinstance(expr.value, int)
                        and expr.value in descr["enum"]
                        and expr.operator != FilterOperation.IN
                    )
        return False

    def __eq__(self, other):
        if not isinstance(other, FilterRule):
            return False
        return (self.terminal_id == other.terminal_id) and (self._expr == other._expr)

    def apply(self, message: InTradeMessage) -> Optional[InTradeMessage]:
        if (
            self._expr.field is None
            or self._expr.operator is None
            or not isinstance(self._expr.operator, FilterOperation)
        ):
            return None
        field_value = getattr(message.body, self._expr.field)
        filter_result = True
        if self._expr.operator == FilterOperation.IN:
            filter_result = self._expr.value in field_value
        else:
            filter_result = FilterRule.op_map[self._expr.operator](
                field_value, self._expr.value
            )
        return message if filter_result else None

    @property
    def is_valid(self) -> bool:
        return FilterRule.examine(self._expr) if self._expr is not None else True


FinalRule = Union[FilterRule, TransformRule]


class ComplexRule(Rule):
    def __init__(self, terminal_id: TerminalId, rules: Union[list, None] = None):
        self.terminal_id = terminal_id
        if rules is None:
            self._rules: List[FinalRule] = []
        else:
            self._rules = rules

    def push_rule(self, rule: FinalRule) -> None:
        assert hasattr(rule, "apply")
        self._rules.append(rule)

    def pop_rule(self):
        if len(self._rules) > 0:
            self._rules.pop()

    def generator(self) -> Generator[Rule, None, None]:
        for rule in self._rules:
            yield rule

    def apply(self, message: InTradeMessage) -> Optional[InTradeMessage]:
        processing_message: Optional[InTradeMessage] = message
        for rule in self._rules:
            if processing_message:
                processing_message = rule.apply(processing_message)
        return processing_message

    def __eq__(self, other):
        if not isinstance(other, ComplexRule):
            return False
        result = self.terminal_id == other.terminal_id
        result = (
            result
            and len(self._rules) == len(other._rules)
            and all(s == o for s, o in zip(self._rules, other._rules))
        )
        return result
