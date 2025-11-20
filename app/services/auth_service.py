from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.auth import validate_password_strength


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def signup(
        self,
        db: Session,
        *,
        email: str,
        password: str,
        confirm_password: str | None = None,
        role: UserRole = UserRole.BUYER,
    ) -> Tuple[User, str]:
        existing_user = self.user_repo.get_by_email(db, email=email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use.",
            )

        if confirm_password is not None and password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet security requirements or does not match confirmation.",
            )

        try:
            validate_password_strength(password)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet security requirements or does not match confirmation.",
            )

        password_hash = get_password_hash(password)
        user = self.user_repo.create(
            db,
            email=email,
            password_hash=password_hash,
            role=role,
        )
        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        return user, access_token

    def signin(
        self,
        db: Session,
        *,
        email: str,
        password: str,
    ) -> Tuple[User, str]:
        user = self.user_repo.get_by_email(db, email=email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
            )

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        return user, access_token
