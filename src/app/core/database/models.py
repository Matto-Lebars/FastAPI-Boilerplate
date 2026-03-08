import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid6 import uuid7


class UUIDMixin:
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, onupdate=lambda: datetime.now(UTC)
    )


class AuditMixin:
    created_by: Mapped[uuid_pkg.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.uuid"), nullable=True, default=None
    )
    modified_by: Mapped[uuid_pkg.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.uuid"), nullable=True, default=None
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class BaseModel(Base, UUIDMixin, TimestampMixin, AuditMixin, SoftDeleteMixin):
    """Base model that includes common fields and behaviors for all entities."""

    __abstract__ = True
