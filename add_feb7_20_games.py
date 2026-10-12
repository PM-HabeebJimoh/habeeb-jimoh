#!/usr/bin/env python3
"""Add NBA games from Feb 7-20, 2026 with real closing lines from Covers.com"""
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
    # Feb 7, 2026 - 4 games (chunk 0)
    {"date": "2026-02-07", "away": "WAS", "away_score": 113, "home": "BKN", "home_score": 127, "market_total": 216.5, "market_spread": 8.0, "favorite": "BKN"},
    {"date": "2026-02-07", "away": "HOU", "away_score": 112, "home": "OKC", "home_score": 106, "market_total": 214.0, "market_spread": 4.0, "favorite": "OKC"},
    {"date": "2026-02-07", "away": "DAL", "away_score": 125, "home": "SAS", "home_score": 138, "market_total": 234.5, "market_spread": 11.0, "favorite": "SAS"},
    {"date": "2026-02-07", "away": "UTA", "away_score": 117, "home": "ORL", "home_score": 120, "market_total": 234.5, "market_spread": 7.5, "favorite": "ORL"},
    
    # Feb 10, 2026 - 4 games (chunk 0)
    {"date": "2026-02-10", "away": "IND", "away_score": 137, "home": "NYK", "home_score": 134, "market_total": 227.0, "market_spread": 11.0, "favorite": "NYK"},
    {"date": "2026-02-10", "away": "LAC", "away_score": 95, "home": "HOU", "home_score": 102, "market_total": 213.5, "market_spread": 9.0, "favorite": "HOU"},
    {"date": "2026-02-10", "away": "DAL", "away_score": 111, "home": "PHX", "home_score": 120, "market_total": 230.0, "market_spread": 8.5, "favorite": "PHX"},
    {"date": "2026-02-10", "away": "SAS", "away_score": 136, "home": "LAL", "home_score": 108, "market_total": 226.0, "market_spread": 13.5, "favorite": "SAS"},
    
    # Feb 12, 2026 - 3 games (chunk 0, All-Star break)
    {"date": "2026-02-12", "away": "MIL", "away_score": 110, "home": "OKC", "home_score": 93, "market_total": 214.5, "market_spread": 13.5, "favorite": "OKC"},
    {"date": "2026-02-12", "away": "POR", "away_score": 135, "home": "UTA", "home_score": 119, "market_total": 236.5, "market_spread": 6.0, "favorite": "POR"},
    {"date": "2026-02-12", "away": "DAL", "away_score": 104, "home": "LAL", "home_score": 124, "market_total": 237.0, "market_spread": 6.0, "favorite": "LAL"},
    
    # Feb 14, 2026 - 4 games (chunk 0)
    {"date": "2026-02-14", "away": "BKN", "away_score": 84, "home": "CLE", "home_score": 112, "market_total": 229.5, "market_spread": 16.0, "favorite": "CLE"},
    {"date": "2026-02-14", "away": "ATL", "away_score": 117, "home": "PHI", "home_score": 107, "market_total": 241.5, "market_spread": 1.0, "favorite": "PHI"},
    {"date": "2026-02-14", "away": "HOU", "away_score": 105, "home": "CHA", "home_score": 101, "market_total": 218.0, "market_spread": 5.0, "favorite": "HOU"},
    {"date": "2026-02-14", "away": "IND", "away_score": 105, "home": "WAS", "home_score": 112, "market_total": 233.5, "market_spread": 2.0, "favorite": "WAS"},
    
    # Feb 20, 2026 - 4 games (chunk 0, after All-Star break)
    {"date": "2026-02-20", "away": "UTA", "away_score": 114, "home": "MEM", "home_score": 123, "market_total": 237.5, "market_spread": 2.5, "favorite": "MEM"},
    {"date": "2026-02-20", "away": "CLE", "away_score": 118, "home": "CHA", "home_score": 113, "market_total": 229.0, "market_spread": 6.0, "favorite": "CLE"},
    {"date": "2026-02-20", "away": "IND", "away_score": 118, "home": "WAS", "home_score": 131, "market_total": 230.0, "market_spread": 1.5, "favorite": "WAS"},
    {"date": "2026-02-20", "away": "MIA", "away_score": 128, "home": "ATL", "home_score": 97, "market_total": 244.0, "market_spread": 3.5, "favorite": "MIA"},
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
