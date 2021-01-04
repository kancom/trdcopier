from domain.value_objects import FilterOperation, FilterType
from pydantic import BaseModel


class Filter(BaseModel):
    id: int
    field: str
    operation: FilterOperation
    value: str
    filter_type: FilterType = FilterType.ALLOW
