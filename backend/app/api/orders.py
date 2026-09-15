from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import Order, Payment, PaymentStatus, Delivery
from app.core.deps import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


def _serialize(order: Order) -> dict:
    return {
        "id": order.id, "offer_id": order.offer_id, "listing_id": order.listing_id,
        "farmer_id": order.farmer_id, "buyer_id": order.buyer_id,
        "final_price_per_kg": float(order.final_price_per_kg),
        "final_quantity_kg": float(order.final_quantity_kg),
        "total_value": float(order.final_price_per_kg) * float(order.final_quantity_kg),
        "status": order.status.value, "created_at": order.created_at,
        "payment_status": order.payment.status.value if order.payment else "PENDING",
        "delivery_status": order.delivery.status if order.delivery else "NOT_SCHEDULED",
    }


@router.get("")
def list_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.models.models import Farmer, Buyer
    orders = []
    farmer = db.query(Farmer).filter(Farmer.user_id == user.id).first()
    buyer = db.query(Buyer).filter(Buyer.user_id == user.id).first()
    q = db.query(Order)
    if farmer:
        orders += q.filter(Order.farmer_id == farmer.id).all()
    if buyer:
        orders += q.filter(Order.buyer_id == buyer.id).all()
    if user.role.value == "ADMIN":
        orders = q.all()
    return [_serialize(o) for o in orders]


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize(order)


@router.post("/{order_id}/pay")
def mark_paid(order_id: int, db: Session = Depends(get_db)):
    """Demo payment flow: PENDING -> PAID (per SIH demo scenario step 11)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = order.payment
    if not payment:
        payment = Payment(order_id=order.id, amount=float(order.final_price_per_kg) * float(order.final_quantity_kg))
        db.add(payment)
    payment.status = PaymentStatus.PAID
    from datetime import datetime
    payment.paid_at = datetime.utcnow()
    db.commit()
    return {"message": "Payment marked PAID", "order_id": order.id}
