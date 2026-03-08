# Database & Migrations

This project uses **SQLAlchemy 2.0** with **asyncio** and **Alembic** for schema management.

---

## 🗄️ Models Architecture

All database models inherit from `BaseModel` (located in `src/app/core/database/models.py`), which provides standard fields for all entities:

- **`uuid`**: Primary key (UUIDv7, ordered and time-sorted).
- **`created_at`**: Creation timestamp.
- **`modified_at`**: Last modification timestamp.
- **`created_by` / `modified_by`**: Foreign keys to the `User` who created or modified the record.
- **`is_deleted` / `deleted_at`**: Soft deletion flags.

### Example Model Definition
```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database.models import BaseModel

class MyEntity(BaseModel):
    __tablename__ = "my_entity"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
```

---

## 🛠️ CRUD Operations

We use a generic `CRUDBase` class in `src/app/core/helper/crud.py` to handle standard database operations asynchronously.

### Common CRUD Methods
- `get(db, **lookup)`: Fetch one record by its unique identifiers.
- `get_multi(db, offset, limit, filters, sort_columns, sort_orders)`: Paginated fetch of multiple records.
- `create(db, obj_in)`: Create a new record from a Pydantic schema.
- `update(db, db_obj, obj_in)`: Update an existing record with fields from a Pydantic schema.
- `soft_delete(db, db_obj)`: Mark a record as deleted without removing it from the database.
- `hard_delete(db, db_obj)`: Permanently remove a record.
- `exists(db, **lookup)`: Check if a record exists matching the given criteria.

### Using CRUD in Routers
```python
from src.app.crud.crud_user import crud_user

# Inside a FastAPI endpoint
user = await crud_user.get(db=db, uuid=user_uuid)
```

---

## 🔄 Migrations with Alembic

Alembic handles database schema versioning.

### 1. Create a New Migration
After modifying a model in `src/app/models/`, generate a new migration script:
```bash
uv run alembic -c src/alembic.ini revision --autogenerate -m "describe changes here"
```

### 2. Apply Migrations
Update your local database to the latest schema:
```bash
uv run alembic -c src/alembic.ini upgrade head
```

### 3. Revert Migrations
Roll back the last migration:
```bash
uv run alembic -c src/alembic.ini downgrade -1
```

---

## 🔍 Database Health Checks

The application includes a built-in health check for the database connection:
- **Endpoint:** `/api/v1/ready`
- **Logic:** `src/app/core/health.py`
