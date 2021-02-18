from typing import Callable, Generator, Iterable, Type, Union

from sqlalchemy.engine import Connection
from tradecopier.application.domain.entities.rule import (ComplexRule,
                                                          Expression,
                                                          FilterRule, Rule,
                                                          TransformRule)
from tradecopier.application.domain.value_objects import (
    EntityNotFoundException, FilterOperation, TerminalId, TransformOperation)
from tradecopier.application.repositories.rule_repo import RuleRepo
from tradecopier.infrastructure.repositories.sql_model import RuleModel


class SqlAlchemyRuleRepo(RuleRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get(self, terminal_id: TerminalId) -> Rule:
        def decode_type(val: str):
            if val is None:
                return None
            if val.startswith("str:"):
                return val[4:]
            elif val.startswith("float:"):
                return float(val[6:])
            elif val.startswith("int:"):
                return int(val[4:])

        rules_db = self._conn.execute(
            RuleModel.select().where(RuleModel.c.terminal_id == terminal_id)
        ).all()
        rules = []
        result: Union[ComplexRule, FilterRule, TransformRule, Rule]
        operator: Union[TransformOperation, FilterOperation]
        rule_class: Union[Type[FilterRule], Type[TransformRule]]
        for rule_db in rules_db:
            if rule_db["is_transform"]:
                operator = TransformOperation(rule_db["operator"])
                rule_class = TransformRule
            else:
                operator = FilterOperation(rule_db["operator"])
                rule_class = FilterRule
            expr = Expression(
                field=rule_db["field"],
                value=decode_type(rule_db["value"]),
                operator=operator,
            )
            rule = rule_class(terminal_id, expr)
            rule.terminal_id = terminal_id
            rules.append(rule)
        if len(rules) > 1:
            result = ComplexRule(terminal_id, rules)
        elif len(rules) == 1:
            result = rules[0]
        else:
            result = Rule()
        result.terminal_id = terminal_id
        return result

    def save(self, rule: Rule):
        def enrigh_type(val):
            if isinstance(val, str):
                return f"str:{val}"
            elif isinstance(val, float):
                return f"float:{val}"
            elif isinstance(val, int):
                return f"int:{val}"

        getter: Generator[Rule, None, None]
        if isinstance(rule, ComplexRule):
            getter = rule.generator()
        else:
            getter = [rule]
        self._conn.execute(
            RuleModel.delete(whereclause=RuleModel.c.terminal_id == rule.terminal_id)
        )
        for next_rule in getter:
            is_transform = isinstance(next_rule, TransformRule)
            rule_expr = next_rule.dict()
            self._conn.execute(
                RuleModel.insert(
                    values={
                        "terminal_id": next_rule.terminal_id,
                        "is_transform": is_transform,
                        "field": rule_expr["field"],
                        "value": enrigh_type(rule_expr["value"]),
                        "operator": rule_expr["operator"],
                    }
                )
            )
