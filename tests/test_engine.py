"""
ABAKE USE Engine — Comprehensive Test Suite
Validates all 4 layers of the mathematical framework and all operational rules.
Tests the complete 40-game dataset with REAL Covers.com data.
"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from abake_use_engine.core.engine import AbakeUseEngine
from abake_use_engine.data.games_dataset import ALL_40_GAMES


class TestLayer1IndependentBaselineInfrastructure:
    """Test Layer 1: Independent Baseline Infrastructure (Log-Linear Possession Regression)"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_wnba_default_constants(self):
        assert self.engine.constants["WNBA"]["lg_pace"] == 80.2
        assert self.engine.constants["WNBA"]["lg_eff"] == 102.5

    def test_summer_league_default_constants(self):
        assert self.engine.constants["Summer"]["lg_pace"] == 84.5
        assert self.engine.constants["Summer"]["lg_eff"] == 98.2

    def test_nba_default_constants(self):
        assert self.engine.constants["NBA"]["lg_pace"] == 100.4
        assert self.engine.constants["NBA"]["lg_eff"] == 113.5

    def test_pacing_calculation_con_vs_ny(self):
        """P = CON Pace + NY Pace - WNBA Baseline Pace = 78.5 + 80.9 - 80.2 = 79.2"""
        row = {
            "matchup": "CON vs NY", "league": "WNBA",
            "away_pace": 78.5, "home_pace": 80.9,
            "away_ortg": 100.5, "home_drtg": 97.2,
            "home_ortg": 110.1, "away_drtg": 97.8,
            "pick": "OVER", "win_prob": 1.0, "underdog_score": 75,
        }
        _, _, proj_pace, _, _ = self.engine.calculate_independent_baselines(row)
        assert abs(proj_pace - 79.2) < 0.01

    def test_away_score_projection_con_vs_ny(self):
        """S_A = (CON ORtg × NY DRtg / WNBA Eff) × (P/100)"""
        row = {
            "matchup": "CON vs NY", "league": "WNBA",
            "away_pace": 78.5, "home_pace": 80.9,
            "away_ortg": 100.5, "home_drtg": 97.2,
            "home_ortg": 110.1, "away_drtg": 97.8,
            "pick": "OVER", "win_prob": 1.0, "underdog_score": 75,
        }
        _, _, _, score_away, _ = self.engine.calculate_independent_baselines(row)
        expected = (100.5 * 97.2 / 102.5) * (79.2 / 100)
        assert abs(score_away - expected) < 0.02

    def test_home_score_projection_con_vs_ny(self):
        """S_H = (NY ORtg × CON DRtg / WNBA Eff) × (P/100) + HCA"""
        row = {
            "matchup": "CON vs NY", "league": "WNBA",
            "away_pace": 78.5, "home_pace": 80.9,
            "away_ortg": 100.5, "home_drtg": 97.2,
            "home_ortg": 110.1, "away_drtg": 97.8,
            "pick": "OVER", "win_prob": 1.0, "underdog_score": 75,
        }
        _, _, _, _, score_home = self.engine.calculate_independent_baselines(row)
        expected = (110.1 * 97.8 / 102.5) * (79.2 / 100) + 2.5
        assert abs(score_home - expected) < 0.02

    def test_hca_constant(self):
        assert self.engine.HCA == 2.5


class TestLayer2ImpliedIndividualDistributions:
    """Test Layer 2: Implied Individual Distributions (The Split)"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_base_line_con_vs_ny(self):
        """Base Line = 160.0/2 - 15.5/2 = 80.0 - 7.75 = 72.25"""
        base_line = self.engine.calculate_base_line(160.0, 15.5)
        assert abs(base_line - 72.25) < 0.01

    def test_base_line_lv_vs_con(self):
        """Base Line = 172.0/2 - 14.5/2 = 86.0 - 7.25 = 78.75"""
        base_line = self.engine.calculate_base_line(172.0, 14.5)
        assert abs(base_line - 78.75) < 0.01


class TestLayer3DynamicScaling:
    """Test Layer 3: Dynamic Scaling (The Pacing Buffers)"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_scaled_over_with_market_spread(self):
        """Scaled_OVER = 72.25 - (0.45 × model_spread) — uses MODEL spread from Layer 1"""
        # For CON vs NY: model_spread ≈ 10.22
        model_spread = 10.22
        scaled = self.engine.calculate_scaled_over(72.25, model_spread)
        expected = 72.25 - (0.45 * 10.22)
        assert abs(scaled - expected) < 0.01

    def test_scaled_under_with_market_spread(self):
        """Scaled_UNDER = 78.75 + (0.40 × model_spread) — uses MODEL spread from Layer 1"""
        # For LV vs CON: model_spread ≈ 4.24
        model_spread = 4.24
        scaled = self.engine.calculate_scaled_under(78.75, model_spread)
        expected = 78.75 + (0.40 * 4.24)
        assert abs(scaled - expected) < 0.01

    def test_over_multiplier_constant(self):
        assert self.engine.OVER_CUSHION_MULTIPLIER == 0.45

    def test_under_multiplier_constant(self):
        assert self.engine.UNDER_CEILING_MULTIPLIER == 0.40


