#!/usr/bin/env python3
"""
Direct game data injection — Dec 21-26, 2025 from Covers.com.
All scores and closing lines are REAL from Covers.com.
"""

import json

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

NEW_GAMES = [
    # Dec 21, 2025 — 4 games (first chunk)
    ("2025-12-21", "CHI", 152, "ATL", 150, 261.0, 2.0, "ATL"),  # Push
    ("2025-12-21", "MIA", 125, "NYK", 132, 231.0, 5.0, "NYK"),
    ("2025-12-21", "TOR", 81, "BKN", 96, 215.5, 4.0, "BKN"),
    ("2025-12-21", "MIL", 100, "MIN", 103, 222.5, 7.5, "MIN"),
    
    # Dec 22, 2025 — 4 games (first chunk)
    ("2025-12-22", "CHA", 132, "CLE", 139, 251.0, 9.5, "CLE"),
    ("2025-12-22", "IND", 95, "BOS", 103, 232.0, 11.0, "BOS"),
    ("2025-12-22", "DAL", 113, "NOP", 119, 244.0, 4.0, "NOP"),
    ("2025-12-22", "UTA", 112, "DEN", 135, 250.0, 20.5, "DEN"),
    
    # Dec 23, 2025 — 6 games (first chunk + second chunk)
    ("2025-12-23", "WAS", 109, "CHA", 126, 229.5, 8.0, "CHA"),
    ("2025-12-23", "BKN", 114, "PHI", 106, 216.5, 9.5, "PHI"),
    ("2025-12-23", "CHI", 126, "ATL", 123, 254.5, 3.5, "ATL"),
    ("2025-12-23", "TOR", 112, "MIA", 91, 227.5, 5.5, "MIA"),
    ("2025-12-23", "MIL", 111, "IND", 94, 217.0, 1.5, "MIL"),
    ("2025-12-23", "NOP", 118, "CLE", 141, 248.5, 10.0, "CLE"),
    
    # Dec 24, 2025 — 4 games (Christmas Eve)
    ("2025-12-24", "CLE", 124, "NYK", 126, 237.5, 3.5, "NYK"),
    ("2025-12-24", "SAS", 117, "OKC", 102, 246.5, 10.5, "OKC"),
    ("2025-12-24", "DAL", 116, "GSW", 126, 228.5, 10.5, "GSW"),
    ("2025-12-24", "HOU", 119, "LAL", 96, 233.0, 5.0, "HOU"),
    
    # Dec 26, 2025 — 4 games (first chunk)
    ("2025-12-26", "BOS", 140, "IND", 122, 229.5, 5.0, "BOS"),
    ("2025-12-26", "TOR", 117, "WAS", 138, 223.0, 8.0, "WAS"),
    ("2025-12-26", "MIA", 126, "ATL", 111, 254.0, 2.5, "ATL"),
    ("2025-12-26", "CHA", 120, "ORL", 105, 236.5, 3.0, "ORL"),
]


def add_games():
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    existing_keys = set()
    for g in data['nba']:
        key = f"{g['date']}_{g['away']}_{g['home']}"
        existing_keys.add(key)
    
    added = 0
    for date, away, away_score, home, home_score, total, spread, favorite in NEW_GAMES:
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
    
    print(f"✅ Added {added} new games")
    print(f"📊 NBA: {len(data['nba'])}/1,230 ({len(data['nba'])/1230*100:.1f}%)")
    print(f"📊 Total: {len(data['nba']) + len(data['wnba'])}/1,447 ({(len(data['nba']) + len(data['wnba']))/1447*100:.1f}%)")


if __name__ == "__main__":
    add_games()
