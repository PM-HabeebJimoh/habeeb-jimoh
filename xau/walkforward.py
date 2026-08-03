"""XAU-Q walk-forward engine.

Anchored-origin walk-forward with a purge gap. Three disjoint blocks slide
forward through time:

    [========== TRAIN ==========][PURGE][== CALIB ==][PURGE][= TEST =]
                                                              ^ predictions
                                                                collected here

  TRAIN  fits the classifier / ridge.
  CALIB  fits isotonic calibration, the abstention threshold, and the conformal
         quantile. This block MUST be separate from TRAIN or the conformal
         guarantee is void and the threshold is overfit.
  PURGE  discards bars adjacent to a boundary so that overlapping feature
         windows cannot leak information across the split.
  TEST   never touched by anything except final scoring.

Nothing is ever refit on test data. The origin advances by the test width, so
every test bar is predicted exactly once, out-of-sample, by a model that only
saw strictly older data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

from .core import Bar, atr, clamp, mean, wilson_interval


def clamp_scale(x: float) -> float:
    """Bound the adaptive component of the conformal scale to [0.5, 2.0]."""
    return clamp(x, 0.5, 2.0)
from .features import (
    FEATURE_NAMES, FeatureBuilder, target_direction, target_range,
)
from .model import (
    ConformalInterval, IsotonicCalibrator, LogisticModel, OnlineScaler,
    RidgeModel, SelectiveClassifier, accuracy_coverage_curve, brier_score,
    log_loss, reliability_table,
)


@dataclass
class Prediction:
    index: int
    ts: str
    session: str
    p_up_raw: float
    p_up: float                # calibrated
    decision: int | None       # 1 up, 0 down, None abstain
    actual_dir: int
    range_pred: float          # in ATR units
    range_lo: float
    range_hi: float
    range_actual: float
    atr_at_pred: float
    close_prev: float
    high_lo: float = 0.0       # absolute-price OHLC band
    high_hi: float = 0.0
    low_lo: float = 0.0
    low_hi: float = 0.0
    actual_high: float = 0.0
    actual_low: float = 0.0


@dataclass
class WalkForwardResult:
    predictions: list[Prediction] = field(default_factory=list)
    folds: int = 0
    feature_names: list[str] = field(default_factory=list)
    coef_history: list[dict[str, float]] = field(default_factory=list)

    # ---------------------------------------------------------------- metrics
    def direction_metrics(self) -> dict:
        y = [p.actual_dir for p in self.predictions]
        ph = [p.p_up for p in self.predictions]
        if not y:
            return {}
        pred_all = [1 if p >= 0.5 else 0 for p in ph]
        acc = mean([1.0 if a == b else 0.0 for a, b in zip(pred_all, y)])
        k = sum(1 for a, b in zip(pred_all, y) if a == b)
        ci = wilson_interval(k, len(y))
        base = max(mean([float(v) for v in y]), 1 - mean([float(v) for v in y]))
        return {
            "n": len(y),
            "accuracy_all_bars": acc,
            "ci95": ci,
            "majority_class_baseline": base,
            "edge_over_baseline": acc - base,
            "brier": brier_score(ph, y),
            "log_loss": log_loss(ph, y),
            "curve": accuracy_coverage_curve(ph, y),
            "reliability": reliability_table(ph, y),
        }

    def range_metrics(self, target_coverage: float = 0.85) -> dict:
        preds = self.predictions
        if not preds:
            return {}
        inside = [1.0 if p.range_lo <= p.range_actual <= p.range_hi else 0.0 for p in preds]
        cov = mean(inside)
        k = int(sum(inside))
        errs = [abs(p.range_pred - p.range_actual) for p in preds]
        widths = [p.range_hi - p.range_lo for p in preds]
        naive = [abs(1.0 - p.range_actual) for p in preds]   # naive: range == ATR
        return {
            "n": len(preds),
            "target_coverage": target_coverage,
            "empirical_coverage": cov,
            "ci95": wilson_interval(k, len(preds)),
            "mae_atr": mean(errs),
            "naive_mae_atr": mean(naive),
            "skill_vs_naive": 1.0 - (mean(errs) / (mean(naive) + 1e-12)),
            "mean_width_atr": mean(widths),
        }

    def ohlc_band_metrics(self) -> dict:
        preds = [p for p in self.predictions if p.actual_high > 0]
        if not preds:
            return {}
        hin = mean([1.0 if p.high_lo <= p.actual_high <= p.high_hi else 0.0 for p in preds])
        lin = mean([1.0 if p.low_lo <= p.actual_low <= p.low_hi else 0.0 for p in preds])
        both = mean([
            1.0 if (p.high_lo <= p.actual_high <= p.high_hi
                    and p.low_lo <= p.actual_low <= p.low_hi) else 0.0
            for p in preds
        ])
        return {
            "n": len(preds),
            "high_coverage": hin,
            "low_coverage": lin,
            "joint_coverage": both,
            "mean_high_band_usd": mean([p.high_hi - p.high_lo for p in preds]),
            "mean_low_band_usd": mean([p.low_hi - p.low_lo for p in preds]),
        }

    def by_session(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for s in {p.session for p in self.predictions}:
            sub = [p for p in self.predictions if p.session == s]
            y = [p.actual_dir for p in sub]
            pred = [1 if p.p_up >= 0.5 else 0 for p in sub]
            k = sum(1 for a, b in zip(pred, y) if a == b)
            rin = sum(1 for p in sub if p.range_lo <= p.range_actual <= p.range_hi)
            out[s] = {
                "n": len(sub),
                "dir_accuracy": k / len(sub) if sub else 0.0,
                "dir_ci95": wilson_interval(k, len(sub)),
                "range_coverage": rin / len(sub) if sub else 0.0,
            }
        return out


def run_walkforward(
    bars: Sequence[Bar],
    train: int = 3000,
    calib: int = 750,
    test: int = 250,
    purge: int = 30,
    alpha: float = 0.15,
    target_acc: float = 0.85,
    builder: FeatureBuilder | None = None,
    progress: Callable[[int, int], None] | None = None,
) -> WalkForwardResult:
    fb = builder or FeatureBuilder()
    res = WalkForwardResult(feature_names=list(FEATURE_NAMES))

    # Precompute all feature vectors once. Each reads only bars[:i], so this is
    # not lookahead — it is just caching.
    feats: dict[int, list[float]] = {}
    dirs: dict[int, int] = {}
    rngs: dict[int, float] = {}
    warm = fb.warmup
    for i in range(warm, len(bars)):
        fv = fb.at(bars, i)
        if fv is None:
            continue
        if not res.feature_names:
            res.feature_names = list(FEATURE_NAMES)
        feats[i] = fv.as_list(res.feature_names)
        d = target_direction(bars, i)
        r = target_range(bars, i)
        if d is None or r is None:
            continue
        dirs[i], rngs[i] = d, r

    idxs = sorted(feats.keys())
    if not idxs:
        return res
    span = train + purge + calib + purge + test
    if len(idxs) < span:
        raise ValueError(
            f"need at least {span} usable bars after warmup, have {len(idxs)}"
        )

    start = 0
    total_folds = max(1, (len(idxs) - span) // test + 1)
    while start + span <= len(idxs):
        tr = idxs[start: start + train]
        ca = idxs[start + train + purge: start + train + purge + calib]
        te_lo = start + train + purge + calib + purge
        te = idxs[te_lo: te_lo + test]
        if not te:
            break

        nf = len(res.feature_names)
        scaler = OnlineScaler(nf)
        for i in tr:
            scaler.update(feats[i])

        Xtr = [scaler.transform(feats[i]) for i in tr]
        ytr = [dirs[i] for i in tr]
        rtr = [rngs[i] for i in tr]

        clf = LogisticModel(n_features=nf, l2=2e-3, lr=0.03, epochs=18).fit(Xtr, ytr)
        rid = RidgeModel(n_features=nf, l2=8.0).fit(Xtr, rtr)

        # ---- calibration block ------------------------------------------
        Xca = [scaler.transform(feats[i]) for i in ca]
        yca = [dirs[i] for i in ca]
        rca = [rngs[i] for i in ca]
        pca_raw = [clf.predict_proba(x) for x in Xca]

        iso = IsotonicCalibrator().fit(pca_raw, yca)
        pca = [iso.transform(p) for p in pca_raw]

        sel = SelectiveClassifier()
        sel.fit_threshold(pca, yca, target_acc=target_acc)

        rca_pred = [rid.predict(x) for x in Xca]
        # Adaptive scale: recent realised range volatility, so intervals breathe.
        # Conformal scale. Normalising by the point prediction (max(0.35,|pred|))
        # makes intervals adaptive, but it also makes the normalised residual
        # non-exchangeable whenever the point model's error is not proportional
        # to its own prediction. Measured on July 2026 H1 that cost 5 points of
        # coverage (79.8% vs an 85% target) while a constant scale delivered
        # 83.4%. We therefore blend: mostly constant, lightly adaptive, and the
        # blend weight is capped so a bad point prediction cannot distort the
        # divisor. See BACKTEST_JULY_2026.md section 4.
        _cal_scale = mean([abs(p) for p in rca_pred]) or 1.0
        sca = [0.75 + 0.25 * clamp_scale(abs(p) / _cal_scale) for p in rca_pred]
        conf = ConformalInterval(alpha=alpha).calibrate(rca, rca_pred, sca)

        res.coef_history.append(
            {n: w for n, w in zip(res.feature_names, clf.w)}
        )

        # ---- test block ---------------------------------------------------
        for i in te:
            x = scaler.transform(feats[i])
            praw = clf.predict_proba(x)
            p = iso.transform(praw)
            rp = rid.predict(x)
            s = 0.75 + 0.25 * clamp_scale(abs(rp) / _cal_scale)
            lo, hi = conf.interval(rp, s)
            lo = max(0.0, lo)

            a = atr(bars[:i], 14) or 1e-9
            prev_c = bars[i - 1].close
            b = bars[i]

            # Convert the ATR-unit range band into absolute high/low bands,
            # anchored on the previous close and tilted by direction probability.
            tilt = (p - 0.5) * 2.0
            mid_hi = prev_c + a * rp * (0.5 + 0.25 * tilt)
            mid_lo = prev_c - a * rp * (0.5 - 0.25 * tilt)
            half = a * (hi - lo) / 2.0

            res.predictions.append(Prediction(
                index=i, ts=b.ts.isoformat(),
                session=__import__("xau.core", fromlist=["session_of"]).session_of(b.ts).value,
                p_up_raw=praw, p_up=p,
                decision=sel.decide(p),
                actual_dir=dirs[i],
                range_pred=rp, range_lo=lo, range_hi=hi,
                range_actual=rngs[i],
                atr_at_pred=a, close_prev=prev_c,
                high_lo=mid_hi - half, high_hi=mid_hi + half,
                low_lo=mid_lo - half, low_hi=mid_lo + half,
                actual_high=b.high, actual_low=b.low,
            ))

        res.folds += 1
        if progress:
            progress(res.folds, total_folds)
        start += test

    return res
