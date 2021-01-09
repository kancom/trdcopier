import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (Boolean, Column, Enum, Integer, MetaData, String,
                        Table)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import CHAR, DateTime, TypeDecorator
from tradecopier.application.domain.value_objects import (CustomerType,
                                                          TerminalType)

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class UUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    Source: https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = CHAR

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[str]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
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


FilterSetModel = Table(
    "filterset",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("set_id", Integer),
)

# terminal = relationship("TerminalModel", back_populates="filters")

TerminalModel = Table(
    "terminal",
    metadata,
    Column("terminal_id", UUID, primary_key=True),
    Column("name", String),
    Column("expire_at", DateTime),
    Column("registered_at", DateTime, default=datetime.now),
    Column("customer_type", Enum(CustomerType)),
    # Column("filter_set_id", Integer, ForeignKey("filterset.set_id")),
    Column("enabled", Boolean),
)

RouterModel = Table(
    "router",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("router_id", Integer, nullable=False),
    Column("terminal_id", UUID, nullable=False),
    Column("terminal_type", Enum(TerminalType), nullable=False),
)

# CustomerModel = Table(
#     "customer",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     # Column("account_id", String, index=True, unique=True),
#     Column("name", String),
#     Column("expire_at", DateTime),
#     Column("registered_at", DateTime, default=datetime.now),
#     Column("sources_mapping_id", Integer),
#     Column("destinations_mapping_id", Integer),
#     Column("customer_type", Enum(CustomerType)),
#     Column("enabled", Boolean),
# )


# filters = relationship("FilterSetModel", back_populates="terminal")

# def __eq__(self, other):
#     return isinstance(other, TerminalModel) and self.id == other.id
