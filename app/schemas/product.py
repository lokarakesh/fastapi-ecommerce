"""
Product schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """Schema for creating a product"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=100)


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)


class ProductOut(BaseModel):
    """Schema for product response"""
    id: int
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True