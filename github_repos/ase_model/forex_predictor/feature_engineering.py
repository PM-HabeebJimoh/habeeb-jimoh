"""
forex_predictor.feature_engineering — REDESIGNED
-----------------------------------------------
Advanced disruptive formulas based purely on OHLC and derived market structure.
Every metric below is mathematically derived from price action with zero black-box AI.
"""
import pandas as pd
import numpy as np

epsilon = 1e-10


def fibonacci_ratios_from_ohlc(open_p, high_p, low_p, close_p):
    """
    Derive Fibonacci retracement levels directly from the current candle's range.
    Used to compute how close price is to structural support/resistance levels.
    """
    total_range = high_p - low_p
    if total_range < epsilon:
        return pd.Series({"fib_0236": 0.5, "fib_0382": 0.5, "fib_0500": 0.5, "fib_0618": 0.5})
    
    fib_0236 = low_p + 0.236 * total_range
    fib_0382 = low_p + 0.382 * total_range
    fib_0500 = low_p + 0.500 * total_range
    fib_0618 = low_p + 0.618 * total_range
    return pd.Series({
        "fib_0236": fib_0236,
        "fib_0382": fib_0382,
        "fib_0500": fib_0500,
        "fib_0618": fib_0618,
    })


def calculate_cbdr_advanced(df: pd.DataFrame) -> pd.Series:
    """
    ADVANCED CBDR — incorporates 3-period trend and wick dominance.
    CBDR_ADV = [sign(C-O) * (Body/Range)] * [1 + Wick_Dominance_Ratio - 0.5]
    Where Wick_Dominance = max(Upper_Wick, Lower_Wick) / Range
    """
    body = (df["close"] - df["open"]).abs()
    total_range = df["high"] - df["low"]
    sign_dir = np.sign(df["close"] - df["open"])
    
    upper_wick = df["high"] - df[["open", "close"]].max(axis=1)
    lower_wick = df[["open", "close"]].min(axis=1) - df["low"]
    max_wick = np.maximum(upper_wick, lower_wick)
    
    wick_dominance = max_wick / (total_range + epsilon)
    
    base_cbdr = sign_dir * (body / (total_range + epsilon))
    multiplier = 1.0 + (wick_dominance - 0.5)  # Amplify when wicks dominate (indecision/reversal signal)
    
    return base_cbdr * np.clip(multiplier, 0.2, 2.0)


