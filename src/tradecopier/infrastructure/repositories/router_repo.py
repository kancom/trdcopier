import itertools
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.engine import Connection
from sqlalchemy.sql import functions
from tradecopier.application.domain.entities.router import Router
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (
    EntityNotFoundException, RouterId, TerminalId, TerminalType)
from tradecopier.application.repositories.router_repo import RouterRepo
from tradecopier.infrastructure.repositories.sql_model import (RouterModel,
                                                               TerminalModel)


class SqlAlchemyRouterRepo(RouterRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get_by_src_terminal(self, terminal_id: TerminalId) -> List[Router]:
        router_id_lst = self._conn.execute(
            select(RouterModel.c.router_id).where(
                and_(
                    RouterModel.c.terminal_id == terminal_id,
                    RouterModel.c.terminal_type == TerminalType.SOURCE,
                )
            )
        )
        return [self.get(r[0]) for r in router_id_lst]

    def get(self, router_id: RouterId) -> Router:
        db_router_rows_iter = self._conn.execute(
            RouterModel.select().where(RouterModel.c.router_id == router_id)
        )
        if not db_router_rows_iter:
            raise EntityNotFoundException(f"{router_id} not found")
        db_router_rows = [r for r in db_router_rows_iter]
        src_terminals = self._conn.execute(
            TerminalModel.select(
                whereclause=TerminalModel.c.terminal_id.in_(
                    [
                        row.terminal_id
                        for row in db_router_rows
                        if row.terminal_type == TerminalType.SOURCE
                    ]
                )
            )
        )
        dst_terminals = self._conn.execute(
            TerminalModel.select(
                whereclause=TerminalModel.c.terminal_id.in_(
                    [
                        row.terminal_id
                        for row in db_router_rows
                        if row.terminal_type == TerminalType.DESTINATION
                    ]
                )
            )
        )
        router = Router(
            router_id=router_id,
            sources=[
                Terminal(**{k: v for k, v in terminal._mapping.items()})
                for terminal in src_terminals
            ],
            destinations=[
                Terminal(**{k: v for k, v in terminal._mapping.items()})
                for terminal in dst_terminals
            ],
        )
        return router

    def save(self, router: Router) -> RouterId:
        if router.router_id is not None:
            router_id = router.router_id
            self._conn.execute(
                RouterModel.delete(
                    whereclause=RouterModel.c.router_id == router.router_id
                )
            )
        else:
            max_id = self._conn.execute(
                select(columns=[functions.max(RouterModel.c.router_id)])
            ).scalar()
            router_id = max_id + 1 if max_id is not None else 0
        for terminal in router.sources:
            self._conn.execute(
                RouterModel.insert(
                    values={
                        RouterModel.c.router_id: router_id,
                        RouterModel.c.terminal_type: TerminalType.SOURCE,
                        RouterModel.c.terminal_id: terminal.terminal_id,
                    }
                )
            )
        for terminal in router.destinations:
            self._conn.execute(
                RouterModel.insert(
                    values={
                        RouterModel.c.router_id: router_id,
                        RouterModel.c.terminal_type: TerminalType.DESTINATION,
                        RouterModel.c.terminal_id: terminal.terminal_id,
                    }
                )
            )
        return router_id
