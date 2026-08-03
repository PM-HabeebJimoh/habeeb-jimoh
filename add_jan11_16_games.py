#!/usr/bin/env python3
"""Add NBA games from Jan 11-16, 2026 with real closing lines from Covers.com"""
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
    # Jan 11, 2026 - chunk 1 (7 more games)
    {"date": "2026-01-11", "away": "MIA", "away_score": 112, "home": "OKC", "home_score": 124, "market_total": 234.0, "market_spread": 15.0, "favorite": "OKC"},
    {"date": "2026-01-11", "away": "SAS", "away_score": 103, "home": "MIN", "home_score": 104, "market_total": 233.0, "market_spread": 2.5, "favorite": "MIN"},
    {"date": "2026-01-11", "away": "WAS", "away_score": 93, "home": "PHX", "home_score": 112, "market_total": 230.5, "market_spread": 15.0, "favorite": "PHX"},
    {"date": "2026-01-11", "away": "MIL", "away_score": 104, "home": "DEN", "home_score": 108, "market_total": 219.0, "market_spread": 6.0, "favorite": "MIL"},
    {"date": "2026-01-11", "away": "ATL", "away_score": 124, "home": "GSW", "home_score": 111, "market_total": 237.5, "market_spread": 7.5, "favorite": "GSW"},
    {"date": "2026-01-11", "away": "HOU", "away_score": 98, "home": "SAC", "home_score": 111, "market_total": 223.0, "market_spread": 14.0, "favorite": "HOU"},
    
    # Jan 12, 2026 - 6 games
    {"date": "2026-01-12", "away": "UTA", "away_score": 123, "home": "CLE", "home_score": 112, "market_total": 249.5, "market_spread": 13.0, "favorite": "CLE"},
    {"date": "2026-01-12", "away": "BOS", "away_score": 96, "home": "IND", "home_score": 98, "market_total": 227.0, "market_spread": 5.0, "favorite": "BOS"},
    {"date": "2026-01-12", "away": "PHI", "away_score": 115, "home": "TOR", "home_score": 102, "market_total": 221.5, "market_spread": 3.0, "favorite": "PHI"},
    {"date": "2026-01-12", "away": "BKN", "away_score": 105, "home": "DAL", "home_score": 113, "market_total": 220.0, "market_spread": 3.5, "favorite": "DAL"},
    {"date": "2026-01-12", "away": "LAL", "away_score": 112, "home": "SAC", "home_score": 124, "market_total": 231.5, "market_spread": 9.5, "favorite": "LAL"},
    {"date": "2026-01-12", "away": "CHA", "away_score": 109, "home": "LAC", "home_score": 117, "market_total": 222.5, "market_spread": 4.5, "favorite": "LAC"},
    
    # Jan 13, 2026 - 7 games
    {"date": "2026-01-13", "away": "PHX", "away_score": 121, "home": "MIA", "home_score": 127, "market_total": 232.5, "market_spread": 1.5, "favorite": "MIA"},
    {"date": "2026-01-13", "away": "DEN", "away_score": 122, "home": "NOP", "home_score": 116, "market_total": 235.5, "market_spread": 2.0, "favorite": "DEN"},
    {"date": "2026-01-13", "away": "SAS", "away_score": 98, "home": "OKC", "home_score": 119, "market_total": 230.0, "market_spread": 8.5, "favorite": "OKC"},
    {"date": "2026-01-13", "away": "CHI", "away_score": 113, "home": "HOU", "home_score": 119, "market_total": 224.0, "market_spread": 12.0, "favorite": "HOU"},
    {"date": "2026-01-13", "away": "MIN", "away_score": 139, "home": "MIL", "home_score": 106, "market_total": 229.5, "market_spread": 1.5, "favorite": "MIL"},
    {"date": "2026-01-13", "away": "ATL", "away_score": 116, "home": "LAL", "home_score": 141, "market_total": 233.5, "market_spread": 1.5, "favorite": "LAL"},
    {"date": "2026-01-13", "away": "POR", "away_score": 97, "home": "GSW", "home_score": 119, "market_total": 226.0, "market_spread": 11.0, "favorite": "GSW"},
    
    # Jan 14, 2026 - 5 games
    {"date": "2026-01-14", "away": "TOR", "away_score": 115, "home": "IND", "home_score": 101, "market_total": 220.5, "market_spread": 1.5, "favorite": "IND"},
    {"date": "2026-01-14", "away": "CLE", "away_score": 133, "home": "PHI", "home_score": 107, "market_total": 237.0, "market_spread": 1.0, "favorite": "PHI"},
    {"date": "2026-01-14", "away": "BKN", "away_score": 113, "home": "NOP", "home_score": 116, "market_total": 232.5, "market_spread": 1.0, "favorite": "BKN"},
    {"date": "2026-01-14", "away": "UTA", "away_score": 126, "home": "CHI", "home_score": 128, "market_total": 241.0, "market_spread": 5.0, "favorite": "CHI"},
    {"date": "2026-01-14", "away": "WAS", "away_score": 105, "home": "LAC", "home_score": 119, "market_total": 227.0, "market_spread": 11.0, "favorite": "LAC"},
    
    # Jan 15, 2026 - 9 games
    {"date": "2026-01-15", "away": "MEM", "away_score": 111, "home": "ORL", "home_score": 118, "market_total": 228.0, "market_spread": 5.5, "favorite": "ORL"},
    {"date": "2026-01-15", "away": "PHX", "away_score": 105, "home": "DET", "home_score": 108, "market_total": 219.0, "market_spread": 7.0, "favorite": "DET"},
    {"date": "2026-01-15", "away": "OKC", "away_score": 111, "home": "HOU", "home_score": 91, "market_total": 222.0, "market_spread": 4.5, "favorite": "OKC"},
    {"date": "2026-01-15", "away": "BOS", "away_score": 119, "home": "MIA", "home_score": 114, "market_total": 235.5, "market_spread": 3.0, "favorite": "BOS"},
    {"date": "2026-01-15", "away": "MIL", "away_score": 101, "home": "SAS", "home_score": 119, "market_total": 225.5, "market_spread": 7.0, "favorite": "SAS"},
    {"date": "2026-01-15", "away": "UTA", "away_score": 122, "home": "DAL", "home_score": 144, "market_total": 237.0, "market_spread": 2.5, "favorite": "DAL"},
    {"date": "2026-01-15", "away": "ATL", "away_score": 101, "home": "POR", "home_score": 117, "market_total": 229.5, "market_spread": 4.0, "favorite": "ATL"},
    {"date": "2026-01-15", "away": "NYK", "away_score": 113, "home": "GSW", "home_score": 126, "market_total": 228.5, "market_spread": 7.5, "favorite": "GSW"},
    {"date": "2026-01-15", "away": "CHA", "away_score": 135, "home": "LAL", "home_score": 117, "market_total": 234.5, "market_spread": 3.5, "favorite": "LAL"},
    
    # Jan 16, 2026 - 4 games (chunk 0, need chunk 1 for more)
    {"date": "2026-01-16", "away": "CLE", "away_score": 117, "home": "PHI", "home_score": 115, "market_total": 233.5, "market_spread": 2.5, "favorite": "PHI"},
    {"date": "2026-01-16", "away": "NOP", "away_score": 119, "home": "IND", "home_score": 127, "market_total": 242.0, "market_spread": 5.0, "favorite": "IND"},
    {"date": "2026-01-16", "away": "LAC", "away_score": 121, "home": "TOR", "home_score": 117, "market_total": 213.5, "market_spread": 2.5, "favorite": "TOR"},
    {"date": "2026-01-16", "away": "CHI", "away_score": 109, "home": "BKN", "home_score": 112, "market_total": 224.5, "market_spread": 1.0, "favorite": "BKN"},
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
