import pytest
from decimal import Decimal
from app.models.product import Product, ProductStatus
from tests.conftest import create_product

def test_admin_can_list_products(client, create_admin, create_seller, db_session, auth_header_factory):
    admin = create_admin()
    seller = create_seller()
    p1 = create_product(db_session, seller_id=seller.id, name="P1")
    p2 = create_product(db_session, seller_id=seller.id, name="P2")
    
    headers = auth_header_factory(admin)
    response = client.get("/api/v1/admin/products", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    names = [p["name"] for p in data["items"]]
    assert "P1" in names
    assert "P2" in names

def test_admin_filter_products_by_seller_id(client, create_admin, create_seller, db_session, auth_header_factory):
    admin = create_admin()
    seller1 = create_seller(email="s1@example.com")
    seller2 = create_seller(email="s2@example.com")
    p1 = create_product(db_session, seller_id=seller1.id, name="S1 Product")
    p2 = create_product(db_session, seller_id=seller2.id, name="S2 Product")
    
    headers = auth_header_factory(admin)
    response = client.get(f"/api/v1/admin/products?seller_id={seller1.id}", headers=headers)
    
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "S1 Product"

def test_admin_filter_products_by_flagged_and_hidden(client, create_admin, create_seller, db_session, auth_header_factory):
    admin = create_admin()
    seller = create_seller()
    
    p_flagged = create_product(db_session, seller_id=seller.id, name="Flagged")
    p_flagged.is_flagged = True
    db_session.add(p_flagged)
    
    p_hidden = create_product(db_session, seller_id=seller.id, name="Hidden")
    p_hidden.is_hidden = True
    db_session.add(p_hidden)
    
    db_session.commit()
    
    headers = auth_header_factory(admin)
    
    # Filter flagged
    response = client.get("/api/v1/admin/products?is_flagged=true", headers=headers)
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Flagged"
    
    # Filter hidden
    response = client.get("/api/v1/admin/products?is_hidden=true", headers=headers)
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Hidden"

def test_admin_can_flag_product_with_reason(client, create_admin, create_seller, db_session, auth_header_factory):
    admin = create_admin()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id, name="To Flag")
    
    headers = auth_header_factory(admin)
    payload = {
        "action": "flag",
        "flag_reason": "Inappropriate content"
    }
    response = client.patch(f"/api/v1/admin/products/{product.id}", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged"] is True
    assert data["flag_reason"] == "Inappropriate content"
    
    # Verify DB
    db_session.refresh(product)
    assert product.is_flagged is True
    assert product.flag_reason == "Inappropriate content"

def test_admin_can_unflag_product(client, create_admin, create_seller, db_session, auth_header_factory):
    admin = create_admin()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id, name="To Unflag")
    product.is_flagged = True
    product.flag_reason = "Old reason"
    db_session.add(product)
    db_session.commit()
    
    headers = auth_header_factory(admin)
    payload = {"action": "unflag"}
    response = client.patch(f"/api/v1/admin/products/{product.id}", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged"] is False
    assert data["flag_reason"] is None

def test_admin_can_hide_and_unhide_product(client, create_admin, create_seller, db_session, auth_header_factory):
    admin = create_admin()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id, name="To Hide")
    
    headers = auth_header_factory(admin)
    
    # Hide
    response = client.patch(f"/api/v1/admin/products/{product.id}", json={"action": "hide"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["is_hidden"] is True
    
    # Unhide
    response = client.patch(f"/api/v1/admin/products/{product.id}", json={"action": "unhide"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["is_hidden"] is False

def test_admin_approve_product_clears_flags_and_unhides(client, create_admin, create_seller, db_session, auth_header_factory):
    admin = create_admin()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id, name="To Approve")
    product.is_flagged = True
    product.flag_reason = "Check this"
    product.is_hidden = True
    db_session.add(product)
    db_session.commit()
    
    headers = auth_header_factory(admin)
    response = client.patch(f"/api/v1/admin/products/{product.id}", json={"action": "approve"}, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged"] is False
    assert data["flag_reason"] is None
    assert data["is_hidden"] is False

def test_non_admin_cannot_moderate_product(client, create_buyer, create_seller, db_session, auth_header_factory):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id, name="Protected")
    
    headers = auth_header_factory(buyer)
    response = client.patch(f"/api/v1/admin/products/{product.id}", json={"action": "hide"}, headers=headers)
    assert response.status_code in [401, 403]
