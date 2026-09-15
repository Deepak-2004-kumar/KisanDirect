from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import Offer, CropListing, Buyer, UserRole, OfferStatus, ListingStatus
from app.schemas.schemas import OfferCreate
from app.core.deps import require_role
from app.ai.matching_service import score_listing_against_offer

router = APIRouter(prefix="/offers", tags=["Offers"])


def _serialize(offer: Offer) -> dict:
    return {
        "id": offer.id, "listing_id": offer.listing_id, "buyer_id": offer.buyer_id,
        "offered_price_per_kg": float(offer.offered_price_per_kg),
        "requested_quantity_kg": float(offer.requested_quantity_kg),
        "match_score": float(offer.match_score) if offer.match_score is not None else None,
        "match_explanation": offer.match_explanation, "status": offer.status.value,
        "created_at": offer.created_at,
    }


@router.post("", status_code=201)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db),
                  user=Depends(require_role(UserRole.BUYER))):
    buyer = db.query(Buyer).filter(Buyer.user_id == user.id).first()
    if not buyer:
        raise HTTPException(status_code=400, detail="Buyer profile not found for this user")

    listing = db.query(CropListing).filter(CropListing.id == payload.listing_id).first()
    if not listing or listing.status != ListingStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Listing is not available")

    # Compute an explainable AI match score at the moment the offer is made
    match_result = score_listing_against_offer(listing, buyer, payload)

    offer = Offer(
        listing_id=listing.id, buyer_id=buyer.id,
        offered_price_per_kg=payload.offered_price_per_kg,
        requested_quantity_kg=payload.requested_quantity_kg,
        needed_within_days=payload.needed_within_days,
        match_score=match_result["match_score"],
        match_explanation=match_result,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return _serialize(offer)


@router.get("")
def list_offers(listing_id: int = None, db: Session = Depends(get_db)):
    q = db.query(Offer)
    if listing_id:
        q = q.filter(Offer.listing_id == listing_id)
    offers = q.order_by(Offer.match_score.desc().nullslast()).all()
    return [_serialize(o) for o in offers]


@router.post("/{offer_id}/accept")
def accept_offer(offer_id: int, db: Session = Depends(get_db),
                  user=Depends(require_role(UserRole.FARMER))):
    from app.models.models import Order
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.listing.farmer.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    if offer.status != OfferStatus.PENDING:
        raise HTTPException(status_code=400, detail="Offer already resolved")

    offer.status = OfferStatus.ACCEPTED
    offer.listing.status = ListingStatus.RESERVED

    order = Order(
        offer_id=offer.id, listing_id=offer.listing_id, farmer_id=offer.listing.farmer_id,
        buyer_id=offer.buyer_id, final_price_per_kg=offer.offered_price_per_kg,
        final_quantity_kg=offer.requested_quantity_kg,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"message": "Offer accepted, order created", "order_id": order.id}
