import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (JSON, Boolean, Column, Enum, Integer, MetaData, String,
                        Table, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import CHAR, DateTime, TypeDecorator
from tradecopier.application.domain.value_objects import (CustomerType,
                                                          RouteStatus)

metadata = MetaData()


class UUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    Source: https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        # if dialect.name == "postgresql":
        #     return dialect.type_descriptor(UUID())
        # else:
        #     return dialect.type_descriptor(CHAR(32))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[str]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                if "%" in value:  # mine
                    return str(value)  # mine
                else:  # mine
                    return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value: Any, dialect: Any) -> Optional[uuid.UUID]:
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value  # type: ignore


TerminalModel = Table(
    "terminal",
    metadata,
    Column("terminal_id", UUID, primary_key=True),
    Column("broker", String(length=255)),
    Column("name", String(length=255)),
    Column("expire_at", DateTime),
    Column("registered_at", DateTime, default=datetime.now),
    Column("customer_type", Enum(CustomerType)),
    # Column("filter_set_id", Integer, ForeignKey("filterset.set_id")),
    Column("enabled", Boolean),
)


RouteModel = Table(
    "route",
    metadata,
    Column("route_id", Integer, primary_key=True),
    Column("src_terminal_id", UUID, index=True, nullable=False),
    Column("dst_terminal_id", UUID, nullable=False),
    Column("status", Enum(RouteStatus), nullable=False),
    UniqueConstraint("src_terminal_id", "dst_terminal_id", name="route"),
)

RuleModel = Table(
    "rule",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("terminal_id", UUID),
    Column("is_transform", Boolean, nullable=False),
    Column("field", String(length=255)),
    Column("value", String(length=255)),
    Column("operator", Integer, nullable=False),
)
