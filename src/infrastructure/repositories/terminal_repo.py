from typing import Optional

from domain.entities.terminal import Terminal
from domain.value_objects import TerminalId
from infrastructure.repositories.sql_model import TerminalModel
from sqlalchemy.engine import Connection

from repositories.terminal_repo import TerminalRepo


class SqlAlchemyTerminalRepo(TerminalRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get(self, terminal_id: TerminalId) -> Optional[Terminal]:
        db_terminal = self._conn.execute(
            TerminalModel.select().where(TerminalModel.c.id == terminal_id)
        ).first()
        if not db_terminal:
            return None
        return Terminal(**{k: v for k, v in db_terminal._mapping.items()})

    def save(self, terminal: Terminal) -> TerminalId:
        update_res = self._conn.execute(
            TerminalModel.update(
                values=terminal.dict(), whereclause=TerminalModel.c.id == terminal.id
            )
        )
        if update_res.rowcount != 1:
            insert_res = self._conn.execute(
                TerminalModel.insert(values=terminal.dict())
            )
        return terminal.id
