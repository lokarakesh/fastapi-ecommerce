"""
Payment processing service
"""
from sqlalchemy.orm import Session
from app.models import Order, Payment, OrderItem
from app.core.constants import (
    ORDER_PLACED, ORDER_PAID, ORDER_CANCELLED,
    PAY_INITIATED, PAY_SUCCESS, PAY_FAILED, PAY_REFUNDED,
    MAX_PAYMENT_ATTEMPTS
)
from app.services import inventory_service
import uuid


class PaymentError(Exception):
    """Raised when payment processing fails"""
    pass


class OrderNotFoundError(Exception):
    """Raised when order is not found"""
    pass


def process_payment(db: Session, order_id: int, user_id: int) -> Payment:
    """Process payment for an order"""
    # Verify order belongs to user and get it with lock
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).with_for_update().first()

    if not order:
        raise OrderNotFoundError(f"Order {order_id} not found")

    if order.status != ORDER_PLACED:
        raise PaymentError(f"Order with status {order.status} cannot be paid")

    # Get last payment attempt
    last_payment = db.query(Payment).filter(
        Payment.order_id == order.id
    ).order_by(Payment.attempt.desc()).first()

    attempt = 1 if not last_payment else last_payment.attempt + 1

    if attempt > MAX_PAYMENT_ATTEMPTS:
        raise PaymentError(
            f"Maximum payment attempts ({MAX_PAYMENT_ATTEMPTS}) exceeded for this order"
        )

    # Create payment record
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        status=PAY_INITIATED,
        attempt=attempt,
        transaction_id=str(uuid.uuid4())
    )
    db.add(payment)
    db.flush()

    try:
        # Simulate payment gateway processing
        success = simulate_payment_gateway(attempt)

        if success:
            payment.status = PAY_SUCCESS
            order.status = ORDER_PAID
        else:
            payment.status = PAY_FAILED

        db.commit()
        db.refresh(payment)

        return payment

    except Exception as e:
        db.rollback()
        raise PaymentError(f"Payment processing failed: {str(e)}")


def simulate_payment_gateway(attempt: int) -> bool:
    """
    Simulate payment gateway response
    Even attempts succeed, odd attempts fail
    """
    return attempt % 2 == 0


def process_refund(db: Session, order_id: int) -> Order:
    """Process refund for an order"""
    order = db.query(Order).filter(
        Order.id == order_id
    ).with_for_update().first()

    if not order:
        raise OrderNotFoundError(f"Order {order_id} not found")

    if order.status != ORDER_PAID:
        raise PaymentError(f"Only {ORDER_PAID} orders can be refunded")

    # Find successful payment
    payment = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.status == PAY_SUCCESS
    ).first()

    if not payment:
        raise PaymentError("No successful payment found for this order")

    try:
        # Get order items to restore inventory
        order_items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()

        # Restore inventory for each item
        for item in order_items:
            inventory_service.release_stock(db, item.product_id, item.quantity)

        # Update payment status
        payment.status = PAY_REFUNDED

        # Update order status
        order.status = ORDER_CANCELLED

        db.commit()
        db.refresh(order)

        return order

    except Exception as e:
        db.rollback()
        raise PaymentError(f"Refund processing failed: {str(e)}")


def get_payment_history(db: Session, order_id: int) -> list:
    """Get payment history for an order"""
    payments = db.query(Payment).filter(
        Payment.order_id == order_id
    ).order_by(Payment.attempt).all()

    return payments