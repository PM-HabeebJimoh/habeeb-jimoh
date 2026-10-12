#!/usr/bin/env python3
"""
Massive Covers.com NBA Scraper — Fetches all 1,230 NBA regular season games.
Reads pre-saved page content from /home/user/habeeb-jimoh/scraped_data/pages/
Parses and saves to /home/user/habeeb-jimoh/scraped_data/nba_2025_26_all.json
"""
import re
import json
import os
import sys
from datetime import datetime, timedelta

DATA_DIR = "/home/user/habeeb-jimoh/scraped_data"
PAGES_DIR = os.path.join(DATA_DIR, "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

# Abbreviation mapping: Covers.com → our internal format
COVERS_NBA_MAP = {
    "ATL": "ATL", "BOS": "BOS", "BK": "BKN", "BKN": "BKN",
    "CHA": "CHA", "CHI": "CHI", "CLE": "CLE", "DAL": "DAL",
    "DEN": "DEN", "DET": "DET", "GS": "GSW", "GSW": "GSW",
    "HOU": "HOU", "IND": "IND", "LAC": "LAC", "LAL": "LAL",
    "LA": "LAL", "MEM": "MEM", "MIA": "MIA", "MIL": "MIL",
    "MIN": "MIN", "NOP": "NOP", "NO": "NOP", "NY": "NYK",
    "NYK": "NYK", "OKC": "OKC", "ORL": "ORL", "PHI": "PHI",
    "PHO": "PHX", "PHX": "PHX", "POR": "POR", "SAC": "SAC",
    "SA": "SAS", "SAS": "SAS", "TOR": "TOR", "UTA": "UTA",
    "WAS": "WAS", "WSH": "WAS",
}

# Full name mapping for covered team identification
TEAM_NAME_MAP = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GSW", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "L.A. Clippers": "LAC", "Los Angeles": "LAL",
    "L.A. Lakers": "LAL", "L.A.": "LAL", "Memphis": "MEM", "Miami": "MIA",
    "Milwaukee": "MIL", "Minnesota": "MIN", "New Orleans": "NOP",
    "New York": "NYK", "Oklahoma City": "OKC", "Orlando": "ORL",
    "Philadelphia": "PHI", "Phoenix": "PHX", "Portland": "POR",
    "Sacramento": "SAC", "San Antonio": "SAS", "Toronto": "TOR",
    "Utah": "UTA", "Washington": "WAS",
}


