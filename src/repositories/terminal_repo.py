import abc
from typing import Optional

from domain.entities.terminal import Terminal
from domain.value_objects import TerminalId


class TerminalRepo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, terminal_id: TerminalId) -> Optional[Terminal]:
        pass

    @abc.abstractmethod
    def save(self, terminal: Terminal) -> TerminalId:
        pass