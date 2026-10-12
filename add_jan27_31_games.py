#!/usr/bin/env python3
"""Add NBA games from Jan 27-31, 2026 with real closing lines from Covers.com"""
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
    # Jan 27, 2026 - 4 games (chunk 0)
    {"date": "2026-01-27", "away": "POR", "away_score": 111, "home": "WAS", "home_score": 115, "market_total": 232.5, "market_spread": 7.0, "favorite": "POR"},
    {"date": "2026-01-27", "away": "SAC", "away_score": 87, "home": "NYK", "home_score": 103, "market_total": 225.0, "market_spread": 14.5, "favorite": "NYK"},
    {"date": "2026-01-27", "away": "NOP", "away_score": 95, "home": "OKC", "home_score": 104, "market_total": 233.0, "market_spread": 14.5, "favorite": "OKC"},
    {"date": "2026-01-27", "away": "MIL", "away_score": 122, "home": "PHI", "home_score": 139, "market_total": 219.5, "market_spread": 10.0, "favorite": "PHI"},
    
    # Jan 28, 2026 - 4 games (chunk 0)
    {"date": "2026-01-28", "away": "LAL", "away_score": 99, "home": "CLE", "home_score": 129, "market_total": 233.5, "market_spread": 4.0, "favorite": "CLE"},
    {"date": "2026-01-28", "away": "CHI", "away_score": 110, "home": "IND", "home_score": 113, "market_total": 236.0, "market_spread": 2.0, "favorite": "CHI"},
    {"date": "2026-01-28", "away": "ORL", "away_score": 133, "home": "MIA", "home_score": 124, "market_total": 232.5, "market_spread": 3.0, "favorite": "MIA"},
    {"date": "2026-01-28", "away": "NYK", "away_score": 119, "home": "TOR", "home_score": 92, "market_total": 220.5, "market_spread": 2.0, "favorite": "TOR"},
    
    # Jan 29, 2026 - 4 games (chunk 0)
    {"date": "2026-01-29", "away": "MIL", "away_score": 99, "home": "WAS", "home_score": 109, "market_total": 223.5, "market_spread": 2.0, "favorite": "MIL"},
    {"date": "2026-01-29", "away": "SAC", "away_score": 111, "home": "PHI", "home_score": 113, "market_total": 229.0, "market_spread": 10.0, "favorite": "PHI"},
    {"date": "2026-01-29", "away": "HOU", "away_score": 104, "home": "ATL", "home_score": 86, "market_total": 225.0, "market_spread": 6.5, "favorite": "HOU"},
    {"date": "2026-01-29", "away": "MIA", "away_score": 116, "home": "CHI", "home_score": 113, "market_total": 238.0, "market_spread": 2.0, "favorite": "MIA"},
    
    # Jan 30, 2026 - 4 games (chunk 0)
    {"date": "2026-01-30", "away": "LAL", "away_score": 142, "home": "WAS", "home_score": 111, "market_total": 230.0, "market_spread": 10.5, "favorite": "LAL"},
    {"date": "2026-01-30", "away": "MEM", "away_score": 106, "home": "NOP", "home_score": 114, "market_total": 231.0, "market_spread": 3.5, "favorite": "NOP"},
    {"date": "2026-01-30", "away": "POR", "away_score": 97, "home": "NYK", "home_score": 127, "market_total": 224.0, "market_spread": 6.5, "favorite": "NYK"},
    {"date": "2026-01-30", "away": "SAC", "away_score": 93, "home": "BOS", "home_score": 112, "market_total": 216.5, "market_spread": 12.0, "favorite": "BOS"},
    
    # Jan 31, 2026 - 4 games (chunk 0)
    {"date": "2026-01-31", "away": "SAS", "away_score": 106, "home": "CHA", "home_score": 111, "market_total": 218.5, "market_spread": 4.0, "favorite": "CHA"},
    {"date": "2026-01-31", "away": "ATL", "away_score": 124, "home": "IND", "home_score": 129, "market_total": 235.0, "market_spread": 1.5, "favorite": "ATL"},
    {"date": "2026-01-31", "away": "NOP", "away_score": 114, "home": "PHI", "home_score": 124, "market_total": 235.0, "market_spread": 6.5, "favorite": "PHI"},
    {"date": "2026-01-31", "away": "MIN", "away_score": 131, "home": "MEM", "home_score": 114, "market_total": 229.5, "market_spread": 11.0, "favorite": "MIN"},
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
