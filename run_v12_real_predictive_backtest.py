#!/usr/bin/env python3
"""
ABAKE USE V12 — REAL PREDICTIVE BACKTEST
─────────────────────────────────────────
For EVERY game, compute Layer 1 Model Total from team stats (using ONLY games
played before that date — no look-ahead), then compare to Market Total for pick
direction, then verify HIT/MISS against the underdog scaled line.

THIS IS THE REAL TEST. No Oracle. No cheating.
"""

import math
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, '/home/user/habeeb-jimoh')
from abake_use_engine.core.engine import AbakeUseEngine

LEAGUE_AVG = {
    'WNBA': {'avg_total': 173.0, 'lg_pace': 80.2, 'lg_eff': 102.5},
    'NBA':  {'avg_total': 220.0, 'lg_pace': 100.4, 'lg_eff': 113.5},
}

COVERS_NBA = {"GS": "GSW", "NO": "NOP", "SA": "SAS", "BK": "BKN", "NY": "NYK", "PHO": "PHX"}
COVERS_WNBA = {"GS": "GS", "LA": "LA", "NY": "NY", "LV": "LV", "PHO": "PHO"}

def compute_team_stats_up_to(games_history, league, up_to_date):
    """
    Compute team ORtg/DRtg/Pace from ALL games played before up_to_date.
    No look-ahead — strict chronological cutoff.
    """
    raw = defaultdict(lambda: {'scored': [], 'allowed': [], 'totals': []})
    
    for g in games_history:
        # Parse date
        gdate = g.get('date', '')
        if gdate >= up_to_date:
            continue  # Skip games on or after this date
        
        away, home = g['away'], g['home']
        ascore, hscore = g['away_score'], g['home_score']
        
        for team, scored, allowed in [(away, ascore, hscore), (home, hscore, ascore)]:
            raw[team]['scored'].append(scored)
            raw[team]['allowed'].append(allowed)
            raw[team]['totals'].append(scored + allowed)
    
    result = {}
    lg = LEAGUE_AVG[league]
    for team, s in raw.items():
        if len(s['scored']) < 3:  # Need at least 3 games for stable stats
            continue
        gp = len(s['scored'])
        ppg = sum(s['scored']) / gp
        dppg = sum(s['allowed']) / gp
        avg_t = sum(s['totals']) / gp
        pace = (avg_t / lg['avg_total']) * lg['lg_pace']
        ortg = ppg * (100.0 / pace)
        drtg = dppg * (100.0 / pace)
        result[team] = {
            'gp': gp, 'ortg': ortg, 'drtg': drtg, 'pace': pace,
            'ppg': ppg, 'dppg': dppg, 'avg_total': avg_t,
        }
    
    return result

def win_prob_from_spread(spread):
    return round(50.0 / (1.0 + math.exp(0.35 * (abs(spread) - 1.5))), 1)

