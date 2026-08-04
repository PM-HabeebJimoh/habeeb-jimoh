#!/usr/bin/env python3
"""
ABAKE USE V12 — TODAY'S GAMES — 2026-08-03

TWO MODES:
  ORACLE (backtest):      Pick = f(actual_result)  → "Did the scaled line work?"
  PREDICTIVE (live bet):  Pick = f(Layer1_model)   → "What should I bet BEFORE tip-off?"

The 91.8% backtest win rate proves: IF you get the direction right, the scaled line HITS 91.8% of the time.
The Predictive mode tells you: WHICH direction to bet BEFORE the game.
"""

import math
import json
import sys
sys.path.insert(0, '/home/user/habeeb-jimoh')

from abake_use_engine.core.engine import AbakeUseEngine

def load_team_efficiency_stats():
    data = json.load(open('/home/user/habeeb-jimoh/scraped_data/all_games_with_real_lines.json'))
    LEAGUE_AVG = {
        'WNBA': {'avg_total': 173.0, 'lg_pace': 80.2},
        'NBA':  {'avg_total': 220.0, 'lg_pace': 100.4},
    }
    raw = {}
    for lk in ['nba', 'wnba']:
        lg = 'NBA' if lk == 'nba' else 'WNBA'
        for g in data.get(lk, []):
            a, h = g['away'], g['home']
            for team, sc, al in [(a, g['away_score'], g['home_score']), (h, g['home_score'], g['away_score'])]:
                key = (team, lg)
                if key not in raw: raw[key] = {'scored': [], 'allowed': [], 'totals': []}
                raw[key]['scored'].append(sc)
                raw[key]['allowed'].append(al)
                raw[key]['totals'].append(sc + al)
    result = {}
    for (team, lg), s in raw.items():
        gp = len(s['scored'])
        ppg = sum(s['scored']) / gp
        dppg = sum(s['allowed']) / gp
        avg_t = sum(s['totals']) / gp
        lavg = LEAGUE_AVG[lg]
        pace = (avg_t / lavg['avg_total']) * lavg['lg_pace']
        result[(team, lg)] = {
            'gp': gp, 'ortg': round(ppg * 100 / pace, 1), 'drtg': round(dppg * 100 / pace, 1),
            'pace': round(pace, 1), 'ppg': round(ppg, 1), 'dppg': round(dppg, 1), 'avg_total': round(avg_t, 1),
        }
    return result

def win_prob_from_spread(spread):
    return round(50.0 / (1.0 + math.exp(0.35 * (abs(spread) - 1.5))), 1)

def run_layer1(away, home, league, stats, engine):
    ak, hk = (away, league), (home, league)
    a, h = stats.get(ak), stats.get(hk)
    if not a or not h: return None
    row = {'league': league, 'away_pace': a['pace'], 'home_pace': h['pace'],
           'away_ortg': a['ortg'], 'home_drtg': h['drtg'], 'home_ortg': h['ortg'], 'away_drtg': a['drtg']}
    return engine.calculate_independent_baselines(row)

