"""
Inventory schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from .product import ProductOut


class InventoryCreate(BaseModel):
    """Schema for creating inventory"""
    product_id: int = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class InventoryUpdate(BaseModel):
    """Schema for updating inventory"""
    stock: int = Field(..., ge=0)


class InventoryOut(BaseModel):
    """Schema for inventory response"""
    id: int
    product_id: int
    stock: int
    updated_at: datetime
    product: ProductOut

    class Config:
        from_attributes = True