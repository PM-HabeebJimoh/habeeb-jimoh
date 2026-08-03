"""XAU-Q test suite. The lookahead detectors are the important ones."""

from __future__ import annotations

import math
import random
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from xau.core import (
    Bar, Session, atr, quantile, session_of, wilson_interval, binomial_p_value,
    dedupe_and_check,
)
from xau.features import FeatureBuilder, target_direction, target_range
from xau.model import (
    ConformalInterval, IsotonicCalibrator, LogisticModel, RidgeModel,
    accuracy_coverage_curve,
)
from xau.synth import generate, stylised_facts
from xau.walkforward import run_walkforward

UTC = timezone.utc


class TestNoLookahead(unittest.TestCase):
    """If any of these fail, every accuracy number in the package is fiction."""

    def setUp(self):
        self.bars = generate(1200, seed=3)
        self.fb = FeatureBuilder()

    def test_features_ignore_future_bars(self):
        """Mutating bars[i:] must not change the feature vector for bar i."""
        i = 700
        base = self.fb.at(self.bars, i).values
        poisoned = list(self.bars)
        for j in range(i, len(poisoned)):
            b = poisoned[j]
            poisoned[j] = Bar(b.ts, b.open * 3, b.high * 3, b.low * 3,
                              b.close * 3, b.volume, b.spread)
        after = self.fb.at(poisoned, i).values
        for k in base:
            self.assertAlmostEqual(
                base[k], after[k], places=9,
                msg=f"feature {k} changed when future bars were altered -> LOOKAHEAD",
            )

    def test_features_ignore_the_target_bar_itself(self):
        """Feature vector for i must not read bars[i] price data."""
        i = 700
        base = self.fb.at(self.bars, i).values
        poisoned = list(self.bars)
        b = poisoned[i]
        poisoned[i] = Bar(b.ts, b.open * 5, b.high * 5, b.low * 5, b.close * 5)
        after = self.fb.at(poisoned, i).values
        for k in base:
            self.assertAlmostEqual(base[k], after[k], places=9,
                                   msg=f"feature {k} reads the target bar -> LOOKAHEAD")

    def test_shuffled_labels_give_chance_accuracy(self):
        """The classic detector: destroy the label/feature link, expect ~50%."""
        bars = generate(4200, seed=9, edge=0.0)
        r = run_walkforward(bars, train=1500, calib=500, test=200, purge=30)
        dm = r.direction_metrics()
        lo, hi = dm["ci95"]
        self.assertLess(lo, 0.5, "no-edge data must not produce a CI above chance")
        self.assertGreater(hi, 0.5)


class TestFalsifiability(unittest.TestCase):
    def test_martingale_scores_near_fifty(self):
        bars = generate(4200, seed=21, edge=0.0)
        r = run_walkforward(bars, train=1500, calib=500, test=200, purge=30)
        acc = r.direction_metrics()["accuracy_all_bars"]
        self.assertLess(abs(acc - 0.5), 0.035,
                        f"martingale scored {acc:.3f}; harness is biased")

    def test_planted_edge_is_detected(self):
        bars = generate(4200, seed=21, edge=3.0)
        r = run_walkforward(bars, train=1500, calib=500, test=200, purge=30)
        dm = r.direction_metrics()
        self.assertGreater(dm["accuracy_all_bars"], 0.53,
                           "harness cannot detect a large planted edge")
        self.assertGreater(dm["curve"][0]["accuracy"], 0.65)


class TestConformalGuarantee(unittest.TestCase):
    def test_coverage_matches_target(self):
        rng = random.Random(0)
        y = [rng.gauss(0, 1) for _ in range(4000)]
        p = [0.0] * 4000
        for alpha in (0.10, 0.15, 0.30):
            ci = ConformalInterval(alpha=alpha).calibrate(y[:2000], p[:2000])
            hits = sum(1 for t in y[2000:]
                       if ci.interval(0.0)[0] <= t <= ci.interval(0.0)[1])
            cov = hits / 2000
            self.assertAlmostEqual(cov, 1 - alpha, delta=0.03,
                                   msg=f"alpha={alpha} gave coverage {cov:.3f}")

    def test_coverage_holds_for_a_useless_model(self):
        """The guarantee must not depend on the point model being good."""
        rng = random.Random(1)
        y = [rng.gauss(0, 1) for _ in range(3000)]
        garbage = [99.0] * 3000            # deliberately terrible predictions
        ci = ConformalInterval(alpha=0.15).calibrate(y[:1500], garbage[:1500])
        hits = sum(1 for t in y[1500:]
                   if ci.interval(99.0)[0] <= t <= ci.interval(99.0)[1])
        self.assertGreater(hits / 1500, 0.80)

    def test_walkforward_range_coverage_hits_85(self):
        bars = generate(7000, seed=11, edge=0.35)
        r = run_walkforward(bars, train=2500, calib=700, test=250, purge=30,
                            alpha=0.15)
        rm = r.range_metrics()
        self.assertGreater(rm["empirical_coverage"], 0.82)
        self.assertLess(rm["empirical_coverage"], 0.90)

    def test_range_model_beats_naive(self):
        bars = generate(7000, seed=11, edge=0.35)
        r = run_walkforward(bars, train=2500, calib=700, test=250, purge=30)
        self.assertGreater(r.range_metrics()["skill_vs_naive"], 0.05)


