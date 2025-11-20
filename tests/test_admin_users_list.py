import pytest
from app.models.user import UserRole, UserStatus

def test_admin_can_list_users(client, create_admin, create_buyer, create_seller, auth_header_factory):
    admin = create_admin()
    buyer = create_buyer(email="buyer1@example.com")
    seller = create_seller(email="seller1@example.com")
    
    headers = auth_header_factory(admin)
    response = client.get("/api/v1/admin/users", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3
    
    emails = [u["email"] for u in data["items"]]
    assert admin.email in emails
    assert buyer.email in emails
    assert seller.email in emails

def test_admin_user_search_filters_by_email(client, create_admin, create_buyer, auth_header_factory):
    admin = create_admin()
    target = create_buyer(email="target@example.com")
    other = create_buyer(email="other@example.com")
    
    headers = auth_header_factory(admin)
    response = client.get("/api/v1/admin/users?search=target", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == target.email

def test_admin_user_filter_by_role_and_status(client, create_admin, create_buyer, create_seller, auth_header_factory, db_session):
    admin = create_admin()
    buyer = create_buyer(email="active_buyer@example.com")
    seller = create_seller(email="active_seller@example.com")
    
    # Create an inactive buyer manually since factory doesn't support status
    from app.models.user import User
    from app.core.security import get_password_hash
    inactive_buyer = User(
        email="inactive@example.com",
        password_hash=get_password_hash("password"),
        role=UserRole.BUYER,
        status=UserStatus.DEACTIVATED,
    )
    db_session.add(inactive_buyer)
    db_session.commit()
    
    headers = auth_header_factory(admin)
    
    # Filter by role BUYER
    response = client.get(f"/api/v1/admin/users?role={UserRole.BUYER.value}", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(item["role"] == UserRole.BUYER.value for item in items)
    emails = [i["email"] for i in items]
    assert buyer.email in emails
    assert inactive_buyer.email in emails
    assert seller.email not in emails
    
    # Filter by status DEACTIVATED
    response = client.get(f"/api/v1/admin/users?status={UserStatus.DEACTIVATED.value}", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["email"] == inactive_buyer.email

def test_non_admin_cannot_list_users(client, create_buyer, auth_header_factory):
    buyer = create_buyer()
    headers = auth_header_factory(buyer)
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code in [401, 403]
