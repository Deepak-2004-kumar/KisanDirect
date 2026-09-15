"""
Seed the database with synthetic demo data from data/synthetic/*.json.
Run this after the backend tables are created:
    python seed.py
"""
import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))

from app.database.db import SessionLocal, Base, engine
from app.models.models import (
    User, Farmer, Buyer, Crop, CropListing, UserRole, ListingStatus,
)
from app.core.security import hash_password

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "synthetic"


def load_json(name):
    with open(DATA_DIR / name) as f:
        return json.load(f)


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already has users — skipping seed. Delete data to reseed.")
            return

        # Admin
        admin = User(full_name="Platform Admin", email="admin@kisandirect.in", phone="9000000000",
                     password_hash=hash_password("admin123"), role=UserRole.ADMIN)
        db.add(admin)

        # Crops
        crops_data = load_json("crops.json")
        crop_objs = {}
        for c in crops_data:
            crop = Crop(name=c["name"], unit=c["unit"])
            db.add(crop)
            db.flush()
            crop_objs[c["name"]] = crop

        # Farmers
        farmers_data = load_json("farmers.json")
        farmer_objs = {}
        for f in farmers_data:
            user = User(
                full_name=f["name"], email=f"farmer{f['id']}@kisandirect.in", phone=f["phone"],
                password_hash=hash_password("farmer123"), role=UserRole.FARMER,
                preferred_language=f["preferred_language"],
            )
            db.add(user)
            db.flush()
            farmer = Farmer(
                user_id=user.id, village=f["village"], land_size_acres=f["land_size_acres"],
                latitude=f["latitude"], longitude=f["longitude"], reliability_score=f["reliability_score"],
            )
            db.add(farmer)
            db.flush()
            farmer_objs[f["id"]] = farmer

        # Buyers
        buyers_data = load_json("buyers.json")
        buyer_objs = {}
        for b in buyers_data:
            user = User(
                full_name=b["business_name"], email=f"buyer{b['id']}@kisandirect.in", phone=b["phone"],
                password_hash=hash_password("buyer123"), role=UserRole.BUYER,
            )
            db.add(user)
            db.flush()
            buyer = Buyer(
                user_id=user.id, business_name=b["business_name"], buyer_type=b["buyer_type"],
                latitude=b["latitude"], longitude=b["longitude"],
                avg_monthly_volume_kg=b["avg_monthly_volume_kg"],
            )
            db.add(buyer)
            db.flush()
            buyer_objs[b["id"]] = buyer

        # Crop listings
        listings_data = load_json("crop_listings.json")
        for l in listings_data:
            listing = CropListing(
                farmer_id=farmer_objs[l["farmer_id"]].id,
                crop_id=crop_objs[l["crop"]].id,
                quantity_kg=l["quantity_kg"], quality_grade=l["quality_grade"],
                expected_price_per_kg=l["expected_price_per_kg"],
                harvest_date=date.fromisoformat(l["harvest_date"]),
                latitude=l["latitude"], longitude=l["longitude"],
                status=ListingStatus.ACTIVE,
            )
            db.add(listing)

        db.commit()
        print(f"Seeded: 1 admin, {len(farmers_data)} farmers, {len(buyers_data)} buyers, "
              f"{len(listings_data)} crop listings.")
        print("Demo logins: admin@kisandirect.in / admin123, farmer1@kisandirect.in / farmer123, "
              "buyer1@kisandirect.in / buyer123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
