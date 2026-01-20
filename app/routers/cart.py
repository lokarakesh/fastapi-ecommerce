"""
Cart routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models import CartItem, Product
from app.schemas import CartAdd, CartUpdate, CartItemOut
from app.dependencies import get_db, buyer_only
from app.services.inventory_service import check_stock, InsufficientStockError

router = APIRouter(prefix="/cart", tags=["Cart"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=CartItemOut,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
    item: CartAdd,
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Add item to cart (Buyer only)"""
    # Verify product exists
    product = db.get(Product, item.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check inventory
    try:
        check_stock(db, item.product_id, item.quantity)
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.product_id == item.product_id
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    # Create new cart item
    cart_item = CartItem(
        user_id=user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    logger.info(f"Item added to cart: User {user.id}, Product {item.product_id}")
    return cart_item


@router.get("", response_model=List[CartItemOut])
def view_cart(
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """View current user's cart (Buyer only)"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == user.id
    ).all()
    return cart_items


@router.put("/{cart_item_id}", response_model=CartItemOut)
def update_cart_item(
    cart_item_id: int,
    update: CartUpdate,
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Update cart item quantity (Buyer only)"""
    item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == user.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    # Check stock for new quantity
    try:
        check_stock(db, item.product_id, update.quantity)
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    item.quantity = update.quantity
    db.commit()
    db.refresh(item)

    return item


@router.delete(
    "/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    user=Depends(buyer_only)
):
    """Remove item from cart (Buyer only)"""
    item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == user.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    db.delete(item)
    db.commit()

    logger.info(f"Cart item removed: ID {cart_item_id}")
    return None