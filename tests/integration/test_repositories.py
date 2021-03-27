import itertools
from uuid import uuid4

import factories
import pytest
from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.entities.rule import (ComplexRule,
                                                          Expression,
                                                          FilterRule,
                                                          TransformRule)
from tradecopier.application.domain.value_objects import (
    CustomerType, EntityNotFoundException, RouteStatus, TerminalType)
from tradecopier.infrastructure.repositories.route_repo import \
    SqlAlchemyRouteRepo
from tradecopier.infrastructure.repositories.rule_repo import \
    SqlAlchemyRuleRepo
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo


def test_route_repo(route_table, terminal_table, sql_conn, route_factory):
    term_repo = SqlAlchemyTerminalRepo(sql_conn)
    route_repo = SqlAlchemyRouteRepo(sql_conn)
    src_terminals = factories.TerminalFactory.build_batch(
        2, customer_type=CustomerType.SILVER
    )
    dst_terminals = factories.TerminalFactory.build_batch(
        3, customer_type=CustomerType.SILVER
    )
    route = Route(
        source=src_terminals[0], destination=dst_terminals[0], status=RouteStatus.BOTH
    )
    for terminal in itertools.chain(src_terminals, dst_terminals):
        term_repo.save(terminal)
    route_id = route_repo.save(route)
    assert route_id == route_repo.save(route)
    route_from_db = route_repo.get(route_id)
    assert route_from_db == route

    route_repo.delete(route_id)
    assert [] == route_repo.get_by_terminal_id(
        src_terminals[0].terminal_id, term_type=TerminalType.SOURCE
    )
    routes = [
        Route(source=src_terminals[0], destination=terminal, status=RouteStatus.BOTH)
        for terminal in dst_terminals
    ]
    for route in routes:
        route_repo.save(route)
    assert len(routes) == len(
        route_repo.get_by_terminal_id(
            src_terminals[0].terminal_id, term_type=TerminalType.SOURCE
        )
    )

    assert 1 == len(
        route_repo.get_by_terminal_id(
            dst_terminals[0].terminal_id, term_type=TerminalType.DESTINATION
        )
    )
    assert 0 == len(
        route_repo.get_by_terminal_id(
            dst_terminals[0].terminal_id, term_type=TerminalType.SOURCE
        )
    )
    assert len(
        route_repo.get_by_terminal_id(
            src_terminals[0].terminal_id, term_type=TerminalType.SOURCE
        )
    ) != len(
        route_repo.get_by_terminal_id(
            src_terminals[0].terminal_id, term_type=TerminalType.DESTINATION
        )
    )


def test_terminal_repo(terminal_table, sql_conn):
    terminal = factories.TerminalFactory.build()
    repo = SqlAlchemyTerminalRepo(sql_conn)
    tid = uuid4()
    assert repo.get(tid) is None
    repo.save(terminal)
    assert repo.get(terminal.terminal_id) == terminal
    terminal.name = "name"
    repo.save(terminal)
    assert repo.get(terminal.terminal_id) == terminal

    watcher_terminal_id = str(terminal.terminal_id)[-12:]
    assert repo.get_by_tail(watcher_terminal_id) == terminal


def test_rule_repo(rule_table, sql_conn, rule_expression_factory, terminal_factory):
    terminal = terminal_factory()
    repo = SqlAlchemyRuleRepo(sql_conn)
    cr = ComplexRule(terminal.terminal_id)
    exprs = rule_expression_factory.create_batch(3)
    for expr in exprs:
        cr.push_rule(FilterRule(terminal.terminal_id, expr))
    cr.push_rule(
        TransformRule(
            terminal.terminal_id,
            Expression(field="reverse", value=None, operator=None),
        )
    )
    repo.save(cr)
    cr_from_db = repo.get(terminal.terminal_id)
    assert cr_from_db == cr

    terminal2 = terminal_factory()
    expr = rule_expression_factory()
    fe = FilterRule(terminal2.terminal_id, expr)
    repo.save(fe)
    fe_from_db = repo.get(terminal2.terminal_id)
    assert fe_from_db == fe
