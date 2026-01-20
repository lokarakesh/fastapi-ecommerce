"""
Inventory management service
"""
from sqlalchemy.orm import Session
from app.models import Inventory


class InsufficientStockError(Exception):
    """Raised when product stock is insufficient"""
    pass


class InventoryError(Exception):
    """Raised when inventory operations fail"""
    pass


def check_stock(db: Session, product_id: int, quantity: int) -> bool:
    """Check if sufficient stock is available for a product"""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        raise InsufficientStockError(f"No inventory record found for product {product_id}")

    if inventory.stock < quantity:
        raise InsufficientStockError(
            f"Insufficient stock for product {product_id}. "
            f"Available: {inventory.stock}, Required: {quantity}"
        )

    return True


def reserve_stock(db: Session, product_id: int, quantity: int) -> None:
    """Reserve stock by decreasing inventory. Uses row-level locking."""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).with_for_update().first()

    if not inventory:
        raise InventoryError(f"No inventory record found for product {product_id}")

    if inventory.stock < quantity:
        raise InsufficientStockError(
            f"Insufficient stock for product {product_id}. "
            f"Available: {inventory.stock}, Required: {quantity}"
        )

    inventory.stock -= quantity


def release_stock(db: Session, product_id: int, quantity: int) -> None:
    """Release reserved stock by increasing inventory. Uses row-level locking."""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).with_for_update().first()

    if not inventory:
        raise InventoryError(f"No inventory record found for product {product_id}")

    inventory.stock += quantity


def get_available_stock(db: Session, product_id: int) -> int:
    """Get available stock for a product"""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        raise InventoryError(f"No inventory record found for product {product_id}")

    return inventory.stock