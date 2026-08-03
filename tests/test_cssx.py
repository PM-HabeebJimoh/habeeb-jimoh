"""CSS-X behavioural tests: separation, safety rails, and monotonicity."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest

from cssx.core import UTC, AssetClass, Observation
from cssx.convergence import score_entity, rank
from cssx.fixtures import CONTROL_FIXTURES, DISTRESS_FIXTURES, FIXTURE_HISTORIES, ALL_FIXTURES
from cssx.store import Store


class TestSeparation(unittest.TestCase):
    def test_distress_above_controls(self):
        verdicts = {v.entity_id: v for v in rank(ALL_FIXTURES, FIXTURE_HISTORIES)}
        worst_control = max(verdicts[o.entity_id].score for o in CONTROL_FIXTURES)
        best_distress = min(verdicts[o.entity_id].score for o in DISTRESS_FIXTURES)
        self.assertGreater(best_distress, worst_control + 0.4,
                           "distress and control populations must be cleanly separated")

    def test_all_distress_reach_critical(self):
        for v in rank(DISTRESS_FIXTURES, FIXTURE_HISTORIES):
            self.assertGreaterEqual(v.score, 0.75, f"{v.entity_id} should be CRITICAL+")

    def test_controls_stay_below_watch(self):
        for v in rank(CONTROL_FIXTURES, FIXTURE_HISTORIES):
            self.assertLess(v.score, 0.35, f"{v.entity_id} must not reach WATCH")


class TestSafetyRails(unittest.TestCase):
    def test_persistence_gate_caps_score(self):
        o = DISTRESS_FIXTURES[0]
        confirmed = score_entity(o, FIXTURE_HISTORIES[o.entity_id])
        unconfirmed = score_entity(o, {})
        self.assertLessEqual(unconfirmed.score, 0.74)
        self.assertGreater(confirmed.score, unconfirmed.score)
        self.assertFalse(unconfirmed.persistence_ok)

    def test_contradiction_caps_score(self):
        base = DISTRESS_FIXTURES[2]
        facts = dict(base.facts)
        facts["verified_raise_30d_usd"] = 50_000_000
        o = Observation(base.entity_id, base.asset_class, base.ts, facts, base.sources)
        v = score_entity(o, FIXTURE_HISTORIES[base.entity_id])
        self.assertLessEqual(v.score, 0.60)
        self.assertTrue(v.contradictions)

    def test_social_layer_cannot_fire_alone(self):
        o = Observation("rumour-only", AssetClass.CEX, datetime.now(UTC), {
            "withdrawal_failure_reports_7d": 200,
            "onchain_corroboration_rate": 0.9,
            "aged_account_share": 0.9,
        })
        v = score_entity(o, {407: 30})
        self.assertEqual(v.score, 0.0, "rumour alone must never score")

    def test_empty_observation_is_silent(self):
        v = score_entity(Observation("unknown", AssetClass.TOKEN, datetime.now(UTC), {}))
        self.assertEqual(v.score, 0.0)
        self.assertEqual(v.coverage, 0.0)
        self.assertLess(v.confidence, 0.6)

    def test_score_always_bounded(self):
        for o in ALL_FIXTURES:
            v = score_entity(o, FIXTURE_HISTORIES.get(o.entity_id))
            self.assertGreaterEqual(v.score, 0.0)
            self.assertLessEqual(v.score, 1.0)


class TestPaths(unittest.TestCase):
    def test_shadow_path_needs_three_absences(self):
        base_facts = {
            "days_since_attestation": 500, "promised_cadence_days": 90,
            "auditor_resigned": True,
        }
        one = score_entity(Observation("shadow-1", AssetClass.CEX, datetime.now(UTC),
                                       base_facts), {404: 30})
        self.assertNotEqual(one.path, "PATH_B_SHADOW")

        three = dict(base_facts)
        three.update({
            "days_since_treasury_tx": 150, "runway_months": 1,
            "unique_depositors_30d": 5, "depositors_baseline_90d": 5000,
            "inflow_30d_usd": 0, "outflow_30d_usd": 1_000_000,
        })
        v = score_entity(Observation("shadow-3", AssetClass.CEX, datetime.now(UTC), three),
                         {403: 30, 404: 30, 405: 30})
        self.assertEqual(v.path, "PATH_B_SHADOW")
        self.assertGreaterEqual(v.active_absences, 3)

    def test_cluster_damping_limits_correlated_stacking(self):
        """Five correlated signals must not beat genuinely independent ones."""
        correlated = Observation("correlated", AssetClass.DEFI, datetime.now(UTC), {
            "kl_divergence_bits": 3.0, "reassurance_density": 0.4,
            "withdrawal_failure_reports_7d": 100, "onchain_corroboration_rate": 0.9,
            "aged_account_share": 0.9,
            "peg_deviation_bps": 300, "deviation_persist_hours": 20,
        })
        v = score_entity(correlated, {406: 30, 407: 30, 203: 30})
        self.assertLess(v.score, 0.75)


class TestMonotonicity(unittest.TestCase):
    def test_worse_inputs_never_lower_score(self):
        mild = {
            "reserves_usd": 9_800_000_000, "liabilities_usd": 10_000_000_000,
            "self_token_reserve_share": 0.1,
            "days_since_attestation": 120, "promised_cadence_days": 90,
            "days_since_treasury_tx": 50, "runway_months": 5,
            "unique_depositors_30d": 1000, "depositors_baseline_90d": 3000,
            "inflow_30d_usd": 100, "outflow_30d_usd": 1000,
        }
        severe = dict(mild)
        severe.update({"reserves_usd": 4_000_000_000, "self_token_reserve_share": 0.6,
                       "days_since_attestation": 400, "days_since_treasury_tx": 200,
                       "runway_months": 0.5, "unique_depositors_30d": 5,
                       "inflow_30d_usd": 0})
        h = {l: 30 for l in (204, 403, 404, 405)}
        a = score_entity(Observation("m1", AssetClass.CEX, datetime.now(UTC), mild), h)
        b = score_entity(Observation("m2", AssetClass.CEX, datetime.now(UTC), severe), h)
        self.assertGreater(b.score, a.score)


class TestStore(unittest.TestCase):
    def test_persistence_streak_accumulates(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            store = Store(os.path.join(d, "t.db"))
            base = DISTRESS_FIXTURES[3]
            for i in range(5):
                ts = datetime.now(UTC) - timedelta(days=4 - i)
                o = Observation(base.entity_id, base.asset_class, ts, base.facts)
                store.record(o, score_entity(o, store.persistence(o.entity_id)))
            streaks = store.persistence(base.entity_id)
            self.assertGreaterEqual(streaks.get(101, 0), 5)
            self.assertEqual(len(store.latest_verdicts()), 5)
            store.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
