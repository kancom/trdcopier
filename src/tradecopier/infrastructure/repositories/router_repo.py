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
            select(RouterModel.c.router_id)
            .distinct()
            .where(
                RouterModel.c.src_terminal_id == terminal_id,
            )
        )
        return [self.get(r.router_id) for r in router_id_lst]

    def get(self, router_id: RouterId) -> Router:
        db_router_rows = self._conn.execute(
            RouterModel.select().where(RouterModel.c.router_id == router_id)
        ).freeze()
        if not db_router_rows:
            raise EntityNotFoundException(f"{router_id} not found")
        # db_router_rows = [r for r in db_router_rows_iter]
        router = Router(
            router_id=router_id,
        )
        for row in db_router_rows():
            source = self._conn.execute(
                TerminalModel.select(
                    whereclause=TerminalModel.c.terminal_id == row.src_terminal_id
                )
            ).one()
            destination = self._conn.execute(
                TerminalModel.select(
                    whereclause=TerminalModel.c.terminal_id == row.dst_terminal_id
                )
            ).one()
            router.add_route(
                source=Terminal(**{k: v for k, v in source._mapping.items()}),
                destination=Terminal(**{k: v for k, v in destination._mapping.items()}),
                status=row.status,
            )

        return router

    def save(self, router: Router) -> RouterId:
        # obtain max router id
        # if router is in db - delete it for update
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

        for route in router.routes:
            self._conn.execute(
                RouterModel.insert(
                    values={
                        RouterModel.c.router_id: router_id,
                        RouterModel.c.src_terminal_id: route.source.terminal_id,
                        RouterModel.c.dst_terminal_id: route.destination.terminal_id,
                        RouterModel.c.status: route.status,
                    }
                )
            )
        return router_id
