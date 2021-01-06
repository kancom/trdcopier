from pydantic import BaseModel
from tradecopier.application.domain.value_objects import (FilterOperation,
                                                          FilterType)


class Filter(BaseModel):
    id: int
    field: str
    operation: FilterOperation
    value: str
    filter_type: FilterType = FilterType.ALLOW
