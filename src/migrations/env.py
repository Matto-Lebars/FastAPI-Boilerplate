import asyncio
import importlib
import logging
import pkgutil

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Bootstrap structlog so that Alembic and SQLAlchemy log records are rendered
# the same way as the FastAPI application (see app/core/logger.py).
# We import the logger module which calls structlog.configure() and attaches
# the handlers to the root logger as a side-effect.
# ---------------------------------------------------------------------------
import app.core.logger  # noqa: F401 - side-effect import; configures structlog
from app.core.config import settings
from app.core.database.models import Base

# Silence noisy SQLAlchemy engine logs unless explicitly requested
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO if settings.ECHO_SQL else logging.WARNING)

# Alembic's own logger at INFO so migration progress is visible
logging.getLogger("alembic").setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Alembic config
# ---------------------------------------------------------------------------
config = context.config

config.set_main_option(
    "sqlalchemy.url",
    f"{settings.POSTGRES_ASYNC_PREFIX}{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
)

# Do NOT call fileConfig() here - logging is already configured by structlog above.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)


def import_models(package_name):
    package = importlib.import_module(package_name)
    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(module_name)


import_models("app.models")
target_metadata = Base.metadata


# Only these schemas are managed by Alembic
INCLUDE_SCHEMAS = {"public"}


# Build the set of (schema, table) pairs from our SQLAlchemy models
# This must be computed AFTER import_models() so all models are registered
_managed_tables = {(t.schema or "public", t.name) for t in target_metadata.sorted_tables}


def include_name(name, type_, parent_names):
    """Only include schemas and tables that belong to our application models."""
    if type_ == "schema":
        return name in INCLUDE_SCHEMAS
    if type_ == "table":
        schema = parent_names.get("schema") or "public"
        if schema not in INCLUDE_SCHEMAS:
            return False
        return (schema, name) in _managed_tables
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine and associate a connection with the context."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
