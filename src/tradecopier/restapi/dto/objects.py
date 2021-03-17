from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator
from tradecopier.application import AddingRouteUseCase, RouteRepo, Terminal
from tradecopier.application.domain.value_objects import (RouteId, RouteStatus,
                                                          TerminalBrand,
                                                          TerminalId)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    terminal_id: TerminalId


class RouteEndpoints(BaseModel):
    source: Optional[Union[TerminalId, str]] = Field(
        example="7cc4e470-f562-4dca-85bf-da27c1b75987"
    )
    destination: Optional[Union[TerminalId, str]] = Field(example="da27c1b75987")

    @validator("source")
    def validate_src(cls, v, values):
        if v is None and ("destination" in values and values["destination"] is None):
            raise ValueError("both source and destination can't be empty")
        return v

    @validator("destination")
    def validate_dst(cls, v, values):
        if v is None and ("destination" in values and values["destination"] is None):
            raise ValueError("both source and destination can't be empty")
        return v


class RoutePeer(BaseModel):
    route_id: RouteId
    terminal_brand: TerminalBrand
    status: RouteStatus
    verbose_name: str


class RoutesPresenter(BaseModel):
    current_terminal: Terminal
    peers_type: Literal["sources", "destinations"]
    peers: List[RoutePeer]
