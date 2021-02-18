import asyncio
import json
import os
import sys
from typing import List, Optional

import dotenv

from main import SqlAlchemyTerminalRepo, get_db_connection
from tradecopier.application.domain import value_objects as vo
from tradecopier.application.domain.entities import message as msg
from tradecopier.application.domain.entities.order import Order
from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase
from tradecopier.infrastructure.adapters.connection_adapter import (
    ReceivingMessagePresenter, WebSocketsConnectionAdapter)
from tradecopier.infrastructure.repositories.route_repo import \
    SqlAlchemyRouteRepo
from tradecopier.infrastructure.repositories.rule_repo import \
    SqlAlchemyRuleRepo
from tradecopier.infrastructure.repositories.sql_model import RouteStatus
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo

src = {
    "account_id": 2,
    "terminal_id": "d327d84f-3f11-11eb-b357-d4258bbc0002",
    "broker": "brk@1234: mt5.123",
}
dst_term = [
    {
        "account_id": 10,
        "terminal_id": "d327d84f-3f11-11eb-b357-d4258bbc0010",
        "broker": "brk@4543: mt5.111",
    },
    {
        "account_id": 11,
        "terminal_id": "d327d84f-3f11-11eb-b357-d4258bbc0011",
        "broker": "brk@4543: mt4.122",
    },
]


def build_src():
    reg_msg = msg.IncomingMessage(
        message=msg.RegisterMessage(
            terminal_id=src["terminal_id"], name="source", broker=src["broker"]
        )
    )
    print(json.dumps(reg_msg.dict()))
    order = Order(
        action=vo.TradeAction.DEAL,
        symbol="EURUSD",
        magic=100,
        order_ticket=100,
        volume=10.1,
        price=1.2,
        order_type=vo.OrderType.ORDER_TYPE_BUY,
        order_type_filling=vo.OrderTypeFilling.ORDER_FILLING_FOK,
        type_time=vo.TypeTime.ORDER_TIME_DAY,
        comment="order1",
    )
    trd_msg = msg.IncomingMessage(
        message=msg.InTradeMessage(
            body=order, account_id=src["account_id"], terminal_id=src["terminal_id"]
        )
    )
    trd_msg.message = msg.InTradeMessage(
        body=order, account_id=src["account_id"], terminal_id=src["terminal_id"]
    )
    print(json.dumps(trd_msg.dict()))


def build_dst(terminal_id, broker):
    reg_msg = msg.IncomingMessage(
        message=msg.RegisterMessage(
            terminal_id=terminal_id, name="destination", broker=broker
        )
    )
    print(json.dumps(reg_msg.dict()))


def configure(db_conn):
    src_term = Terminal(
        terminal_id=src["terminal_id"], name="source_terminal", broker=src["broker"]
    )
    route_repo = SqlAlchemyRouteRepo(db_conn)
    term_repo = SqlAlchemyTerminalRepo(db_conn)
    for dst in dst_term:
        dst_t = Terminal(
            terminal_id=dst["terminal_id"],
            name="destination_terminal",
            broker=dst["broker"],
        )
        route = Route(source=src_term, destination=dst_t, status=RouteStatus.BOTH)
        route_repo.save(route)
        term_repo.save(dst_t)
    term_repo.save(src_term)


def main(argv: Optional[List[str]]) -> None:
    config_path = os.environ.get(
        "CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), os.pardir, ".env"),
    )
    dotenv.load_dotenv(config_path)
    wsca = WebSocketsConnectionAdapter()
    db_conn = get_db_connection()
    rec_msg_presenter = ReceivingMessagePresenter()
    route_repo = SqlAlchemyRouteRepo(db_conn)
    term_repo = SqlAlchemyTerminalRepo(db_conn)
    rule_repo = SqlAlchemyRuleRepo(db_conn)
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        route_repo=route_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
        outboundary=rec_msg_presenter,
    )

    build_src()
    for t in dst_term:
        build_dst(t["terminal_id"], t["broker"])
    configure(db_conn)
    start_server = wsca.start_server(uc, rec_msg_presenter)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
