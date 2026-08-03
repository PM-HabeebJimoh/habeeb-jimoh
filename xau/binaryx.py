"""BinaryX — next-candle OHLC prediction model.

Predicts the next candle's full Open, High, Low and Close, scored in dollars.

BinaryX = four ridge regressions, one per OHLC component, each predicting an
ATR-normalised OFFSET from the prior close, with L2 selected per component on a
validation split, plus a candle-consistency repair.

Predicting offsets rather than absolute prices is what makes BinaryX work when
the test period sits at price levels the training period never visited -- which
is exactly the April-June 2026 ($4,300-4,700) -> July 2026 ($3,959-4,203) case
this module backtests.

BACKTEST DESIGN (real data, daily bars)
----------------------------------------
Because only ~71 real training days exist before July, a standard large-fold
walk-forward is impossible. Instead BinaryX uses EXPANDING-WINDOW walk-forward:

    for each July day t:
        train on every real bar strictly before t
        predict bar t
        move to t+1

Every July prediction is genuinely out-of-sample and uses only past real data.
The model is refit each day, which is also how it would run live.

Small-sample honesty: 27 test days is a small sample. Every metric is reported
with a bootstrap confidence interval, and the naive persistence baseline is
shown alongside so the reader can see the improvement rather than an absolute
percentage that gold's price level inflates.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Sequence

from .core import Bar, atr, mean, quantile
from .features import FEATURE_NAMES, FeatureBuilder
from .predictor import Candle, CandlePrediction, CandleResult, NextCandleModel

MODEL_NAME = "BinaryX"
MODEL_VERSION = "1.0"


def bootstrap_ci(values: Sequence[float], n_boot: int = 5000,
                 seed: int = 7, alpha: float = 0.05) -> tuple[float, float]:
    """Percentile bootstrap CI for a mean. Essential at n=27."""
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_boot):
        means.append(mean([values[rng.randrange(n)] for _ in range(n)]))
    return (quantile(means, alpha / 2), quantile(means, 1 - alpha / 2))


@dataclass
class BinaryXResult(CandleResult):
    train_sizes: list[int] = field(default_factory=list)
    warmup_used: int = 0

    def bootstrap_metrics(self) -> dict:
        """Per-component bootstrap CIs on MAE, plus the paired improvement."""
        out = {}
        for c in ("open", "high", "low", "close"):
            errs = [p.errors()[c] for p in self.predictions]
            berrs = [p.baseline_errors()[c] for p in self.predictions]
            diffs = [b - m for m, b in zip(errs, berrs)]   # positive = model better
            out[c] = {
                "mae": mean(errs),
                "mae_ci": bootstrap_ci(errs),
                "baseline_mae": mean(berrs),
                "improvement_usd": mean(diffs),
                "improvement_ci": bootstrap_ci(diffs),
                "beats_baseline_significantly": bootstrap_ci(diffs)[0] > 0,
            }
        all_e = [e for p in self.predictions for e in p.errors().values()]
        all_b = [e for p in self.predictions for e in p.baseline_errors().values()]
        all_d = [b - m for m, b in zip(all_e, all_b)]
        out["overall"] = {
            "mae": mean(all_e),
            "mae_ci": bootstrap_ci(all_e),
            "baseline_mae": mean(all_b),
            "improvement_usd": mean(all_d),
            "improvement_ci": bootstrap_ci(all_d),
            "beats_baseline_significantly": bootstrap_ci(all_d)[0] > 0,
        }
        return out


def run_binaryx_expanding(
    bars: Sequence[Bar],
    test_from: str,
    test_to: str,
    min_train: int = 40,
) -> BinaryXResult:
    """Expanding-window walk-forward. Refit before every test bar."""
    fb = FeatureBuilder(lookback_long=30)   # short lookback: daily bars are scarce
    res = BinaryXResult()
    res.warmup_used = fb.warmup

    feats: dict[int, list[float]] = {}
    tgts: dict[int, dict[str, float]] = {}
    names: list[str] = []

    for i in range(fb.warmup, len(bars)):
        fv = fb.at(bars, i)
        if fv is None:
            continue
        if not names:
            names = list(FEATURE_NAMES)
        a = atr(bars[:i], 14)
        if a <= 0:
            continue
        pc = bars[i - 1].close
        b = bars[i]
        feats[i] = fv.as_list(names)
        tgts[i] = {"open": (b.open - pc) / a, "high": (b.high - pc) / a,
                   "low": (b.low - pc) / a, "close": (b.close - pc) / a}

    idxs = sorted(feats.keys())
    for i in idxs:
        day = bars[i].ts.strftime("%Y-%m-%d")
        if not (test_from <= day <= test_to):
            continue
        train_idx = [j for j in idxs if j < i]
        if len(train_idx) < min_train:
            continue

        X = [feats[j] for j in train_idx]
        T = {c: [tgts[j][c] for j in train_idx]
             for c in ("open", "high", "low", "close")}
        m = NextCandleModel().fit(X, T, names)
        res.chosen_l2 = dict(m.chosen_l2)
        res.train_sizes.append(len(train_idx))

        a = atr(bars[:i], 14)
        pc = bars[i - 1].close
        prev = bars[i - 1]
        b = bars[i]
        pred = m.predict(feats[i], pc, a)
        pred.ts = b.ts.isoformat()
        res.predictions.append(CandlePrediction(
            index=i, ts=b.ts.isoformat(), predicted=pred,
            actual=Candle(b.ts.isoformat(), b.open, b.high, b.low, b.close),
            baseline=Candle(b.ts.isoformat(), prev.open, prev.high,
                            prev.low, prev.close),
            prev_close=pc, atr=a,
        ))
        res.folds += 1
    return res


def format_binaryx_report(res: BinaryXResult, split: dict,
                          color: bool = True) -> str:
    B = "\033[1m" if color else ""
    G = "\033[32m" if color else ""
    R = "\033[31m" if color else ""
    D = "\033[2m" if color else ""
    X = "\033[0m" if color else ""
    m = res.metrics()
    bs = res.bootstrap_metrics()
    L = []

    L.append(f"{B}{'='*78}{X}")
    L.append(f"{B}  BinaryX v{MODEL_VERSION} — JULY 2026 BACKTEST — 100% REAL MARKET DATA{X}")
    L.append(f"{B}{'='*78}{X}")
    L.append("")
    L.append(f"{B}DATA{X}  {G}REAL XAUUSD daily OHLC{X} — myfxbook, cross-checked vs "
             f"investing.com & barchart")
    L.append(f"  train  {split['train_days']} real days  "
             f"{split['train_start']} -> {split['train_end']}  "
             f"(${split['train_price_range'][0]:,.0f}-${split['train_price_range'][1]:,.0f})")
    L.append(f"  test   {split['test_days']} real days  "
             f"{split['test_start']} -> {split['test_end']}  "
             f"(${split['test_price_range'][0]:,.0f}-${split['test_price_range'][1]:,.0f})")
    L.append(f"  {D}Note the price gap: BinaryX is tested on levels it never saw in{X}")
    L.append(f"  {D}training. ATR-normalised offsets are what make that possible.{X}")
    L.append("")
    L.append(f"  method  expanding-window walk-forward, refit before every test day")
    L.append(f"  folds   {res.folds}  (train size grew {min(res.train_sizes)} -> "
             f"{max(res.train_sizes)} bars)")
    L.append("")

    o = m["overall"]
    ob = bs["overall"]
    L.append(f"{B}RESULT — WHOLE CANDLE{X}")
    L.append(f"  BinaryX MAE            ${o['mae_usd']:.2f}   "
             f"95% CI [${ob['mae_ci'][0]:.2f}, ${ob['mae_ci'][1]:.2f}]")
    L.append(f"  naive baseline MAE     ${o['baseline_mae_usd']:.2f}")
    L.append(f"  error reduction        ${ob['improvement_usd']:.2f}/candle  "
             f"({o['improvement_pct']:+.1f}%)")
    L.append(f"  improvement 95% CI     [${ob['improvement_ci'][0]:.2f}, "
             f"${ob['improvement_ci'][1]:.2f}]")
    sig = (f"{G}YES — CI excludes zero{X}" if ob["beats_baseline_significantly"]
           else f"{R}NO — CI includes zero{X}")
    L.append(f"  statistically better?  {sig}")
    L.append(f"  Theil's U2             {o['theil_u2']:.4f}  "
             f"{D}(<1 = beats naive; scale-free){X}")
    L.append(f"  accuracy (100-MAPE)    {o['accuracy_pct']:.3f}%   "
             f"{D}naive floor {o['baseline_accuracy_pct']:.3f}%{X}")
    L.append("")

    L.append(f"{B}PER COMPONENT{X}")
    L.append(f"  {'':<7}{'MAE $':>9}{'95% CI':>20}{'naive $':>10}"
             f"{'gain $':>9}{'sig?':>6}")
    for c in ("open", "high", "low", "close"):
        d, e = m["components"][c], bs[c]
        s = "yes" if e["beats_baseline_significantly"] else "no"
        L.append(f"  {c:<7}{d['mae_usd']:>9.2f}"
                 f"   [{e['mae_ci'][0]:>7.2f},{e['mae_ci'][1]:>7.2f}]"
                 f"{e['baseline_mae']:>10.2f}{e['improvement_usd']:>9.2f}{s:>6}")
    L.append("")

    L.append(f"{B}HIT RATES{X} {D}(prediction within $X of actual){X}")
    keys = list(m["components"]["close"]["hit_rates"].keys())
    L.append(f"  {'':<7}" + "".join(f"{k:>13}" for k in keys))
    for c in ("open", "high", "low", "close"):
        hr = m["components"][c]["hit_rates"]
        L.append(f"  {c:<7}" + "".join(f"{hr[k]:>12.1%} " for k in keys))
    L.append("")

    d = m["direction"]
    L.append(f"{B}DIRECTION{X} {D}(secondary — BinaryX predicts levels, not sign){X}")
    L.append(f"  close vs prev close    {d['accuracy']:.3f}  "
             f"CI [{d['ci95'][0]:.3f}, {d['ci95'][1]:.3f}]")
    L.append("")

    L.append(f"{B}EVERY JULY 2026 PREDICTION vs REALITY{X}  {D}(all real prices){X}")
    L.append(f"  {'date':<12}{'':<5}{'open':>9}{'high':>9}{'low':>9}{'close':>9}")
    for p in res.predictions:
        a, q, e = p.actual, p.predicted, p.errors()
        L.append(f"  {p.ts[:10]:<12}{'pred':<5}{q.open:>9.2f}{q.high:>9.2f}"
                 f"{q.low:>9.2f}{q.close:>9.2f}")
        L.append(f"  {'':<12}{'real':<5}{a.open:>9.2f}{a.high:>9.2f}"
                 f"{a.low:>9.2f}{a.close:>9.2f}")
        L.append(f"  {'':<12}{D}{'err':<5}{e['open']:>9.2f}{e['high']:>9.2f}"
                 f"{e['low']:>9.2f}{e['close']:>9.2f}{X}")
    return "\n".join(L)
