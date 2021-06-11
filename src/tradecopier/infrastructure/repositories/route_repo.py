from typing import List

from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import functions
from tradecopier.application.domain.entities.route import Route
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (
    EntityNotFoundException, RouteId, TerminalId, TerminalType)
from tradecopier.application.repositories.route_repo import RouteRepo
from tradecopier.infrastructure.repositories.sql_model import (RouteModel,
                                                               TerminalModel)


class SqlAlchemyRouteRepo(RouteRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get_by_terminal_id(
        self, terminal_id: TerminalId, term_type: TerminalType
    ) -> List[Route]:
        cond = (
            RouteModel.c.src_terminal_id == terminal_id
            if term_type == TerminalType.SOURCE
            else RouteModel.c.dst_terminal_id == terminal_id
        )
        route_id_lst = self._conn.execute(
            select(RouteModel.c.route_id).distinct().where(cond)
        )
        return [self.get(r.route_id) for r in route_id_lst]

    def delete(self, route_id: RouteId) -> None:
        self._conn.execute(RouteModel.delete().where(RouteModel.c.route_id == route_id))

    def get(self, route_id: RouteId) -> Route:
        db_route_row = self._conn.execute(
            RouteModel.select().where(RouteModel.c.route_id == route_id)
        ).one_or_none()
        if db_route_row is None:
            raise EntityNotFoundException(f"{route_id} not found")
        source = self._conn.execute(
            TerminalModel.select(
                whereclause=TerminalModel.c.terminal_id == db_route_row.src_terminal_id
            )
        ).first()
        destination = self._conn.execute(
            TerminalModel.select(
                whereclause=TerminalModel.c.terminal_id == db_route_row.dst_terminal_id
            )
        ).first()
        if source is None or destination is None:
            raise EntityNotFoundException("terminal[s] for the route were not found")
        route = Route(
            route_id=route_id,
            source=Terminal(**{k: v for k, v in source._mapping.items()}),
            destination=Terminal(**{k: v for k, v in destination._mapping.items()}),
            status=db_route_row.status,
        )

        return route

    def save(self, route: Route) -> RouteId:
        # obtain max route id
        # if route is in db - delete it for update
        if route.route_id is not None:
            route_id = route.route_id
            self._conn.execute(
                RouteModel.delete(whereclause=RouteModel.c.route_id == route.route_id)
            )
        else:
            max_id = self._conn.execute(
                select(columns=[functions.max(RouteModel.c.route_id)])
            ).scalar()
            route_id = max_id + 1 if max_id is not None else 0

        existing_route_raw = self._conn.execute(
            RouteModel.select().where(
                and_(
                    RouteModel.c.src_terminal_id == route.source.terminal_id,
                    RouteModel.c.dst_terminal_id == route.destination.terminal_id,
                )
            )
        ).one_or_none()
        if existing_route_raw is None:
            self._conn.execute(
                RouteModel.insert(
                    values={
                        RouteModel.c.route_id: route_id,
                        RouteModel.c.src_terminal_id: route.source.terminal_id,
                        RouteModel.c.dst_terminal_id: route.destination.terminal_id,
                        RouteModel.c.status: route.status,
                    }
                )
            )
        else:
            route_id = existing_route_raw["route_id"]
            self._conn.execute(
                RouteModel.update(
                    values={"status": route.status},
                    whereclause=RouteModel.c.route_id == route_id,
                )
            )
        return route_id
