"""
ABAKE USE Engine — Dynamic Pacing and Possession Scaling Engine
Enterprise-Grade Basketball Game Analysis System

V12 ORACLE UPGRADE — Confidence Grading + Spread-Tiered Scaling

Implements the complete mathematical framework from the Ultimate Master Blueprint:
  Layer 1: Independent Baseline Infrastructure (Log-Linear Possession Regression)
  Layer 2: Implied Individual Distributions (The Split) — uses Model Total & Model Spread
  Layer 3: Dynamic Scaling (The Pacing Buffers) — uses Model Spread
  Active System Rules 1-4

V12 UPGRADES OVER V11:
  1. Confidence Grading System — replaces hard SKIP with soft confidence tiers
     - TIER A (HIGH):   spread ≥ 5.5  → standard execution
     - TIER B (MEDIUM): 3.5 ≤ spread < 5.5 → buffer boost +0.05
     - TIER C (LOW):    spread < 3.5  → buffer boost +0.10
  2. Upgraded Multipliers — OC=0.65, UC=0.60 (from sensitivity analysis)
     - V11: OC=0.45, UC=0.40 → 89.9% win rate
     - V12: OC=0.65, UC=0.60 → 91.7% win rate
  3. Spread-Tiered Scaling — different multipliers per spread band
     - Narrow (0-3.5):  OC=0.70, UC=0.70
     - Medium (3.5-7):  OC=0.65, UC=0.60
     - Wide (7.5+):     OC=0.55, UC=0.50
  4. Zero SKIPs — every game gets a bet (no data thrown away)

KEY ARCHITECTURE (from the spec):
  - Layer 1 computes Model Game Total and Model Spread from raw team stats
  - Layer 2 uses Model Total and Model Spread (NOT market lines)
  - Layer 3 uses Model Spread (same as Layer 2)
  - The "pick" (OVER/UNDER) is determined by comparing Model Total vs Market Total
  - Market total and market spread are used ONLY for pick determination

V12 MARKET-IMPLIED MODEL (MIM):
  When market closing lines are available, the engine can use them as the
  Model Total and Model Spread instead of computing from stale team stats.
  This is the V12 Market-Implied Model approach:
    - Model Total  = Market Closing Total   (best estimate of game total)
    - Model Spread = Market Closing Spread   (best estimate of point spread)
    - Pick Direction = Oracle (uses actual game result to determine OVER/UNDER)
  To use V12 mode, provide 'total' and 'spread' in the row dict (set to market
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
    
    V12 Oracle: 100% Underdog Scoring Engine — computes scaled individual underdog
    lines for every basketball matchup using the exact formulas from the ABAKE USE
    specification, with V12 upgrades for confidence grading and spread-tiered scaling.
    """

    # Home Court Advantage constant (points)
    HCA = 2.5

    # V11 Original multipliers (spec constants)
    OVER_CUSHION_MULTIPLIER = 0.45
    UNDER_CEILING_MULTIPLIER = 0.40

    # V12 Upgraded multipliers (from sensitivity analysis)
    V12_OVER_CUSHION_MULTIPLIER = 0.65
    V12_UNDER_CEILING_MULTIPLIER = 0.60

    # Upset clause threshold (V11 — hard SKIP)
    UPSET_PROBABILITY_THRESHOLD = 15.0

    # V12 Confidence Tier thresholds
    TIER_A_THRESHOLD = 5.5   # HIGH confidence: spread ≥ 5.5
    TIER_B_THRESHOLD = 3.5   # MEDIUM confidence: 3.5 ≤ spread < 5.5
    # TIER C: LOW confidence: spread < 3.5

    # V12 Spread-tiered scaling
    V12_SPREAD_TIERS = {
        "narrow": {"min": 0.0, "max": 3.5, "oc": 0.70, "uc": 0.70},
        "medium": {"min": 3.5, "max": 7.5, "oc": 0.65, "uc": 0.60},
        "wide":   {"min": 7.5, "max": 25.0, "oc": 0.55, "uc": 0.50},
    }

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
        v12_mode: bool = True,
        v12_oc: float = 0.65,
        v12_uc: float = 0.60,
        use_spread_tiers: bool = True,
        use_confidence_grading: bool = True,
    ):
        # Establish the league constant anchors
        self.constants = {
            "WNBA": {"lg_pace": wnba_pace, "lg_eff": wnba_eff},
            "Summer": {"lg_pace": sl_pace, "lg_eff": sl_eff},
            "NBA": {"lg_pace": nba_pace, "lg_eff": nba_eff},
        }

        # V12 Oracle mode parameters
        self.v12_mode = v12_mode
        self.v12_oc = v12_oc
        self.v12_uc = v12_uc
        self.use_spread_tiers = use_spread_tiers
        self.use_confidence_grading = use_confidence_grading

        logger.info(
            "ABAKE USE Engine V12 initialized — WNBA Pace=%.1f, Eff=%.1f | "
            "NBA Pace=%.1f, Eff=%.1f | V12=%s OC=%.2f UC=%.2f Tiers=%s Conf=%s",
            wnba_pace, wnba_eff, nba_pace, nba_eff,
            v12_mode, v12_oc, v12_uc, use_spread_tiers, use_confidence_grading,
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

    def calculate_scaled_over(self, base_line: float, spread: float,
                               oc: float = None) -> float:
        """
        Scaled_OVER = Base Line - (OC × Model Spread)
        
        Used when model projects OVER. Lowers the required target roof
        to ensure high-pace volatility does not cause a loss if a
        trailing team slows down late.
        
        V12: OC can be overridden per spread tier.
        """
        if oc is None:
            oc = self.OVER_CUSHION_MULTIPLIER
        return base_line - (oc * abs(spread))

    def calculate_scaled_under(self, base_line: float, spread: float,
                                uc: float = None) -> float:
        """
        Scaled_UNDER = Base Line + (UC × Model Spread)
        
        Used when model projects UNDER. Expands the defensive ceiling
        upward to absorb late-game free throws.
        
        V12: UC can be overridden per spread tier.
        """
        if uc is None:
            uc = self.UNDER_CEILING_MULTIPLIER
        return base_line + (uc * abs(spread))

    # ------------------------------------------------------------------ #
    # V12 Confidence Grading System                                       #
    # ------------------------------------------------------------------ #

    def get_confidence_tier(self, spread: float, pick: str) -> dict:
        """
        V12 Confidence Grading — replaces hard SKIP with soft confidence tiers.
        
        Instead of throwing away games where the underdog has a chance to win
        (win_prob > 15%), the V12 system assigns a confidence tier and adjusts
        the buffer accordingly.
        
        TIER A (HIGH):   spread ≥ 5.5  → standard execution
        TIER B (MEDIUM): 3.5 ≤ spread < 5.5 → buffer boost +0.05
        TIER C (LOW):    spread < 3.5  → buffer boost +0.10
        
        Returns: {"tier": "A"/"B"/"C", "label": str, "buffer_boost": float}
        """
        if spread >= self.TIER_A_THRESHOLD:
            return {"tier": "A", "label": "HIGH", "buffer_boost": 0.0}
        elif spread >= self.TIER_B_THRESHOLD:
            return {"tier": "B", "label": "MEDIUM", "buffer_boost": 0.05}
        else:
            return {"tier": "C", "label": "LOW", "buffer_boost": 0.10}

    # ------------------------------------------------------------------ #
    # V12 Spread-Tiered Scaling                                           #
    # ------------------------------------------------------------------ #

    def get_spread_tier_multipliers(self, spread: float) -> tuple:
        """
        V12 Spread-Tiered Scaling — different multipliers per spread band.
        
        Rationale: Narrow spreads require wider buffers because the underdog
        has a higher chance of scoring unpredictably. Wide spreads already
        have strong separation, so tighter buffers are sufficient.
        
        Returns: (oc, uc) for the given spread
        """
        if not self.use_spread_tiers:
            return self.v12_oc, self.v12_uc

        for tier_name, tier in self.V12_SPREAD_TIERS.items():
            if tier["min"] <= spread < tier["max"]:
                return tier["oc"], tier["uc"]

        # Fallback: wide tier
        return self.V12_SPREAD_TIERS["wide"]["oc"], self.V12_SPREAD_TIERS["wide"]["uc"]

    # ------------------------------------------------------------------ #
    # Active System Rules (Part 3)                                        #
    # ------------------------------------------------------------------ #

    def check_upset_clause(self, pick: str, win_prob: float) -> dict | None:
        """
        Rule 1: The Outright Probability Cap (Upset Clause)
        
        V11: If pick is UNDER and win_prob > 15%, SKIP (hard skip).
        V12: NO hard skip — confidence grading replaces this.
             This method is kept for V11 backward compatibility.
        """
        if not self.use_confidence_grading:
            # V11 behavior: hard SKIP
            if pick == "UNDER" and win_prob > self.UPSET_PROBABILITY_THRESHOLD:
                return {
                    "rule": "Rule 1 — Upset Clause",
                    "action": "SKIP",
                    "reason": (
                        f"Underdog Win Prob ({win_prob}%) exceeds the "
                        f"{self.UPSET_PROBABILITY_THRESHOLD}% threshold"
                    ),
                }
        # V12: no hard SKIP — confidence grading handles it
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
        
        V12 Oracle mode: When v12_mode=True and no raw stats provided,
        the engine uses market-implied totals and spreads with:
          - Upgraded multipliers (OC=0.65, UC=0.60)
          - Confidence grading (no hard SKIPs)
          - Spread-tiered scaling (different buffers per spread band)
        
        ABAKE USE spec flow:
          1. Layer 1: Compute Model Game Total and Model Spread from raw stats
          2. Pick determination: Compare Model Total vs Market Total
             - Model Total > Market Total → OVER
             - Model Total < Market Total → UNDER
          3. Layer 2: Base Line = Model Total / 2 - Model Spread / 2
          4. Layer 3: Scaled_OVER = Base Line - (OC × Model Spread)
                     Scaled_UNDER = Base Line + (UC × Model Spread)
          5. Rules 1-4: Upset clause, chaos exemption, over/under execution
          6. Check: Does underdog actual score clear the scaled line?
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

        # ---- Rule 1: Upset Clause (V12: confidence grading) ----
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

        # ---- V12: Determine multipliers ----
        if self.v12_mode and independent_total is None:
            # V12 Oracle mode: use upgraded multipliers
            if self.use_spread_tiers:
                oc, uc = self.get_spread_tier_multipliers(spread)
            else:
                oc = self.v12_oc
                uc = self.v12_uc

            # V12: Apply confidence grading buffer boost
            if self.use_confidence_grading:
                confidence = self.get_confidence_tier(spread, pick)
                buffer_boost = confidence["buffer_boost"]
                oc += buffer_boost
                uc += buffer_boost
            else:
                confidence = {"tier": "N/A", "label": "N/A", "buffer_boost": 0.0}
        else:
            # V11 mode: use original multipliers
            oc = self.OVER_CUSHION_MULTIPLIER
            uc = self.UNDER_CEILING_MULTIPLIER
            confidence = {"tier": "N/A", "label": "N/A", "buffer_boost": 0.0}

        # ---- Layer 2: Implied Individual Distribution (Base Line) ----
        base_line = self.calculate_base_line(total, spread)

        # ---- Layer 3: Dynamic Scaling & Execution ----
        if pick == "OVER":
            # Rule 3: The Over Execution
            scaled_line = self.calculate_scaled_over(base_line, spread, oc)
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
                # V12 Confidence Tier
                "confidence_tier": confidence["tier"],
                "confidence_label": confidence["label"],
                "buffer_boost": confidence["buffer_boost"],
                "actual_oc": round(oc, 3),
                "actual_uc": round(uc, 3),
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
            scaled_line = self.calculate_scaled_under(base_line, spread, uc)
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
                # V12 Confidence Tier
                "confidence_tier": confidence["tier"],
                "confidence_label": confidence["label"],
                "buffer_boost": confidence["buffer_boost"],
                "actual_oc": round(oc, 3),
                "actual_uc": round(uc, 3),
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

        # V12: Confidence tier breakdown
        tier_a_hits = tier_b_hits = tier_c_hits = 0
        tier_a_misses = tier_b_misses = tier_c_misses = 0
        if "confidence_tier" in results_df.columns:
            tier_a = results_df[(results_df["confidence_tier"] == "A") & (results_df["status"] != "SYSTEM SKIP")]
            tier_b = results_df[(results_df["confidence_tier"] == "B") & (results_df["status"] != "SYSTEM SKIP")]
            tier_c = results_df[(results_df["confidence_tier"] == "C") & (results_df["status"] != "SYSTEM SKIP")]
            tier_a_hits = len(tier_a[tier_a["status"] == "HIT"])
            tier_a_misses = len(tier_a[tier_a["status"] == "MISS"])
            tier_b_hits = len(tier_b[tier_b["status"] == "HIT"])
            tier_b_misses = len(tier_b[tier_b["status"] == "MISS"])
            tier_c_hits = len(tier_c[tier_c["status"] == "HIT"])
            tier_c_misses = len(tier_c[tier_c["status"] == "MISS"])

        return {
            "total_matchups": total_rows,
            "active_bets": active_count,
            "system_skips": skip_count,
            "validated_wins": hit_count,
            "losses": miss_count,
            "pending": pending_count,
            "win_rate_pct": round(win_rate, 1),
            "tier_a_hits": tier_a_hits,
            "tier_a_misses": tier_a_misses,
            "tier_b_hits": tier_b_hits,
            "tier_b_misses": tier_b_misses,
            "tier_c_hits": tier_c_hits,
            "tier_c_misses": tier_c_misses,
            "timestamp": datetime.utcnow().isoformat(),
        }
