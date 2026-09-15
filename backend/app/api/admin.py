from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.db import get_db
from app.models.models import Farmer, Buyer, CropListing, Order, ListingStatus, OrderStatus, UserRole
from app.core.deps import require_role

router = APIRouter(prefix="/admin", tags=["Admin Analytics"])


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), user=Depends(require_role(UserRole.ADMIN))):
    total_farmers = db.query(func.count(Farmer.id)).scalar() or 0
    total_buyers = db.query(func.count(Buyer.id)).scalar() or 0
    active_listings = db.query(func.count(CropListing.id)).filter(
        CropListing.status == ListingStatus.ACTIVE).scalar() or 0
    active_orders = db.query(func.count(Order.id)).filter(
        Order.status.in_([OrderStatus.CREATED, OrderStatus.CONFIRMED, OrderStatus.IN_TRANSIT])
    ).scalar() or 0

    orders = db.query(Order).all()
    total_value = sum(float(o.final_price_per_kg) * float(o.final_quantity_kg) for o in orders)
    avg_farmer_price = (
        sum(float(o.final_price_per_kg) for o in orders) / len(orders) if orders else 0.0
    )

    return {
        "total_farmers": total_farmers,
        "total_buyers": total_buyers,
        "active_listings": active_listings,
        "active_orders": active_orders,
        "total_transaction_value": round(total_value, 2),
        "average_farmer_price": round(avg_farmer_price, 2),
        "estimated_intermediary_layers_reduced": "Estimated/Synthetic — not a verified real-world measurement",
        "note": "All figures reflect this prototype's demo data only.",
    }
