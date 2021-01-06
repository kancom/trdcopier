import datetime

import factories
from tradecopier.application.domain.value_objects import CustomerType
from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase


def test_receiving_message_register_on_new(mocker):
    """
    tests registration of new terminal and customer
    with cyphered=SILVER and non-cyphered message
    """

    def cust_save(outer_custome):
        def inner(customer):
            for a in ("id", "account_id", "expire_at", "customer_type"):
                assert getattr(outer_custome, a) == getattr(customer, a)

        return inner

    reg_msg_plain = factories.RegIncomingMessageFactory.create()
    customer_brz = factories.CustomerFactory(
        id=None,
        account_id=reg_msg_plain.message.account_id,
        registered_at=datetime.datetime.now(),
        customer_type=CustomerType.BRONZE,
    )
    reg_msg_cyp = factories.RegIncomingMessageFactory(
        message=factories.RegisterMessageFactory(is_cyphered=True)
    )
    customer_slv = factories.CustomerFactory(
        id=None,
        account_id=reg_msg_cyp.message.account_id,
        registered_at=datetime.datetime.now(),
        customer_type=CustomerType.SILVER,
    )
    wsca = mocker.patch(
        "tradecopier.infrastructure.adapters.connection_adapter.WebSocketsConnectionAdapter",
        autospec=True,
    )
    cust_repo = mocker.patch(
        "tradecopier.infrastructure.repositories.customer_repo.SqlAlchemyCustomerRepo",
        autospec=True,
    )
    term_repo = mocker.patch(
        "tradecopier.infrastructure.repositories.terminal_repo.SqlAlchemyTerminalRepo",
        autospec=True,
    )
    rule_repo = mocker.MagicMock()
    wsca.is_new_connection.return_value = True
    cust_repo.get_by_account.return_value = None
    cust_repo.save.side_effect = cust_save(customer_brz)
    term_repo.get.return_value = None
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        customer_repo=cust_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
    )
    uc.execute(reg_msg_plain)
    assert wsca.is_new_connection.called
    assert cust_repo.get_by_account.called
    assert term_repo.get.called
    cust_repo.save.side_effect = cust_save(customer_slv)
    uc.execute(reg_msg_cyp)


def test_receiving_message_non_register_on_new(mocker):
    wsca = mocker.patch(
        "tradecopier.infrastructure.adapters.connection_adapter.WebSocketsConnectionAdapter",
        autospec=True,
    )
    cust_repo = mocker.patch(
        "tradecopier.infrastructure.repositories.customer_repo.SqlAlchemyCustomerRepo",
        autospec=True,
    )
    term_repo = mocker.patch(
        "tradecopier.infrastructure.repositories.terminal_repo.SqlAlchemyTerminalRepo",
        autospec=True,
    )
    rule_repo = mocker.MagicMock()
    wsca.is_new_connection.return_value = True
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        customer_repo=cust_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
    )
    reg_msg = factories.OrdIncomingMessageFactory.create()
    uc.execute(reg_msg)
    assert wsca.is_new_connection.called
    assert wsca.send_message.called