def run_real_predictive_backtest():
    data = json.load(open('/home/user/habeeb-jimoh/scraped_data/all_games_with_real_lines.json'))
    engine = AbakeUseEngine(v12_mode=True, use_spread_tiers=True, use_confidence_grading=True)
    
    # Combine all games
    all_games = []
    for g in data.get('nba', []):
        all_games.append({**g, 'league': 'NBA'})
    for g in data.get('wnba', []):
        all_games.append({**g, 'league': 'WNBA'})
    
    # Sort by date
    all_games.sort(key=lambda x: x.get('date', ''))
    
    total = len(all_games)
    print("=" * 120)
    print("  ⚡ ABAKE USE V12 — REAL PREDICTIVE BACKTEST — NO ORACLE — NO CHEATING")
    print("=" * 120)
    print()
    print("  For EVERY game:")
    print("    1. Compute team ORtg/DRtg/Pace from games played BEFORE this date (no look-ahead)")
    print("    2. Layer 1: Model Total from team efficiency ratings")
    print("    3. Pick Direction: Model Total vs Market Total")
    print("    4. V12 Scaled Line → verify HIT/MISS against actual underdog score")
    print()
    print(f"  Total games: {total}")
    print(f"  Processing...", flush=True)
    
    hits = misses = pushes = skips = no_stats = 0
    over_hits = over_misses = under_hits = under_misses = 0
    tier_a_h = tier_a_m = tier_b_h = tier_b_m = tier_c_h = tier_c_m = 0
    oracle_agree = oracle_disagree = 0
    
    # Track per-league results
    league_results = defaultdict(lambda: {'hits': 0, 'misses': 0, 'pushes': 0, 'skips': 0, 'no_stats': 0})
    
    # Separate game lists by league for stat computation
    nba_games = [g for g in all_games if g['league'] == 'NBA']
    wnba_games = [g for g in all_games if g['league'] == 'WNBA']
    
    # Cache stats by date to avoid recomputation
    stats_cache = {}
    
    details = []
    
    for i, g in enumerate(all_games):
        league = g['league']
        away, home = g['away'], g['home']
        ascore, hscore = g['away_score'], g['home_score']
        market_total = g['market_total']
        market_spread = g['market_spread']
        favorite = g['favorite']
        gdate = g.get('date', '')
        
        actual_total = ascore + hscore
        
        # Determine underdog and underdog score
        if favorite == home:
            underdog = away
            underdog_score = ascore
        elif favorite == away:
            underdog = home
            underdog_score = hscore
        else:
            # Can't determine favorite
            skips += 1
            continue
        
        # Get team stats up to this date (no look-ahead)
        cache_key = (league, gdate)
        if cache_key not in stats_cache:
            history = nba_games if league == 'NBA' else wnba_games
            stats_cache[cache_key] = compute_team_stats_up_to(history, league, gdate)
        
        team_stats = stats_cache[cache_key]
        
        # Check if we have stats for both teams
        if away not in team_stats or home not in team_stats:
            no_stats += 1
            league_results[league]['no_stats'] += 1
            continue
        
        # Layer 1: Compute Model Total and Model Spread
        a_s = team_stats[away]
        h_s = team_stats[home]
        
        row = {
            'league': league,
            'away_pace': a_s['pace'], 'home_pace': h_s['pace'],
            'away_ortg': a_s['ortg'], 'home_drtg': h_s['drtg'],
            'home_ortg': h_s['ortg'], 'away_drtg': a_s['drtg'],
        }
        
        model_total, model_spread, proj_pace, score_away, score_home = \
            engine.calculate_independent_baselines(row)
        
        # PREDICTIVE PICK: Model Total vs Market Total
        pred_pick = "OVER" if model_total > market_total else "UNDER"
        edge = model_total - market_total
        
        # ORACLE PICK (for comparison only — NOT used for the bet)
        oracle_pick = "OVER" if actual_total > market_total else "UNDER"
        
        if pred_pick == oracle_pick:
            oracle_agree += 1
        else:
            oracle_disagree += 1
        
        # Run through V12 engine
        game_dict = {
            "matchup": f"{away} vs {home}",
            "league": league,
            "total": round(model_total * 2) / 2,  # Round to nearest 0.5
            "spread": round(abs(model_spread) * 2) / 2,
            "market_total": market_total,
            "pick": pred_pick,
            "favorite": favorite,
            "underdog": underdog,
            "underdog_score": underdog_score,
            "win_prob": win_prob_from_spread(market_spread),
        }
        
        result = engine.process_matchup(game_dict)
        status = result['status']
        tier = result.get('confidence_tier', 'N/A')
        
        if status == "HIT":
            hits += 1
            league_results[league]['hits'] += 1
            if pred_pick == "OVER": over_hits += 1
            else: under_hits += 1
            if tier == "A": tier_a_h += 1
            elif tier == "B": tier_b_h += 1
            else: tier_c_h += 1
        elif status == "MISS":
            misses += 1
            league_results[league]['misses'] += 1
            if pred_pick == "OVER": over_misses += 1
            else: under_misses += 1
            if tier == "A": tier_a_m += 1
            elif tier == "B": tier_b_m += 1
            else: tier_c_m += 1
        elif status == "PUSH":
            pushes += 1
            league_results[league]['pushes'] += 1
        else:
            skips += 1
            league_results[league]['skips'] += 1
        
        details.append({
            'date': gdate, 'away': away, 'home': home, 'league': league,
            'model_total': model_total, 'market_total': market_total,
            'edge': edge, 'pred_pick': pred_pick, 'oracle_pick': oracle_pick,
            'underdog': underdog, 'scaled_line': result.get('underdog_scaled_line', 0),
            'underdog_score': underdog_score, 'status': status,
            'tier': tier, 'match': pred_pick == oracle_pick,
        })
        
        if (i + 1) % 200 == 0:
            active = hits + misses
            wr = (hits / active * 100) if active > 0 else 0
            print(f"    {i+1}/{total} processed — {hits}H/{misses}M = {wr:.1f}%", flush=True)
    
    active = hits + misses
    win_rate = (hits / active * 100) if active > 0 else 0
    pick_accuracy = (oracle_agree / (oracle_agree + oracle_disagree) * 100) if (oracle_agree + oracle_disagree) > 0 else 0
    
    print()
    print("=" * 120)
    print("  ⚡ REAL PREDICTIVE BACKTEST COMPLETE — NO ORACLE — NO CHEATING")
    print("=" * 120)
    print()
    print(f"  Total games:        {total}")
    print(f"  No team stats:      {no_stats} (skipped — not enough prior games)")
    print(f"  Active bets:        {active}")
    print(f"  System skips:       {skips}")
    print(f"  Pushes:             {pushes}")
    print()
    print(f"  ┌────────────────────────────────────────────────────────────────────┐")
    print(f"  │  ✅ HITs:              {hits:>6d}                                        │")
    print(f"  │  ❌ MISSes:            {misses:>6d}                                        │")
    print(f"  │  ➖ PUSHes:            {pushes:>6d}                                        │")
    print(f"  │  🏆 WIN RATE:          {win_rate:>6.1f}%                                       │")
    print(f"  └────────────────────────────────────────────────────────────────────┘")
    print()
    print(f"  📊 Pick Direction Accuracy (Predictive vs Oracle):")
    print(f"     Predictive agreed with Oracle:  {oracle_agree} / {oracle_agree + oracle_disagree} = {pick_accuracy:.1f}%")
    print(f"     Predictive disagreed:           {oracle_disagree}")
    print()
    print(f"  📊 By Category:")
    print(f"     OVER:   {over_hits}H / {over_misses}M = {(over_hits/(over_hits+over_misses)*100) if (over_hits+over_misses)>0 else 0:.1f}%")
    print(f"     UNDER:  {under_hits}H / {under_misses}M = {(under_hits/(under_hits+under_misses)*100) if (under_hits+under_misses)>0 else 0:.1f}%")
    print()
    print(f"  📊 By Confidence Tier:")
    print(f"     A (HIGH):   {tier_a_h}H / {tier_a_m}M = {(tier_a_h/(tier_a_h+tier_a_m)*100) if (tier_a_h+tier_a_m)>0 else 0:.1f}%")
    print(f"     B (MEDIUM):  {tier_b_h}H / {tier_b_m}M = {(tier_b_h/(tier_b_h+tier_b_m)*100) if (tier_b_h+tier_b_m)>0 else 0:.1f}%")
    print(f"     C (LOW):    {tier_c_h}H / {tier_c_m}M = {(tier_c_h/(tier_c_h+tier_c_m)*100) if (tier_c_h+tier_c_m)>0 else 0:.1f}%")
    print()
    print(f"  📊 By League:")
    for lg in ['NBA', 'WNBA']:
        lr = league_results[lg]
        la = lr['hits'] + lr['misses']
        lwr = (lr['hits'] / la * 100) if la > 0 else 0
        print(f"     {lg}: {lr['hits']}H / {lr['misses']}M / {lr['no_stats']} no-stats = {lwr:.1f}% ({la} active bets)")
    print()
    print(f"  ────────────────────────────────────────────────────────────")
    print(f"  🔑 KEY INSIGHT:")
    print(f"  Oracle backtest (cheating):  91.8% — proves scaled lines work IF direction is correct")
    print(f"  Predictive backtest (real):  {win_rate:.1f}% — actual performance when system picks its own direction")
    print(f"  Pick accuracy:               {pick_accuracy:.1f}% — how often Layer 1 guesses the right OVER/UNDER")
    print()
    
    # Show some miss examples
    miss_examples = [d for d in details if d['status'] == 'MISS'][:10]
    if miss_examples:
        print(f"  📋 Sample MISSes (first 10):")
        print(f"  {'Date':<12} {'Game':<16} {'Lg':<5} {'Model T':<9} {'Mkt T':<7} {'Edge':<7} {'Pred':<7} {'Oracle':<7} {'UD':<5} {'SL':<8} {'UD Sc':<6} {'Match'}")
        for d in miss_examples:
            print(f"  {d['date']:<12} {d['away']+'@'+d['home']:<16} {d['league']:<5} {d['model_total']:<9.1f} {d['market_total']:<7.1f} {d['edge']:<+7.1f} {d['pred_pick']:<7} {d['oracle_pick']:<7} {d['underdog']:<5} {d['scaled_line']:<8.1f} {d['underdog_score']:<6} {'✅' if d['match'] else '❌'}")
        print()
    
    return details

if __name__ == "__main__":
    run_real_predictive_backtest()
