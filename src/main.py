import asyncio
import os
import sys
from typing import List, Optional

import dotenv
from sqlalchemy import create_engine

from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase
from tradecopier.infrastructure.adapters.connection_adapter import (
    ReceivingMessagePresenter, WebSocketsConnectionAdapter)
from tradecopier.infrastructure.repositories.route_repo import \
    SqlAlchemyRouteRepo
from tradecopier.infrastructure.repositories.rule_repo import \
    SqlAlchemyRuleRepo
from tradecopier.infrastructure.repositories.sql_model import metadata
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo


def get_db_connection():
    engine = create_engine(os.environ["DB_DSN"])
    create_db(engine)
    db_conn = engine.connect()
    return db_conn


def create_db(engine):
    metadata.create_all(engine)


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

    start_server = wsca.start_server(uc, rec_msg_presenter)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
