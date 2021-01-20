from typing import List, Optional

from pydantic import BaseModel, Field
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import RouterId, RouteStatus


class Route(BaseModel):
    source: Terminal
    destination: Terminal
    status: RouteStatus


class Router(BaseModel):
    router_id: Optional[RouterId]
    routes: List[Route] = Field(default_factory=list)

    def add_route(
        self,
        source: Terminal,
        destination: Terminal,
        status: RouteStatus = RouteStatus.BOTH,
    ):

        assert source.is_active, "source must be active"
        assert destination.is_active, "destination must be active"
        assert not any(
            [route.destination == source for route in self.routes]
        ), "terminal loop schema"
        assert not any(
            [route.source == destination for route in self.routes]
        ), "terminal loop schema"
        for route in self.routes:
            if route.source == source and route.destination == destination:
                route.status = status
                return

        self.routes.append(Route(source=source, destination=destination, status=status))

    def remove_route(
        self,
        source: Terminal,
        destination: Terminal,
    ):
        idx = None
        for route in self.routes:
            if route.source == source and route.destination == destination:
                idx = self.routes.index(route)
                break
        if idx is not None:
            del self.routes[idx]
        else:
            raise IndexError("route was not found")
