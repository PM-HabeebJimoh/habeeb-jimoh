#!/usr/bin/env python3
"""
ABAKE USE Engine — CLI Runner
Runs the complete 40-game ABAKE USE pipeline with all underdog scaled line scores.
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from abake_use_engine.core.engine import AbakeUseEngine
from abake_use_engine.data.games_dataset import ALL_40_GAMES
from abake_use_engine.data.services import BasketballDataService
from abake_use_engine.data.analytics import AnalyticsService
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("abake_use_runner")


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  ⚡ {title}")
    print("=" * 80 + "\n")


def run_verification(engine: AbakeUseEngine) -> bool:
    """Run the 3 verification profiles from the specification."""
    print_header("ENGINE VERIFICATION — 3 Calibration Profiles")

    profiles = [
        {
            "name": "Profile 1: CON vs NY (May 8) — OVER",
            "data": ALL_40_GAMES[0],  # Game 1
            "expected": "HIT",
            "expected_scaled": 71.0,
            "steps": [
                "Step 1 (Raw Inputs): Away Pace: 78.5, Home Pace: 80.9 | Away ORtg: 100.5, Home DRtg: 97.2 | Home ORtg: 110.1, Away DRtg: 97.8",
                "Step 2 (Pacing): P = 78.5 + 80.9 - 80.2 = 79.2 Possessions",
                "Step 3 (Score Projections): S_A = (100.5×97.2/102.5)×(79.2/100) = 75.48 | S_H = (110.1×97.8/102.5)×(79.2/100)+2.5 = 85.70",
                "Step 4 (Core Baselines): Model Total = 161.18 → 161.0 (rounded), Model Spread = 10.22 → 10.0 (rounded)",
                "Step 5 (Baseline Split): Base Line = 161.0/2 - 10.0/2 = 80.5 - 5.0 = 75.5 (using MODEL total/spread)",
                "Step 6 (Filter Check): Pick is OVER. Rule 1 does not apply. CLEARED.",
                "Step 7 (Dynamic Scaling): Scaled_OVER = 75.5 - (0.45×10.0) = 75.5 - 4.50 = 71.0 (using MODEL spread)",
                "Step 8 (Verification): Underdog CON scored 75. (75 > 71.0) → HIT ✓",
            ],
        },
        {
            "name": "Profile 2: LV vs CON (May 13) — UNDER",
            "data": ALL_40_GAMES[15],  # Game 16
            "expected": "HIT",
            "expected_scaled": 82.35,
            "steps": [
                "Step 1 (Raw Inputs): Away Pace: 81.6, Home Pace: 78.5 | Away ORtg: 111.4, Home DRtg: 97.8 | Home ORtg: 100.5, Away DRtg: 99.8",
                "Step 2 (Core Baselines): Model Total = 165.61 → 165.5 (rounded), Model Spread = 4.24 → 4.0 (rounded)",
                "Step 3 (Baseline Split): Base Line = 165.5/2 - 4.0/2 = 82.75 - 2.0 = 80.75 (using MODEL total/spread)",
                "Step 4 (Filter Check): Win prob 3.3% ≤ 15.0%. CLEARED.",
                "Step 5 (Dynamic Scaling): Scaled_UNDER = 80.75 + (0.40×4.0) = 80.75 + 1.60 = 82.35 (using MODEL spread)",
                "Step 6 (Verification): Underdog CON scored 69. (69 < 82.35) → HIT ✓",
            ],
        },
        {
            "name": "Profile 3: SEA vs CON (May 10) — UPSET CLAUSE",
            "data": ALL_40_GAMES[13],  # Game 14
            "expected": "SYSTEM SKIP",
            "expected_scaled": None,
            "steps": [
                "Step 1 (Raw Inputs): Market Total = 163.0, Market Spread = 1.5 | Pick: UNDER | Win Prob: 20.0% | Underdog: SEA",
                "Step 2 (Filter Check): Win prob 20.0% > 15.0% → Rule 1 Upset Clause TRIGGERED",
                "Step 3 (Verification): Position voided. SYSTEM SKIP ✓",
            ],
        },
    ]

    all_pass = True
    for profile in profiles:
        print(f"▶ {profile['name']}")
        print("-" * 70)
        for step in profile["steps"]:
            print(f"  {step}")

        result = engine.process_matchup(profile["data"])
        actual_status = result["status"]
        expected_status = profile["expected"]
        passed = actual_status == expected_status

        # Verify scaled line
        scaled_match = True
        if profile["expected_scaled"] is not None:
            actual_scaled = result.get("underdog_scaled_line", 0)
            scaled_match = abs(actual_scaled - profile["expected_scaled"]) < 0.01

        if passed and scaled_match:
            print(f"\n  ✅ RESULT: {actual_status} — VERIFIED")
            if "underdog_scaled_line" in result:
                print(f"     Underdog Scaled Line: {result['underdog_scaled_line']:.2f}")
                print(f"     Underdog Actual Score: {result.get('underdog_score', 'N/A')}")
        else:
            print(f"\n  ❌ RESULT: {actual_status} — EXPECTED {expected_status} — FAILED")
            if not scaled_match:
                print(f"     Scaled line mismatch: expected {profile['expected_scaled']}, got {result.get('underdog_scaled_line', 'N/A')}")
            all_pass = False

    print(f"\n{'='*80}")
    if all_pass:
        print("  ✅ ALL 3 VERIFICATION PROFILES PASSED — ENGINE IS CALIBRATED")
    else:
        print("  ❌ VERIFICATION FAILED")
    print(f"{'='*80}")
    return all_pass


def run_full_40_game_matrix(engine: AbakeUseEngine) -> pd.DataFrame:
    """Run the complete 40-game ABAKE USE matrix with all underdog scaled lines."""
    print_header("COMPLETE 40-GAME ABAKE USE MATRIX — ALL UNDERDOG SCALED LINES")

    # Process all 40 games
    results = []
    for i, game in enumerate(ALL_40_GAMES, 1):
        result = engine.process_matchup(game)
        results.append(result)

        # Print with clear underdog scaled line
        status_emoji = {
            "HIT": "✅", "MISS": "❌", "SYSTEM SKIP": "⚠️", "PENDING": "⏳"
        }.get(result["status"], "❓")

        print(f"  {i:2d}. {result['matchup']:<16} [{game['date']}]")

        if result["status"] == "SYSTEM SKIP":
            print(f"      {status_emoji} {result['status']} — {result['rule_triggered']}")
            print(f"      Reason: {result['details']}")
        else:
            # THE KEY OUTPUT — Underdog Scaled Line
            print(f"      {status_emoji} {result['status']} | {result['category']}")
            print(f"      Model Total: {result['model_total']} | Model Spread: {result['model_spread']}")
            print(f"      Base Line (Layer 2): {result['base_line']:.2f}")
            print(f"      🎯 UNDERDOG SCALED LINE (Layer 3): {result['underdog_scaled_line']:.2f}")
            print(f"      Underdog: {result['underdog']} | Actual Score: {result['underdog_score']}")
            if result['underdog_score'] is not None:
                print(f"      {result['details']}")
        print()

    # Compute summary
    results_df = pd.DataFrame(results)
    summary = engine.compute_summary(results_df)

    print_header("ABAKE USE MATRIX SUMMARY — 40-GAME PERFORMANCE")
    print(f"  📊 Total Data Grid Rows:        {summary['total_matchups']} Matchups")
    print(f"  🎯 ABAKE USE Active Bets:       {summary['active_bets']} Positions")
    print(f"  ✅ System Validated Wins:        {summary['validated_wins']} Wins")
    print(f"  ❌ Systemic Failures / Losses:   {summary['losses']} Losses")
    print(f"  ⚠️  Strategic Skips:             {summary['system_skips']} Matchups")
    print(f"  🏆 Net Matrix Accuracy:          {summary['win_rate_pct']}%")
    print()

    # Print the UNDERDOG SCALED LINE TABLE
    print_header("UNDERDOG SCALED LINE SCORE TABLE — ALL 38 ACTIVE POSITIONS")
    print(f"  {'#':>2} {'Matchup':<16} {'Pick':<6} {'Total':>7} {'Spread':>7} {'Base':>7} {'Scaled':>8} {'Underdog':<10} {'Score':>6} {'Result':<6}")
    print(f"  {'':->2} {'':->16} {'':->6} {'':->7} {'':->7} {'':->7} {'':->8} {'':->10} {'':->6} {'':->6}")

    active = [r for r in results if r["status"] != "SYSTEM SKIP"]
    for i, r in enumerate(active, 1):
        scaled = r.get("underdog_scaled_line", 0)
        score = r.get("underdog_score", "—")
        result_str = r["status"]
        print(f"  {i:2d} {r['matchup']:<16} {r.get('category','?'):<6} {r['model_total']:>7.1f} {r['model_spread']:>7.1f} {r['base_line']:>7.2f} {scaled:>8.2f} {r.get('underdog','?'):<10} {str(score):>6} {result_str:<6}")

    return results_df


def process_todays_games(engine: AbakeUseEngine, data_service: BasketballDataService,
                         analytics: AnalyticsService) -> pd.DataFrame:
    """Process today's live games through the ABAKE USE engine."""
    print_header("TODAY'S BASKETBALL GAMES — ABAKE USE ANALYSIS (August 2, 2026)")

    print("  📡 Loading game data for today...")
    all_games = data_service.get_all_todays_games()

    if not all_games:
        print("  ⚠️  No games found for today.")
        return pd.DataFrame()

    completed = [g for g in all_games if g.get("is_final")]
    scheduled = [g for g in all_games if g.get("is_scheduled")]

    print(f"  📊 Found {len(all_games)} total games: {len(completed)} Final, {len(scheduled)} Scheduled\n")

    results = []
    for i, game in enumerate(all_games, 1):
        game = analytics.enrich_game_with_stats(game)
        row = _game_to_engine_row(game, engine, analytics)
        result = engine.process_matchup(row)
        results.append(result)

        status_emoji = {"HIT": "✅", "MISS": "❌", "SYSTEM SKIP": "⚠️", "PENDING": "⏳"}.get(result["status"], "❓")
        game_status = "FINAL" if game.get("is_final") else "SCHEDULED"

        print(f"  {i}. {result['matchup']} [{game_status}]")
        print(f"     {status_emoji} {result['status']}")
        if result["status"] != "SYSTEM SKIP":
            print(f"     Model Total: {result['model_total']} | Model Spread: {result['model_spread']}")
            print(f"     🎯 UNDERDOG SCALED LINE: {result['underdog_scaled_line']:.2f}")
            print(f"     Underdog: {result.get('underdog','?')} | Score: {result.get('underdog_score','—')}")
        print(f"     {result.get('details', '')}")
        print()

    results_df = pd.DataFrame(results)
    summary = engine.compute_summary(results_df)
    print_header("TODAY'S SUMMARY")
    print(f"  Active: {summary['active_bets']} | Wins: {summary['validated_wins']} | Losses: {summary['losses']} | Skips: {summary['system_skips']} | Pending: {summary['pending']}")
    return results_df


