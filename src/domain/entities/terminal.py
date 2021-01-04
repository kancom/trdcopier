from typing import List, Optional
from uuid import uuid1

from domain.entities.filter import Filter
from domain.value_objects import CustomerId, TerminalId, TerminalType
from pydantic import BaseModel, Field


class Terminal(BaseModel):
    id: TerminalId = uuid1()
    customer_id: CustomerId
    name: Optional[str] = None
    terminal_type: TerminalType = TerminalType.DESTINATION
    # filters: List[Filter] = Field(default_factory=list)
    is_active: bool = True

    def __hash__(self):
        return hash(self.guid)
