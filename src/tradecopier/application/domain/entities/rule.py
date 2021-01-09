from typing import Optional

from pydantic import BaseModel
from tradecopier.application.domain.entities.message import InTradeMessage
from tradecopier.application.domain.value_objects import RuleId


class Rule(BaseModel):
    id: Optional[RuleId]

    def apply(self, message: InTradeMessage) -> Optional[InTradeMessage]:
        return message
