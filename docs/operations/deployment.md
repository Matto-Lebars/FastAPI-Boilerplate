# Deployment

This project supports containerized deployment using **Docker** and automated documentation publishing with **GitHub Actions**.

---

## 🐳 Dockerized Deployment

The project is fully dockerized with a multi-stage `Dockerfile` optimized for size and security.

### Dockerfile Highlights
- **Base Image**: `python:3.14-slim`
- **Builder Stage**: Uses `uv` to install dependencies and compile bytecode.
- **Final Stage**:
    - Minimal runtime environment.
    - Runs as a **non-root user** (`app`) for security.
    - Exposes port `8000`.
- **Server**: Uses `uvicorn` (with optional `gunicorn` configuration for production).

### Production Build
To build and run the production image manually:
```bash
docker build -t my-fastapi-app -f docker/local_uvicorn/Dockerfile .
docker run -p 8000:8000 my-fastapi-app
```

---

## 🏗️ Infrastructure with Docker Compose

For more complex setups, the `docker-compose.yml` in `docker/local_uvicorn/` manages multiple services:

1.  **`app`**: The FastAPI backend.
2.  **`db`**: PostgreSQL with the PostGIS extension.

### Running in Production Mode
While the provided compose file is for local development, it can be adapted for production by:
- Setting `ENVIRONMENT=production` in `.env`.
- Removing `--reload` from the `uvicorn` command.
- Using a persistent volume for the database.

---

## 🚀 Continuous Deployment

### Documentation Publishing
We use **GitHub Actions** to automatically build and deploy this MkDocs documentation to **GitHub Pages**.

- **Workflow**: `.github/workflows/docs.yml`
- **Trigger**: Every push to the `main` branch.
- **Tools**: `uv` handles dependency installation and `mkdocs gh-deploy` handles the deployment.

### API Deployment (TODO)
Consider adding a GitHub Action workflow to:
1.  Run tests and linting.
2.  Build the Docker image.
3.  Push the image to a container registry (Docker Hub, GHCR).
4.  Deploy to your hosting provider (AWS, GCP, DigitalOcean, etc.).

---

## 📝 Best Practices for Production

1.  **Secrets Management**: Never use the default `SECRET_KEY`. Use a secure vault or environment variables.
2.  **Database Backups**: Regularly back up your PostgreSQL volumes.
3.  **HTTPS**: Always serve the API behind a reverse proxy (like Nginx or Traefik) that handles SSL termination.
4.  **Monitoring**: Use the `/api/v1/ready` endpoint to configure health checks in your deployment orchestrator (Kubernetes, Docker Swarm, etc.).
