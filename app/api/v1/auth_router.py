from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_auth_service
from app.models.user import User, UserRole
from app.schemas.auth import (
    AuthResponse,
    AuthUser,
    SignInRequest,
    SignUpRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    payload: SignUpRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    user, token = auth_service.signup(
        db,
        email=payload.email,
        password=payload.password,
        role=payload.role or UserRole.BUYER,
    )
    return AuthResponse(user=user, access_token=token)


@router.post("/signin", response_model=AuthResponse)
def signin(
    payload: SignInRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    user, token = auth_service.signin(
        db,
        email=payload.email,
        password=payload.password,
    )
    return AuthResponse(user=user, access_token=token)


@router.get("/me", response_model=AuthUser)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
