#!/usr/bin/env python3
"""Add NBA games from Feb 2-6, 2026 with real closing lines from Covers.com"""
import json

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_games(data, new_games):
    existing = set()
    for g in data['nba']:
        key = f"{g['date']}_{g['away']}_{g['home']}"
        existing.add(key)
    added = 0
    for g in new_games:
        key = f"{g['date']}_{g['away']}_{g['home']}"
        if key not in existing:
            data['nba'].append(g)
            existing.add(key)
            added += 1
    return added

new_games = [
    # Feb 2, 2026 - 4 games (chunk 0)
    {"date": "2026-02-02", "away": "NOP", "away_score": 95, "home": "CHA", "home_score": 102, "market_total": 230.0, "market_spread": 6.5, "favorite": "CHA"},
    {"date": "2026-02-02", "away": "HOU", "away_score": 118, "home": "IND", "home_score": 114, "market_total": 218.5, "market_spread": 6.5, "favorite": "HOU"},
    {"date": "2026-02-02", "away": "MIN", "away_score": 128, "home": "MEM", "home_score": 137, "market_total": 232.0, "market_spread": 7.5, "favorite": "MEM"},
    {"date": "2026-02-02", "away": "PHI", "away_score": 128, "home": "LAC", "home_score": 113, "market_total": 220.0, "market_spread": 1.0, "favorite": "PHI"},
    
    # Feb 3, 2026 - 4 games (chunk 0)
    {"date": "2026-02-03", "away": "NYK", "away_score": 132, "home": "WAS", "home_score": 101, "market_total": 228.0, "market_spread": 13.0, "favorite": "NYK"},
    {"date": "2026-02-03", "away": "UTA", "away_score": 131, "home": "IND", "home_score": 122, "market_total": 232.5, "market_spread": 2.5, "favorite": "UTA"},
    {"date": "2026-02-03", "away": "DEN", "away_score": 121, "home": "DET", "home_score": 124, "market_total": 229.5, "market_spread": 5.0, "favorite": "DET"},
    {"date": "2026-02-03", "away": "ATL", "away_score": 127, "home": "MIA", "home_score": 115, "market_total": 236.5, "market_spread": 1.0, "favorite": "MIA"},
    
    # Feb 4, 2026 - 4 games (chunk 0)
    {"date": "2026-02-04", "away": "DEN", "away_score": 127, "home": "NYK", "home_score": 134, "market_total": 228.0, "market_spread": 4.5, "favorite": "NYK"},
    {"date": "2026-02-04", "away": "MIN", "away_score": 128, "home": "TOR", "home_score": 126, "market_total": 228.5, "market_spread": 2.0, "favorite": "MIN"},
    {"date": "2026-02-04", "away": "NOP", "away_score": 137, "home": "MIL", "home_score": 141, "market_total": 223.5, "market_spread": 4.5, "favorite": "MIL"},
    {"date": "2026-02-04", "away": "BOS", "away_score": 114, "home": "HOU", "home_score": 93, "market_total": 210.5, "market_spread": 8.0, "favorite": "HOU"},
    
    # Feb 5, 2026 - 4 games (chunk 0)
    {"date": "2026-02-05", "away": "BKN", "away_score": 98, "home": "ORL", "home_score": 118, "market_total": 215.0, "market_spread": 9.5, "favorite": "ORL"},
    {"date": "2026-02-05", "away": "WAS", "away_score": 126, "home": "DET", "home_score": 117, "market_total": 228.0, "market_spread": 17.0, "favorite": "DET"},
    {"date": "2026-02-05", "away": "CHI", "away_score": 107, "home": "TOR", "home_score": 123, "market_total": 227.0, "market_spread": 7.5, "favorite": "TOR"},
    {"date": "2026-02-05", "away": "UTA", "away_score": 119, "home": "ATL", "home_score": 121, "market_total": 245.5, "market_spread": 8.5, "favorite": "ATL"},
    
    # Feb 6, 2026 - 4 games (chunk 0)
    {"date": "2026-02-06", "away": "NYK", "away_score": 80, "home": "DET", "home_score": 118, "market_total": 219.5, "market_spread": 5.5, "favorite": "DET"},
    {"date": "2026-02-06", "away": "MIA", "away_score": 96, "home": "BOS", "home_score": 98, "market_total": 227.5, "market_spread": 5.5, "favorite": "BOS"},
    {"date": "2026-02-06", "away": "IND", "away_score": 99, "home": "MIL", "home_score": 105, "market_total": 224.0, "market_spread": 1.5, "favorite": "MIL"},
    {"date": "2026-02-06", "away": "NOP", "away_score": 119, "home": "MIN", "home_score": 115, "market_total": 237.0, "market_spread": 8.5, "favorite": "MIN"},
]

def main():
    data = load_data()
    before = len(data['nba'])
    added = add_games(data, new_games)
    after = len(data['nba'])
    data['nba'].sort(key=lambda g: (g['date'], g['away']))
    save_data(data)
    print(f"Added {added} new NBA games ({before} → {after})")
    print(f"Total NBA games: {after}")

if __name__ == "__main__":
    main()
