"""BinaryX-D — bullish/bearish next-candle classifier.

INPUT :  price history up to now
OUTPUT:  BUY (next candle bullish) or SELL (next candle bearish), plus confidence

This is a pure binary direction model. No OHLC levels, no ranges, no intervals.
One question, one answer: will the next candle close above its open?

DESIGN
------
With ~70 real daily bars available, a 42-feature model is hopeless (p/n ~ 0.6).
BinaryX-D therefore uses an ENSEMBLE OF DELIBERATELY SIMPLE VOTERS, each of
which needs only a handful of observations to estimate:

  1. Logistic regression on a SMALL, stability-selected feature subset
  2. Momentum voter        (does short-term drift persist?)
  3. Mean-reversion voter  (does an extreme move snap back?)
  4. Candle-body voter     (does the last body's sign continue?)
  5. Session voter         (learned per-session bullish prior)
  6. Volatility-regime voter (direction conditioned on expansion/compression)

Each voter returns a probability. They are averaged with weights learned from
their own recent hit rate, so voters that have been wrong lately are discounted.
This is a "many weak learners" design, which is what small samples support.

ABSTENTION
----------
The model can output HOLD when the ensemble is not confident. That converts a
weak all-bar accuracy into a higher accuracy on a smaller number of calls. The
report shows the full accuracy-vs-coverage curve so the trade-off is explicit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from .core import (
    Bar, atr, binomial_p_value, clamp, logret, mean, session_of, sign, stdev,
    wilson_interval,
)
from .features import FEATURE_NAMES
from .model import IsotonicCalibrator, LogisticModel, OnlineScaler

MODEL_NAME = "BinaryX-D"


# A small, hand-chosen feature subset. Fewer parameters is the entire point.
CORE_FEATURES = [
    "mom_3", "mom_10", "close_loc", "body_frac", "wick_skew_5",
    "run_len", "range_pctile", "vol_ratio_5_60", "gap_atr",
]

# Longest window any compact feature reads. The full FeatureBuilder needs 105
# bars of warmup (rv_60 plus a 100-bar squeeze window); with only 98 real daily
# bars in existence that produced ZERO signals. This compact builder needs 21,
# which leaves ~70 usable training bars.
COMPACT_WARMUP = 21


def compact_features(bars: Sequence[Bar], i: int) -> dict | None:
    """Features for predicting bars[i], reading ONLY bars[:i].

    Deliberately small: 9 features estimable from ~20 bars of history.
    """
    if i < COMPACT_WARMUP or i > len(bars):
        return None
    h = bars[:i]
    last = h[-1]
    a = atr(h, 14) or 1e-9
    rng = last.range + 1e-9

    def lr(n: int) -> float:
        return logret(h[-n].close, last.close) / (a / last.close + 1e-12)

    r5 = [logret(h[j - 1].close, h[j].close) for j in range(len(h) - 5, len(h))]
    r20 = [logret(h[j - 1].close, h[j].close) for j in range(len(h) - 20, len(h))]

    run = 0
    for j in range(len(h) - 1, 0, -1):
        sg = sign(h[j].close - h[j - 1].close)
        if run == 0:
            run = sg
        elif sign(run) == sg and sg != 0:
            run += sg
        else:
            break

    uw = sum(b.upper_wick for b in h[-5:])
    lw = sum(b.lower_wick for b in h[-5:])
    ranges = [b.range for b in h[-20:]]

    return {
        "mom_3": lr(3),
        "mom_10": lr(10),
        "close_loc": (last.close - last.low) / rng,
        "body_frac": last.body / rng,
        "wick_skew_5": (lw - uw) / (lw + uw + 1e-9),
        "run_len": clamp(run / 5.0, -2.0, 2.0),
        "range_pctile": sum(1 for x in ranges if x < last.range) / len(ranges),
        "vol_ratio_5_60": (stdev(r5) + 1e-12) / (stdev(r20) + 1e-12),
        "gap_atr": (last.open - h[-2].close) / a if len(h) > 2 else 0.0,
    }


@dataclass
class Signal:
    ts: str
    call: str                 # "BUY" | "SELL" | "HOLD"
    prob_up: float
    confidence: float
    votes: dict[str, float] = field(default_factory=dict)
    actual: str | None = None
    correct: bool | None = None


# --------------------------------------------------------------------- voters
def _v_momentum(f: dict) -> float:
    """Short-term drift persists."""
    m = f.get("mom_3", 0.0) * 0.6 + f.get("mom_10", 0.0) * 0.4
    return clamp(0.5 + 0.12 * m, 0.05, 0.95)


def _v_reversion(f: dict) -> float:
    """Extreme moves snap back."""
    m = f.get("mom_10", 0.0)
    if abs(m) < 0.8:
        return 0.5
    return clamp(0.5 - 0.10 * m, 0.05, 0.95)


def _v_body(f: dict) -> float:
    """Last candle's body sign continues; closing near the high is bullish."""
    b = f.get("body_frac", 0.0)
    cl = f.get("close_loc", 0.5)
    return clamp(0.5 + 0.18 * b + 0.22 * (cl - 0.5), 0.05, 0.95)