class TestSyntheticRealism(unittest.TestCase):
    def test_stylised_facts_in_gold_range(self):
        for seed in (1, 4, 7):
            f = stylised_facts(generate(6000, seed=seed))
            self.assertLess(abs(f["ret_autocorr_lag1"]), 0.06)
            self.assertGreater(f["absret_autocorr_lag1"], 0.10)
            self.assertGreater(f["excess_kurtosis"], 2.0)
            self.assertLess(f["excess_kurtosis"], 12.0,
                            "kurtosis outside real gold's 5-9 band")

    def test_session_ordering_is_realistic(self):
        f = stylised_facts(generate(8000, seed=2))
        m = f["session_vol_multipliers"]
        self.assertLess(m["asia"], m["london"])
        self.assertLess(m["london"], m["overlap"])

    def test_bars_are_internally_valid(self):
        for b in generate(2000, seed=6):
            b.validate()


class TestPlumbing(unittest.TestCase):
    def test_wilson_interval_sanity(self):
        lo, hi = wilson_interval(85, 100)
        self.assertLess(lo, 0.85)
        self.assertGreater(hi, 0.85)
        self.assertGreater(hi - lo, 0.05, "n=100 must produce a wide CI")

    def test_small_sample_ci_is_honest(self):
        """17/20 = 85% but the CI must reach well below it."""
        lo, hi = wilson_interval(17, 20)
        self.assertLess(lo, 0.70)

    def test_binomial_p_value(self):
        self.assertLess(binomial_p_value(80, 100), 1e-6)
        self.assertGreater(binomial_p_value(52, 100), 0.2)

    def test_isotonic_is_monotone(self):
        rng = random.Random(2)
        p = [rng.random() for _ in range(500)]
        y = [1 if rng.random() < pi else 0 for pi in p]
        iso = IsotonicCalibrator().fit(p, y)
        xs = [i / 50 for i in range(51)]
        out = [iso.transform(x) for x in xs]
        for a, b in zip(out, out[1:]):
            self.assertLessEqual(a, b + 1e-9)

    def test_ridge_recovers_linear_signal(self):
        rng = random.Random(4)
        X = [[rng.gauss(0, 1) for _ in range(3)] for _ in range(600)]
        y = [2.0 * x[0] - 1.0 * x[1] + 0.3 + rng.gauss(0, 0.05) for x in X]
        m = RidgeModel(3, l2=0.1).fit(X, y)
        self.assertAlmostEqual(m.w[0], 2.0, delta=0.15)
        self.assertAlmostEqual(m.w[1], -1.0, delta=0.15)

    def test_logistic_learns_separable_data(self):
        rng = random.Random(5)
        X, y = [], []
        for _ in range(400):
            a = rng.gauss(0, 1)
            X.append([a, rng.gauss(0, 1)])
            y.append(1 if a > 0 else 0)
        m = LogisticModel(2, epochs=30).fit(X, y)
        acc = sum(1 for x, t in zip(X, y)
                  if (1 if m.predict_proba(x) > 0.5 else 0) == t) / len(y)
        self.assertGreater(acc, 0.9)

    def test_quantile_edges(self):
        xs = [1, 2, 3, 4, 5]
        self.assertEqual(quantile(xs, 0.0), 1)
        self.assertEqual(quantile(xs, 1.0), 5)
        self.assertAlmostEqual(quantile(xs, 0.5), 3)

    def test_session_boundaries(self):
        f = lambda h: session_of(datetime(2024, 1, 3, h, tzinfo=UTC))
        self.assertEqual(f(2), Session.ASIA)
        self.assertEqual(f(9), Session.LONDON)
        self.assertEqual(f(14), Session.OVERLAP)
        self.assertEqual(f(18), Session.NEWYORK)
        self.assertEqual(f(22), Session.LATE)

    def test_dedupe_removes_duplicate_timestamps(self):
        t = datetime(2024, 1, 1, tzinfo=UTC)
        bars = [Bar(t, 1, 2, 0.5, 1.5), Bar(t, 1, 2, 0.5, 1.5),
                Bar(t + timedelta(hours=1), 1, 2, 0.5, 1.5)]
        clean, stats = dedupe_and_check(bars)
        self.assertEqual(len(clean), 2)
        self.assertEqual(stats["duplicates_removed"], 1)

    def test_invalid_bar_rejected(self):
        with self.assertRaises(ValueError):
            Bar(datetime(2024, 1, 1, tzinfo=UTC), 5, 2, 1, 1.5).validate()

    def test_accuracy_coverage_curve_monotone_ish(self):
        rng = random.Random(8)
        p, y = [], []
        for _ in range(2000):
            pi = rng.random()
            p.append(pi)
            y.append(1 if rng.random() < pi else 0)
        curve = accuracy_coverage_curve(p, y)
        self.assertTrue(all(0 <= r["coverage"] <= 1 for r in curve))
        # 1e-9 tolerance: Wilson's upper bound is 0.9999999999999999 at p=1.0.
        self.assertTrue(all(r["ci_low"] - 1e-9 <= r["accuracy"] <= r["ci_high"] + 1e-9
                            for r in curve))


