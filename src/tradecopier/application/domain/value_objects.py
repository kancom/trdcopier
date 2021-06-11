from enum import IntEnum, auto
from uuid import UUID

RouteId = int
RuleId = int
TerminalId = UUID
TerminalIdLen = 36
AccountId = str
Symbol = str


class TradeAction(IntEnum):
    DEAL = 0
    PENDING = 1
    SLTP = 2
    MODIFY = 3
    REMOVE = 4
    CLOSE_BY = 5


class OrderReason(IntEnum):
    ORDER_REASON_CLIENT = 0
    ORDER_REASON_MOBILE = auto()
    ORDER_REASON_WEB = auto()
    ORDER_REASON_EXPERT = auto()
    ORDER_REASON_SL = auto()
    ORDER_REASON_TP = auto()
    ORDER_REASON_SO = auto()


class OrderType(IntEnum):
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = auto()
    ORDER_TYPE_BUY_LIMIT = auto()
    ORDER_TYPE_SELL_LIMIT = auto()
    ORDER_TYPE_BUY_STOP = auto()
    ORDER_TYPE_SELL_STOP = auto()
    ORDER_TYPE_BUY_STOP_LIMIT = auto()
    ORDER_TYPE_SELL_STOP_LIMIT = auto()
    ORDER_TYPE_CLOSE_BY = auto()


class OrderTypeFilling(IntEnum):
    ORDER_FILLING_FOK = 0
    ORDER_FILLING_IOC = auto()
    ORDER_FILLING_RETURN = auto()


class TypeTime(IntEnum):
    ORDER_TIME_GTC = 0
    ORDER_TIME_DAY = auto()
    ORDER_TIME_SPECIFIED = auto()
    ORDER_TIME_SPECIFIED_DAY = auto()


class FilterOperation(IntEnum):
    LT = 0
    LE = auto()
    EQ = auto()
    GE = auto()
    GT = auto()
    NE = auto()
    IN = auto()


type_filter_operation_map = {
    "int": [
        FilterOperation.LT,
        FilterOperation.LE,
        FilterOperation.EQ,
        FilterOperation.GE,
        FilterOperation.GT,
        FilterOperation.NE,
    ],
    "float": [
        FilterOperation.LT,
        FilterOperation.LE,
        FilterOperation.EQ,
        FilterOperation.GE,
        FilterOperation.GT,
        FilterOperation.NE,
    ],
    "str": [FilterOperation.EQ, FilterOperation.NE, FilterOperation.IN],
    "OrderType": [FilterOperation.EQ, FilterOperation.NE],
    "OrderTypeFilling": [FilterOperation.EQ, FilterOperation.NE],
    "TradeAction": [FilterOperation.EQ, FilterOperation.NE],
    "TypeTime": [FilterOperation.EQ, FilterOperation.NE],
    "OrderReason": [FilterOperation.EQ, FilterOperation.NE],
}


class TransformOperation(IntEnum):
    SET = 100
    APPEND = auto()
    MULTIPLY = auto()
    ADD = auto()
    SETIF = auto()
    REVERSE = auto()


type_transform_operation_map = {
    TransformOperation.SET: ["int", "float", "str"],
    TransformOperation.MULTIPLY: ["int", "float"],
    TransformOperation.ADD: ["int", "float"],
    TransformOperation.APPEND: ["str"],
    TransformOperation.REVERSE: [],
    # TransformOperation.SETIF: [],
}


class FilterType(IntEnum):
    BLOCK = 0
    ALLOW = 1


class TerminalType(IntEnum):
    SOURCE = 0
    DESTINATION = 1
    UNKNOWN = 2


class RouteStatus(IntEnum):
    SOURCE = 0
    DESTINATION = 1
    BOTH = 2


class CustomerType(IntEnum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2


class EntityNotFoundException(Exception):
    pass


class TerminalBrand(IntEnum):
    UNKNOWN = 0
    METATRADER4 = auto()
    METATRADER5 = auto()
    QUIK = auto()
    WEB_BINANCE = auto()
