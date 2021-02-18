import asyncio

import pytest
import websockets as ws
from pytest_factoryboy import register as register_factory
from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase
from tradecopier.infrastructure.adapters.connection_adapter import \
    WebSocketsConnectionAdapter

import factories

# from use_case.registering_terminal import RegisterTerminalUseCase


register_factory(factories.RouteFactory)
register_factory(factories.TerminalFactory)
register_factory(factories.RegisterMessageFactory)
register_factory(factories.RegIncomingMessageFactory)
register_factory(factories.OrdIncomingMessageFactory)
register_factory(factories.TradeMessageFactory)
register_factory(factories.RuleExpressionFactory)


@pytest.fixture
def terminals():
    terminals = factories.TerminalFactory.create_batch(5)
    yield terminals


@pytest.fixture(scope="session")
def ws_url():
    return "ws://localhost:6789"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope="session")
def application(event_loop):
    wsca = WebSocketsConnectionAdapter()
    # uc_reg = RegisterTerminalUseCase()
    # rp = RegisterPresenter(uc_reg)
    uc_rec = ReceivingMessageUseCase(wsca, None, None, None)
    start_server = wsca.start_server(uc_rec)
    event_loop.run_until_complete(start_server)
    # event_loop.run_forever()
    yield wsca


@pytest.fixture(scope="session")
def ws_client_send(ws_url, event_loop):
    def sub(msg):
        async def sender():
            async with ws.connect(ws_url) as websocket:
                await websocket.send(msg)

        event_loop.run_until_complete(sender())

    return sub
