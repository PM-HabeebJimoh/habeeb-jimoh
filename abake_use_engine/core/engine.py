"""
ABAKE USE Engine — Dynamic Pacing and Possession Scaling Engine
Enterprise-Grade Basketball Game Analysis System

Implements the complete mathematical framework from the Ultimate Master Blueprint:
  Layer 1: Independent Baseline Infrastructure (Log-Linear Possession Regression)
  Layer 2: Implied Individual Distributions (The Split)
  Layer 3: Dynamic Scaling (The Pacing Buffers)
  Active System Rules 1-4

The engine computes the UNDERDOG INDIVIDUAL TEAM TOTAL scaled line
for every game, then compares the underdog's actual score against it.
"""

import math
import logging
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("abake_use_engine")


class AbakeUseEngine:
    """
    Production-grade ABAKE USE framework engine.
    
    100% Underdog Scoring Engine — computes scaled individual underdog
    lines for every basketball matchup using the exact formulas from
    the ABAKE USE specification.
    """

    # Home Court Advantage constant (points)
    HCA = 2.5

    # Dynamic scaling multipliers
    OVER_CUSHION_MULTIPLIER = 0.45
    UNDER_CEILING_MULTIPLIER = 0.40

    # Upset clause threshold
    UPSET_PROBABILITY_THRESHOLD = 15.0

    # High-variance chaos matches to skip (Rule 2)
    CHAOS_MATCHUPS = {"POR vs IND"}

    def __init__(
        self,
        wnba_pace: float = 80.2,
        wnba_eff: float = 102.5,
        sl_pace: float = 84.5,
        sl_eff: float = 98.2,
        nba_pace: float = 100.4,
        nba_eff: float = 113.5,
    ):
        # Establish the league constant anchors
        self.constants = {
            "WNBA": {"lg_pace": wnba_pace, "lg_eff": wnba_eff},
            "Summer": {"lg_pace": sl_pace, "lg_eff": sl_eff},
            "NBA": {"lg_pace": nba_pace, "lg_eff": nba_eff},
        }
        logger.info(
            "ABAKE USE Engine initialized — WNBA Pace=%.1f, Eff=%.1f | "
            "Summer Pace=%.1f, Eff=%.1f",
            wnba_pace, wnba_eff, sl_pace, sl_eff,
        )

    # ------------------------------------------------------------------ #
    # Layer 1: Independent Baseline Infrastructure                        #
    # ------------------------------------------------------------------ #

    def calculate_independent_baselines(self, row: dict) -> tuple:
        """
        Generate independent Game Totals and Spreads from raw analytics inputs.
        Log-Linear Possession Regression.

        Formulas:
            P  = Away Pace + Home Pace - League Baseline Pace
            S_A = (Away ORtg × Home DRtg / League Eff) × (P / 100)
            S_H = (Home ORtg × Away DRtg / League Eff) × (P / 100) + HCA
            Model Game Total  = S_A + S_H
            Model Spread = S_H - S_A

        Returns: (model_total, model_spread, proj_pace, score_away, score_home)
        """
        league = row.get("league", "WNBA")
        if league not in self.constants:
            league = "WNBA"

        lg_pace = self.constants[league]["lg_pace"]
        lg_eff = self.constants[league]["lg_eff"]

        # Projected Game Pacing
        proj_pace = row["away_pace"] + row["home_pace"] - lg_pace

        # Projected Individual Team Scores
        score_away = (
            (row["away_ortg"] * row["home_drtg"]) / lg_eff
        ) * (proj_pace / 100)

        score_home = (
            ((row["home_ortg"] * row["away_drtg"]) / lg_eff) * (proj_pace / 100)
        ) + self.HCA

        # Final Core Baselines
        model_total = score_away + score_home
        model_spread = score_home - score_away

        return model_total, model_spread, proj_pace, score_away, score_home

    # ------------------------------------------------------------------ #
    # Layer 2: Implied Individual Distributions (The Split)              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def calculate_base_line(total: float, spread: float) -> float:
        """
        Base Line = (Model Total / 2) - (Model Spread / 2)
        
        This isolates the underdog's default share of the total.
        """
        return (total / 2) - (abs(spread) / 2)

    # ------------------------------------------------------------------ #
    # Layer 3: Dynamic Scaling (The Pacing Buffers)                       #
    # ------------------------------------------------------------------ #

    def calculate_scaled_over(self, base_line: float, spread: float) -> float:
        """
        Scaled_OVER = Base Line - (0.45 × Model Spread)
        
        Used when model projects OVER. Lowers the required target roof
        to ensure high-pace volatility does not cause a loss if a
        trailing team slows down late.
        """
        return base_line - (self.OVER_CUSHION_MULTIPLIER * abs(spread))

    def calculate_scaled_under(self, base_line: float, spread: float) -> float:
        """
        Scaled_UNDER = Base Line + (0.40 × Model Spread)
        
        Used when model projects UNDER. Expands the defensive ceiling
        upward to absorb late-game free throws.
        """
        return base_line + (self.UNDER_CEILING_MULTIPLIER * abs(spread))

    # ------------------------------------------------------------------ #
    # Active System Rules (Part 3)                                        #
    # ------------------------------------------------------------------ #

    def check_upset_clause(self, pick: str, win_prob: float) -> dict | None:
        """
        Rule 1: The Outright Probability Cap (Upset Clause)
        If pick is UNDER and underdog win probability > 15%, SKIP.
        """
        if pick == "UNDER" and win_prob > self.UPSET_PROBABILITY_THRESHOLD:
            return {
                "rule": "Rule 1 — Upset Clause",
                "action": "SKIP",
                "reason": (
                    f"Underdog Win Prob ({win_prob}%) exceeds the "
                    f"{self.UPSET_PROBABILITY_THRESHOLD}% threshold"
                ),
            }
        return None

    def check_chaos_exemption(self, matchup: str, total: float) -> dict | None:
        """
        Rule 2: The Structural Outlier Exemption
        Skip high-variance chaos matches or games with incomplete data.
        """
        if matchup in self.CHAOS_MATCHUPS:
            return {
                "rule": "Rule 2 — High-Variance Exemption",
                "action": "SKIP",
                "reason": f"High-variance chaos signature: {matchup}",
            }
        if isinstance(total, float) and np.isnan(total):
            return {
                "rule": "Rule 2 — Data Omission",
                "action": "SKIP",
                "reason": "Incomplete tracking block (missing parameters)",
            }
        return None

    # ------------------------------------------------------------------ #
    # Full Matchup Processing Pipeline                                    #
    # ------------------------------------------------------------------ #

    def process_matchup(self, row: dict) -> dict[str, Any]:
        """
        Execute the complete ABAKE USE rule book over a data row.
        
        For every game, the engine computes:
          1. Model Game Total and Model Spread (from Layer 1 or provided)
          2. Base Line (underdog's implied share)
          3. Scaled Underdog Line (the actual betting target)
          4. Whether the underdog's actual score clears the scaled line
        
        Returns a comprehensive result with ALL intermediate values.
        """
        matchup = row.get("matchup", "UNKNOWN")
        pick = row.get("pick", "OVER")
        win_prob = row.get("win_prob", 0.0)
        underdog = row.get("underdog", "")
        underdog_score = row.get("underdog_score", row.get("actual_score", None))

        # ---- Layer 1: Independent Baselines (if raw metrics available) ----
        independent_total = None
        independent_spread = None
        proj_pace = None
        score_away = None
        score_home = None

        if all(k in row and row[k] is not None for k in
               ("away_pace", "home_pace", "away_ortg", "home_drtg", "home_ortg", "away_drtg")):
            independent_total, independent_spread, proj_pace, score_away, score_home = (
                self.calculate_independent_baselines(row)
            )

        # ---- Determine Model Total and Model Spread ----
        # These are the Layer 1 outputs used for Layer 2 and Layer 3
        total = row.get("total", None)
        spread = row.get("spread", None)

        # If not provided, use independent baselines
        if total is None and independent_total is not None:
            total = round(independent_total * 2) / 2
        if spread is None and independent_spread is not None:
            spread = abs(round(independent_spread * 2) / 2)

        if total is None or spread is None:
            return {
                "matchup": matchup,
                "status": "SYSTEM SKIP",
                "rule_triggered": "Rule 2 — Data Omission",
                "details": "Missing model total and/or spread",
                "underdog": underdog,
                "underdog_score": underdog_score,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Ensure spread is absolute value (positive)
        spread = abs(spread)

        # ---- Rule 2: Chaos Exemption ----
        chaos_result = self.check_chaos_exemption(matchup, total)
        if chaos_result:
            return {
                "matchup": matchup,
                "status": "SYSTEM SKIP",
                "rule_triggered": chaos_result["rule"],
                "details": chaos_result["reason"],
                "model_total": total,
                "model_spread": spread,
                "underdog": underdog,
                "underdog_score": underdog_score,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # ---- Rule 1: Upset Clause ----
        upset_result = self.check_upset_clause(pick, win_prob)
        if upset_result:
            return {
                "matchup": matchup,
                "status": "SYSTEM SKIP",
                "rule_triggered": upset_result["rule"],
                "details": upset_result["reason"],
                "model_total": total,
                "model_spread": spread,
                "underdog": underdog,
                "underdog_score": underdog_score,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # ---- Layer 2: Implied Individual Distribution (Base Line) ----
        base_line = self.calculate_base_line(total, spread)

        # ---- Layer 3: Dynamic Scaling & Execution ----
        if pick == "OVER":
            # Rule 3: The Over Execution
            scaled_line = self.calculate_scaled_over(base_line, spread)
            if underdog_score is not None:
                is_hit = underdog_score > scaled_line
                status = "HIT" if is_hit else "MISS"
            else:
                is_hit = None
                status = "PENDING"

            return {
                "matchup": matchup,
                "status": status,
                "rule_triggered": "Rule 3 — Over Execution",
                "category": "OVER",
                # Layer 1 outputs
                "model_total": total,
                "model_spread": spread,
                "independent_total": round(independent_total, 2) if independent_total else None,
                "independent_spread": round(independent_spread, 2) if independent_spread else None,
                # Layer 2 output
                "base_line": round(base_line, 2),
                # Layer 3 output — THE UNDERDOG SCALED LINE
                "underdog_scaled_line": round(scaled_line, 3),
                "underdog": underdog,
                "underdog_score": underdog_score,
                # Verification
                "is_hit": is_hit,
                "details": (
                    f"Underdog {underdog} OVER {scaled_line:.3f} | "
                    f"Actual: {underdog_score} | "
                    f"{'✓ CLEARS' if is_hit else '✗ FAILS'}"
                    if underdog_score is not None
                    else f"Underdog {underdog} OVER {scaled_line:.3f} | Awaiting result"
                ),
                # Layer 1 raw (if available)
                "proj_pace": proj_pace,
                "score_away": round(score_away, 2) if score_away else None,
                "score_home": round(score_home, 2) if score_home else None,
                "win_prob": win_prob,
                "timestamp": datetime.utcnow().isoformat(),
            }

        elif pick == "UNDER":
            # Rule 4: The Under Execution
            scaled_line = self.calculate_scaled_under(base_line, spread)
            if underdog_score is not None:
                is_hit = underdog_score < scaled_line
                status = "HIT" if is_hit else "MISS"
            else:
                is_hit = None
                status = "PENDING"

            return {
                "matchup": matchup,
                "status": status,
                "rule_triggered": "Rule 4 — Under Execution",
                "category": "UNDER",
                # Layer 1 outputs
                "model_total": total,
                "model_spread": spread,
                "independent_total": round(independent_total, 2) if independent_total else None,
                "independent_spread": round(independent_spread, 2) if independent_spread else None,
                # Layer 2 output
                "base_line": round(base_line, 2),
                # Layer 3 output — THE UNDERDOG SCALED LINE
                "underdog_scaled_line": round(scaled_line, 3),
                "underdog": underdog,
                "underdog_score": underdog_score,
                # Verification
                "is_hit": is_hit,
                "details": (
                    f"Underdog {underdog} UNDER {scaled_line:.3f} | "
                    f"Actual: {underdog_score} | "
                    f"{'✓ STAYS BELOW' if is_hit else '✗ EXCEEDS'}"
                    if underdog_score is not None
                    else f"Underdog {underdog} UNDER {scaled_line:.3f} | Awaiting result"
                ),
                # Layer 1 raw (if available)
                "proj_pace": proj_pace,
                "score_away": round(score_away, 2) if score_away else None,
                "score_home": round(score_home, 2) if score_home else None,
                "win_prob": win_prob,
                "timestamp": datetime.utcnow().isoformat(),
            }

        else:
            return {
                "matchup": matchup,
                "status": "ERROR",
                "details": f"Invalid pick value: {pick}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    # ------------------------------------------------------------------ #
    # Batch Processing                                                    #
    # ------------------------------------------------------------------ #

    def process_batch(self, data: list[dict] | pd.DataFrame) -> pd.DataFrame:
        """Process an entire batch of matchups and return a DataFrame."""
        if isinstance(data, pd.DataFrame):
            rows = data.to_dict("records")
        else:
            rows = data

        results = []
        for row in rows:
            result = self.process_matchup(row)
            results.append(result)

        return pd.DataFrame(results)

    def compute_summary(self, results_df: pd.DataFrame) -> dict:
        """Compute the ABAKE USE Matrix Summary from processed results."""
        total_rows = len(results_df)
        active = results_df[results_df["status"] != "SYSTEM SKIP"]
        skipped = results_df[results_df["status"] == "SYSTEM SKIP"]
        hits = results_df[results_df["status"] == "HIT"]
        misses = results_df[results_df["status"] == "MISS"]
        pending = results_df[results_df["status"] == "PENDING"]

        active_count = len(active)
        hit_count = len(hits)
        miss_count = len(misses)
        skip_count = len(skipped)
        pending_count = len(pending)

        win_rate = (hit_count / active_count * 100) if active_count > 0 else 0.0

        return {
            "total_matchups": total_rows,
            "active_bets": active_count,
            "system_skips": skip_count,
            "validated_wins": hit_count,
            "losses": miss_count,
            "pending": pending_count,
            "win_rate_pct": round(win_rate, 1),
            "timestamp": datetime.utcnow().isoformat(),
        }
