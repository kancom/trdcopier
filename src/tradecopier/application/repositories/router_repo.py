import abc
from typing import List

from tradecopier.application.domain.entities.router import Router
from tradecopier.application.domain.value_objects import RouterId, TerminalId


class RouterRepo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, router_id: RouterId) -> Router:
        pass

    @abc.abstractmethod
    def save(self, router: Router) -> RouterId:
        pass

    @abc.abstractmethod
    def get_by_src_terminal(self, terminal_id: TerminalId) -> List[Router]:
        pass
