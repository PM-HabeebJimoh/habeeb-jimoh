#!/usr/bin/env python3
"""
Comprehensive Covers.com NBA Scraper
Parses raw page content from Covers.com matchups pages and extracts game data.
Reads from saved .txt files in scraped_data/pages/ directory.
"""

import os
import re
import json
from datetime import datetime, timedelta

PAGES_DIR = "/home/user/habeeb-jimoh/scraped_data/pages"
DATA_DIR = "/home/user/habeeb-jimoh/scraped_data"

# Abbreviation mapping: Covers.com → internal format
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

# Full team name map for parsing "covered" team names
TEAM_NAME_MAP = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GSW", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "L.A. Clippers": "LAC", "L.A. Lakers": "LAL",
    "Los Angeles": "LAL", "Memphis": "MEM", "Miami": "MIA", "Milwaukee": "MIL",
    "Minnesota": "MIN", "New Orleans": "NOP", "New York": "NYK",
    "Oklahoma City": "OKC", "Orlando": "ORL", "Philadelphia": "PHI",
    "Phoenix": "PHX", "Portland": "POR", "Sacramento": "SAC",
    "San Antonio": "SAS", "Toronto": "TOR", "Utah": "UTA", "Washington": "WAS",
}


def parse_game_blocks(content):
    """Parse all game blocks from a Covers.com page.
    
    Returns list of dicts with: away, away_score, home, home_score, 
    market_total, market_spread, favorite
    """
    games = []
    
    # Find all game blocks - each starts with a team pattern like "CHI **110**"
    # and ends with the total/spread line
    
    # Strategy: Find all "covered the spread" and "total score" lines
    # Then match them with team scores
    
    # Pattern for team scores: "ABBR **score**"
    # This captures the team abbreviation and score
    team_score_pattern = re.compile(r'\b([A-Z]{2,3})\s+\*\*(\d+)\*\*')
    
    # Pattern for total: "The total score of XXX was **over/under YYY**"
    total_pattern = re.compile(r'total score of (\d+) was \*\*(over|under)\s+(\d+\.?\d*)\*\*')
    
    # Pattern for spread: "TeamName covered the spread of **+/-X.X**"
    spread_pattern = re.compile(r'covered the spread of \*\*([+-]?\d+\.?\d*)\*\*')
    
    # Find all team scores
    team_scores = list(team_score_pattern.finditer(content))
    
    # Find all totals
    totals = list(total_pattern.finditer(content))
    
    # Find all spreads
    spreads = list(spread_pattern.finditer(content))
    
    # Group team scores into pairs (away, home)
    pairs = []
    used = set()
    for i in range(len(team_scores)):
        if i in used:
            continue
        for j in range(i + 1, len(team_scores)):
            if j in used:
                continue
            # Two consecutive team scores = one game
            # Check they're close enough (within 500 chars)
            if team_scores[j].start() - team_scores[i].end() < 500:
                pairs.append((i, j))
                used.update([i, j])
                break
    
    # Match each pair with a total and spread
    for pair_idx, (ti, tj) in enumerate(pairs):
        away_abbr = team_scores[ti].group(1)
        away_score = int(team_scores[ti].group(2))
        home_abbr = team_scores[tj].group(1)
        home_score = int(team_scores[tj].group(2))
        actual_total = away_score + home_score
        
        # Define the block of text for this game
        block_start = team_scores[ti].start()
        block_end = team_scores[tj].end() + 800
        if pair_idx + 1 < len(pairs):
            block_end = min(block_end, team_scores[pairs[pair_idx + 1][0]].start())
        block = content[block_start:block_end]
        
        # Find the total line for this game
        market_total = None
        total_direction = None
        for tm in totals:
            if int(tm.group(1)) == actual_total and block_start <= tm.start() < block_end:
                market_total = float(tm.group(3))
                total_direction = tm.group(2)
                break
        
        # Find the spread line for this game
        market_spread = None
        covered_team = None
        spread_matches = list(spread_pattern.finditer(block))
        if spread_matches:
            sm = spread_matches[0]
            spread_value = float(sm.group(1))
            
            # Find which team covered - look backwards from the spread match
            pre_text = block[:sm.start()]
            
            # Try to find a team name in the text before the spread
            covered = None
            for name, abbr in TEAM_NAME_MAP.items():
                if name.lower() in pre_text[-200:].lower():
                    covered = abbr
                    break
            
            if not covered:
                # Try abbreviation
                for abbr in [away_abbr, home_abbr]:
                    if abbr.lower() in pre_text[-100:].lower():
                        covered = COVERS_NBA.get(abbr, abbr)
                        break
            
            if not covered:
                covered = COVERS_NBA.get(away_abbr, away_abbr)
            
            # Determine favorite and spread
            if spread_value > 0:
                # Positive spread = covered team is underdog
                if covered == COVERS_NBA.get(away_abbr, away_abbr):
                    favorite = COVERS_NBA.get(home_abbr, home_abbr)
                else:
                    favorite = COVERS_NBA.get(away_abbr, away_abbr)
                market_spread = abs(spread_value)
            else:
                # Negative spread = covered team is favorite
                favorite = covered
                market_spread = abs(spread_value)
        else:
            favorite = None
        
        if market_total and market_spread and favorite:
            # Map abbreviations
            away_mapped = COVERS_NBA.get(away_abbr, away_abbr)
            home_mapped = COVERS_NBA.get(home_abbr, home_abbr)
            
            games.append({
                "away": away_mapped,
                "away_score": away_score,
                "home": home_mapped,
                "home_score": home_score,
                "market_total": market_total,
                "market_spread": market_spread,
                "favorite": favorite,
                "total_direction": total_direction,
            })
    
    return games


