import itertools
from uuid import uuid1

import factories
import pytest
from domain.entities.terminal import Terminal
from domain.value_objects import TerminalId
from infrastructure.repositories.customer_repo import SqlAlchemyCustomerRepo
from infrastructure.repositories.terminal_repo import SqlAlchemyTerminalRepo


def test_customer_repo(
    term2cust_table, customer_table, terminal_table, sql_conn, customer_factory
):
    src_terminals = factories.TerminalFactory.build_batch(2)
    dst_terminals = factories.TerminalFactory.build_batch(3)
    customer = customer_factory()
    term_repo = SqlAlchemyTerminalRepo(sql_conn)
    cust_repo = SqlAlchemyCustomerRepo(sql_conn)
    for terminal in src_terminals:
        customer.add_source(terminal)
        term_repo.save(terminal)
    for terminal in dst_terminals:
        customer.add_destination(terminal)
        term_repo.save(terminal)
    cust_id = cust_repo.save(customer)
    customer_from_db = cust_repo.get(cust_id)
    assert customer_from_db == customer
    customer.sources[0].is_active = False
    cust_id = cust_repo.save(customer)
    customer_from_db = cust_repo.get(cust_id)


def test_terminal_repo(terminal_table, sql_conn):
    terminal = factories.TerminalFactory.build()
    repo = SqlAlchemyTerminalRepo(sql_conn)
    tid = uuid1()
    assert repo.get(tid) is None
    repo.save(terminal)
    assert repo.get(terminal.id) == terminal
    terminal.name = "name"
    repo.save(terminal)
    assert repo.get(terminal.id) == terminal