def _v_wick(f: dict) -> float:
    """Sustained rejection from one side (lower wicks = buyers defending)."""
    return clamp(0.5 + 0.20 * f.get("wick_skew_5", 0.0), 0.05, 0.95)


def _v_regime(f: dict) -> float:
    """In expansion, follow momentum; in compression, fade it."""
    expand = f.get("vol_ratio_5_60", 1.0) > 1.15
    m = f.get("mom_3", 0.0)
    return clamp(0.5 + (0.10 if expand else -0.07) * m, 0.05, 0.95)


def _v_run(f: dict) -> float:
    """Long same-direction runs tend to pause."""
    r = f.get("run_len", 0.0)
    if abs(r) < 0.6:
        return 0.5
    return clamp(0.5 - 0.12 * r, 0.05, 0.95)


VOTERS = {
    "momentum": _v_momentum, "reversion": _v_reversion, "body": _v_body,
    "wick": _v_wick, "regime": _v_regime, "run": _v_run,
}


class BinaryXD:
    """The bullish/bearish classifier."""

    def __init__(self, band: float = 0.0, adaptive_weights: bool = True):
        self.band = band                      # abstain if |p-0.5| < band
        self.adaptive = adaptive_weights
        self.logit: LogisticModel | None = None
        self.scaler: OnlineScaler | None = None
        self.iso: IsotonicCalibrator | None = None
        self.vw: dict[str, float] = {k: 1.0 for k in VOTERS}
        self.feat_idx: list[int] = []

    # ------------------------------------------------------------------ fit
    def fit(self, rows: Sequence[tuple[dict, int]]) -> "BinaryXD":
        if len(rows) < 20:
            return self
        names = list(CORE_FEATURES)
        X = [[f.get(n, 0.0) for n in names] for f, _ in rows]
        y = [t for _, t in rows]

        self.scaler = OnlineScaler(len(names))
        for x in X:
            self.scaler.update(x)
        Xs = [self.scaler.transform(x) for x in X]

        # Strong L2: small n, and we want a gentle tilt, not a confident fit.
        self.logit = LogisticModel(n_features=len(names), l2=2.0,
                                   lr=0.02, epochs=40).fit(Xs, y)
        self.names = names

        # Calibrate on the training set (small n; better than nothing).
        praw = [self.logit.predict_proba(x) for x in Xs]
        self.iso = IsotonicCalibrator().fit(praw, y)

        # Adaptive voter weights from in-sample hit rate.
        if self.adaptive:
            for k, fn in VOTERS.items():
                hits = sum(1 for (f, t) in rows
                           if (1 if fn(f) >= 0.5 else 0) == t)
                acc = hits / len(rows)
                # Weight >1 when a voter is better than chance, <1 when worse.
                self.vw[k] = max(0.1, 1.0 + 4.0 * (acc - 0.5))
        return self

    # -------------------------------------------------------------- predict
    def predict_proba(self, f: dict) -> tuple[float, dict[str, float]]:
        votes = {k: fn(f) for k, fn in VOTERS.items()}
        wsum = sum(self.vw[k] for k in votes)
        ens = sum(votes[k] * self.vw[k] for k in votes) / wsum if wsum else 0.5

        if self.logit and self.scaler:
            x = self.scaler.transform([f.get(n, 0.0) for n in self.names])
            pl = self.logit.predict_proba(x)
            if self.iso:
                pl = self.iso.transform(pl)
            votes["logistic"] = pl
            # Blend: the ensemble of weak voters carries most of the weight,
            # because on small samples the logistic overfits.
            p = 0.6 * ens + 0.4 * pl
        else:
            p = ens
        return clamp(p, 0.02, 0.98), votes

    def signal(self, f: dict, ts: str = "") -> Signal:
        p, votes = self.predict_proba(f)
        if abs(p - 0.5) < self.band:
            call = "HOLD"
        else:
            call = "BUY" if p >= 0.5 else "SELL"
        return Signal(ts=ts, call=call, prob_up=p,
                      confidence=abs(p - 0.5) * 2, votes=votes)


