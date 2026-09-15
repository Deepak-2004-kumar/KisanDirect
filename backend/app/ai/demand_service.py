"""Wraps ml/demand_forecasting/demand_model.py for use inside the FastAPI backend."""
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[3] / "ml"
sys.path.insert(0, str(ML_ROOT / "demand_forecasting"))

from demand_model import DemandForecaster  # noqa: E402

_forecaster = None


def get_forecaster() -> DemandForecaster:
    global _forecaster
    if _forecaster is None:
        _forecaster = DemandForecaster()
    return _forecaster


def get_demand_forecast(crop: str, region: str = None) -> dict:
    return get_forecaster().get_forecast(crop, region).to_dict()
