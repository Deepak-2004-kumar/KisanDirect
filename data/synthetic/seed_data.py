"""
KisanDirect - Synthetic Seed Data Generator
=============================================
Generates realistic (but SYNTHETIC / DEMO) data for:
  - Farmers, Buyers
  - Crop master list
  - Crop Listings
  - Historical price series (for price intelligence baseline model)
  - Historical orders (for demand forecasting baseline model)

IMPORTANT: All data here is synthetic and clearly labeled as such.
It is NOT sourced from any real government or market database.
Run this script to (re)generate the JSON/CSV fixtures used by the
backend seed script and by the ML notebooks/tests.
"""
import json
import random
import csv
import math
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # reproducible demo data

OUT_DIR = Path(__file__).parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Locations (lat/lon) -- a handful of real town coordinates used only as
#    map reference points for the MVP demo (public, non-sensitive geodata).
# ---------------------------------------------------------------------------
LOCATIONS = {
    "Rohtak":     (28.8955, 76.6066),
    "Delhi":      (28.7041, 77.1025),
    "Sonipat":    (28.9931, 77.0151),
    "Karnal":     (29.6857, 76.9905),
    "Panipat":    (29.3909, 76.9635),
    "Gurugram":   (28.4595, 77.0266),
    "Hisar":      (29.1492, 75.7217),
    "Ludhiana":   (30.9010, 75.8573),
    "Chandigarh": (30.7333, 76.7794),
    "Ambala":     (30.3782, 76.7767),
}

CROPS = [
    {"name": "Tomato",  "unit": "kg", "base_price": 22, "volatility": 0.35, "seasonal_peak_month": 9},
    {"name": "Wheat",   "unit": "kg", "base_price": 24, "volatility": 0.08, "seasonal_peak_month": 4},
    {"name": "Potato",  "unit": "kg", "base_price": 14, "volatility": 0.20, "seasonal_peak_month": 2},
    {"name": "Onion",   "unit": "kg", "base_price": 18, "volatility": 0.40, "seasonal_peak_month": 11},
    {"name": "Mustard", "unit": "kg", "base_price": 55, "volatility": 0.12, "seasonal_peak_month": 3},
]

QUALITY_GRADES = ["Grade A", "Grade B", "Grade C"]

BUYER_TYPES = ["Local Retailer", "Restaurant", "Food Processor", "Institutional Buyer", "FPO Aggregator"]

FARMER_NAMES = [
    "Ramesh Kumar", "Suresh Yadav", "Anita Devi", "Rajinder Singh", "Meena Kumari",
    "Sanjay Chauhan", "Pooja Rani", "Vikram Malik", "Sunita Sharma", "Deepak Verma",
    "Kavita Yadav", "Harpreet Singh", "Manoj Kumar", "Geeta Devi", "Ashok Kumar",
]

BUYER_NAMES = [
    "FreshMart Retail", "Spice Route Restaurant", "AgroProcess Foods Pvt Ltd",
    "Green Valley Hostel Mess", "Farmers FPO Collective", "City Fresh Grocers",
    "Punjab Grand Restaurant", "National Food Processing Co", "Sunrise Institutional Caterers",
    "Metro Retail Chain",
]


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# 2. Farmers
# ---------------------------------------------------------------------------
farmers = []
for i, name in enumerate(FARMER_NAMES, start=1):
    loc = random.choice(list(LOCATIONS.keys()))
    lat, lon = LOCATIONS[loc]
    lat += random.uniform(-0.05, 0.05)
    lon += random.uniform(-0.05, 0.05)
    farmers.append({
        "id": i,
        "user_id": i,
        "name": name,
        "phone": f"9{random.randint(100000000, 999999999)}",
        "village": loc,
        "location": loc,
        "latitude": round(lat, 5),
        "longitude": round(lon, 5),
        "land_size_acres": round(random.uniform(0.5, 8.0), 1),
        "reliability_score": round(random.uniform(0.6, 1.0), 2),  # synthetic history-based score
        "preferred_language": random.choice(["en", "hi"]),
    })

# ---------------------------------------------------------------------------
# 3. Buyers
# ---------------------------------------------------------------------------
buyers = []
for i, name in enumerate(BUYER_NAMES, start=1):
    loc = random.choice(list(LOCATIONS.keys()))
    lat, lon = LOCATIONS[loc]
    lat += random.uniform(-0.05, 0.05)
    lon += random.uniform(-0.05, 0.05)
    buyers.append({
        "id": i,
        "user_id": 100 + i,
        "business_name": name,
        "buyer_type": BUYER_TYPES[i % len(BUYER_TYPES)],
        "phone": f"8{random.randint(100000000, 999999999)}",
        "location": loc,
        "latitude": round(lat, 5),
        "longitude": round(lon, 5),
        "avg_monthly_volume_kg": random.choice([200, 500, 1000, 2000, 5000]),
    })

