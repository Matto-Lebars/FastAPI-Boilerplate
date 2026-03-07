import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer
from uuid6 import uuid7


class HealthCheck(BaseModel):
    status: str
    environment: str
    version: str
    timestamp: str


class ReadyCheck(BaseModel):
    status: str
    environment: str
    version: str
    app: str
    database: str
    redis: str
    timestamp: str


# -------------- mixins --------------
class UUIDSchema(BaseModel):
    uuid: uuid_pkg.UUID = Field(default_factory=uuid7)


class TimestampSchema(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    modified_at: datetime = Field(default=lambda: datetime.now(UTC).replace(tzinfo=None))

    @field_serializer("created_at")
    def serialize_dt(self, created_at: datetime | None, _info: Any) -> str | None:
        if created_at is not None:
            return created_at.isoformat()

        return None

    @field_serializer("modified_at")
    def serialize_modified_at(self, modified_at: datetime | None, _info: Any) -> str | None:
        if modified_at is not None:
            return modified_at.isoformat()

        return None


class AuditSchema(BaseModel):
    created_by: uuid_pkg.UUID | None = Field(default=None)
    modified_by: uuid_pkg.UUID | None = Field(default=None)


class PersistentDeletion(BaseModel):
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = False

    @field_serializer("deleted_at")
    def serialize_dates(self, deleted_at: datetime | None, _info: Any) -> str | None:
        if deleted_at is not None:
            return deleted_at.isoformat()

        return None
