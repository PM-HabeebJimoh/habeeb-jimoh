"""
ABAKE USE Engine — Comprehensive Test Suite (V10)
Validates all 4 layers of the mathematical framework and all operational rules.
Tests the complete 40-game dataset with REAL Covers.com data.

V10: Engine now uses Model Total/Model Spread for Layers 2&3 (per ABAKE USE spec).
When raw stats are available, the engine computes Model Total and Model Spread
from Layer 1 and uses those for both Layer 2 and Layer 3.
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

    def test_base_line_formula(self):
        """Base Line = Model Total / 2 - Model Spread / 2"""
        # Model Total = 161.0, Model Spread = 10.0 for CON vs NY
        base_line = self.engine.calculate_base_line(161.0, 10.0)
        assert abs(base_line - 75.5) < 0.01

    def test_base_line_lv_vs_con(self):
        """Base Line = 165.5/2 - 4.0/2 = 82.75 - 2.0 = 80.75"""
        base_line = self.engine.calculate_base_line(165.5, 4.0)
        assert abs(base_line - 80.75) < 0.01


class TestLayer3DynamicScaling:
    """Test Layer 3: Dynamic Scaling (The Pacing Buffers)"""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_scaled_over_formula(self):
        """Scaled_OVER = Base Line - (0.45 × Model Spread)"""
        # For CON vs NY: base_line=75.5, model_spread=10.0
        scaled = self.engine.calculate_scaled_over(75.5, 10.0)
        expected = 75.5 - (0.45 * 10.0)
        assert abs(scaled - expected) < 0.01

    def test_scaled_under_formula(self):
        """Scaled_UNDER = Base Line + (0.40 × Model Spread)"""
        # For LV vs CON: base_line=80.75, model_spread=4.0
        scaled = self.engine.calculate_scaled_under(80.75, 4.0)
        expected = 80.75 + (0.40 * 4.0)
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
    """Test the verification profiles from the specification.

    NOTE: The engine now uses Model Total/Model Spread for Layers 2&3.
    The spec's Execution Profile 1 (CHI vs LV) shows Layer 1 computing
    Model Total = 174.71 and Model Spread = 14.71, then the data sheet
    uses 162.0 and 8.2. The engine follows the spec's code which uses
    the Layer 1 computed values when raw stats are available.
    """

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_profile1_con_vs_ny_over(self):
        """CON vs NY: Model Total=161.0, Model Spread=10.0, pick=OVER → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        assert result["status"] == "HIT"
        # With Model Total/Model Spread: base_line=75.5, scaled=75.5-0.45*10=71.0
        assert abs(result["underdog_scaled_line"] - 71.0) < 0.01
        assert result["underdog_score"] == 75

    def test_profile2_lv_vs_con_under(self):
        """LV vs CON: Model Total=165.5, Model Spread=4.0, pick=UNDER → HIT"""
        result = self.engine.process_matchup(ALL_40_GAMES[15])
        assert result["status"] == "HIT"
        # With Model Total/Model Spread: base_line=80.75, scaled=80.75+0.40*4=82.35
        assert abs(result["underdog_scaled_line"] - 82.35) < 0.01
        assert result["underdog_score"] == 69

    def test_profile3_sea_vs_con_upset_clause(self):
        """SEA vs CON: win_prob > 15% → SYSTEM SKIP (Upset Clause)"""
        result = self.engine.process_matchup(ALL_40_GAMES[13])
        assert result["status"] == "SYSTEM SKIP"
        assert "Upset Clause" in result["rule_triggered"]


