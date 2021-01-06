from typing import Optional

from pydantic import BaseModel
from tradecopier.application.domain.entities.message import IncomingMessage
from tradecopier.application.domain.value_objects import RuleId


class Rule(BaseModel):
    id: Optional[RuleId]

    def apply(self, message: IncomingMessage) -> Optional[IncomingMessage]:
        return message
