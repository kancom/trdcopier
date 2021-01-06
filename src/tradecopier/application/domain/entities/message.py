from typing import Optional, Union

from pydantic import BaseModel
from tradecopier.application.domain.entities.order import Order
from tradecopier.application.domain.value_objects import AccountId, TerminalId


class Message(BaseModel):
    terminal_id: TerminalId


class RegisterMessage(Message):
    name: Optional[str] = None
    is_cyphered: bool = False
    account_id: AccountId


class InTradeMessage(Message):
    body: Order
    account_id: AccountId
    is_cyphered: bool = False


class IncomingMessage(BaseModel):
    message: Union[RegisterMessage, InTradeMessage]


class AskRegistrationMessage(Message):
    body: str = "register"


class OutTradeMessage(Message):
    body: Order


class OutgoingMessage(BaseModel):
    message: Union[AskRegistrationMessage, OutTradeMessage]
