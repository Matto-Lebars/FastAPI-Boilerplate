<h1 align="center">FastAPI Boilerplate</h1>

<p align="center" markdown=1>
  <i>A modern, modular, and high-performance FastAPI boilerplate with async SQLAlchemy 2.0 and PostgreSQL.</i>
</p>

<p align="center">
  <a href="https://fastapi.tiangolo.com">
      <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  </a>
  <a href="https://www.postgresql.org">
      <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  </a>
  <a href="https://github.com/astral-sh/uv">
      <img src="https://img.shields.io/badge/uv-de5b43?style=for-the-badge&logo=python&logoColor=white" alt="uv">
  </a>
</p>

---

## ⚙️ Key Features

- **🚀 FastAPI Powered:** High-performance, async-first web framework.
- **🔐 JWT Security:** Robust authentication with token blacklisting (HS256).
- **🗄️ Async ORM:** SQLAlchemy 2.0 with asyncio and support for PostgreSQL, MySQL, and SQLite.
- **🛡️ Data Validation:** Pydantic v2 for seamless schema validation and environment settings.
- **📈 Structured Logging:** Enhanced observability using `structlog` and custom middleware.
- **⚡ Dependency Management:** Managed with `uv` for blazing-fast installations.
- **🐳 Dockerized:** One-command development and production environments.

---

## 🚀 Quick Start

### 1. Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [uv](https://github.com/astral-sh/uv) (for local development)

### 2. Environment Setup

```bash
# Copy the example environment variables
cp scripts/docker/.env.example src/.env
```

> [!IMPORTANT]
> Edit `src/.env` to configure your database credentials and secret keys.

### 3. Run with Docker

```bash
# Navigate to docker scripts
cd scripts/docker

# Build and start the containers
docker compose up --build -d
```

Once the containers are running, you can access the interactive API documentation at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 4. Local Development (without Docker)

```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn src.app.main:app --reload
```

---

## 📁 Architecture Overview

- `src/app/`: Core application logic.
    - `api/v1/`: Versioned API routes (health, login, logout, user).
    - `core/`: 
        - `config.py`: Centralized Pydantic-Settings configuration.
        - `setup.py`: Unified app creation, lifespan, and middleware setup.
        - `auth/`: JWT handling, security utilities, and token management.
        - `database/`: Async engine and session factory.
        - `helpers/`: Pagination and common utilities.
        - `exceptions/`: Domain-specific HTTP exceptions.
    - `crud/`: Generic and specialized CRUD classes for database operations.
    - `models/`: SQLAlchemy database models.
    - `schemas/`: Pydantic validation and transformation schemas.
    - `middleware/`: Custom middleware (e.g., logging request IDs).
- `scripts/docker/`: Docker-related configuration and scripts.
- `pyproject.toml`: Project metadata and dependencies managed by `uv`.
