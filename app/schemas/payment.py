"""
Payment schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentOut(BaseModel):
    """Schema for payment response"""
    id: int
    order_id: int
    amount: float
    status: str
    attempt: int
    transaction_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True