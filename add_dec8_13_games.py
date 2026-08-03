#!/usr/bin/env python3
"""
Direct game data injection — Dec 8-13, 2025 from Covers.com.
All scores and closing lines are REAL from Covers.com.
"""

import json

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

NEW_GAMES = [
    # Dec 8, 2025 — 3 games
    ("2025-12-08", "SAC", 105, "IND", 116, 232.0, 4.0, "IND"),
    ("2025-12-08", "PHX", 108, "MIN", 105, 225.5, 8.0, "MIN"),
    ("2025-12-08", "SAS", 135, "NOP", 132, 238.5, 8.0, "SAS"),
    
    # Dec 9, 2025 — 2 games (NBA Cup)
    ("2025-12-09", "MIA", 108, "ORL", 117, 235.0, 1.5, "ORL"),
    ("2025-12-09", "NYK", 117, "TOR", 101, 226.5, 6.0, "NYK"),
    
    # Dec 11, 2025 — 4 games
    ("2025-12-11", "POR", 120, "NOP", 143, 242.5, 4.0, "NOP"),
    ("2025-12-11", "BOS", 101, "MIL", 116, 222.5, 9.5, "BOS"),
    ("2025-12-11", "LAC", 113, "HOU", 115, 221.5, 9.0, "HOU"),
    ("2025-12-11", "DEN", 136, "SAC", 105, 240.0, 10.5, "DEN"),
    
    # Dec 12, 2025 — 7 games
    ("2025-12-12", "IND", 105, "PHI", 115, 221.0, 5.0, "PHI"),
    ("2025-12-12", "CHI", 129, "CHA", 126, 229.5, 2.5, "CHI"),
    ("2025-12-12", "ATL", 115, "DET", 142, 233.0, 7.0, "DET"),
    ("2025-12-12", "CLE", 130, "WAS", 126, 246.0, 17.0, "CLE"),
    ("2025-12-12", "UTA", 130, "MEM", 126, 244.0, 7.5, "MEM"),
    ("2025-12-12", "BKN", 111, "DAL", 119, 219.0, 7.5, "DAL"),
    ("2025-12-12", "MIN", 127, "GSW", 120, 229.0, 5.0, "GSW"),
    
    # Dec 13, 2025 — 2 games (NBA Cup)
    ("2025-12-13", "NYK", 132, "ORL", 120, 225.0, 4.0, "NYK"),
    ("2025-12-13", "SAS", 111, "OKC", 109, 234.0, 10.0, "OKC"),
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
