from uuid import uuid1

import factories
from tradecopier.application.domain.value_objects import CustomerType
from tradecopier.infrastructure.repositories.router_repo import \
    SqlAlchemyRouterRepo
from tradecopier.infrastructure.repositories.terminal_repo import \
    SqlAlchemyTerminalRepo


def test_router_repo(router_table, terminal_table, sql_conn, router_factory):
    term_repo = SqlAlchemyTerminalRepo(sql_conn)
    router_repo = SqlAlchemyRouterRepo(sql_conn)
    src_terminals = factories.TerminalFactory.build_batch(
        2, customer_type=CustomerType.SILVER
    )
    dst_terminals = factories.TerminalFactory.build_batch(
        3, customer_type=CustomerType.SILVER
    )
    router = router_factory()
    for terminal in src_terminals:
        router.add_source(terminal)
        term_repo.save(terminal)
    for terminal in dst_terminals:
        router.add_destination(terminal)
        term_repo.save(terminal)
    router_id = router_repo.save(router)
    router_from_db = router_repo.get(router_id)
    assert router_from_db == router

    router.remove_source(src_terminals[0])
    router_id = router_repo.save(router)
    router_from_db = router_repo.get(router_id)
    assert router_from_db == router

    router = router_factory()
    src_terminal = factories.TerminalFactory.build(customer_type=CustomerType.SILVER)
    router.add_source(src_terminal)
    router.add_source(src_terminals[1])
    for terminal in dst_terminals:
        router.add_destination(terminal)
    router_id = router_repo.save(router)
    routers = router_repo.get_by_src_terminal(src_terminals[1].terminal_id)
    assert len(routers) == 2


def test_terminal_repo(terminal_table, sql_conn):
    terminal = factories.TerminalFactory.build()
    repo = SqlAlchemyTerminalRepo(sql_conn)
    tid = uuid1()
    assert repo.get(tid) is None
    repo.save(terminal)
    assert repo.get(terminal.terminal_id) == terminal
    terminal.name = "name"
    repo.save(terminal)
    assert repo.get(terminal.terminal_id) == terminal
