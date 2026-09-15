"""Wraps ml/price_prediction/price_model.py for use inside the FastAPI backend."""
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[3] / "ml"
sys.path.insert(0, str(ML_ROOT / "price_prediction"))

from price_model import PricePredictor  # noqa: E402

_predictor = None


def get_predictor() -> PricePredictor:
    global _predictor
    if _predictor is None:
        _predictor = PricePredictor()
    return _predictor


def get_price_report(crop: str) -> dict:
    return get_predictor().get_report(crop).to_dict()
