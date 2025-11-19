from fastapi import FastAPI

from app.api.v1.admin_router import router as admin_router
from app.api.v1.auth_router import router as auth_router
from app.api.v1.products_router import router as products_router
from app.api.v1.seller_products_router import router as seller_products_router
from app.api.v1.cart_router import router as cart_router
from app.api.v1.orders_router import router as orders_router
from app.api.v1.payments_router import router as payments_router
from app.api.v1.ai_stylist_router import router as ai_stylist_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(products_router, prefix=settings.API_V1_PREFIX)
app.include_router(seller_products_router, prefix=settings.API_V1_PREFIX)
app.include_router(cart_router, prefix=settings.API_V1_PREFIX)
app.include_router(orders_router, prefix=settings.API_V1_PREFIX)
app.include_router(payments_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_stylist_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def read_root():
    return {"message": "AI Clothing Store API"}
