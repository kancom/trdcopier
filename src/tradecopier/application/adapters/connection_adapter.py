import abc

from tradecopier.application.domain.entities.message import OutgoingMessage
from tradecopier.application.domain.value_objects import TerminalId


class ConnectionHandlerAdapter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def disconnect(self, terminal_id: TerminalId):
        pass

    @abc.abstractmethod
    def is_connected(self, terminal_id: TerminalId) -> bool:
        pass

    @abc.abstractmethod
    def send_message(self, terminal_id: TerminalId, message: OutgoingMessage):
        pass
