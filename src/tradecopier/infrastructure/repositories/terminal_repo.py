from typing import Optional

from sqlalchemy.engine import Connection
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (
    TerminalId)
from tradecopier.application.repositories.terminal_repo import TerminalRepo
from tradecopier.infrastructure.repositories.sql_model import TerminalModel


class SqlAlchemyTerminalRepo(TerminalRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get(self, terminal_id: TerminalId) -> Optional[Terminal]:
        db_terminal = self._conn.execute(
            TerminalModel.select().where(TerminalModel.c.terminal_id == terminal_id)
        ).first()
        if not db_terminal:
            return None
            # raise EntityNotFoundException(f"{terminal_id} not found")
        return Terminal(**{k: v for k, v in db_terminal._mapping.items()})

    def save(self, terminal: Terminal) -> TerminalId:
        update_res = self._conn.execute(
            TerminalModel.update(
                values=terminal.dict(),
                whereclause=TerminalModel.c.terminal_id == terminal.terminal_id,
            )
        )
        if update_res.rowcount != 1:
            insert_res = self._conn.execute(
                TerminalModel.insert(values=terminal.dict())
            )
        return terminal.terminal_id
