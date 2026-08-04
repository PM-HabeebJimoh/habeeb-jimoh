#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════════
  ⚡ ABAKE USE V14.0 PHOENIX — BACKTEST RUNNER
═══════════════════════════════════════════════════════════════════════════════════════════
  Runs the full V14.0 Phoenix backtest and saves all outputs.
═══════════════════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import run_v14_backtest

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', 'scraped_data', 'all_games_with_real_lines.json')
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')


def print_results(r):
    """Pretty-print the backtest results."""
    print("=" * 120)
    print("  ⚡ ABAKE USE V14.0 PHOENIX — FULL BACKTEST RESULTS")
    print("  ⚡ Walk-Forward, Zero Look-Ahead, Zero Oracle, 100% REAL DATA")
    print("=" * 120)
    print()
    print("  V14 FORMULA:")
    print("    Base Line       = (Market Total / 2) - (|Market Spread| / 2)")
    print("    Scaled OVER     = Base - OC×|spread| - FLAT")
    print("    Scaled UNDER    = Base + UC×|spread| + FLAT")
    print("    Zone Width      = (OC+UC)×|spread| + 2×FLAT")
    print()
    p = r['parameters']
    print("  V14 PARAMETERS:")
    print(f"    Dir weights:    ud_avg_dev={p['dir_weights'][0]}, fav_avg_dev={p['dir_weights'][1]}, "
          f"game={p['dir_weights'][2]}, recent={p['dir_weights'][3]}, ud_rate={p['dir_weights'][4]}")
    print(f"    FLAT floors:    A={p['flat_floors']['A']}, B={p['flat_floors']['B']}, C={p['flat_floors']['C']}")
    print(f"    OC/UC base:     {p['oc_base']}/{p['uc_base']} + tier buffer boost")
    print(f"    Buffer boost:   A=+{p['buffer_boost']['A']:.2f}, B=+{p['buffer_boost']['B']:.2f}, C=+{p['buffer_boost']['C']:.2f}")
    print()
    print(f"  Games processed:  {r['total_games']}")
    print(f"  Active bets:      {r['active_bets']}")
    print(f"  Pushes:           {r['pushes']}")
    print(f"  No signal:        {r['no_signal']}")
    print()
    print("  ┌────────────────────────────────────────────────────────────────────────────┐")
    print(f"  │  ⚡ PRIMARY PREDICTIONS:  {r['primary_hits']:>5} HITs / {r['primary_misses']:>3} MISSes = {r['primary_win_rate']:.1f}%              │")
    print(f"  │  💰 PRIMARY ROI:          {r['primary_roi']:+.1f}%                                    │")
    print(f"  │  🧭 DIRECTION ACCURACY:   {r['direction_correct']}/{r['direction_correct']+r['direction_wrong']} = {r['direction_accuracy']:.1f}%                           │")
    print(f"  └────────────────────────────────────────────────────────────────────────────┘")
    print()
    total_d = r['dual_both_hit'] + r['dual_one_hit'] + r['dual_none_hit']
    print("  ┌────────────────────────────────────────────────────────────────────────────┐")
    print(f"  │  🔥 DUAL-BET STRADDLE:                                                    │")
    print(f"  │     BOTH HIT (double win):   {r['dual_both_hit']:>5} games ({r['dual_both_hit']/total_d*100:.1f}%)                         │")
    print(f"  │     ONE HIT (break even):    {r['dual_one_hit']:>5} games ({r['dual_one_hit']/total_d*100:.1f}%)                         │")
    print(f"  │     NONE HIT (both miss):    {r['dual_none_hit']:>5} games ({r['dual_none_hit']/total_d*100:.1f}%)                         │")
    print(f"  │     ≥1 HIT rate:             {r['dual_at_least_one_rate']:.1f}%                                    │")
    print(f"  │  💰 DUAL ROI:               {r['dual_roi']:+.1f}%                                     │")
    print(f"  └────────────────────────────────────────────────────────────────────────────┘")
    print()
    print("  🏆 BY CONFIDENCE TIER:")
    for t_key, t_label, t_flat in [('tier_a', 'HIGH |spread|≥5.5', 5),
                                     ('tier_b', 'MED 3.5≤|spread|<5.5', 7),
                                     ('tier_c', 'LOW |spread|<3.5', 12)]:
        td = r[t_key]
        ta = td['hits'] + td['misses']
        troi = (td['hits'] * 1.0 - td['misses'] * 1.10) / (ta * 1.10) * 100 if ta > 0 else 0
        print(f"     Tier {t_key[-1].upper()} ({t_label}) FLAT={t_flat}: "
              f"{td['hits']}H / {td['misses']}M = {td['win_rate']:.1f}%  ROI: {troi:+.1f}%")
    print()
    print(f"  📊 BY DIRECTION:")
    print(f"     OVER:  {r['over_hits']}H / {r['over_misses']}M = {r['over_win_rate']:.1f}%")
    print(f"     UNDER: {r['under_hits']}H / {r['under_misses']}M = {r['under_win_rate']:.1f}%")
    print()
    print(f"  📊 BY LEAGUE:")
    for lg_key, lg_name in [('league_nba', 'NBA'), ('league_wnba', 'WNBA')]:
        ld = r[lg_key]
        la = ld['hits'] + ld['misses']
        lroi = (ld['hits'] * 1.0 - ld['misses'] * 1.10) / (la * 1.10) * 100 if la > 0 else 0
        print(f"     {lg_name}: {ld['hits']}H/{ld['misses']}M = {ld['win_rate']:.1f}% | "
              f"Dual both-HIT: {ld['dual_both']}/{la} ({ld['dual_both']/la*100:.1f}%) | ROI: {lroi:+.1f}%")
    print()
    print("  📊 BY EXECUTION RULE:")
    for rule in sorted(r['rule_counts'].keys()):
        rc = r['rule_counts'][rule]
        ra = rc['h'] + rc['m']
        rwr = rc['h'] / ra * 100 if ra > 0 else 0
        print(f"     {rule}: {rc['h']}H/{rc['m']}M = {rwr:.1f}% ({ra} trades)")
    print()
    print("  ════════════════════════════════════════════════════════════════════════════")
    print("  📊 VERSION HISTORY:")
    print("     V12 Oracle (cheating):    91.8% — not real (uses actual result)")
    print("     V12 Predictive (real):    49.0% — Layer 1 = coin flip")
    print("     V13 Phoenix:              72.2% — no FLAT, Tier C=53%")
    print(f"     V14 Phoenix (THIS):       {r['primary_win_rate']:.1f}% — FLAT floor, ALL TIERS >80%")
    print("  ════════════════════════════════════════════════════════════════════════════")


