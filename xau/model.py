"""XAU-Q model layer: online logistic regression, isotonic calibration,
conformal interval prediction, and the SELECTIVE ABSTENTION mechanism.

WHY THIS ARCHITECTURE AND NOT A DEEP NET
-----------------------------------------
With ~10k-100k bars and ~40 features, a regularised linear model with proper
calibration beats a gradient-boosted forest or an LSTM out-of-sample on FX/metals
in the overwhelming majority of published comparisons, because the signal-to-noise
ratio is around 0.02 and everything else overfits the noise. The value here is in
the *calibration and abstention*, not the classifier.

THE 85% MECHANISM — READ THIS
------------------------------
Unconditional next-candle direction accuracy on gold is ~50-53%. That is not a
modelling failure, it is the efficient-market boundary; a system claiming 85% on
every bar is either lookahead-biased or lying.

85% IS REACHABLE ONLY AS A *CONDITIONAL, SELECTIVE* NUMBER:

  (a) DIRECTION with abstention. The model outputs a calibrated probability.
      It only fires when p is beyond a threshold learned on validation data.
      Accuracy on the fired subset rises as coverage falls. Empirically on gold
      you reach ~60-65% at ~10% coverage. 85% directional at meaningful coverage
      is NOT achievable and this package will tell you so, numerically.

  (b) RANGE / OHLC BOUNDS via conformal prediction. THIS is where 85% is real
      and provable. Instead of "will it go up", the system predicts an interval
      [low, high] for the next bar and guarantees, by construction, that the
      true value falls inside it 85% of the time. Split-conformal prediction
      gives this as a distribution-free finite-sample guarantee — it holds
      regardless of whether the underlying model is any good.

So: 85% on OHLC RANGE — yes, guaranteed and validated here.
    85% on next-candle DIRECTION — no, and I show you the measured curve instead.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Sequence

from .core import clamp, mean, quantile, stdev, wilson_interval


# --------------------------------------------------------------------------- scaler
class OnlineScaler:
    """Streaming z-score using Welford. Fit on train only, applied everywhere."""

    def __init__(self, n_features: int):
        self.n = 0
        self.mean = [0.0] * n_features
        self.m2 = [0.0] * n_features

    def update(self, x: Sequence[float]) -> None:
        self.n += 1
        for j, v in enumerate(x):
            d = v - self.mean[j]
            self.mean[j] += d / self.n
            self.m2[j] += d * (v - self.mean[j])

    def transform(self, x: Sequence[float]) -> list[float]:
        out = []
        for j, v in enumerate(x):
            var = self.m2[j] / (self.n - 1) if self.n > 1 else 1.0
            sd = math.sqrt(var) if var > 1e-12 else 1.0
            out.append(clamp((v - self.mean[j]) / sd, -6.0, 6.0))
        return out


# --------------------------------------------------------------------------- logistic
@dataclass
class LogisticModel:
    """L2-regularised logistic regression trained by AdamW-flavoured SGD.

    Pure stdlib. Deterministic given a seed. Handles ~50k x 40 in seconds.
    """

    n_features: int
    l2: float = 1e-3
    lr: float = 0.05
    epochs: int = 24
    seed: int = 7
    w: list[float] = field(default_factory=list)
    b: float = 0.0

    def __post_init__(self):
        if not self.w:
            self.w = [0.0] * self.n_features

    def _z(self, x: Sequence[float]) -> float:
        return sum(wi * xi for wi, xi in zip(self.w, x)) + self.b

    def predict_proba(self, x: Sequence[float]) -> float:
        z = clamp(self._z(x), -35.0, 35.0)
        return 1.0 / (1.0 + math.exp(-z))

    def fit(self, X: Sequence[Sequence[float]], y: Sequence[int],
            sample_weight: Sequence[float] | None = None) -> "LogisticModel":
        rng = random.Random(self.seed)
        n = len(X)
        if n == 0:
            return self
        sw = list(sample_weight) if sample_weight else [1.0] * n
        idx = list(range(n))
        m_w = [0.0] * self.n_features
        v_w = [0.0] * self.n_features
        m_b = v_b = 0.0
        b1, b2, eps = 0.9, 0.999, 1e-8
        t = 0
        for _ in range(self.epochs):
            rng.shuffle(idx)
            for i in idx:
                t += 1
                x, target, wgt = X[i], y[i], sw[i]
                p = self.predict_proba(x)
                g = (p - target) * wgt
                for j in range(self.n_features):
                    grad = g * x[j] + self.l2 * self.w[j]
                    m_w[j] = b1 * m_w[j] + (1 - b1) * grad
                    v_w[j] = b2 * v_w[j] + (1 - b2) * grad * grad
                    mh = m_w[j] / (1 - b1 ** t)
                    vh = v_w[j] / (1 - b2 ** t)
                    self.w[j] -= self.lr * mh / (math.sqrt(vh) + eps)
                m_b = b1 * m_b + (1 - b1) * g
                v_b = b2 * v_b + (1 - b2) * g * g
                self.b -= self.lr * (m_b / (1 - b1 ** t)) / (math.sqrt(v_b / (1 - b2 ** t)) + eps)
        return self


# --------------------------------------------------------------------------- ridge
@dataclass
class RidgeModel:
    """Closed-form ridge regression via normal equations + Gaussian elimination.

    Used for the range/magnitude target, which is the genuinely predictable one.
    """

    n_features: int
    l2: float = 1.0
    w: list[float] = field(default_factory=list)
    b: float = 0.0

    def fit(self, X: Sequence[Sequence[float]], y: Sequence[float]) -> "RidgeModel":
        n, d = len(X), self.n_features
        if n == 0:
            self.w = [0.0] * d
            return self
        ybar = mean(y)
        # Build (X'X + lambda I) and X'y on centred y.
        A = [[0.0] * (d + 1) for _ in range(d)]
        for i in range(n):
            xi, yi = X[i], y[i] - ybar
            for a in range(d):
                xa = xi[a]
                if xa == 0.0:
                    continue
                row = A[a]
                for bx in range(d):
                    row[bx] += xa * xi[bx]
                row[d] += xa * yi
        for a in range(d):
            A[a][a] += self.l2
        self.w = _solve(A, d)
        self.b = ybar
        return self

    def predict(self, x: Sequence[float]) -> float:
        return sum(wi * xi for wi, xi in zip(self.w, x)) + self.b


def _solve(A: list[list[float]], d: int) -> list[float]:
    """Gaussian elimination with partial pivoting on an augmented d x (d+1)."""
    for col in range(d):
        piv = max(range(col, d), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-12:
            continue
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        for r in range(d):
            if r == col:
                continue
            factor = A[r][col] / pv
            if factor == 0.0:
                continue
            for c in range(col, d + 1):
                A[r][c] -= factor * A[col][c]
    out = []
    for r in range(d):
        out.append(A[r][d] / A[r][r] if abs(A[r][r]) > 1e-12 else 0.0)
    return out


# --------------------------------------------------------------------------- calibration
class IsotonicCalibrator:
    """Pool-adjacent-violators isotonic regression, mapping raw p -> calibrated p.

    Logistic outputs on financial data are systematically overconfident. Without
    this, the abstention threshold is meaningless because p=0.7 does not mean
    70%. This is the difference between a probability and a number.
    """

    def __init__(self):
        self.x: list[float] = []
        self.y: list[float] = []

    def fit(self, probs: Sequence[float], labels: Sequence[int]) -> "IsotonicCalibrator":
        if not probs:
            return self
        pairs = sorted(zip(probs, labels))
        xs = [p for p, _ in pairs]
        ys = [float(l) for _, l in pairs]
        w = [1.0] * len(ys)
        i = 0
        while i < len(ys) - 1:
            if ys[i] <= ys[i + 1]:
                i += 1
                continue
            tw = w[i] + w[i + 1]
            ty = (ys[i] * w[i] + ys[i + 1] * w[i + 1]) / tw
            ys[i:i + 2] = [ty]
            w[i:i + 2] = [tw]
            xs[i:i + 2] = [xs[i]]
            i = max(i - 1, 0)
        self.x, self.y = xs, ys
        return self

    def transform(self, p: float) -> float:
        if not self.x:
            return p
        if p <= self.x[0]:
            return self.y[0]
        if p >= self.x[-1]:
            return self.y[-1]
        lo, hi = 0, len(self.x) - 1
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if self.x[mid] <= p:
                lo = mid
            else:
                hi = mid
        x0, x1 = self.x[lo], self.x[hi]
        y0, y1 = self.y[lo], self.y[hi]
        if x1 == x0:
            return y0
        return y0 + (y1 - y0) * (p - x0) / (x1 - x0)


# --------------------------------------------------------------------------- conformal
@dataclass
class ConformalInterval:
    """Split-conformal prediction for the next bar's range / high / low.

    THE GUARANTEE: given exchangeable calibration residuals and a target
    coverage of 1-alpha, the returned interval contains the true value with
    probability >= 1-alpha, in FINITE SAMPLES, with NO distributional assumption
    and NO assumption that the underlying point model is correct.

    This is why the 85% request is answerable for ranges but not for direction:
    here 85% is a property we impose and then verify, not a skill we claim.

    Because volatility clusters (property P1), we use NORMALISED residuals —
    dividing by a predicted scale — which makes intervals adaptive: tight in
    quiet regimes, wide in violent ones, while preserving coverage.
    """

    alpha: float = 0.15               # 1 - alpha = 85% target coverage
    residuals: list[float] = field(default_factory=list)
    q: float = 0.0

    def calibrate(self, y_true: Sequence[float], y_pred: Sequence[float],
                  scale: Sequence[float] | None = None) -> "ConformalInterval":
        sc = list(scale) if scale else [1.0] * len(y_true)
        self.residuals = [
            abs(t - p) / (s if s > 1e-9 else 1e-9)
            for t, p, s in zip(y_true, y_pred, sc)
        ]
        n = len(self.residuals)
        if n == 0:
            self.q = 0.0
            return self
        # Finite-sample corrected quantile level: ceil((n+1)(1-alpha))/n
        level = min(1.0, math.ceil((n + 1) * (1 - self.alpha)) / n)
        self.q = quantile(self.residuals, level)
        return self

    def interval(self, y_pred: float, scale: float = 1.0) -> tuple[float, float]:
        d = self.q * (scale if scale > 1e-9 else 1e-9)
        return (y_pred - d, y_pred + d)

    def width(self, scale: float = 1.0) -> float:
        return 2.0 * self.q * scale


# --------------------------------------------------------------------------- abstention
@dataclass
class SelectiveClassifier:
    """Wraps a calibrated classifier with a learned abstention band.

    Reports the full accuracy-vs-coverage curve rather than a single number,
    because the honest answer to "how accurate is it" is a curve.
    """

    lo: float = 0.5
    hi: float = 0.5

    def fit_threshold(self, probs: Sequence[float], labels: Sequence[int],
                      target_acc: float = 0.85,
                      min_coverage: float = 0.02) -> dict:
        """Find the tightest symmetric band achieving target_acc, if one exists."""
        curve = accuracy_coverage_curve(probs, labels)
        best = None
        for row in curve:
            if row["accuracy"] >= target_acc and row["coverage"] >= min_coverage:
                best = row
                break
        if best is None:
            # Report the best achievable instead of silently pretending.
            feasible = [r for r in curve if r["coverage"] >= min_coverage]
            best = max(feasible, key=lambda r: r["accuracy"]) if feasible else None
        if best:
            self.lo, self.hi = best["lo"], best["hi"]
        return {"curve": curve, "selected": best}

    def decide(self, p: float) -> int | None:
        """1 = up, 0 = down, None = abstain."""
        if p >= self.hi:
            return 1
        if p <= self.lo:
            return 0
        return None


def accuracy_coverage_curve(probs: Sequence[float], labels: Sequence[int],
                            steps: int = 24) -> list[dict]:
    """Accuracy as a function of how selective we are. The honest deliverable."""
    out = []
    n = len(probs)
    if n == 0:
        return out
    for k in range(steps):
        margin = 0.5 * k / steps          # 0 -> fire on everything
        lo, hi = 0.5 - margin, 0.5 + margin
        fired = [(p, l) for p, l in zip(probs, labels) if p >= hi or p <= lo]
        if not fired:
            continue
        correct = sum(1 for p, l in fired if (1 if p >= hi else 0) == l)
        acc = correct / len(fired)
        ci = wilson_interval(correct, len(fired))
        out.append({
            "margin": margin, "lo": lo, "hi": hi,
            "coverage": len(fired) / n, "n_fired": len(fired),
            "accuracy": acc, "ci_low": ci[0], "ci_high": ci[1],
            "correct": correct,
        })
    out.sort(key=lambda r: (-r["accuracy"], -r["coverage"]))
    return out


# --------------------------------------------------------------------------- metrics
def brier_score(probs: Sequence[float], labels: Sequence[int]) -> float:
    if not probs:
        return 0.0
    return mean([(p - l) ** 2 for p, l in zip(probs, labels)])


def log_loss(probs: Sequence[float], labels: Sequence[int]) -> float:
    if not probs:
        return 0.0
    tot = 0.0
    for p, l in zip(probs, labels):
        pc = clamp(p, 1e-9, 1 - 1e-9)
        tot += -(l * math.log(pc) + (1 - l) * math.log(1 - pc))
    return tot / len(probs)


def reliability_table(probs: Sequence[float], labels: Sequence[int],
                      bins: int = 10) -> list[dict]:
    """Calibration diagnostic: in each probability bucket, does p match reality?"""
    buckets: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for p, l in zip(probs, labels):
        b = min(int(p * bins), bins - 1)
        buckets[b].append((p, l))
    rows = []
    for i, bk in enumerate(buckets):
        if not bk:
            continue
        rows.append({
            "bin": f"{i/bins:.1f}-{(i+1)/bins:.1f}",
            "n": len(bk),
            "mean_pred": mean([p for p, _ in bk]),
            "observed": mean([float(l) for _, l in bk]),
        })
    return rows
