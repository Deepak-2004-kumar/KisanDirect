"""Pydantic request/response schemas."""
from datetime import date, datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str = Field(min_length=6)
    role: str  # FARMER | BUYER
    preferred_language: str = "en"
    # Farmer-only fields
    village: Optional[str] = None
    land_size_acres: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Buyer-only fields
    business_name: Optional[str] = None
    buyer_type: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    full_name: str


# ---------- Crop Listings ----------
class CropListingCreate(BaseModel):
    crop: str
    quantity_kg: float = Field(gt=0)
    quality_grade: str
    expected_price_per_kg: float = Field(gt=0)
    harvest_date: date
    latitude: float
    longitude: float


class CropListingUpdate(BaseModel):
    quantity_kg: Optional[float] = None
    expected_price_per_kg: Optional[float] = None
    status: Optional[str] = None


class CropListingOut(BaseModel):
    id: int
    farmer_id: int
    crop: str
    quantity_kg: float
    quality_grade: str
    expected_price_per_kg: float
    harvest_date: date
    latitude: float
    longitude: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Offers ----------
class OfferCreate(BaseModel):
    listing_id: int
    offered_price_per_kg: float = Field(gt=0)
    requested_quantity_kg: float = Field(gt=0)
    needed_within_days: int = 7


class OfferOut(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    offered_price_per_kg: float
    requested_quantity_kg: float
    match_score: Optional[float] = None
    match_explanation: Optional[Any] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Orders ----------
class OrderOut(BaseModel):
    id: int
    offer_id: int
    listing_id: int
    farmer_id: int
    buyer_id: int
    final_price_per_kg: float
    final_quantity_kg: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- AI Matching ----------
class MatchRequest(BaseModel):
    listing_id: int
    buyer_id: int
    required_quantity_kg: Optional[float] = None
    min_quality_grade: Optional[str] = None
    offered_price_per_kg: Optional[float] = None
    needed_within_days: int = 7


class MatchResponse(BaseModel):
    match_score: float
    sub_scores: dict
    distance_km: float
    estimated_transport_cost: float
    effective_price_per_kg: float
    summary: str
    reasons: List[str]
    warnings: List[str]


# ---------- Logistics ----------
class LogisticsRequest(BaseModel):
    farmer_lat: float = Field(ge=-90, le=90)
    farmer_lon: float = Field(ge=-180, le=180)
    buyer_lat: float = Field(ge=-90, le=90)
    buyer_lon: float = Field(ge=-180, le=180)
    quantity_kg: float = Field(gt=0, le=50000)
    delivery_deadline_hours: Optional[float] = Field(default=None, gt=0, le=720)


class LogisticsResponse(BaseModel):
    distance_km: float
    suggested_vehicle: str
    estimated_cost: float
    estimated_delivery_hours: float
    estimated_delivery_date_note: str
    scalability_note: str


# ---------- Price Intelligence ----------
class PriceReportResponse(BaseModel):
    crop: str
    current_price: float
    min_price: float
    max_price: float
    avg_price: float
    trend_direction: str
    trend_pct_30d: float
    forecast_7d: List[dict]
    is_synthetic: bool
    disclaimer: str


# ---------- Demand Forecast ----------
class DemandForecastResponse(BaseModel):
    crop: str
    region: Optional[str]
    demand_level: str
    expected_daily_quantity_kg: float
    trend_7d: List[dict]
    trend_30d_avg_kg: float
    is_synthetic: bool
    disclaimer: str


# ---------- Admin Analytics ----------
class AdminAnalyticsResponse(BaseModel):
    total_farmers: int
    total_buyers: int
    active_listings: int
    active_orders: int
    total_transaction_value: float
    average_farmer_price: float
    estimated_intermediary_layers_reduced: str
    note: str = "Figures marked Estimated/Synthetic are prototype metrics, not verified real-world savings."
