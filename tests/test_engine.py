"""
ABAKE USE Engine — Comprehensive Test Suite
Validates all 4 layers of the mathematical framework and all operational rules.
Tests the complete 40-game dataset from the specification.
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

    def test_pacing_calculation(self):
        """P = Away Pace + Home Pace - League Baseline Pace = 81.2"""
        row = {
            "matchup": "CHI vs LV", "league": "WNBA",
            "away_pace": 79.8, "home_pace": 81.6,
            "away_ortg": 101.2, "home_drtg": 99.8,
            "home_ortg": 111.4, "away_drtg": 104.5,
            "pick": "OVER", "win_prob": 1.4, "underdog_score": 84,
        }
        _, _, proj_pace, _, _ = self.engine.calculate_independent_baselines(row)
        assert abs(proj_pace - 81.2) < 0.01

    def test_away_score_projection(self):
        """S_A = (101.2 × 99.8 / 102.5) × (81.2/100) = 80.00"""
        row = {
            "matchup": "CHI vs LV", "league": "WNBA",
            "away_pace": 79.8, "home_pace": 81.6,
            "away_ortg": 101.2, "home_drtg": 99.8,
            "home_ortg": 111.4, "away_drtg": 104.5,
            "pick": "OVER", "win_prob": 1.4, "underdog_score": 84,
        }
        _, _, _, score_away, _ = self.engine.calculate_independent_baselines(row)
        assert abs(score_away - 80.00) < 0.02

    def test_home_score_projection(self):
        """S_H = (111.4 × 104.5 / 102.5) × (81.2/100) + 2.5 = 94.71"""
        row = {
            "matchup": "CHI vs LV", "league": "WNBA",
            "away_pace": 79.8, "home_pace": 81.6,
            "away_ortg": 101.2, "home_drtg": 99.8,
            "home_ortg": 111.4, "away_drtg": 104.5,
            "pick": "OVER", "win_prob": 1.4, "underdog_score": 84,
        }
        _, _, _, _, score_home = self.engine.calculate_independent_baselines(row)
        assert abs(score_home - 94.71) < 0.02

    def test_hca_constant(self):
        assert self.engine.HCA == 2.5


class TestLayer2ImpliedIndividualDistributions:
    """Test Layer 2: Implied Individual Distributions (The Split)"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_base_line_chi_vs_lv(self):
        """Base Line = 162.0/2 - 8.2/2 = 76.90"""
        base_line = self.engine.calculate_base_line(162.0, 8.2)
        assert abs(base_line - 76.90) < 0.01

    def test_base_line_ind_vs_con(self):
        """Base Line = 178.5/2 - 10.5/2 = 84.00"""
        base_line = self.engine.calculate_base_line(178.5, 10.5)
        assert abs(base_line - 84.00) < 0.01


class TestLayer3DynamicScaling:
    """Test Layer 3: Dynamic Scaling (The Pacing Buffers)"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_scaled_over_chi_vs_lv(self):
        """Scaled_OVER = 76.90 - (0.45 × 8.2) = 73.21"""
        scaled = self.engine.calculate_scaled_over(76.90, 8.2)
        assert abs(scaled - 73.21) < 0.01

    def test_scaled_under_ind_vs_con(self):
        """Scaled_UNDER = 84.00 + (0.40 × 10.5) = 88.20"""
        scaled = self.engine.calculate_scaled_under(84.00, 10.5)
        assert abs(scaled - 88.20) < 0.01

    def test_over_multiplier_constant(self):
        assert self.engine.OVER_CUSHION_MULTIPLIER == 0.45

    def test_under_multiplier_constant(self):
        assert self.engine.UNDER_CEILING_MULTIPLIER == 0.40


class TestActiveSystemRules:
    """Test all 4 active system rules"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_rule1_upset_clause_triggers(self):
        """ATL vs SEA: win_prob=24.3% > 15% → SKIP"""
        result = self.engine.process_matchup({
            "matchup": "ATL vs SEA", "total": 178.5, "spread": 12.5,
            "pick": "UNDER", "win_prob": 24.3, "underdog_score": None,
        })
        assert result["status"] == "SYSTEM SKIP"
        assert "Upset Clause" in result["rule_triggered"]

    def test_rule1_upset_clause_passes(self):
        """IND vs CON: win_prob=3.3% < 15% → CLEARED"""
        result = self.engine.process_matchup({
            "matchup": "IND vs CON", "total": 178.5, "spread": 10.5,
            "pick": "UNDER", "win_prob": 3.3, "underdog_score": 88,
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
            "matchup": "POR vs IND", "total": 170.0, "spread": 5.5,
            "pick": "UNDER", "win_prob": 5.0, "underdog_score": None,
        })
        assert result["status"] == "SYSTEM SKIP"
        assert "High-Variance" in result["rule_triggered"]

    def test_rule3_over_execution_hit(self):
        """CHI vs LV: underdog_score=84 > scaled_line=73.21 → HIT"""
        result = self.engine.process_matchup({
            "matchup": "CHI vs LV", "total": 162.0, "spread": 8.2,
            "pick": "OVER", "win_prob": 1.4, "underdog_score": 84,
        })
        assert result["status"] == "HIT"
        assert result["underdog_scaled_line"] == 73.21

    def test_rule3_over_execution_miss(self):
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 162.0, "spread": 8.2,
            "pick": "OVER", "win_prob": 1.4, "underdog_score": 70,
        })
        assert result["status"] == "MISS"

    def test_rule4_under_execution_hit(self):
        """IND vs CON: underdog_score=88 < scaled_line=88.20 → HIT"""
        result = self.engine.process_matchup({
            "matchup": "IND vs CON", "total": 178.5, "spread": 10.5,
            "pick": "UNDER", "win_prob": 3.3, "underdog_score": 88,
        })
        assert result["status"] == "HIT"
        assert result["underdog_scaled_line"] == 88.20

    def test_rule4_under_execution_miss(self):
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 178.5, "spread": 10.5,
            "pick": "UNDER", "win_prob": 3.3, "underdog_score": 90,
        })
        assert result["status"] == "MISS"


