#!/usr/bin/env python3
"""Add NBA games from Mar 30 - Apr 13, 2026 with real closing lines from Covers.com"""
import json

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

# Covers.com abbreviations -> standard abbreviations
COVERS_TO_STD = {
    "NY": "NYK", "NO": "NOP", "SA": "SAS", "BK": "BKN", "GS": "GSW", "PHO": "PHX",
    "LA": "LAC",  # context-dependent, handled manually
}

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
    # ===== Mar 30, 2026 - 4 games =====
    {"date": "2026-03-30", "away": "PHI", "away_score": 109, "home": "MIA", "home_score": 119, "market_total": 242.5, "market_spread": 2.5, "favorite": "MIA"},
    {"date": "2026-03-30", "away": "BOS", "away_score": 102, "home": "ATL", "home_score": 112, "market_total": 226.0, "market_spread": 3.0, "favorite": "ATL"},
    {"date": "2026-03-30", "away": "PHX", "away_score": 131, "home": "MEM", "home_score": 105, "market_total": 228.0, "market_spread": 12.5, "favorite": "PHX"},
    {"date": "2026-03-30", "away": "CHI", "away_score": 114, "home": "SAS", "home_score": 129, "market_total": 246.5, "market_spread": 18.0, "favorite": "SAS"},

    # ===== Mar 31, 2026 - 7 games =====
    {"date": "2026-03-31", "away": "PHX", "away_score": 111, "home": "ORL", "home_score": 115, "market_total": 225.0, "market_spread": 2.5, "favorite": "ORL"},
    {"date": "2026-03-31", "away": "CHA", "away_score": 117, "home": "BKN", "home_score": 86, "market_total": 219.5, "market_spread": 18.5, "favorite": "CHA"},
    {"date": "2026-03-31", "away": "DAL", "away_score": 99, "home": "MIL", "home_score": 123, "market_total": 231.0, "market_spread": 3.0, "favorite": "MIL"},
    {"date": "2026-03-31", "away": "TOR", "away_score": 116, "home": "DET", "home_score": 127, "market_total": 220.5, "market_spread": 3.5, "favorite": "DET"},
    {"date": "2026-03-31", "away": "NYK", "away_score": 94, "home": "HOU", "home_score": 111, "market_total": 218.5, "market_spread": 1.0, "favorite": "HOU"},
    {"date": "2026-03-31", "away": "CLE", "away_score": 113, "home": "LAL", "home_score": 127, "market_total": 236.0, "market_spread": 2.0, "favorite": "LAL"},
    {"date": "2026-03-31", "away": "POR", "away_score": 114, "home": "LAC", "home_score": 104, "market_total": 226.0, "market_spread": 4.5, "favorite": "POR"},

    # ===== Apr 1, 2026 - 9 games =====
    {"date": "2026-04-01", "away": "PHI", "away_score": 153, "home": "WAS", "home_score": 131, "market_total": 238.5, "market_spread": 14.5, "favorite": "PHI"},
    {"date": "2026-04-01", "away": "ATL", "away_score": 130, "home": "ORL", "home_score": 101, "market_total": 235.5, "market_spread": 2.5, "favorite": "ATL"},
    {"date": "2026-04-01", "away": "BOS", "away_score": 147, "home": "MIA", "home_score": 129, "market_total": 230.0, "market_spread": 4.5, "favorite": "BOS"},
    {"date": "2026-04-01", "away": "SAC", "away_score": 123, "home": "TOR", "home_score": 115, "market_total": 228.5, "market_spread": 12.5, "favorite": "SAC"},
    {"date": "2026-04-01", "away": "NYK", "away_score": 130, "home": "MEM", "home_score": 119, "market_total": 225.5, "market_spread": 13.5, "favorite": "NYK"},
    {"date": "2026-04-01", "away": "IND", "away_score": 145, "home": "CHI", "home_score": 126, "market_total": 246.5, "market_spread": 4.0, "favorite": "IND"},
    {"date": "2026-04-01", "away": "MIL", "away_score": 113, "home": "HOU", "home_score": 119, "market_total": 216.5, "market_spread": 19.5, "favorite": "HOU"},
    {"date": "2026-04-01", "away": "DEN", "away_score": 130, "home": "UTA", "home_score": 117, "market_total": 249.5, "market_spread": 17.0, "favorite": "DEN"},
    {"date": "2026-04-01", "away": "SAS", "away_score": 127, "home": "GSW", "home_score": 113, "market_total": 228.5, "market_spread": 14.5, "favorite": "SAS"},

    # ===== Apr 2, 2026 - 6 games =====
    {"date": "2026-04-02", "away": "MIN", "away_score": 108, "home": "DET", "home_score": 113, "market_total": 221.0, "market_spread": 5.5, "favorite": "DET"},
    {"date": "2026-04-02", "away": "PHX", "away_score": 107, "home": "CHA", "home_score": 127, "market_total": 228.0, "market_spread": 5.5, "favorite": "CHA"},
    {"date": "2026-04-02", "away": "LAL", "away_score": 96, "home": "OKC", "home_score": 139, "market_total": 233.0, "market_spread": 9.0, "favorite": "OKC"},
    {"date": "2026-04-02", "away": "CLE", "away_score": 118, "home": "GSW", "home_score": 111, "market_total": 229.5, "market_spread": 10.0, "favorite": "CLE"},
    {"date": "2026-04-02", "away": "NOP", "away_score": 106, "home": "POR", "home_score": 118, "market_total": 235.0, "market_spread": 5.5, "favorite": "POR"},
    {"date": "2026-04-02", "away": "SAS", "away_score": 118, "home": "LAC", "home_score": 99, "market_total": 231.5, "market_spread": 2.5, "favorite": "SAS"},

    # ===== Apr 3, 2026 - 9 games =====
    {"date": "2026-04-03", "away": "IND", "away_score": 108, "home": "CHA", "home_score": 129, "market_total": 234.5, "market_spread": 15.5, "favorite": "CHA"},
    {"date": "2026-04-03", "away": "MIN", "away_score": 103, "home": "PHI", "home_score": 115, "market_total": 234.5, "market_spread": 3.5, "favorite": "PHI"},
    {"date": "2026-04-03", "away": "CHI", "away_score": 96, "home": "NYK", "home_score": 136, "market_total": 236.5, "market_spread": 13.5, "favorite": "NYK"},
    {"date": "2026-04-03", "away": "ATL", "away_score": 141, "home": "BKN", "home_score": 107, "market_total": 225.0, "market_spread": 16.5, "favorite": "ATL"},
    {"date": "2026-04-03", "away": "UTA", "away_score": 106, "home": "HOU", "home_score": 140, "market_total": 233.0, "market_spread": 18.5, "favorite": "HOU"},
    {"date": "2026-04-03", "away": "BOS", "away_score": 133, "home": "MIL", "home_score": 101, "market_total": 218.0, "market_spread": 17.5, "favorite": "BOS"},
    {"date": "2026-04-03", "away": "TOR", "away_score": 128, "home": "MEM", "home_score": 96, "market_total": 234.5, "market_spread": 15.0, "favorite": "TOR"},
    {"date": "2026-04-03", "away": "ORL", "away_score": 138, "home": "DAL", "home_score": 127, "market_total": 240.0, "market_spread": 7.0, "favorite": "ORL"},
    {"date": "2026-04-03", "away": "NOP", "away_score": 113, "home": "SAC", "home_score": 117, "market_total": 232.5, "market_spread": 6.5, "favorite": "SAC"},

    # ===== Apr 4, 2026 - 3 games =====
    {"date": "2026-04-04", "away": "SAS", "away_score": 134, "home": "DEN", "home_score": 136, "market_total": 244.0, "market_spread": 2.0, "favorite": "DEN"},
    {"date": "2026-04-04", "away": "WAS", "away_score": 136, "home": "MIA", "home_score": 152, "market_total": 246.0, "market_spread": 18.0, "favorite": "MIA"},
    {"date": "2026-04-04", "away": "DET", "away_score": 116, "home": "PHI", "home_score": 93, "market_total": 226.0, "market_spread": 3.5, "favorite": "DET"},

    # ===== Apr 5, 2026 - 11 games =====
    {"date": "2026-04-05", "away": "WAS", "away_score": 115, "home": "BKN", "home_score": 121, "market_total": 230.5, "market_spread": 3.0, "favorite": "BKN"},
    {"date": "2026-04-05", "away": "MEM", "away_score": 115, "home": "MIL", "home_score": 131, "market_total": 230.5, "market_spread": 7.5, "favorite": "MIL"},
    {"date": "2026-04-05", "away": "PHX", "away_score": 120, "home": "CHI", "home_score": 110, "market_total": 242.5, "market_spread": 11.5, "favorite": "PHX"},
    {"date": "2026-04-05", "away": "TOR", "away_score": 101, "home": "BOS", "home_score": 115, "market_total": 220.5, "market_spread": 9.0, "favorite": "BOS"},
    {"date": "2026-04-05", "away": "IND", "away_score": 108, "home": "CLE", "home_score": 117, "market_total": 239.5, "market_spread": 16.5, "favorite": "CLE"},
    {"date": "2026-04-05", "away": "UTA", "away_score": 111, "home": "OKC", "home_score": 146, "market_total": 240.5, "market_spread": 25.0, "favorite": "OKC"},
    {"date": "2026-04-05", "away": "ORL", "away_score": 112, "home": "NOP", "home_score": 108, "market_total": 237.0, "market_spread": 6.5, "favorite": "ORL"},
    {"date": "2026-04-05", "away": "CHA", "away_score": 122, "home": "MIN", "home_score": 108, "market_total": 226.5, "market_spread": 5.0, "favorite": "CHA"},
    {"date": "2026-04-05", "away": "LAL", "away_score": 128, "home": "DAL", "home_score": 134, "market_total": 235.0, "market_spread": 1.5, "favorite": "DAL"},
    {"date": "2026-04-05", "away": "LAC", "away_score": 138, "home": "SAC", "home_score": 109, "market_total": 228.0, "market_spread": 13.5, "favorite": "LAC"},
    {"date": "2026-04-05", "away": "HOU", "away_score": 117, "home": "GSW", "home_score": 116, "market_total": 228.5, "market_spread": 4.0, "favorite": "HOU"},

    # ===== Apr 6, 2026 - 5 games =====
    {"date": "2026-04-06", "away": "NYK", "away_score": 108, "home": "ATL", "home_score": 105, "market_total": 226.5, "market_spread": 1.5, "favorite": "NYK"},
    {"date": "2026-04-06", "away": "DET", "away_score": 107, "home": "ORL", "home_score": 123, "market_total": 223.0, "market_spread": 1.0, "favorite": "ORL"},
    {"date": "2026-04-06", "away": "CLE", "away_score": 142, "home": "MEM", "home_score": 126, "market_total": 232.0, "market_spread": 13.5, "favorite": "CLE"},
    {"date": "2026-04-06", "away": "PHI", "away_score": 102, "home": "SAS", "home_score": 115, "market_total": 237.5, "market_spread": 8.5, "favorite": "SAS"},
    {"date": "2026-04-06", "away": "POR", "away_score": 132, "home": "DEN", "home_score": 137, "market_total": 236.0, "market_spread": 7.0, "favorite": "DEN"},

    # ===== Apr 7, 2026 - 9 games =====
    {"date": "2026-04-07", "away": "MIN", "away_score": 124, "home": "IND", "home_score": 104, "market_total": 235.0, "market_spread": 12.5, "favorite": "MIN"},
    {"date": "2026-04-07", "away": "CHI", "away_score": 129, "home": "WAS", "home_score": 98, "market_total": 249.0, "market_spread": 6.5, "favorite": "CHI"},
    {"date": "2026-04-07", "away": "MIA", "away_score": 95, "home": "TOR", "home_score": 121, "market_total": 241.5, "market_spread": 2.5, "favorite": "TOR"},
    {"date": "2026-04-07", "away": "MIL", "away_score": 90, "home": "BKN", "home_score": 96, "market_total": 217.5, "market_spread": 1.5, "favorite": "BKN"},
    {"date": "2026-04-07", "away": "CHA", "away_score": 102, "home": "BOS", "home_score": 113, "market_total": 221.5, "market_spread": 4.5, "favorite": "BOS"},
    {"date": "2026-04-07", "away": "UTA", "away_score": 137, "home": "NOP", "home_score": 156, "market_total": 243.0, "market_spread": 6.0, "favorite": "NOP"},
    {"date": "2026-04-07", "away": "SAC", "away_score": 105, "home": "GSW", "home_score": 110, "market_total": 233.5, "market_spread": 15.5, "favorite": "GSW"},
    {"date": "2026-04-07", "away": "OKC", "away_score": 123, "home": "LAL", "home_score": 87, "market_total": 221.0, "market_spread": 18.0, "favorite": "OKC"},
    {"date": "2026-04-07", "away": "DAL", "away_score": 103, "home": "LAC", "home_score": 116, "market_total": 235.5, "market_spread": 12.0, "favorite": "LAC"},
    # HOU @ PHO - HOU -1.5, total 223
    {"date": "2026-04-07", "away": "HOU", "away_score": 119, "home": "PHX", "home_score": 105, "market_total": 223.0, "market_spread": 1.5, "favorite": "HOU"},

    # ===== Apr 8, 2026 - 8 games =====
    {"date": "2026-04-08", "away": "MIN", "away_score": 120, "home": "ORL", "home_score": 132, "market_total": 233.5, "market_spread": 12.0, "favorite": "ORL"},
    {"date": "2026-04-08", "away": "MIL", "away_score": 111, "home": "DET", "home_score": 137, "market_total": 222.5, "market_spread": 22.0, "favorite": "DET"},
    {"date": "2026-04-08", "away": "ATL", "away_score": 116, "home": "CLE", "home_score": 122, "market_total": 237.0, "market_spread": 4.5, "favorite": "CLE"},
    {"date": "2026-04-08", "away": "MEM", "away_score": 119, "home": "DEN", "home_score": 136, "market_total": 247.0, "market_spread": 23.5, "favorite": "DEN"},
    {"date": "2026-04-08", "away": "POR", "away_score": 101, "home": "SAS", "home_score": 112, "market_total": 230.0, "market_spread": 3.0, "favorite": "SAS"},
    {"date": "2026-04-08", "away": "DAL", "away_score": 107, "home": "PHX", "home_score": 112, "market_total": 233.5, "market_spread": 12.5, "favorite": "PHX"},
    {"date": "2026-04-08", "away": "OKC", "away_score": 128, "home": "LAC", "home_score": 110, "market_total": 224.0, "market_spread": 8.5, "favorite": "OKC"},
    # Note: Apr 8 had additional games not captured in chunk 1 (likely NYK, BOS, etc.)

    # ===== Apr 9, 2026 - 6 games =====
    {"date": "2026-04-09", "away": "CHI", "away_score": 119, "home": "WAS", "home_score": 108, "market_total": 249.0, "market_spread": 6.5, "favorite": "CHI"},
    {"date": "2026-04-09", "away": "MIA", "away_score": 114, "home": "TOR", "home_score": 128, "market_total": 236.5, "market_spread": 4.5, "favorite": "TOR"},
    {"date": "2026-04-09", "away": "BOS", "away_score": 106, "home": "NYK", "home_score": 112, "market_total": 211.0, "market_spread": 4.0, "favorite": "NYK"},
    {"date": "2026-04-09", "away": "IND", "away_score": 123, "home": "BKN", "home_score": 94, "market_total": 225.5, "market_spread": 3.0, "favorite": "IND"},
    {"date": "2026-04-09", "away": "PHI", "away_score": 102, "home": "HOU", "home_score": 113, "market_total": 226.5, "market_spread": 6.0, "favorite": "HOU"},
    {"date": "2026-04-09", "away": "LAL", "away_score": 119, "home": "GSW", "home_score": 103, "market_total": 222.5, "market_spread": 1.5, "favorite": "LAL"},

    # ===== Apr 10, 2026 - 11 games =====
    {"date": "2026-04-10", "away": "DET", "away_score": 118, "home": "CHA", "home_score": 100, "market_total": 225.5, "market_spread": 5.5, "favorite": "DET"},
    {"date": "2026-04-10", "away": "CLE", "away_score": 102, "home": "ATL", "home_score": 124, "market_total": 233.0, "market_spread": 8.0, "favorite": "ATL"},
    {"date": "2026-04-10", "away": "MIA", "away_score": 140, "home": "WAS", "home_score": 117, "market_total": 243.5, "market_spread": 16.0, "favorite": "MIA"},
    {"date": "2026-04-10", "away": "NOP", "away_score": 118, "home": "BOS", "home_score": 144, "market_total": 227.0, "market_spread": 18.0, "favorite": "BOS"},
    {"date": "2026-04-10", "away": "PHI", "away_score": 105, "home": "IND", "home_score": 94, "market_total": 234.5, "market_spread": 15.0, "favorite": "PHI"},
    {"date": "2026-04-10", "away": "TOR", "away_score": 95, "home": "NYK", "home_score": 112, "market_total": 219.0, "market_spread": 6.5, "favorite": "NYK"},
    {"date": "2026-04-10", "away": "BKN", "away_score": 108, "home": "MIL", "home_score": 125, "market_total": 218.0, "market_spread": 10.0, "favorite": "MIL"},
    {"date": "2026-04-10", "away": "ORL", "away_score": 127, "home": "CHI", "home_score": 103, "market_total": 246.5, "market_spread": 15.5, "favorite": "ORL"},
    {"date": "2026-04-10", "away": "DAL", "away_score": 120, "home": "SAS", "home_score": 139, "market_total": 236.0, "market_spread": 18.0, "favorite": "SAS"},
    {"date": "2026-04-10", "away": "OKC", "away_score": 107, "home": "DEN", "home_score": 127, "market_total": 223.5, "market_spread": 2.5, "favorite": "DEN"},
    {"date": "2026-04-10", "away": "MIN", "away_score": 136, "home": "HOU", "home_score": 132, "market_total": 228.0, "market_spread": 9.5, "favorite": "MIN"},

    # ===== Apr 11, 2026 - 4 games (same as Apr 12 data - likely Saturday games) =====
    # These are the same games as Apr 12 - Covers.com shows them for both dates
    # Using Apr 11 as the actual date since the calendar shows Apr 11 as Saturday
    {"date": "2026-04-11", "away": "MIL", "away_score": 106, "home": "PHI", "home_score": 126, "market_total": 224.5, "market_spread": 16.0, "favorite": "PHI"},
    {"date": "2026-04-11", "away": "ORL", "away_score": 108, "home": "BOS", "home_score": 113, "market_total": 222.0, "market_spread": 13.0, "favorite": "BOS"},
    {"date": "2026-04-11", "away": "ATL", "away_score": 117, "home": "MIA", "home_score": 143, "market_total": 240.5, "market_spread": 10.5, "favorite": "MIA"},
    {"date": "2026-04-11", "away": "BKN", "away_score": 101, "home": "TOR", "home_score": 136, "market_total": 218.5, "market_spread": 24.0, "favorite": "TOR"},
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
