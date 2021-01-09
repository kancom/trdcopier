from typing import List, Optional

from pydantic import BaseModel, Field
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import RouterId


class Router(BaseModel):
    router_id: Optional[RouterId]
    sources: List[Terminal] = Field(default_factory=list)
    destinations: List[Terminal] = Field(default_factory=list)

    def add_source(self, terminal: Terminal) -> None:
        assert terminal.is_active, "terminal must be active"
        assert terminal not in self.destinations, "terminal loop schema"
        if terminal not in self.sources:
            self.sources.append(terminal)

    def add_destination(self, terminal: Terminal) -> None:
        assert terminal.is_active, "terminal must be active"
        assert terminal not in self.sources, "terminal loop schema"
        if terminal not in self.destinations:
            self.destinations.append(terminal)

    def remove_source(self, terminal: Terminal) -> int:
        if (idx := self.sources.index(terminal)) >= 0:
            self.sources.pop(idx)
            return idx
        raise IndexError("terminal is not found")

    def remove_destination(self, terminal: Terminal) -> int:
        if (idx := self.destinations.index(terminal)) >= 0:
            self.destinations.pop(idx)
            return idx
        raise IndexError("terminal is not found")
