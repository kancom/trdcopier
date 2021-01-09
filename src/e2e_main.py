import asyncio
import json
import sys
from typing import List, Optional

from main import SqlAlchemyTerminalRepo, get_db_connection
from tradecopier.application.domain import value_objects as vo
from tradecopier.application.domain.entities import message as msg
from tradecopier.application.domain.entities.order import Order
from tradecopier.application.domain.entities.router import Router
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase
from tradecopier.infrastructure.adapters.connection_adapter import (
    ReceivingMessagePresenter, WebSocketsConnectionAdapter)
from tradecopier.infrastructure.repositories.router_repo import \
    SqlAlchemyRouterRepo
from tradecopier.infrastructure.repositories.rule_repo import \
    SqlAlchemyRuleRepo
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo

src = {"account_id": 2, "terminal_id": "d327d84f-3f11-11eb-b357-d4258bbc0002"}
dst_term = [
    {"account_id": 10, "terminal_id": "d327d84f-3f11-11eb-b357-d4258bbc0010"},
    {"account_id": 11, "terminal_id": "d327d84f-3f11-11eb-b357-d4258bbc0011"},
]


def build_src():
    reg_msg = msg.IncomingMessage(
        message=msg.RegisterMessage(terminal_id=src["terminal_id"], name="source")
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


def build_dst(terminal_id):
    reg_msg = msg.IncomingMessage(
        message=msg.RegisterMessage(
            terminal_id=terminal_id,
            name="destination",
        )
    )
    print(json.dumps(reg_msg.dict()))


def configure(db_conn):
    router = Router()
    src_term = Terminal(terminal_id=src["terminal_id"], name="source_terminal")
    router_repo = SqlAlchemyRouterRepo(db_conn)
    term_repo = SqlAlchemyTerminalRepo(db_conn)
    router.add_source(src_term)
    term_repo.save(src_term)
    for dst in dst_term:
        dst_t = Terminal(terminal_id=dst["terminal_id"], name="destination_terminal")
        router.add_destination(dst_t)
        term_repo.save(dst_t)
    cust_id = router_repo.save(router)


def main(argv: Optional[List[str]]) -> None:
    wsca = WebSocketsConnectionAdapter()
    db_conn = get_db_connection()
    rec_msg_presenter = ReceivingMessagePresenter()
    router_repo = SqlAlchemyRouterRepo(db_conn)
    term_repo = SqlAlchemyTerminalRepo(db_conn)
    rule_repo = SqlAlchemyRuleRepo(db_conn)
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        router_repo=router_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
        outboundary=rec_msg_presenter,
    )

    build_src()
    for t in dst_term:
        build_dst(t["terminal_id"])
    configure(db_conn)
    start_server = wsca.start_server(uc, rec_msg_presenter)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
