import abc

from domain.entities.message import OutgoingMessage
from domain.value_objects import TerminalId


class ConnectionHandlerAdapter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def disconnect(self, terminal_id: TerminalId):
        pass

    @abc.abstractmethod
    def is_new_connection(self, terminal_id: TerminalId) -> bool:
        pass

    @abc.abstractmethod
    def send_message(self, terminal_id: TerminalId, message: OutgoingMessage):
        pass