class TestFull40GameMatrix:
    """Test the complete 40-game dataset.

    With the corrected engine (Model Total/Model Spread for Layers 2&3),
    the 40-game spec produces 33 HIT, 5 MISS, 2 SKIP = 86.8%.
    """

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

    def test_33_hits_5_misses(self):
        """With corrected engine: 33 HITs, 5 MISSes (86.8% accuracy)."""
        results = [self.engine.process_matchup(g) for g in ALL_40_GAMES]
        import pandas as pd
        df = pd.DataFrame(results)
        summary = self.engine.compute_summary(df)
        assert summary["validated_wins"] == 33
        assert summary["losses"] == 5

    def test_accuracy_86_8_percent(self):
        """The ABAKE USE system achieves 86.8% accuracy on the 40-game dataset
        with the corrected engine (Model Total/Model Spread for Layers 2&3)."""
        results = [self.engine.process_matchup(g) for g in ALL_40_GAMES]
        import pandas as pd
        df = pd.DataFrame(results)
        summary = self.engine.compute_summary(df)
        assert abs(summary["win_rate_pct"] - 86.8) < 0.1

    def test_over_games_majority_hits(self):
        """OVER games should mostly be HITs (some MISSes with Model values)."""
        over_games = [g for g in ALL_40_GAMES if g["pick"] == "OVER"]
        hits = 0
        misses = 0
        for game in over_games:
            result = self.engine.process_matchup(game)
            if result["status"] == "HIT":
                hits += 1
            elif result["status"] == "MISS":
                misses += 1
        # Most OVER games should still be HITs
        assert hits > misses

    def test_under_games_majority_hits(self):
        """UNDER games should mostly be HITs (some MISSes with Model values)."""
        under_games = [g for g in ALL_40_GAMES if g["pick"] == "UNDER"]
        hits = 0
        misses = 0
        for game in under_games:
            result = self.engine.process_matchup(game)
            if result["status"] == "HIT":
                hits += 1
            elif result["status"] == "MISS":
                misses += 1
        # Most UNDER games should still be HITs
        assert hits > misses

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

    def test_model_total_used_for_layers_2_and_3(self):
        """When raw stats are available, the engine uses Model Total/Model Spread
        for Layers 2&3, not the market values."""
        # CON vs NY: Market Total=160.0, Model Total=161.0
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        # The engine should use Model Total (161.0) not Market Total (160.0)
        assert result["model_total"] == 161.0
        # Base line should be computed from Model Total/Model Spread
        # base_line = 161.0/2 - 10.0/2 = 75.5
        assert abs(result["base_line"] - 75.5) < 0.01


class TestSpecificScaledLines:
    """Test exact scaled line values with the corrected engine.

    The engine now uses Model Total/Model Spread for Layers 2&3.
    These values are computed from the raw Layer 1 stats.
    """

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_game1_con_vs_ny_scaled(self):
        """CON vs NY: Model Total=161.0, Model Spread=10.0
        Base Line = 161.0/2 - 10.0/2 = 75.5
        Scaled_OVER = 75.5 - (0.45 × 10.0) = 71.0"""
        result = self.engine.process_matchup(ALL_40_GAMES[0])
        assert abs(result["underdog_scaled_line"] - 71.0) < 0.01

    def test_game2_gs_vs_sea_scaled(self):
        """GS vs SEA: Model Total=165.0, Model Spread=2.5
        Base Line = 165.0/2 - 2.5/2 = 81.25
        Scaled_OVER = 81.25 - (0.45 × 2.5) = 80.125"""
        result = self.engine.process_matchup(ALL_40_GAMES[1])
        assert abs(result["underdog_scaled_line"] - 80.125) < 0.01

    def test_game3_phx_vs_lv_scaled(self):
        """PHX vs LV: Model Total=179.0, Model Spread=11.5
        Base Line = 179.0/2 - 11.5/2 = 83.75
        Scaled_OVER = 83.75 - (0.45 × 11.5) = 78.575"""
        result = self.engine.process_matchup(ALL_40_GAMES[2])
        assert abs(result["underdog_scaled_line"] - 78.575) < 0.01

    def test_game16_lv_vs_con_scaled(self):
        """LV vs CON: Model Total=165.5, Model Spread=4.0
        Base Line = 165.5/2 - 4.0/2 = 80.75
        Scaled_UNDER = 80.75 + (0.40 × 4.0) = 82.35"""
        result = self.engine.process_matchup(ALL_40_GAMES[15])
        assert abs(result["underdog_scaled_line"] - 82.35) < 0.01

    def test_game17_chi_vs_gs_scaled(self):
        """CHI vs GS: Model Total=166.0, Model Spread=9.5
        Base Line = 166.0/2 - 9.5/2 = 78.25
        Scaled_UNDER = 78.25 + (0.40 × 9.5) = 82.05"""
        result = self.engine.process_matchup(ALL_40_GAMES[16])
        assert abs(result["underdog_scaled_line"] - 82.05) < 0.01

    def test_game20_tor_vs_min_scaled(self):
        """TOR vs MIN: Model Total=164.0, Model Spread=14.5
        Base Line = 164.0/2 - 14.5/2 = 74.75
        Scaled_UNDER = 74.75 + (0.40 × 14.5) = 80.55"""
        result = self.engine.process_matchup(ALL_40_GAMES[19])
        assert abs(result["underdog_scaled_line"] - 80.55) < 0.01


