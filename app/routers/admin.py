"""
Admin routes (Seller only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models import Order
from app.schemas import OrderOut
from app.dependencies import get_db, seller_only
from app.core.constants import ORDER_PLACED, ORDER_PAID, ORDER_SHIPPED, ORDER_DELIVERED, ORDER_CANCELLED
from app.services.payment_service import process_refund, PaymentError, OrderNotFoundError

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


@router.get("/orders", response_model=List[OrderOut])
def list_all_orders(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Get all orders with optional status filter (Seller only)"""
    query = db.query(Order)

    if status_filter:
        valid_statuses = [ORDER_PLACED, ORDER_PAID, ORDER_SHIPPED, ORDER_DELIVERED, ORDER_CANCELLED]
        if status_filter not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        query = query.filter(Order.status == status_filter)

    orders = query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
    return orders


@router.post("/orders/{order_id}/ship", response_model=OrderOut)
def ship_order(
    order_id: int,
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Mark order as shipped (Seller only)"""
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status != ORDER_PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {ORDER_PAID} orders can be shipped"
        )

    order.status = ORDER_SHIPPED
    db.commit()
    db.refresh(order)

    logger.info(f"Order shipped: ID {order_id}")
    return order


@router.post("/orders/{order_id}/deliver", response_model=OrderOut)
def deliver_order(
    order_id: int,
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Mark order as delivered (Seller only)"""
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status != ORDER_SHIPPED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {ORDER_SHIPPED} orders can be delivered"
        )

    order.status = ORDER_DELIVERED
    db.commit()
    db.refresh(order)

    logger.info(f"Order delivered: ID {order_id}")
    return order


@router.post("/orders/{order_id}/refund", response_model=OrderOut)
def refund_order(
    order_id: int,
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Process refund for an order (Seller only)"""
    try:
        order = process_refund(db, order_id)
        logger.info(f"Order refunded: ID {order_id}")
        return order
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