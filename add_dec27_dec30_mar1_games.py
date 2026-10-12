#!/usr/bin/env python3
"""Add NBA games from Dec 27, Dec 30, and Mar 1"""
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
    # ===== Dec 27, 2025 - 9 games =====
    {"date": "2025-12-27", "away": "DAL", "away_score": 107, "home": "SAC", "home_score": 113, "market_total": 236.5, "market_spread": 1.0, "favorite": "SAC"},
    {"date": "2025-12-27", "away": "DEN", "away_score": 126, "home": "ORL", "home_score": 127, "market_total": 239.0, "market_spread": 1.5, "favorite": "ORL"},
    {"date": "2025-12-27", "away": "PHX", "away_score": 123, "home": "NOP", "home_score": 114, "market_total": 238.0, "market_spread": 4.5, "favorite": "PHX"},
    {"date": "2025-12-27", "away": "MIL", "away_score": 112, "home": "CHI", "home_score": 103, "market_total": 229.5, "market_spread": 3.0, "favorite": "MIL"},
    {"date": "2025-12-27", "away": "NYK", "away_score": 128, "home": "ATL", "home_score": 125, "market_total": 243.5, "market_spread": 4.5, "favorite": "NYK"},
    {"date": "2025-12-27", "away": "UTA", "away_score": 127, "home": "SAS", "home_score": 114, "market_total": 243.5, "market_spread": 13.0, "favorite": "UTA"},
    {"date": "2025-12-27", "away": "IND", "away_score": 116, "home": "MIA", "home_score": 142, "market_total": 238.5, "market_spread": 6.5, "favorite": "MIA"},
    {"date": "2025-12-27", "away": "CLE", "away_score": 100, "home": "HOU", "home_score": 117, "market_total": 228.5, "market_spread": 2.0, "favorite": "HOU"},
    {"date": "2025-12-27", "away": "BKN", "away_score": 123, "home": "MIN", "home_score": 107, "market_total": 225.5, "market_spread": 12.0, "favorite": "BKN"},

    # ===== Dec 30, 2025 - 4 games =====
    {"date": "2025-12-30", "away": "PHI", "away_score": 139, "home": "MEM", "home_score": 136, "market_total": 237.5, "market_spread": 3.5, "favorite": "PHI"},
    {"date": "2025-12-30", "away": "BOS", "away_score": 129, "home": "UTA", "home_score": 119, "market_total": 247.0, "market_spread": 4.0, "favorite": "BOS"},
    {"date": "2025-12-30", "away": "DET", "away_score": 128, "home": "LAL", "home_score": 106, "market_total": 238.5, "market_spread": 3.0, "favorite": "DET"},
    {"date": "2025-12-30", "away": "SAC", "away_score": 90, "home": "LAC", "home_score": 131, "market_total": 216.5, "market_spread": 10.0, "favorite": "LAC"},

    # ===== Mar 1, 2026 - 9 games =====
    {"date": "2026-03-01", "away": "SAS", "away_score": 89, "home": "NYK", "home_score": 114, "market_total": 227.5, "market_spread": 1.0, "favorite": "NYK"},
    {"date": "2026-03-01", "away": "CLE", "away_score": 106, "home": "BKN", "home_score": 102, "market_total": 224.5, "market_spread": 11.5, "favorite": "CLE"},
    {"date": "2026-03-01", "away": "MIN", "away_score": 117, "home": "DEN", "home_score": 108, "market_total": 241.0, "market_spread": 3.0, "favorite": "MIN"},
    {"date": "2026-03-01", "away": "MIL", "away_score": 97, "home": "CHI", "home_score": 120, "market_total": 231.5, "market_spread": 2.5, "favorite": "CHI"},
    {"date": "2026-03-01", "away": "DET", "away_score": 106, "home": "ORL", "home_score": 92, "market_total": 225.5, "market_spread": 5.0, "favorite": "DET"},
    {"date": "2026-03-01", "away": "PHI", "away_score": 98, "home": "BOS", "home_score": 114, "market_total": 220.0, "market_spread": 8.5, "favorite": "BOS"},
    {"date": "2026-03-01", "away": "OKC", "away_score": 100, "home": "DAL", "home_score": 87, "market_total": 237.0, "market_spread": 16.5, "favorite": "OKC"},
    {"date": "2026-03-01", "away": "NOP", "away_score": 117, "home": "LAC", "home_score": 137, "market_total": 222.5, "market_spread": 8.5, "favorite": "LAC"},
    {"date": "2026-03-01", "away": "SAC", "away_score": 104, "home": "LAL", "home_score": 128, "market_total": 236.0, "market_spread": 13.0, "favorite": "LAL"},
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
