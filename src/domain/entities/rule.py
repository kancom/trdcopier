from typing import Optional

from domain.value_objects import RuleId
from pydantic import BaseModel

from message import IncomingMessage


class Rule(BaseModel):
    id: Optional[RuleId]

    def apply(self, message: IncomingMessage) -> Optional[IncomingMessage]:
        return message
