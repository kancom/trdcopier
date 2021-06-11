from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel
from tradecopier.application.domain.value_objects import (CustomerType,
                                                          TerminalBrand,
                                                          TerminalId)

DEFAULT_LIFETIME = 60 * 60 * 24 * 10  # 60 days


class Terminal(BaseModel):
    terminal_id: TerminalId = uuid4()
    broker: str
    name: Optional[str] = None
    expire_at: Optional[datetime]
    registered_at: datetime = datetime.now()
    customer_type: CustomerType = CustomerType.BRONZE
    enabled: bool = True

    @property
    def str_id(self):
        name = self.name if self.name is not None and self.name != "" else self.broker
        return name + "|" + self.terminal_id.hex[-12:]

    @property
    def expiration(self) -> Optional[datetime]:
        if self.expire_at is not None:
            return self.expire_at
        if self.customer_type == CustomerType.BRONZE:
            return self.registered_at + timedelta(seconds=DEFAULT_LIFETIME)

    @property
    def terminal_brand(self) -> int:
        result = TerminalBrand.UNKNOWN.value
        if self.broker != "":
            if ": mt4" in self.broker.lower():
                result = TerminalBrand.METATRADER4.value
            elif ": mt5" in self.broker.lower():
                result = TerminalBrand.METATRADER5.value

        return result

    def __hash__(self):
        return hash(self.terminal_id)

    @property
    def is_active(self) -> bool:
        if (not self.enabled) or (
            self.customer_type == CustomerType.BRONZE
            and (
                (self.expire_at and datetime.now() > self.expire_at)
                or (
                    not self.expire_at
                    and (datetime.now() - self.registered_at).total_seconds()
                    > DEFAULT_LIFETIME
                )
            )
        ):
            return False
        return True

    def __str__(self):
        return (
            f"{self.__class__.__name__}({self.terminal_id}):"
            f" {self.name} active: {self.is_active}"
        )
