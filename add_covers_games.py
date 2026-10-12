#!/usr/bin/env python3
"""
Covers.com NBA scraper — batch scraping and parsing.
Processes fetched Covers.com pages and extracts game data.
"""

import re
import json
import os
import sys

COVERS_NBA = {
    "ATL": "ATL", "BOS": "BOS", "BK": "BKN", "BKN": "BKN", "CHA": "CHA",
    "CHI": "CHI", "CLE": "CLE", "DAL": "DAL", "DEN": "DEN", "DET": "DET",
    "GS": "GSW", "GSW": "GSW", "HOU": "HOU", "IND": "IND", "LAC": "LAC",
    "LAL": "LAL", "LA": "LAL", "MEM": "MEM", "MIA": "MIA", "MIL": "MIL",
    "MIN": "MIN", "NOP": "NOP", "NO": "NOP", "NY": "NYK", "NYK": "NYK",
    "OKC": "OKC", "ORL": "ORL", "PHI": "PHI", "PHO": "PHX", "PHX": "PHX",
    "POR": "POR", "SAC": "SAC", "SA": "SAS", "SAS": "SAS", "TOR": "TOR",
    "UTA": "UTA", "WAS": "WAS", "WSH": "WAS",
}


def parse_covers_game_block(block_text, date_str):
    """Parse a single game block from Covers.com page."""
    # Find scores
    score_matches = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', block_text)
    if len(score_matches) < 2:
        return None
    
    # Find "Final" marker
    if '**Final**' not in block_text:
        return None
    
    # Split by "Final" to get away and home scores
    parts = block_text.split('**Final**')
    if len(parts) != 2:
        return None
    
    before_final = parts[0]
    after_final = parts[1]
    
    # Get away team score (last match before Final)
    away_matches = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', before_final)
    if not away_matches:
        return None
    away_abbr, away_score = away_matches[-1]
    
    # Get home team score (first match after Final)
    home_matches = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', after_final)
    if not home_matches:
        return None
    home_abbr, home_score = home_matches[0]
    
    # Find total (under/over)
    total_match = re.search(r'(?:under|over)\s+(\d+\.?\d*)', block_text, re.IGNORECASE)
    if not total_match:
        return None
    total_value = float(total_match.group(1))
    
    # Find spread
    spread_matches = re.findall(r'([A-Z]{2,3})\s+([+-]?\d+\.?\d*)', after_final)
    market_spread = None
    favorite = None
    
    for team_abbr, spread_val in spread_matches:
        sv = float(spread_val)
        if abs(sv) < 0.5 or abs(sv) > 25:
            continue
        
        if sv < 0:
            favorite = team_abbr
            market_spread = abs(sv)
        elif sv > 0:
            if team_abbr == away_abbr:
                favorite = home_abbr
            else:
                favorite = away_abbr
            market_spread = abs(sv)
        break
    
    if market_spread is None or favorite is None:
        return None
    
    # Normalize abbreviations
    away = COVERS_NBA.get(away_abbr, away_abbr)
    home = COVERS_NBA.get(home_abbr, home_abbr)
    fav = COVERS_NBA.get(favorite, favorite)
    
    return {
        "date": date_str,
        "away": away,
        "away_score": int(away_score),
        "home": home,
        "home_score": int(home_score),
        "market_total": total_value,
        "market_spread": market_spread,
        "favorite": fav,
    }


def parse_covers_page(text, date_str):
    """Parse a full Covers.com page to extract all games."""
    games = []
    
    # Split by "Boxscore" to separate games
    # Each game block ends with "Boxscore" link
    game_blocks = re.split(r'Boxscore', text)
    
    for block in game_blocks:
        if '**Final**' not in block:
            continue
        
        # The game block includes the previous game's end and the current game's data
        # We need to find the "Final" marker and extract the game data
        game = parse_covers_game_block(block, date_str)
        if game:
            games.append(game)
    
    return games


def deduplicate_games(existing_games, new_games):
    """Remove duplicate games based on date, away, home."""
    existing_keys = set()
    for g in existing_games:
        key = (g.get("date", ""), g.get("away", ""), g.get("home", ""))
        existing_keys.add(key)
    
    unique = []
    for g in new_games:
        key = (g.get("date", ""), g.get("away", ""), g.get("home", ""))
        if key not in existing_keys:
            unique.append(g)
            existing_keys.add(key)
    
    return unique


