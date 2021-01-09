from datetime import datetime
from typing import Optional
from uuid import uuid1

from pydantic import BaseModel
from tradecopier.application.domain.value_objects import (CustomerType,
                                                          TerminalId)

DEFAULT_LIFETIME = 60 * 60 * 24 * 60  # 60 days


class Terminal(BaseModel):
    terminal_id: TerminalId = uuid1()
    name: Optional[str] = None
    expire_at: Optional[datetime]
    registered_at: datetime = datetime.now()
    customer_type: CustomerType = CustomerType.BRONZE
    # filters: List[Filter] = Field(default_factory=list)
    enabled: bool = True

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
        return f"{self.__class__.__name__}({self.id}): {self.name} active: {self.is_active}"
