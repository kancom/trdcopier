from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..value_objects import (OrderType, OrderTypeFilling, Symbol, TradeAction,
                             TypeTime)


class Order(BaseModel):
    filterable = [
        "action",
        "symbol",
        "magic",
        "volume",
        "price",
        "stoplimit",
        "sl",
        "tp",
        "order_type",
        "order_type_filling",
        "comment",
    ]
    translateable = [
        "symbol",
        "magic",
        "action",
        "volume",
        "price",
        "stoplimit",
        "sl",
        "tp",
    ]
    risk_mgmt_realated = [
        "volume",
        "sl",
        "tp",
    ]

    action: TradeAction = Field(
        description="Trade operation type. Can be one of the ENUM_TRADE_REQUEST_ACTIONS enumeration values."
    )
    symbol: Symbol = Field(
        description="Symbol of the order. It is not necessary for order modification and position close operations.",
        filterable=True,
    )
    magic: int = Field(
        ge=0,
        description="Expert Advisor ID. It allows organizing analytical processing of trade orders. Each Expert Advisor can set its own unique ID when sending a trade request.",
    )
    # order_ticket: int = Field(ge=0, description='Order ticket. It is used for modifying pending orders.')
    volume: float = Field(
        ge=0,
        description="Requested order volume in lots. Note that the real volume of a deal will depend on the order execution type.",
    )
    price: float = Field(
        ge=0,
        description='Price, reaching which the order must be executed. Market orders of symbols, whose execution type is "Market Execution" (SYMBOL_TRADE_EXECUTION_MARKET), of TRADE_ACTION_DEAL type, do not require specification of price.',
    )
    stoplimit: Optional[float] = Field(
        ge=0,
        description="The price value, at which the Limit pending order will be placed, when price reaches the price value (this condition is obligatory). Until then the pending order is not placed.",
    )
    sl: Optional[float] = Field(
        ge=0, description="Stop Loss price in case of the unfavorable price movement"
    )
    tp: Optional[float] = Field(
        ge=0,
        description="Take Profit price in the case of the favorable price movement",
    )
    deviation: Optional[int] = Field(
        ge=0, description="The maximal price deviation, specified in points"
    )
    order_type: OrderType = Field(
        description="Order type. Can be one of the ENUM_ORDER_TYPE enumeration values."
    )
    order_type_filling: Optional[OrderTypeFilling] = Field(
        description="Order execution type. Can be one of the enumeration ENUM_ORDER_TYPE_FILLING values."
    )
    type_time: Optional[TypeTime] = Field(
        description="Order expiration type. Can be one of the enumeration ENUM_ORDER_TYPE_TIME values."
    )
    expiration: Optional[datetime] = Field(
        description="Order expiration time (for orders of ORDER_TIME_SPECIFIED type)"
    )
    comment: str = Field(default="", description="Order comment")
    position: Optional[int] = Field(
        description="Ticket of a position. Should be filled in when a position is modified or closed to identify the position. As a rule it is equal to the ticket of the order, based on which the position was opened."
    )
    position_by: Optional[int] = Field(
        description="Ticket of an opposite position. Used when a position is closed by an opposite one open for the same symbol in the opposite direction."
    )

    def __hash__(self):
        return hash(
            (
                self.action,
                self.symbol,
                self.magic,
                self.volume,
                self.price,
                self.stoplimit,
                self.sl,
                self.tp,
                self.deviation,
                self.order_type,
                self.order_type_filling,
                self.type_time,
                self.expiration,
                self.comment,
                self.position,
                self.position_by,
            )
        )
