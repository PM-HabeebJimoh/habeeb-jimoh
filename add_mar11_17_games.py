#!/usr/bin/env python3
"""Add NBA games from Mar 11-17, 2026 with real closing lines from Covers.com"""
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
    # ===== Mar 11, 2026 - 4 games =====
    {"date": "2026-03-11", "away": "CLE", "away_score": 122, "home": "ORL", "home_score": 128, "market_total": 226.5, "market_spread": 3.5, "favorite": "CLE"},
    {"date": "2026-03-11", "away": "TOR", "away_score": 111, "home": "NOP", "home_score": 122, "market_total": 235.5, "market_spread": 2.5, "favorite": "NOP"},
    {"date": "2026-03-11", "away": "NYK", "away_score": 134, "home": "UTA", "home_score": 117, "market_total": 231.5, "market_spread": 14.0, "favorite": "NYK"},
    {"date": "2026-03-11", "away": "HOU", "away_score": 93, "home": "DEN", "home_score": 129, "market_total": 232.0, "market_spread": 7.0, "favorite": "DEN"},

    # ===== Mar 12, 2026 - 4 games =====
    {"date": "2026-03-12", "away": "WAS", "away_score": 131, "home": "ORL", "home_score": 136, "market_total": 236.5, "market_spread": 13.5, "favorite": "ORL"},
    {"date": "2026-03-12", "away": "PHX", "away_score": 123, "home": "IND", "home_score": 108, "market_total": 222.0, "market_spread": 9.0, "favorite": "PHX"},
    {"date": "2026-03-12", "away": "PHI", "away_score": 109, "home": "DET", "home_score": 131, "market_total": 224.0, "market_spread": 15.0, "favorite": "DET"},
    {"date": "2026-03-12", "away": "MIL", "away_score": 105, "home": "MIA", "home_score": 112, "market_total": 234.0, "market_spread": 5.5, "favorite": "MIA"},

    # ===== Mar 13, 2026 - 4 games =====
    {"date": "2026-03-13", "away": "MEM", "away_score": 110, "home": "DET", "home_score": 126, "market_total": 232.0, "market_spread": 16.5, "favorite": "DET"},
    {"date": "2026-03-13", "away": "CLE", "away_score": 138, "home": "DAL", "home_score": 105, "market_total": 236.0, "market_spread": 13.0, "favorite": "CLE"},
    {"date": "2026-03-13", "away": "PHX", "away_score": 115, "home": "TOR", "home_score": 122, "market_total": 220.5, "market_spread": 5.5, "favorite": "TOR"},
    {"date": "2026-03-13", "away": "NYK", "away_score": 101, "home": "IND", "home_score": 92, "market_total": 228.0, "market_spread": 12.5, "favorite": "NYK"},

    # ===== Mar 14, 2026 - 4 games =====
    {"date": "2026-03-14", "away": "BKN", "away_score": 97, "home": "PHI", "home_score": 104, "market_total": 217.0, "market_spread": 9.0, "favorite": "PHI"},
    {"date": "2026-03-14", "away": "MIL", "away_score": 99, "home": "ATL", "home_score": 122, "market_total": 228.0, "market_spread": 11.0, "favorite": "ATL"},
    {"date": "2026-03-14", "away": "CHA", "away_score": 102, "home": "SAS", "home_score": 115, "market_total": 232.0, "market_spread": 6.0, "favorite": "SAS"},
    {"date": "2026-03-14", "away": "WAS", "away_score": 100, "home": "BOS", "home_score": 111, "market_total": 233.0, "market_spread": 20.5, "favorite": "BOS"},

    # ===== Mar 16, 2026 - 4 games =====
    {"date": "2026-03-16", "away": "GSW", "away_score": 125, "home": "WAS", "home_score": 117, "market_total": 234.5, "market_spread": 7.5, "favorite": "GSW"},
    {"date": "2026-03-16", "away": "ORL", "away_score": 112, "home": "ATL", "home_score": 124, "market_total": 232.0, "market_spread": 3.5, "favorite": "ATL"},
    {"date": "2026-03-16", "away": "PHX", "away_score": 112, "home": "BOS", "home_score": 122, "market_total": 216.5, "market_spread": 9.0, "favorite": "BOS"},
    {"date": "2026-03-16", "away": "POR", "away_score": 114, "home": "BKN", "home_score": 95, "market_total": 221.0, "market_spread": 11.5, "favorite": "POR"},

    # ===== Mar 17, 2026 - 4 games =====
    {"date": "2026-03-17", "away": "DET", "away_score": 130, "home": "WAS", "home_score": 117, "market_total": 233.5, "market_spread": 19.5, "favorite": "DET"},
    {"date": "2026-03-17", "away": "MIA", "away_score": 106, "home": "CHA", "home_score": 136, "market_total": 236.5, "market_spread": 5.0, "favorite": "CHA"},
    {"date": "2026-03-17", "away": "OKC", "away_score": 113, "home": "ORL", "home_score": 108, "market_total": 224.5, "market_spread": 10.0, "favorite": "OKC"},
    {"date": "2026-03-17", "away": "IND", "away_score": 110, "home": "NYK", "home_score": 136, "market_total": 222.5, "market_spread": 14.0, "favorite": "NYK"},
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
