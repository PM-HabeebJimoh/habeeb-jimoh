"""
ABAKE USE Engine — Dynamic Pacing and Possession Scaling Engine
Enterprise-Grade Basketball Game Analysis System

Implements the complete mathematical framework from the Ultimate Master Blueprint:
  Layer 1: Independent Baseline Infrastructure (Log-Linear Possession Regression)
  Layer 2: Implied Individual Distributions (The Split) — uses Model Total & Model Spread
  Layer 3: Dynamic Scaling (The Pacing Buffers) — uses Model Spread
  Active System Rules 1-4

The engine computes the UNDERDOG INDIVIDUAL TEAM TOTAL scaled line
for every game, then compares the underdog's actual score against it.

KEY ARCHITECTURE (from the spec):
  - Layer 1 computes Model Game Total and Model Spread from raw team stats
  - Layer 2 uses Model Total and Model Spread (NOT market lines)
  - Layer 3 uses Model Spread (same as Layer 2)
  - The "pick" (OVER/UNDER) is determined by comparing Model Total vs Market Total
  - Market total and market spread are used ONLY for pick determination

V11 MARKET-IMPLIED MODEL (MIM):
  When market closing lines are available, the engine can use them as the
  Model Total and Model Spread instead of computing from stale team stats.
  This is the V11 Market-Implied Model approach:
    - Model Total  = Market Closing Total   (best estimate of game total)
    - Model Spread = Market Closing Spread   (best estimate of point spread)
    - Pick Direction = Layer 1 Edge Signal (computed total vs market total)
  To use V11 mode, provide 'total' and 'spread' in the row dict (set to market
  values) WITHOUT providing raw stats (away_pace, home_pace, etc.).
  The engine's fallback mechanism will use the row's total/spread directly.
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
        Uses Model Total and Model Spread from Layer 1.
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
        
        ABAKE USE spec flow:
          1. Layer 1: Compute Model Game Total and Model Spread from raw stats
          2. Pick determination: Compare Model Total vs Market Total
             - Model Total > Market Total → OVER
             - Model Total < Market Total → UNDER
          3. Layer 2: Base Line = Model Total / 2 - Model Spread / 2
          4. Layer 3: Scaled_OVER = Base Line - (0.45 × Model Spread)
                     Scaled_UNDER = Base Line + (0.40 × Model Spread)
          5. Rules 1-4: Upset clause, chaos exemption, over/under execution
          6. Check: Does underdog actual score clear the scaled line?
        
        The row dict can contain:
          - Raw stats: away_pace, home_pace, away_ortg, home_drtg, home_ortg, away_drtg
          - Market data: market_total, market_spread (for pick determination)
          - OR pre-determined: pick, total, spread (for backward compatibility)
          - Game info: matchup, league, underdog, underdog_score/actual_score, win_prob
        """
        matchup = row.get("matchup", "UNKNOWN")
        underdog = row.get("underdog", "")
        underdog_score = row.get("underdog_score", row.get("actual_score", None))
        win_prob = row.get("win_prob", 0.0)

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
        # ABAKE USE spec: When raw stats are available (Layer 1 computed),
        # ALWAYS use the model-computed total and spread for Layer 2 and Layer 3.
        # This matches the spec's code:
        #   if 'away_pace' in row:
        #       total, spread = self.calculate_independent_baselines(row)
        #   else:
        #       total, spread = row['total'], row['spread']
        if independent_total is not None:
            # Layer 1 computed model values — use them for Layer 2 and Layer 3
            total = round(independent_total * 2) / 2
            spread = abs(round(independent_spread * 2) / 2)
        else:
            # No raw stats — use the row's total and spread as fallback
            total = row.get("total", None)
            spread = row.get("spread", None)

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

        # ---- Pick Determination ----
        # ABAKE USE spec: Compare Model Total vs Market Total to determine pick
        # Model Total > Market Total → OVER (model thinks more points)
        # Model Total < Market Total → UNDER (model thinks fewer points)
        # If market_total is not provided, use the row's pre-determined pick
        market_total = row.get("market_total", None)
        if market_total is not None and independent_total is not None:
            # Determine pick from Model Total vs Market Total
            pick = "OVER" if independent_total > market_total else "UNDER"
        else:
            # Fallback to row's pick (backward compatibility)
            pick = row.get("pick", "OVER")

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
                "market_total": market_total,
                "pick": pick,
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
                "market_total": market_total,
                "pick": pick,
                "underdog": underdog,
                "underdog_score": underdog_score,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # ---- Layer 2: Implied Individual Distribution (Base Line) ----
        # ABAKE USE spec: Base Line = Model Total / 2 - Model Spread / 2
        # Uses the Model Total and Model Spread from Layer 1
        base_line = self.calculate_base_line(total, spread)

        # ---- Layer 3: Dynamic Scaling & Execution ----
        # ABAKE USE spec: Layer 3 uses the SAME Model Spread as Layer 2.
        # Scaled_OVER = Base Line - (0.45 × Model Spread)
        # Scaled_UNDER = Base Line + (0.40 × Model Spread)

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
                # Layer 1 outputs (MODEL values)
                "model_total": total,
                "model_spread": spread,
                "independent_total": round(independent_total, 2) if independent_total else None,
                "independent_spread": round(independent_spread, 2) if independent_spread else None,
                # Market data
                "market_total": market_total,
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
            # ABAKE USE spec: Scaled_UNDER = Base Line + (0.40 × Model Spread)
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
                # Layer 1 outputs (MODEL values)
                "model_total": total,
                "model_spread": spread,
                "independent_total": round(independent_total, 2) if independent_total else None,
                "independent_spread": round(independent_spread, 2) if independent_spread else None,
                # Market data
                "market_total": market_total,
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
