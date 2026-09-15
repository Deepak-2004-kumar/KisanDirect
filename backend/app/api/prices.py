from fastapi import APIRouter, HTTPException, Query
from app.ai.price_service import get_price_report

router = APIRouter(prefix="/prices", tags=["Price Intelligence"])


@router.get("")
def get_prices(crop: str = Query(...)):
    try:
        return get_price_report(crop)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trends")
def get_price_trends(crop: str = Query(...)):
    try:
        report = get_price_report(crop)
        return {"crop": report["crop"], "trend_direction": report["trend_direction"],
                "trend_pct_30d": report["trend_pct_30d"], "forecast_7d": report["forecast_7d"],
                "is_synthetic": report["is_synthetic"], "disclaimer": report["disclaimer"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
