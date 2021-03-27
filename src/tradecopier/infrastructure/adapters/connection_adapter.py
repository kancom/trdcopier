import asyncio
import json
from typing import Dict, Iterable, List, Tuple, Union

import websockets as ws
from loguru import logger
from tradecopier.application.adapters.connection_adapter import \
    ConnectionHandlerAdapter
from tradecopier.application.domain.entities.message import (IncomingMessage,
                                                             OutgoingMessage)
from tradecopier.application.domain.value_objects import TerminalId
from tradecopier.application.use_case.receiving_message import (
    ReceivingMessageBoundary, ReceivingMessageUseCase)


class ReceivingMessagePresenter(ReceivingMessageBoundary):
    def __init__(self):
        self._reply: List[Tuple[Iterable[TerminalId], OutgoingMessage]] = []

    def present(self, reply: List[Tuple[Iterable[TerminalId], OutgoingMessage]]):
        self._reply = reply

    def __iter__(self):
        self._iter = iter(self._reply)
        return self._iter

    def __next__(self):
        return next(self._iter)


class WebSocketsConnectionAdapter(ConnectionHandlerAdapter):
    def __init__(self, host: str = "", port: int = 6789):
        self._host = host
        self._port = port
        self._server: Union[ws.server.Serve, None] = None
        self._ws_register: Dict[str, ws.WebSocketServerProtocol] = {}

    def _callback(
        self, uc: ReceivingMessageUseCase, presenter: ReceivingMessagePresenter
    ):
        async def consumer_handler(in_ws: ws.WebSocketServerProtocol, path: str):
            try:
                async for message in in_ws:
                    logger.debug(
                        "{!r}, {!r}, {!r}, {!r}".format(
                            type(message), message, in_ws, path
                        )
                    )
                    inc_message = IncomingMessage(**json.loads(message))
                    uc.execute(inc_message)
                    for seq in presenter:
                        terminals, out_message = seq
                        for terminal_id in terminals:
                            out_ws = self._ws_register.get(str(terminal_id))
                            if (
                                out_ws is None
                                and inc_message.message.terminal_id == terminal_id
                            ):
                                await in_ws.send(json.dumps(out_message.dict()))
                            elif out_ws is not None:
                                await out_ws.send(json.dumps(out_message.dict()))
                    self._register_ws(inc_message.message.terminal_id, in_ws)
            except ws.exceptions.ConnectionClosedError as e:
                try:
                    del self._ws_register[str(inc_message.message.terminal_id)]
                finally:
                    raise Exception(str(e)) from e

        return consumer_handler

    def _register_ws(
        self, terminal_id: TerminalId, wsproto: ws.WebSocketServerProtocol
    ):
        self._ws_register[str(terminal_id)] = wsproto

    def start_server(
        self, uc: ReceivingMessageUseCase, presenter: ReceivingMessagePresenter
    ):
        self._server = ws.serve(self._callback(uc, presenter), self._host, self._port)
        logger.debug(str(self._server))
        return self._server

    def disconnect(self, terminal_id: TerminalId):
        logger.info("disconnect")
        assert str(terminal_id) in self._ws_register, "not known"
        self._ws_register[str(terminal_id)].close()

    def is_connected(self, terminal_id: TerminalId) -> bool:
        return str(terminal_id) in self._ws_register

    def send_message(self, terminal_id: TerminalId, message: OutgoingMessage):
        async def _send_message(ws, message: OutgoingMessage):
            await ws.send(json.dumps(message.dict()))

        logger.debug(f"send: {message}")
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(
            _send_message(self._ws_register[str(terminal_id)], message), loop=loop
        )