def _game_to_engine_row(game, engine, analytics):
    """Convert a live game dict to an engine-ready row."""
    row = {"matchup": game.get("matchup", ""), "league": game.get("league", "WNBA")}

    for key in ("away_pace", "away_ortg", "away_drtg", "home_pace", "home_ortg", "home_drtg"):
        if game.get(key):
            row[key] = float(game[key])

    spread = game.get("spread", 0) or 0
    total = game.get("total", 0) or 0

    if game.get("is_final") or game.get("is_live"):
        row["underdog_score"] = game.get("away_score", 0) or 0
    else:
        row["underdog_score"] = None

    row["total"] = float(total) if total else None
    row["spread"] = float(abs(spread)) if spread else None
    row["underdog"] = game.get("away_team", "")

    if all(k in row for k in ("away_pace", "home_pace", "away_ortg", "home_drtg", "home_ortg", "away_drtg")):
        model_total, model_spread, _, _, _ = engine.calculate_independent_baselines(row)
        market_total = row.get("total", model_total)
        row["pick"] = "OVER" if model_total > market_total else "UNDER"
    else:
        row["pick"] = "OVER" if (row.get("spread", 5) or 5) > 5 else "UNDER"

    row["win_prob"] = game.get("win_prob", analytics.estimate_win_probability(row.get("spread", 5.0) or 5.0))
    return row


