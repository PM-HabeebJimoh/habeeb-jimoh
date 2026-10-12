#!/usr/bin/env python3
"""Add NBA games from Mar 5-10, 2026 with real closing lines from Covers.com"""
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
    # ===== Mar 5, 2026 (chunk 1 - 4 more games) =====
    {"date": "2026-03-05", "away": "CHI", "away_score": 105, "home": "PHX", "home_score": 103, "market_total": 225.0, "market_spread": 11.5, "favorite": "PHX"},
    {"date": "2026-03-05", "away": "LAL", "away_score": 113, "home": "DEN", "home_score": 120, "market_total": 241.0, "market_spread": 4.0, "favorite": "DEN"},
    {"date": "2026-03-05", "away": "NOP", "away_score": 133, "home": "SAC", "home_score": 123, "market_total": 236.0, "market_spread": 6.5, "favorite": "NOP"},

    # ===== Mar 6, 2026 - 4 games =====
    {"date": "2026-03-06", "away": "MIA", "away_score": 128, "home": "CHA", "home_score": 120, "market_total": 229.5, "market_spread": 7.0, "favorite": "CHA"},
    {"date": "2026-03-06", "away": "DAL", "away_score": 100, "home": "BOS", "home_score": 120, "market_total": 226.0, "market_spread": 15.5, "favorite": "BOS"},
    {"date": "2026-03-06", "away": "POR", "away_score": 99, "home": "HOU", "home_score": 106, "market_total": 221.0, "market_spread": 6.5, "favorite": "HOU"},
    {"date": "2026-03-06", "away": "NOP", "away_score": 116, "home": "PHX", "home_score": 118, "market_total": 228.0, "market_spread": 4.0, "favorite": "PHX"},

    # ===== Mar 7, 2026 - 4 games =====
    {"date": "2026-03-07", "away": "ORL", "away_score": 119, "home": "MIN", "home_score": 92, "market_total": 225.0, "market_spread": 7.0, "favorite": "MIN"},
    {"date": "2026-03-07", "away": "BKN", "away_score": 107, "home": "DET", "home_score": 105, "market_total": 214.5, "market_spread": 13.5, "favorite": "DET"},
    {"date": "2026-03-07", "away": "PHI", "away_score": 116, "home": "ATL", "home_score": 125, "market_total": 234.5, "market_spread": 7.0, "favorite": "ATL"},
    {"date": "2026-03-07", "away": "LAC", "away_score": 123, "home": "MEM", "home_score": 120, "market_total": 229.0, "market_spread": 7.5, "favorite": "MEM"},

    # ===== Mar 8, 2026 - 4 games =====
    {"date": "2026-03-08", "away": "BOS", "away_score": 109, "home": "CLE", "home_score": 98, "market_total": 224.5, "market_spread": 2.0, "favorite": "CLE"},
    {"date": "2026-03-08", "away": "NYK", "away_score": 97, "home": "LAL", "home_score": 110, "market_total": 227.0, "market_spread": 5.0, "favorite": "NYK"},
    {"date": "2026-03-08", "away": "DET", "away_score": 110, "home": "MIA", "home_score": 121, "market_total": 230.5, "market_spread": 1.0, "favorite": "DET"},
    {"date": "2026-03-08", "away": "DAL", "away_score": 92, "home": "TOR", "home_score": 122, "market_total": 233.5, "market_spread": 10.0, "favorite": "TOR"},

    # ===== Mar 9, 2026 - 4 games =====
    {"date": "2026-03-09", "away": "PHI", "away_score": 101, "home": "CLE", "home_score": 115, "market_total": 225.5, "market_spread": 14.0, "favorite": "CLE"},
    {"date": "2026-03-09", "away": "DEN", "away_score": 126, "home": "OKC", "home_score": 129, "market_total": 237.0, "market_spread": 3.5, "favorite": "OKC"},
    {"date": "2026-03-09", "away": "MEM", "away_score": 115, "home": "BKN", "home_score": 129, "market_total": 220.0, "market_spread": 1.0, "favorite": "BKN"},
    {"date": "2026-03-09", "away": "GSW", "away_score": 116, "home": "UTA", "home_score": 119, "market_total": 225.5, "market_spread": 6.5, "favorite": "UTA"},

    # ===== Mar 10, 2026 - 4 games =====
    {"date": "2026-03-10", "away": "MEM", "away_score": 129, "home": "PHI", "home_score": 139, "market_total": 229.0, "market_spread": 5.0, "favorite": "PHI"},
    {"date": "2026-03-10", "away": "DET", "away_score": 138, "home": "BKN", "home_score": 100, "market_total": 217.0, "market_spread": 15.0, "favorite": "DET"},
    {"date": "2026-03-10", "away": "DAL", "away_score": 112, "home": "ATL", "home_score": 124, "market_total": 240.5, "market_spread": 10.0, "favorite": "ATL"},
    {"date": "2026-03-10", "away": "WAS", "away_score": 129, "home": "MIA", "home_score": 150, "market_total": 236.5, "market_spread": 16.0, "favorite": "MIA"},
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
