"""
Payment routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models import Order, Payment
from app.schemas import PaymentOut
from app.dependencies import get_db, buyer_only
from app.services.payment_service import (
    process_payment,
    OrderNotFoundError,
    PaymentError
)

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)


@router.post("/orders/{order_id}/pay", response_model=PaymentOut)
def initiate_payment(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Initiate payment for an order (Buyer only)"""
    try:
        payment = process_payment(db, order_id, user.id)
        logger.info(f"Payment initiated: Order {order_id}, Attempt {payment.attempt}")
        return payment
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/orders/{order_id}/payments", response_model=List[PaymentOut])
def list_order_payments(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Get payment history for an order (Buyer only)"""
    # Verify order belongs to user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    payments = db.query(Payment).filter(
        Payment.order_id == order_id
    ).all()

    return payments