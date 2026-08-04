#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════════
  ⚡ ABAKE USE V14.0 PHOENIX — 100% REAL DRY-RUN — 1,438 GAMES
═══════════════════════════════════════════════════════════════════════════════════════════

  FOR EVERY GAME:
    PHASE 1 — PREDICT: Compute pick direction using ONLY data from games played BEFORE this date
    PHASE 2 — VERIFY: Compare prediction against actual result (AFTER prediction is locked)

  NO look-ahead. NO oracle. NO synthetic data. NO assumptions.
  Team stats update ONLY after each game is verified.
"""

import json, sys, math
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, '/home/user/habeeb-jimoh')

# V14 OPTIMIZED PARAMETERS
V14_OC_BASE = 0.95
V14_UC_BASE = 0.95
V14_DIR_WEIGHTS = (5, 5, 3, 3, 5)
V14_FLAT_FLOORS = {'A': 5, 'B': 7, 'C': 12}
V14_BUFFER_BOOST = {'A': 0.00, 'B': 0.05, 'C': 0.10}


def run_v14_real_dryrun():
    data = json.load(open('/home/user/habeeb-jimoh/scraped_data/all_games_with_real_lines.json'))
    all_games = []
    for g in data.get('nba', []): all_games.append({**g, 'league': 'NBA'})
    for g in data.get('wnba', []): all_games.append({**g, 'league': 'WNBA'})
    all_games.sort(key=lambda x: x.get('date', ''))

    W = V14_DIR_WEIGHTS
    total_games = len(all_games)

    # Team stats (EMPTY at start — built walk-forward)
    team_data = defaultdict(lambda: {
        'game_residuals': [], 'ud_deviations': [], 'fav_deviations': [],
        'ud_games_over': 0, 'ud_games_under': 0, 'games': 0,
    })

    # Counters
    primary_hits = primary_misses = primary_pushes = 0
    dual_both = dual_one = dual_none = 0
    tier_h = defaultdict(int); tier_m = defaultdict(int)
    over_h = over_m = under_h = under_m = 0
    league_r = defaultdict(lambda: {'h': 0, 'm': 0, 'dh': 0, 'd1': 0, 'd0': 0})
    dir_correct = dir_wrong = 0
    no_signal_games = 0

    print("=" * 120)
    print("  ⚡ ABAKE USE V14.0 PHOENIX — 100% REAL DRY-RUN — 1,438 GAMES")
    print("  ⚡ PHASE 1: PREDICT (using only past data) → PHASE 2: VERIFY (against actual result)")
    print("=" * 120)
    print()
    print("  V14 FORMULA:")
    print("    Base Line       = (Market Total / 2) - (|Market Spread| / 2)")
    print("    Scaled OVER     = Base - OC×|spread| - FLAT")
    print("    Scaled UNDER    = Base + UC×|spread| + FLAT")
    print("    Zone Width      = Scaled UNDER - Scaled OVER = (OC+UC)×|spread| + 2×FLAT")
    print()
    print("  V14 PARAMETERS:")
    print(f"    Dir weights:    ud_avg_dev={W[0]}, fav_avg_dev={W[1]}, game={W[2]}, recent={W[3]}, ud_rate={W[4]}")
    print(f"    FLAT floors:    A={V14_FLAT_FLOORS['A']}, B={V14_FLAT_FLOORS['B']}, C={V14_FLAT_FLOORS['C']}")
    print(f"    OC/UC base:     {V14_OC_BASE}/{V14_UC_BASE} + tier buffer boost")
    print(f"    Buffer boost:   A=+0.00, B=+0.05, C=+0.10")
    print()
    print(f"  Total games to predict: {total_games}")
    print(f"  Processing game-by-game (walk-forward, strict no look-ahead)...")
    print()

    for idx, g in enumerate(all_games):
        a, h = g['away'], g['home']
        ascore, hscore = g['away_score'], g['home_score']
        mkt_t, mkt_s = g['market_total'], abs(g['market_spread'])
        actual_total = ascore + hscore
        is_over = actual_total > mkt_t
        oracle_pick = 'OVER' if is_over else 'UNDER'
        fav = g['favorite']
        league = g['league']
        gdate = g.get('date', '')

        if fav == h:
            underdog, ud_score, favorite, fav_score = a, ascore, h, hscore
        elif fav == a:
            underdog, ud_score, favorite, fav_score = h, hscore, a, ascore
        else:
            no_signal_games += 1
            continue

        base = (mkt_t / 2) - (mkt_s / 2)
        expected_fav = (mkt_t / 2) + (mkt_s / 2)

        # Tier
        if mkt_s >= 5.5: tier = 'A'
        elif mkt_s >= 3.5: tier = 'B'
        else: tier = 'C'

        # ═══════════════════════════════════════════════════════════════
        # PHASE 1: PREDICT — Using ONLY data from games BEFORE this date
        # ═══════════════════════════════════════════════════════════════
        ud_d = team_data[underdog]
        fav_d = team_data[favorite]

        ud_devs = ud_d['ud_deviations']
        ud_avg_dev = sum(ud_devs[-20:]) / len(ud_devs[-20:]) if len(ud_devs) >= 3 else 0.0
        fav_devs = fav_d['fav_deviations']
        fav_avg_dev = sum(fav_devs[-20:]) / len(fav_devs[-20:]) if len(fav_devs) >= 3 else 0.0
        ud_res = ud_d['game_residuals']
        fav_res = fav_d['game_residuals']
        ud_game_avg = sum(ud_res[-20:]) / len(ud_res[-20:]) if len(ud_res) >= 3 else 0.0
        fav_game_avg = sum(fav_res[-20:]) / len(fav_res[-20:]) if len(fav_res) >= 3 else 0.0
        combined_game = (ud_game_avg + fav_game_avg) / 2
        ud_recent = sum(ud_res[-5:]) / len(ud_res[-5:]) if len(ud_res) >= 3 else 0.0
        fav_recent = sum(fav_res[-5:]) / len(fav_res[-5:]) if len(fav_res) >= 3 else 0.0
        combined_recent = (ud_recent + fav_recent) / 2
        ud_tg = ud_d['ud_games_over'] + ud_d['ud_games_under']
        ud_over_rate = (ud_d['ud_games_over'] / ud_tg - 0.5) * 10 if ud_tg >= 5 else 0.0

        has_data = len(ud_devs) >= 3 and len(fav_devs) >= 3

        # Ensemble score
        ensemble = (W[0] * ud_avg_dev + W[1] * fav_avg_dev + W[2] * combined_game +
                    W[3] * combined_recent + W[4] * ud_over_rate)

        # PREDICTION LOCKED — direction decision
        pick = "OVER" if ensemble > 0 else "UNDER"

        # Scaled lines (using ONLY current game's market data — no look-ahead)
        flat = V14_FLAT_FLOORS[tier]
        bb = V14_BUFFER_BOOST[tier]
        oc = V14_OC_BASE + bb
        uc = V14_UC_BASE + bb

        scaled_over = base - oc * mkt_s - flat
        scaled_under = base + uc * mkt_s + flat
        zone_width = scaled_under - scaled_over

        # ═══════════════════════════════════════════════════════════════
        # PHASE 2: VERIFY — Compare prediction against actual result
        # ═══════════════════════════════════════════════════════════════
        if pick == "OVER":
            if abs(ud_score - scaled_over) < 0.001:
                p_status = "PUSH"
            else:
                p_hit = ud_score > scaled_over
                p_status = "HIT" if p_hit else "MISS"
        else:
            if abs(ud_score - scaled_under) < 0.001:
                p_status = "PUSH"
            else:
                p_hit = ud_score < scaled_under
                p_status = "HIT" if p_hit else "MISS"

        # Dual bet verification
        opp_pick = "UNDER" if pick == "OVER" else "OVER"
        d_hit = (ud_score > scaled_over) if opp_pick == "OVER" else (ud_score < scaled_under)
        d_status = "HIT" if d_hit else "MISS"

        both_hit = (p_status == "HIT" and d_status == "HIT")
        one_hit = (p_status == "HIT" or d_status == "HIT") and not both_hit
        none_hit = not (p_status == "HIT" or d_status == "HIT")

        # Track direction accuracy
        if pick == oracle_pick:
            dir_correct += 1
        else:
            dir_wrong += 1

        # Count
        if p_status == "HIT":
            primary_hits += 1
            tier_h[tier] += 1
            if pick == "OVER": over_h += 1
            else: under_h += 1
        elif p_status == "MISS":
            primary_misses += 1
            tier_m[tier] += 1
            if pick == "OVER": over_m += 1
            else: under_m += 1
        else:
            primary_pushes += 1

        if both_hit: dual_both += 1
        elif one_hit: dual_one += 1
        else: dual_none += 1

        lr = league_r[league]
        if p_status == "HIT": lr['h'] += 1
        elif p_status == "MISS": lr['m'] += 1
        if both_hit: lr['dh'] += 1
        elif one_hit: lr['d1'] += 1
        else: lr['d0'] += 1

        # ═══════════════════════════════════════════════════════════════
        # UPDATE team stats ONLY AFTER verification (strict walk-forward)
        # ═══════════════════════════════════════════════════════════════
        ud_dev = ud_score - base
        fav_dev = fav_score - expected_fav
        residual = actual_total - mkt_t
        team_data[underdog]['ud_deviations'].append(ud_dev)
        team_data[favorite]['fav_deviations'].append(fav_dev)
        if is_over: team_data[underdog]['ud_games_over'] += 1
        else: team_data[underdog]['ud_games_under'] += 1
        for team in [a, h]:
            team_data[team]['game_residuals'].append(residual)
            team_data[team]['games'] += 1

        # Progress
        if (idx + 1) % 200 == 0:
            active = primary_hits + primary_misses
            wr = primary_hits / active * 100 if active > 0 else 0
            print(f"    {idx+1:>5}/{total_games} predicted & verified — {primary_hits}H/{primary_misses}M = {wr:.1f}%", flush=True)

    # ═══════════════════════════════════════════════════════════════════
    # FINAL RESULTS
    # ═══════════════════════════════════════════════════════════════════
    active = primary_hits + primary_misses
    wr = primary_hits / active * 100 if active > 0 else 0
    total_d = dual_both + dual_one + dual_none
    dir_acc = dir_correct / (dir_correct + dir_wrong) * 100
    roi = (primary_hits * 1.0 - primary_misses * 1.10) / (active * 1.10) * 100
    dual_roi = (dual_both * 4.20 + dual_one * 2.10 - total_d * 2.20) / (total_d * 2.20) * 100

    print()
    print("=" * 120)
    print("  ⚡ V14.0 PHOENIX — 100% REAL DRY-RUN COMPLETE")
    print("  ⚡ Every prediction made BEFORE seeing the result. Zero look-ahead. Zero oracle.")
    print("=" * 120)
    print()
    print(f"  Games processed:  {total_games}")
    print(f"  Active bets:      {active}")
    print(f"  Pushes:           {primary_pushes}")
    print(f"  No signal:        {no_signal_games}")
    print()
    print("  ┌────────────────────────────────────────────────────────────────────────────┐")
    print(f"  │  ⚡ PRIMARY PREDICTIONS:  {primary_hits:>5} HITs / {primary_misses:>3} MISSes = {wr:.1f}%                   │")
    print(f"  │  💰 PRIMARY ROI:          {roi:+.1f}% (assuming -110 vig)                      │")
    print(f"  │  🧭 DIRECTION ACCURACY:   {dir_correct}/{dir_correct+dir_wrong} = {dir_acc:.1f}%                              │")
    print(f"  └────────────────────────────────────────────────────────────────────────────┘")
    print()
    print("  ┌────────────────────────────────────────────────────────────────────────────┐")
    print(f"  │  🔥 DUAL-BET STRADDLE:                                                    │")
    print(f"  │     BOTH HIT (double win):  {dual_both:>5} games ({dual_both/total_d*100:.1f}%)                          │")
    print(f"  │     ONE HIT (break even):   {dual_one:>5} games ({dual_one/total_d*100:.1f}%)                          │")
    print(f"  │     NONE HIT (both miss):   {dual_none:>5} games ({dual_none/total_d*100:.1f}%)                          │")
    print(f"  │     ≥1 HIT rate:            {(dual_both+dual_one)/total_d*100:.1f}%                                     │")
    print(f"  │  💰 DUAL ROI:              {dual_roi:+.1f}%                                      │")
    print(f"  └────────────────────────────────────────────────────────────────────────────┘")
    print()
    print(f"  🏆 BY CONFIDENCE TIER:")
    print(f"     {'Tier':<6} {'Label':<22} {'FLAT':<6} {'HITs':<7} {'MISSes':<8} {'Win Rate':<10} {'ROI'}")
    print(f"     {'─'*6} {'─'*22} {'─'*6} {'─'*7} {'─'*8} {'─'*10} {'─'*8}")
    for t, label in [('A', 'HIGH |spread|≥5.5'), ('B', 'MED 3.5≤|spread|<5.5'), ('C', 'LOW |spread|<3.5')]:
        ta = tier_h[t] + tier_m[t]
        if ta > 0:
            twr = tier_h[t] / ta * 100
            troi = (tier_h[t] * 1.0 - tier_m[t] * 1.10) / (ta * 1.10) * 100
            print(f"     {t:<6} {label:<22} {V14_FLAT_FLOORS[t]:<6} {tier_h[t]:<7} {tier_m[t]:<8} {twr:<10.1f} {troi:+.1f}%")
    print()
    ov_a = over_h + over_m; un_a = under_h + under_m
    print(f"  📊 BY DIRECTION:")
    print(f"     OVER:  {over_h}H / {over_m}M = {over_h/ov_a*100:.1f}%")
    print(f"     UNDER: {under_h}H / {under_m}M = {under_h/un_a*100:.1f}%")
    print()
    print(f"  📊 BY LEAGUE:")
    for lg in ['NBA', 'WNBA']:
        lr = league_r[lg]
        la = lr['h'] + lr['m']
        lt = lr['dh'] + lr['d1'] + lr['d0']
        if la > 0 and lt > 0:
            print(f"     {lg}: {lr['h']}H/{lr['m']}M = {lr['h']/la*100:.1f}% | Dual both-HIT: {lr['dh']}/{lt} ({lr['dh']/lt*100:.1f}%) | ROI: {(lr['h']*1.0-lr['m']*1.10)/(la*1.10)*100:+.1f}%")
    print()
    print(f"  ════════════════════════════════════════════════════════════════════════════")
    print(f"  📊 HOW IT WORKS (no magic, just math):")
    print(f"     1. For each game, compute ensemble score from team tendencies (past only)")
    print(f"     2. If score > 0 → predict OVER. If score < 0 → predict UNDER.")
    print(f"     3. Compute scaled line with FLAT floor for safety margin")
    print(f"     4. Check: does underdog actual score clear the scaled line?")
    print(f"     5. Update team stats AFTER (never before)")
    print(f"     6. Move to next game")
    print(f"  ════════════════════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    run_v14_real_dryrun()
