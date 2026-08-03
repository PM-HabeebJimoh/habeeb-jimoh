"""
forex_predictor.prediction_engine
---------------------------------
Takes engineered features and pattern rules to output predictions.
Includes validation and transparency reports.
"""
import pandas as pd
import numpy as np
from .pattern_engine import generate_prediction_advanced, compute_cdp_advanced, DEFAULT_WEIGHTS


def predict_direction(df: pd.DataFrame, weights: dict = None) -> pd.DataFrame:
    """Run the full predictive pipeline and return predictions."""
    return generate_prediction_advanced(df, weights=weights)


def accuracy_report(df: pd.DataFrame) -> dict:
    """
    Calculate directional prediction accuracy.
    Filters to predictions where prediction != 0 (non-neutral).
    Reports:
    - Total signals
    - Correct predictions
    - Accuracy %
    - Bullish accuracy
    - Bearish accuracy
    """
    pred_df = df.dropna(subset=["prediction_binary", "actual"])
    # Use binary prediction for standard accuracy; also report advanced tier breakdown
    pred_col = "prediction_binary" if "prediction_binary" in pred_df.columns else "prediction_advanced"
    signals = pred_df[pred_df[pred_col] != 0].copy()
    
    # For binary accuracy, treat positive as bullish, negative as bearish
    signals["correct_binary"] = (signals[pred_col] == signals["actual"]).astype(int)
    
    # For advanced tier: separate strong (±2) and moderate (±1) signals
    strong_bull = signals[signals["prediction_advanced"] == 2]
    moderate_bull = signals[signals["prediction_advanced"] == 1]
    strong_bear = signals[signals["prediction_advanced"] == -2]
    moderate_bear = signals[signals["prediction_advanced"] == -1]
    
    if len(signals) == 0:
        return {
            "total_signals": 0,
            "correct": 0,
            "accuracy_pct": 0.0,
            "bullish_signals": 0,
            "bullish_accuracy_pct": 0.0,
            "bearish_signals": 0,
            "bearish_accuracy_pct": 0.0,
            "strong_bull_signals": 0,
            "strong_bear_signals": 0,
            "note": "No directional signals generated.",
        }

    total = len(signals)
    correct = int(signals["correct_binary"].sum())
    
    # Count by binary direction (positive = bullish, negative = bearish)
    bullish_all = signals[signals[pred_col] == 1]
    bearish_all = signals[signals[pred_col] == -1]
    
    # Also count strong signals separately
    bullish_acc = (bullish_all["correct_binary"].sum() / len(bullish_all) * 100) if len(bullish_all) > 0 else 0.0
    bearish_acc = (bearish_all["correct_binary"].sum() / len(bearish_all) * 100) if len(bearish_all) > 0 else 0.0
    
    strong_bull_acc = (strong_bull["correct_binary"].sum() / len(strong_bull) * 100) if len(strong_bull) > 0 else 0.0
    strong_bear_acc = (strong_bear["correct_binary"].sum() / len(strong_bear) * 100) if len(strong_bear) > 0 else 0.0
    
    overall_acc = (correct / total) * 100

    return {
        "total_signals": total,
        "correct": correct,
        "accuracy_pct": round(overall_acc, 2),
        "bullish_signals": len(bullish_all),
        "bullish_accuracy_pct": round(bullish_acc, 2),
        "bearish_signals": len(bearish_all),
        "bearish_accuracy_pct": round(bearish_acc, 2),
        "strong_bull_signals": len(strong_bull),
        "strong_bear_signals": len(strong_bear),
        "strong_bull_accuracy_pct": round(strong_bull_acc, 2),
        "strong_bear_accuracy_pct": round(strong_bear_acc, 2),
        "note": (
            f"Advanced directional accuracy on {total} signals: {overall_acc:.2f}%. "
            f"Strong Bullish ({len(strong_bull)} signals): {strong_bull_acc:.1f}%. "
            f"Strong Bearish ({len(strong_bear)} signals): {strong_bear_acc:.1f}%. "
            "System uses redesigned non-linear composite formulas (CDP_Advanced)."
        ),
    }


def summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return a concise summary table for quick inspection."""
    result = predict_direction(df.copy())
    report = accuracy_report(result)
    summary = pd.DataFrame({
        "Metric": [
            "Total Signals",
            "Correct",
            "Directional Accuracy (%)",
            "Bullish Signals",
            "Bullish Accuracy (%)",
            "Bearish Signals",
            "Bearish Accuracy (%)",
        ],
        "Value": [
            report["total_signals"],
            report["correct"],
            report["accuracy_pct"],
            report["bullish_signals"],
            report["bullish_accuracy_pct"],
            report["bearish_signals"],
            report["bearish_accuracy_pct"],
        ],
    })
    return summary