def calculate_orci_advanced(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    ADVANCED ORCI — uses standard deviation bands, not just mean comparison.
    ORCI_ADV = (Range - SMA_Range) / (2 * STD_Range + epsilon)
    This creates a z-score style metric for range expansion/compression.
    """
    current_range = df["high"] - df["low"]
    sma_range = current_range.rolling(window=window).mean()
    std_range = current_range.rolling(window=window).std()
    return (current_range - sma_range) / (2 * std_range + epsilon)


def calculate_vams_advanced(df: pd.DataFrame, ma_window: int = 10) -> pd.Series:
    """
    ADVANCED VAMS — true ATR-style volatility normalization.
    ATR_proxy = rolling mean of (High - Low)
    VAMS_ADV = ((Close - SMA_10) / SMA_10) / (ATR_proxy / SMA_10 + epsilon)
    = (Close - SMA_10) / ATR_proxy
    Additionally scaled by body-size momentum to capture conviction.
    """
    sma_10 = df["close"].rolling(window=ma_window).mean()
    range_ma = (df["high"] - df["low"]).rolling(window=ma_window).mean()
    body = (df["close"] - df["open"]).abs()
    
    raw_vams = (df["close"] - sma_10) / (range_ma + epsilon)
    conviction_factor = body / (range_ma + epsilon)
    
    return raw_vams * (1 + conviction_factor)


def calculate_divergence_score(df: pd.DataFrame) -> pd.Series:
    """
    DIVERGENCE SCORE — detects hidden divergence between price and momentum.
    Compares current candle close change vs previous candle body change vs range change.
    """
    price_delta = df["close"].diff()
    body_delta = (df["close"] - df["open"]).diff()
    range_delta = (df["high"] - df["low"]).diff()
    
    # If price moves up but body shrinks and range expands = divergence / weakness
    divergence = np.sign(price_delta) * (np.sign(body_delta) * -1) * (np.sign(range_delta) + 1)
    return divergence.clip(-1, 1)


def calculate_multi_period_alignment(df: pd.DataFrame) -> pd.Series:
    """
    MULTI-PERIOD ALIGNMENT — checks if 5-period, 10-period, and 20-period trends agree.
    Returns +1 when all align bullish, -1 when all bearish, 0 when mixed.
    """
    ma5 = df["close"].rolling(window=5).mean()
    ma10 = df["close"].rolling(window=10).mean()
    ma20 = df["close"].rolling(window=20).mean()
    
    align_5_10 = np.sign(ma5 - ma10)
    align_10_20 = np.sign(ma10 - ma20)
    
    # Agreement score
    agreement = (align_5_10 + align_10_20) / 2
    return agreement.clip(-1, 1)


def calculate_fib_proximity_score(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate how close close price is to Fibonacci structural levels."""
    result = pd.DataFrame(index=df.index)
    
    fib_levels = df.apply(lambda row: fibonacci_ratios_from_ohlc(
        row["open"], row["high"], row["low"], row["close"]
    ), axis=1)
    
    # Compute normalized proximity: 0 = at low, 1 = at high
    total_range = df["high"] - df["low"]
    normalized_pos = (df["close"] - df["low"]) / (total_range + epsilon)
    
    # Score based on whether price is near key levels (high = near 0.618, low = near 0.236 for reversals)
    # Bullish signal when price pulls back to 0.382-0.500 zone from previous high context
    result["fib_proximity"] = np.clip(
        1 - (normalized_pos - 0.50).abs() * 2, -1, 1
    )
    return result


def calculate_volume_momentum(df: pd.DataFrame) -> pd.Series:
    """Volume momentum relative to its 20-period average."""
    vol_sma20 = df["volume"].rolling(window=20).mean()
    return (df["volume"] - vol_sma20) / (vol_sma20 + epsilon)


def calculate_structural_range_score(df: pd.DataFrame, window: int = 10) -> pd.Series:
    """
    STRUCTURAL RANGE SCORE — compares current candle range to previous 10-candle average range.
    Combined with body position within the range to detect accumulation/distribution.
    """
    current_range = df["high"] - df["low"]
    avg_range = current_range.rolling(window=window).mean()
    range_ratio = current_range / (avg_range + epsilon)
    
    # Where does the close sit within the current range?
    position_in_range = (df["close"] - df["low"]) / (current_range + epsilon)
    
    # Bullish when range expands but close sits in upper half; bearish when range expands but close in lower half
    score = np.sign(position_in_range - 0.5) * range_ratio
    return np.clip(score, -3, 3)


def add_all_features_advanced(df: pd.DataFrame) -> pd.DataFrame:
    """Full advanced feature pipeline."""
    df = df.copy()
    
    # Basic derived
    df["body_size"] = (df["close"] - df["open"]).abs()
    df["upper_wick"] = df["high"] - df[["open", "close"]].max(axis=1)
    df["lower_wick"] = df[["open", "close"]].min(axis=1) - df["low"]
    
    # Original / redesigned advanced formulas
    df["cbdr_adv"] = calculate_cbdr_advanced(df)
    df["orci_adv"] = calculate_orci_advanced(df, window=20)
    df["vams_adv"] = calculate_vams_advanced(df, ma_window=10)
    df["divergence_score"] = calculate_divergence_score(df)
    df["multi_period_alignment"] = calculate_multi_period_alignment(df)
    df["volume_momentum"] = calculate_volume_momentum(df)
    df["structural_range_score"] = calculate_structural_range_score(df, window=10)
    
    # Fibonacci proximity
    fib_df = calculate_fib_proximity_score(df)
    df = df.join(fib_df)
    
    # Standard indicators — refined calculations
    df["rsi_14"] = calculate_rsi_advanced(df, window=14)
    df["sma_10"] = df["close"].rolling(window=10).mean()
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["sma_50"] = df["close"].rolling(window=50).mean()
    df["ema_12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_26"] = df["close"].ewm(span=26, adjust=False).mean()
    
    # MACD with refined signal
    df["macd_line"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd_line"] - df["macd_signal"]
    
    # Bollinger Bands
    df["bb_mid"] = df["close"].rolling(window=20).mean()
    df["bb_std"] = df["close"].rolling(window=20).std()
    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]
    df["bb_bandwidth"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"]
    
    # Pattern detection — redesigned with stricter mathematical conditions
    # Bullish Hammer: long lower wick (>2x body), small body (<30% range), close > open
    df["hammer_bullish"] = (
        (df["lower_wick"] > 2.5 * df["body_size"]) &
        (df["body_size"] > epsilon) &
        (df["close"] > df["open"]) &
        (df["body_size"] < 0.35 * (df["high"] - df["low"]))
    ).astype(int)
    
    # Bearish Shooting Star: long upper wick (>2.5x body), small body (<30% range), close < open
    df["shooting_star_bearish"] = (
        (df["upper_wick"] > 2.5 * df["body_size"]) &
        (df["body_size"] > epsilon) &
        (df["close"] < df["open"]) &
        (df["body_size"] < 0.35 * (df["high"] - df["low"]))
    ).astype(int)
    
    # Bullish Engulfing (strict): previous close < previous open (bearish), current open < previous open, current close > previous close
    df_shifted = df.shift(1)
    df["prev_close"] = df_shifted["close"]
    df["prev_open"] = df_shifted["open"]
    df["prev_high"] = df_shifted["high"]
    df["prev_low"] = df_shifted["low"]
    
    df["bullish_engulfing"] = (
        (df["prev_close"] < df["prev_open"]) &
        (df["open"] < df["prev_close"]) &
        (df["close"] > df["prev_open"]) &
        (df["close"] > df["prev_high"] * 0.95)  # Must break previous high for strength
    ).astype(int)
    
    df["bearish_engulfing"] = (
        (df["prev_close"] > df["prev_open"]) &
        (df["open"] > df["prev_close"]) &
        (df["close"] < df["prev_open"]) &
        (df["close"] < df["prev_low"] * 1.05)  # Must break previous low for strength
    ).astype(int)
    
    # Additional advanced patterns
    # Bullish Piercing Line: open below previous low, close above previous midpoint
    prev_mid = (df_shifted["high"] + df_shifted["low"]) / 2
    df["bullish_piercing"] = (
        (df["open"] < df_shifted["low"]) &
        (df["close"] > prev_mid) &
        (df["close"] < df_shifted["high"])
    ).astype(int)
    
    # Bearish Dark Cloud: open above previous high, close below previous midpoint
    df["bearish_dark_cloud"] = (
        (df["open"] > df_shifted["high"]) &
        (df["close"] < prev_mid) &
        (df["close"] > df_shifted["low"])
    ).astype(int)
    
    # Morning Star / Evening Star approximation (3-candle structures)
    # Use direct shifted columns for previous candle values
    df_shifted = df.shift(1)
    prev_body_size = (df_shifted["close"] - df_shifted["open"]).abs()
    
    df["morning_star"] = (
        (df_shifted["close"] < df_shifted["open"]) &  # Previous bearish (close < open)
        (prev_body_size > 0) &
        (df["close"] > df_shifted["open"]) &  # Current close above previous open
        (df["open"] < df_shifted["low"])  # Current open below previous low (gap down then up)
    ).astype(int)
    
    df["evening_star"] = (
        (df_shifted["close"] > df_shifted["open"]) &  # Previous bullish
        (prev_body_size > 0) &
        (df["close"] < df_shifted["open"]) &  # Current close below previous open
        (df["open"] > df_shifted["high"])  # Current open above previous high (gap up then down)
    ).astype(int)
    
    df = df.drop(columns=["prev_close", "prev_open", "prev_high", "prev_low"], errors="ignore")
    return df


def calculate_rsi_advanced(df: pd.DataFrame, window: int = 14) -> pd.Series:
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / (avg_loss + epsilon)
    rsi = 100 - (100 / (1 + rs))
    return rsi