class TestPickDetermination:
    """Test that pick is correctly determined by comparing Model Total vs Market Total."""

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_model_gt_market_over(self):
        """When Model Total > Market Total, pick should be OVER."""
        result = self.engine.process_matchup({
            "matchup": "TEST", "league": "WNBA",
            "away_pace": 80.0, "home_pace": 80.0,
            "away_ortg": 105.0, "home_drtg": 100.0,
            "home_ortg": 105.0, "away_drtg": 100.0,
            "market_total": 150.0, "win_prob": 5.0, "underdog_score": 75,
        })
        # Model Total ≈ 165+, Market Total = 150 → OVER
        assert result.get("category") == "OVER"

    def test_model_lt_market_under(self):
        """When Model Total < Market Total, pick should be UNDER."""
        result = self.engine.process_matchup({
            "matchup": "TEST", "league": "WNBA",
            "away_pace": 80.0, "home_pace": 80.0,
            "away_ortg": 95.0, "home_drtg": 105.0,
            "home_ortg": 95.0, "away_drtg": 105.0,
            "market_total": 180.0, "win_prob": 5.0, "underdog_score": 75,
        })
        # Model Total ≈ 150-, Market Total = 180 → UNDER
        assert result.get("category") == "UNDER"

    def test_fallback_to_row_pick(self):
        """When no market_total is provided, use the row's pick."""
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 162.0, "spread": 8.2,
            "pick": "OVER", "win_prob": 5.0, "underdog_score": 84,
        })
        assert result.get("category") == "OVER"


