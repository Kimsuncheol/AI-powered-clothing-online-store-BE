from fastapi import status

from app.core.security import create_access_token
from app.models.user import UserRole, UserStatus
from tests.conftest import create_user


def test_signup_success_creates_user_and_returns_token(client, db_session):
    payload = {
        "email": "newuser@example.com",
        "password": "supersecret",
        "role": UserRole.SELLER.value,
    }

    response = client.post("/api/v1/auth/signup", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["role"] == UserRole.SELLER.value
    assert data["access_token"]


def test_signup_fails_when_email_not_unique(client, db_session, create_buyer):
    create_buyer(email="duplicate@example.com")

    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "role": UserRole.BUYER.value,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_signup_role_defaults_to_buyer_when_not_provided(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "nole@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user"]["role"] == UserRole.BUYER.value


def test_signin_success_returns_token_and_user_info(client, create_buyer):
    user = create_buyer(email="signin@example.com", password="password123")

    response = client.post(
        "/api/v1/auth/signin",
        json={"email": user.email, "password": "password123"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["user"]["email"] == user.email
    assert body["access_token"]


def test_signin_fails_with_wrong_password(client, create_buyer):
    user = create_buyer(email="wrongpass@example.com", password="password123")

    response = client.post(
        "/api/v1/auth/signin",
        json={"email": user.email, "password": "badpassword"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_signin_fails_for_nonexistent_email(client):
    response = client.post(
        "/api/v1/auth/signin",
        json={"email": "missing@example.com", "password": "password123"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_signin_fails_if_user_banned_or_deactivated(client, db_session):
    for status_value in (UserStatus.DEACTIVATED, UserStatus.BANNED):
        user = create_user(
            db_session,
            email=f"{status_value.value}@example.com",
            password="password123",
            role=UserRole.BUYER,
            status=status_value,
        )
        response = client.post(
            "/api/v1/auth/signin",
            json={
                "email": user.email,
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_me_returns_current_user_when_token_valid(client, create_buyer):
    user = create_buyer(email="me@example.com")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == user.email


def test_get_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
