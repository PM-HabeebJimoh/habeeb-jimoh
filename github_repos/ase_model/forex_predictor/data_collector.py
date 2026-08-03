"""
forex_predictor.data_collector
-----------------------------
Collects freely available forex OHLC data using yfinance.

NOTE ON DATA QUALITY & REALISM:
Forex directional prediction using only public OHLC + derived indicators
cannot reliably achieve 85% sustained accuracy. This module collects
clean data; the prediction module uses that data with full transparency.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Major pairs as per user scope
MAJOR_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
    "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
]


def fetch_ohlc(pair: str, start: str = "2026-07-01", end: str = "2026-07-31", interval: str = "1d") -> pd.DataFrame:
    """Fetch ONLY REAL OHLCV data for July 2026. NO SYNTHETIC / NO MOCK / NO DUMMY DATA."""
    ticker = yf.Ticker(pair)
    df = ticker.history(start=start, end=end, interval=interval)
    # Yahoo forex pairs use =X suffix
    df = df.rename(columns={
        "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
    })
    df.index = pd.to_datetime(df.index)
    # Ensure column names are lowercase
    df.columns = [c.lower() for c in df.columns]
    # Drop any non-OHLCV columns
    df = df.loc[:, ["open", "high", "low", "close", "volume"]].dropna()
    # STRICT FILTER: ONLY JULY 2026 REAL DATA — reject empty or synthetic sources
    if len(df) == 0:
        raise ValueError(f"NO REAL DATA AVAILABLE FOR {pair} IN JULY 2026 — ONLY REAL DATA PERMITTED")
    return df


def fetch_all_majors(start: str = "2026-07-01", end: str = "2026-07-31", interval: str = "1d") -> dict[str, pd.DataFrame]:
    """Fetch ONLY REAL OHLC for all major pairs — July 2026 ONLY."""
    results = {}
    for pair in MAJOR_PAIRS:
        try:
            results[pair] = fetch_ohlc(pair, start, end, interval)
        except Exception as e:
            print(f"[ERROR — REAL DATA ONLY] Failed to fetch {pair}: {e}")
            # NO FALLBACK — NO SYNTHETIC DATA ALLOWED
    return results
