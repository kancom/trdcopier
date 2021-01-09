import asyncio
import sys
from typing import List, Optional

from sqlalchemy import create_engine

from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase
from tradecopier.infrastructure.adapters.connection_adapter import \
    WebSocketsConnectionAdapter
from tradecopier.infrastructure.repositories.router_repo import \
    SqlAlchemyRouterRepo
from tradecopier.infrastructure.repositories.rule_repo import \
    SqlAlchemyRuleRepo
from tradecopier.infrastructure.repositories.sql_model import metadata
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo


def get_db_connection():
    engine = create_engine("sqlite:///testdb.db", echo=False)
    create_db(engine)
    db_conn = engine.connect()
    return db_conn


def create_db(engine):
    metadata.create_all(engine)


def main(argv: Optional[List[str]]) -> None:
    db_conn = get_db_connection()
    wsca = WebSocketsConnectionAdapter()
    router_repo = SqlAlchemyRouterRepo(db_conn)
    term_repo = SqlAlchemyTerminalRepo(db_conn)
    rule_repo = SqlAlchemyRuleRepo(db_conn)
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        router_repo=router_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
    )

    start_server = wsca.start_server(uc)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
