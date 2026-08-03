#!/usr/bin/env python3
"""
ABAKE USE — Batch Covers.com NBA Scraper
Fetches all NBA game scores and closing lines from Covers.com for the 2025-26 season.
Uses the Covers.com matchup pages which have BOTH scores AND closing lines.

This script is designed to be run incrementally - it saves progress after each date.
"""

import json
import re
import os
from datetime import datetime, timedelta

# Team abbreviation mappings
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

TEAM_NAME_MAP = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GSW", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "L.A. Clippers": "LAC", "LA Lakers": "LAL",
    "L.A. Lakers": "LAL", "Los Angeles": "LAL", "Memphis": "MEM", "Miami": "MIA",
    "Milwaukee": "MIL", "Minnesota": "MIN", "New Orleans": "NOP", "New York": "NYK",
    "Oklahoma City": "OKC", "Orlando": "ORL", "Philadelphia": "PHI", "Phoenix": "PHX",
    "Portland": "POR", "Sacramento": "SAC", "San Antonio": "SAS", "Toronto": "TOR",
    "Utah": "UTA", "Washington": "WAS",
}

def parse_covers_page(text, date_str):
    """Parse a Covers.com matchup page to extract game data."""
    games = []
    
    # Pattern 1: "TeamName covered the spread of **X.X**"
    spread_pattern = r'([\w.\s]+?)covered the spread of\s+\*\*([+-]?\d+\.?\d*)\*\*'
    # Pattern 2: "total score of XXX was **over/under XXX.X**"
    total_pattern = r'total score of (\d+) was \*\*(?:over|under)\s+(\d+\.?\d*)\*\*'
    # Pattern 3: "ABBR **XXX**" (team abbreviation and score)
    score_pattern = r'([A-Z]{2,3})\s+\*\*(\d+)\*\*'
    
    spread_matches = list(re.finditer(spread_pattern, text))
    total_matches = list(re.finditer(total_pattern, text))
    
    for idx, spread_match in enumerate(spread_matches):
        covered_team_name = spread_match.group(1).strip()
        spread = float(spread_match.group(2))
        
        # Map covered team name to abbreviation
        covered_team = None
        for name, abbr in TEAM_NAME_MAP.items():
            if name in covered_team_name:
                covered_team = abbr
                break
        
        # Get total from corresponding match
        total = float(total_matches[idx].group(2)) if idx < len(total_matches) else None
        
        # Find team scores in the text before this spread match
        pre_text = text[max(0, spread_match.start()-2000):spread_match.start()]
        score_matches = list(re.finditer(score_pattern, pre_text))
        
        if len(score_matches) >= 2:
            # Get the last two score matches (away and home)
            away_raw = score_matches[-2].group(1)
            away_score = int(score_matches[-2].group(2))
            home_raw = score_matches[-1].group(1)
            home_score = int(score_matches[-1].group(2))
            
            away_abbr = COVERS_NBA.get(away_raw, away_raw)
            home_abbr = COVERS_NBA.get(home_raw, home_raw)
            
            # Determine favorite from the spread
            # If spread is negative, the covered team is the favorite (they covered the -X.X spread)
            # If spread is positive, the covered team is the underdog
            if spread < 0:
                favorite = covered_team if covered_team else away_abbr
            else:
                # The covered team covered the +X.X spread, meaning they're the underdog
                # The favorite is the other team
                if covered_team == away_abbr:
                    favorite = home_abbr
                else:
                    favorite = away_abbr
            
            if total is not None and spread is not None:
                games.append({
                    "date": date_str,
                    "away": away_abbr,
                    "away_score": away_score,
                    "home": home_abbr,
                    "home_score": home_score,
                    "market_total": total,
                    "market_spread": abs(spread),
                    "favorite": favorite,
                })
    
    return games


def generate_date_range(start, end):
    """Generate all dates between start and end."""
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return dates


def main():
    # Load existing data
    output_file = "scraped_data/nba_2025_26_covers_games_v3.json"
    if os.path.exists(output_file):
        existing_games = json.load(open(output_file))
        print(f"Loaded {len(existing_games)} existing games from {output_file}")
    else:
        existing_games = json.load(open("scraped_data/nba_2025_26_covers_games_v2.json"))
        print(f"Loaded {len(existing_games)} existing games from v2")
    
    # Get dates we already have
    existing_dates = set(g['date'] for g in existing_games)
    
    # Generate all dates we need
    all_dates = generate_date_range(datetime(2025, 10, 21), datetime(2026, 4, 13))
    missing_dates = [d for d in all_dates if d not in existing_dates]
    
    print(f"Missing dates: {len(missing_dates)}")
    print(f"First missing: {missing_dates[0] if missing_dates else 'N/A'}")
    print(f"Last missing: {missing_dates[-1] if missing_dates else 'N/A'}")
    
    # Save missing dates for the fetch_page workflow
    with open("scraped_data/missing_nba_dates.json", "w") as f:
        json.dump(missing_dates, f)
    
    print(f"\nSaved {len(missing_dates)} missing dates to scraped_data/missing_nba_dates.json")
    print("Use fetch_page to get Covers.com data for each date, then parse and save.")


if __name__ == "__main__":
    main()