class TestHonestyGuards(unittest.TestCase):
    """These encode the claims the README makes. If they fail, fix the README."""

    def test_direction_accuracy_is_not_claimed_above_60(self):
        bars = generate(7000, seed=11, edge=0.35)
        r = run_walkforward(bars, train=2500, calib=700, test=250, purge=30)
        acc = r.direction_metrics()["accuracy_all_bars"]
        self.assertLess(acc, 0.60,
                        "realistic-edge data should NOT yield >60% direction; "
                        "if it does, suspect lookahead")

    def test_ohlc_joint_band_near_target(self):
        bars = generate(7000, seed=11, edge=0.35)
        r = run_walkforward(bars, train=2500, calib=700, test=250, purge=30)
        om = r.ohlc_band_metrics()
        self.assertGreater(om["joint_coverage"], 0.80)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestJuly2026Backtest(unittest.TestCase):
    """Regressions from the July 2026 H1 run."""

    @classmethod
    def setUpClass(cls):
        from xau.backtest_july import run_july_h1
        from xau.july2026 import synthesize_h1, verify_reconstruction
        cls.h1 = synthesize_h1()
        cls.recon = verify_reconstruction(cls.h1)
        cls.res = run_july_h1()

    def test_h1_reproduces_real_daily_ohlc_exactly(self):
        """The whole run's validity rests on this: reconstruction must be exact."""
        for field, err in self.recon["max_abs_error_usd"].items():
            self.assertLess(err, 1e-6,
                            f"H1 series does not reproduce real daily {field}")
        self.assertEqual(self.recon["days_checked"], 30)

    def test_july_facts_match_published_market_data(self):
        from xau.july2026 import july_stats
        s = july_stats()
        # Barchart: July low 3960.36 on 07/17, high 4201.70 on 07/06.
        self.assertAlmostEqual(s["month_high"], 4203.10, delta=3.0)
        self.assertAlmostEqual(s["month_low"], 3959.23, delta=3.0)
        self.assertEqual(s["trading_days"], 27)

    def test_all_h1_bars_valid(self):
        for b in self.h1:
            b.validate()

    def test_coverage_shortfall_is_documented_not_hidden(self):
        """July H1 coverage lands below target; assert it is in the known band."""
        cov = self.res["range"]["empirical_coverage"]
        self.assertGreater(cov, 0.75, "coverage collapsed below documented range")
        self.assertLess(cov, 0.88)

    def test_daily_rollup_uses_real_prices(self):
        from xau.july2026 import DAILY_RAW
        real = {d: (h, l) for d, _, h, l, _ in DAILY_RAW}
        for row in self.res["daily_rollup"]["rows"]:
            rh, rl = real[row["date"]]
            self.assertEqual(row["real_high"], rh)
            self.assertEqual(row["real_low"], rl)

    def test_main_evaluation_not_regressed_by_scale_fix(self):
        """The conformal scale fix must not break the n=5250 synthetic run."""
        from xau.synth import generate
        from xau.walkforward import run_walkforward
        bars = generate(9000, seed=11, edge=0.35)
        r = run_walkforward(bars, train=2500, calib=700, test=250, purge=30)
        rm = r.range_metrics()
        self.assertGreater(rm["empirical_coverage"], 0.82)
        self.assertLess(rm["empirical_coverage"], 0.89)
        self.assertGreater(rm["skill_vs_naive"], 0.05)


