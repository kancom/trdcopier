import asyncio
import json
import logging
import sys
from typing import List, Optional

import websockets

from domain.entities.message import IncomingMessage
from infrastructure.adapters.connection_adapter import \
    WebSocketsConnectionAdapter
from infrastructure.register_terminal import RegisterPresenter
from use_case.receiving_message import ReceivingMessageUseCase


def main(argv: Optional[List[str]]) -> None:
    wsca = WebSocketsConnectionAdapter()
    rp = RegisterPresenter()
    uc = ReceivingMessageUseCase(wsca, None, rp)

    start_server = wsca.start_server(uc)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
