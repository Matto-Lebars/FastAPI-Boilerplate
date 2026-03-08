"""Generic async CRUD helper built on top of SQLAlchemy.

Usage example::

    from src.app.core.helper.crud import HelperCRUD
    from src.app.models.user import User

    crud_user = HelperCRUD(model=User)

    # Create
    user = await crud_user.create(db, obj_in=user_schema)

    # Read one
    user = await crud_user.get(db, uuid=some_uuid)

    # Read many with filters, sorting & schema conversion
    users = await crud_user.get_multi(
        db,
        filters={"is_superuser": False},
        sort_columns=["created_at"],
        sort_orders=["desc"],
        schema=UserRead,
    )
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypeVar

import structlog
from pydantic import BaseModel
from sqlalchemy import Select, and_, asc, desc, func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = structlog.stdlib.get_logger(__name__)


class CRUDBase[ModelType]:
    """Generic async CRUD helper for SQLAlchemy models.

    Parameters
    ----------
    model:
        The SQLAlchemy ORM model class to operate on.
    """

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model
        self._model_name: str = model.__name__

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_column(self, column_name: str):
        """Return a model column by name, or raise ``ValueError``."""
        mapper = inspect(self.model)
        if column_name not in mapper.columns:
            raise ValueError(f"Column '{column_name}' does not exist on model '{self._model_name}'.")
        return mapper.columns[column_name]

    def _apply_filters(self, stmt: Select, filters: dict[str, Any] | None) -> Select:
        """Apply simple equality filters to a SELECT statement."""
        if not filters:
            return stmt
        conditions = []
        for col_name, value in filters.items():
            column = self._get_column(col_name)
            conditions.append(column == value)
        return stmt.where(and_(*conditions))

    def _apply_sorting(
        self,
        stmt: Select,
        sort_columns: list[str] | str | None = None,
        sort_orders: list[str] | str | None = None,
    ) -> Select:
        """Apply ORDER BY clauses to a SELECT statement.

        Parameters
        ----------
        sort_columns:
            Column name(s) to sort on.
        sort_orders:
            ``"asc"`` or ``"desc"`` for each corresponding column.
            Defaults to ``"asc"`` when omitted.
        """
        if sort_columns is None:
            return stmt

        if isinstance(sort_columns, str):
            sort_columns = [sort_columns]

        if sort_orders is None:
            sort_orders = ["asc"] * len(sort_columns)
        elif isinstance(sort_orders, str):
            sort_orders = [sort_orders]

        if len(sort_columns) != len(sort_orders):
            raise ValueError(
                f"sort_columns ({len(sort_columns)}) and sort_orders ({len(sort_orders)}) must have the same length."
            )

        for col_name, order in zip(sort_columns, sort_orders, strict=True):
            column = self._get_column(col_name)
            if order.lower() == "desc":
                stmt = stmt.order_by(desc(column))
            else:
                stmt = stmt.order_by(asc(column))
        return stmt

    @staticmethod
    def _to_schema(
        row: ModelType,
        schema: type[BaseModel] | None = None,
    ) -> ModelType | BaseModel:
        """Optionally convert an ORM row to a Pydantic schema."""
        if schema is None:
            return row
        return schema.model_validate(row, from_attributes=True)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        """Insert a new row and return the refreshed ORM instance.

        Parameters
        ----------
        db:
            The async database session.
        obj_in:
            A Pydantic schema whose ``.model_dump()`` represents the row data.
        """
        log = logger.bind(model=self._model_name)
        try:
            db_obj = self.model(**obj_in.model_dump())
            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            log.info("record_created", uuid=str(getattr(db_obj, "uuid", None)))
            return db_obj
        except Exception:
            log.exception("create_failed")
            raise

    # ------------------------------------------------------------------
    # READ - single row
    # ------------------------------------------------------------------

    async def get(
        self,
        db: AsyncSession,
        *,
        filters: dict[str, Any] | None = None,
        schema: type[BaseModel] | None = None,
        **lookup: Any,
    ) -> ModelType | BaseModel | None:
        """Fetch a single row matching the given filters / lookup kwargs.

        Parameters
        ----------
        db:
            The async database session.
        filters:
            Dict of ``{column_name: value}`` equality filters.
        schema:
            Optional Pydantic model to convert the result.
        **lookup:
            Shorthand filters passed as keyword arguments
            (e.g. ``uuid=some_uuid``).  Merged with *filters*.
        """
        log = logger.bind(model=self._model_name)
        merged = {**(filters or {}), **lookup}
        if not merged:
            raise ValueError("At least one filter must be provided.")

        stmt = select(self.model)
        stmt = self._apply_filters(stmt, merged)

        try:
            result = await db.execute(stmt)
            row = result.scalars().first()
            if row is None:
                log.debug("record_not_found", filters=merged)
                return None
            return self._to_schema(row, schema)
        except Exception:
            log.exception("get_failed", filters=merged)
            raise

    # ------------------------------------------------------------------
    # READ - multiple rows
    # ------------------------------------------------------------------

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort_columns: list[str] | str | None = None,
        sort_orders: list[str] | str | None = None,
        schema: type[BaseModel] | None = None,
    ) -> list[ModelType] | list[BaseModel]:
        """Fetch multiple rows with optional filtering, sorting & pagination.

        Parameters
        ----------
        db:
            The async database session.
        offset / limit:
            Pagination controls.
        filters:
            Dict of equality filters.
        sort_columns / sort_orders:
            Sorting specification.
        schema:
            Optional Pydantic model for result conversion.
        """
        log = logger.bind(model=self._model_name)
        stmt = select(self.model)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_sorting(stmt, sort_columns, sort_orders)
        stmt = stmt.offset(offset).limit(limit)

        try:
            result = await db.execute(stmt)
            rows = list(result.scalars().all())
            if schema is not None:
                return [self._to_schema(r, schema) for r in rows]
            return rows
        except Exception:
            log.exception("get_multi_failed", filters=filters)
            raise

    # ------------------------------------------------------------------
    # COUNT
    # ------------------------------------------------------------------

    async def count(
        self,
        db: AsyncSession,
        *,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """Return the total number of rows matching *filters*."""
        log = logger.bind(model=self._model_name)
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply_filters(stmt, filters)

        try:
            result = await db.execute(stmt)
            return result.scalar_one()
        except Exception:
            log.exception("count_failed", filters=filters)
            raise

    # ------------------------------------------------------------------
    # EXISTS
    # ------------------------------------------------------------------

    async def exists(
        self,
        db: AsyncSession,
        *,
        filters: dict[str, Any] | None = None,
        **lookup: Any,
    ) -> bool:
        """Return ``True`` if at least one row matches the filters."""
        log = logger.bind(model=self._model_name)
        merged = {**(filters or {}), **lookup}
        if not merged:
            raise ValueError("At least one filter must be provided.")

        # Only fetch the PK to keep the query lightweight.
        pk_col = inspect(self.model).primary_key[0]
        stmt = select(pk_col).select_from(self.model)
        stmt = self._apply_filters(stmt, merged)
        stmt = stmt.limit(1)

        try:
            result = await db.execute(stmt)
            return result.scalars().first() is not None
        except Exception:
            log.exception("exists_failed", filters=merged)
            raise

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        auto_modified_at: bool = True,
    ) -> ModelType:
        """Patch an existing ORM instance with data from *obj_in*.

        Parameters
        ----------
        db_obj:
            The ORM instance to update (must already be loaded).
        obj_in:
            A Pydantic schema with the new values.  Only fields that are
            explicitly set (``exclude_unset=True``) will be applied.
        auto_modified_at:
            If ``True`` and the model has a ``modified_at`` column, it will be
            set to ``utcnow()`` automatically.
        """
        log = logger.bind(model=self._model_name)
        update_data = obj_in.model_dump(exclude_unset=True)

        if auto_modified_at and hasattr(db_obj, "modified_at"):
            update_data.setdefault("modified_at", datetime.now(UTC))

        try:
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            log.info("record_updated", uuid=str(getattr(db_obj, "uuid", None)))
            return db_obj
        except Exception:
            log.exception("update_failed")
            raise

    # ------------------------------------------------------------------
    # SOFT DELETE / RESTORE
    # ------------------------------------------------------------------

    async def soft_delete(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
    ) -> ModelType:
        """Mark a row as deleted (soft delete) using ``is_deleted`` / ``deleted_at``."""
        log = logger.bind(model=self._model_name)
        if not hasattr(db_obj, "is_deleted"):
            raise TypeError(f"Model '{self._model_name}' does not support soft delete (missing 'is_deleted' column).")

        try:
            db_obj.is_deleted = True  # type: ignore[attr-defined]
            db_obj.deleted_at = datetime.now(UTC)  # type: ignore[attr-defined]
            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            log.info("record_soft_deleted", uuid=str(getattr(db_obj, "uuid", None)))
            return db_obj
        except Exception:
            log.exception("soft_delete_failed")
            raise

    async def restore(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
    ) -> ModelType:
        """Restore a soft-deleted row."""
        log = logger.bind(model=self._model_name)
        if not hasattr(db_obj, "is_deleted"):
            raise TypeError(f"Model '{self._model_name}' does not support soft delete (missing 'is_deleted' column).")

        try:
            db_obj.is_deleted = False  # type: ignore[attr-defined]
            db_obj.deleted_at = None  # type: ignore[attr-defined]
            db.add(db_obj)
            await db.flush()
            await db.refresh(db_obj)
            log.info("record_restored", uuid=str(getattr(db_obj, "uuid", None)))
            return db_obj
        except Exception:
            log.exception("restore_failed")
            raise

    # ------------------------------------------------------------------
    # HARD DELETE
    # ------------------------------------------------------------------

    async def hard_delete(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
    ) -> None:
        """Permanently remove a row from the database."""
        log = logger.bind(model=self._model_name)
        try:
            await db.delete(db_obj)
            await db.flush()
            log.info("record_hard_deleted", uuid=str(getattr(db_obj, "uuid", None)))
        except Exception:
            log.exception("hard_delete_failed")
            raise
