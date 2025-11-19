from datetime import datetime

from pydantic import BaseModel

from app.models.user import UserRole, UserStatus
from app.schemas.auth import AuthUser


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserDetail(AuthUser):
    created_at: datetime