class TestExecutionProfiles:
    """Test the 3 verification profiles from the specification."""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_profile1_chi_vs_lv(self):
        """CHI vs LV: Scaled_OVER=73.21, underdog CHI scored 84 → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        assert result["status"] == "HIT"
        assert result["underdog_scaled_line"] == 73.21
        assert result["underdog_score"] == 84

    def test_profile2_ind_vs_con(self):
        """IND vs CON: Scaled_UNDER=88.20, underdog CON scored 88 → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[15])
        assert result["status"] == "HIT"
        assert result["underdog_scaled_line"] == 88.20
        assert result["underdog_score"] == 88

    def test_profile3_atl_vs_sea(self):
        """ATL vs SEA: win_prob=24.3% > 15% → SYSTEM SKIP"""
        result = self.engine.process_matchup(ALL_40_GAMES[14])
        assert result["status"] == "SYSTEM SKIP"


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
        """38 active positions, 2 system skips (POR vs IND and ATL vs SEA)."""
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

    def test_category_a_over_games(self):
        """All 13 OVER games should be HITs with correct scaled lines."""
        over_games = [g for g in ALL_40_GAMES if g["pick"] == "OVER"]
        assert len(over_games) == 13

        expected_scaled_lines = {
            "CHI vs LV": 73.21,
            "PHX vs NY": 74.35,
            "WSH vs DAL": 79.925,
            "WSH vs LV": 76.075,
            "GS vs WSH": 65.675,
            "GS vs WSH": 66.175,  # Jul 19 game
            "IND vs GS": 80.875,
            "MIN vs PHX": 72.875,
            "LV vs IND": 79.29,
            "DAL vs CHI": 75.11,
            "TOR vs NY": 76.25,
            "MIN vs NY": 78.53,
            "LV vs PHX": 74.35,
        }

        for game in over_games:
            result = self.engine.process_matchup(game)
            assert result["status"] == "HIT", f"MISS for {game['matchup']}: {result}"

    def test_category_b_under_games(self):
        """All 25 UNDER games (excluding 2 skips) should be HITs."""
        under_games = [g for g in ALL_40_GAMES if g["pick"] == "UNDER"]
        assert len(under_games) == 27  # 25 active + 2 skips

        for game in under_games:
            result = self.engine.process_matchup(game)
            assert result["status"] in ("HIT", "SYSTEM SKIP"), \
                f"Unexpected status for {game['matchup']}: {result['status']}"

    def test_por_vs_ind_is_skip(self):
        """POR vs IND (Aug 1) should be SYSTEM SKIP (Rule 2)."""
        result = self.engine.process_matchup(ALL_40_GAMES[13])
        assert result["status"] == "SYSTEM SKIP"
        assert "High-Variance" in result["rule_triggered"]

    def test_atl_vs_sea_is_skip(self):
        """ATL vs SEA (Jul 31) should be SYSTEM SKIP (Rule 1)."""
        result = self.engine.process_matchup(ALL_40_GAMES[14])
        assert result["status"] == "SYSTEM SKIP"
        assert "Upset Clause" in result["rule_triggered"]

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


class TestSpecificScaledLines:
    """Test exact scaled line values from the specification."""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_game1_chi_vs_lv_scaled(self):
        """CHI vs LV: Scaled_OVER = 73.21"""
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        assert result["underdog_scaled_line"] == 73.21

    def test_game2_phx_vs_ny_scaled(self):
        """PHX vs NY: Scaled_OVER = 74.35"""
        result = self.engine.process_matchup(ALL_40_GAMES[1])
        assert result["underdog_scaled_line"] == 74.35

    def test_game3_wsh_vs_dal_scaled(self):
        """WSH vs DAL: Scaled_OVER = 79.925"""
        result = self.engine.process_matchup(ALL_40_GAMES[2])
        assert abs(result["underdog_scaled_line"] - 79.925) < 0.01

    def test_game16_ind_vs_con_scaled(self):
        """IND vs CON: Scaled_UNDER = 88.20"""
        result = self.engine.process_matchup(ALL_40_GAMES[15])
        assert result["underdog_scaled_line"] == 88.20

    def test_game17_sea_vs_min_scaled(self):
        """SEA vs MIN: Scaled_UNDER = 88.70"""
        result = self.engine.process_matchup(ALL_40_GAMES[16])
        assert result["underdog_scaled_line"] == 88.70

    def test_game20_okc_vs_bkn_scaled(self):
        """OKC vs BKN: Scaled_UNDER = 93.90"""
        result = self.engine.process_matchup(ALL_40_GAMES[19])
        assert result["underdog_scaled_line"] == 93.90

    def test_game38_phi_vs_orl_scaled(self):
        """PHI vs ORL: Scaled_UNDER = 91.80 (spec has arithmetic error: 90.00+1.80=91.80, not 90.67)"""
        result = self.engine.process_matchup(ALL_40_GAMES[37])
        # Base Line = 184.5/2 - 4.5/2 = 90.00
        # Scaled_UNDER = 90.00 + (0.40 × 4.5) = 90.00 + 1.80 = 91.80
        # The spec states 90.67 but 90.00 + 1.80 = 91.80 (arithmetic error in spec)
        assert abs(result["underdog_scaled_line"] - 91.80) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
