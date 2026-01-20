"""
Order schemas
"""
from pydantic import BaseModel
from typing import List
from datetime import datetime
from .product import ProductOut


class OrderItemOut(BaseModel):
    """Schema for order item response"""
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductOut

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    """Schema for order response"""
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrderDetailOut(BaseModel):
    """Schema for detailed order response with items"""
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    order_items: List[OrderItemOut]

    class Config:
        from_attributes = True