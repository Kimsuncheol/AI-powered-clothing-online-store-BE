import pytest
from fastapi import HTTPException, status

from app.models.user import UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from tests.conftest import create_user


@pytest.fixture()
def auth_service() -> AuthService:
    return AuthService(UserRepository())


def test_signup_creates_user_and_hashes_password(auth_service, db_session):
    user, token = auth_service.signup(
        db_session,
        email="service_signup@example.com",
        password="password123",
        role=UserRole.SELLER,
    )

    assert user.id is not None
    assert user.password_hash != "password123"
    assert token


def test_signup_raises_when_email_exists(auth_service, db_session):
    create_user(
        db_session,
        email="duplicate_service@example.com",
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.signup(
            db_session,
            email="duplicate_service@example.com",
            password="password123",
            role=UserRole.BUYER,
        )
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


def test_signin_returns_user_and_token(auth_service, db_session):
    create_user(
        db_session,
        email="service_signin@example.com",
        password="password123",
    )

    user, token = auth_service.signin(
        db_session,
        email="service_signin@example.com",
        password="password123",
    )

    assert user.email == "service_signin@example.com"
    assert token


def test_signin_raises_on_bad_password(auth_service, db_session):
    create_user(
        db_session,
        email="service_badpass@example.com",
        password="password123",
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.signin(
            db_session,
            email="service_badpass@example.com",
            password="wrongpassword",
        )
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_signin_raises_on_unknown_email(auth_service, db_session):
    with pytest.raises(HTTPException) as exc:
        auth_service.signin(
            db_session,
            email="unknown@example.com",
            password="password123",
        )
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_signin_raises_when_user_not_active(auth_service, db_session):
    create_user(
        db_session,
        email="inactive@example.com",
        password="password123",
        status=UserStatus.BANNED,
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.signin(
            db_session,
            email="inactive@example.com",
            password="password123",
        )
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
