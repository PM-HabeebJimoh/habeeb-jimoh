#!/usr/bin/env python3
"""Add NBA games from Jan 22-26, 2026 with real closing lines from Covers.com"""
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
    # Jan 22, 2026 - chunk 1 (4 more games)
    {"date": "2026-01-22", "away": "CHI", "away_score": 120, "home": "MIN", "home_score": 115, "market_total": 240.0, "market_spread": 9.0, "favorite": "MIN"},
    {"date": "2026-01-22", "away": "SAS", "away_score": 126, "home": "UTA", "home_score": 109, "market_total": 239.5, "market_spread": 12.0, "favorite": "SAS"},
    {"date": "2026-01-22", "away": "LAL", "away_score": 104, "home": "LAC", "home_score": 112, "market_total": 224.5, "market_spread": 2.5, "favorite": "LAC"},
    {"date": "2026-01-22", "away": "MIA", "away_score": 110, "home": "POR", "home_score": 127, "market_total": 235.0, "market_spread": 3.0, "favorite": "POR"},
    
    # Jan 23, 2026 - 6 games
    {"date": "2026-01-23", "away": "HOU", "away_score": 111, "home": "DET", "home_score": 104, "market_total": 217.0, "market_spread": 4.0, "favorite": "DET"},
    {"date": "2026-01-23", "away": "BOS", "away_score": 130, "home": "BKN", "home_score": 126, "market_total": 215.0, "market_spread": 8.0, "favorite": "BOS"},
    {"date": "2026-01-23", "away": "PHX", "away_score": 103, "home": "ATL", "home_score": 110, "market_total": 234.0, "market_spread": 2.5, "favorite": "PHX"},
    {"date": "2026-01-23", "away": "SAC", "away_score": 118, "home": "CLE", "home_score": 123, "market_total": 233.0, "market_spread": 13.0, "favorite": "CLE"},
    {"date": "2026-01-23", "away": "IND", "away_score": 117, "home": "OKC", "home_score": 114, "market_total": 226.5, "market_spread": 15.5, "favorite": "OKC"},
    {"date": "2026-01-23", "away": "NOP", "away_score": 133, "home": "MEM", "home_score": 127, "market_total": 240.0, "market_spread": 5.0, "favorite": "MEM"},
    
    # Jan 24, 2026 - 4 games (chunk 0)
    {"date": "2026-01-24", "away": "WAS", "away_score": 115, "home": "CHA", "home_score": 119, "market_total": 232.5, "market_spread": 11.5, "favorite": "CHA"},
    {"date": "2026-01-24", "away": "NYK", "away_score": 112, "home": "PHI", "home_score": 109, "market_total": 228.0, "market_spread": 1.0, "favorite": "NYK"},
    {"date": "2026-01-24", "away": "CLE", "away_score": 119, "home": "ORL", "home_score": 105, "market_total": 226.0, "market_spread": 1.0, "favorite": "ORL"},
    {"date": "2026-01-24", "away": "BOS", "away_score": 111, "home": "CHI", "home_score": 114, "market_total": 232.0, "market_spread": 3.0, "favorite": "BOS"},
    
    # Jan 26, 2026 - 4 games (chunk 0)
    {"date": "2026-01-26", "away": "IND", "away_score": 116, "home": "ATL", "home_score": 132, "market_total": 234.0, "market_spread": 5.5, "favorite": "ATL"},
    {"date": "2026-01-26", "away": "PHI", "away_score": 93, "home": "CHA", "home_score": 130, "market_total": 229.5, "market_spread": 2.0, "favorite": "CHA"},
    {"date": "2026-01-26", "away": "ORL", "away_score": 98, "home": "CLE", "home_score": 114, "market_total": 222.5, "market_spread": 5.0, "favorite": "CLE"},
    {"date": "2026-01-26", "away": "MEM", "away_score": 99, "home": "HOU", "home_score": 108, "market_total": 225.5, "market_spread": 11.0, "favorite": "HOU"},
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
