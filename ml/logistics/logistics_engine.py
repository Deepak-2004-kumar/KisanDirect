"""
KisanDirect - Logistics Optimization Module
=============================================
MVP scope (per spec section 5):
  - Compute farmer->buyer distance (haversine, straight-line proxy for
    road distance in the prototype).
  - Estimate transportation cost using a simple per-km + per-kg tariff
    model with vehicle-size selection based on quantity.
  - Suggest a vehicle/route type and an estimated delivery time.
  - Document how this scales to true Vehicle Routing Problem (VRP)
    optimization with Google OR-Tools when there are multiple
    farmers/orders to batch into one route (see `plan_multi_stop_route`
    docstring below for the OR-Tools upgrade path).

For real deployments: replace `haversine_km` with an OSRM/OpenRouteService
road-distance API call, and swap `estimate_transport_cost` for real
transporter tariff cards. Both are isolated as pure functions to make
that swap trivial.
"""
from __future__ import annotations
import math
from dataclasses import dataclass

EARTH_RADIUS_KM = 6371.0

# Simple vehicle tariff table for the MVP (INR). Real deployments would
# source this from registered Transporters in the database.
VEHICLE_TIERS = [
    {"name": "Mini Truck (upto 500kg)",  "max_kg": 500,   "base_fare": 150, "per_km": 9,  "avg_speed_kmph": 35},
    {"name": "Tempo (upto 1500kg)",      "max_kg": 1500,  "base_fare": 300, "per_km": 14, "avg_speed_kmph": 30},
    {"name": "Truck (upto 5000kg)",      "max_kg": 5000,  "base_fare": 600, "per_km": 22, "avg_speed_kmph": 28},
    {"name": "Large Truck (5000kg+)",    "max_kg": float("inf"), "base_fare": 1200, "per_km": 35, "avg_speed_kmph": 25},
]


@dataclass
class LogisticsPlan:
    distance_km: float
    suggested_vehicle: str
    estimated_cost: float
    estimated_delivery_hours: float
    estimated_delivery_date_note: str
    scalability_note: str

    def to_dict(self):
        return self.__dict__.copy()


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    straight_line = 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))
    # apply a simple road-network detour factor (real roads aren't straight lines)
    return round(straight_line * 1.25, 2)


def select_vehicle(quantity_kg: float) -> dict:
    for tier in VEHICLE_TIERS:
        if quantity_kg <= tier["max_kg"]:
            return tier
    return VEHICLE_TIERS[-1]


def estimate_transport_cost(distance_km: float, quantity_kg: float) -> tuple[float, dict]:
    vehicle = select_vehicle(quantity_kg)
    cost = vehicle["base_fare"] + vehicle["per_km"] * distance_km
    return round(cost, 2), vehicle


def plan_route(farmer_lat, farmer_lon, buyer_lat, buyer_lon, quantity_kg: float,
                delivery_deadline_hours: float | None = None) -> LogisticsPlan:
    if not (-90 <= farmer_lat <= 90 and -90 <= buyer_lat <= 90):
        raise ValueError("Latitude must be between -90 and 90.")
    if not (-180 <= farmer_lon <= 180 and -180 <= buyer_lon <= 180):
        raise ValueError("Longitude must be between -180 and 180.")
    if quantity_kg <= 0:
        raise ValueError("Quantity must be greater than zero.")
    distance = haversine_km(farmer_lat, farmer_lon, buyer_lat, buyer_lon)
    cost, vehicle = estimate_transport_cost(distance, quantity_kg)
    hours = round(distance / vehicle["avg_speed_kmph"] + 0.5, 1)  # +0.5h loading/unloading buffer

    deadline_note = "within deadline" if (delivery_deadline_hours is None or hours <= delivery_deadline_hours) \
        else "MAY MISS requested delivery deadline — consider a faster vehicle tier or nearer buyer"

    return LogisticsPlan(
        distance_km=distance,
        suggested_vehicle=vehicle["name"],
        estimated_cost=cost,
        estimated_delivery_hours=hours,
        estimated_delivery_date_note=deadline_note,
        scalability_note=(
            "This single-route calculation is the MVP baseline. When multiple farmer "
            "pickups and buyer drop-offs need to be batched into one truck run, this "
            "becomes a Capacitated Vehicle Routing Problem (CVRP) with time windows — "
            "solvable with Google OR-Tools' routing library (see plan_multi_stop_route "
            "docstring in this module for the intended API)."
        ),
    )


def plan_multi_stop_route(stops: list[dict], vehicle_capacity_kg: float):
    """
    PLACEHOLDER / architecture note for the production upgrade path.

    In production, this function would:
      1. Build a distance matrix between all pickup (farmer) and
         drop-off (buyer) points using OSRM/road-network distances.
      2. Model it as a Capacitated VRP with Time Windows (CVRPTW) using
         Google OR-Tools' `pywrapcp` routing solver:
           - Nodes: depot + each farmer pickup + each buyer drop-off
           - Demands: +quantity at pickup, -quantity at drop-off
           - Vehicle capacity constraint: vehicle_capacity_kg
           - Time windows: harvest availability / delivery deadlines
      3. Return an ordered stop sequence per vehicle minimizing total
         distance/cost while respecting capacity and time windows.

    For the MVP/demo, `plan_route` above handles the single farmer ->
    single buyer case, which covers the SIH demo scenario end-to-end.
    """
    raise NotImplementedError(
        "Multi-stop VRP optimization is out of scope for the MVP demo. "
        "See docstring for the Google OR-Tools upgrade path."
    )


if __name__ == "__main__":
    # SIH demo: Farmer (Rohtak) -> Buyer A (~18km) and Buyer B (~100km+)
    plan_a = plan_route(28.8955, 76.6066, 28.98, 76.75, quantity_kg=500, delivery_deadline_hours=6)
    plan_b = plan_route(28.8955, 76.6066, 29.9457, 76.8781, quantity_kg=500, delivery_deadline_hours=6)

    print("=== Logistics Plan: Farmer -> Buyer A ===")
    print(plan_a.to_dict())
    print("\n=== Logistics Plan: Farmer -> Buyer B ===")
    print(plan_b.to_dict())
