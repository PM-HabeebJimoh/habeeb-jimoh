#!/usr/bin/env python3
"""
Direct game data injection — Dec 27-31, 2025 from Covers.com.
All scores and closing lines are REAL from Covers.com.
"""

import json

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

NEW_GAMES = [
    # Dec 28, 2025 — 4 games (first chunk)
    ("2025-12-28", "PHI", 104, "OKC", 129, 230.5, 17.5, "OKC"),
    ("2025-12-28", "GSW", 127, "TOR", 141, 233.0, 6.0, "TOR"),
    ("2025-12-28", "MEM", 112, "WAS", 116, 244.5, 8.0, "WAS"),
    ("2025-12-28", "BOS", 108, "POR", 114, 231.5, 9.5, "POR"),
    
    # Dec 29, 2025 — 4 games (first chunk)
    ("2025-12-29", "PHX", 115, "WAS", 101, 230.0, 11.0, "PHX"),
    ("2025-12-29", "MIL", 123, "CHA", 113, 226.5, 4.0, "MIL"),
    ("2025-12-29", "ORL", 106, "TOR", 107, 216.5, 6.0, "TOR"),
    ("2025-12-29", "DEN", 123, "MIA", 147, 245.0, 1.5, "MIA"),
    
    # Dec 30, 2025 — no games (Covers page returned error)
    
    # Dec 31, 2025 — 5 games (first chunk)
    ("2025-12-31", "GSW", 132, "CHA", 125, 239.0, 8.0, "CHA"),
    ("2025-12-31", "MIN", 102, "ATL", 126, 247.5, 3.0, "ATL"),
    ("2025-12-31", "ORL", 112, "IND", 110, 228.5, 7.0, "IND"),
    ("2025-12-31", "PHX", 113, "CLE", 129, 237.5, 11.0, "CLE"),
    ("2025-12-31", "NYK", 132, "SAS", 0, 0.0, 0.0, "SAS"),  # incomplete - skip
]


def add_games():
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    existing_keys = set()
    for g in data['nba']:
        key = f"{g['date']}_{g['away']}_{g['home']}"
        existing_keys.add(key)
    
    added = 0
    skipped = 0
    for date, away, away_score, home, home_score, total, spread, favorite in NEW_GAMES:
        # Skip incomplete games
        if total == 0.0 or home_score == 0:
            skipped += 1
            continue
        key = f"{date}_{away}_{home}"
        if key in existing_keys:
            continue
        game = {
            "date": date, "away": away, "away_score": away_score,
            "home": home, "home_score": home_score,
            "market_total": total, "market_spread": spread, "favorite": favorite,
        }
        data['nba'].append(game)
        existing_keys.add(key)
        added += 1
    
    data['metadata']['nba_count'] = len(data['nba'])
    data['metadata']['total_count'] = len(data['nba']) + len(data['wnba'])
    data['metadata']['nba_coverage_pct'] = round(len(data['nba']) / 1230 * 100, 1)
    data['metadata']['total_coverage_pct'] = round(
        (len(data['nba']) + len(data['wnba'])) / 1447 * 100, 1
    )
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added {added} new games ({skipped} skipped due to incomplete data)")
    print(f"📊 NBA: {len(data['nba'])}/1,230 ({len(data['nba'])/1230*100:.1f}%)")
    print(f"📊 Total: {len(data['nba']) + len(data['wnba'])}/1,447 ({(len(data['nba']) + len(data['wnba']))/1447*100:.1f}%)")


if __name__ == "__main__":
    add_games()