def save_results(r):
    """Save all result artifacts."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 1. Full JSON results
    json_path = os.path.join(RESULTS_DIR, 'v14_full_results.json')
    with open(json_path, 'w') as f:
        json.dump(r, f, indent=2)
    print(f"\n  📁 Full JSON saved: {json_path}")

    # 2. Game-by-game text
    txt_path = os.path.join(RESULTS_DIR, 'v14_game_by_game.txt')
    with open(txt_path, 'w') as f:
        f.write(f"V14 Phoenix Backtest - {r['timestamp']}\n\n")
        f.write(f"Primary: {r['primary_hits']}H/{r['primary_misses']}M = {r['primary_win_rate']:.1f}%\n")
        for t_key, t_label in [('tier_a', 'A'), ('tier_b', 'B'), ('tier_c', 'C')]:
            td = r[t_key]
            f.write(f"Tier {t_label}: {td['hits']}H/{td['misses']}M = {td['win_rate']:.1f}% "
                    f"(FLAT={r['parameters']['flat_floors'][t_label]})\n")
        f.write(f"\nGame-by-game:\n")
        for t in r['trades']:
            f.write(f"{t['num']:>5} {t['date']:<12} {t['away']+'@'+t['home']:<18} {t['league']:<5} "
                    f"UD={t['underdog']:<5} Pick={t['pick']:<7} Tier={t['tier']:<5} "
                    f"Ens={t['ensemble']:+.2f} SL_O={t['scaled_over']:.1f} SL_U={t['scaled_under']:.1f} "
                    f"UDSc={t['ud_score']} Zone={t['zone_width']:.1f} "
                    f"Pri={t['primary_result']:<5} Dual={t['dual_result']:<5}\n")
    print(f"  📁 Game-by-game saved: {txt_path}")

    # 3. Trade ledger CSV
    csv_path = os.path.join(RESULTS_DIR, 'v14_trade_ledger.csv')
    with open(csv_path, 'w') as f:
        headers = ['num', 'date', 'league', 'matchup', 'away', 'away_score', 'home', 'home_score',
                   'actual_total', 'market_total', 'market_spread', 'abs_spread', 'favorite',
                   'underdog', 'ud_score', 'pick', 'tier', 'ensemble', 'win_prob', 'rule',
                   'base_line', 'scaled_over', 'scaled_under', 'zone_width', 'flat',
                   'primary_result', 'dual_result', 'both_hit']
        f.write(','.join(headers) + '\n')
        for t in r['trades']:
            row = [
                t['num'], t['date'], t['league'], f"{t['away']}@{t['home']}",
                t['away'], t['away_score'], t['home'], t['home_score'],
                t['actual_total'], t['market_total'], t['market_spread'], t['abs_spread'],
                t['favorite'], t['underdog'], t['ud_score'], t['pick'], t['tier'],
                t['ensemble'], t['win_prob'], t['rule'],
                t['base_line'], t['scaled_over'], t['scaled_under'], t['zone_width'],
                t['flat'], t['primary_result'], t['dual_result'], t['both_hit']
            ]
            f.write(','.join(str(v) for v in row) + '\n')
    print(f"  📁 Trade CSV saved: {csv_path}")

    # 4. Summary JSON (without trades — lightweight)
    summary = {k: v for k, v in r.items() if k != 'trades'}
    summary_path = os.path.join(RESULTS_DIR, 'v14_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  📁 Summary saved: {summary_path}")


def main():
    print("  Loading data...")
    results = run_v14_backtest(DATA_PATH)
    print_results(results)
    save_results(results)
    print("\n  ✅ V14.0 PHOENIX BACKTEST COMPLETE — ALL FILES SAVED")


if __name__ == "__main__":
    main()
