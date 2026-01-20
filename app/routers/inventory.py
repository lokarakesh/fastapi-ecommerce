"""
Inventory routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models import Inventory, Product
from app.schemas import InventoryCreate, InventoryUpdate, InventoryOut
from app.dependencies import get_db, seller_only

router = APIRouter(prefix="/inventory", tags=["Inventory"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=InventoryOut,
    status_code=status.HTTP_201_CREATED
)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Create inventory record for a product (Seller only)"""
    # Verify product exists
    product = db.get(Product, inventory.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check if inventory already exists
    existing = db.query(Inventory).filter(
        Inventory.product_id == inventory.product_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory already exists for this product"
        )

    inv = Inventory(
        product_id=inventory.product_id,
        stock=inventory.stock
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    logger.info(f"Inventory created: Product {inventory.product_id}, Stock {inventory.stock}")
    return inv


@router.get("", response_model=List[InventoryOut])
def list_inventory(
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Get all inventory records (Seller only)"""
    inventory = db.query(Inventory).all()
    return inventory


@router.get("/{product_id}", response_model=InventoryOut)
def get_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Get inventory for a specific product (Seller only)"""
    inv = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    return inv


@router.put("/{product_id}", response_model=InventoryOut)
def update_inventory(
    product_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db),
    seller=Depends(seller_only)
):
    """Update inventory stock (Seller only)"""
    inv = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )

    inv.stock = inventory.stock
    db.commit()
    db.refresh(inv)

    logger.info(f"Inventory updated: Product {product_id}, New stock {inventory.stock}")
    return inv