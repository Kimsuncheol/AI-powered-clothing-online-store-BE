from fastapi import status

from app.core.security import create_access_token
from app.models.user import UserRole, UserStatus
from tests.conftest import create_user


def _auth_header_for_user(user):
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_change_user_role(client, db_session, create_admin, create_buyer):
    admin = create_admin()
    user = create_buyer(email="targetrole@example.com")

    response = client.patch(
        f"/api/v1/admin/users/{user.id}/role",
        json={"role": UserRole.SELLER.value},
        headers=_auth_header_for_user(admin),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == UserRole.SELLER.value

    db_session.refresh(user)
    assert user.role == UserRole.SELLER


def test_non_admin_cannot_change_user_role(client, create_buyer):
    acting_user = create_buyer(email="acting@example.com")
    target_user = create_buyer(email="target@example.com")

    response = client.patch(
        f"/api/v1/admin/users/{target_user.id}/role",
        json={"role": UserRole.SELLER.value},
        headers=_auth_header_for_user(acting_user),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_deactivate_and_ban_user(client, create_admin, create_buyer, db_session):
    admin = create_admin()
    target_user = create_buyer(email="status@example.com")

    deactivate = client.patch(
        f"/api/v1/admin/users/{target_user.id}/status",
        json={"status": UserStatus.DEACTIVATED.value},
        headers=_auth_header_for_user(admin),
    )
    assert deactivate.status_code == status.HTTP_200_OK
    assert deactivate.json()["status"] == UserStatus.DEACTIVATED.value

    ban = client.patch(
        f"/api/v1/admin/users/{target_user.id}/status",
        json={"status": UserStatus.BANNED.value},
        headers=_auth_header_for_user(admin),
    )
    assert ban.status_code == status.HTTP_200_OK
    assert ban.json()["status"] == UserStatus.BANNED.value

    db_session.refresh(target_user)
    assert target_user.status == UserStatus.BANNED


def test_non_admin_cannot_change_status(client, create_buyer):
    acting_user = create_buyer(email="acting_status@example.com")
    target_user = create_buyer(email="target_status@example.com")

    response = client.patch(
        f"/api/v1/admin/users/{target_user.id}/status",
        json={"status": UserStatus.DEACTIVATED.value},
        headers=_auth_header_for_user(acting_user),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