def main():
    # Load existing data
    data_file = "scraped_data/all_games_with_real_lines.json"
    if os.path.exists(data_file):
        existing = json.load(open(data_file))
        nba_games = existing["nba"]
        wnba_games = existing["wnba"]
    else:
        nba_games = []
        wnba_games = []
    
    print(f"Existing NBA games: {len(nba_games)}")
    print(f"Existing WNBA games: {len(wnba_games)}")
    
    # Manually parsed games from Covers.com pages we've already fetched
    # Nov 24, 2025
    new_games = [
        # Nov 24, 2025
        {"date": "2025-11-24", "away": "CLE", "away_score": 99, "home": "TOR", "home_score": 110, "market_total": 231.5, "market_spread": 1.5, "favorite": "TOR"},
        {"date": "2025-11-24", "away": "DET", "away_score": 122, "home": "IND", "home_score": 117, "market_total": 237.0, "market_spread": 10.0, "favorite": "DET"},
        {"date": "2025-11-24", "away": "NYK", "away_score": 113, "home": "BKN", "home_score": 100, "market_total": 228.5, "market_spread": 12.5, "favorite": "NYK"},
        {"date": "2025-11-24", "away": "DAL", "away_score": 102, "home": "MIA", "home_score": 106, "market_total": 240.0, "market_spread": 7.5, "favorite": "MIA"},
        
        # Nov 25, 2025
        {"date": "2025-11-25", "away": "ATL", "away_score": 113, "home": "WAS", "home_score": 132, "market_total": 240.5, "market_spread": 11.0, "favorite": "WAS"},
        {"date": "2025-11-25", "away": "ORL", "away_score": 144, "home": "PHI", "home_score": 103, "market_total": 229.5, "market_spread": 4.5, "favorite": "ORL"},
        {"date": "2025-11-25", "away": "LAC", "away_score": 118, "home": "LAL", "home_score": 135, "market_total": 228.0, "market_spread": 5.5, "favorite": "LAL"},
        
        # Nov 26, 2025
        {"date": "2025-11-26", "away": "DET", "away_score": 114, "home": "BOS", "home_score": 117, "market_total": 233.0, "market_spread": 2.0, "favorite": "DET"},
        {"date": "2025-11-26", "away": "NYK", "away_score": 129, "home": "CHA", "home_score": 101, "market_total": 242.0, "market_spread": 6.5, "favorite": "NYK"},
        {"date": "2025-11-26", "away": "MIL", "away_score": 103, "home": "MIA", "home_score": 106, "market_total": 237.0, "market_spread": 10.0, "favorite": "MIA"},
        {"date": "2025-11-26", "away": "IND", "away_score": 95, "home": "TOR", "home_score": 97, "market_total": 234.0, "market_spread": 10.5, "favorite": "TOR"},
        
        # Nov 27, 2025
        {"date": "2025-11-27", "away": "WAS", "away_score": 86, "home": "IND", "home_score": 119, "market_total": 240.5, "market_spread": 6.5, "favorite": "IND"},
        {"date": "2025-11-27", "away": "CLE", "away_score": 123, "home": "ATL", "home_score": 130, "market_total": 236.0, "market_spread": 6.5, "favorite": "CLE"},
        {"date": "2025-11-27", "away": "MIL", "away_score": 109, "home": "NYK", "home_score": 118, "market_total": 232.0, "market_spread": 7.5, "favorite": "NYK"},
        {"date": "2025-11-27", "away": "PHI", "away_score": 115, "home": "BKN", "home_score": 103, "market_total": 221.5, "market_spread": 7.0, "favorite": "PHI"},
    ]
    
    # Deduplicate
    unique = deduplicate_games(nba_games, new_games)
    print(f"New unique games: {len(unique)}")
    
    if unique:
        nba_games.extend(unique)
        print(f"Total NBA games after adding: {len(nba_games)}")
        
        # Save updated data
        existing["nba"] = nba_games
        existing["metadata"]["nba_count"] = len(nba_games)
        existing["metadata"]["total_count"] = len(nba_games) + len(wnba_games)
        existing["metadata"]["nba_coverage_pct"] = round(len(nba_games) / 1230 * 100, 1)
        existing["metadata"]["last_updated"] = "2026-08-03"
        
        with open(data_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        print(f"✅ Saved {len(nba_games)} NBA games to {data_file}")
    else:
        print("No new games to add")


if __name__ == "__main__":
    main()