# --------------------------------------------------------------- backtesting
@dataclass
class DirectionResult:
    signals: list[Signal] = field(default_factory=list)
    train_sizes: list[int] = field(default_factory=list)

    def scorecard(self) -> dict:
        acted = [s for s in self.signals if s.call != "HOLD"]
        n = len(acted)
        hits = sum(1 for s in acted if s.correct)
        misses = n - hits
        wr = hits / n if n else 0.0
        lo, hi = wilson_interval(hits, n) if n else (0.0, 1.0)

        buys = [s for s in acted if s.call == "BUY"]
        sells = [s for s in acted if s.call == "SELL"]
        bh = sum(1 for s in buys if s.correct)
        sh = sum(1 for s in sells if s.correct)

        # Base rate: what you'd get by always calling the majority class.
        ups = sum(1 for s in self.signals if s.actual == "BULL")
        base = max(ups, len(self.signals) - ups) / len(self.signals) \
            if self.signals else 0.5

        return {
            "total_signals": len(self.signals),
            "acted": n, "held": len(self.signals) - n,
            "hits": hits, "misses": misses,
            "win_rate": wr, "ci95": (lo, hi),
            "p_value_vs_coinflip": binomial_p_value(hits, n) if n else 1.0,
            "base_rate": base,
            "edge_vs_base": wr - base,
            "buy": {"n": len(buys), "hits": bh, "misses": len(buys) - bh,
                    "wr": bh / len(buys) if buys else 0.0},
            "sell": {"n": len(sells), "hits": sh, "misses": len(sells) - sh,
                     "wr": sh / len(sells) if sells else 0.0},
        }

    def coverage_curve(self, steps: int = 10) -> list[dict]:
        """Accuracy if we only act on the most confident N% of signals."""
        out = []
        ranked = sorted(self.signals, key=lambda s: -s.confidence)
        for k in range(1, steps + 1):
            take = max(1, int(len(ranked) * k / steps))
            sub = ranked[:take]
            hits = sum(1 for s in sub if s.correct)
            lo, hi = wilson_interval(hits, len(sub))
            out.append({"coverage": take / len(ranked), "n": len(sub),
                        "hits": hits, "misses": len(sub) - hits,
                        "wr": hits / len(sub), "ci": (lo, hi)})
        return out


