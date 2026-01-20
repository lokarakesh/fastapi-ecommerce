"""
Cart schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from .product import ProductOut


class CartAdd(BaseModel):
    """Schema for adding item to cart"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, gt=0)


class CartUpdate(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., gt=0)


class CartItemOut(BaseModel):
    """Schema for cart item response"""
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime
    product: ProductOut

    class Config:
        from_attributes = True