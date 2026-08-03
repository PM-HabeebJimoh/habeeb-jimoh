#!/usr/bin/env python3
"""
Parse Covers.com NBA matchup pages to extract game data.
Extracts: away team, away score, home team, home score, closing total, closing spread, favorite.
"""

import re
import json
import os

# Covers.com abbreviation mapping
COVERS_NBA = {
    "ATL": "ATL", "BOS": "BOS", "BK": "BKN", "BKN": "BKN", "CHA": "CHA", "CHI": "CHI",
    "CLE": "CLE", "DAL": "DAL", "DEN": "DEN", "DET": "DET", "GS": "GSW", "GSW": "GSW",
    "HOU": "HOU", "IND": "IND", "LAC": "LAC", "LAL": "LAL", "LA": "LAL", "MEM": "MEM",
    "MIA": "MIA", "MIL": "MIL", "MIN": "MIN", "NOP": "NOP", "NO": "NOP", "NY": "NYK",
    "NYK": "NYK", "OKC": "OKC", "ORL": "ORL", "PHI": "PHI", "PHO": "PHX", "PHX": "PHX",
    "POR": "POR", "SAC": "SAC", "SA": "SAS", "SAS": "SAS", "TOR": "TOR", "UTA": "UTA",
    "WAS": "WAS", "WSH": "WAS",
}

# Team name mapping for "covered the spread of" lines
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


def parse_covers_page(text, date_str):
    """Parse a Covers.com matchup page and extract game data."""
    games = []
    
    # Pattern 1: Match game blocks
    # Each game has: "TEAM **SCORE**" pattern for away and home
    # Then: "TeamName covered the spread of **SPREAD**" 
    # Then: "The total score of TOTAL was **over/under TOTAL_LINE**"
    
    # Split into game blocks by looking for team score patterns
    # Pattern: "CLE **99**" or "TOR **110**"
    score_pattern = r'\b([A-Z]{2,3})\s+\*\*(\d+)\*\*'
    
    # Find all team-score pairs
    score_matches = list(re.finditer(score_pattern, text))
    
    # Group them into pairs (away, home)
    # Each game has 2 score entries
    i = 0
    while i < len(score_matches) - 1:
        away_abbr = score_matches[i].group(1)
        away_score = int(score_matches[i].group(2))
        home_abbr = score_matches[i + 1].group(1)
        home_score = int(score_matches[i + 1].group(2))
        
        # Skip if this looks like a non-game score (e.g., odds numbers)
        if away_score > 300 or home_score > 300:
            i += 1
            continue
        
        # Look for spread and total in the text between this pair and the next
        start_pos = score_matches[i].start()
        end_pos = score_matches[i + 2].start() if i + 2 < len(score_matches) else len(text)
        
        # If no next pair, use the end of the text
        game_text = text[start_pos:end_pos]
        
        # Extract spread: "TeamName covered the spread of **SPREAD**"
        spread_match = re.search(r'(\w[\w\s.]+?)\s+covered the spread of\s+\*\*([+-]?\d+\.?\d*)\*\*', game_text)
        spread = None
        covered_team = None
        if spread_match:
            covered_team_name = spread_match.group(1).strip()
            spread = float(spread_match.group(2))
            # Try to map the covered team name
            for name, abbr in TEAM_NAME_MAP.items():
                if name in covered_team_name:
                    covered_team = abbr
                    break
        
        # Extract total: "The total score of TOTAL was **over/under TOTAL_LINE**"
        total_match = re.search(r'total score of (\d+) was \*\*(over|under)\s+(\d+\.?\d*)\*\*', game_text)
        total = None
        over_under = None
        if total_match:
            total = float(total_match.group(3))
            over_under = total_match.group(2)
        
        # Map abbreviations
        away_mapped = COVERS_NBA.get(away_abbr, away_abbr)
        home_mapped = COVERS_NBA.get(home_abbr, home_abbr)
        
        # Determine favorite
        favorite = None
        if spread is not None:
            if spread < 0:
                # Negative spread = covered team is the favorite
                favorite = covered_team
            elif spread > 0:
                # Positive spread = covered team is the underdog, so the other team is the favorite
                if covered_team == away_mapped:
                    favorite = home_mapped
                else:
                    favorite = away_mapped
            # spread = 0 means pick'em, no favorite
        
        # Skip if no spread or total (game might have "Off" lines)
        if total is not None and spread is not None:
            games.append({
                "date": date_str,
                "away": away_mapped,
                "away_score": away_score,
                "home": home_mapped,
                "home_score": home_score,
                "market_total": total,
                "market_spread": abs(spread),
                "favorite": favorite,
            })
        
        i += 2
    
    return games


