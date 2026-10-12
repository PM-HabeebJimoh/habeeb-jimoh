#!/usr/bin/env python3
"""
V12 Oracle Sensitivity Analysis — Find optimal multipliers and spread-tiered scaling.
Runs all 387 games with various OC/UC combinations to find the best parameters.
"""

import json
import math
import os

# ── Load game data ──
_script_dir = os.path.dirname(os.path.abspath(__file__))
_v12_root = os.path.dirname(_script_dir)
_repo_root = os.path.dirname(_v12_root)
_data_candidates = [
    os.path.join(_v12_root, "data", "all_games_with_real_lines.json"),
    os.path.join(_repo_root, "scraped_data", "all_games_with_real_lines.json"),
    "scraped_data/all_games_with_real_lines.json",
]
data = None
for candidate in _data_candidates:
    if os.path.exists(candidate):
        data = json.load(open(candidate))
        break
if data is None:
    raise FileNotFoundError("Cannot find all_games_with_real_lines.json")

COVERS_NBA = {
    "ATL": "ATL", "BOS": "BOS", "BK": "BKN", "BKN": "BKN", "CHA": "CHA",
    "CHI": "CHI", "CLE": "CLE", "DAL": "DAL", "DEN": "DEN", "DET": "DET",
    "GS": "GSW", "GSW": "GSW", "HOU": "HOU", "IND": "IND", "LAC": "LAC",
    "LAL": "LAL", "LA": "LAL", "MEM": "MEM", "MIA": "MIA", "MIL": "MIL",
    "MIN": "MIN", "NOP": "NOP", "NO": "NOP", "NY": "NYK", "NYK": "NYK",
    "OKC": "OKC", "ORL": "ORL", "PHI": "PHI", "PHO": "PHX", "PHX": "PHX",
    "POR": "POR", "SAC": "SAC", "SA": "SAS", "SAS": "SAS", "TOR": "TOR",
    "UTA": "UTA", "WAS": "WAS", "WSH": "WAS",
}
COVERS_WNBA = {
    "ATL": "ATL", "CHI": "CHI", "CON": "CON", "DAL": "DAL", "GS": "GS",
    "IND": "IND", "LA": "LA", "LV": "LV", "MIN": "MIN", "NY": "NY",
    "PHO": "PHX", "PDX": "POR", "SEA": "SEA", "TOR": "TOR", "WAS": "WSH",
}

def build_game(game, league):
    if league == "NBA":
        away = COVERS_NBA.get(game["away"], game["away"])
        home = COVERS_NBA.get(game["home"], game["home"])
    else:
        away = COVERS_WNBA.get(game["away"], game["away"])
        home = COVERS_WNBA.get(game["home"], game["home"])

    market_total = game["market_total"]
    market_spread = game["market_spread"]
    away_score = game["away_score"]
    home_score = game["home_score"]
    actual_total = away_score + home_score
    favorite = game["favorite"]

    if favorite == home:
        underdog = away
        underdog_score = away_score
    else:
        underdog = home
        underdog_score = home_score

    oracle_pick = "OVER" if actual_total > market_total else "UNDER"
    win_prob = round(50.0 / (1.0 + math.exp(0.35 * (market_spread - 1.5))), 1)

    return {
        "matchup": f"{away} vs {home}",
        "league": league,
        "total": market_total,
        "spread": market_spread,
        "pick": oracle_pick,
        "win_prob": win_prob,
        "underdog": underdog,
        "underdog_score": underdog_score,
        "market_total": market_total,
        "market_spread": market_spread,
    }

all_games = [build_game(g, "WNBA") for g in data["wnba"]] + [build_game(g, "NBA") for g in data["nba"]]
print(f"Total games: {len(all_games)}")

# ── Backtest function ──
def backtest(games, oc, uc, upset_threshold=15.0, use_upset_clause=True,
             spread_tiers=None):
    """
    Run backtest with given parameters.
    spread_tiers: dict of {tier_name: (min_spread, max_spread, oc, uc)} or None
    """
    hits = misses = 0
    results = []
    for g in games:
        total = g["total"]
        spread = abs(g["spread"])
        pick = g["pick"]
        underdog_score = g["underdog_score"]
        win_prob = g["win_prob"]

        # Check upset clause
        if use_upset_clause and pick == "UNDER" and win_prob > upset_threshold:
            results.append({"status": "SKIP", "reason": "upset"})
            continue

        # Check chaos exemption
        if g["matchup"] == "POR vs IND":
            results.append({"status": "SKIP", "reason": "chaos"})
            continue

        # Determine multipliers based on spread tier
        actual_oc = oc
        actual_uc = uc
        if spread_tiers:
            for tier_name, (min_s, max_s, tier_oc, tier_uc) in spread_tiers.items():
                if min_s <= spread <= max_s:
                    actual_oc = tier_oc
                    actual_uc = tier_uc
                    break

        # Layer 2: Base Line
        base_line = (total / 2) - (spread / 2)

        # Layer 3: Scaled Line
        if pick == "OVER":
            scaled_line = base_line - (actual_oc * spread)
            is_hit = underdog_score > scaled_line
        else:
            scaled_line = base_line + (actual_uc * spread)
            is_hit = underdog_score < scaled_line

        if is_hit:
            hits += 1
        else:
            misses += 1
        results.append({
            "status": "HIT" if is_hit else "MISS",
            "pick": pick,
            "spread": spread,
            "scaled_line": scaled_line,
            "underdog_score": underdog_score,
            "oc": actual_oc,
            "uc": actual_uc,
        })

    active = hits + misses
    win_rate = (hits / active * 100) if active > 0 else 0
    skips = len([r for r in results if r["status"] == "SKIP"])
    return {"hits": hits, "misses": misses, "skips": skips, "active": active, "win_rate": round(win_rate, 1)}

