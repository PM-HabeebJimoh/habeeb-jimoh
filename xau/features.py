"""XAU-Q feature engine — what is actually knowable about gold from OHLCV.

This is the "study the market" part of the brief. Every feature below is here
because it encodes a documented structural property of gold specifically, not
because it is a popular indicator.

WHAT GOLD ACTUALLY IS, MECHANICALLY
-----------------------------------
XAUUSD is not a currency pair and treating it as one is the first mistake. It is
a *ratio between a zero-yield monetary metal and the world's funding currency*.
That gives it four exploitable structural properties, and everything in this
file targets one of them:

  P1. VOLATILITY CLUSTERS HARDER THAN DIRECTION PERSISTS.
      Gold's absolute returns are strongly autocorrelated; its signed returns
      are barely autocorrelated at all. This is the single most important fact
      for this task, and it is why range/level prediction is tractable while
      direction prediction is close to a coin flip. Features: rv_*, atr_*, vol_of_vol.

  P2. THE SESSION CYCLE IS REAL AND MECHANICAL.
      Asian hours compress range (thin book, no data releases). London open
      expands it. The 12:00-16:00 UTC overlap carries the US calendar and the
      LBMA PM auction. This is a *calendar* effect, not a price effect, so it
      cannot be arbitraged away. Features: session_*, hour_sin/cos, or_*.

  P3. LIQUIDITY POOLS SIT AT PRIOR EXTREMES AND ROUND NUMBERS.
      Stops cluster above prior highs / below prior lows and at $10/$25/$50
      handles. Sweeps of those levels that immediately reverse are the most
      reliable short-horizon reversal tell in gold. Features: sweep_*, round_*.

  P4. RANGE EXPANSION FOLLOWS RANGE COMPRESSION (NR-N effect).
      The narrowest range in N bars is followed by an outsized range far more
      often than chance. Direction is ~coin-flip; magnitude is not.
      Features: nr_rank, squeeze_*, range_pctile.

Anything that only measures "is price going up" (moving-average crosses, naive
momentum) is deliberately down-weighted, because on gold those features carry
almost no out-of-sample signed information at intraday horizons.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .core import (
    Bar, Session, atr, clamp, logret, mean, quantile, session_of, sign, stdev,
    true_range,
)


FEATURE_NAMES: list[str] = []


def _register(*names: str) -> None:
    for n in names:
        if n not in FEATURE_NAMES:
            FEATURE_NAMES.append(n)


@dataclass
class FeatureVector:
    values: dict[str, float]
    ts_index: int

    def as_list(self, names: Sequence[str]) -> list[float]:
        return [self.values.get(n, 0.0) for n in names]


class FeatureBuilder:
    """Builds features for bar i using ONLY bars[0:i].

    The `warmup` property tells the walk-forward driver the first index at which
    a complete feature vector exists.
    """

    def __init__(self, lookback_long: int = 240):
        self.lookback_long = lookback_long

    @property
    def warmup(self) -> int:
        return self.lookback_long + 5

    # ------------------------------------------------------------------ main
    def at(self, bars: Sequence[Bar], i: int) -> FeatureVector | None:
        """Feature vector for predicting bars[i]. Reads bars[:i] only."""
        if i < self.warmup or i >= len(bars) + 1:
            return None
        h = bars[:i]                      # history: everything strictly before i
        f: dict[str, float] = {}

        last = h[-1]
        a14 = atr(h, 14) or 1e-9
        a50 = atr(h, 50) or 1e-9

        # ---- P1: volatility state -------------------------------------------
        # Realised vol at three horizons, in log-return space, annualisation-free.
        for n in (5, 20, 60):
            rets = [logret(h[j - 1].close, h[j].close) for j in range(len(h) - n, len(h))]
            f[f"rv_{n}"] = stdev(rets)
        _register("rv_5", "rv_20", "rv_60")

        # Vol regime: short vol relative to long vol. >1 means expanding.
        f["vol_ratio_5_60"] = f["rv_5"] / (f["rv_60"] + 1e-12)
        f["vol_ratio_20_60"] = f["rv_20"] / (f["rv_60"] + 1e-12)
        _register("vol_ratio_5_60", "vol_ratio_20_60")

        # Vol-of-vol: is the volatility itself unstable? High vov precedes regime breaks.
        rv_series = []
        for k in range(10):
            seg = h[len(h) - 20 - k: len(h) - k]
            if len(seg) > 2:
                rv_series.append(stdev([logret(seg[j - 1].close, seg[j].close)
                                        for j in range(1, len(seg))]))
        f["vol_of_vol"] = stdev(rv_series) / (mean(rv_series) + 1e-12) if rv_series else 0.0
        _register("vol_of_vol")

        # ATR normalisation — every price-distance feature below is in ATR units,
        # which makes the model transferable across gold's $1200 -> $3000+ history.
        f["atr_ratio_14_50"] = a14 / a50
        _register("atr_ratio_14_50")

        # ---- P4: compression / expansion ------------------------------------
        ranges = [b.range for b in h[-self.lookback_long:]]
        cur_r = last.range
        f["range_pctile"] = _pctile_rank(ranges, cur_r)
        # NR-N: how many of the last 20 bars had a narrower range than the last bar?
        last20 = [b.range for b in h[-20:]]
        f["nr_rank"] = sum(1 for r in last20 if r < cur_r) / max(len(last20), 1)
        # Squeeze: current 20-bar high-low envelope vs its own 100-bar norm.
        env20 = max(b.high for b in h[-20:]) - min(b.low for b in h[-20:])
        env100 = max(b.high for b in h[-100:]) - min(b.low for b in h[-100:])
        f["squeeze"] = env20 / (env100 + 1e-9)
        _register("range_pctile", "nr_rank", "squeeze")

        # ---- P2: session and calendar ---------------------------------------
        # The bar being predicted is bars[i]; its TIMESTAMP is known in advance
        # (it is a calendar fact, not price data), so using it is not lookahead.
        target_ts = bars[i].ts if i < len(bars) else last.ts
        sess = session_of(target_ts)
        for s in Session:
            f[f"sess_{s.value}"] = 1.0 if sess == s else 0.0
        _register(*[f"sess_{s.value}" for s in Session])

        hh = target_ts.hour + target_ts.minute / 60.0
        f["hour_sin"] = math.sin(2 * math.pi * hh / 24.0)
        f["hour_cos"] = math.cos(2 * math.pi * hh / 24.0)
        f["dow"] = target_ts.weekday() / 6.0
        _register("hour_sin", "hour_cos", "dow")

        # Session-relative position: where are we inside the current session's range?
        sess_bars = [b for b in h[-48:] if session_of(b.ts) == sess]
        if len(sess_bars) >= 2:
            sh = max(b.high for b in sess_bars)
            sl = min(b.low for b in sess_bars)
            f["sess_pos"] = (last.close - sl) / (sh - sl + 1e-9)
            f["sess_range_atr"] = (sh - sl) / a14
        else:
            f["sess_pos"], f["sess_range_atr"] = 0.5, 1.0
        _register("sess_pos", "sess_range_atr")

        # ---- P3: liquidity pools --------------------------------------------
        # Distance to prior N-bar extremes, in ATR. Small positive = stops nearby.
        for n in (20, 60):
            hi = max(b.high for b in h[-n:])
            lo = min(b.low for b in h[-n:])
            f[f"dist_hi_{n}"] = (hi - last.close) / a14
            f[f"dist_lo_{n}"] = (last.close - lo) / a14
        _register("dist_hi_20", "dist_lo_20", "dist_hi_60", "dist_lo_60")

        # Sweep detection: did the last bar poke through a prior extreme and
        # close back inside? This is the highest-value single pattern in gold.
        prev_hi = max(b.high for b in h[-21:-1]) if len(h) > 21 else last.high
        prev_lo = min(b.low for b in h[-21:-1]) if len(h) > 21 else last.low
        f["sweep_high"] = 1.0 if (last.high > prev_hi and last.close < prev_hi) else 0.0
        f["sweep_low"] = 1.0 if (last.low < prev_lo and last.close > prev_lo) else 0.0
        f["sweep_depth"] = (max(0.0, last.high - prev_hi) + max(0.0, prev_lo - last.low)) / a14
        _register("sweep_high", "sweep_low", "sweep_depth")

        # Round-number magnetism: gold respects $10 and $25 handles.
        for step in (10.0, 25.0):
            d = min(last.close % step, step - (last.close % step))
            f[f"round_{int(step)}"] = d / step          # 0 = on the handle, .5 = midway
        _register("round_10", "round_25")

        # ---- candle microstructure ------------------------------------------
        rng = last.range + 1e-9
        f["body_frac"] = last.body / rng
        f["upper_wick_frac"] = last.upper_wick / rng
        f["lower_wick_frac"] = last.lower_wick / rng
        f["close_loc"] = (last.close - last.low) / rng    # 1 = closed on high
        _register("body_frac", "upper_wick_frac", "lower_wick_frac", "close_loc")

        # Wick asymmetry over 5 bars: sustained rejection from one side.
        uw = sum(b.upper_wick for b in h[-5:])
        lw = sum(b.lower_wick for b in h[-5:])
        f["wick_skew_5"] = (lw - uw) / (lw + uw + 1e-9)
        _register("wick_skew_5")

        # ---- momentum (kept deliberately small, see module docstring) --------
        for n in (3, 10, 30):
            f[f"mom_{n}"] = logret(h[-n].close, last.close) / (a14 / last.close + 1e-12)
        _register("mom_3", "mom_10", "mom_30")

        # Signed-return autocorrelation over the recent window. On gold this
        # hovers near zero — the feature exists so the model can LEARN that,
        # rather than us assuming momentum works.
        rets20 = [logret(h[j - 1].close, h[j].close) for j in range(len(h) - 20, len(h))]
        f["ac1_20"] = _autocorr1(rets20)
        _register("ac1_20")

        # Consecutive same-direction closes (run length), signed.
        run = 0
        for j in range(len(h) - 1, 0, -1):
            s = sign(h[j].close - h[j - 1].close)
            if run == 0:
                run = s
            elif sign(run) == s and s != 0:
                run += s
            else:
                break
        f["run_len"] = clamp(run / 5.0, -2.0, 2.0)
        _register("run_len")

        # ---- gap structure ---------------------------------------------------
        f["gap_atr"] = (last.open - h[-2].close) / a14 if len(h) > 2 else 0.0
        _register("gap_atr")

        # ---- volume (if present) --------------------------------------------
        vols = [b.volume for b in h[-50:] if b.volume > 0]
        if len(vols) > 10 and last.volume > 0:
            f["vol_z"] = (last.volume - mean(vols)) / (stdev(vols) + 1e-9)
            f["vol_trend"] = mean(vols[-5:]) / (mean(vols) + 1e-9)
        else:
            f["vol_z"], f["vol_trend"] = 0.0, 1.0
        _register("vol_z", "vol_trend")

        return FeatureVector(values=f, ts_index=i)


def _pctile_rank(xs: Sequence[float], v: float) -> float:
    if not xs:
        return 0.5
    return sum(1 for x in xs if x < v) / len(xs)


def _autocorr1(xs: Sequence[float]) -> float:
    if len(xs) < 3:
        return 0.0
    m = mean(xs)
    num = sum((xs[i] - m) * (xs[i - 1] - m) for i in range(1, len(xs)))
    den = sum((x - m) ** 2 for x in xs)
    return num / den if den > 0 else 0.0


# --------------------------------------------------------------------------- targets
def target_direction(bars: Sequence[Bar], i: int) -> int | None:
    """1 if bar i closes above its open, 0 otherwise. None if unavailable."""
    if i >= len(bars):
        return None
    return 1 if bars[i].close > bars[i].open else 0


def target_signed_move(bars: Sequence[Bar], i: int) -> float | None:
    """Close-to-close log return of bar i, in ATR units of the prior history."""
    if i >= len(bars) or i < 1:
        return None
    a = atr(bars[:i], 14) or 1e-9
    return (bars[i].close - bars[i - 1].close) / a


def target_range(bars: Sequence[Bar], i: int) -> float | None:
    """Bar i's true range in ATR units of prior history. This is the target the
    market actually lets you predict."""
    if i >= len(bars) or i < 1:
        return None
    a = atr(bars[:i], 14) or 1e-9
    return true_range(bars[i - 1].close, bars[i]) / a
