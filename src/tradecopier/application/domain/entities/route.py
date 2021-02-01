from typing import List, Optional

from pydantic import BaseModel, Field, validator
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import RouteId, RouteStatus


class Route(BaseModel):
    route_id: Optional[RouteId]
    source: Terminal
    destination: Terminal
    status: RouteStatus = RouteStatus.BOTH

    @validator("source")
    def validate_source(cls, v):
        if not v.is_active:
            raise ValueError("source must be active")
        return v

    @validator("destination")
    def validate_destination(cls, v):
        if not v.is_active:
            raise ValueError("destination must be active")
        return v

    def __eq__(self, other):
        if not isinstance(other, Route):
            return False
        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in ("source", "destination", "status")
        )
