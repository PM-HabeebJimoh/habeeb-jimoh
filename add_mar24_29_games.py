#!/usr/bin/env python3
"""Add NBA games from Mar 24-29, 2026 with real closing lines from Covers.com"""
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
    # ===== Mar 24, 2026 - 4 games =====
    {"date": "2026-03-24", "away": "SAC", "away_score": 90, "home": "CHA", "home_score": 134, "market_total": 233.0, "market_spread": 18.0, "favorite": "CHA"},
    {"date": "2026-03-24", "away": "NOP", "away_score": 116, "home": "NYK", "home_score": 121, "market_total": 228.5, "market_spread": 8.5, "favorite": "NYK"},
    {"date": "2026-03-24", "away": "ORL", "away_score": 131, "home": "CLE", "home_score": 136, "market_total": 229.5, "market_spread": 10.5, "favorite": "CLE"},
    {"date": "2026-03-24", "away": "DEN", "away_score": 125, "home": "PHX", "home_score": 123, "market_total": 233.5, "market_spread": 6.0, "favorite": "DEN"},

    # ===== Mar 25, 2026 - 4 games =====
    {"date": "2026-03-25", "away": "ATL", "away_score": 130, "home": "DET", "home_score": 129, "market_total": 229.5, "market_spread": 2.5, "favorite": "DET"},
    {"date": "2026-03-25", "away": "CHI", "away_score": 137, "home": "PHI", "home_score": 157, "market_total": 241.0, "market_spread": 6.5, "favorite": "PHI"},
    {"date": "2026-03-25", "away": "LAL", "away_score": 137, "home": "IND", "home_score": 130, "market_total": 241.0, "market_spread": 8.5, "favorite": "LAL"},
    {"date": "2026-03-25", "away": "MIA", "away_score": 120, "home": "CLE", "home_score": 103, "market_total": 243.0, "market_spread": 2.5, "favorite": "CLE"},

    # ===== Mar 26, 2026 - 3 games =====
    {"date": "2026-03-26", "away": "SAC", "away_score": 117, "home": "ORL", "home_score": 121, "market_total": 231.0, "market_spread": 15.5, "favorite": "ORL"},
    {"date": "2026-03-26", "away": "NOP", "away_score": 108, "home": "DET", "home_score": 129, "market_total": 225.5, "market_spread": 5.5, "favorite": "DET"},
    {"date": "2026-03-26", "away": "NYK", "away_score": 103, "home": "CHA", "home_score": 114, "market_total": 224.0, "market_spread": 2.5, "favorite": "CHA"},

    # ===== Mar 27, 2026 - 4 games =====
    {"date": "2026-03-27", "away": "LAC", "away_score": 114, "home": "IND", "home_score": 113, "market_total": 236.5, "market_spread": 9.0, "favorite": "IND"},
    {"date": "2026-03-27", "away": "MIA", "away_score": 128, "home": "CLE", "home_score": 149, "market_total": 241.0, "market_spread": 5.5, "favorite": "CLE"},
    {"date": "2026-03-27", "away": "ATL", "away_score": 102, "home": "BOS", "home_score": 109, "market_total": 223.5, "market_spread": 4.5, "favorite": "BOS"},
    {"date": "2026-03-27", "away": "CHI", "away_score": 113, "home": "OKC", "home_score": 131, "market_total": 241.5, "market_spread": 19.0, "favorite": "OKC"},

    # ===== Mar 28, 2026 - 4 games =====
    {"date": "2026-03-28", "away": "SAS", "away_score": 127, "home": "MIL", "home_score": 95, "market_total": 227.5, "market_spread": 17.0, "favorite": "SAS"},
    {"date": "2026-03-28", "away": "DET", "away_score": 109, "home": "MIN", "home_score": 87, "market_total": 222.0, "market_spread": 2.0, "favorite": "DET"},
    {"date": "2026-03-28", "away": "PHI", "away_score": 118, "home": "CHA", "home_score": 114, "market_total": 232.0, "market_spread": 6.5, "favorite": "CHA"},
    {"date": "2026-03-28", "away": "SAC", "away_score": 113, "home": "ATL", "home_score": 123, "market_total": 235.0, "market_spread": 13.5, "favorite": "ATL"},

    # ===== Mar 29, 2026 - 4 games =====
    {"date": "2026-03-29", "away": "LAC", "away_score": 127, "home": "MIL", "home_score": 113, "market_total": 219.5, "market_spread": 17.5, "favorite": "LAC"},
    {"date": "2026-03-29", "away": "MIA", "away_score": 118, "home": "IND", "home_score": 135, "market_total": 245.5, "market_spread": 8.5, "favorite": "IND"},
    {"date": "2026-03-29", "away": "BOS", "away_score": 114, "home": "CHA", "home_score": 99, "market_total": 217.0, "market_spread": 2.0, "favorite": "BOS"},
    {"date": "2026-03-29", "away": "WAS", "away_score": 88, "home": "POR", "home_score": 123, "market_total": 235.5, "market_spread": 16.5, "favorite": "POR"},
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
