#!/usr/bin/env python3
"""Add NBA games from Feb 8-26, 2026 with real closing lines from Covers.com"""
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
    # ===== Feb 8, 2026 - 4 games =====
    {"date": "2026-02-08", "away": "NYK", "away_score": 111, "home": "BOS", "home_score": 89, "market_total": 213.0, "market_spread": 3.5, "favorite": "BOS"},
    {"date": "2026-02-08", "away": "MIA", "away_score": 132, "home": "WAS", "home_score": 101, "market_total": 236.0, "market_spread": 13.5, "favorite": "MIA"},
    {"date": "2026-02-08", "away": "IND", "away_score": 104, "home": "TOR", "home_score": 122, "market_total": 226.5, "market_spread": 8.5, "favorite": "TOR"},
    {"date": "2026-02-08", "away": "LAC", "away_score": 115, "home": "MIN", "home_score": 96, "market_total": 222.0, "market_spread": 8.5, "favorite": "MIN"},

    # ===== Feb 9, 2026 - 4 games =====
    {"date": "2026-02-09", "away": "DET", "away_score": 110, "home": "CHA", "home_score": 104, "market_total": 222.5, "market_spread": 2.5, "favorite": "DET"},
    {"date": "2026-02-09", "away": "UTA", "away_score": 115, "home": "MIA", "home_score": 111, "market_total": 236.0, "market_spread": 6.0, "favorite": "MIA"},
    {"date": "2026-02-09", "away": "MIL", "away_score": 99, "home": "ORL", "home_score": 118, "market_total": 220.5, "market_spread": 9.5, "favorite": "ORL"},
    {"date": "2026-02-09", "away": "CHI", "away_score": 115, "home": "BKN", "home_score": 123, "market_total": 219.0, "market_spread": 3.5, "favorite": "CHI"},

    # ===== Feb 11, 2026 - 11 games =====
    {"date": "2026-02-11", "away": "WAS", "away_score": 113, "home": "CLE", "home_score": 138, "market_total": 239.0, "market_spread": 17.5, "favorite": "CLE"},
    {"date": "2026-02-11", "away": "MIL", "away_score": 116, "home": "ORL", "home_score": 108, "market_total": 220.0, "market_spread": 11.0, "favorite": "ORL"},
    {"date": "2026-02-11", "away": "ATL", "away_score": 107, "home": "CHA", "home_score": 110, "market_total": 235.5, "market_spread": 2.0, "favorite": "CHA"},
    {"date": "2026-02-11", "away": "DET", "away_score": 113, "home": "TOR", "home_score": 95, "market_total": 223.5, "market_spread": 1.0, "favorite": "TOR"},
    {"date": "2026-02-11", "away": "IND", "away_score": 115, "home": "BKN", "home_score": 110, "market_total": 215.5, "market_spread": 6.5, "favorite": "BKN"},
    {"date": "2026-02-11", "away": "CHI", "away_score": 105, "home": "BOS", "home_score": 124, "market_total": 227.0, "market_spread": 14.0, "favorite": "BOS"},
    {"date": "2026-02-11", "away": "NYK", "away_score": 138, "home": "PHI", "home_score": 89, "market_total": 225.0, "market_spread": 2.5, "favorite": "NYK"},
    {"date": "2026-02-11", "away": "MIA", "away_score": 123, "home": "NOP", "home_score": 111, "market_total": 233.5, "market_spread": 2.0, "favorite": "NOP"},
    {"date": "2026-02-11", "away": "LAC", "away_score": 105, "home": "HOU", "home_score": 102, "market_total": 212.5, "market_spread": 8.5, "favorite": "HOU"},
    {"date": "2026-02-11", "away": "POR", "away_score": 109, "home": "MIN", "home_score": 133, "market_total": 238.0, "market_spread": 7.5, "favorite": "MIN"},
    {"date": "2026-02-11", "away": "MEM", "away_score": 116, "home": "DEN", "home_score": 122, "market_total": 239.5, "market_spread": 14.0, "favorite": "DEN"},

    # ===== Feb 21, 2026 - 6 games =====
    {"date": "2026-02-21", "away": "ORL", "away_score": 110, "home": "PHX", "home_score": 113, "market_total": 218.5, "market_spread": 3.5, "favorite": "PHX"},
    {"date": "2026-02-21", "away": "PHI", "away_score": 111, "home": "NOP", "home_score": 126, "market_total": 235.0, "market_spread": 4.0, "favorite": "PHI"},
    {"date": "2026-02-21", "away": "DET", "away_score": 126, "home": "CHI", "home_score": 110, "market_total": 234.5, "market_spread": 10.5, "favorite": "DET"},
    {"date": "2026-02-21", "away": "SAC", "away_score": 122, "home": "SAS", "home_score": 139, "market_total": 230.5, "market_spread": 18.5, "favorite": "SAS"},
    {"date": "2026-02-21", "away": "MEM", "away_score": 120, "home": "MIA", "home_score": 136, "market_total": 238.0, "market_spread": 12.0, "favorite": "MIA"},
    {"date": "2026-02-21", "away": "HOU", "away_score": 106, "home": "NYK", "home_score": 108, "market_total": 220.5, "market_spread": 3.5, "favorite": "NYK"},

    # ===== Feb 22, 2026 - 11 games =====
    {"date": "2026-02-22", "away": "CLE", "away_score": 113, "home": "OKC", "home_score": 121, "market_total": 228.0, "market_spread": 4.0, "favorite": "CLE"},
    {"date": "2026-02-22", "away": "DEN", "away_score": 117, "home": "GSW", "home_score": 128, "market_total": 228.5, "market_spread": 6.0, "favorite": "DEN"},
    {"date": "2026-02-22", "away": "BKN", "away_score": 104, "home": "ATL", "home_score": 115, "market_total": 228.0, "market_spread": 9.5, "favorite": "ATL"},
    {"date": "2026-02-22", "away": "TOR", "away_score": 122, "home": "MIL", "home_score": 94, "market_total": 219.0, "market_spread": 4.0, "favorite": "TOR"},
    {"date": "2026-02-22", "away": "DAL", "away_score": 134, "home": "IND", "home_score": 130, "market_total": 237.5, "market_spread": 1.0, "favorite": "DAL"},
    {"date": "2026-02-22", "away": "CHA", "away_score": 129, "home": "WAS", "home_score": 112, "market_total": 224.5, "market_spread": 10.5, "favorite": "CHA"},
    {"date": "2026-02-22", "away": "BOS", "away_score": 111, "home": "LAL", "home_score": 89, "market_total": 230.5, "market_spread": 1.0, "favorite": "BOS"},
    {"date": "2026-02-22", "away": "PHI", "away_score": 135, "home": "MIN", "home_score": 108, "market_total": 239.0, "market_spread": 9.5, "favorite": "MIN"},
    {"date": "2026-02-22", "away": "NYK", "away_score": 105, "home": "CHI", "home_score": 99, "market_total": 234.0, "market_spread": 9.0, "favorite": "NYK"},
    {"date": "2026-02-22", "away": "POR", "away_score": 92, "home": "PHX", "home_score": 77, "market_total": 225.0, "market_spread": 3.5, "favorite": "POR"},
    {"date": "2026-02-22", "away": "ORL", "away_score": 113, "home": "LAC", "home_score": 109, "market_total": 215.5, "market_spread": 4.0, "favorite": "LAC"},

    # ===== Feb 23, 2026 - 3 games =====
    {"date": "2026-02-23", "away": "SAS", "away_score": 114, "home": "DET", "home_score": 103, "market_total": 232.5, "market_spread": 1.5, "favorite": "DET"},
    {"date": "2026-02-23", "away": "SAC", "away_score": 123, "home": "MEM", "home_score": 114, "market_total": 233.5, "market_spread": 2.5, "favorite": "MEM"},
    {"date": "2026-02-23", "away": "UTA", "away_score": 105, "home": "HOU", "home_score": 125, "market_total": 228.0, "market_spread": 13.5, "favorite": "HOU"},

    # ===== Feb 24, 2026 - 4 games =====
    {"date": "2026-02-24", "away": "PHI", "away_score": 135, "home": "IND", "home_score": 114, "market_total": 234.0, "market_spread": 11.0, "favorite": "PHI"},
    {"date": "2026-02-24", "away": "NYK", "away_score": 94, "home": "CLE", "home_score": 109, "market_total": 231.5, "market_spread": 4.0, "favorite": "CLE"},
    {"date": "2026-02-24", "away": "WAS", "away_score": 98, "home": "ATL", "home_score": 119, "market_total": 236.5, "market_spread": 12.0, "favorite": "ATL"},
    {"date": "2026-02-24", "away": "DAL", "away_score": 123, "home": "BKN", "home_score": 114, "market_total": 226.5, "market_spread": 1.5, "favorite": "DAL"},

    # ===== Feb 25, 2026 - 4 games =====
    {"date": "2026-02-25", "away": "SAS", "away_score": 110, "home": "TOR", "home_score": 107, "market_total": 230.5, "market_spread": 6.0, "favorite": "SAS"},
    {"date": "2026-02-25", "away": "GSW", "away_score": 133, "home": "MEM", "home_score": 112, "market_total": 226.5, "market_spread": 4.0, "favorite": "GSW"},
    {"date": "2026-02-25", "away": "OKC", "away_score": 116, "home": "DET", "home_score": 124, "market_total": 221.0, "market_spread": 10.5, "favorite": "DET"},
    {"date": "2026-02-25", "away": "CLE", "away_score": 116, "home": "MIL", "home_score": 118, "market_total": 221.0, "market_spread": 3.0, "favorite": "CLE"},

    # ===== Feb 26, 2026 - 4 games =====
    {"date": "2026-02-26", "away": "CHA", "away_score": 133, "home": "IND", "home_score": 109, "market_total": 229.5, "market_spread": 12.0, "favorite": "CHA"},
    {"date": "2026-02-26", "away": "MIA", "away_score": 117, "home": "PHI", "home_score": 124, "market_total": 240.5, "market_spread": 2.0, "favorite": "PHI"},
    {"date": "2026-02-26", "away": "SAS", "away_score": 126, "home": "BKN", "home_score": 110, "market_total": 223.5, "market_spread": 10.5, "favorite": "SAS"},
    {"date": "2026-02-26", "away": "WAS", "away_score": 96, "home": "ATL", "home_score": 126, "market_total": 236.0, "market_spread": 10.5, "favorite": "ATL"},
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
