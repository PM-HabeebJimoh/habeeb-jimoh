#!/usr/bin/env python3
"""
main.py — Forex Predictive System Runner
------------------------------------------
Runs data collection, feature engineering, prediction, and reporting
for major forex pairs.
"""
import sys
import pandas as pd
from forex_predictor.data_collector import fetch_all_majors
from forex_predictor.feature_engineering import add_all_features_advanced as add_all_features
from forex_predictor.prediction_engine import predict_direction, accuracy_report, summary_table
from forex_predictor.pattern_engine import DEFAULT_WEIGHTS, compute_cdp_advanced


def main():
    print("=" * 70)
    print("ASE — Nigerian Yoruba Name: Yoruba: ASE (Power / Command)")
    print("=" * 70)
    print()
    print("TRANSPARENCY NOTICE:")
    print("- No OHLC-only system achieves sustained 85% directional accuracy.")
    print("- This system uses original composite formulas (CDP, CBDR, ORCI, VAMS).")
    print("- Realistic directional accuracy: 45% - 58% (market-dependent).")
    print()

    pairs = [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
        "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
    ]

    results = []
    for pair in pairs:
        print(f"Processing {pair} ...")
        try:
            from forex_predictor.data_collector import fetch_ohlc
            # ONLY REAL DATA — July 2026
            df = fetch_ohlc(pair, start="2026-07-01", end="2026-07-31", interval="1d")
            # NO SYNTHETIC / NO MOCK / NO SIMULATION — ONLY REAL MARKET DATA
            df_features = add_all_features(df)
            predictions = predict_direction(df_features)
            report = accuracy_report(predictions)
            results.append({
                "pair": pair,
                "status": "completed",
                **report,
            })
            print(f"  -> Signals: {report['total_signals']} | "
                  f"Accuracy: {report['accuracy_pct']}% | "
                  f"Note: {report['note']}")
        except Exception as e:
            print(f"  -> ERROR for {pair}: {e}")
            results.append({"pair": pair, "status": "error", "message": str(e)})

    # Print aggregated table
    print()
    print("=" * 70)
    print("AGGREGATED BACKTEST RESULTS — REAL DATA: JULY 2026 ONLY")
    print("=" * 70)
    result_df = pd.DataFrame(results)
    for _, row in result_df.iterrows():
        pair = row.get("pair", "N/A")
        status = row.get("status", "unknown")
        if status == "completed":
            print(f"{pair:12s} | Signals: {str(row.get('total_signals', 'N/A')):>4s} | "
                  f"Acc: {str(row.get('accuracy_pct', 'N/A')):>5s}% | "
                  f"Correct: {str(row.get('correct', 'N/A')):>3s} | "
                  f"Bullish Acc: {str(row.get('bullish_accuracy_pct', 'N/A')):>5s}%")
        else:
            print(f"{pair:12s} | Status: {status}")

    print()
    print("=" * 70)
    print("FORMULA REFERENCE")
    print("=" * 70)
    print("CBDR  = Candle Body Dominance Ratio")
    print("ORCI  = OHLC Range Compression Index")
    print("VAMS  = Volatility-Adjusted Momentum Score")
    print("CDP   = Composite Directional Probability (disruptive predictive formula)")
    print()
    print("REDESIGNED FORMULAS (Advanced Mathematical Framework):")
    print("  CBDR_ADV = sign(C-O) * (Body/Range) * (1 + Wick_Dominance - 0.5)")
    print("  ORCI_ADV = (Range - SMA_Range) / (2 * STD_Range)  [z-score]")
    print("  VAMS_ADV = (Close - SMA_10) / Range_MA_10 * (1 + Body/Range_MA_10)")
    print("  DIVERGENCE = price_delta * -body_delta * (range_delta + 1)")
    print("  MULTI_ALIGN = (MA5_vs_MA10 + MA10_vs_MA20) / 2")
    print("  CDP_ADV = tanh( 0.18*tanh(CBDR/2) + 0.20*tanh(VAMS/3) + 0.12*ORCI_NORM +")
    print("                 0.12*DIVERGENCE + 0.08*MULTI_ALIGN + 0.12*PATTERN + 0.08*RSI_QUAD + 0.05*VOL + 0.05*STRUCT )")
    print()
    print("PREDICTION RULES (Advanced Tier System):")
    print("  CDP > +0.35  -> STRONG BULLISH (high confidence, positive binary signal)")
    print("  CDP > +0.15  -> BULLISH (moderate confidence)")
    print("  CDP < -0.35  -> STRONG BEARISH (high confidence)")
    print("  CDP < -0.15  -> BEARISH (moderate confidence)")
    print("  Between ±0.15 -> NEUTRAL (filtered out / no signal)")
    print()
    print("DISCLAIMER:")
    print("This is a research / educational system. Forex trading carries risk.")
    print("Òrìṣà Àṣeyọrí operates exclusively on real market OHLC data — July 2026 only. No synthetic inputs permitted.")
    print("Always use proper risk management and do not rely solely on this model.")


if __name__ == "__main__":
    main()
