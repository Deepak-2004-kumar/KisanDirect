from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.db import get_db
from app.models.models import CropListing, Crop, Farmer, UserRole
from app.schemas.schemas import CropListingCreate, CropListingUpdate, CropListingOut
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/crop-listings", tags=["Crop Listings"])


def _serialize(listing: CropListing) -> dict:
    return {
        "id": listing.id, "farmer_id": listing.farmer_id, "crop": listing.crop.name,
        "quantity_kg": float(listing.quantity_kg), "quality_grade": listing.quality_grade,
        "expected_price_per_kg": float(listing.expected_price_per_kg),
        "harvest_date": listing.harvest_date, "latitude": float(listing.latitude),
        "longitude": float(listing.longitude), "status": listing.status.value,
        "created_at": listing.created_at,
    }


@router.post("", status_code=201)
def create_listing(payload: CropListingCreate, db: Session = Depends(get_db),
                    user=Depends(require_role(UserRole.FARMER))):
    farmer = db.query(Farmer).filter(Farmer.user_id == user.id).first()
    if not farmer:
        raise HTTPException(status_code=400, detail="Farmer profile not found for this user")

    crop = db.query(Crop).filter(Crop.name.ilike(payload.crop)).first()
    if not crop:
        crop = Crop(name=payload.crop)
        db.add(crop)
        db.flush()

    listing = CropListing(
        farmer_id=farmer.id, crop_id=crop.id, quantity_kg=payload.quantity_kg,
        quality_grade=payload.quality_grade, expected_price_per_kg=payload.expected_price_per_kg,
        harvest_date=payload.harvest_date, latitude=payload.latitude, longitude=payload.longitude,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return _serialize(listing)


@router.get("")
def search_listings(
    crop: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None,
    min_quantity: Optional[float] = None, quality_grade: Optional[str] = None,
    location: Optional[str] = None, db: Session = Depends(get_db),
):
    q = db.query(CropListing).join(Crop)
    if crop:
        q = q.filter(Crop.name.ilike(f"%{crop}%"))
    if min_price is not None:
        q = q.filter(CropListing.expected_price_per_kg >= min_price)
    if max_price is not None:
        q = q.filter(CropListing.expected_price_per_kg <= max_price)
    if min_quantity is not None:
        q = q.filter(CropListing.quantity_kg >= min_quantity)
    if quality_grade:
        q = q.filter(CropListing.quality_grade == quality_grade)
    listings = q.all()
    return [_serialize(l) for l in listings]


@router.get("/{listing_id}")
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _serialize(listing)


@router.put("/{listing_id}")
def update_listing(listing_id: int, payload: CropListingUpdate, db: Session = Depends(get_db),
                    user=Depends(require_role(UserRole.FARMER))):
    listing = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.farmer.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return _serialize(listing)


@router.delete("/{listing_id}", status_code=204)
def delete_listing(listing_id: int, db: Session = Depends(get_db),
                    user=Depends(require_role(UserRole.FARMER))):
    listing = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.farmer.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    db.delete(listing)
    db.commit()
    return None