def main():
    print_header("ABAKE USE ENGINE — 100% Underdog Scoring Engine")
    print(f"  Version: 1.0.0 | Timestamp: {datetime.utcnow().isoformat()}")
    print(f"  Framework: Dynamic Pacing & Possession Scaling Engine")
    print()
    print("  League Constants:")
    print(f"    WNBA:         Pace=80.2, Eff=102.5")
    print(f"    Summer League: Pace=84.5, Eff=98.2")
    print(f"  HCA: 2.5 points")
    print(f"  Over Cushion Multiplier: 0.45")
    print(f"  Under Ceiling Multiplier: 0.40")
    print(f"  Upset Probability Threshold: 15.0%")

    engine = AbakeUseEngine()
    data_service = BasketballDataService()
    analytics_svc = AnalyticsService()

    # Step 1: Verify engine
    verified = run_verification(engine)
    if not verified:
        print("\n❌ ENGINE VERIFICATION FAILED")
        sys.exit(1)

    # Step 2: Run the COMPLETE 40-game matrix
    results_df = run_full_40_game_matrix(engine)

    # Step 3: Process today's live games
    process_todays_games(engine, data_service, analytics_svc)

    # Final status
    print_header("ENGINE STATUS")
    print("  ✅ Engine: OPERATIONAL")
    print("  ✅ Verification: ALL PROFILES PASSED")
    print("  ✅ 40-Game Matrix: ALL PROCESSED")
    print("  ✅ Today's Games: PROCESSED")
    print()
    print("  🎯 The ABAKE USE Engine is LIVE and WORKING.")


if __name__ == "__main__":
    main()
