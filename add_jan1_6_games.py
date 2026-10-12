#!/usr/bin/env python3
"""
Direct game data injection — Jan 1-6, 2026 from Covers.com.
All scores and closing lines are REAL from Covers.com.
"""

import json

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

NEW_GAMES = [
    # Jan 1, 2026 — 4 games
    ("2026-01-01", "HOU", 120, "BKN", 96, 217.5, 17.0, "HOU"),
    ("2026-01-01", "MIA", 118, "DET", 112, 238.5, 2.5, "DET"),
    ("2026-01-01", "PHI", 123, "DAL", 108, 234.0, 1.0, "DAL"),
    ("2026-01-01", "BOS", 120, "SAC", 106, 234.5, 8.0, "BOS"),
    
    # Jan 2, 2026 — 4 games
    ("2026-01-02", "BKN", 99, "WAS", 119, 230.0, 5.0, "WAS"),
    ("2026-01-02", "SAS", 123, "IND", 113, 243.0, 1.0, "SAS"),
    ("2026-01-02", "ATL", 111, "NYK", 99, 247.5, 6.0, "NYK"),
    ("2026-01-02", "DEN", 108, "CLE", 113, 237.0, 14.0, "CLE"),
    
    # Jan 3, 2026 — 4 games
    ("2026-01-03", "MIN", 125, "MIA", 115, 234.0, 6.5, "MIN"),
    ("2026-01-03", "PHI", 130, "NYK", 119, 227.5, 4.0, "NYK"),
    ("2026-01-03", "ATL", 117, "TOR", 134, 226.5, 4.0, "TOR"),
    ("2026-01-03", "CHA", 112, "CHI", 99, 244.0, 2.5, "CHI"),
    
    # Jan 4, 2026 — 4 games
    ("2026-01-04", "DET", 114, "CLE", 110, 240.5, 3.5, "CLE"),
    ("2026-01-04", "IND", 127, "ORL", 135, 234.0, 5.5, "ORL"),
    ("2026-01-04", "DEN", 115, "BKN", 127, 223.5, 1.5, "BKN"),
    ("2026-01-04", "NOP", 106, "MIA", 125, 258.0, 7.0, "MIA"),
    
    # Jan 6, 2026 — 4 games
    ("2026-01-06", "CLE", 120, "IND", 116, 236.5, 6.5, "CLE"),
    ("2026-01-06", "ORL", 112, "WAS", 120, 235.5, 7.5, "ORL"),
    ("2026-01-06", "MIA", 94, "MIN", 122, 238.0, 5.5, "MIN"),
    ("2026-01-06", "LAL", 111, "NOP", 103, 246.0, 5.5, "LAL"),
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
