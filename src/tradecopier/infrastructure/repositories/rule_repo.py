from typing import Optional

from sqlalchemy.engine import Connection
from tradecopier.application.domain.entities.rule import Rule
from tradecopier.application.domain.value_objects import (
    EntityNotFoundException, RuleId, TerminalId)
from tradecopier.application.repositories.rule_repo import RuleRepo


class SqlAlchemyRuleRepo(RuleRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get(self, rule_id: RuleId) -> Rule:
        db_rule = Rule()
        if not db_rule:
            raise EntityNotFoundException(f"{rule_id} not found")
        return db_rule

    def get_by_terminal_id(self, terminal_id: TerminalId) -> Rule:
        return Rule()

    def save(self, rule: Rule) -> RuleId:
        pass
