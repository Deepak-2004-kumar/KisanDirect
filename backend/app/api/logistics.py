from fastapi import APIRouter, HTTPException
from app.schemas.schemas import LogisticsRequest
from app.ai.logistics_service import get_logistics_plan

router = APIRouter(prefix="/logistics", tags=["Logistics"])


@router.post("/route")
def plan_route_endpoint(payload: LogisticsRequest):
    try:
        return get_logistics_plan(
            payload.farmer_lat, payload.farmer_lon, payload.buyer_lat, payload.buyer_lon,
            payload.quantity_kg, payload.delivery_deadline_hours,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