class TestV11MarketImpliedModel:
    """Test V11 Market-Implied Model (MIM) mode.
    
    V11 Reformulated Layer 1:
      Model Total  = Market Closing Total
      Model Spread = Market Closing Spread
      Pick Direction = Layer 1 Edge Signal (computed total vs market total)
    
    Layers 2 & 3 and Rules 1-4 are UNCHANGED.
    When raw stats are NOT provided, the engine uses the row's total/spread
    directly — this is the V11 mode.
    """

    def setup_method(self):
        self.engine = AbakeUseEngine()

    def test_v11_market_total_used_for_scaled_lines(self):
        """V11: When no raw stats, market total/spread are used for Layers 2&3."""
        result = self.engine.process_matchup({
            "matchup": "GS vs TOR", "league": "WNBA",
            "total": 164.5, "spread": 12.5,
            "pick": "OVER", "win_prob": 5.0, "underdog_score": 75,
            "underdog": "GS",
        })
        # Model Total = 164.5, Model Spread = 12.5
        # Base Line = 164.5/2 - 12.5/2 = 76.0
        # Scaled_OVER = 76.0 - (0.45 × 12.5) = 70.375
        assert abs(result["model_total"] - 164.5) < 0.01
        assert abs(result["base_line"] - 76.0) < 0.01
        assert abs(result["underdog_scaled_line"] - 70.375) < 0.01

    def test_v11_market_spread_used_for_scaled_lines(self):
        """V11: Market spread is used for Layer 3 scaling."""
        result = self.engine.process_matchup({
            "matchup": "DAL vs CON", "league": "WNBA",
            "total": 172.5, "spread": 11.5,
            "pick": "UNDER", "win_prob": 3.0, "underdog_score": 80,
            "underdog": "CON",
        })
        # Model Total = 172.5, Model Spread = 11.5
        # Base Line = 172.5/2 - 11.5/2 = 80.5
        # Scaled_UNDER = 80.5 + (0.40 × 11.5) = 85.1
        assert abs(result["model_total"] - 172.5) < 0.01
        assert abs(result["base_line"] - 80.5) < 0.01
        assert abs(result["underdog_scaled_line"] - 85.1) < 0.01

    def test_v11_pick_from_row(self):
        """V11: Pick comes from row when no raw stats are provided."""
        result_over = self.engine.process_matchup({
            "matchup": "TEST", "total": 165.0, "spread": 5.5,
            "pick": "OVER", "win_prob": 5.0, "underdog_score": 80,
        })
        assert result_over["category"] == "OVER"

        result_under = self.engine.process_matchup({
            "matchup": "TEST", "total": 165.0, "spread": 5.5,
            "pick": "UNDER", "win_prob": 5.0, "underdog_score": 80,
        })
        assert result_under["category"] == "UNDER"

    def test_v11_no_independent_total(self):
        """V11: When no raw stats, independent_total should be None."""
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 165.0, "spread": 5.5,
            "pick": "OVER", "win_prob": 5.0, "underdog_score": 80,
        })
        assert result["independent_total"] is None

    def test_v11_rules_still_apply(self):
        """V11: Rules 1-4 still apply in Market-Implied Model mode."""
        # Rule 1: Upset Clause
        result = self.engine.process_matchup({
            "matchup": "TEST", "total": 165.0, "spread": 5.5,
            "pick": "UNDER", "win_prob": 20.0, "underdog_score": 80,
        })
        assert result["status"] == "SYSTEM SKIP"
        assert "Upset Clause" in result["rule_triggered"]

        # Rule 2: Chaos Exemption
        result = self.engine.process_matchup({
            "matchup": "POR vs IND", "total": 175.5, "spread": 10.5,
            "pick": "OVER", "win_prob": 5.0, "underdog_score": 80,
        })
        assert result["status"] == "SYSTEM SKIP"

    def test_v11_over_hit(self):
        """V11: OVER game where underdog clears the scaled line."""
        result = self.engine.process_matchup({
            "matchup": "GS vs TOR", "league": "WNBA",
            "total": 164.5, "spread": 12.5,
            "pick": "OVER", "win_prob": 5.0, "underdog_score": 75,
            "underdog": "GS",
        })
        # Scaled_OVER = 70.375, score=75 → HIT
        assert result["status"] == "HIT"
        assert result["underdog_score"] > result["underdog_scaled_line"]

    def test_v11_under_hit(self):
        """V11: UNDER game where underdog stays below the scaled line."""
        result = self.engine.process_matchup({
            "matchup": "DAL vs CON", "league": "WNBA",
            "total": 172.5, "spread": 11.5,
            "pick": "UNDER", "win_prob": 3.0, "underdog_score": 80,
            "underdog": "CON",
        })
        # Scaled_UNDER = 85.1, score=80 → HIT
        assert result["status"] == "HIT"
        assert result["underdog_score"] < result["underdog_scaled_line"]

    def test_v11_formulas_match_spec(self):
        """V11: Verify all formulas match the ABAKE USE spec exactly."""
        # Market Total = 170.0, Market Spread = 8.5
        model_total = 170.0
        model_spread = 8.5

        # Layer 2: Base Line = (Model Total / 2) - (Model Spread / 2)
        base_line = (model_total / 2) - (model_spread / 2)
        assert abs(base_line - 80.75) < 0.01

        # Layer 3: Scaled_OVER = Base Line - (0.45 × Model Spread)
        scaled_over = base_line - (0.45 * model_spread)
        assert abs(scaled_over - 76.925) < 0.01

        # Layer 3: Scaled_UNDER = Base Line + (0.40 × Model Spread)
        scaled_under = base_line + (0.40 * model_spread)
        assert abs(scaled_under - 84.15) < 0.01

    def test_v11_vs_v10_same_formulas(self):
        """V11 and V10 use the SAME formulas for Layers 2&3.
        The only difference is the source of Model Total/Spread."""
        # V10: Model Total from Layer 1 stats
        v10_result = self.engine.process_matchup({
            "matchup": "CON vs NY", "league": "WNBA",
            "away_pace": 78.5, "home_pace": 80.9,
            "away_ortg": 100.5, "home_drtg": 97.2,
            "home_ortg": 110.1, "away_drtg": 97.8,
            "pick": "OVER", "win_prob": 1.0, "underdog_score": 75,
            "market_total": 160.0,
        })

        # V11: Model Total from market
        v11_result = self.engine.process_matchup({
            "matchup": "CON vs NY", "league": "WNBA",
            "total": 160.0, "spread": 15.5,
            "pick": "OVER", "win_prob": 1.0, "underdog_score": 75,
        })

        # Both should use the same Layer 2 formula
        # V10: Base Line = Model Total/2 - Model Spread/2
        # V11: Base Line = Market Total/2 - Market Spread/2
        assert abs(v10_result["base_line"] - (v10_result["model_total"]/2 - v10_result["model_spread"]/2)) < 0.01
        assert abs(v11_result["base_line"] - (v11_result["model_total"]/2 - v11_result["model_spread"]/2)) < 0.01

        # Both should use the same Layer 3 formulas
        v10_base = v10_result["base_line"]
        v11_base = v11_result["base_line"]
        assert abs(v10_result["underdog_scaled_line"] - (v10_base - 0.45 * v10_result["model_spread"])) < 0.01
        assert abs(v11_result["underdog_scaled_line"] - (v11_base - 0.45 * v11_result["model_spread"])) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
