#!/usr/bin/env python3
"""Add additional NBA games from Apr 11, Apr 13, Mar 15, Jan 25, and Mar 1"""
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
    # ===== Apr 11, 2026 - additional games from chunk 1 =====
    {"date": "2026-04-11", "away": "DET", "away_score": 133, "home": "IND", "home_score": 121, "market_total": 230.5, "market_spread": 16.5, "favorite": "DET"},
    {"date": "2026-04-11", "away": "WAS", "away_score": 117, "home": "CLE", "home_score": 130, "market_total": 234.5, "market_spread": 11.0, "favorite": "CLE"},
    {"date": "2026-04-11", "away": "CHA", "away_score": 110, "home": "NYK", "home_score": 96, "market_total": 216.5, "market_spread": 14.5, "favorite": "CHA"},
    {"date": "2026-04-11", "away": "SAC", "away_score": 110, "home": "POR", "home_score": 122, "market_total": 227.0, "market_spread": 18.5, "favorite": "POR"},
    {"date": "2026-04-11", "away": "MEM", "away_score": 101, "home": "HOU", "home_score": 132, "market_total": 231.5, "market_spread": 14.5, "favorite": "HOU"},
    {"date": "2026-04-11", "away": "CHI", "away_score": 128, "home": "DAL", "home_score": 149, "market_total": 249.5, "market_spread": 5.0, "favorite": "DAL"},
    {"date": "2026-04-11", "away": "PHX", "away_score": 135, "home": "OKC", "home_score": 103, "market_total": 212.5, "market_spread": 7.5, "favorite": "PHX"},

    # ===== Apr 13, 2026 - Play-in games =====
    {"date": "2026-04-13", "away": "MIA", "away_score": 126, "home": "CHA", "home_score": 127, "market_total": 228.0, "market_spread": 6.0, "favorite": "CHA"},
    {"date": "2026-04-13", "away": "POR", "away_score": 114, "home": "PHX", "home_score": 110, "market_total": 216.0, "market_spread": 2.5, "favorite": "POR"},

    # ===== Mar 15, 2026 - 6 games =====
    {"date": "2026-03-15", "away": "MIN", "away_score": 103, "home": "OKC", "home_score": 116, "market_total": 228.0, "market_spread": 9.0, "favorite": "OKC"},
    {"date": "2026-03-15", "away": "IND", "away_score": 123, "home": "MIL", "home_score": 134, "market_total": 228.0, "market_spread": 7.5, "favorite": "MIL"},
    {"date": "2026-03-15", "away": "DAL", "away_score": 130, "home": "CLE", "home_score": 120, "market_total": 234.0, "market_spread": 15.0, "favorite": "DAL"},
    {"date": "2026-03-15", "away": "DET", "away_score": 108, "home": "TOR", "home_score": 119, "market_total": 224.5, "market_spread": 3.0, "favorite": "TOR"},
    {"date": "2026-03-15", "away": "UTA", "away_score": 111, "home": "SAC", "home_score": 116, "market_total": 230.5, "market_spread": 3.5, "favorite": "SAC"},

    # ===== Jan 25, 2026 - 9 games =====
    {"date": "2026-01-25", "away": "SAC", "away_score": 116, "home": "DET", "home_score": 139, "market_total": 227.0, "market_spread": 13.0, "favorite": "DET"},
    {"date": "2026-01-25", "away": "GSW", "away_score": 111, "home": "MIN", "home_score": 85, "market_total": 236.5, "market_spread": 6.0, "favorite": "GSW"},
    {"date": "2026-01-25", "away": "NOP", "away_score": 104, "home": "SAS", "home_score": 95, "market_total": 239.5, "market_spread": 11.5, "favorite": "NOP"},
    {"date": "2026-01-25", "away": "TOR", "away_score": 103, "home": "OKC", "home_score": 101, "market_total": 225.5, "market_spread": 11.0, "favorite": "TOR"},
    {"date": "2026-01-25", "away": "MIA", "away_score": 111, "home": "PHX", "home_score": 102, "market_total": 226.0, "market_spread": 4.5, "favorite": "MIA"},
    {"date": "2026-01-25", "away": "BKN", "away_score": 89, "home": "LAC", "home_score": 126, "market_total": 211.5, "market_spread": 10.5, "favorite": "LAC"},
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
