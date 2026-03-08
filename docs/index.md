<div class="hero-wrapper">
  <h1>core-backend</h1>
  <p>A modern, modular, and high-performance FastAPI boilerplate with async SQLAlchemy 2.0 and PostgreSQL.</p>
  <p>
    <a href="getting-started/" class="hero-btn">Get Started →</a>
  </p>
</div>

## Explore the Documentation

<div class="docs-grid">
  <a href="getting-started/" class="docs-card">
    <h3>🚀 Getting Started</h3>
    <p>Set up your local development environment and run your first API request.</p>
  </a>
  <a href="architecture/" class="docs-card">
    <h3>🏗️ Architecture</h3>
    <p>Understand the modular design patterns and project structure.</p>
  </a>
  <a href="api/v1/" class="docs-card">
    <h3>📡 API Reference</h3>
    <p>Browse the available endpoints for authentication, users, and more.</p>
  </a>
  <a href="development/database/" class="docs-card">
    <h3>🗄️ Database</h3>
    <p>Learn about SQLAlchemy models, migrations, and CRUD operations.</p>
  </a>
  <a href="development/security/" class="docs-card">
    <h3>🔐 Security</h3>
    <p>Deep dive into JWT implementation and security best practices.</p>
  </a>
  <a href="operations/deployment/" class="docs-card">
    <h3>🐳 Deployment</h3>
    <p>Instructions for production setup using Docker and GitHub Actions.</p>
  </a>
</div>

<br>

## Key Features

- **🚀 FastAPI Powered:** High-performance, async-first web framework.
- **🔐 JWT Security:** Robust authentication with access & refresh tokens and token blacklisting (HS256).
- **🗄️ Async ORM:** SQLAlchemy 2.0 with asyncio support for PostgreSQL (asyncpg) and PostGIS.
- **🛡️ Data Validation:** Pydantic v2 for seamless schema validation and environment settings.
- **📈 Structured Logging:** Enhanced observability using `structlog` and custom middleware.
- **⚡ Dependency Management:** Managed with `uv` for blazing-fast installations.
- **🐳 Dockerized:** One-command development and production environments.
- **🔄 DB Migrations:** Schema versioning via Alembic.
- **🧹 Code Quality:** Linting and formatting with `ruff`.

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Matto-Lebars/FastAPI-Boilerplate.git && cd fastapi-boilerplate

# 2. Configure environment
cp ./docker/local_uvicorn/.env.example ./src/.env

# 3. Run local uvicorn server with Docker Compose
docker compose -f ./docker/local_uvicorn/docker-compose.yml up --build
```

The API will be available at **`http://localhost:8000`**.
Interactive docs at **`http://localhost:8000/docs`**.

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL + PostGIS |
| Migrations | Alembic |
| Auth | python-jose (JWT HS256) + bcrypt |
| Validation | Pydantic v2 |
| Logging | structlog + Rich |
| Package Manager | uv |
| Containerization | Docker & Docker Compose |