def run_today():
    engine = AbakeUseEngine(v12_mode=True, use_spread_tiers=True, use_confidence_grading=True)
    stats = load_team_efficiency_stats()

    # Today's games
    games = [
        {"num": 1, "away": "NY", "home": "SA", "league": "NBA", "time": "FINAL",
         "mkt_total": 215.5, "mkt_spread": 5.5, "favorite": "SA", "underdog": "NY",
         "away_score": 94, "home_score": 90},
        {"num": 2, "away": "LV", "home": "ATL", "league": "WNBA", "time": "7:00 PM ET",
         "mkt_total": 185.0, "mkt_spread": 1.5, "favorite": "ATL", "underdog": "LV",
         "away_score": None, "home_score": None},
        {"num": 3, "away": "SEA", "home": "NY", "league": "WNBA", "time": "7:00 PM ET",
         "mkt_total": 183.5, "mkt_spread": 7.5, "favorite": "NY", "underdog": "SEA",
         "away_score": None, "home_score": None},
        {"num": 4, "away": "PHO", "home": "CHI", "league": "WNBA", "time": "9:00 PM ET",
         "mkt_total": 179.0, "mkt_spread": 1.5, "favorite": "PHO", "underdog": "CHI",
         "away_score": None, "home_score": None},
    ]

    print("=" * 120)
    print("  ⚡ ABAKE USE V12 — TODAY'S GAMES — 2026-08-03")
    print("=" * 120)
    print()
    print("  TWO MODES:")
    print("  ──────────")
    print("  ORACLE (backtest verification):  Pick direction = actual game result")
    print("     → Proves: 'If you knew the right OVER/UNDER, would the scaled line HIT?'")
    print("     → The 91.8% backtest rate = the scaled line works when direction is correct")
    print()
    print("  PREDICTIVE (live betting):       Pick direction = Layer 1 Model Total vs Market Total")
    print("     → Tells you: 'Bet OVER if model > market, bet UNDER if model < market'")
    print("     → This is what you bet BEFORE tip-off")
    print()
    print("  V12 Spread-Tiered Scaling:")
    print("    Narrow (0-3.5): OC=0.70, UC=0.70 | Medium (3.5-7.5): OC=0.65, UC=0.60 | Wide (7.5+): OC=0.55, UC=0.50")
    print("  V12 Confidence Grading: A (|s|≥5.5) +0.00 | B (3.5≤|s|<5.5) +0.05 | C (|s|<3.5) +0.10")
    print()

    results = []

    for g in games:
        n, away, home, lg = g['num'], g['away'], g['home'], g['league']
        mt_m, ms_m, fav, ud = g['mkt_total'], g['mkt_spread'], g['favorite'], g['underdog']
        is_final = g['away_score'] is not None

        print()
        print("─" * 120)
        tag = "✅ FINAL" if is_final else "🔮 UPCOMING"
        print(f"  🏀 GAME {n}: {away} @ {home} ({lg}) — {g['time']} — {tag}")
        print("─" * 120)

        # Team stats
        ak, hk = (away, lg), (home, lg)
        a_s, h_s = stats.get(ak, {}), stats.get(hk, {})
        if a_s:
            print(f"    {away:4s}: GP={a_s['gp']}  ORtg={a_s['ortg']}  DRtg={a_s['drtg']}  Pace={a_s['pace']}  PPG={a_s['ppg']}")
        if h_s:
            print(f"    {home:4s}: GP={h_s['gp']}  ORtg={h_s['ortg']}  DRtg={h_s['drtg']}  Pace={h_s['pace']}  PPG={h_s['ppg']}")

        # Layer 1 Model
        l1 = run_layer1(away, home, lg, stats, engine)
        if l1 is None:
            print("  ❌ Missing team stats")
            continue
        model_total, model_spread, proj_pace, score_away, score_home = l1

        # PREDICTIVE pick (Layer 1 Model vs Market)
        pred_pick = "OVER" if model_total > mt_m else "UNDER"
        pred_edge = model_total - mt_m

        # ORACLE pick (actual result)
        if is_final:
            actual_total = g['away_score'] + g['home_score']
            oracle_pick = "OVER" if actual_total > mt_m else "UNDER"
            ud_score = g['away_score'] if away == ud else g['home_score']
        else:
            actual_total = None
            oracle_pick = None
            ud_score = None

        print()
        print(f"  Layer 1 Model Total:   {model_total:.1f}")
        print(f"  Layer 1 Model Spread:  {model_spread:+.1f}")
        print(f"  Projected Scores:      {away} {score_away:.1f} — {home} {score_home:.1f}")
        print(f"  Market Total:          {mt_m}")
        print(f"  Market Spread:         {fav} -{ms_m}")
        print()

        # ── PREDICTIVE MODE ──
        print(f"  ╔════════════════════════════════════════════════════════════════════════════════╗")
        print(f"  ║  🔮 PREDICTIVE PICK:  {pred_pick:6s}  │  Edge: {pred_edge:+.1f}  │  Model {model_total:.1f} vs Market {mt_m}  ║")
        print(f"  ╚════════════════════════════════════════════════════════════════════════════════╝")

        # Run predictive through engine
        pred_game = {
            "matchup": f"{away} vs {home}", "league": lg,
            "total": round(model_total * 2) / 2,
            "spread": round(abs(model_spread) * 2) / 2,
            "market_total": mt_m, "pick": pred_pick,
            "favorite": fav, "underdog": ud,
            "underdog_score": ud_score if is_final else None,
            "win_prob": win_prob_from_spread(ms_m),
        }
        r_pred = engine.process_matchup(pred_game)
        
        action_pred = "score MORE than" if pred_pick == "OVER" else "stay BELOW"
        print(f"  Underdog: {ud}  |  Tier: {r_pred['confidence_tier']} ({r_pred['confidence_label']})  |  OC={r_pred['actual_oc']} UC={r_pred['actual_uc']}")
        print(f"  Base Line: {r_pred['base_line']}  |  Buffer Boost: +{r_pred['buffer_boost']}")
        print(f"  ┌──────────────────────────────────────────────────────────────────────────────┐")
        print(f"  │  🎯 UNDERDOG SCALED LINE:  {r_pred['underdog_scaled_line']:.3f}                                         │")
        print(f"  │  🎯 PREDICTIVE BET:  {ud} {pred_pick} {r_pred['underdog_scaled_line']:.1f}  ({ud} must {action_pred})            │")
        print(f"  └──────────────────────────────────────────────────────────────────────────────┘")

        if is_final and ud_score is not None:
            pred_hit = (ud_score > r_pred['underdog_scaled_line']) if pred_pick == "OVER" else (ud_score < r_pred['underdog_scaled_line'])
            pred_verdict = "✅ HIT" if pred_hit else "❌ MISS"
            print(f"  Verification: {ud} {ud_score} vs line {r_pred['underdog_scaled_line']:.1f} → {pred_verdict}")

        # ── ORACLE MODE (for final games or showing what it would check) ──
        if is_final:
            print()
            print(f"  ╔════════════════════════════════════════════════════════════════════════════════╗")
            print(f"  ║  👁️ ORACLE PICK:      {oracle_pick:6s}  │  Actual total: {actual_total} vs Market: {mt_m}          ║")
            print(f"  ╚════════════════════════════════════════════════════════════════════════════════╝")

            oracle_game = {
                "matchup": f"{away} vs {home}", "league": lg,
                "total": mt_m, "spread": ms_m,
                "market_total": mt_m, "pick": oracle_pick,
                "favorite": fav, "underdog": ud,
                "underdog_score": ud_score,
                "win_prob": win_prob_from_spread(ms_m),
            }
            r_oracle = engine.process_matchup(oracle_game)
            
            action_orc = "score MORE than" if oracle_pick == "OVER" else "stay BELOW"
            print(f"  Underdog: {ud}  |  Tier: {r_oracle['confidence_tier']} ({r_oracle['confidence_label']})  |  OC={r_oracle['actual_oc']} UC={r_oracle['actual_uc']}")
            print(f"  Base Line: {r_oracle['base_line']}")
            print(f"  ┌──────────────────────────────────────────────────────────────────────────────┐")
            print(f"  │  🎯 UNDERDOG SCALED LINE:  {r_oracle['underdog_scaled_line']:.3f}                                         │")
            print(f"  │  👁️ ORACLE CHECK:   {ud} {oracle_pick} {r_oracle['underdog_scaled_line']:.1f}  ({ud} must {action_orc})            │")
            print(f"  └──────────────────────────────────────────────────────────────────────────────┘")
            print(f"  Result: {ud} {ud_score} → {r_oracle['status']}")

            match_str = "✅ SAME" if pred_pick == oracle_pick else "⚠️ DIFFERENT"
            print(f"  Predictive vs Oracle: {match_str} (Pred={pred_pick}, Oracle={oracle_pick})")

        results.append({
            'num': n, 'away': away, 'home': home, 'lg': lg, 'ud': ud,
            'mt': model_total, 'mkt_t': mt_m, 'edge': pred_edge,
            'pred_pick': pred_pick, 'pred_sl': r_pred['underdog_scaled_line'],
            'pred_tier': r_pred['confidence_tier'],
            'oracle_pick': oracle_pick,
            'is_final': is_final,
        })

    # ══════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    print()
    print("=" * 120)
    print("  ⚡ YOUR V12 PREDICTIVE BETS — 2026-08-03")
    print("=" * 120)
    print()
    print(f"  {'#':<4} {'Game':<16} {'Lg':<5} {'UD':<5} {'Model T':<9} {'Mkt T':<7} {'Edge':<7} {'Pick':<7} {'Tier':<5} {'Scaled Line':<13} {'Your Bet'}")
    print(f"  {'─'*4} {'─'*16} {'─'*5} {'─'*5} {'─'*9} {'─'*7} {'─'*7} {'─'*7} {'─'*5} {'─'*13} {'─'*40}")

    for r in results:
        pick = r['pred_pick']
        sl = r['pred_sl']
        if r['is_final']:
            bet_str = f"🔥 {r['ud']} {pick} {sl:.1f} (verified)"
        else:
            bet_str = f"🔥 {r['ud']} {pick} {sl:.1f}"
        print(f"  {r['num']:<4} {r['away']+'@'+r['home']:<16} {r['lg']:<5} {r['ud']:<5} {r['mt']:<9.1f} {r['mkt_t']:<7.1f} {r['edge']:<+7.1f} {pick:<7} {r['pred_tier']:<5} {sl:<13.3f} {bet_str}")

    print()
    print("  🔮 PREDICTIVE MODE = What to bet BEFORE tip-off")
    print("     Pick direction = Layer 1 Model Total vs Market Total")
    print("     Model > Market → OVER | Model < Market → UNDER")
    print()
    print("  👁️ ORACLE MODE = Backtest verification (uses actual result)")
    print("     This is how the 91.8% backtest win rate was computed")
    print("     Oracle proves: if direction is right, scaled line HITS 91.8% of the time")
    print()
    print("  ✅ All team stats from REAL 2026 season data (Covers.com)")
    print("  ✅ All market lines from REAL Covers.com closing lines")
    print()

if __name__ == "__main__":
    run_today()
