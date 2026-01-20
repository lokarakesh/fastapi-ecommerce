"""
Order routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models import Order
from app.schemas import OrderOut, OrderDetailOut
from app.dependencies import get_db, buyer_only
from app.services.order_service import (
    create_order_from_cart,
    cancel_order,
    OrderNotFoundError,
    CartEmptyError
)
from app.services.inventory_service import InsufficientStockError

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED
)
def place_order(
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Place an order from cart (Buyer only)"""
    try:
        order = create_order_from_cart(db, user.id)
        logger.info(f"Order placed: ID {order.id}, User {user.id}")
        return order
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CartEmptyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order processing failed"
        )


@router.get("", response_model=List[OrderOut])
def list_my_orders(
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Get current user's orders (Buyer only)"""
    orders = db.query(Order).filter(
        Order.user_id == user.id
    ).order_by(Order.id.desc()).all()
    return orders


@router.get("/{order_id}", response_model=OrderDetailOut)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Get detailed order information (Buyer only)"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_user_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Cancel an order (Buyer only)"""
    try:
        order = cancel_order(db, order_id, user.id)
        logger.info(f"Order cancelled: ID {order_id}")
        return order
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )