"""XAU-Q exhaustive rule miner.

The brief: "run 100s of calculations and formulas and rules and patterns to beat
85% accuracy on next candle predictions."

This module does exactly that, systematically, and — critically — with the
statistics that tell you whether a winner is real or an artifact of having
looked 500 times.

WHY MULTIPLE-TESTING CORRECTION IS THE WHOLE BALLGAME
------------------------------------------------------
If you test 500 independent rules on pure noise at p<0.05, you expect ~25 to
"work". Sort them by accuracy and the best will look spectacular. This is how
every 85%-accuracy trading product is manufactured — not by fraud, usually, but
by searching hard and reporting only the maximum.

Three defences are applied to every rule found here:

  1. BONFERRONI / BENJAMINI-HOCHBERG on the p-values. A rule must survive
     correction for the number of rules tested, not just beat 0.05 alone.

  2. WHITE'S REALITY CHECK (bootstrap). Resample the *entire search* under the
     null that no rule has skill, and ask how often the best rule in a null
     universe beats our best real rule. This is the correct test for "is my
     winner just the max of 500 draws?"

  3. OUT-OF-SAMPLE HOLDOUT. Rules are discovered on a train split and scored on
     a test split they never touched. Discovery accuracy is reported next to
     holdout accuracy so the decay is visible.

TARGET FORMULATIONS
-------------------
"Direction of the next candle" is not one question, it is a family. This module
tests eight formulations, because the answer to "can you hit 85%?" depends
entirely on which one you mean — and one of them genuinely can.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Sequence

from .core import (
    Bar, atr, binomial_p_value, clamp, logret, mean, quantile, session_of,
    sign, stdev, true_range, wilson_interval,
)
from .features import FeatureBuilder, FEATURE_NAMES


# ============================================================== TARGETS
@dataclass
class Target:
    name: str
    description: str
    fn: Callable[[Sequence[Bar], int], int | None]
    tradeable: bool
    note: str = ""


def _t_dir_oc(bars, i):
    """Classic: does bar i close above its open?"""
    if i >= len(bars):
        return None
    return 1 if bars[i].close > bars[i].open else 0


def _t_dir_cc(bars, i):
    """Does bar i close above bar i-1's close?"""
    if i >= len(bars) or i < 1:
        return None
    return 1 if bars[i].close > bars[i - 1].close else 0


def _t_high_exceeds_close(bars, i):
    """Does bar i's HIGH exceed the previous close?

    Path-dependent: the high is a maximum over the intrabar path, so this is
    structurally easier than close-direction. Base rate ~75-85%.
    """
    if i >= len(bars) or i < 1:
        return None
    return 1 if bars[i].high > bars[i - 1].close else 0


def _t_low_breaks_close(bars, i):
    if i >= len(bars) or i < 1:
        return None
    return 1 if bars[i].low < bars[i - 1].close else 0


def _make_barrier(up_k: float, dn_k: float, horizon: int):
    """Asymmetric first-touch barrier over the next `horizon` bars.

    Returns 1 if price touches prev_close + up_k*ATR BEFORE it touches
    prev_close - dn_k*ATR. This is the formulation where >85% is genuinely,
    provably reachable — not by predicting anything clever, but because an
    asymmetric barrier has an asymmetric hitting probability.
    """
    def fn(bars, i):
        if i < 1 or i + horizon > len(bars):
            return None
        a = atr(bars[:i], 14)
        if a <= 0:
            return None
        c = bars[i - 1].close
        up, dn = c + up_k * a, c - dn_k * a
        for j in range(i, i + horizon):
            hi_hit = bars[j].high >= up
            lo_hit = bars[j].low <= dn
            if hi_hit and lo_hit:
                return None          # ambiguous within the bar: discard
            if hi_hit:
                return 1
            if lo_hit:
                return 0
        return None                  # neither touched: discard
    return fn


def _t_range_exceeds_half_atr(bars, i):
    if i >= len(bars) or i < 1:
        return None
    a = atr(bars[:i], 14)
    if a <= 0:
        return None
    return 1 if true_range(bars[i - 1].close, bars[i]) > 0.5 * a else 0


TARGETS: list[Target] = [
    Target("dir_open_close", "close > open (the classic 'next candle direction')",
           _t_dir_oc, True,
           "The formulation everyone means. Efficient-market limit applies."),
    Target("dir_close_close", "close > previous close",
           _t_dir_cc, True, "Same information content as dir_open_close."),
    Target("high_gt_prev_close", "next bar's HIGH exceeds previous close",
           _t_high_exceeds_close, False,
           "Path-dependent, high base rate, but you cannot trade it directly: "
           "knowing the high is touched says nothing about where you exit."),
    Target("low_lt_prev_close", "next bar's LOW breaks previous close",
           _t_low_breaks_close, False, "Mirror of the above."),
    Target("barrier_0.25up_2.0dn_8", "touch +0.25 ATR before -2.0 ATR within 8 bars",
           _make_barrier(0.25, 2.0, 8), True,
           "ASYMMETRIC BARRIER. High accuracy by construction; the payoff is "
           "correspondingly asymmetric. This is where >85% actually lives."),
    Target("barrier_0.5up_3.0dn_12", "touch +0.5 ATR before -3.0 ATR within 12 bars",
           _make_barrier(0.5, 3.0, 12), True, ""),
    Target("barrier_1.0up_1.0dn_6", "touch +1.0 ATR before -1.0 ATR within 6 bars",
           _make_barrier(1.0, 1.0, 6), True,
           "SYMMETRIC barrier: the fair-odds control. Should sit near 50%."),
    Target("range_gt_half_atr", "true range exceeds 0.5 ATR",
           _t_range_exceeds_half_atr, False, "Volatility target, not direction."),
]


# ============================================================== RULES
@dataclass
class Rule:
    name: str
    family: str
    predicate: Callable[[dict], int | None]   # features -> 1 / 0 / None(abstain)


def build_rule_universe() -> list[Rule]:
    """Several hundred rules across every feature dimension available."""
    rules: list[Rule] = []

    def add(name, family, fn):
        rules.append(Rule(name, family, fn))

    # ---- 1. Single-feature threshold rules, both polarities ----------------
    thresholds = {
        "mom_3": [-1.5, -0.8, -0.3, 0.3, 0.8, 1.5],
        "mom_10": [-1.5, -0.8, -0.3, 0.3, 0.8, 1.5],
        "mom_30": [-2.0, -1.0, 1.0, 2.0],
        "close_loc": [0.1, 0.25, 0.5, 0.75, 0.9],
        "body_frac": [-0.6, -0.3, 0.3, 0.6],
        "upper_wick_frac": [0.3, 0.5, 0.7],
        "lower_wick_frac": [0.3, 0.5, 0.7],
        "wick_skew_5": [-0.5, -0.2, 0.2, 0.5],
        "run_len": [-1.0, -0.6, 0.6, 1.0],
        "rv_5": [0.0005, 0.001, 0.002],
        "vol_ratio_5_60": [0.6, 0.8, 1.2, 1.6],
        "vol_ratio_20_60": [0.7, 1.0, 1.3],
        "vol_of_vol": [0.2, 0.4, 0.7],
        "atr_ratio_14_50": [0.7, 0.9, 1.1, 1.3],
        "range_pctile": [0.1, 0.25, 0.5, 0.75, 0.9],
        "nr_rank": [0.1, 0.3, 0.7, 0.9],
        "squeeze": [0.2, 0.35, 0.5, 0.7],
        "sess_pos": [0.1, 0.25, 0.5, 0.75, 0.9],
        "sess_range_atr": [0.5, 1.0, 2.0, 3.0],
        "dist_hi_20": [0.2, 0.5, 1.0, 2.0],
        "dist_lo_20": [0.2, 0.5, 1.0, 2.0],
        "dist_hi_60": [0.5, 1.5, 3.0],
        "dist_lo_60": [0.5, 1.5, 3.0],
        "sweep_depth": [0.05, 0.15, 0.35],
        "round_10": [0.1, 0.25, 0.4],
        "round_25": [0.1, 0.25, 0.4],
        "gap_atr": [-0.5, -0.2, 0.2, 0.5],
        "ac1_20": [-0.3, -0.1, 0.1, 0.3],
        "vol_z": [-1.0, 0.0, 1.0, 2.0],
        "vol_trend": [0.8, 1.0, 1.2],
    }
    for feat, cuts in thresholds.items():
        for c in cuts:
            add(f"{feat}>{c}", "threshold",
                lambda f, k=feat, t=c: (1 if f.get(k, 0.0) > t else 0))
            add(f"{feat}<={c}", "threshold",
                lambda f, k=feat, t=c: (1 if f.get(k, 0.0) <= t else 0))

    # ---- 2. Boolean pattern rules ------------------------------------------
    add("sweep_high_fade", "pattern",
        lambda f: 0 if f.get("sweep_high", 0) > 0 else None)
    add("sweep_low_bounce", "pattern",
        lambda f: 1 if f.get("sweep_low", 0) > 0 else None)
    add("sweep_high_follow", "pattern",
        lambda f: 1 if f.get("sweep_high", 0) > 0 else None)
    add("sweep_low_follow", "pattern",
        lambda f: 0 if f.get("sweep_low", 0) > 0 else None)

    # ---- 3. Session-conditional rules --------------------------------------
    for s in ("asia", "london", "overlap", "newyork", "late"):
        add(f"{s}_long", "session", lambda f, k=s: 1 if f.get(f"sess_{k}", 0) > 0 else None)
        add(f"{s}_short", "session", lambda f, k=s: 0 if f.get(f"sess_{k}", 0) > 0 else None)
        for feat, t in (("mom_10", 0.5), ("close_loc", 0.7), ("sess_pos", 0.8),
                        ("range_pctile", 0.8), ("nr_rank", 0.2)):
            add(f"{s}&{feat}>{t}_long", "session_combo",
                lambda f, k=s, ft=feat, th=t:
                    (1 if f.get(ft, 0) > th else 0) if f.get(f"sess_{k}", 0) > 0 else None)
            add(f"{s}&{feat}>{t}_short", "session_combo",
                lambda f, k=s, ft=feat, th=t:
                    (0 if f.get(ft, 0) > th else 1) if f.get(f"sess_{k}", 0) > 0 else None)

    # ---- 4. Two-feature interaction rules ----------------------------------
    pairs = [
        ("mom_10", 0.5, "range_pctile", 0.7),
        ("mom_10", -0.5, "range_pctile", 0.7),
        ("close_loc", 0.8, "vol_ratio_5_60", 1.2),
        ("close_loc", 0.2, "vol_ratio_5_60", 1.2),
        ("nr_rank", 0.2, "squeeze", 0.3),
        ("dist_hi_20", 0.3, "mom_3", 0.5),
        ("dist_lo_20", 0.3, "mom_3", -0.5),
        ("wick_skew_5", 0.4, "sess_pos", 0.3),
        ("wick_skew_5", -0.4, "sess_pos", 0.7),
        ("run_len", 0.8, "range_pctile", 0.6),
        ("run_len", -0.8, "range_pctile", 0.6),
        ("vol_z", 1.5, "body_frac", 0.4),
        ("gap_atr", 0.3, "close_loc", 0.6),
        ("gap_atr", -0.3, "close_loc", 0.4),
        ("round_10", 0.15, "mom_3", 0.4),
        ("ac1_20", 0.2, "mom_10", 0.5),
        ("ac1_20", -0.2, "mom_10", 0.5),
        ("squeeze", 0.25, "sess_range_atr", 1.5),
        ("atr_ratio_14_50", 1.2, "mom_30", 1.0),
        ("vol_of_vol", 0.5, "range_pctile", 0.8),
    ]
    for fa, ta, fb, tb in pairs:
        for pol in (1, 0):
            add(f"({fa}>{ta})&({fb}>{tb})->{pol}", "interaction",
                lambda f, a=fa, x=ta, b=fb, y=tb, p=pol:
                    p if (f.get(a, 0) > x and f.get(b, 0) > y) else None)
            add(f"({fa}<{ta})&({fb}>{tb})->{pol}", "interaction",
                lambda f, a=fa, x=ta, b=fb, y=tb, p=pol:
                    p if (f.get(a, 0) < x and f.get(b, 0) > y) else None)

    # ---- 5. Triple-condition rules (deep conditioning) ---------------------
    triples = [
        ("sess_overlap", 0.5, "nr_rank", 0.2, "mom_10", 0.3),
        ("sess_london", 0.5, "range_pctile", 0.8, "close_loc", 0.7),
        ("sess_asia", 0.5, "squeeze", 0.3, "sess_pos", 0.2),
        ("sess_newyork", 0.5, "vol_z", 1.0, "body_frac", 0.3),
        ("sess_overlap", 0.5, "dist_hi_20", 0.3, "mom_3", 0.5),
    ]
    for fa, ta, fb, tb, fc, tc in triples:
        for pol in (1, 0):
            add(f"({fa}>{ta})&({fb}>{tb})&({fc}>{tc})->{pol}", "triple",
                lambda f, a=fa, x=ta, b=fb, y=tb, c=fc, z=tc, p=pol:
                    p if (f.get(a, 0) > x and f.get(b, 0) > y and f.get(c, 0) > z)
                    else None)
            add(f"({fa}>{ta})&({fb}<{tb})&({fc}<{tc})->{pol}", "triple",
                lambda f, a=fa, x=ta, b=fb, y=tb, c=fc, z=tc, p=pol:
                    p if (f.get(a, 0) > x and f.get(b, 0) < y and f.get(c, 0) < z)
                    else None)

    # ---- 6. Classic TA-style composites ------------------------------------
    add("mean_reversion_extreme", "classic",
        lambda f: (0 if f.get("mom_10", 0) > 1.2 else 1)
        if abs(f.get("mom_10", 0)) > 1.2 else None)
    add("momentum_continuation", "classic",
        lambda f: (1 if f.get("mom_10", 0) > 1.2 else 0)
        if abs(f.get("mom_10", 0)) > 1.2 else None)
    add("nr7_breakout_long", "classic",
        lambda f: 1 if f.get("nr_rank", 1) < 0.15 else None)
    add("nr7_breakout_short", "classic",
        lambda f: 0 if f.get("nr_rank", 1) < 0.15 else None)
    add("pin_bar_bull", "classic",
        lambda f: 1 if (f.get("lower_wick_frac", 0) > 0.55
                        and f.get("body_frac", 0) > -0.2) else None)
    add("pin_bar_bear", "classic",
        lambda f: 0 if (f.get("upper_wick_frac", 0) > 0.55
                        and f.get("body_frac", 0) < 0.2) else None)
    add("inside_bar_compress", "classic",
        lambda f: 1 if f.get("range_pctile", 1) < 0.12 else None)
    add("exhaustion_gap_fade", "classic",
        lambda f: (0 if f.get("gap_atr", 0) > 0.4 else 1)
        if abs(f.get("gap_atr", 0)) > 0.4 else None)

    return rules


# ============================================================== EVALUATION
@dataclass
class RuleResult:
    rule: str
    family: str
    target: str
    n_train: int
    acc_train: float
    n_test: int
    acc_test: float
    ci_test: tuple[float, float]
    p_value: float
    p_bonferroni: float
    base_rate: float
    edge_vs_base: float
    coverage: float
    survives_bh: bool = False

    def to_dict(self) -> dict:
        return {k: (list(v) if isinstance(v, tuple) else v)
                for k, v in self.__dict__.items()}


def evaluate_rules(
    bars: Sequence[Bar],
    target: Target,
    rules: Sequence[Rule],
    split: float = 0.6,
    min_n: int = 120,
    fdr_q: float = 0.05,
) -> list[RuleResult]:
    """Discover on train, score on test, correct for multiple testing."""
    fb = FeatureBuilder()
    rows: list[tuple[dict, int]] = []
    for i in range(fb.warmup, len(bars)):
        y = target.fn(bars, i)
        if y is None:
            continue
        fv = fb.at(bars, i)
        if fv is None:
            continue
        rows.append((fv.values, y))

    if len(rows) < min_n * 3:
        return []

    cut = int(len(rows) * split)
    tr, te = rows[:cut], rows[cut:]
    base = mean([float(y) for _, y in te]) if te else 0.5
    base = max(base, 1 - base)

    out: list[RuleResult] = []
    for rule in rules:
        ftr = [(rule.predicate(f), y) for f, y in tr]
        ftr = [(p, y) for p, y in ftr if p is not None]
        if len(ftr) < min_n:
            continue
        acc_tr = mean([1.0 if p == y else 0.0 for p, y in ftr])

        fte = [(rule.predicate(f), y) for f, y in te]
        fte = [(p, y) for p, y in fte if p is not None]
        if len(fte) < min_n // 2:
            continue
        k = sum(1 for p, y in fte if p == y)
        n = len(fte)
        acc_te = k / n
        out.append(RuleResult(
            rule=rule.name, family=rule.family, target=target.name,
            n_train=len(ftr), acc_train=acc_tr,
            n_test=n, acc_test=acc_te,
            ci_test=wilson_interval(k, n),
            p_value=binomial_p_value(k, n, 0.5),
            p_bonferroni=0.0, base_rate=base,
            edge_vs_base=acc_te - base,
            coverage=n / max(len(te), 1),
        ))

    m = len(out)
    for r in out:
        r.p_bonferroni = min(1.0, r.p_value * m)

    # Benjamini-Hochberg FDR control.
    ordered = sorted(out, key=lambda r: r.p_value)
    for idx, r in enumerate(ordered, 1):
        if r.p_value <= fdr_q * idx / max(m, 1):
            r.survives_bh = True
    out.sort(key=lambda r: -r.acc_test)
    return out


def reality_check(results: Sequence[RuleResult], n_boot: int = 2000,
                  seed: int = 17) -> dict:
    """White's Reality Check, simplified.

    Under the null that every rule has zero skill, each rule's test accuracy is
    Binomial(n, 0.5)/n. Simulate the WHOLE search that many times and record how
    often the best rule in a null universe beats our observed best. That
    p-value answers the only question that matters: "is my winner just the
    maximum of N draws?"
    """
    if not results:
        return {}
    rng = random.Random(seed)
    observed_best = max(r.acc_test for r in results)
    ns = [r.n_test for r in results]

    def sim_acc(n: int) -> float:
        # Normal approximation to Binomial(n, 0.5) accuracy.
        return 0.5 + rng.gauss(0, 0.5 / math.sqrt(n))

    beats = 0
    null_bests = []
    for _ in range(n_boot):
        b = max(sim_acc(n) for n in ns)
        null_bests.append(b)
        if b >= observed_best:
            beats += 1
    return {
        "observed_best_acc": observed_best,
        "n_rules": len(results),
        "null_best_mean": mean(null_bests),
        "null_best_p95": quantile(null_bests, 0.95),
        "reality_check_p": beats / n_boot,
        "verdict": ("REAL — best rule beats what pure search noise produces"
                    if beats / n_boot < 0.05
                    else "ARTIFACT — this accuracy is what searching this many "
                         "rules produces on noise alone"),
    }
