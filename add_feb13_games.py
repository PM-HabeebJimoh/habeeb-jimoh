#!/usr/bin/env python3
"""Add NBA games from Feb 13 and Apr 12 (last missing dates)"""
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
    # ===== Feb 13, 2026 - 10 games =====
    {"date": "2026-02-13", "away": "BKN", "away_score": 84, "home": "CLE", "home_score": 112, "market_total": 229.5, "market_spread": 16.0, "favorite": "CLE"},
    {"date": "2026-02-13", "away": "ATL", "away_score": 117, "home": "PHI", "home_score": 107, "market_total": 241.5, "market_spread": 1.0, "favorite": "ATL"},
    {"date": "2026-02-13", "away": "HOU", "away_score": 105, "home": "CHA", "home_score": 101, "market_total": 218.0, "market_spread": 5.0, "favorite": "HOU"},
    {"date": "2026-02-13", "away": "IND", "away_score": 105, "home": "WAS", "home_score": 112, "market_total": 233.5, "market_spread": 2.0, "favorite": "WAS"},
    {"date": "2026-02-13", "away": "DET", "away_score": 126, "home": "NYK", "home_score": 111, "market_total": 218.5, "market_spread": 4.0, "favorite": "DET"},
    {"date": "2026-02-13", "away": "TOR", "away_score": 110, "home": "CHI", "home_score": 101, "market_total": 234.5, "market_spread": 6.0, "favorite": "TOR"},
    {"date": "2026-02-13", "away": "PHX", "away_score": 94, "home": "SAS", "home_score": 121, "market_total": 229.5, "market_spread": 8.0, "favorite": "SAS"},
    {"date": "2026-02-13", "away": "BOS", "away_score": 121, "home": "GSW", "home_score": 110, "market_total": 211.5, "market_spread": 5.5, "favorite": "BOS"},
    {"date": "2026-02-13", "away": "ORL", "away_score": 131, "home": "SAC", "home_score": 94, "market_total": 226.5, "market_spread": 8.0, "favorite": "ORL"},
    {"date": "2026-02-13", "away": "DEN", "away_score": 114, "home": "LAC", "home_score": 115, "market_total": 226.5, "market_spread": 4.5, "favorite": "LAC"},

    # ===== Apr 12, 2026 - same games as Apr 11 (Covers.com shows same data) =====
    # These are the same games we already have under Apr 11, so no new games needed
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
