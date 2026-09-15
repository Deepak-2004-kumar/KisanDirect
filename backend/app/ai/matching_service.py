"""Wraps ml/matching/matching_engine.py for use inside the FastAPI backend."""
import sys
from pathlib import Path

# ml/ lives at the project root, sibling to backend/
ML_ROOT = Path(__file__).resolve().parents[3] / "ml"
sys.path.insert(0, str(ML_ROOT / "matching"))

from matching_engine import ListingInput, BuyerRequirementInput, compute_match  # noqa: E402


def score_listing_against_offer(listing_row, buyer_row, offer_req) -> dict:
    """
    listing_row: CropListing ORM object (with .crop.name)
    buyer_row: Buyer ORM object
    offer_req: OfferCreate schema (or similar) with offered_price_per_kg etc.
    """
    listing_input = ListingInput(
        crop=listing_row.crop.name,
        quantity_kg=float(listing_row.quantity_kg),
        quality_grade=listing_row.quality_grade,
        expected_price_per_kg=float(listing_row.expected_price_per_kg),
        latitude=float(listing_row.latitude),
        longitude=float(listing_row.longitude),
        harvest_date_days_from_now=0,
        farmer_reliability_score=float(listing_row.farmer.reliability_score or 0.8),
    )
    buyer_input = BuyerRequirementInput(
        crop=listing_row.crop.name,
        required_quantity_kg=float(offer_req.requested_quantity_kg),
        min_quality_grade=listing_row.quality_grade,
        offered_price_per_kg=float(offer_req.offered_price_per_kg),
        latitude=float(buyer_row.latitude),
        longitude=float(buyer_row.longitude),
        needed_within_days=offer_req.needed_within_days,
    )
    result = compute_match(listing_input, buyer_input)
    return result.to_dict()
