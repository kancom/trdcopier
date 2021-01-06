from typing import Optional
from uuid import uuid1

from pydantic import BaseModel
from tradecopier.application.domain.value_objects import (CustomerId,
                                                          TerminalId,
                                                          TerminalType)


class Terminal(BaseModel):
    id: TerminalId = uuid1()
    customer_id: Optional[CustomerId]
    name: Optional[str] = None
    terminal_type: TerminalType = TerminalType.DESTINATION
    # filters: List[Filter] = Field(default_factory=list)
    enabled: bool = True

    def __hash__(self):
        return hash(self.guid)

    @property
    def is_active(self):
        return self.enabled
