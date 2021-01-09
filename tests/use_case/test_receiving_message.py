import datetime
from uuid import uuid1

import factories
import pytest
from tradecopier.application.domain.value_objects import (
    CustomerType, EntityNotFoundException)
from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase


@pytest.fixture
def wsca(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.adapters.connection_adapter.WebSocketsConnectionAdapter",
        autospec=True,
    )


@pytest.fixture
def router_repo(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.repositories.router_repo.SqlAlchemyRouterRepo",
        autospec=True,
    )


@pytest.fixture
def term_repo(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.repositories.terminal_repo.SqlAlchemyTerminalRepo",
        autospec=True,
    )


@pytest.fixture
def rule_repo(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.repositories.rule_repo.SqlAlchemyRuleRepo",
        autospec=True,
    )


def test_receiving_message_register_on_new(wsca, router_repo, term_repo, rule_repo):
    """
    tests registration of new terminal
    with cyphered=SILVER and non-cyphered message
    """

    def cust_save(outer_terminal):
        def inner(terminal):
            for a in ("terminal_id", "expire_at", "customer_type"):
                assert getattr(outer_terminal, a) == getattr(terminal, a)

        return inner

    terminal_brz = factories.TerminalFactory(
        registered_at=datetime.datetime.now(),
        customer_type=CustomerType.BRONZE,
    )
    reg_msg_plain = factories.RegIncomingMessageFactory.create(
        terminal_id=terminal_brz.terminal_id
    )
    wsca.is_new_connection.return_value = True
    term_repo.save.side_effect = cust_save(terminal_brz)
    term_repo.get.return_value = None
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        router_repo=router_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
    )
    uc.execute(reg_msg_plain)
    assert wsca.is_new_connection.called
    assert term_repo.get.called

    terminal_slv = factories.TerminalFactory(
        registered_at=datetime.datetime.now(),
        customer_type=CustomerType.SILVER,
    )
    reg_msg_cyp = factories.RegIncomingMessageFactory(
        message=factories.RegisterMessageFactory(is_cyphered=True),
        terminal_id=terminal_brz.terminal_id,
    )
    term_repo.save.side_effect = cust_save(terminal_slv)
    uc.execute(reg_msg_cyp)


def test_receiving_message_non_register_on_new(
    wsca, mocker, router_repo, term_repo, rule_repo
):
    """
    ensure that ask registration message sent upon receive of
    non registration message for new connection
    """
    wsca.is_new_connection.return_value = True
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        router_repo=router_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
    )
    reg_msg = factories.OrdIncomingMessageFactory()
    reg_msg.message = factories.TradeMessageFactory()
    uc.execute(reg_msg)
    assert wsca.is_new_connection.called
    assert wsca.send_message.called


def test_resceiving_trade_msg_no_rules(wsca, router_repo, term_repo, rule_repo):
    """
    test bypass if not active
    test raising exception in case if no incoming rules defined.
    """
    router = factories.RouterFactory()
    dst_term = factories.TerminalFactory(customer_type=CustomerType.SILVER)
    src_term = factories.TerminalFactory()
    router.add_destination(dst_term)
    trd_msg = factories.OrdIncomingMessageFactory()
    trd_msg.message = factories.TradeMessageFactory()

    wsca.is_new_connection.return_value = False
    rule_repo.get_by_terminal_id.return_value = None

    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        router_repo=router_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
    )
    term_repo.get.return_value = src_term
    uc.execute(trd_msg)

    # is not active, thus - no processing
    rule_repo.get_by_terminal_id.assert_not_called()

    # no src rule - exception
    src_term = factories.TerminalFactory(customer_type=CustomerType.SILVER)
    term_repo.get.return_value = src_term
    with pytest.raises(EntityNotFoundException):
        uc.execute(trd_msg)


@pytest.mark.skip("looks excessive now")
def test_resceiving_trade_msg_with_rules(wsca, router_repo, term_repo, rule_repo):
    """
    test if src terminal != customer->source teminal found by account id
    then if equals - proceed
    """
    customer = factories.RouterFactory(customer_type=CustomerType.SILVER)
    dst_term = factories.TerminalFactory()
    src_term = factories.TerminalFactory()
    src_term.id = uuid1()
    customer.add_destination(dst_term)
    customer.add_source(src_term)
    trd_msg = factories.OrdIncomingMessageFactory()
    trd_msg.message = factories.TradeMessageFactory()

    wsca.is_new_connection.return_value = False
    rule_repo.get_by_terminal_id.return_value = factories.RuleFactory()

    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        router_repo=router_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
    )
    uc.execute(trd_msg)
    rule_repo.get_by_terminal_id.assert_not_called()

    customer.remove_source(src_term)
    src_term = factories.TerminalFactory()
    src_term.id = trd_msg.message.terminal_id
    customer.add_source(src_term)
    uc.execute(trd_msg)
    rule_repo.get_by_terminal_id.assert_called()
    wsca.send_message.assert_called()
