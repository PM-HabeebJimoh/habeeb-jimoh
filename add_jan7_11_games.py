#!/usr/bin/env python3
"""Add NBA games from Jan 7-11, 2026 with real closing lines from Covers.com"""
import json
import os

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_games(data, new_games):
    """Add games avoiding duplicates based on date+away+home"""
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

# Games extracted from Covers.com
# Format: date, away, away_score, home, home_score, market_total, market_spread, favorite
# Covers.com abbreviations mapped to standard: NO=NOP, BK=BKN, NY=NYK, GS=GSW, SA=SAS, PHO=PHX, LA (context-dependent)

new_games = [
    # Jan 7, 2026 - 11 games
    {"date": "2026-01-07", "away": "CHI", "away_score": 93, "home": "DET", "home_score": 108, "market_total": 227.0, "market_spread": 8.0, "favorite": "DET"},
    {"date": "2026-01-07", "away": "DEN", "away_score": 114, "home": "BOS", "home_score": 110, "market_total": 229.5, "market_spread": 9.5, "favorite": "BOS"},
    {"date": "2026-01-07", "away": "TOR", "away_score": 97, "home": "CHA", "home_score": 96, "market_total": 229.5, "market_spread": 2.0, "favorite": "TOR"},
    {"date": "2026-01-07", "away": "WAS", "away_score": 110, "home": "PHI", "home_score": 131, "market_total": 234.0, "market_spread": 16.0, "favorite": "PHI"},
    {"date": "2026-01-07", "away": "ORL", "away_score": 104, "home": "BKN", "home_score": 103, "market_total": 221.0, "market_spread": 2.5, "favorite": "ORL"},
    {"date": "2026-01-07", "away": "NOP", "away_score": 100, "home": "ATL", "home_score": 117, "market_total": 247.0, "market_spread": 10.5, "favorite": "ATL"},
    {"date": "2026-01-07", "away": "LAC", "away_score": 111, "home": "NYK", "home_score": 123, "market_total": 223.0, "market_spread": 5.5, "favorite": "NYK"},
    {"date": "2026-01-07", "away": "UTA", "away_score": 125, "home": "OKC", "home_score": 129, "market_total": 243.5, "market_spread": 19.5, "favorite": "OKC"},
    {"date": "2026-01-07", "away": "PHX", "away_score": 117, "home": "MEM", "home_score": 98, "market_total": 231.5, "market_spread": 6.0, "favorite": "PHX"},
    {"date": "2026-01-07", "away": "LAL", "away_score": 91, "home": "SAS", "home_score": 107, "market_total": 233.5, "market_spread": 8.5, "favorite": "SAS"},
    {"date": "2026-01-07", "away": "MIL", "away_score": 113, "home": "GSW", "home_score": 120, "market_total": 228.0, "market_spread": 6.5, "favorite": "GSW"},
    
    # Jan 8, 2026 - 3 completed games (MIA@CHI was upcoming/not played)
    {"date": "2026-01-08", "away": "IND", "away_score": 114, "home": "CHA", "home_score": 112, "market_total": 233.0, "market_spread": 4.0, "favorite": "CHA"},
    {"date": "2026-01-08", "away": "CLE", "away_score": 122, "home": "MIN", "home_score": 131, "market_total": 239.5, "market_spread": 2.5, "favorite": "MIN"},
    {"date": "2026-01-08", "away": "DAL", "away_score": 114, "home": "UTA", "home_score": 116, "market_total": 243.5, "market_spread": 5.0, "favorite": "DAL"},
    
    # Jan 9, 2026 - 10 games
    {"date": "2026-01-09", "away": "PHI", "away_score": 103, "home": "ORL", "home_score": 91, "market_total": 227.0, "market_spread": 3.5, "favorite": "PHI"},
    {"date": "2026-01-09", "away": "TOR", "away_score": 117, "home": "BOS", "home_score": 125, "market_total": 223.5, "market_spread": 9.5, "favorite": "BOS"},
    {"date": "2026-01-09", "away": "NOP", "away_score": 128, "home": "WAS", "home_score": 107, "market_total": 244.0, "market_spread": 3.0, "favorite": "NOP"},
    {"date": "2026-01-09", "away": "LAC", "away_score": 121, "home": "BKN", "home_score": 105, "market_total": 215.0, "market_spread": 6.0, "favorite": "LAC"},
    {"date": "2026-01-09", "away": "OKC", "away_score": 117, "home": "MEM", "home_score": 116, "market_total": 230.0, "market_spread": 6.0, "favorite": "OKC"},
    {"date": "2026-01-09", "away": "NYK", "away_score": 107, "home": "PHX", "home_score": 112, "market_total": 229.0, "market_spread": 1.0, "favorite": "NYK"},
    {"date": "2026-01-09", "away": "ATL", "away_score": 110, "home": "DEN", "home_score": 87, "market_total": 229.5, "market_spread": 3.0, "favorite": "ATL"},
    {"date": "2026-01-09", "away": "SAC", "away_score": 103, "home": "GSW", "home_score": 137, "market_total": 231.5, "market_spread": 15.0, "favorite": "GSW"},
    {"date": "2026-01-09", "away": "HOU", "away_score": 105, "home": "POR", "home_score": 111, "market_total": 222.5, "market_spread": 7.0, "favorite": "HOU"},
    {"date": "2026-01-09", "away": "MIL", "away_score": 105, "home": "LAL", "home_score": 101, "market_total": 228.5, "market_spread": 3.0, "favorite": "LAL"},
    
    # Jan 11, 2026 - 4 games (from chunk 0)
    {"date": "2026-01-11", "away": "NOP", "away_score": 118, "home": "ORL", "home_score": 128, "market_total": 236.5, "market_spread": 7.5, "favorite": "ORL"},
    {"date": "2026-01-11", "away": "BKN", "away_score": 98, "home": "MEM", "home_score": 103, "market_total": 221.5, "market_spread": 7.5, "favorite": "MEM"},
    {"date": "2026-01-11", "away": "NYK", "away_score": 123, "home": "POR", "home_score": 114, "market_total": 230.5, "market_spread": 5.0, "favorite": "NYK"},
    {"date": "2026-01-11", "away": "PHI", "away_score": 115, "home": "TOR", "home_score": 116, "market_total": 220.0, "market_spread": 1.0, "favorite": "PHI"},
]

def main():
    data = load_data()
    before = len(data['nba'])
    added = add_games(data, new_games)
    after = len(data['nba'])
    
    # Sort by date
    data['nba'].sort(key=lambda g: (g['date'], g['away']))
    
    save_data(data)
    print(f"Added {added} new NBA games ({before} → {after})")
    print(f"Total NBA games: {after}")

if __name__ == "__main__":
    main()
