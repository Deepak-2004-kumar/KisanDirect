"""
KisanDirect - Demand Forecasting Module
=========================================
Baseline model: aggregates SYNTHETIC/DEMO historical orders by
crop + region + day-of-week + rolling trend, then classifies expected
demand as LOW / MEDIUM / HIGH using tertile thresholds learned from
history, and produces a simple 7-day / 30-day trend projection using
a Linear Regression on daily aggregated quantity.

Upgrade path: replace with a proper time-series model (Prophet, SARIMA,
or a gradient-boosted regressor with lag features) once real order
history accumulates on the platform.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from sklearn.linear_model import LinearRegression

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "orders_history.csv"


@dataclass
class DemandForecastReport:
    crop: str
    region: str | None
    demand_level: str  # LOW / MEDIUM / HIGH
    expected_daily_quantity_kg: float
    trend_7d: list
    trend_30d_avg_kg: float
    is_synthetic: bool = True
    disclaimer: str = "Demand forecast uses SYNTHETIC/DEMO order history for prototype purposes."

    def to_dict(self):
        return self.__dict__.copy()


class DemandForecaster:
    def __init__(self, data_path: Path = DATA_PATH):
        self.df = pd.read_csv(data_path, parse_dates=["date"])

    def _daily_series(self, crop: str, region: str | None) -> pd.DataFrame:
        df = self.df[self.df["crop"].str.lower() == crop.lower()]
        if region:
            df = df[df["region"].str.lower() == region.lower()]
        daily = df.groupby("date")["quantity_kg"].sum().reset_index()
        # fill missing days with 0 so trend isn't skewed
        if daily.empty:
            return daily
        full_range = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
        daily = daily.set_index("date").reindex(full_range, fill_value=0).rename_axis("date").reset_index()
        return daily

    def get_forecast(self, crop: str, region: str | None = None, forecast_days: int = 7) -> DemandForecastReport:
        daily = self._daily_series(crop, region)
        if daily.empty:
            raise ValueError(f"No order history for crop='{crop}' region='{region}'")

        recent_30 = daily.tail(30)
        avg_30 = float(recent_30["quantity_kg"].mean())

        # Tertile-based LOW/MEDIUM/HIGH thresholds from full history for this crop
        all_daily_vals = daily["quantity_kg"].values
        low_thresh, high_thresh = np.percentile(all_daily_vals, [33, 66])
        recent_avg_7 = float(daily.tail(7)["quantity_kg"].mean())
        if recent_avg_7 <= low_thresh:
            level = "LOW"
        elif recent_avg_7 <= high_thresh:
            level = "MEDIUM"
        else:
            level = "HIGH"

        # Linear regression trend projection
        daily = daily.reset_index(drop=True)
        daily["day_idx"] = np.arange(len(daily))
        X = daily[["day_idx"]].tail(60).values
        y = daily["quantity_kg"].tail(60).values
        model = LinearRegression()
        model.fit(X, y)

        last_idx = daily["day_idx"].iloc[-1]
        last_date = daily["date"].iloc[-1]
        trend = []
        for i in range(1, forecast_days + 1):
            pred = float(model.predict([[last_idx + i]])[0])
            pred = max(0.0, pred)
            trend.append({
                "date": (last_date + pd.Timedelta(days=i)).date().isoformat(),
                "projected_quantity_kg": round(pred, 1),
            })

        return DemandForecastReport(
            crop=crop,
            region=region,
            demand_level=level,
            expected_daily_quantity_kg=round(recent_avg_7, 1),
            trend_7d=trend,
            trend_30d_avg_kg=round(avg_30, 1),
        )


if __name__ == "__main__":
    forecaster = DemandForecaster()
    for crop in ["Tomato", "Onion"]:
        report = forecaster.get_forecast(crop)
        print(f"\n=== {crop} Demand Forecast (SYNTHETIC DEMO DATA) ===")
        print(f"Demand level: {report.demand_level} | Expected daily qty: {report.expected_daily_quantity_kg} kg "
              f"| 30d avg: {report.trend_30d_avg_kg} kg")
        print("7-day projection:")
        for t in report.trend_7d:
            print(f"  {t['date']}: {t['projected_quantity_kg']} kg")
