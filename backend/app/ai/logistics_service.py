"""Wraps ml/logistics/logistics_engine.py for use inside the FastAPI backend."""
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[3] / "ml"
sys.path.insert(0, str(ML_ROOT / "logistics"))

from logistics_engine import plan_route  # noqa: E402


def get_logistics_plan(farmer_lat, farmer_lon, buyer_lat, buyer_lon, quantity_kg, delivery_deadline_hours=None) -> dict:
    plan = plan_route(farmer_lat, farmer_lon, buyer_lat, buyer_lon, quantity_kg, delivery_deadline_hours)
    return plan.to_dict()
