from typing import Optional, Union

from pydantic import BaseModel
from tradecopier.application.domain.entities.order import Order
from tradecopier.application.domain.value_objects import AccountId, TerminalId


class Message(BaseModel):
    terminal_id: TerminalId

    def dict(self, *args, **kwargs):
        result = super().dict(*args, **kwargs)
        result["terminal_id"] = str(self.terminal_id)
        return result


class RegisterMessage(Message):
    name: Optional[str] = None
    is_cyphered: bool = False


class InTradeMessage(Message):
    body: Order
    account_id: AccountId
    is_cyphered: bool = False


class IncomingMessage(BaseModel):
    message: Union[
        InTradeMessage,
        RegisterMessage,
    ]


class AskRegistrationMessage(Message):
    body: str = "register"

    def __hash__(self):
        return hash(self.body)


class OutTradeMessage(Message):
    body: Order

    def __hash__(self):
        return hash(self.body)


class OutgoingMessage(BaseModel):
    message: Union[AskRegistrationMessage, OutTradeMessage]

    def __hash__(self):
        return hash(self.message)