def parse_covers_page(content, date_str):
    """Parse a Covers.com matchups page and extract NBA game data.
    
    Returns list of tuples: (away_covers, away_score, home_covers, home_score,
                             date_label, market_total, market_spread_abs, fav_team_covers)
    """
    games = []
    
    # Step 1: Find all "total score of" matches
    total_pattern = r'total score of (\d+) was \*\*(?:over|under)\s+(\d+\.?\d*)\*\*'
    total_matches = list(re.finditer(total_pattern, content))
    
    # Step 2: Find all "covered the spread of" matches
    spread_pattern = r'covered the spread of \*\*([+-]?\d+\.?\d*)\*\*'
    spread_matches = list(re.finditer(spread_pattern, content))
    
    # Step 3: Find all team-score pairs
    team_score_pattern = r'\b([A-Z]{2,3})\s+\*\*(\d+)\*\*'
    team_scores = list(re.finditer(team_score_pattern, content))
    
    # Step 4: Group into game pairs
    game_pairs = []
    used = set()
    for i in range(len(team_scores)):
        if i in used:
            continue
        for j in range(i + 1, len(team_scores)):
            if j in used:
                continue
            score_i = int(team_scores[i].group(2))
            score_j = int(team_scores[j].group(2))
            game_pairs.append((i, j, score_i, score_j))
            used.add(i)
            used.add(j)
            break
    
    # Step 5: Match totals with game pairs
    used_totals = set()
    used_spreads = set()
    
    for idx, (ti, tj, score_i, score_j) in enumerate(game_pairs):
        away_covers = team_scores[ti].group(1)
        away_score = score_i
        home_covers = team_scores[tj].group(1)
        home_score = score_j
        actual_total = away_score + home_score
        
        # Find matching total
        market_total = None
        for t_idx, tm in enumerate(total_matches):
            if t_idx in used_totals:
                continue
            tm_actual = int(tm.group(1))
            if tm_actual == actual_total:
                market_total = float(tm.group(2))
                used_totals.add(t_idx)
                break
        
        # Find spread for this game
        market_spread = None
        fav_team_covers = None
        
        # Define game block boundaries
        block_start = team_scores[ti].start()
        block_end = team_scores[tj].end() + 500
        if idx + 1 < len(game_pairs):
            next_start = team_scores[game_pairs[idx+1][0]].start()
            block_end = min(block_end, next_start)
        block = content[block_start:block_end]
        
        # Find spread in block
        spread_in_block = list(re.finditer(spread_pattern, block))
        if spread_in_block:
            sm = spread_in_block[0]
            spread_val = float(sm.group(1))
            
            # Find which team covered by looking for team name before the spread
            pre_text = block[:sm.start()]
            
            # Check for full team names
            covered_abbr = None
            for name, abbr in TEAM_NAME_MAP.items():
                if name.lower() in pre_text[-100:].lower():
                    covered_abbr = abbr
                    break
            
            if not covered_abbr:
                # Check for abbreviation matches
                for abbr in [away_covers, home_covers]:
                    if abbr.lower() in pre_text[-80:].lower():
                        covered_abbr = abbr
                        break
            
            if not covered_abbr:
                # Default: the team that appears first in the block is the away team
                # The covered team usually appears right before the spread
                covered_abbr = away_covers
            
            # Determine favorite
            if spread_val > 0:
                # Covered team is UNDERDOG (getting points)
                if covered_abbr == away_covers or covered_abbr == COVERS_NBA_MAP.get(away_covers, away_covers):
                    fav_team_covers = home_covers
                else:
                    fav_team_covers = away_covers
                market_spread = abs(spread_val)
            else:
                # Covered team is FAVORITE (giving points)
                fav_team_covers = covered_abbr
                # Map to Covers abbreviation
                for covers_abbr, internal in COVERS_NBA_MAP.items():
                    if internal == covered_abbr:
                        fav_team_covers = covers_abbr
                        break
                market_spread = abs(spread_val)
        
        if market_total and market_spread and fav_team_covers:
            # Format date label
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            date_label = dt.strftime("%b %-d").replace(" 0", " ")
            
            games.append((
                away_covers, away_score, home_covers, home_score,
                date_label, market_total, market_spread, fav_team_covers
            ))
    
    return games


def process_all_pages():
    """Process all saved pages and extract game data."""
    all_games = []
    dates_with_games = 0
    dates_no_games = 0
    
    # Generate all NBA dates
    start = datetime(2025, 10, 21)
    end = datetime(2026, 4, 13)
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    for date_str in dates:
        page_file = os.path.join(PAGES_DIR, f"nba_{date_str}.txt")
        if os.path.exists(page_file):
            with open(page_file, 'r') as f:
                content = f.read()
            games = parse_covers_page(content, date_str)
            if games:
                all_games.extend(games)
                dates_with_games += 1
            else:
                dates_no_games += 1
        else:
            dates_no_games += 1
    
    # Save results
    output_file = os.path.join(DATA_DIR, "nba_2025_26_all.json")
    with open(output_file, 'w') as f:
        json.dump(all_games, f, indent=2)
    
    print(f"Processed {len(dates)} dates")
    print(f"Dates with games: {dates_with_games}")
    print(f"Dates without games: {dates_no_games}")
    print(f"Total games scraped: {len(all_games)}")
    print(f"Saved to: {output_file}")
    
    return all_games


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "process":
        process_all_pages()
    else:
        print("Usage: python scrape_all_nba.py process")
        print("  First, save Covers.com pages to scraped_data/pages/nba_YYYY-MM-DD.txt")
        print("  Then run: python scrape_all_nba.py process")
