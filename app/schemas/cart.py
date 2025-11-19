from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, conint


class CartItemCreate(BaseModel):
    product_id: int
    quantity: conint(gt=0) = 1
    variant_data: Optional[Dict[str, Any]] = None


class CartItemUpdate(BaseModel):
    quantity: conint(gt=0)


class CartItemSchema(BaseModel):
    id: int
    product_id: int
    quantity: int
    variant_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CartSchema(BaseModel):
    id: int
    user_id: int
    items: List[CartItemSchema]

    model_config = ConfigDict(from_attributes=True)