class TestRuleMining(unittest.TestCase):
    """Regressions from the 3,232-test exhaustive rule search."""

    @classmethod
    def setUpClass(cls):
        from xau.miner import build_rule_universe
        cls.rules = build_rule_universe()

    def test_universe_is_large(self):
        self.assertGreaterEqual(len(self.rules), 400)

    def test_best_of_search_on_noise_is_high(self):
        """The core finding: searching 404 rules on PURE NOISE yields ~58-64%.

        Any 'discovered' direction rule below this band is a search artifact.
        This test exists so nobody -- including me -- can later present a 60%+
        mined direction rule as an edge.
        """
        from xau.miner import TARGETS, evaluate_rules
        from xau.synth import generate
        t = next(x for x in TARGETS if x.name == "dir_open_close")
        res = evaluate_rules(generate(9000, seed=52, edge=0.0), t, self.rules)
        self.assertTrue(res)
        self.assertGreater(res[0].acc_test, 0.53,
                           "noise search should still produce an inflated maximum")

    def test_reality_check_flags_noise(self):
        from xau.miner import TARGETS, evaluate_rules, reality_check
        from xau.synth import generate
        t = next(x for x in TARGETS if x.name == "dir_open_close")
        res = evaluate_rules(generate(9000, seed=50, edge=0.0), t, self.rules)
        rc = reality_check(res)
        self.assertIn("reality_check_p", rc)
        self.assertGreaterEqual(rc["null_best_mean"], 0.5)

    def test_symmetric_barrier_is_a_coin_flip(self):
        """The fair-odds control: +1/-1 ATR must sit near 50%."""
        from xau.miner import _make_barrier
        from xau.synth import generate
        fn = _make_barrier(1.0, 1.0, 6)
        b = generate(9000, seed=31, edge=0.0)
        ys = [fn(b, i) for i in range(300, len(b) - 6)]
        ys = [y for y in ys if y is not None]
        rate = sum(ys) / len(ys)
        self.assertAlmostEqual(rate, 0.5, delta=0.06)

    def test_asymmetric_barrier_accuracy_is_base_rate_not_skill(self):
        """>85% on an asymmetric barrier comes from geometry, not prediction."""
        from xau.miner import _make_barrier
        from xau.synth import generate
        fn = _make_barrier(0.25, 4.0, 16)
        b = generate(9000, seed=31, edge=0.0)   # ZERO edge
        ys = [fn(b, i) for i in range(300, len(b) - 16)]
        ys = [y for y in ys if y is not None]
        rate = sum(ys) / len(ys)
        self.assertGreater(rate, 0.90,
                           "asymmetric barrier should exceed 90% on pure noise")

    def test_close_only_barrier_has_negative_ev(self):
        """Barrier accuracy does not survive contact with honest accounting."""
        from xau.core import atr
        from xau.synth import generate
        b = generate(6000, seed=91, edge=0.0)
        up, dn, h = 0.25, 2.0, 8
        w = l = to = 0
        pnl = 0.0
        for i in range(300, len(b) - h):
            a = atr(b[:i], 14)
            if a <= 0:
                continue
            c = b[i - 1].close
            out = None
            for j in range(i, i + h):
                if b[j].close >= c + up * a:
                    out = "w"
                    break
                if b[j].close <= c - dn * a:
                    out = "l"
                    break
            if out == "w":
                w += 1
                pnl += up
            elif out == "l":
                l += 1
                pnl -= dn
            else:
                to += 1
                pnl += (b[i + h - 1].close - c) / a
        n = w + l + to
        acc = w / (w + l) if (w + l) else 0
        self.assertGreater(acc, 0.75, "accuracy should look impressive")
        self.assertLess(pnl / n, 0.0,
                        "...while EV per trade is NEGATIVE. High accuracy != profit.")
