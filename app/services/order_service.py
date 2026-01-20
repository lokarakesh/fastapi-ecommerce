"""
Order management service
"""
from sqlalchemy.orm import Session
from app.models import Order, CartItem, OrderItem, Product
from app.core.constants import ORDER_PLACED, ORDER_PAID, ORDER_SHIPPED, ORDER_DELIVERED, ORDER_CANCELLED
from app.services import inventory_service


class OrderNotFoundError(Exception):
    """Raised when order is not found"""
    pass


class CartEmptyError(Exception):
    """Raised when cart is empty"""
    pass


def create_order_from_cart(db: Session, user_id: int) -> Order:
    """Create an order from user's cart items"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == user_id
    ).all()

    if not cart_items:
        raise CartEmptyError("Cart is empty")

    # Create order
    order = Order(user_id=user_id, total_amount=0, status=ORDER_PLACED)
    db.add(order)
    db.flush()

    total = 0

    try:
        for cart_item in cart_items:
            # Reserve stock with locking
            inventory_service.reserve_stock(db, cart_item.product_id, cart_item.quantity)

            # Get product details
            product = db.get(Product, cart_item.product_id)
            cost = product.price * cart_item.quantity
            total += cost

            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=product.price
            )
            db.add(order_item)

            # Remove from cart
            db.delete(cart_item)

        # Update order total
        order.total_amount = total
        db.commit()
        db.refresh(order)

        return order

    except Exception as e:
        db.rollback()
        raise


def cancel_order(db: Session, order_id: int, user_id: int) -> Order:
    """Cancel an order and restore inventory"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        raise OrderNotFoundError(f"Order {order_id} not found")

    if order.status in [ORDER_SHIPPED, ORDER_DELIVERED]:
        raise ValueError(f"Order with status {order.status} cannot be cancelled")

    if order.status == ORDER_CANCELLED:
        raise ValueError("Order is already cancelled")

    try:
        # Get order items
        order_items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()

        # Restore inventory for each item
        for item in order_items:
            inventory_service.release_stock(db, item.product_id, item.quantity)

        # Update order status
        order.status = ORDER_CANCELLED
        db.commit()
        db.refresh(order)

        return order

    except Exception as e:
        db.rollback()
        raise


def get_order_by_id(db: Session, order_id: int, user_id: int = None) -> Order:
    """Get order by ID with optional user verification"""
    query = db.query(Order).filter(Order.id == order_id)

    if user_id:
        query = query.filter(Order.user_id == user_id)

    order = query.first()

    if not order:
        raise OrderNotFoundError(f"Order {order_id} not found")

    return order


def update_order_status(db: Session, order_id: int, new_status: str) -> Order:
    """Update order status with validation"""
    order = db.get(Order, order_id)

    if not order:
        raise OrderNotFoundError(f"Order {order_id} not found")

    # Validate status transitions
    valid_transitions = {
        ORDER_PLACED: [ORDER_PAID, ORDER_CANCELLED],
        ORDER_PAID: [ORDER_SHIPPED, ORDER_CANCELLED],
        ORDER_SHIPPED: [ORDER_DELIVERED],
        ORDER_DELIVERED: [],
        ORDER_CANCELLED: []
    }

    if new_status not in valid_transitions.get(order.status, []):
        raise ValueError(
            f"Invalid status transition from {order.status} to {new_status}"
        )

    order.status = new_status
    db.commit()
    db.refresh(order)

    return order