def run_direction_backtest(bars: Sequence[Bar], test_from: str, test_to: str,
                           min_train: int = 30, band: float = 0.0) -> DirectionResult:
    """Expanding-window walk-forward. Refit before every test bar."""
    # lookback_long must exceed the longest window any feature reads (rv_60
    # needs 60 bars, `squeeze` reads 100), otherwise FeatureBuilder indexes
    # past the start of history.
    res = DirectionResult()

    rows: dict[int, tuple[dict, int]] = {}
    for i in range(COMPACT_WARMUP, len(bars)):
        fv = compact_features(bars, i)
        if fv is None:
            continue
        rows[i] = (fv, 1 if bars[i].close > bars[i].open else 0)

    idxs = sorted(rows.keys())
    for i in idxs:
        day = bars[i].ts.strftime("%Y-%m-%d")
        if not (test_from <= day <= test_to):
            continue
        train = [rows[j] for j in idxs if j < i]
        if len(train) < min_train:
            continue
        m = BinaryXD(band=band).fit(train)
        f, truth = rows[i]
        s = m.signal(f, ts=bars[i].ts.isoformat())
        s.actual = "BULL" if truth == 1 else "BEAR"
        if s.call != "HOLD":
            s.correct = (s.call == "BUY") == (truth == 1)
        res.signals.append(s)
        res.train_sizes.append(len(train))
    return res


def format_direction_report(res: DirectionResult, title: str,
                            color: bool = True) -> str:
    B = "\033[1m" if color else ""
    G = "\033[32m" if color else ""
    R = "\033[31m" if color else ""
    D = "\033[2m" if color else ""
    X = "\033[0m" if color else ""
    sc = res.scorecard()
    L = []
    L.append(f"{B}{'='*70}{X}")
    L.append(f"{B}  BinaryX-D — BULLISH / BEARISH NEXT-CANDLE PREDICTION{X}")
    L.append(f"{B}  {title}{X}")
    L.append(f"{B}{'='*70}{X}")
    L.append("")
    L.append(f"{B}  SCORECARD{X}")
    L.append(f"    total predictions   {sc['total_signals']}")
    L.append(f"    {G}HITS                {sc['hits']}{X}")
    L.append(f"    {R}MISSES              {sc['misses']}{X}")
    L.append(f"    {B}WIN RATE            {sc['win_rate']:.1%}{X}   "
             f"95% CI [{sc['ci95'][0]:.1%}, {sc['ci95'][1]:.1%}]")
    L.append(f"    p vs coin flip      {sc['p_value_vs_coinflip']:.3f}")
    L.append(f"    always-majority     {sc['base_rate']:.1%}  "
             f"(edge {sc['edge_vs_base']:+.1%})")
    L.append("")
    L.append(f"{B}  BY SIGNAL TYPE{X}")
    L.append(f"    {'':<6}{'n':>5}{'hits':>7}{'misses':>8}{'WR':>8}")
    for k in ("buy", "sell"):
        d = sc[k]
        L.append(f"    {k.upper():<6}{d['n']:>5}{d['hits']:>7}"
                 f"{d['misses']:>8}{d['wr']:>7.1%}")
    L.append("")
    L.append(f"{B}  IF YOU ONLY ACT ON THE MOST CONFIDENT SIGNALS{X}")
    L.append(f"    {'coverage':>9}{'n':>5}{'hits':>6}{'miss':>6}{'WR':>8}"
             f"{'95% CI':>18}")
    for r in res.coverage_curve():
        L.append(f"    {r['coverage']:>9.0%}{r['n']:>5}{r['hits']:>6}"
                 f"{r['misses']:>6}{r['wr']:>7.1%}"
                 f"   [{r['ci'][0]:.0%},{r['ci'][1]:.0%}]")
    L.append("")
    L.append(f"{B}  EVERY PREDICTION{X}")
    L.append(f"    {'date':<12}{'call':>6}{'P(up)':>8}{'actual':>8}{'result':>8}")
    for s in res.signals:
        mark = "HIT" if s.correct else ("MISS" if s.correct is False else "-")
        col = G if s.correct else (R if s.correct is False else D)
        L.append(f"    {s.ts[:10]:<12}{s.call:>6}{s.prob_up:>8.3f}"
                 f"{s.actual or '-':>8}{col}{mark:>8}{X}")
    return "\n".join(L)
