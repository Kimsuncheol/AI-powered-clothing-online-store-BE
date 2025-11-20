import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, ValidationInfo, field_validator

from app.models.user import UserRole, UserStatus


PASSWORD_MIN_LENGTH = 8


def validate_password_strength(password: str) -> str:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain a digit.")
    if not re.search(r"[^\w\s]", password):
        raise ValueError("Password must contain a special character.")
    return password


class SignUpIn(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    role: Optional[UserRole] = UserRole.BUYER

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        value = email.strip()
        if len(value) > 255:
            raise ValueError("Email must be at most 255 characters.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        return validate_password_strength(password)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, confirm_password: str, info: ValidationInfo) -> str:
        password = info.data.get("password") if info and info.data else None
        if password is not None and confirm_password != password:
            raise ValueError("Passwords do not match.")
        return confirm_password


class SignInRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        value = email.strip()
        if len(value) > 255:
            raise ValueError("Email must be at most 255 characters.")
        return value


class AuthUser(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    status: UserStatus

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    user: AuthUser
    access_token: str
    token_type: str = "bearer"


# Backwards compatibility alias
SignUpRequest = SignUpIn
