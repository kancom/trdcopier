import factories
import pytest


@pytest.mark.integration
def test_recevive_reg_msg(application, ws_client_send, mocker):
    reg_msg = factories.RegIncomingMessageFactory.create_batch(2)
    ws_client_send(reg_msg[0].json())
    assert len(application._ws_register) == 1
    ws_client_send(reg_msg[0].json())
    assert len(application._ws_register) == 1
    ws_client_send(reg_msg[1].json())
    assert len(application._ws_register) == 2
