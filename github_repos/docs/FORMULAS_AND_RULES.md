# Forex Disruptive Pattern, Formula, Calculations & Rules System
## ASE — Nigerian Yoruba Name: Yoruba: ASE (Power / Command)

## Author / Project
- Project: `PM-HabeebJimoh/habeeb-jimoh`
- Branch: `arena/019fc691-habeeb-jimoh`
- Date: 2026-08-03
- Focus: REAL DATA ONLY: July 2026 Forex Pairs (EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD)

---

## 1. Study of Forex OHLC Market Data

### 1.1 Data Source
- **Source**: Yahoo Finance (`yfinance` Python library)
- **Access Method**: Free public API via Python module `data_collector.py`
- **Pairs Covered**: Major pairs only (`MAJOR_PAIRS` list in code)
- **Interval**: Daily (`1d`) by default (configurable to `1h`, `5m`, etc.)
- **History**: 2 years (`2y`) default

### 1.2 What Data Is Collected Per Pair
For each pair (e.g., `EURUSD=X`), the system collects:
- `open` — Opening price
- `high` — Highest price in the period
- `low` — Lowest price in the period
- `close` — Closing price
- `volume` — Trading volume (if available for the pair)

### 1.3 Additional Derived Metrics Collected / Calculated
The feature engineering module calculates over **20 derived metrics** per candle:
- `body_size` — Absolute difference between open and close
- `upper_wick` / `lower_wick` — Wick lengths
- `cbdr` — Candle Body Dominance Ratio (original formula)
- `orci` — OHLC Range Compression Index (original formula)
- `vams` — Volatility-Adjusted Momentum Score (original formula)
- `rsi_14` — 14-period Relative Strength Index
- `sma_10`, `sma_50` — Simple Moving Averages
- `ema_12`, `ema_26` — Exponential Moving Averages (MACD components)
- `macd_line`, `macd_signal`, `macd_hist`
- `bb_upper`, `bb_lower`, `bb_mid`, `bb_bandwidth` — Bollinger Bands
- `hammer_bullish`, `shooting_star_bearish`, `bullish_engulfing`, `bearish_engulfing` — Pattern flags

---

## 2. The Disruptive Pattern & Formula System

### 2.1 Philosophy — Why "Disruptive"
Standard forex models rely heavily on single-indicator strategies (e.g., EMA crossover alone, RSI alone). The disruptive approach here combines **original composite formulas** that synthesize multiple market dimensions (body dominance, volatility-adjusted momentum, range compression, pattern recognition, RSI extremes, and trend alignment) into a single directional probability score.

### 2.2 Original Formulas

#### Formula A: CBDR (Candle Body Dominance Ratio)
```
CBDR = sign(Close - Open) * (|Close - Open| / (High - Low + epsilon))
```
- **Purpose**: Measures how much of the candle's total range is captured by the body, signed by direction.
- **Range**: [-1, 1]
- **Interpretation**: 
  - Near +1 = Strong bullish candle with little to no wicks (high conviction).
  - Near -1 = Strong bearish candle with little to no wicks.
  - Near 0 = Small body relative to range (indecision / doji-like behavior).

---

#### Formula B: ORCI (OHLC Range Compression Index)
```
ORCI = (Current_Range - SMA_Range(20)) / (SMA_Range(20) + epsilon)
```
- **Purpose**: Detects whether the current candle's range is compressed (low volatility) or expanded (high volatility) relative to its 20-candle history.
- **Range**: Unbounded; typically [-2, 2] in practice.
- **Interpretation**:
  - Positive = Range expansion (often precedes breakouts).
  - Negative = Range compression (often precedes volatility expansion / breakout).

---

#### Formula C: VAMS (Volatility-Adjusted Momentum Score)
```
SMA_10 = SMA(Close, 10)
Range_MA_10 = SMA(High - Low, 10)
VAMS = (Close - SMA_10) / (Range_MA_10 + epsilon)
```
- **Purpose**: Normalizes price momentum by recent volatility.
- **Range**: Unbounded; clipped to [-3, 3] before weighting.
- **Interpretation**:
  - Positive = Price above its 10-candle average relative to recent volatility.
  - Negative = Price below its 10-candle average relative to recent volatility.

---

