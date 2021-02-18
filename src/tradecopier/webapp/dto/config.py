from pydantic import BaseModel, Field
from tradecopier.application.domain.value_objects import RouteId


class DeleteRouteDTO(BaseModel):
    route_id: RouteId
