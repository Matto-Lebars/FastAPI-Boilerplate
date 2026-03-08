# Configuration

This project uses **[pydantic-settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)** for centralized configuration management.

---

## 🛠️ Settings Architecture

All configuration is managed in `src/app/core/config.py`. Settings are divided into logical base classes (e.g., `AppSettings`, `PostgresSettings`, `CORSSettings`) and then combined into a single `Settings` class.

### Key Configuration Classes
- **`AppSettings`**: Basic metadata about the application.
- **`CryptSettings`**: Security, hashing, and JWT signing settings.
- **`PostgresSettings`**: Database connection details for PostgreSQL.
- **`EnvironmentSettings`**: Determines the environment mode (`local`, `staging`, `production`).
- **`CORSSettings`**: Configures Cross-Origin Resource Sharing.
- **`FirstUserSettings`**: Credentials for the initial superuser.

---

## 📄 Environment Variables

Settings are loaded from environment variables or a `.env` file in the project root.

### The `.env` File
The application looks for a `.env` file at the root of the project (parent of `src`). You can copy the template:
```bash
cp docker/local_uvicorn/.env.example src/.env
```

!!! important
    **Never commit your `.env` file to version control.** It contains sensitive credentials.

### Example Configuration
```env
# Database Settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=my_secure_password
POSTGRES_SERVER=db
POSTGRES_DB=app_db

# Security Settings
SECRET_KEY=generate_a_long_random_string
ENVIRONMENT=local
```

---

## ➕ Adding New Settings

To add a new setting:

1.  **Identify the Class**: Decide which base class in `src/app/core/config.py` your new setting belongs to.
2.  **Add the Field**: Add the field with a type hint and an optional default value.
    ```python
    class AppSettings(BaseSettings):
        ...
        NEW_SETTING: str = "default_value"
    ```
3.  **Use the Setting**: Access the setting anywhere in the app via the `settings` object.
    ```python
    from src.app.core.config import settings
    print(settings.NEW_SETTING)
    ```

---

## 🧬 Dynamic Properties

Some settings are dynamically calculated using Pydantic's `@computed_field`. For example, `POSTGRES_URI` is automatically constructed from individual host, user, and password variables.

```python
@computed_field
@property
def POSTGRES_URI(self) -> str:
    return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
```
