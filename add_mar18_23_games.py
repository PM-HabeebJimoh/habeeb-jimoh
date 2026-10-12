#!/usr/bin/env python3
"""Add NBA games from Mar 18-23, 2026 with real closing lines from Covers.com"""
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
    # ===== Mar 18, 2026 - 4 games =====
    {"date": "2026-03-18", "away": "GSW", "away_score": 99, "home": "BOS", "home_score": 120, "market_total": 217.0, "market_spread": 11.5, "favorite": "BOS"},
    {"date": "2026-03-18", "away": "OKC", "away_score": 121, "home": "BKN", "home_score": 92, "market_total": 216.5, "market_spread": 19.0, "favorite": "OKC"},
    {"date": "2026-03-18", "away": "POR", "away_score": 127, "home": "IND", "home_score": 119, "market_total": 233.0, "market_spread": 11.5, "favorite": "POR"},
    {"date": "2026-03-18", "away": "TOR", "away_score": 139, "home": "CHI", "home_score": 109, "market_total": 237.0, "market_spread": 8.0, "favorite": "TOR"},

    # ===== Mar 19, 2026 - 4 games =====
    {"date": "2026-03-19", "away": "DET", "away_score": 117, "home": "WAS", "home_score": 95, "market_total": 231.5, "market_spread": 14.5, "favorite": "DET"},
    {"date": "2026-03-19", "away": "ORL", "away_score": 111, "home": "CHA", "home_score": 130, "market_total": 226.5, "market_spread": 6.0, "favorite": "CHA"},
    {"date": "2026-03-19", "away": "CLE", "away_score": 115, "home": "CHI", "home_score": 110, "market_total": 237.0, "market_spread": 9.5, "favorite": "CLE"},
    {"date": "2026-03-19", "away": "LAC", "away_score": 99, "home": "NOP", "home_score": 105, "market_total": 229.0, "market_spread": 4.0, "favorite": "NOP"},

    # ===== Mar 20, 2026 - 4 games =====
    {"date": "2026-03-20", "away": "NYK", "away_score": 93, "home": "BKN", "home_score": 92, "market_total": 214.5, "market_spread": 18.5, "favorite": "NYK"},
    {"date": "2026-03-20", "away": "GSW", "away_score": 101, "home": "DET", "home_score": 115, "market_total": 219.0, "market_spread": 6.0, "favorite": "DET"},
    {"date": "2026-03-20", "away": "POR", "away_score": 108, "home": "MIN", "home_score": 104, "market_total": 231.0, "market_spread": 1.0, "favorite": "POR"},
    {"date": "2026-03-20", "away": "BOS", "away_score": 117, "home": "MEM", "home_score": 112, "market_total": 229.5, "market_spread": 15.0, "favorite": "BOS"},

    # ===== Mar 21, 2026 - 4 games =====
    {"date": "2026-03-21", "away": "OKC", "away_score": 132, "home": "WAS", "home_score": 111, "market_total": 231.0, "market_spread": 21.5, "favorite": "OKC"},
    {"date": "2026-03-21", "away": "CLE", "away_score": 111, "home": "NOP", "home_score": 106, "market_total": 238.0, "market_spread": 5.0, "favorite": "CLE"},
    {"date": "2026-03-21", "away": "LAL", "away_score": 105, "home": "ORL", "home_score": 104, "market_total": 234.5, "market_spread": 2.5, "favorite": "LAL"},
    {"date": "2026-03-21", "away": "MEM", "away_score": 101, "home": "CHA", "home_score": 124, "market_total": 232.5, "market_spread": 19.0, "favorite": "CHA"},

    # ===== Mar 22, 2026 - 4 games =====
    {"date": "2026-03-22", "away": "POR", "away_score": 112, "home": "DEN", "home_score": 128, "market_total": 237.5, "market_spread": 8.0, "favorite": "DEN"},
    {"date": "2026-03-22", "away": "BKN", "away_score": 122, "home": "SAC", "home_score": 126, "market_total": 218.5, "market_spread": 7.0, "favorite": "SAC"},
    {"date": "2026-03-22", "away": "WAS", "away_score": 113, "home": "NYK", "home_score": 145, "market_total": 229.5, "market_spread": 22.5, "favorite": "NYK"},
    {"date": "2026-03-22", "away": "MIN", "away_score": 102, "home": "BOS", "home_score": 92, "market_total": 222.5, "market_spread": 10.0, "favorite": "BOS"},

    # ===== Mar 23, 2026 - 4 games =====
    {"date": "2026-03-23", "away": "OKC", "away_score": 123, "home": "PHI", "home_score": 103, "market_total": 226.5, "market_spread": 16.0, "favorite": "OKC"},
    {"date": "2026-03-23", "away": "SAS", "away_score": 136, "home": "MIA", "home_score": 111, "market_total": 244.5, "market_spread": 3.5, "favorite": "SAS"},
    {"date": "2026-03-23", "away": "LAL", "away_score": 110, "home": "DET", "home_score": 113, "market_total": 224.5, "market_spread": 1.0, "favorite": "DET"},
    {"date": "2026-03-23", "away": "IND", "away_score": 128, "home": "ORL", "home_score": 126, "market_total": 233.5, "market_spread": 10.5, "favorite": "ORL"},
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
