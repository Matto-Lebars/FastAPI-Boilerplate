# Development Workflow

This document outlines the standard development practices and tools used in this project.

---

## 🛠️ Essential Tools

- **[uv](https://github.com/astral-sh/uv)**: Used for all package and project management tasks. It's significantly faster than `pip` and `poetry`.
- **[ruff](https://github.com/astral-sh/ruff)**: An extremely fast Python linter and code formatter.
- **[pytest](https://docs.pytest.org/)**: The preferred testing framework.

---

## 🧹 Code Quality (Linting & Formatting)

We use **Ruff** to maintain high code quality and consistent formatting. Configuration is located in `pyproject.toml`.

### Check for Linting Errors
```bash
uv run ruff check .
```

### Auto-fix Linting Errors
```bash
uv run ruff check --fix .
```

### Format Code
```bash
uv run ruff format .
```

!!! tip
    We recommend configuring your IDE (VS Code, PyCharm, etc.) to run Ruff on save.

---

## 🧪 Testing

While a comprehensive test suite is under development, `pytest` is configured as the primary testing tool.

### Run All Tests
```bash
uv run pytest
```

---

## 🔄 Development Cycle

1. **Create a Branch:** Always work on a new feature or bugfix branch.
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Local Development:** Run the application locally with hot-reloading.
   ```bash
   uv run uvicorn src.app.main:app --reload
   ```
3. **Verify Changes:** Run linting and tests before committing.
   ```bash
   uv run ruff check .
   uv run ruff format .
   # uv run pytest (if tests are available)
   ```
4. **API Testing:** Use the embedded [Bruno collection](../../bruno_collection/) or Swagger UI at `http://localhost:8000/docs`.
5. **Commit & Push:** Follow conventional commit messages if possible.
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   git push origin feature/your-feature-name
   ```

---

## 📜 Project Scripts

The project includes utility scripts in `src/scripts/`:

- **`create_first_superuser.py`**: Creates the initial administrator account.
  ```bash
  uv run python -m src.scripts.create_first_superuser
  ```
