import pytest
from decimal import Decimal
from app.models.order import Order, OrderStatus

def create_order(db, user_id, total_amount=Decimal("100.00"), status=OrderStatus.PENDING):
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        currency="USD",
        status=status
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def test_admin_can_list_all_orders(client, create_admin, create_buyer, db_session, auth_header_factory):
    admin = create_admin()
    buyer = create_buyer()
    o1 = create_order(db_session, buyer.id)
    o2 = create_order(db_session, buyer.id)
    
    headers = auth_header_factory(admin)
    response = client.get("/api/v1/admin/orders", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    ids = [o["id"] for o in data["items"]]
    assert o1.id in ids
    assert o2.id in ids

def test_admin_filter_orders_by_user_id(client, create_admin, create_buyer, db_session, auth_header_factory):
    admin = create_admin()
    buyer1 = create_buyer(email="b1@example.com")
    buyer2 = create_buyer(email="b2@example.com")
    
    o1 = create_order(db_session, buyer1.id)
    o2 = create_order(db_session, buyer2.id)
    
    headers = auth_header_factory(admin)
    response = client.get(f"/api/v1/admin/orders?user_id={buyer1.id}", headers=headers)
    
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == o1.id

def test_admin_filter_orders_by_status(client, create_admin, create_buyer, db_session, auth_header_factory):
    admin = create_admin()
    buyer = create_buyer()
    
    o_paid = create_order(db_session, buyer.id, status=OrderStatus.PAID)
    o_pending = create_order(db_session, buyer.id, status=OrderStatus.PENDING)
    
    headers = auth_header_factory(admin)
    response = client.get(f"/api/v1/admin/orders?status={OrderStatus.PAID.value}", headers=headers)
    
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == o_paid.id

def test_non_admin_cannot_list_orders(client, create_buyer, auth_header_factory):
    buyer = create_buyer()
    headers = auth_header_factory(buyer)
    response = client.get("/api/v1/admin/orders", headers=headers)
    assert response.status_code in [401, 403]
