"""
forex_predictor.backtester
--------------------------
Backtests the predictive system across pairs and reports accuracy.
Includes transparency notes about 85% expectations.
"""
import pandas as pd
from .data_collector import fetch_all_majors
from .feature_engineering import add_all_features_advanced as add_all_features
from .prediction_engine import predict_direction, accuracy_report, summary_table


def backtest_pair(pair: str, period: str = "2y", interval: str = "1d") -> dict:
    """Run the full pipeline on a single pair and return accuracy metrics."""
    from .data_collector import fetch_ohlc
    df = fetch_ohlc(pair, period=period, interval=interval)
    df_features = add_all_features(df)
    predictions = predict_direction(df_features)
    report = accuracy_report(predictions)
    return {
        "pair": pair,
        **report,
    }


def backtest_all_majors(period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """Run backtest on all major pairs and return aggregated results."""
    data = fetch_all_majors(period=period, interval=interval)
    results = []
    for pair, df in data.items():
        if df.empty:
            results.append({
                "pair": pair,
                "total_signals": 0,
                "correct": 0,
                "accuracy_pct": 0.0,
                "note": "No data fetched.",
            })
            continue
        df_features = add_all_features(df)
        predictions = predict_direction(df_features)
        report = accuracy_report(predictions)
        results.append({"pair": pair, **report})
    return pd.DataFrame(results)