def parse_covers_page_v2(text, date_str):
    """More robust parser for Covers.com matchup pages."""
    games = []
    
    # Find all game blocks using the "covered the spread of" anchor
    # Each game block starts with team scores and ends with the total line
    
    # Pattern: "TEAM_ABBR **SCORE**" 
    score_pattern = r'([A-Z]{2,3})\s+\*\*(\d+)\*\*'
    
    # Pattern: "TeamName covered the spread of **SPREAD**"
    spread_pattern = r'([\w.\s]+?)covered the spread of\s+\*\*([+-]?\d+\.?\d*)\*\*'
    
    # Pattern: "The total score of TOTAL was **over/under TOTAL_LINE**"
    total_pattern = r'total score of (\d+) was \*\*(?:over|under)\s+(\d+\.?\d*)\*\*'
    
    # Find all spread matches first (these anchor each game)
    spread_matches = list(re.finditer(spread_pattern, text))
    total_matches = list(re.finditer(total_pattern, text))
    
    if len(spread_matches) != len(total_matches):
        # Try to match them up
        pass
    
    for idx, spread_match in enumerate(spread_matches):
        covered_team_name = spread_match.group(1).strip()
        spread = float(spread_match.group(2))
        
        # Map covered team name
        covered_team = None
        for name, abbr in TEAM_NAME_MAP.items():
            if name in covered_team_name:
                covered_team = abbr
                break
        
        # Find the corresponding total
        total = None
        if idx < len(total_matches):
            total = float(total_matches[idx].group(2))
        
        # Find the team scores before this spread match
        # Look backwards from the spread match position
        pre_text = text[max(0, spread_match.start() - 1500):spread_match.start()]
        score_matches = list(re.finditer(score_pattern, pre_text))
        
        if len(score_matches) >= 2:
            # Last two score matches are the home and away scores
            away_match = score_matches[-2]
            home_match = score_matches[-1]
            
            away_abbr = away_match.group(1)
            away_score = int(away_match.group(2))
            home_abbr = home_match.group(1)
            home_score = int(home_match.group(2))
            
            # Validate scores
            if away_score > 300 or home_score > 300:
                continue
            
            # Map abbreviations
            away_mapped = COVERS_NBA.get(away_abbr, away_abbr)
            home_mapped = COVERS_NBA.get(home_abbr, home_abbr)
            
            # Determine favorite
            favorite = None
            if spread < 0:
                favorite = covered_team
            elif spread > 0:
                if covered_team == away_mapped:
                    favorite = home_mapped
                else:
                    favorite = away_mapped
            
            if total is not None and spread is not None:
                games.append({
                    "date": date_str,
                    "away": away_mapped,
                    "away_score": away_score,
                    "home": home_mapped,
                    "home_score": home_score,
                    "market_total": total,
                    "market_spread": abs(spread),
                    "favorite": favorite,
                })
    
    return games


def parse_all_pages(directory):
    """Parse all saved Covers.com pages and return a combined game list."""
    all_games = []
    
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith('.txt'):
            continue
        
        # Extract date from filename (e.g., "nba_2025-10-21.txt")
        parts = filename.replace('.txt', '').split('_')
        date_str = parts[-1] if len(parts) > 1 else filename
        
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            text = f.read()
        
        games = parse_covers_page_v2(text, date_str)
        all_games.extend(games)
        print(f"  {filename}: {len(games)} games")
    
    return all_games


if __name__ == "__main__":
    # Test with the existing pages
    games = parse_all_pages("scraped_data/pages")
    print(f"\nTotal games parsed: {len(games)}")
    
    # Save to JSON
    with open("scraped_data/nba_2025_26_covers_games_v2.json", "w") as f:
        json.dump(games, f, indent=2)
    
    # Compare with existing data
    with open("scraped_data/nba_2025_26_covers_games.json") as f:
        old_games = json.load(f)
    print(f"Old data: {len(old_games)} games")
    print(f"New data: {len(games)} games")