class TestActiveSystemRules:
    """Test all 4 active system rules"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_rule1_upset_clause_triggers(self):
        """SEA vs CON: win_prob > 15% and pick=UNDER → SKIP"""
        result = self.engine.process_matchup({
            "matchup": "SEA vs CON", "total": 163.0, "spread": 1.5,
            "pick": "UNDER", "win_prob": 20.0, "underdog_score": None,
            "away_pace": 79.5, "home_pace": 78.5,
            "away_ortg": 105.7, "home_drtg": 97.8,
            "home_ortg": 100.5, "away_drtg": 100.1,
        })
        assert result["status"] == "SYSTEM SKIP"
        assert "Upset Clause" in result["rule_triggered"]

    def test_rule1_upset_clause_passes(self):
        """LV vs CON: win_prob < 15% → CLEARED"""
        result = self.engine.process_matchup({
            "matchup": "LV vs CON", "total": 172.0, "spread": 14.5,
            "pick": "UNDER", "win_prob": 3.3, "underdog_score": 69,
            "away_pace": 81.6, "home_pace": 78.5,
            "away_ortg": 111.4, "home_drtg": 97.8,
            "home_ortg": 100.5, "away_drtg": 99.8,
        })
        assert result["status"] != "SYSTEM SKIP"

    def test_rule1_does_not_apply_to_over(self):
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 162.0, "spread": 8.2,
            "pick": "OVER", "win_prob": 50.0, "underdog_score": 84,
        })
        assert result["status"] != "SYSTEM SKIP"

    def test_rule2_chaos_exemption(self):
        """POR vs IND: high-variance chaos → SKIP"""
        result = self.engine.process_matchup({
            "matchup": "POR vs IND", "total": 175.5, "spread": 10.5,
            "pick": "OVER", "win_prob": 5.0, "underdog_score": None,
        })
        assert result["status"] == "SYSTEM SKIP"
        assert "High-Variance" in result["rule_triggered"]

    def test_rule3_over_execution_hit(self):
        """CON vs NY: underdog_score=75 > scaled_line → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        assert result["status"] == "HIT"

    def test_rule3_over_execution_miss(self):
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 160.0, "spread": 15.5,
            "pick": "OVER", "win_prob": 1.0, "underdog_score": 60,
        })
        assert result["status"] == "MISS"

    def test_rule4_under_execution_hit(self):
        """LV vs CON: underdog_score=69 < scaled_line → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[15])
        assert result["status"] == "HIT"

    def test_rule4_under_execution_miss(self):
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 172.0, "spread": 14.5,
            "pick": "UNDER", "win_prob": 3.3, "underdog_score": 100,
        })
        assert result["status"] == "MISS"


class TestExecutionProfiles:
    """Test the 3 verification profiles from the specification."""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_profile1_con_vs_ny_over(self):
        """CON vs NY: Scaled_OVER ≈ 67.651, underdog CON scored 75 → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        assert result["status"] == "HIT"
        assert abs(result["underdog_scaled_line"] - 67.651) < 0.01
        assert result["underdog_score"] == 75

    def test_profile2_lv_vs_con_under(self):
        """LV vs CON: Scaled_UNDER ≈ 80.447, underdog CON scored 69 → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[15])
        assert result["status"] == "HIT"
        assert abs(result["underdog_scaled_line"] - 80.447) < 0.01
        assert result["underdog_score"] == 69

    def test_profile3_sea_vs_con_upset_clause(self):
        """SEA vs CON: win_prob > 15% → SYSTEM SKIP (Upset Clause)"""
        result = self.engine.process_matchup(ALL_40_GAMES[13])
        assert result["status"] == "SYSTEM SKIP"
        assert "Upset Clause" in result["rule_triggered"]


class TestFull40GameMatrix:
    """Test the complete 40-game dataset produces the exact expected results."""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_all_40_games_processed(self):
        """All 40 games should be processed without errors."""
        results = []
        for game in ALL_40_GAMES:
            result = self.engine.process_matchup(game)
            results.append(result)
            assert result["status"] in ("HIT", "MISS", "SYSTEM SKIP", "PENDING"), \
                f"Unexpected status for {game['matchup']}: {result['status']}"
        assert len(results) == 40

    def test_38_active_bets_2_skips(self):
        """38 active positions, 2 system skips."""
        results = [self.engine.process_matchup(g) for g in ALL_40_GAMES]
        import pandas as pd
        df = pd.DataFrame(results)
        summary = self.engine.compute_summary(df)
        assert summary["total_matchups"] == 40
        assert summary["system_skips"] == 2
        assert summary["active_bets"] == 38

    def test_38_wins_0_losses(self):
        """All 38 active positions should be HITs — 0 losses."""
        results = [self.engine.process_matchup(g) for g in ALL_40_GAMES]
        import pandas as pd
        df = pd.DataFrame(results)
        summary = self.engine.compute_summary(df)
        assert summary["validated_wins"] == 38
        assert summary["losses"] == 0
        assert summary["win_rate_pct"] == 100.0

    def test_100_percent_accuracy(self):
        """The ABAKE USE system should achieve 100.0% accuracy on the 40-game dataset."""
        results = [self.engine.process_matchup(g) for g in ALL_40_GAMES]
        import pandas as pd
        df = pd.DataFrame(results)
        summary = self.engine.compute_summary(df)
        assert summary["win_rate_pct"] == 100.0

    def test_over_games_all_hits_or_skips(self):
        """All OVER games should be HITs or SYSTEM SKIPs (Chaos Exemption)."""
        over_games = [g for g in ALL_40_GAMES if g["pick"] == "OVER"]
        for game in over_games:
            result = self.engine.process_matchup(game)
            assert result["status"] in ("HIT", "SYSTEM SKIP"), \
                f"Unexpected status for {game['matchup']}: {result['status']}"

    def test_under_games_hits_or_skips(self):
        """All UNDER games should be HITs or SYSTEM SKIPs."""
        under_games = [g for g in ALL_40_GAMES if g["pick"] == "UNDER"]
        for game in under_games:
            result = self.engine.process_matchup(game)
            assert result["status"] in ("HIT", "SYSTEM SKIP"), \
                f"Unexpected status for {game['matchup']}: {result['status']}"

    def test_sea_vs_con_is_skip(self):
        """SEA vs CON (May 10) should be SYSTEM SKIP (Rule 1 — Upset Clause)."""
        result = self.engine.process_matchup(ALL_40_GAMES[13])
        assert result["status"] == "SYSTEM SKIP"
        assert "Upset Clause" in result["rule_triggered"]

    def test_por_vs_ind_is_skip(self):
        """POR vs IND (May 20) should be SYSTEM SKIP (Rule 2 — High-Variance)."""
        result = self.engine.process_matchup(ALL_40_GAMES[14])
        assert result["status"] == "SYSTEM SKIP"
        assert "High-Variance" in result["rule_triggered"]

    def test_underdog_scaled_lines_present(self):
        """Every active game should have an underdog_scaled_line."""
        for game in ALL_40_GAMES:
            result = self.engine.process_matchup(game)
            if result["status"] != "SYSTEM SKIP":
                assert "underdog_scaled_line" in result, \
                    f"Missing underdog_scaled_line for {game['matchup']}"
                assert result["underdog_scaled_line"] is not None, \
                    f"None underdog_scaled_line for {game['matchup']}"

    def test_underdog_scores_present(self):
        """Every active game should have an underdog_score."""
        for game in ALL_40_GAMES:
            result = self.engine.process_matchup(game)
            if result["status"] == "HIT":
                assert result["underdog_score"] is not None, \
                    f"Missing underdog_score for {game['matchup']}"

    def test_all_games_have_real_lines(self):
        """Every game in the dataset should have real closing lines from Covers.com."""
        for game in ALL_40_GAMES:
            assert game.get("has_real_lines") is True, \
                f"Game {game['matchup']} does not have real closing lines"

    def test_all_games_have_raw_stats(self):
        """Every game in the dataset should have raw Layer 1 stats."""
        for game in ALL_40_GAMES:
            for key in ("away_pace", "home_pace", "away_ortg", "home_drtg", "home_ortg", "away_drtg"):
                assert key in game and game[key] is not None, \
                    f"Missing {key} for {game['matchup']}"


class TestSpecificScaledLines:
    """Test exact scaled line values from the real-data specification."""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_game1_con_vs_ny_scaled(self):
        """CON vs NY: Scaled_OVER ≈ 67.651"""
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        assert abs(result["underdog_scaled_line"] - 67.651) < 0.01

    def test_game2_gs_vs_sea_scaled(self):
        """GS vs SEA: Scaled_OVER ≈ 74.375"""
        result = self.engine.process_matchup(ALL_40_GAMES[1])
        assert abs(result["underdog_scaled_line"] - 74.375) < 0.01

    def test_game3_phx_vs_lv_scaled(self):
        """PHX vs LV: Scaled_OVER ≈ 74.437"""
        result = self.engine.process_matchup(ALL_40_GAMES[2])
        assert abs(result["underdog_scaled_line"] - 74.437) < 0.01

    def test_game16_lv_vs_con_scaled(self):
        """LV vs CON: Scaled_UNDER ≈ 80.447"""
        result = self.engine.process_matchup(ALL_40_GAMES[15])
        assert abs(result["underdog_scaled_line"] - 80.447) < 0.01

    def test_game17_chi_vs_gs_scaled(self):
        """CHI vs GS: Scaled_UNDER ≈ 84.326"""
        result = self.engine.process_matchup(ALL_40_GAMES[16])
        assert abs(result["underdog_scaled_line"] - 84.326) < 0.01

    def test_game20_tor_vs_min_scaled(self):
        """TOR vs MIN: Scaled_UNDER ≈ 89.603"""
        result = self.engine.process_matchup(ALL_40_GAMES[19])
        assert abs(result["underdog_scaled_line"] - 89.603) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
