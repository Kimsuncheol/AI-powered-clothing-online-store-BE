from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.db.session import get_db
from app.dependencies import get_user_service
from app.models.user import User
from app.schemas.user import (
    UserDetail,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.patch("/users/{user_id}/role", response_model=UserDetail)
def update_user_role(
    user_id: int,
    body: UserRoleUpdate,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserDetail:
    updated_user = user_service.change_role(
        db,
        target_user_id=user_id,
        new_role=body.role,
    )
    return updated_user


@router.patch("/users/{user_id}/status", response_model=UserDetail)
def update_user_status(
    user_id: int,
    body: UserStatusUpdate,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserDetail:
    updated_user = user_service.change_status(
        db,
        target_user_id=user_id,
        new_status=body.status,
    )
    return updated_user
