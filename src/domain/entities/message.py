from typing import Optional, Union

from domain.entities.order import Order
from domain.value_objects import AccountId, TerminalId
from pydantic import BaseModel


class Message(BaseModel):
    terminal_id: TerminalId


class RegisterMessage(Message):
    name: Optional[str]
    name: Optional[str] = None
    is_cyphered: bool = True
    account_id: AccountId


class InTradeMessage(Message):
    body: Order
    account_id: AccountId


class IncomingMessage(BaseModel):
    message: Union[RegisterMessage, InTradeMessage]


class AskRegistrationMessage(Message):
    body: str = "register"


class OutTradeMessage(Message):
    body: Order


class OutgoingMessage(BaseModel):
    message: Union[AskRegistrationMessage, OutTradeMessage]
