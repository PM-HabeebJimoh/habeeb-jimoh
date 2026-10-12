#!/usr/bin/env python3
"""
Direct game data injection — Dec 14-19, 2025 from Covers.com.
All scores and closing lines are REAL from Covers.com.
"""

import json

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

NEW_GAMES = [
    # Dec 14, 2025 — 8 games
    ("2025-12-14", "WAS", 108, "IND", 89, 233.5, 10.0, "IND"),
    ("2025-12-14", "CHA", 119, "CLE", 111, 233.0, 12.5, "CLE"),
    ("2025-12-14", "PHI", 117, "ATL", 120, 226.0, 4.5, "ATL"),
    ("2025-12-14", "MIL", 82, "BKN", 127, 216.0, 1.0, "MIL"),
    ("2025-12-14", "NOP", 114, "CHI", 104, 247.5, 4.5, "CHI"),
    ("2025-12-14", "SAC", 103, "MIN", 117, 235.5, 10.0, "MIN"),
    ("2025-12-14", "LAL", 116, "PHX", 114, 232.0, 1.5, "PHX"),
    ("2025-12-14", "GSW", 131, "POR", 136, 238.0, 5.0, "POR"),
    
    # Dec 16, 2025 — 1 game (NBA Cup)
    ("2025-12-16", "SAS", 113, "NYK", 124, 233.0, 2.5, "NYK"),
    
    # Dec 17, 2025 — 2 games
    ("2025-12-17", "MEM", 116, "MIN", 110, 227.0, 6.5, "MIN"),
    ("2025-12-17", "CLE", 111, "CHI", 127, 243.5, 5.5, "CLE"),
    
    # Dec 18, 2025 — 10 games
    ("2025-12-18", "NYK", 114, "IND", 113, 225.0, 2.5, "NYK"),
    ("2025-12-18", "ATL", 126, "CHA", 133, 246.0, 2.5, "CHA"),
    ("2025-12-18", "MIA", 106, "BKN", 95, 236.0, 11.5, "MIA"),
    ("2025-12-18", "HOU", 128, "NOP", 133, 236.0, 9.5, "HOU"),
    ("2025-12-18", "TOR", 111, "MIL", 105, 218.0, 4.5, "TOR"),
    ("2025-12-18", "WAS", 94, "SAS", 119, 241.0, 16.0, "SAS"),
    ("2025-12-18", "LAC", 101, "OKC", 122, 222.5, 17.0, "OKC"),
    ("2025-12-18", "DET", 114, "DAL", 116, 233.0, 1.5, "DAL"),
    ("2025-12-18", "ORL", 115, "DEN", 126, 238.0, 4.5, "DEN"),
    ("2025-12-18", "LAL", 143, "UTA", 135, 249.5, 7.0, "LAL"),
    # GS 98 @ PHX 99 — PHX +2, Total: 231
    ("2025-12-18", "GSW", 98, "PHX", 99, 231.0, 2.0, "PHX"),
    
    # Dec 19, 2025 — 5 games
    ("2025-12-19", "MIA", 116, "BOS", 129, 234.0, 8.0, "BOS"),
    ("2025-12-19", "PHI", 116, "NYK", 107, 233.5, 3.5, "NYK"),
    ("2025-12-19", "CHI", 136, "CLE", 125, 240.0, 8.0, "CLE"),
    ("2025-12-19", "SAS", 126, "ATL", 98, 238.5, 6.0, "SAS"),
    ("2025-12-19", "OKC", 107, "MIN", 112, 231.0, 7.0, "OKC"),
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
