from enum import IntEnum, auto
from uuid import UUID

RouterId = int
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


class FilterType(IntEnum):
    BLOCK = 0
    ALLOW = 1


class TerminalType(IntEnum):
    SOURCE = 0
    DESTINATION = 1


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