def parse_all_pages():
    """Parse all saved pages and build the complete game database."""
    all_games = []
    seen = set()  # Track unique games to avoid duplicates
    
    for f in sorted(os.listdir(PAGES_DIR)):
        if not f.startswith("nba_") or not f.endswith(".txt"):
            continue
        
        date_str = f[4:-4]  # Extract date from filename
        
        filepath = os.path.join(PAGES_DIR, f)
        with open(filepath) as fh:
            content = fh.read()
        
        games = parse_game_blocks(content)
        
        for game in games:
            # Create a unique key for this game
            key = (game["away"], game["away_score"], game["home"], game["home_score"])
            if key not in seen:
                seen.add(key)
                game["date"] = date_str
                all_games.append(game)
    
    # Sort by date
    all_games.sort(key=lambda g: g["date"])
    
    # Save to JSON
    out_path = os.path.join(DATA_DIR, "nba_2025_26_games.json")
    with open(out_path, "w") as fh:
        json.dump(all_games, fh, indent=2)
    
    return all_games


def generate_backtest_data(games):
    """Generate the data in the format needed for the backtest script.
    
    Format: (away_abbr, away_score, home_abbr, home_score, label, market_total, market_spread, favorite)
    """
    results = []
    for game in games:
        dt = datetime.strptime(game["date"], "%Y-%m-%d")
        label = dt.strftime("%b %-d").replace(" 0", " ")
        
        results.append((
            game["away"],
            game["away_score"],
            game["home"],
            game["home_score"],
            label,
            game["market_total"],
            game["market_spread"],
            game["favorite"],
        ))
    
    return results


def status():
    """Show scraping status."""
    existing = set()
    for f in os.listdir(PAGES_DIR):
        if f.startswith("nba_") and f.endswith(".txt"):
            existing.add(f[4:-4])
    
    start = datetime(2025, 10, 21)
    end = datetime(2026, 4, 13)
    current = start
    total_dates = 0
    while current <= end:
        total_dates += 1
        current += timedelta(days=1)
    
    # Parse all games
    games = parse_all_pages()
    
    print(f"Covers.com pages scraped: {len(existing)}/{total_dates}")
    print(f"Total NBA games parsed: {len(games)}")
    print(f"Missing dates: {total_dates - len(existing)}")
    
    # Generate missing dates list
    missing = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        if date_str not in existing:
            missing.append(date_str)
        current += timedelta(days=1)
    
    if missing:
        missing_path = os.path.join(DATA_DIR, "missing_dates.txt")
        with open(missing_path, "w") as fh:
            fh.write("\n".join(missing) + "\n")
        print(f"Missing dates saved to: {missing_path}")
    
    # Show some stats
    if games:
        dates_with_games = set(g["date"] for g in games)
        print(f"\nGames per month:")
        for month in sorted(set(d[:7] for d in dates_with_games)):
            month_games = [g for g in games if g["date"].startswith(month)]
            print(f"  {month}: {len(month_games)} games")
    
    return games


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            status()
        elif sys.argv[1] == "parse":
            games = parse_all_pages()
            print(f"Total games: {len(games)}")
            for g in games[:5]:
                print(f"  {g['date']}: {g['away']} {g['away_score']} @ {g['home']} {g['home_score']} | Total: {g['market_total']} | Spread: {g['market_spread']} | Fav: {g['favorite']}")
        elif sys.argv[1] == "generate":
            games = parse_all_pages()
            results = generate_backtest_data(games)
            print(f"Generated {len(results)} game entries for backtest")
            for r in results[:5]:
                print(f"  {r}")
    else:
        status()
