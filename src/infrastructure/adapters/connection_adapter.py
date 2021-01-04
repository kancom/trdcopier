import json
from typing import Any, Awaitable, Callable, Dict

import websockets as ws
from domain.entities.message import IncomingMessage, OutgoingMessage
from domain.value_objects import TerminalId
from use_case.receiving_message import ReceivingMessageUseCase

from adapters.connection_adapter import ConnectionHandlerAdapter


class WebSocketsConnectionAdapter(ConnectionHandlerAdapter):
    def __init__(self, host: str = "localhost", port: int = 6789):
        self._host = host
        self._port = port
        self._server: ws.Serve = None
        self._ws_register: Dict[str, ws.WebSocketServerProtocol] = {}

    def _callback(self, uc: ReceivingMessageUseCase):
        async def consumer_handler(websocket: ws.WebSocketServerProtocol, path: str):
            async for message in websocket:
                print(type(message), message, websocket, path)
                inc_message = IncomingMessage(**json.loads(message))
                uc.execute(inc_message)
                self._register_ws(inc_message.message.terminal_id, websocket)

        return consumer_handler

    def _register_ws(
        self, terminal_id: TerminalId, wsproto: ws.WebSocketServerProtocol
    ):
        self._ws_register[str(terminal_id)] = wsproto

    def start_server(
        self,
        uc: ReceivingMessageUseCase,
    ):
        self._server = ws.serve(self._callback(uc), self._host, self._port)
        return self._server

    def disconnect(self, terminal_id: TerminalId):
        print("disconnect")
        assert str(terminal_id) in self._ws_register, "not known"
        self._ws_register[str(terminal_id)].close()

    def is_new_connection(self, terminal_id: TerminalId) -> bool:
        return str(terminal_id) in self._ws_register

    def send_message(self, terminal_id: TerminalId, message: OutgoingMessage):
        print("send", str(message))
