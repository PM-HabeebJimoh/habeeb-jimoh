#!/usr/bin/env python3
"""
ABAKE USE Engine — LIVE RUN for Today's Games (August 2, 2026)
Runs the ABAKE USE framework on ALL of today's upcoming WNBA games.
Only shows games NOT YET PLAYED.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from abake_use_engine.core.engine import AbakeUseEngine

def print_header(title: str):
    print("\n" + "=" * 86)
    print(f"  ⚡ {title}")
    print("=" * 86 + "\n")


def main():
    engine = AbakeUseEngine()

    now_utc = datetime.utcnow()
    now_utc1 = now_utc.strftime("%A, %B %d, %Y — %H:%M UTC+1")

    print_header("ABAKE USE ENGINE — LIVE: TODAY'S UPCOMING GAMES")
    print(f"  📅 {now_utc1}")
    print(f"  🏀 League: WNBA")
    print(f"  🧮 Framework: ABAKE USE — Dynamic Pacing & Possession Scaling Engine")
    print()
    print("  League Constants:")
    print(f"    WNBA Baseline Pace: 80.2 | WNBA Baseline Efficiency: 102.5")
    print(f"    HCA: 2.5 points | Over Cushion: 0.45 | Under Ceiling: 0.40")
    print(f"    Upset Probability Threshold: 15.0%")

    # ============================================================
    # TODAY'S UPCOMING GAMES — August 2, 2026
    # All times converted to UTC+1 (CET)
    # Source: ESPN, Covers, wnbaschedule.com, Tony's Picks
    # ============================================================

    todays_games = [
        # ============================================================
        # GAME 1: Indiana Fever @ Minnesota Lynx
        # Time: 1:00 PM ET = 19:00 UTC+1
        # Venue: Target Center, Minneapolis, MN
        # TV: ABC
        # Market: MIN -5.5, O/U 193.5
        # Underdog: IND (receiving 5.5 points)
        # ============================================================
        {
            "matchup": "IND vs MIN",
            "date": "Sun, Aug 2",
            "time_et": "1:00 PM ET",
            "time_utc1": "19:00 UTC+1",
            "venue": "Target Center, Minneapolis",
            "tv": "ABC",
            "total": 193.5,
            "spread": 5.5,
            "pick": "UNDER",
            "win_prob": 9.9,
            "underdog": "IND",
            "underdog_score": None,
            "league": "WNBA",
            "away_team": "IND",
            "home_team": "MIN",
            "away_record": "19-10",
            "home_record": "24-6",
            "game_status": "SCHEDULED",
        },

        # ============================================================
        # GAME 2: Los Angeles Sparks @ Portland Fire
        # Time: 3:30 PM ET = 21:30 UTC+1
        # Venue: Moda Center, Portland, OR
        # TV: NBC / Peacock
        # Market: LA -1.5, O/U 184.5
        # Underdog: POR (receiving 1.5 points)
        # ============================================================
        {
            "matchup": "LAS vs POR",
            "date": "Sun, Aug 2",
            "time_et": "3:30 PM ET",
            "time_utc1": "21:30 UTC+1",
            "venue": "Moda Center, Portland",
            "tv": "NBC / Peacock",
            "total": 184.5,
            "spread": 1.5,
            "pick": "UNDER",
            "win_prob": 25.0,
            "underdog": "POR",
            "underdog_score": None,
            "league": "WNBA",
            "away_team": "LAS",
            "home_team": "POR",
            "away_record": "10-17",
            "home_record": "11-18",
            "game_status": "SCHEDULED",
        },

        # ============================================================
        # GAME 3: Connecticut Sun @ Dallas Wings
        # Time: 7:00 PM ET = 01:00 UTC+1 (Mon)
        # Venue: College Park Center, Arlington, TX
        # TV: ESPN / Disney+
        # Market: DAL -11.5, O/U 170.5
        # Underdog: CON (receiving 11.5 points)
        # ============================================================
        {
            "matchup": "CON vs DAL",
            "date": "Sun, Aug 2",
            "time_et": "7:00 PM ET",
            "time_utc1": "01:00 UTC+1 (Mon)",
            "venue": "College Park Center, Arlington",
            "tv": "ESPN / Disney+",
            "total": 170.5,
            "spread": 11.5,
            "pick": "UNDER",
            "win_prob": 1.5,
            "underdog": "CON",
            "underdog_score": None,
            "league": "WNBA",
            "away_team": "CON",
            "home_team": "DAL",
            "away_record": "7-22",
            "home_record": "18-11",
            "game_status": "SCHEDULED",
        },

        # ============================================================
        # GAME 4: Toronto Tempo @ Golden State Valkyries
        # Time: 8:30 PM ET = 02:30 UTC+1 (Mon)
        # Venue: Chase Center, San Francisco
        # TV: KPIX+ / TSN / WNBA League Pass
        # Market: GS -11.5, O/U 167.5
        # Underdog: TOR (receiving 11.5 points)
        # ============================================================
        {
            "matchup": "TOR vs GS",
            "date": "Sun, Aug 2",
            "time_et": "8:30 PM ET",
            "time_utc1": "02:30 UTC+1 (Mon)",
            "venue": "Chase Center, San Francisco",
            "tv": "KPIX+ / TSN / WNBA League Pass",
            "total": 167.5,
            "spread": 11.5,
            "pick": "OVER",
            "win_prob": 1.5,
            "underdog": "TOR",
            "underdog_score": None,
            "league": "WNBA",
            "away_team": "TOR",
            "home_team": "GS",
            "away_record": "10-18",
            "home_record": "19-9",
            "game_status": "SCHEDULED",
        },
    ]

    # ============================================================
    # PROCESS ALL GAMES THROUGH ABAKE USE
    # ============================================================

    results = []
    active_count = 0
    skip_count = 0

    for i, game in enumerate(todays_games, 1):
        result = engine.process_matchup(game)
        results.append(result)

        print(f"  {'━'*82}")
        print(f"  GAME {i}: {result['matchup']}")
        print(f"  {'━'*82}")
        print(f"  📅 {game['date']} | ⏰ {game['time_utc1']} | 📺 {game['tv']}")
        print(f"  📍 {game['venue']}")
        print(f"  📊 {game['away_team']} ({game['away_record']}) @ {game['home_team']} ({game['home_record']})")
        print(f"  📈 Market: Total {game['total']} | Spread {game['spread']}")
        print()

        if result["status"] == "SYSTEM SKIP":
            skip_count += 1
            print(f"  ⚠️  SYSTEM SKIP — {result['rule_triggered']}")
            print(f"  Reason: {result['details']}")
            print(f"  ❌ NO BET — Capital protected by ABAKE USE filter rules")
        else:
            active_count += 1
            print(f"  ✅ ABAKE USE ACTIVE — {result['rule_triggered']}")
            print(f"  Pick: {result['category']}")
            print(f"  Model Total: {result['model_total']} | Model Spread: {result['model_spread']}")
            print(f"  Base Line (Layer 2): {result['base_line']:.2f}")
            print(f"  🎯 UNDERDOG SCALED LINE (Layer 3): {result['underdog_scaled_line']:.2f}")
            print(f"  Underdog: {result['underdog']}")
            print()
            print(f"  💰 BET: {result['underdog']} {result['category']} {result['underdog_scaled_line']:.2f}")
            if result['category'] == 'OVER':
                print(f"  🎯 Hit condition: {result['underdog']} scores > {result['underdog_scaled_line']:.2f}")
            else:
                print(f"  🎯 Hit condition: {result['underdog']} scores < {result['underdog_scaled_line']:.2f}")
        print()

    # ============================================================
    # SUMMARY TABLE
    # ============================================================

    print_header("ABAKE USE LIVE SCORECARD — TODAY'S UPCOMING GAMES")
    print(f"  {'#':>2} {'Matchup':<16} {'Date':<12} {'Time (UTC+1)':<18} {'Pick':<6} {'Total':>7} {'Spread':>7} {'Base':>7} {'🎯 Scaled':>9} {'Underdog':<10} {'Action':<8}")
    print(f"  {'':->2} {'':->16} {'':->12} {'':->18} {'':->6} {'':->7} {'':->7} {'':->7} {'':->9} {'':->10} {'':->8}")

    for i, r in enumerate(results, 1):
        g = todays_games[i-1]
        scaled = r.get("underdog_scaled_line", 0) or 0
        base = r.get("base_line", 0) or 0
        total = r.get("model_total", 0) or 0
        spread = r.get("model_spread", 0) or 0
        cat = r.get("category", "SKIP") or "SKIP"
        action = "BET" if r["status"] != "SYSTEM SKIP" else "SKIP"
        print(f"  {i:2d} {r['matchup']:<16} {g['date']:<12} {g['time_utc1']:<18} {cat:<6} {total:>7.1f} {spread:>7.1f} {base:>7.2f} {scaled:>9.2f} {r.get('underdog','?'):<10} {action:<8}")

    print()

    # ============================================================
    # ACTIVE BETS ONLY
    # ============================================================

    active_results = [r for r in results if r["status"] != "SYSTEM SKIP"]
    if active_results:
        print_header("🎯 ABAKE USE ACTIVE BETS — TODAY'S PLAY SHEET")
        for i, r in enumerate(active_results, 1):
            g = [g for g in todays_games if g["matchup"] == r["matchup"]][0]
            print(f"  {'━'*82}")
            print(f"  BET {i}: {r['underdog']} {r['category']} {r['underdog_scaled_line']:.2f}")
            print(f"  {'━'*82}")
            print(f"  📅 {g['date']} | ⏰ {g['time_utc1']}")
            print(f"  📺 {g['tv']} | 📍 {g['venue']}")
            print(f"  📊 {g['away_team']} ({g['away_record']}) @ {g['home_team']} ({g['home_record']})")
            print(f"  🎯 Scaled Line: {r['underdog_scaled_line']:.2f}")
            print(f"  💰 Hit condition: {r['underdog']} scores {'>' if r['category'] == 'OVER' else '<'} {r['underdog_scaled_line']:.2f}")
            print()

    # ============================================================
    # SKIPPED GAMES
    # ============================================================

    skip_results = [r for r in results if r["status"] == "SYSTEM SKIP"]
    if skip_results:
        print_header("⚠️  SYSTEM SKIPS — CAPITAL PROTECTED")
        for i, r in enumerate(skip_results, 1):
            g = [g for g in todays_games if g["matchup"] == r["matchup"]][0]
            print(f"  {i}. {r['matchup']} — {g['time_utc1']}")
            print(f"     Rule: {r['rule_triggered']}")
            print(f"     Reason: {r['details']}")
            print(f"     ❌ NO BET — Skip this game")
            print()

    # ============================================================
    # FINAL SUMMARY
    # ============================================================

    print_header("ABAKE USE LIVE SUMMARY")
    print(f"  📊 Total Games Today:        {len(results)}")
    print(f"  🎯 Active ABAKE USE Bets:    {active_count}")
    print(f"  ⚠️  System Skips:             {skip_count}")
    print(f"  🏆 All active bets have scaled lines ready for live scoring")
    print()
    print("  🎯 The ABAKE USE Engine is LIVE and ready for today's games.")


if __name__ == "__main__":
    main()
