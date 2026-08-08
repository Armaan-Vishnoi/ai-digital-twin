from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def unique_email() -> str:
    return f"test-{uuid4().hex}@example.com"


def register_user(
    *,
    full_name: str = "Test User",
    email: str | None = None,
    password: str = "StrongPassword123!",
):
    return client.post(
        "/api/v1/auth/register",
        json={
            "full_name": full_name,
            "email": email or unique_email(),
            "password": password,
        },
    )


def login_user(
    email: str,
    password: str = "StrongPassword123!",
):
    return client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )


# ============================================================
# REGISTER
# ============================================================


def test_register_user():
    email = unique_email()

    response = register_user(
        full_name="Prem Test",
        email=email,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Prem Test"
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_verified"] is False

    # Password must never be returned.
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_fails():
    email = unique_email()

    first_response = register_user(
        email=email,
    )

    assert first_response.status_code == 201

    second_response = register_user(
        email=email,
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered."


# ============================================================
# LOGIN
# ============================================================


def test_login_returns_access_and_refresh_tokens():
    email = unique_email()

    register_response = register_user(
        email=email,
    )

    assert register_response.status_code == 201

    response = login_user(email)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)

    assert data["access_token"]
    assert data["refresh_token"]


def test_login_with_wrong_password_fails():
    email = unique_email()

    response = register_user(
        email=email,
    )

    assert response.status_code == 201

    response = login_user(
        email,
        password="WrongPassword123!",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_with_nonexistent_email_fails():
    response = login_user(
        unique_email(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


# ============================================================
# AUTHENTICATED USER
# ============================================================


def test_get_current_user_requires_authentication():
    response = client.get(
        "/api/v1/users/me",
    )

    assert response.status_code == 401


def test_get_current_user_with_valid_token():
    email = unique_email()

    register_response = register_user(
        full_name="Authenticated User",
        email=email,
    )

    assert register_response.status_code == 201

    login_response = login_user(email)

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Authenticated User"

    assert "hashed_password" not in data
    assert "password" not in data


def test_get_current_user_with_invalid_token_fails():
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


# ============================================================
# JWT CLAIMS
# ============================================================


def test_access_token_contains_expected_claims():
    email = unique_email()

    register_response = register_user(
        email=email,
    )

    assert register_response.status_code == 201

    login_response = login_user(email)

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    payload = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["email"] == email
    assert payload["type"] == "access"
    assert "sub" in payload
    assert "exp" in payload


def test_refresh_token_contains_refresh_type():
    email = unique_email()

    register_response = register_user(
        email=email,
    )

    assert register_response.status_code == 201

    login_response = login_user(email)

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    payload = jwt.decode(
        refresh_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["email"] == email
    assert payload["type"] == "refresh"
    assert "sub" in payload
    assert "exp" in payload


# ============================================================
# REFRESH TOKEN SECURITY
# ============================================================


def test_refresh_token_cannot_access_protected_endpoint():
    email = unique_email()

    register_response = register_user(
        email=email,
    )

    assert register_response.status_code == 201

    login_response = login_user(email)

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {refresh_token}",
        },
    )

    assert response.status_code == 401