# ---------------------------------------------------------------------------
# 4. Crop listings (current, active) -- used for the live marketplace demo
# ---------------------------------------------------------------------------
crop_listings = []
listing_id = 1
today = date(2026, 9, 13)
for farmer in farmers:
    num_listings = random.randint(1, 2)
    for _ in range(num_listings):
        crop = random.choice(CROPS)
        harvest_date = today + timedelta(days=random.randint(-3, 20))
        crop_listings.append({
            "id": listing_id,
            "farmer_id": farmer["id"],
            "crop": crop["name"],
            "quantity_kg": random.choice([100, 200, 300, 500, 750, 1000]),
            "quality_grade": random.choice(QUALITY_GRADES),
            "expected_price_per_kg": round(crop["base_price"] * random.uniform(0.9, 1.15), 2),
            "harvest_date": harvest_date.isoformat(),
            "location": farmer["location"],
            "latitude": farmer["latitude"],
            "longitude": farmer["longitude"],
            "status": "ACTIVE",
            "created_at": (today - timedelta(days=random.randint(0, 10))).isoformat(),
        })
        listing_id += 1

# Force-create the exact SIH demo scenario listing (Step 2 of the script)
DEMO_FARMER_ID = farmers[0]["id"]
farmers[0].update({"name": "Ramesh Kumar", "village": "Rohtak", "location": "Rohtak",
                    "latitude": LOCATIONS["Rohtak"][0], "longitude": LOCATIONS["Rohtak"][1]})
demo_listing = {
    "id": listing_id,
    "farmer_id": DEMO_FARMER_ID,
    "crop": "Tomato",
    "quantity_kg": 500,
    "quality_grade": "Grade A",
    "expected_price_per_kg": 25,
    "harvest_date": "2026-09-15",
    "location": "Rohtak",
    "latitude": LOCATIONS["Rohtak"][0],
    "longitude": LOCATIONS["Rohtak"][1],
    "status": "ACTIVE",
    "created_at": today.isoformat(),
    "is_demo_scenario": True,
}
crop_listings.append(demo_listing)

# ---------------------------------------------------------------------------
# 5. Historical prices (for price intelligence baseline model)
#    ~365 days per crop, synthetic seasonal + noise pattern
# ---------------------------------------------------------------------------
price_history = []
start = today - timedelta(days=365)
for crop in CROPS:
    for d in range(365):
        day = start + timedelta(days=d)
        # seasonal factor: peak near seasonal_peak_month
        month_diff = min(abs(day.month - crop["seasonal_peak_month"]), 12 - abs(day.month - crop["seasonal_peak_month"]))
        seasonal = 1 + (0.25 * (1 - month_diff / 6))
        trend = 1 + 0.02 * math.sin(d / 40)
        noise = random.uniform(1 - crop["volatility"] * 0.3, 1 + crop["volatility"] * 0.3)
        price = round(crop["base_price"] * seasonal * trend * noise, 2)
        price_history.append({
            "crop": crop["name"],
            "date": day.isoformat(),
            "price_per_kg": price,
            "market": random.choice(list(LOCATIONS.keys())),
        })

# ---------------------------------------------------------------------------
# 6. Historical orders (for demand forecasting baseline model)
# ---------------------------------------------------------------------------
orders_history = []
order_id = 1
for crop in CROPS:
    for d in range(180):
        day = start + timedelta(days=d + 185)
        # simulate 0-4 orders per day per crop with weekday & seasonal effect
        month_diff = min(abs(day.month - crop["seasonal_peak_month"]), 12 - abs(day.month - crop["seasonal_peak_month"]))
        seasonal_demand = 1 + (0.5 * (1 - month_diff / 6))
        weekday_boost = 1.3 if day.weekday() in (4, 5) else 1.0  # Fri/Sat busier
        expected_orders = max(0, round(random.gauss(2 * seasonal_demand * weekday_boost, 1)))
        for _ in range(expected_orders):
            region = random.choice(list(LOCATIONS.keys()))
            qty = random.choice([50, 100, 150, 200, 300])
            orders_history.append({
                "id": order_id,
                "crop": crop["name"],
                "date": day.isoformat(),
                "region": region,
                "quantity_kg": qty,
            })
            order_id += 1

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
with open(OUT_DIR / "farmers.json", "w") as f:
    json.dump(farmers, f, indent=2)
with open(OUT_DIR / "buyers.json", "w") as f:
    json.dump(buyers, f, indent=2)
with open(OUT_DIR / "crops.json", "w") as f:
    json.dump(CROPS, f, indent=2)
with open(OUT_DIR / "crop_listings.json", "w") as f:
    json.dump(crop_listings, f, indent=2)

with open(OUT_DIR / "price_history.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["crop", "date", "price_per_kg", "market"])
    writer.writeheader()
    writer.writerows(price_history)

with open(OUT_DIR / "orders_history.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "crop", "date", "region", "quantity_kg"])
    writer.writeheader()
    writer.writerows(orders_history)

with open(OUT_DIR / "locations.json", "w") as f:
    json.dump({k: {"lat": v[0], "lon": v[1]} for k, v in LOCATIONS.items()}, f, indent=2)

print(f"Generated {len(farmers)} farmers, {len(buyers)} buyers, {len(crop_listings)} listings, "
      f"{len(price_history)} price rows, {len(orders_history)} order rows.")
print("NOTE: All generated data is SYNTHETIC/DEMO data for the SIH prototype only.")
