from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (OrderType,
                                                          OrderTypeFilling,
                                                          Symbol, TradeAction,
                                                          TypeTime)


class Order(BaseModel):
    """
    Trade operation type. Can be one of the ENUM_TRADE_REQUEST_ACTIONS enumeration values.
    Expert Advisor ID. It allows organizing analytical processing of trade orders. Each Expert Advisor can set its own unique ID when sending a trade request.
    Order ticket. It is used for modifying pending orders.
    Symbol of the order. It is not necessary for order modification and position close operations.
    Requested order volume in lots. Note that the real volume of a deal will depend on the order execution type.
    Price, reaching which the order must be executed. Market orders of symbols, whose execution type is "Market Execution" (SYMBOL_TRADE_EXECUTION_MARKET), of TRADE_ACTION_DEAL type, do not require specification of price.
    The price value, at which the Limit pending order will be placed, when price reaches the price value (this condition is obligatory). Until then the pending order is not placed.
    Stop Loss price in case of the unfavorable price movement
    Take Profit price in the case of the favorable price movement
    The maximal price deviation, specified in points
    Order type. Can be one of the ENUM_ORDER_TYPE enumeration values.
    Order execution type. Can be one of the enumeration ENUM_ORDER_TYPE_FILLING values.
    Order expiration type. Can be one of the enumeration ENUM_ORDER_TYPE_TIME values.
    Order expiration time (for orders of ORDER_TIME_SPECIFIED type)
    Order comment
    Ticket of a position. Should be filled in when a position is modified or closed to identify the position. As a rule it is equal to the ticket of the order, based on which the position was opened.
    Ticket of an opposite position. Used when a position is closed by an opposite one open for the same symbol in the opposite direction.
    """

    action: TradeAction
    symbol: Symbol
    magic: int = Field(ge=0)
    order_ticket: int = Field(ge=0)
    volume: float = Field(ge=0)
    price: float = Field(ge=0)
    stoplimit: Optional[float] = Field(ge=0)
    sl: Optional[float] = Field(ge=0)
    tp: Optional[float] = Field(ge=0)
    deviation: Optional[int] = Field(ge=0)
    order_type: OrderType
    order_type_filling: Optional[OrderTypeFilling]
    type_time: Optional[TypeTime]
    expiration: Optional[datetime]
    comment: str = ""
    position: Optional[int] = None
    position_by: Optional[int] = None
