from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import CropListing, Buyer
from app.schemas.schemas import MatchRequest
from app.ai.matching_service import score_listing_against_offer

router = APIRouter(prefix="/ai", tags=["AI Matching"])


@router.post("/match")
def ai_match(payload: MatchRequest, db: Session = Depends(get_db)):
    listing = db.query(CropListing).filter(CropListing.id == payload.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    buyer = db.query(Buyer).filter(Buyer.id == payload.buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    class _Req:
        pass
    req = _Req()
    req.requested_quantity_kg = payload.required_quantity_kg or listing.quantity_kg
    req.offered_price_per_kg = payload.offered_price_per_kg or listing.expected_price_per_kg
    req.needed_within_days = payload.needed_within_days

    result = score_listing_against_offer(listing, buyer, req)
    return result
