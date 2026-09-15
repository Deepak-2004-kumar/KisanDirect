from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import Farmer

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.get("")
def list_farmers(db: Session = Depends(get_db)):
    farmers = db.query(Farmer).all()
    return [
        {
            "id": f.id, "user_id": f.user_id, "village": f.village,
            "district": f.district, "land_size_acres": float(f.land_size_acres or 0),
            "latitude": float(f.latitude or 0), "longitude": float(f.longitude or 0),
            "reliability_score": float(f.reliability_score or 0),
        }
        for f in farmers
    ]


@router.get("/{farmer_id}")
def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    f = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return {
        "id": f.id, "user_id": f.user_id, "village": f.village,
        "district": f.district, "land_size_acres": float(f.land_size_acres or 0),
        "latitude": float(f.latitude or 0), "longitude": float(f.longitude or 0),
        "reliability_score": float(f.reliability_score or 0),
    }
