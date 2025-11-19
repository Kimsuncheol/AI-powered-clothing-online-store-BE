from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password


def test_password_hash_and_verify_works():
    password = "supersecret"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_create_access_token_and_decode():
    payload = {"sub": "1", "role": "admin"}
    token = create_access_token(payload)

    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert decoded["sub"] == "1"
    assert decoded["role"] == "admin"
