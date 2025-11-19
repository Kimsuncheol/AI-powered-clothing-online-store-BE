from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, constr

from app.models.user import UserRole, UserStatus


class SignUpRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore[valid-type]
    role: Optional[UserRole] = UserRole.BUYER


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


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
