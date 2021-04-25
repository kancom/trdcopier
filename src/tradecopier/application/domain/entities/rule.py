import json
import operator
from decimal import Decimal
from typing import Generator, List, Optional, Union

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
        if values["field"] == "reverse":
            values["field"] = ""
            values["value"] = ""
            return TransformOperation.REVERSE
        return v


class Rule:
    terminal_id: TerminalId

    def __init__(self, terminal_id: TerminalId, expr: Expression):
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
    def applies_to(self) -> str:
        if self._expr.operator == TransformOperation.REVERSE:
            return "reverse"
        return super().applies_to

    @property
    def value(self):
        if self._expr.operator == TransformOperation.REVERSE:
            return None
        return self._expr.value

    @property
    def operator(self):
        if self._expr.operator == TransformOperation.REVERSE:
            return None
        return self._expr.operator

    def apply(self, message: InTradeMessage) -> Optional[InTradeMessage]:
        if (
            self._expr.operator == TransformOperation.APPEND
            and self._expr.field is not None
        ):
            field_value = getattr(message.body, self._expr.field)
            field_value = (
                field_value + self._expr.value
                if field_value is not None
                else self._expr.value
            )
            setattr(message.body, self._expr.field, field_value)
            return message

        if self._expr.operator == TransformOperation.REVERSE:
            order_type = message.body.order_type
            if order_type in (
                OrderType.ORDER_TYPE_CLOSE_BY,
                OrderType.ORDER_TYPE_BUY_STOP_LIMIT,
                OrderType.ORDER_TYPE_SELL_STOP_LIMIT,
            ):
                raise NotImplementedError(f"Order type {order_type} is not supported")
            sl = message.body.sl
            tp = message.body.tp
            price = message.body.price
            if order_type in (
                OrderType.ORDER_TYPE_BUY,
                OrderType.ORDER_TYPE_BUY_LIMIT,
                OrderType.ORDER_TYPE_BUY_STOP,
            ):
                order_type = OrderType(int(order_type) + 1)  # buy -> sell
                if sl is not None and sl > 0:
                    sl = price + (price - sl)
                if tp is not None and tp > 0:
                    tp = price - (tp - price)
            else:  # sell -> buy
                order_type = OrderType(int(order_type) - 1)
                if sl is not None and sl > 0:
                    sl = price - (sl - price)
                if tp is not None and tp > 0:
                    tp = price + (price - tp)
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
    def is_valid(self):
        return FilterRule.examine(self._expr)


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