#### Formula D: Pattern Score (PS)
```
PS = Bullish_Patterns - Bearish_Patterns
```
Where:
- Bullish patterns = `hammer_bullish` + `bullish_engulfing`
- Bearish patterns = `shooting_star_bearish` + `bearish_engulfing`
- **Range**: Clipped to [-1, 1].

---

#### Formula E: RSI Extreme Score (RSI_Ext)
```
If RSI < 30:  RSI_Ext = (30 - RSI) / 30   (positive -> bullish signal)
If RSI > 70:  RSI_Ext = -(RSI - 70) / 30  (negative -> bearish signal)
Else:          RSI_Ext = 0
```
- **Purpose**: Converts RSI into a directional signal based on overbought/oversold extremes.
- **Range**: [-1, 1].

---

#### Formula F: Trend Filter Score (Trend_Filter)
```
EMA_Cross = sign(EMA_12 - EMA_26)
Price_vs_SMA50 = sign(Close - SMA_50)
Trend_Filter = (EMA_Cross + Price_vs_SMA50) / 2
```
- **Purpose**: Confirms whether short-term trend aligns with medium-term price position.
- **Range**: [-1, 1].

---

### 2.3 Final Predictive Formula: CDP (Composite Directional Probability)
```
CDP = 0.20 * CBDR_trend(5) + 0.25 * VAMS + 0.15 * (ORCI / 2) + 0.15 * Pattern_Score + 0.15 * RSI_Extreme + 0.10 * Trend_Filter
```
- **CBDR_trend** = 5-candle rolling mean of CBDR (smooths noise).
- **ORCI / 2** = Normalized to roughly [-1, 1] range.
- **Weights** (`DEFAULT_WEIGHTS` in code) are configurable.
- **Range**: Typically [-1, 1]; extreme values rare due to normalization.

---

### 2.4 Prediction Rules (Rule Engine)
Based on the CDP value at each candle:

| Condition | Prediction (Next Candle) | Confidence Level |
|-----------|-------------------------|------------------|
| `CDP > +0.15` | **Bullish** (expect higher close or upward direction) | Moderate |
| `CDP < -0.15` | **Bearish** (expect lower close or downward direction) | Moderate |
| `-0.15 <= CDP <= +0.15` | **Neutral** (no directional signal; avoid trade) | Low |

**How the rules are applied in the pipeline (`pattern_engine.py`):**
1. Calculate all feature indicators (`feature_engineering.py`).
2. Compute CDP (`pattern_engine.py`).
3. Apply prediction rules (`prediction_engine.py`).
4. Compare prediction to actual next-candle direction (`prediction_engine.py`).
5. Report accuracy (`backtester.py`).

---

## 3. Calculations & Implementation Details

### 3.1 Module Structure (`forex_predictor/`)
```
forex_predictor/
  __init__.py         (optional package init)
  data_collector.py   # Fetch OHLC from Yahoo Finance
  feature_engineering.py  # All original + standard indicators
  pattern_engine.py    # Rules, CDP formula, pattern detection
  prediction_engine.py # Apply rules and compute accuracy
  backtester.py        # Aggregate backtests across pairs
```

### 3.2 Data Flow
```
Yahoo Finance API
      ↓
fetch_ohlc(pair)  ->  OHLC DataFrame
      ↓
add_all_features()  ->  Features (CBDR, ORCI, VAMS, RSI, BB, MACD, patterns)
      ↓
generate_prediction()  ->  CDP + Prediction (1, -1, 0) + Actual (shifted)
      ↓
accuracy_report()  ->  Signal count, accuracy %, bullish/bearish accuracy
```

### 3.3 Backtesting Approach
- **Method**: Daily interval (`1d`), 2 years of history.
- **Prediction target**: Next candle's close direction (`close_next > close_current` = Bullish, else Bearish).
- **Signal filter**: Only predictions where `prediction != 0` (non-neutral) are counted.
- **Accuracy formula**: `Correct / Total Signals * 100`

---

## 4. Results & Transparency Report

### 4.1 Realistic Expectations (Critical Transparency)
**Claim Check**: The user requested a system predicting with **85% accuracy** the direction of the next candles.

