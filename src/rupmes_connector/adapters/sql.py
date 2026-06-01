from __future__ import annotations

from typing import Any

from sqlalchemy import MetaData, Table, and_, create_engine, or_, select, text
from sqlalchemy.engine import Engine

from rupmes_connector.adapters.base import BaseSourceAdapter
from rupmes_connector.checkpoint import Checkpoint
from rupmes_connector.config import SourceConfig


class SqlSourceAdapter(BaseSourceAdapter):
    def __init__(self, config: SourceConfig):
        self.config = config
        self.engine: Engine = create_engine(self.config.connection_url, future=True)
        self._table: Table | None = None

    def _get_table(self) -> Table:
        if self._table is None:
            metadata = MetaData()
            self._table = Table(
                self.config.table,
                metadata,
                schema=self.config.source_schema,
                autoload_with=self.engine,
            )
        return self._table

    def fetch_batch(self, checkpoint: Checkpoint) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            if self.config.query:
                params = {
                    "since_ts": checkpoint.last_value,
                    "last_id": checkpoint.last_id,
                    "limit": self.config.batch_size,
                }
                rows = connection.execute(text(self.config.query), params).mappings().all()
                return [dict(row) for row in rows]

            table = self._get_table()
            date_column = table.c[self.config.date_field]
            stmt = select(table)

            if self.config.id_field:
                id_column = table.c[self.config.id_field]
                if checkpoint.last_id is not None:
                    stmt = stmt.where(
                        or_(
                            date_column > checkpoint.last_value,
                            and_(date_column == checkpoint.last_value, id_column > checkpoint.last_id),
                        )
                    )
                else:
                    stmt = stmt.where(date_column >= checkpoint.last_value)
                stmt = stmt.order_by(date_column.asc(), id_column.asc())
            else:
                stmt = stmt.where(date_column > checkpoint.last_value)
                stmt = stmt.order_by(date_column.asc())

            for clause in self.config.extra_filters:
                stmt = stmt.where(text(clause))

            stmt = stmt.limit(self.config.batch_size)
            rows = connection.execute(stmt).mappings().all()
            return [dict(row) for row in rows]
