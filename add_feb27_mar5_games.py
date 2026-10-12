#!/usr/bin/env python3
"""Add NBA games from Feb 27-Mar 5, 2026 with real closing lines from Covers.com"""
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
    # ===== Feb 27, 2026 - 4 games =====
    {"date": "2026-02-27", "away": "CLE", "away_score": 119, "home": "DET", "home_score": 122, "market_total": 227.0, "market_spread": 8.5, "favorite": "DET"},
    {"date": "2026-02-27", "away": "BKN", "away_score": 111, "home": "BOS", "home_score": 148, "market_total": 209.5, "market_spread": 16.5, "favorite": "BOS"},
    {"date": "2026-02-27", "away": "NYK", "away_score": 127, "home": "MIL", "home_score": 98, "market_total": 219.5, "market_spread": 8.5, "favorite": "NYK"},
    {"date": "2026-02-27", "away": "MEM", "away_score": 124, "home": "DAL", "home_score": 105, "market_total": 241.5, "market_spread": 5.0, "favorite": "DAL"},

    # ===== Feb 28, 2026 - 4 games =====
    {"date": "2026-02-28", "away": "POR", "away_score": 93, "home": "CHA", "home_score": 109, "market_total": 229.5, "market_spread": 6.5, "favorite": "CHA"},
    {"date": "2026-02-28", "away": "HOU", "away_score": 105, "home": "MIA", "home_score": 115, "market_total": 226.0, "market_spread": 2.0, "favorite": "HOU"},
    {"date": "2026-02-28", "away": "TOR", "away_score": 134, "home": "WAS", "home_score": 125, "market_total": 229.0, "market_spread": 14.0, "favorite": "TOR"},
    {"date": "2026-02-28", "away": "LAL", "away_score": 129, "home": "GSW", "home_score": 101, "market_total": 225.5, "market_spread": 4.0, "favorite": "LAL"},

    # ===== Mar 2, 2026 - 4 games =====
    {"date": "2026-03-02", "away": "HOU", "away_score": 123, "home": "WAS", "home_score": 118, "market_total": 225.5, "market_spread": 14.5, "favorite": "HOU"},
    {"date": "2026-03-02", "away": "BOS", "away_score": 108, "home": "MIL", "home_score": 81, "market_total": 216.0, "market_spread": 2.5, "favorite": "BOS"},
    {"date": "2026-03-02", "away": "DEN", "away_score": 128, "home": "UTA", "home_score": 125, "market_total": 242.0, "market_spread": 11.5, "favorite": "DEN"},
    {"date": "2026-03-02", "away": "LAC", "away_score": 114, "home": "GSW", "home_score": 101, "market_total": 216.5, "market_spread": 1.0, "favorite": "LAC"},

    # ===== Mar 3, 2026 - 4 games =====
    {"date": "2026-03-03", "away": "WAS", "away_score": 109, "home": "ORL", "home_score": 126, "market_total": 228.0, "market_spread": 16.0, "favorite": "ORL"},
    {"date": "2026-03-03", "away": "DET", "away_score": 109, "home": "CLE", "home_score": 113, "market_total": 228.0, "market_spread": 2.5, "favorite": "DET"},
    {"date": "2026-03-03", "away": "DAL", "away_score": 90, "home": "CHA", "home_score": 117, "market_total": 227.0, "market_spread": 13.0, "favorite": "CHA"},
    {"date": "2026-03-03", "away": "BKN", "away_score": 98, "home": "MIA", "home_score": 124, "market_total": 226.0, "market_spread": 12.5, "favorite": "MIA"},

    # ===== Mar 4, 2026 - 4 games =====
    {"date": "2026-03-04", "away": "OKC", "away_score": 103, "home": "NYK", "home_score": 100, "market_total": 221.0, "market_spread": 4.0, "favorite": "OKC"},
    {"date": "2026-03-04", "away": "CHA", "away_score": 118, "home": "BOS", "home_score": 89, "market_total": 215.0, "market_spread": 6.5, "favorite": "BOS"},
    {"date": "2026-03-04", "away": "UTA", "away_score": 102, "home": "PHI", "home_score": 106, "market_total": 238.0, "market_spread": 7.0, "favorite": "PHI"},
    {"date": "2026-03-04", "away": "POR", "away_score": 122, "home": "MEM", "home_score": 114, "market_total": 231.5, "market_spread": 9.5, "favorite": "POR"},

    # ===== Mar 5, 2026 - 6 games =====
    {"date": "2026-03-05", "away": "UTA", "away_score": 122, "home": "WAS", "home_score": 112, "market_total": 241.0, "market_spread": 4.0, "favorite": "WAS"},
    {"date": "2026-03-05", "away": "DAL", "away_score": 114, "home": "ORL", "home_score": 115, "market_total": 229.5, "market_spread": 7.5, "favorite": "ORL"},
    {"date": "2026-03-05", "away": "GSW", "away_score": 115, "home": "HOU", "home_score": 113, "market_total": 214.5, "market_spread": 9.5, "favorite": "HOU"},
    {"date": "2026-03-05", "away": "BKN", "away_score": 110, "home": "MIA", "home_score": 126, "market_total": 225.0, "market_spread": 12.5, "favorite": "MIA"},
    {"date": "2026-03-05", "away": "TOR", "away_score": 107, "home": "MIN", "home_score": 115, "market_total": 227.0, "market_spread": 5.0, "favorite": "MIN"},
    {"date": "2026-03-05", "away": "DET", "away_score": 106, "home": "SAS", "home_score": 121, "market_total": 229.0, "market_spread": 3.0, "favorite": "SAS"},
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
