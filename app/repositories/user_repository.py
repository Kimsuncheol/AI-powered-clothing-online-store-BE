from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus


class UserRepository:
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, *, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def create(
        self,
        db: Session,
        *,
        email: str,
        password_hash: str,
        role: UserRole,
    ) -> User:
        user = User(email=email, password_hash=password_hash, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_role(self, db: Session, *, user: User, role: UserRole) -> User:
        user.role = role
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_status(self, db: Session, *, user: User, status: UserStatus) -> User:
        user.status = status
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
