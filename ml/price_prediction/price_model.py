"""
KisanDirect - Price Intelligence Module
========================================
Baseline-first approach (per spec):
  1. Simple, reliable baseline: rolling statistics (min/max/avg/trend) on
     historical (SYNTHETIC/DEMO) price data.
  2. A Linear Regression model on day-index + seasonal (month) features to
     project a short-term future trend line.

Both are clearly labeled DEMO/estimated, and predictions are explicitly
NOT presented as guaranteed prices, per product principle #3.

To upgrade later: swap `LinearRegression` for `RandomForestRegressor` or
`XGBRegressor` on richer features (weather, arrivals, festivals) once real
mandi/market data is available — the interface (`PricePredictor`) stays
the same.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from sklearn.linear_model import LinearRegression

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "price_history.csv"


@dataclass
class PriceIntelligenceReport:
    crop: str
    current_price: float
    min_price: float
    max_price: float
    avg_price: float
    trend_direction: str  # "up" / "down" / "stable"
    trend_pct_30d: float
    forecast_7d: list  # list of {date, projected_price}
    is_synthetic: bool = True
    disclaimer: str = "Prices shown use SYNTHETIC/DEMO market data for prototype purposes. Forecasts are estimates, not guarantees."

    def to_dict(self):
        d = self.__dict__.copy()
        return d


class PricePredictor:
    def __init__(self, data_path: Path = DATA_PATH):
        self.df = pd.read_csv(data_path, parse_dates=["date"])

    def get_report(self, crop: str, lookback_days: int = 90, forecast_days: int = 7) -> PriceIntelligenceReport:
        crop_df = self.df[self.df["crop"].str.lower() == crop.lower()].sort_values("date")
        if crop_df.empty:
            raise ValueError(f"No price history found for crop '{crop}'")

        recent = crop_df.tail(lookback_days).copy()
        current_price = float(recent["price_per_kg"].iloc[-1])
        min_price = float(recent["price_per_kg"].min())
        max_price = float(recent["price_per_kg"].max())
        avg_price = float(round(recent["price_per_kg"].mean(), 2))

        # 30-day trend %: compare avg of last 30d vs prior 30d
        last30 = crop_df.tail(30)["price_per_kg"].mean()
        prev30 = crop_df.tail(60).head(30)["price_per_kg"].mean() if len(crop_df) >= 60 else last30
        trend_pct = round(((last30 - prev30) / prev30) * 100, 1) if prev30 else 0.0
        trend_direction = "up" if trend_pct > 2 else ("down" if trend_pct < -2 else "stable")

        # --- Baseline regression model: day index -> price ---
        recent = recent.reset_index(drop=True)
        recent["day_idx"] = np.arange(len(recent))
        X = recent[["day_idx"]].values
        y = recent["price_per_kg"].values
        model = LinearRegression()
        model.fit(X, y)

        last_idx = recent["day_idx"].iloc[-1]
        last_date = recent["date"].iloc[-1]
        forecast = []
        for i in range(1, forecast_days + 1):
            future_idx = np.array([[last_idx + i]])
            projected = float(model.predict(future_idx)[0])
            # keep forecast within a sane band around recent min/max to avoid wild extrapolation
            projected = max(min_price * 0.85, min(max_price * 1.15, projected))
            forecast.append({
                "date": (last_date + pd.Timedelta(days=i)).date().isoformat(),
                "projected_price": round(projected, 2),
            })

        return PriceIntelligenceReport(
            crop=crop,
            current_price=current_price,
            min_price=min_price,
            max_price=max_price,
            avg_price=avg_price,
            trend_direction=trend_direction,
            trend_pct_30d=trend_pct,
            forecast_7d=forecast,
        )


if __name__ == "__main__":
    predictor = PricePredictor()
    for crop in ["Tomato", "Wheat", "Onion"]:
        report = predictor.get_report(crop)
        print(f"\n=== {crop} Price Intelligence (SYNTHETIC DEMO DATA) ===")
        print(f"Current: Rs.{report.current_price} | Avg(90d): Rs.{report.avg_price} | "
              f"Min: Rs.{report.min_price} | Max: Rs.{report.max_price}")
        print(f"30-day trend: {report.trend_direction} ({report.trend_pct_30d}%)")
        print("7-day forecast (ESTIMATE, not guaranteed):")
        for f in report.forecast_7d:
            print(f"  {f['date']}: Rs.{f['projected_price']}")
