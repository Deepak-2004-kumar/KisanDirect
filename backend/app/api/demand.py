from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.ai.demand_service import get_demand_forecast

router = APIRouter(prefix="/demand", tags=["Demand Forecasting"])


@router.get("/forecast")
def demand_forecast(crop: str = Query(...), region: Optional[str] = None):
    try:
        return get_demand_forecast(crop, region)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
