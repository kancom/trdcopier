from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator
from tradecopier.application import Terminal
from tradecopier.application.domain.value_objects import (FilterOperation,
                                                          RouteId, RouteStatus,
                                                          TerminalBrand,
                                                          TerminalId,
                                                          TransformOperation)


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
        if v is None and ("destination" not in values or values["destination"] is None):
            raise ValueError("both source and destination can't be empty")
        return v

    @validator("destination")
    def validate_dst(cls, v, values):
        if v is None and ("source" not in values or values["source"] is None):
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


class PeerTerminalId(BaseModel):
    identifier: str = Field(regex=r"[a-fA-F0-9\-]{12,36}")


class RuleDTO(BaseModel):
    number: int = Field(gt=0, lt=100, example=1)
    rule_type: Literal["filter", "transform"]
    field: str = Field(min_length=3, max_length=20, example="price")
    operator: Union[TransformOperation, FilterOperation, None] = Field(
        example=TransformOperation.ADD
    )
    value: Union[float, int, str, None] = Field(example=123.123)


class Rules(BaseModel):
    rules: List[RuleDTO] = Field(default_factory=list)


class PermittedRules(BaseModel):
    transform_operation_map: Dict[str, List[str]]
    filter_operation_map: Dict[str, List[str]]
    fields: Dict[str, str]
    enums: Dict[str, Dict[int, str]]
