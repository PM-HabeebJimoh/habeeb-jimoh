#!/usr/bin/env python3
"""
Direct game data injection — manually extracted from Covers.com pages.
All scores and closing lines are REAL from Covers.com.
"""

import json
import os

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

# Games extracted from Covers.com pages (Dec 2-7, 2025)
# Format: (date, away, away_score, home, home_score, market_total, market_spread, favorite)
NEW_GAMES = [
    # Dec 2, 2025 — 6 games
    ("2025-12-02", "WAS", 102, "PHI", 121, 235.5, 13.0, "PHI"),
    ("2025-12-02", "POR", 118, "TOR", 121, 231.5, 5.0, "TOR"),
    ("2025-12-02", "MIN", 149, "NOP", 142, 229.5, 12.5, "MIN"),
    ("2025-12-02", "NYK", 117, "BOS", 123, 231.0, 1.0, "BOS"),
    ("2025-12-02", "MEM", 119, "SAS", 126, 232.5, 5.0, "SAS"),
    ("2025-12-02", "OKC", 124, "GSW", 112, 223.5, 11.0, "OKC"),
    
    # Dec 3, 2025 — 9 games
    ("2025-12-03", "DEN", 135, "IND", 120, 237.5, 8.0, "DEN"),
    ("2025-12-03", "POR", 122, "CLE", 110, 245.0, 10.0, "CLE"),
    ("2025-12-03", "SAS", 114, "ORL", 112, 236.0, 8.0, "ORL"),
    ("2025-12-03", "CHA", 104, "NYK", 119, 235.5, 9.0, "NYK"),
    ("2025-12-03", "LAC", 115, "ATL", 92, 225.5, 2.0, "ATL"),
    ("2025-12-03", "SAC", 95, "HOU", 121, 231.0, 15.5, "HOU"),
    ("2025-12-03", "BKN", 113, "CHI", 103, 231.0, 8.0, "CHI"),
    ("2025-12-03", "DET", 109, "MIL", 113, 228.0, 4.5, "MIL"),
    ("2025-12-03", "MIA", 108, "DAL", 118, 239.0, 4.5, "DAL"),
    
    # Dec 4, 2025 — 4 games
    ("2025-12-04", "BOS", 146, "WAS", 101, 232.0, 11.0, "BOS"),
    ("2025-12-04", "GSW", 98, "PHI", 99, 223.5, 4.0, "PHI"),
    ("2025-12-04", "LAL", 123, "TOR", 120, 228.5, 2.0, "TOR"),
    ("2025-12-04", "UTA", 123, "BKN", 110, 231.0, 5.0, "UTA"),
    
    # Dec 6, 2025 — 7 games
    ("2025-12-06", "NOP", 101, "BKN", 119, 227.5, 4.0, "BKN"),
    ("2025-12-06", "ATL", 131, "WAS", 116, 237.5, 9.5, "ATL"),
    ("2025-12-06", "MIL", 112, "DET", 124, 223.5, 12.5, "DET"),
    ("2025-12-06", "GSW", 99, "CLE", 94, 230.5, 9.5, "CLE"),
    ("2025-12-06", "SAC", 127, "MIA", 111, 241.5, 8.5, "MIA"),
    ("2025-12-06", "LAC", 106, "MIN", 109, 228.0, 8.0, "MIN"),
    ("2025-12-06", "HOU", 109, "DAL", 122, 221.5, 6.5, "DAL"),
    
    # Dec 7, 2025 — 7 games
    ("2025-12-07", "ORL", 100, "NYK", 106, 229.5, 1.0, "NYK"),
    ("2025-12-07", "BOS", 121, "TOR", 113, 224.5, 3.5, "BOS"),
    ("2025-12-07", "DEN", 115, "CHA", 106, 235.5, 10.5, "DEN"),
    ("2025-12-07", "POR", 96, "MEM", 119, 232.5, 2.0, "MEM"),
    ("2025-12-07", "GSW", 123, "CHI", 91, 229.5, 1.0, "GSW"),
    ("2025-12-07", "LAL", 112, "PHI", 108, 234.0, 2.5, "LAL"),
    ("2025-12-07", "OKC", 131, "UTA", 101, 234.0, 11.5, "OKC"),
]


def add_games():
    """Add new games to the dataset."""
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    # Get existing game keys
    existing_keys = set()
    for g in data['nba']:
        key = f"{g['date']}_{g['away']}_{g['home']}"
        existing_keys.add(key)
    
    added = 0
    duplicates = 0
    
    for date, away, away_score, home, home_score, total, spread, favorite in NEW_GAMES:
        key = f"{date}_{away}_{home}"
        if key in existing_keys:
            duplicates += 1
            continue
        
        game = {
            "date": date,
            "away": away,
            "away_score": away_score,
            "home": home,
            "home_score": home_score,
            "market_total": total,
            "market_spread": spread,
            "favorite": favorite,
        }
        data['nba'].append(game)
        existing_keys.add(key)
        added += 1
    
    # Update metadata
    data['metadata']['nba_count'] = len(data['nba'])
    data['metadata']['total_count'] = len(data['nba']) + len(data['wnba'])
    data['metadata']['nba_coverage_pct'] = round(len(data['nba']) / 1230 * 100, 1)
    data['metadata']['total_coverage_pct'] = round(
        (len(data['nba']) + len(data['wnba'])) / 1447 * 100, 1
    )
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added {added} new games ({duplicates} duplicates skipped)")
    print(f"📊 NBA: {len(data['nba'])}/1,230 ({len(data['nba'])/1230*100:.1f}%)")
    print(f"📊 Total: {len(data['nba']) + len(data['wnba'])}/1,447 ({(len(data['nba']) + len(data['wnba']))/1447*100:.1f}%)")


if __name__ == "__main__":
    add_games()
