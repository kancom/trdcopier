import datetime
from uuid import uuid1

import factories
import pytest
from tradecopier.application.domain.entities.rule import Rule
from tradecopier.application.domain.value_objects import (
    CustomerType, EntityNotFoundException, RouteId, RouteStatus)
from tradecopier.application.use_case.receiving_message import \
    ReceivingMessageUseCase


@pytest.fixture
def route_repo(mocker):
    return mocker.patch(
        "tradecopier.infrastructure.repositories.route_repo.SqlAlchemyRouteRepo",
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


def test_receiving_message_register_on_new(
    wsca, route_repo, term_repo, rule_repo, recv_msg_bnd
):
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
        message=factories.RegisterMessageFactory(terminal_id=terminal_brz.terminal_id)
    )
    term_repo.save.side_effect = cust_save(terminal_brz)
    term_repo.get.return_value = None
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        route_repo=route_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
        outboundary=recv_msg_bnd,
    )
    uc.execute(reg_msg_plain)
    assert term_repo.get.called
    term_repo.save.side_effect = None

    terminal_slv = factories.TerminalFactory(
        registered_at=datetime.datetime.now(),
        customer_type=CustomerType.SILVER,
    )
    reg_msg_cyp = factories.RegIncomingMessageFactory(
        message=factories.RegisterMessageFactory(
            is_cyphered=True,
            terminal_id=terminal_slv.terminal_id,
        )
    )
    assert reg_msg_cyp.message.terminal_id == terminal_slv.terminal_id
    term_repo.save.side_effect = cust_save(terminal_slv)
    uc.execute(reg_msg_cyp)
    term_repo.save.side_effect = None


def test_receiving_message_non_register_on_new(
    wsca, mocker, route_repo, term_repo, rule_repo, recv_msg_bnd
):
    """
    ensure that ask registration message sent upon receive of
    non registration message for new connection
    """
    term_repo.get.return_value = None
    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        route_repo=route_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
        outboundary=recv_msg_bnd,
    )
    reg_msg = factories.OrdIncomingMessageFactory()
    reg_msg.message = factories.TradeMessageFactory()
    uc.execute(reg_msg)
    assert recv_msg_bnd.present.called


def test_resceiving_trade_msg_no_rules(
    wsca, route_repo, term_repo, rule_repo, recv_msg_bnd
):
    """
    test bypass if not active
    test raising exception in case if no incoming rules defined.
    """
    route = factories.RouteFactory()
    dst_term = factories.TerminalFactory(customer_type=CustomerType.SILVER)
    src_term = factories.TerminalFactory(enabled=False)
    # route.add_destination(dst_term)
    trd_msg = factories.OrdIncomingMessageFactory()
    trd_msg.message = factories.TradeMessageFactory()

    wsca.is_connected.return_value = False
    rule_repo.get.return_value = None

    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        route_repo=route_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
        outboundary=recv_msg_bnd,
    )
    term_repo.get.return_value = src_term
    uc.execute(trd_msg)

    # is not active, thus - no processing
    rule_repo.get.assert_not_called()

    # no src rule - exception
    src_term = factories.TerminalFactory(customer_type=CustomerType.SILVER)
    term_repo.get.return_value = src_term
    with pytest.raises(EntityNotFoundException):
        uc.execute(trd_msg)


def test_resceiving_trade_msg_one_way_confirmed(
    wsca, route_repo, term_repo, rule_repo, recv_msg_bnd
):
    route = factories.RouteFactory(status=RouteStatus.SOURCE)
    src_term = factories.TerminalFactory(customer_type=CustomerType.SILVER)

    trd_msg = factories.OrdIncomingMessageFactory()
    trd_msg.message = factories.TradeMessageFactory()

    wsca.is_connected.return_value = True
    route_repo.get_by_terminal_id.return_value = [route]
    rule_repo.get.return_value = Rule(src_term.terminal_id, None)

    uc = ReceivingMessageUseCase(
        conn_handler=wsca,
        route_repo=route_repo,
        terminal_repo=term_repo,
        rule_repo=rule_repo,
        outboundary=recv_msg_bnd,
    )
    term_repo.get.return_value = src_term
    uc.execute(trd_msg)
    recv_msg_bnd.present.assert_called_with([])

    route = factories.RouteFactory(status=RouteStatus.DESTINATION)
    route_repo.get_by_terminal_id.return_value = [route]
    uc.execute(trd_msg)
    recv_msg_bnd.present.assert_called_with([])
