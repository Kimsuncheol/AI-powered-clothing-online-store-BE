from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def change_role(
        self,
        db: Session,
        *,
        target_user_id: int,
        new_role: UserRole,
    ) -> User:
        user = self.user_repo.get_by_id(db, user_id=target_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return self.user_repo.update_role(db, user=user, role=new_role)

    def change_status(
        self,
        db: Session,
        *,
        target_user_id: int,
        new_status: UserStatus,
    ) -> User:
        user = self.user_repo.get_by_id(db, user_id=target_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return self.user_repo.update_status(db, user=user, status=new_status)