**Reality**: 
- Forex markets are highly efficient, noisy, and influenced by macroeconomic events, central bank actions, geopolitical news, liquidity conditions, and institutional order flow — none of which are fully captured by OHLC candles alone.
- Academic and industry studies show that technical-indicator-only forex models typically achieve **45% - 58% directional accuracy** on out-of-sample daily data, with significant variance by pair and market regime.
- **No public OHLC-only model achieves sustained 85% directional accuracy.** Any claim of 85% sustained accuracy with only OHLC data is either:
  1. Overfitted to historical data (curve-fitting / data snooping),
  2. Measured on extremely short or cherry-picked timeframes,
  3. Not accounting for slippage, spread, and transaction costs, or
  4. Not reproducible in live markets.

**This System's Design Intent**:
- The system **attempts 85%** through aggressive composite optimization (original formulas, multiple confirmation layers, weight tuning).
- The code reports **actual backtested accuracy** honestly.
- Users are explicitly warned in code comments, console output, and this document.

### 4.2 What This System Provides
- **Disruptive formulas**: CBDR, ORCI, VAMS, CDP — original mathematical constructs.
- **Rule-based engine**: Configurable weights, clear prediction rules, and transparency.
- **Free data access**: No paid API required (Yahoo Finance via `yfinance`).
- **Backtesting framework**: Automated accuracy reporting per pair.
- **Full transparency**: Every claim is backed by code and clearly labeled.

### 4.3 How to Improve Realistic Accuracy Further (Beyond OHLC)
To push accuracy closer to 55-65% (still not 85%), one would need:
- **Multi-timeframe analysis** (e.g., confirm daily signal with H4 / H1 structure).
- **Fundamental / macro filters** (interest rate differentials, COT reports, economic calendar).
- **Volume profile / order flow data** (not freely available at high quality for all forex pairs).
- **Machine learning ensemble** (Random Forest, XGBoost, or LSTM on engineered features) rather than linear weights.
- **Risk management and position sizing** (even 52% accuracy can be profitable with proper risk/reward ratios).

---

## 5. Files & How to Use

### 5.1 Run the System
```bash
# Install dependencies (if not already installed)
pip install yfinance pandas numpy

# Run the full pipeline
python main.py
```

### 5.2 Key Files
- `main.py` — Entry point. Runs data fetch, feature engineering, prediction, and prints aggregated results.
- `forex_predictor/data_collector.py` — Fetches OHLC data from Yahoo Finance.
- `forex_predictor/feature_engineering.py` — Computes CBDR, ORCI, VAMS, RSI, BB, MACD, pattern flags.
- `forex_predictor/pattern_engine.py` — Defines rules, calculates CDP, generates predictions.
- `forex_predictor/prediction_engine.py` — Computes accuracy metrics.
- `forex_predictor/backtester.py` — Aggregates backtests across pairs.
- `docs/FORMULAS_AND_RULES.md` — This document.

### 5.3 Example Output (Conceptual)
```
FOREX DISRUPTIVE PREDICTION SYSTEM
...
Pair: EURUSD=X  | Signals: 320  | Acc: 52.50% | Bullish Acc: 51.00% | Note: ...
Pair: GBPUSD=X  | Signals: 310  | Acc: 49.35% | Bullish Acc: 48.20% | Note: ...
```
(Note: Actual numbers will vary based on market conditions at time of execution.)

---

## 6. Code Quality & Design Notes

- **Modular**: Each component (data, features, rules, predictions, backtests) is isolated.
- **Configurable**: Weights in `DEFAULT_WEIGHTS` can be adjusted to experiment.
- **Transparent**: Every prediction is explained by the CDP formula; no black-box AI.
- **Realistic**: No false promises of 85% accuracy; transparency is hard-coded.
- **Reproducible**: Uses only free public APIs and standard Python libraries.

---

## 7. Conclusion

This repository delivers a **disruptive, formula-driven forex prediction framework** that:
1. Studies all major forex pairs using freely available OHLC data.
2. Defines original calculations (CBDR, ORCI, VAMS) and a composite predictive formula (CDP).
3. Applies a clear rule system (thresholds at ±0.15) to predict the next candle direction.
4. Reports results honestly, explicitly noting that **85% sustained directional accuracy is not achievable** with OHLC-only public data.
5. Provides a transparent, modular Python system for research, education, and further development.

---

*Document updated: 2026-08-03*
*Branch: arena/019fc691-habeeb-jimoh*
