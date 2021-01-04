import factories
from use_case.receiving_message import ReceivingMessageUseCase


def test_receiving_message_register_on_new(mocker):
    wsca = mocker.patch(
        "infrastructure.adapters.connection_adapter.WebSocketsConnectionAdapter",
        autospec=True,
    )
    rp = mocker.patch(
        "infrastructure.register_terminal.RegisterPresenter", autospec=True
    )
    wsca.is_new_connection.return_value = True
    uc = ReceivingMessageUseCase(wsca, None, rp)
    reg_msg = factories.RegIncomingMessageFactory.create()
    uc.execute(reg_msg)
    assert wsca.is_new_connection.called
    assert rp.present.called


def test_receiving_message_non_register_on_new(mocker):
    wsca = mocker.patch(
        "infrastructure.adapters.connection_adapter.WebSocketsConnectionAdapter",
        autospec=True,
    )
    rp = mocker.patch(
        "infrastructure.register_terminal.RegisterPresenter", autospec=True
    )
    wsca.is_new_connection.return_value = True
    uc = ReceivingMessageUseCase(wsca, None, rp)
    reg_msg = factories.OrdIncomingMessageFactory.create()
    uc.execute(reg_msg)
    assert wsca.is_new_connection.called
    assert wsca.send_message.called
    assert not rp.present.called
