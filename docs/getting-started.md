# Getting Started

Follow these instructions to get your development environment up and running.

---

## Setup Options

=== "🐳 Docker"

    !!! info "Prerequisites"
        - **Docker & Docker Compose**

    ### 1. Navigate to the Docker Directory

    ```bash
    cd docker/local_uvicorn
    ```

    ### 2. Build and Start All Services

    ```bash
    docker compose up --build
    ```

    This starts:

    - The **FastAPI** application with hot-reloading
    - A **PostgreSQL + PostGIS** database container
    - Runs **Alembic migrations** automatically
    - Creates the **initial superuser** automatically

    !!! note
        The first build may take a few minutes to pull images and install dependencies.

=== "🖥️ Native (Local)"

    !!! info "Prerequisites"
        - **Python 3.14+**
        - **[uv](https://github.com/astral-sh/uv)** — fast Python package and project manager
        - **Docker & Docker Compose** — for running PostgreSQL with PostGIS (optional, but recommended for local development)
        - **PostgreSQL** — with PostGIS extension (optional)

    ### 1. Clone the Repository

    ```bash
    git clone https://github.com/Matto-Lebars/FastAPI-Boilerplate.git
    cd core-backend
    ```

    ### 2. Install Dependencies

    ```bash
    uv sync
    ```

    This creates a virtual environment and installs all dependencies defined in `pyproject.toml`.

    ### 3. Configure Environment

    Copy the example environment file and edit it with your local settings:

    ```bash
    cp docker/local_uvicorn/.env.example src/.env
    ```

    !!! tip
        Set `POSTGRES_SERVER=localhost` if your database is running locally (not in Docker).

    Key variables to configure:

    | Variable | Description | Default |
    |---|---|---|
    | `POSTGRES_SERVER` | Database host | `localhost` |
    | `POSTGRES_USER` | Database username | `postgres` |
    | `POSTGRES_PASSWORD` | Database password | `postgres` |
    | `POSTGRES_DB` | Database name | `postgres` |
    | `SECRET_KEY` | JWT signing key | _(change this!)_ |
    | `ENVIRONMENT` | `local`, `staging`, or `production` | `local` |


    ### 4. Start PostgreSQL in Docker (preferred) or Ensure Local DB is Running
    
    If you don't have a local PostgreSQL instance, you can start one using Docker:

    ```bash
    docker compose -f ./docker/local_uvicorn/docker-compose.yml up -d db
    ```

    ### 5. Run Migrations

    Ensure your PostgreSQL instance is running, then apply all migrations:

    ```bash
    uv run alembic -c src/alembic.ini upgrade head
    ```

    ### 6. Create the First Superuser

    ```bash
    uv run python -m src.scripts.create_first_superuser
    ```

    Default credentials are read from your `.env` file (`ADMIN_EMAIL`, `ADMIN_PASSWORD`).

    ### 7. Start the Development Server

    ```bash
    uv run uvicorn src.app.main:app --reload
    ```

    The API is now available at **`http://localhost:8000`**.

---

## Verifying the Setup

Once running, check the following URLs:

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Interactive Swagger UI |
| `http://localhost:8000/redoc` | ReDoc documentation |
| `http://localhost:8000/api/v1/health` | Application health check |
| `http://localhost:8000/api/v1/ready` | Readiness check (includes DB) |

---

## First API Request

### 1. Log in to get a token

```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@admin.com&password=!Ch4ng3Th1sP4ssW0rd!"
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### 2. Call a protected endpoint

```bash
curl http://localhost:8000/api/v1/user/me \
  -H "Authorization: Bearer <your_access_token>"
```

---

## Embedded bruno collection

!!! info "Prerequisites"
    - **[bruno](https://www.usebruno.com/)** — API testing and documentation tool

You can also explore the API using the embedded bruno collection. 
To do this open the bruno app and import the folder bruno_collection in the root of the project. 
This collection contains pre-configured requests for all API endpoints, allowing you to test and understand the API without writing any code.

---

## Next Steps

- 📖 [Understand the Architecture](architecture.md)
- 🗄️ [Learn about Database & Migrations](development/database.md)
- 🔐 [Read about Security & Auth](development/security.md)
- 📡 [Browse the API Reference](api/v1.md)
