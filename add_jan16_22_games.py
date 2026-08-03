#!/usr/bin/env python3
"""Add NBA games from Jan 16-22, 2026 with real closing lines from Covers.com"""
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
    # Jan 16, 2026 - chunk 1 (2 more games)
    {"date": "2026-01-16", "away": "MIN", "away_score": 105, "home": "HOU", "home_score": 110, "market_total": 221.0, "market_spread": 4.0, "favorite": "HOU"},
    {"date": "2026-01-16", "away": "WAS", "away_score": 115, "home": "SAC", "home_score": 128, "market_total": 235.0, "market_spread": 7.5, "favorite": "SAC"},
    
    # Jan 17, 2026 - 9 games
    {"date": "2026-01-17", "away": "UTA", "away_score": 120, "home": "DAL", "home_score": 138, "market_total": 240.5, "market_spread": 3.0, "favorite": "DAL"},
    {"date": "2026-01-17", "away": "PHX", "away_score": 106, "home": "NYK", "home_score": 99, "market_total": 224.0, "market_spread": 1.0, "favorite": "NYK"},
    {"date": "2026-01-17", "away": "BOS", "away_score": 132, "home": "ATL", "home_score": 106, "market_total": 230.5, "market_spread": 3.5, "favorite": "BOS"},
    {"date": "2026-01-17", "away": "IND", "away_score": 78, "home": "DET", "home_score": 121, "market_total": 225.0, "market_spread": 16.0, "favorite": "DET"},
    {"date": "2026-01-17", "away": "OKC", "away_score": 120, "home": "MIA", "home_score": 122, "market_total": 235.0, "market_spread": 11.5, "favorite": "OKC"},
    {"date": "2026-01-17", "away": "MIN", "away_score": 123, "home": "SAS", "home_score": 126, "market_total": 234.5, "market_spread": 5.0, "favorite": "SAS"},
    {"date": "2026-01-17", "away": "CHA", "away_score": 116, "home": "GSW", "home_score": 136, "market_total": 237.5, "market_spread": 7.5, "favorite": "GSW"},
    {"date": "2026-01-17", "away": "WAS", "away_score": 115, "home": "DEN", "home_score": 121, "market_total": 227.0, "market_spread": 10.0, "favorite": "DEN"},
    {"date": "2026-01-17", "away": "LAL", "away_score": 116, "home": "POR", "home_score": 132, "market_total": 223.5, "market_spread": 3.5, "favorite": "POR"},
    
    # Jan 18, 2026 - 6 games
    {"date": "2026-01-18", "away": "ORL", "away_score": 109, "home": "MEM", "home_score": 126, "market_total": 229.5, "market_spread": 3.0, "favorite": "ORL"},
    {"date": "2026-01-18", "away": "NOP", "away_score": 110, "home": "HOU", "home_score": 119, "market_total": 232.5, "market_spread": 14.0, "favorite": "HOU"},
    {"date": "2026-01-18", "away": "BKN", "away_score": 102, "home": "CHI", "home_score": 124, "market_total": 223.5, "market_spread": 7.0, "favorite": "CHI"},
    {"date": "2026-01-18", "away": "CHA", "away_score": 110, "home": "DEN", "home_score": 87, "market_total": 226.0, "market_spread": 2.5, "favorite": "CHA"},
    {"date": "2026-01-18", "away": "POR", "away_score": 117, "home": "SAC", "home_score": 110, "market_total": 230.5, "market_spread": 1.0, "favorite": "POR"},
    {"date": "2026-01-18", "away": "TOR", "away_score": 93, "home": "LAL", "home_score": 110, "market_total": 227.0, "market_spread": 2.5, "favorite": "LAL"},
    
    # Jan 19, 2026 - 9 games
    {"date": "2026-01-19", "away": "MIL", "away_score": 112, "home": "ATL", "home_score": 110, "market_total": 232.5, "market_spread": 1.5, "favorite": "ATL"},
    {"date": "2026-01-19", "away": "OKC", "away_score": 136, "home": "CLE", "home_score": 104, "market_total": 230.0, "market_spread": 6.0, "favorite": "OKC"},
    {"date": "2026-01-19", "away": "LAC", "away_score": 110, "home": "WAS", "home_score": 106, "market_total": 227.0, "market_spread": 6.5, "favorite": "LAC"},
    {"date": "2026-01-19", "away": "DAL", "away_score": 114, "home": "NYK", "home_score": 97, "market_total": 232.0, "market_spread": 12.5, "favorite": "NYK"},
    {"date": "2026-01-19", "away": "UTA", "away_score": 110, "home": "SAS", "home_score": 123, "market_total": 237.5, "market_spread": 16.5, "favorite": "SAS"},
    {"date": "2026-01-19", "away": "IND", "away_score": 104, "home": "PHI", "home_score": 113, "market_total": 229.5, "market_spread": 7.0, "favorite": "PHI"},
    {"date": "2026-01-19", "away": "PHX", "away_score": 126, "home": "BKN", "home_score": 117, "market_total": 214.5, "market_spread": 9.5, "favorite": "PHX"},
    {"date": "2026-01-19", "away": "BOS", "away_score": 103, "home": "DET", "home_score": 104, "market_total": 223.0, "market_spread": 2.5, "favorite": "DET"},
    {"date": "2026-01-19", "away": "MIA", "away_score": 112, "home": "GSW", "home_score": 135, "market_total": 239.5, "market_spread": 5.0, "favorite": "GSW"},
    
    # Jan 21, 2026 - 7 games
    {"date": "2026-01-21", "away": "CLE", "away_score": 94, "home": "CHA", "home_score": 87, "market_total": 238.0, "market_spread": 3.5, "favorite": "CLE"},
    {"date": "2026-01-21", "away": "IND", "away_score": 104, "home": "BOS", "home_score": 119, "market_total": 225.0, "market_spread": 10.0, "favorite": "BOS"},
    {"date": "2026-01-21", "away": "BKN", "away_score": 66, "home": "NYK", "home_score": 120, "market_total": 220.0, "market_spread": 12.5, "favorite": "NYK"},
    {"date": "2026-01-21", "away": "ATL", "away_score": 124, "home": "MEM", "home_score": 122, "market_total": 239.5, "market_spread": 1.5, "favorite": "MEM"},
    {"date": "2026-01-21", "away": "DET", "away_score": 112, "home": "NOP", "home_score": 104, "market_total": 232.5, "market_spread": 7.5, "favorite": "DET"},
    {"date": "2026-01-21", "away": "OKC", "away_score": 122, "home": "MIL", "home_score": 102, "market_total": 224.5, "market_spread": 12.5, "favorite": "OKC"},
    {"date": "2026-01-21", "away": "TOR", "away_score": 122, "home": "SAC", "home_score": 109, "market_total": 226.5, "market_spread": 5.0, "favorite": "TOR"},
    
    # Jan 22, 2026 - 4 games (chunk 0)
    {"date": "2026-01-22", "away": "CHA", "away_score": 124, "home": "ORL", "home_score": 97, "market_total": 224.5, "market_spread": 4.0, "favorite": "ORL"},
    {"date": "2026-01-22", "away": "DEN", "away_score": 107, "home": "WAS", "home_score": 97, "market_total": 227.5, "market_spread": 6.0, "favorite": "DEN"},
    {"date": "2026-01-22", "away": "HOU", "away_score": 122, "home": "PHI", "home_score": 128, "market_total": 221.0, "market_spread": 2.0, "favorite": "HOU"},
    {"date": "2026-01-22", "away": "GSW", "away_score": 115, "home": "DAL", "home_score": 123, "market_total": 234.5, "market_spread": 6.5, "favorite": "GSW"},
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
