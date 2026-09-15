"""SQLAlchemy ORM models mirroring backend/app/database/schema.sql"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Date, DateTime, ForeignKey,
    Enum as SAEnum, Text, SmallInteger, JSON
)
from sqlalchemy.orm import relationship
from app.database.db import Base


class UserRole(str, enum.Enum):
    FARMER = "FARMER"
    BUYER = "BUYER"
    ADMIN = "ADMIN"


class ListingStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class OfferStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    preferred_language = Column(String(5), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="user", uselist=False)
    buyer = relationship("Buyer", back_populates="user", uselist=False)


class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    village = Column(String(150))
    district = Column(String(150))
    state = Column(String(150))
    land_size_acres = Column(Numeric(6, 2))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    reliability_score = Column(Numeric(4, 3), default=0.80)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="farmer")
    listings = relationship("CropListing", back_populates="farmer")


class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(200), nullable=False)
    buyer_type = Column(String(50), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    avg_monthly_volume_kg = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="buyer")
    offers = relationship("Offer", back_populates="buyer")


class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    unit = Column(String(20), default="kg")
    category = Column(String(50))


class CropListing(Base):
    __tablename__ = "crop_listings"
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    quantity_kg = Column(Numeric(10, 2), nullable=False)
    quality_grade = Column(String(20), nullable=False)
    expected_price_per_kg = Column(Numeric(8, 2), nullable=False)
    harvest_date = Column(Date, nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    status = Column(SAEnum(ListingStatus), default=ListingStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="listings")
    crop = relationship("Crop")
    offers = relationship("Offer", back_populates="listing")


class Offer(Base):
    __tablename__ = "offers"
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("crop_listings.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    offered_price_per_kg = Column(Numeric(8, 2), nullable=False)
    requested_quantity_kg = Column(Numeric(10, 2), nullable=False)
    needed_within_days = Column(Integer, default=7)
    match_score = Column(Numeric(5, 2))
    match_explanation = Column(JSON)
    status = Column(SAEnum(OfferStatus), default=OfferStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listing = relationship("CropListing", back_populates="offers")
    buyer = relationship("Buyer", back_populates="offers")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), unique=True, nullable=False)
    listing_id = Column(Integer, ForeignKey("crop_listings.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    final_price_per_kg = Column(Numeric(8, 2), nullable=False)
    final_quantity_kg = Column(Numeric(10, 2), nullable=False)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.CREATED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    delivery = relationship("Delivery", back_populates="order", uselist=False)
    payment = relationship("Payment", back_populates="order", uselist=False)


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    transporter_id = Column(Integer, ForeignKey("transporters.id"))
    distance_km = Column(Numeric(8, 2))
    estimated_cost = Column(Numeric(10, 2))
    estimated_delivery_hours = Column(Numeric(6, 2))
    status = Column(String(20), default="SCHEDULED")
    scheduled_at = Column(DateTime)
    delivered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="delivery")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(50))
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payment")


class Transporter(Base):
    __tablename__ = "transporters"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20))
    vehicle_type = Column(String(100))
    capacity_kg = Column(Numeric(10, 2))
    base_fare = Column(Numeric(8, 2))
    per_km_rate = Column(Numeric(8, 2))
    is_active = Column(Boolean, default=True)


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    capacity_kg = Column(Numeric(12, 2))
    operator_name = Column(String(150))


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    reviewer_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(SmallInteger)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
