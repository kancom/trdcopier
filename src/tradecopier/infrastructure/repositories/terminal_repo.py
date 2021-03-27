from typing import Optional

from sqlalchemy.engine import Connection
from sqlalchemy.exc import StatementError
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import TerminalId
from tradecopier.application.repositories.terminal_repo import TerminalRepo
from tradecopier.infrastructure.repositories.sql_model import TerminalModel


class SqlAlchemyTerminalRepo(TerminalRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get(self, terminal_id: TerminalId) -> Optional[Terminal]:
        try:
            db_terminal = self._conn.execute(
                TerminalModel.select().where(
                    TerminalModel.c.terminal_id == terminal_id,
                )
            ).first()
        except StatementError as e:
            return None
        if not db_terminal:
            return None
            # raise EntityNotFoundException(f"{terminal_id} not found")
        return Terminal(**{k: v for k, v in db_terminal._mapping.items()})

    def get_by_tail(self, terminal_id_tail: str) -> Optional[Terminal]:
        db_terminal = self._conn.execute(
            TerminalModel.select().where(
                TerminalModel.c.terminal_id.ilike(f"%{terminal_id_tail}"),
            )
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
        elif update_res.rowcount > 1:
            raise Exception("More than one row updated")
        return terminal.terminal_id
