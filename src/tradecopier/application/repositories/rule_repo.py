import abc

from tradecopier.application.domain.entities.rule import Rule
from tradecopier.application.domain.value_objects import RuleId, TerminalId


class RuleRepo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, rule_id: RuleId) -> Rule:
        pass

    @abc.abstractmethod
    def get_by_terminal_id(self, terminal_id: TerminalId) -> Rule:
        pass

    @abc.abstractmethod
    def save(self, rule: Rule) -> RuleId:
        pass

    # @abc.abstractmethod
    # def mark_changed(self, terminal_id: TerminalId):
    #     pass

    # @abc.abstractmethod
    # def is_changed(self, terminal_id: TerminalId) -> bool:
    #     pass

    # @abc.abstractmethod
    # def mark_change_consumed(self, terminal_id: TerminalId):
    #     pass