# ── Test 1: No upset clause, various OC/UC combinations ──
print("\n" + "=" * 80)
print("  SENSITIVITY ANALYSIS — No Upset Clause (all 387 games active)")
print("=" * 80)
print(f"  {'OC':>6} {'UC':>6} {'HITs':>6} {'MISSes':>6} {'Active':>6} {'WinRate':>8}")
print(f"  {'─'*6} {'─'*6} {'─'*6} {'─'*6} {'─'*6} {'─'*8}")

best_rate = 0
best_params = None
for oc in [0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
    for uc in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
        r = backtest(all_games, oc, uc, use_upset_clause=False)
        if r["win_rate"] > best_rate:
            best_rate = r["win_rate"]
            best_params = (oc, uc, r)
        print(f"  {oc:>6.2f} {uc:>6.2f} {r['hits']:>6} {r['misses']:>6} {r['active']:>6} {r['win_rate']:>7.1f}%")

print(f"\n  🏆 BEST: OC={best_params[0]}, UC={best_params[1]} → {best_params[2]['hits']}H/{best_params[2]['misses']}M = {best_params[2]['win_rate']}%")

# ── Test 2: Spread-tiered scaling ──
print("\n" + "=" * 80)
print("  SPREAD-TIERED SCALING ANALYSIS — No Upset Clause")
print("=" * 80)

# Find best OC/UC for each spread tier separately
tier_ranges = {
    "narrow": (0, 3.5),
    "medium": (4.0, 7.0),
    "wide": (7.5, 20.0),
}

for tier_name, (min_s, max_s) in tier_ranges.items():
    tier_games = [g for g in all_games if min_s <= abs(g["spread"]) <= max_s]
    print(f"\n  {tier_name.upper()} spreads ({min_s}-{max_s}): {len(tier_games)} games")
    print(f"  {'OC':>6} {'UC':>6} {'HITs':>6} {'MISSes':>6} {'Active':>6} {'WinRate':>8}")
    print(f"  {'─'*6} {'─'*6} {'─'*6} {'─'*6} {'─'*6} {'─'*8}")

    tier_best = 0
    tier_best_params = None
    for oc in [0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        for uc in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
            r = backtest(tier_games, oc, uc, use_upset_clause=False)
            if r["win_rate"] > tier_best and r["active"] >= 5:
                tier_best = r["win_rate"]
                tier_best_params = (oc, uc, r)
            if r["win_rate"] >= 90.0:
                print(f"  {oc:>6.2f} {uc:>6.2f} {r['hits']:>6} {r['misses']:>6} {r['active']:>6} {r['win_rate']:>7.1f}%")

    if tier_best_params:
        print(f"  🏆 {tier_name.upper()} BEST: OC={tier_best_params[0]}, UC={tier_best_params[1]} → {tier_best_params[2]['hits']}H/{tier_best_params[2]['misses']}M = {tier_best_params[2]['win_rate']}%")

# ── Test 3: Best spread-tiered combination ──
print("\n" + "=" * 80)
print("  COMBINED SPREAD-TIERED ANALYSIS")
print("=" * 80)

# Try various tier combinations
tier_configs = [
    {
        "name": "A: OC=0.65/0.60/0.55 UC=0.60/0.55/0.50",
        "tiers": {"narrow": (0, 3.5, 0.65, 0.60), "medium": (4.0, 7.0, 0.60, 0.55), "wide": (7.5, 20.0, 0.55, 0.50)},
    },
    {
        "name": "B: OC=0.75/0.65/0.55 UC=0.70/0.60/0.50",
        "tiers": {"narrow": (0, 3.5, 0.75, 0.70), "medium": (4.0, 7.0, 0.65, 0.60), "wide": (7.5, 20.0, 0.55, 0.50)},
    },
    {
        "name": "C: OC=0.70/0.65/0.55 UC=0.65/0.60/0.50",
        "tiers": {"narrow": (0, 3.5, 0.70, 0.65), "medium": (4.0, 7.0, 0.65, 0.60), "wide": (7.5, 20.0, 0.55, 0.50)},
    },
    {
        "name": "D: OC=0.80/0.65/0.50 UC=0.75/0.60/0.50",
        "tiers": {"narrow": (0, 3.5, 0.80, 0.75), "medium": (4.0, 7.0, 0.65, 0.60), "wide": (7.5, 20.0, 0.50, 0.50)},
    },
    {
        "name": "E: OC=0.65/0.65/0.65 UC=0.60/0.60/0.60 (uniform)",
        "tiers": None,  # uniform
    },
    {
        "name": "F: OC=0.70/0.65/0.60 UC=0.65/0.60/0.55",
        "tiers": {"narrow": (0, 3.5, 0.70, 0.65), "medium": (4.0, 7.0, 0.65, 0.60), "wide": (7.5, 20.0, 0.60, 0.55)},
    },
    {
        "name": "G: OC=0.75/0.70/0.55 UC=0.70/0.65/0.50",
        "tiers": {"narrow": (0, 3.5, 0.75, 0.70), "medium": (4.0, 7.0, 0.70, 0.65), "wide": (7.5, 20.0, 0.55, 0.50)},
    },
    {
        "name": "H: OC=0.85/0.70/0.55 UC=0.80/0.65/0.50",
        "tiers": {"narrow": (0, 3.5, 0.85, 0.80), "medium": (4.0, 7.0, 0.70, 0.65), "wide": (7.5, 20.0, 0.55, 0.50)},
    },
]

for config in tier_configs:
    if config["tiers"] is None:
        r = backtest(all_games, 0.65, 0.60, use_upset_clause=False)
    else:
        r = backtest(all_games, 0.65, 0.60, use_upset_clause=False, spread_tiers=config["tiers"])
    print(f"  {config['name']}: {r['hits']}H/{r['misses']}M/{r['skips']}S = {r['win_rate']}%")

# ── Test 4: V11 baseline comparison ──
print("\n" + "=" * 80)
print("  BASELINE COMPARISON")
print("=" * 80)
v11 = backtest(all_games, 0.45, 0.40, use_upset_clause=True)
v11_no_upset = backtest(all_games, 0.45, 0.40, use_upset_clause=False)
v12_uniform = backtest(all_games, 0.65, 0.60, use_upset_clause=False)

print(f"  V11 (OC=0.45 UC=0.40 + upset clause): {v11['hits']}H/{v11['misses']}M/{v11['skips']}S = {v11['win_rate']}%")
print(f"  V11 (OC=0.45 UC=0.40 NO upset clause): {v11_no_upset['hits']}H/{v11_no_upset['misses']}M/{v11_no_upset['skips']}S = {v11_no_upset['win_rate']}%")
print(f"  V12 (OC=0.65 UC=0.60 NO upset clause): {v12_uniform['hits']}H/{v12_uniform['misses']}M/{v12_uniform['skips']}S = {v12_uniform['win_rate']}%")

# ── Test 5: Per-league breakdown ──
print("\n" + "=" * 80)
print("  LEAGUE BREAKDOWN — V12 (OC=0.65 UC=0.60)")
print("=" * 80)
wnba_games = [g for g in all_games if g["league"] == "WNBA"]
nba_games = [g for g in all_games if g["league"] == "NBA"]

for league, games in [("WNBA", wnba_games), ("NBA", nba_games)]:
    v11_r = backtest(games, 0.45, 0.40, use_upset_clause=True)
    v12_r = backtest(games, 0.65, 0.60, use_upset_clause=False)
    print(f"  {league} V11: {v11_r['hits']}H/{v11_r['misses']}M/{v11_r['skips']}S = {v11_r['win_rate']}%")
    print(f"  {league} V12: {v12_r['hits']}H/{v12_r['misses']}M/{v12_r['skips']}S = {v12_r['win_rate']}%")

# ── Test 6: Detailed MISS analysis ──
print("\n" + "=" * 80)
print("  DETAILED MISS ANALYSIS — V12 (OC=0.65 UC=0.60)")
print("=" * 80)

for g in all_games:
    total = g["total"]
    spread = abs(g["spread"])
    pick = g["pick"]
    underdog_score = g["underdog_score"]
    base_line = (total / 2) - (spread / 2)

    if pick == "OVER":
        scaled_line = base_line - (0.65 * spread)
        is_hit = underdog_score > scaled_line
        margin = underdog_score - scaled_line
    else:
        scaled_line = base_line + (0.60 * spread)
        is_hit = underdog_score < scaled_line
        margin = scaled_line - underdog_score

    if not is_hit:
        print(f"  MISS: {g['matchup']:<18} {pick:<7} spread={spread:>5.1f} scaled={scaled_line:>8.3f} score={underdog_score:>4} margin={margin:>7.3f} league={g['league']}")
