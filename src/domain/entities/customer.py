from datetime import datetime
from typing import List, Optional, Union

from domain.entities.terminal import Terminal
from domain.value_objects import AccountId, CustomerId, CustomerType
from pydantic import BaseModel, Field


class Customer(BaseModel):
    id: Optional[CustomerId]
    account_id: AccountId
    name: Optional[str]
    expire_at: Optional[datetime]
    registered_at: datetime = datetime.now()
    sources: List[Terminal] = Field(default_factory=list)
    destinations: List[Terminal] = Field(default_factory=list)
    customer_type: CustomerType = CustomerType.BRONZE
    is_active: bool = True

    def add_source(self, terminal: Terminal) -> None:
        assert terminal.is_active, "terminal must be active"
        assert terminal not in self.destinations, "terminal loop schema"
        if terminal not in self.sources:
            terminal.customer_id = self.id
            self.sources.append(terminal)

    def add_destination(self, terminal: Terminal) -> None:
        assert terminal.is_active, "terminal must be active"
        assert terminal not in self.sources, "terminal loop schema"
        if terminal not in self.destinations:
            terminal.customer_id = self.id
            self.destinations.append(terminal)

    def remove_source(self, terminal: Terminal) -> int:
        if (idx := self.sources.index(terminal)) > 0:
            self.sources.pop(idx)
            return idx
        raise IndexError("terminal is not found")

    def remove_destination(self, terminal: Terminal) -> int:
        if (idx := self.destinations.index(terminal)) > 0:
            self.destinations.pop(idx)
            return idx
        raise IndexError("terminal is not found")

    @property
    def is_active(self) -> bool:
        if (not self.is_active) or (
            self.customer_type == CustomerType.BRONZE
            and datetime.now() > self.expire_at
        ):
            return False
        return True

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}): {self.name} active: {self.is_active}"
