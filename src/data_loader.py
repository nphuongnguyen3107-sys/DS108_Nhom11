"""Data loader — load cleaned_final.csv cho dashboard."""
import pandas as pd
from pathlib import Path


def load_cleaned_data() -> pd.DataFrame:
    path = Path(__file__).resolve().parent.parent / "data" / "processed" / "cleaned_final.csv"
    df = pd.read_csv(path, parse_dates=["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    return {
        "total_hours": len(df),
        "date_range": f"{df['time'].min().date()} → {df['time'].max().date()}",
        "pm25_mean": round(df["pm25"].mean(), 2),
        "pm25_max": round(df["pm25"].max(), 1),
        "pm25_valid_pct": round(df["pm25"].notna().mean() * 100, 1),
    }