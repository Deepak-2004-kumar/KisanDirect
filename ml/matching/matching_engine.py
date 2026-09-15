"""
KisanDirect - AI Matching Engine
=================================
Produces an EXPLAINABLE 0-100 match score between a crop listing (farmer)
and a buyer requirement / offer.

Design principles (per product spec):
  - Never simply pick the highest price.
  - Every score must come with human-readable reasons.
  - Weights are transparent and tunable (config below), not a black box.
  - This is a deterministic, auditable baseline. It is intentionally NOT a
    deep-learning model: for a two-sided marketplace with few features and
    a hard requirement for explainability, a transparent weighted-feature
    scorer is the right first model. It can later be replaced/augmented by
    a learned ranking model (e.g. LightGBM LambdaRank) trained on accepted
    vs rejected offers, using these same features.

Score = sum of sub-scores (each 0-100), combined with configurable weights.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Tunable weights - must sum to 1.0. Kept as named constants (not buried
# magic numbers) so the scoring is auditable and adjustable by a domain
# expert without touching the scoring math.
# ---------------------------------------------------------------------------
WEIGHTS = {
    "crop_compatibility": 0.20,
    "quantity_compatibility": 0.15,
    "quality_compatibility": 0.10,
    "price_compatibility": 0.20,
    "distance_logistics": 0.20,
    "delivery_compatibility": 0.05,
    "reliability": 0.10,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6

QUALITY_RANK = {"Grade A": 3, "Grade B": 2, "Grade C": 1}

# Approximate per-km transport cost for a small/medium load (INR/km), used
# only to translate distance into an effective-price penalty. Configurable.
TRANSPORT_COST_PER_KM = 8.0
# km beyond which logistics score decays sharply (soft threshold)
DISTANCE_COMFORT_KM = 50.0
MAX_REASONABLE_DISTANCE_KM = 300.0


@dataclass
class ListingInput:
    crop: str
    quantity_kg: float
    quality_grade: str
    expected_price_per_kg: float
    latitude: float
    longitude: float
    harvest_date_days_from_now: int = 0
    farmer_reliability_score: float = 0.8  # 0-1, synthetic historical score


@dataclass
class BuyerRequirementInput:
    crop: str
    required_quantity_kg: float
    min_quality_grade: str
    offered_price_per_kg: float
    latitude: float
    longitude: float
    needed_within_days: int = 7


@dataclass
class MatchResult:
    match_score: float
    sub_scores: dict
    distance_km: float
    estimated_transport_cost: float
    effective_price_per_kg: float
    reasons: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def to_dict(self):
        return {
            "match_score": round(self.match_score, 1),
            "sub_scores": {k: round(v, 1) for k, v in self.sub_scores.items()},
            "distance_km": round(self.distance_km, 1),
            "estimated_transport_cost": round(self.estimated_transport_cost, 2),
            "effective_price_per_kg": round(self.effective_price_per_kg, 2),
            "summary": self.summary(),
            "reasons": self.reasons,
            "warnings": self.warnings,
        }

    def summary(self) -> str:
        top_reason = self.reasons[0] if self.reasons else ""
        return f"{round(self.match_score)}% Match — {top_reason}"


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _crop_compatibility(listing: ListingInput, req: BuyerRequirementInput) -> tuple[float, str]:
    if listing.crop.strip().lower() == req.crop.strip().lower():
        return 100.0, f"Same crop ({listing.crop})"
    return 0.0, "Different crop — not a valid match"


def _quantity_compatibility(listing: ListingInput, req: BuyerRequirementInput) -> tuple[float, str]:
    if req.required_quantity_kg <= 0:
        return 100.0, "No specific quantity requirement"
    ratio = listing.quantity_kg / req.required_quantity_kg
    if ratio >= 1.0:
        # Fully satisfies; small penalty for very large surplus (may need multiple buyers)
        surplus_penalty = min(15.0, max(0.0, (ratio - 1.0) * 5))
        score = max(70.0, 100.0 - surplus_penalty)
        reason = "quantity fully satisfied" if ratio < 1.5 else "quantity more than sufficient (surplus available)"
    else:
        # Partial fulfilment scaled down
        score = max(0.0, ratio * 90.0)
        reason = f"only {round(ratio * 100)}% of required quantity available"
    return score, reason


def _quality_compatibility(listing: ListingInput, req: BuyerRequirementInput) -> tuple[float, str]:
    listing_rank = QUALITY_RANK.get(listing.quality_grade, 1)
    min_rank = QUALITY_RANK.get(req.min_quality_grade, 1)
    if listing_rank >= min_rank:
        score = 100.0 if listing_rank == min_rank else 100.0  # meeting/exceeding grade is fully fine
        reason = f"meets required quality ({listing.quality_grade})"
    else:
        diff = min_rank - listing_rank
        score = max(0.0, 100.0 - diff * 40.0)
        reason = f"below required quality grade ({listing.quality_grade} vs {req.min_quality_grade} needed)"
    return score, reason


def _price_compatibility(listing: ListingInput, req: BuyerRequirementInput) -> tuple[float, str]:
    """
    Reward offers that are at/above the farmer's expected price (good for farmer)
    while still being reasonable for the buyer (not wildly above market).
    Score peaks when offered_price is between expected_price and expected_price*1.15.
    """
    expected = listing.expected_price_per_kg
    offered = req.offered_price_per_kg
    if expected <= 0:
        return 50.0, "expected price not specified"
    ratio = offered / expected
    if ratio < 0.85:
        score = max(0.0, ratio * 70.0)
        reason = f"offer (₹{offered}) is below farmer's expected price (₹{expected})"
    elif ratio <= 1.15:
        score = 100.0
        reason = f"offer (₹{offered}) matches farmer's expected price (₹{expected})"
    else:
        # Very high offers aren't penalized much (good for farmer) but flagged for buyer sanity
        score = 95.0
        reason = f"offer (₹{offered}) is above expected price — favorable for farmer"
    return score, reason


def _distance_logistics(listing: ListingInput, req: BuyerRequirementInput) -> tuple[float, str, float, float]:
    dist = haversine_km(listing.latitude, listing.longitude, req.latitude, req.longitude)
    transport_cost = round(dist * TRANSPORT_COST_PER_KM, 2)
    if dist <= DISTANCE_COMFORT_KM:
        score = 100.0 - (dist / DISTANCE_COMFORT_KM) * 20.0  # 100 -> 80 within comfort zone
    else:
        # Decays further beyond comfort zone, floors near 0 past MAX_REASONABLE_DISTANCE_KM
        excess = dist - DISTANCE_COMFORT_KM
        span = MAX_REASONABLE_DISTANCE_KM - DISTANCE_COMFORT_KM
        score = max(0.0, 80.0 - (excess / span) * 80.0)
    reason = f"{round(dist)} km distance (~₹{transport_cost} est. transport)"
    return score, reason, dist, transport_cost


def _delivery_compatibility(listing: ListingInput, req: BuyerRequirementInput) -> tuple[float, str]:
    if listing.harvest_date_days_from_now <= req.needed_within_days:
        score = 100.0
        reason = "harvest/availability fits delivery window"
    else:
        late_days = listing.harvest_date_days_from_now - req.needed_within_days
        score = max(0.0, 100.0 - late_days * 10.0)
        reason = f"produce ready {late_days} day(s) after buyer's needed date"
    return score, reason


def _reliability(listing: ListingInput) -> tuple[float, str]:
    score = listing.farmer_reliability_score * 100.0
    reason = f"farmer reliability score {round(score)}/100 (based on past fulfilled orders)"
    return score, reason


def compute_match(listing: ListingInput, req: BuyerRequirementInput) -> MatchResult:
    warnings = []

    crop_score, crop_reason = _crop_compatibility(listing, req)
    qty_score, qty_reason = _quantity_compatibility(listing, req)
    quality_score, quality_reason = _quality_compatibility(listing, req)
    price_score, price_reason = _price_compatibility(listing, req)
    dist_score, dist_reason, dist_km, transport_cost = _distance_logistics(listing, req)
    delivery_score, delivery_reason = _delivery_compatibility(listing, req)
    reliability_score, reliability_reason = _reliability(listing)

    sub_scores = {
        "crop_compatibility": crop_score,
        "quantity_compatibility": qty_score,
        "quality_compatibility": quality_score,
        "price_compatibility": price_score,
        "distance_logistics": dist_score,
        "delivery_compatibility": delivery_score,
        "reliability": reliability_score,
    }

    if crop_score == 0.0:
        warnings.append("Crop mismatch — this pairing should not be recommended.")
        final_score = 0.0
    else:
        final_score = sum(sub_scores[k] * WEIGHTS[k] for k in WEIGHTS)

    effective_price = req.offered_price_per_kg - (transport_cost / max(listing.quantity_kg, 1))

    # Build ranked, human-readable reasons (most impactful sub-scores first)
    reason_pool = [
        (crop_score, crop_reason),
        (qty_score, qty_reason),
        (quality_score, quality_reason),
        (price_score, price_reason),
        (dist_score, dist_reason),
        (delivery_score, delivery_reason),
        (reliability_score, reliability_reason),
    ]
    reasons = [r for _, r in sorted(reason_pool, key=lambda x: -x[0])]

    if dist_km > MAX_REASONABLE_DISTANCE_KM:
        warnings.append("Distance is very large — verify transport feasibility before accepting.")
    if price_score < 40:
        warnings.append("Offer price is notably below the farmer's expectation.")

    return MatchResult(
        match_score=final_score,
        sub_scores=sub_scores,
        distance_km=dist_km,
        estimated_transport_cost=transport_cost,
        effective_price_per_kg=effective_price,
        reasons=reasons,
        warnings=warnings,
    )


def rank_buyers_for_listing(listing: ListingInput, requirements: list[BuyerRequirementInput]) -> list[dict]:
    """Rank multiple buyer offers/requirements against a single farmer listing."""
    results = []
    for req in requirements:
        m = compute_match(listing, req)
        results.append(m.to_dict())
    return sorted(results, key=lambda r: -r["match_score"])


if __name__ == "__main__":
    # ---- SIH demo scenario: Farmer A (Rohtak, Tomato) vs Buyer A & Buyer B ----
    farmer_listing = ListingInput(
        crop="Tomato",
        quantity_kg=500,
        quality_grade="Grade A",
        expected_price_per_kg=25,
        latitude=28.8955,
        longitude=76.6066,
        harvest_date_days_from_now=2,
        farmer_reliability_score=0.92,
    )

    buyer_a = BuyerRequirementInput(
        crop="Tomato", required_quantity_kg=500, min_quality_grade="Grade A",
        offered_price_per_kg=26, latitude=28.98, longitude=76.75,  # ~18km away (Sonipat-ish)
        needed_within_days=3,
    )
    buyer_b = BuyerRequirementInput(
        crop="Tomato", required_quantity_kg=500, min_quality_grade="Grade A",
        offered_price_per_kg=29, latitude=29.9457, longitude=76.8781,  # far, ~100km+
        needed_within_days=3,
    )

    print("=== KisanDirect AI Matching Engine — Demo ===\n")
    for name, buyer in [("Buyer A", buyer_a), ("Buyer B", buyer_b)]:
        result = compute_match(farmer_listing, buyer)
        print(f"{name}: {result.summary()}")
        print(f"  Distance: {round(result.distance_km)} km | Est. transport: Rs.{result.estimated_transport_cost}")
        print(f"  Sub-scores: {result.to_dict()['sub_scores']}")
        print(f"  Reasons: {result.reasons}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
        print()
