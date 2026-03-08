# Security & Authentication

This document details the project's security implementation, focusing on JWT authentication and user authorization.

---

## 🔐 Authentication Mechanism

We use **JWT (JSON Web Tokens)** with the `HS256` algorithm for stateless authentication.

### Token Types
1.  **Access Token**: Short-lived (default 30 mins) used to authenticate requests.
2.  **Refresh Token**: Long-lived (default 7 days) used to obtain new access tokens.

---

## 🍪 Token Storage & Security

- **Access Token**: Returned in the JSON response body.
- **Refresh Token**: Stored in a **HttpOnly, Secure, SameSite=Lax** cookie to prevent XSS attacks.

### Authentication Flow
1.  **Login**: `/api/v1/login` returns an `access_token` and sets a `refresh_token` cookie.
2.  **Requests**: Client sends `Authorization: Bearer <access_token>` in headers.
3.  **Refresh**: `/api/v1/refresh` uses the refresh cookie to issue a new access token.
4.  **Logout**: `/api/v1/logout` blacklists both tokens and clears the refresh cookie.

---

## 🚫 Token Blacklisting

To support immediate logout and session invalidation, we use a database-backed **Token Blacklist**.

- **Model**: `TokenBlacklist` (in `src/app/core/auth/token_blacklist.py`)
- **Action**: When a token is verified, we check if it's already in the blacklist.
- **Cleanup**: (TODO) Implement a background task to remove expired tokens from the blacklist.

---

## 🛡️ User Authorization

FastAPI dependencies (in `src/app/api/dependencies.py`) handle authorization:

- **`get_current_user`**: Validates the access token and returns the authenticated `User` object.
- **`get_current_superuser`**: Checks the `is_superuser` flag on the current user.
- **`get_optional_user`**: Validates the token if present, but doesn't require it.

---

## 🔑 Password Hashing

We use **bcrypt** for secure password hashing.

- **Storage**: Only the hashed password is ever stored in the database.
- **Comparison**: `bcrypt.checkpw()` is used to verify passwords during login.
- **Implementation**: Located in `src/app/core/auth/security.py`.

---

## 🛠️ Security Settings

Settings are managed in `src/app/core/config.py` under the `CryptSettings` class:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Key for signing JWTs | `secret-key` (CHANGE THIS!) |
| `ALGORITHM` | Hashing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan | `7` |
