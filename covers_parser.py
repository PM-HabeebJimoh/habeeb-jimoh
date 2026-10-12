#!/usr/bin/env python3
"""Parse Covers.com NBA matchup pages to extract game data with closing lines."""

import re
import json

# Covers.com abbreviation mapping
COVERS_TO_NBA = {
    'GS': 'GSW', 'NO': 'NOP', 'SA': 'SAS', 'BK': 'BKN', 'NY': 'NYK',
    'PHO': 'PHX', 'LAC': 'LAC', 'LAL': 'LAL', 'OKC': 'OKC', 'HOU': 'HOU',
    'DEN': 'DEN', 'BOS': 'BOS', 'MIA': 'MIA', 'MIL': 'MIL', 'MIN': 'MIN',
    'DAL': 'DAL', 'DET': 'DET', 'IND': 'IND', 'ATL': 'ATL', 'CHA': 'CHA',
    'ORL': 'ORL', 'WAS': 'WAS', 'WSH': 'WAS', 'CLE': 'CLE', 'CHI': 'CHI',
    'TOR': 'TOR', 'PHI': 'PHI', 'BKN': 'BKN', 'NYK': 'NYK', 'POR': 'POR',
    'SAC': 'SAC', 'UTA': 'UTA', 'MEM': 'MEM', 'SAS': 'SAS', 'NOP': 'NOP',
    'GSW': 'GSW', 'PHX': 'PHX', 'LA': 'LAL',  # LA on Covers usually means Lakers
}

def normalize_abbr(abbr):
    return COVERS_TO_NBA.get(abbr, abbr)

def parse_covers_page(text, date_str):
    """Parse a Covers.com NBA matchups page and extract games.
    
    Looks for summary sentences like:
    "Team covered the spread of **-X.X**. The total score of XXX was **over/under XXX.X**."
    or
    "The spread for this game pushed at **+X**. The total score of XXX was **over/under XXX.X**."
    
    Also extracts team abbreviations and scores from the game headers.
    """
    games = []
    
    # Strategy: Find all game blocks by looking for the pattern:
    # "AWAY **score** ... HOME **score**" followed by summary sentence
    
    # Find all matchup headers: **Away @ Home** or **Away @ Home** NBA Cup
    matchup_pattern = r'\*\*([A-Z]{2,3})\s*@\s*([A-Z]{2,3})\*\*'
    
    # Find score patterns: AWAY **score** and HOME **score**
    # Format: AWAY **XX** ... Final ... HOME **XX**
    score_pattern = r'([A-Z]{2,3})\s*\*\*(\d+)\*\*'
    
    # Find summary sentences:
    # "Team covered the spread of **-X.X**. The total score of XXX was **over/under XXX.X**."
    # or "The spread for this game pushed at **+X**. The total score of XXX was **over/under XXX.X**."
    summary_pattern = r'([A-Za-z\s\.]+(?:covered the spread|pushed)).*?\*\*(-?[\d.]+)\*\*\.\s*The total score of (\d+) was \*\*(over|under)\s+([\d.]+)\*\*'
    pushed_summary = r'The spread for this game pushed at \*\*([+-]?[\d.]+)\*\*\.\s*The total score of (\d+) was \*\*(over|under)\s+([\d.]+)\*\*'
    
    # More robust approach: split by game blocks
    # Each game block starts with a matchup header like "**Team @ Team**"
    
    # Find all matchup positions
    matchups = list(re.finditer(matchup_pattern, text))
    
    if not matchups:
        return games
    
    for i, m in enumerate(matchups):
        away_raw = m.group(1)
        home_raw = m.group(2)
        
        # Get the text block for this game (from this matchup to the next one or end)
        start = m.start()
        if i + 1 < len(matchups):
            end = matchups[i + 1].start()
        else:
            end = len(text)
        
        block = text[start:end]
        
        # Extract scores from the block
        # Pattern: ABBREV **SCORE** ... Final ... ABBREV **SCORE**
        scores = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', block)
        
        away_score = None
        home_score = None
        
        if len(scores) >= 2:
            # First score is away, second is home
            away_score = int(scores[0][1])
            home_score = int(scores[1][1])
        
        # Extract spread and total from summary sentence
        # Pattern 1: "Team covered the spread of **-X.X**. The total score of NNN was **over/under XXX.X**."
        covered = re.search(r'covered the spread of \*\*(-?[\d.]+)\*\*\.\s*The total score of \d+ was \*\*(?:over|under)\s+([\d.]+)\*\*', block)
        
        # Pattern 2: pushed spread
        pushed = re.search(r'pushed at \*\*([+-]?[\d.]+)\*\*\.\s*The total score of \d+ was \*\*(?:over|under)\s+([\d.]+)\*\*', block)
        
        spread = None
        total = None
        favorite = None
        
        if covered:
            spread_val = float(covered.group(1))
            total = float(covered.group(2))
            # Negative spread = favorite is the team mentioned
            # Positive spread = underdog is the team mentioned
            # The spread value from Covers.com is from the covering team's perspective
            # We need absolute value for our engine
            spread = abs(spread_val)
            
            # Determine favorite from the spread and matchup
            # "Team covered the spread of **-X**" means that team was favored by X
            # "Team covered the spread of **+X**" means that team was the underdog getting X
            # Find which team covered
            cover_team_match = re.search(r'([A-Za-z\s\.]+?)\s+covered the spread', block)
            
            if cover_team_match:
                cover_text = cover_team_match.group(1).strip()
                # Extract the team abbreviation from the cover text
                cover_abbr_match = re.search(r'([A-Z]{2,3})', cover_text)
                if cover_abbr_match:
                    cover_abbr = normalize_abbr(cover_abbr_match.group(1))
                    away_norm = normalize_abbr(away_raw)
                    home_norm = normalize_abbr(home_raw)
                    
                    if spread_val < 0:
                        # Covering team was favorite (negative spread)
                        favorite = cover_abbr
                    else:
                        # Covering team was underdog (positive spread)
                        # Favorite is the other team
                        if cover_abbr == away_norm:
                            favorite = home_norm
                        else:
                            favorite = away_norm
        
        elif pushed:
            spread_val = float(pushed.group(1))
            total = float(pushed.group(2))
            spread = abs(spread_val)
            # On a push, just default to home as favorite
            favorite = normalize_abbr(home_raw)
        
        # Only add if we have all required data
        if away_score is not None and home_score is not None and spread is not None and total is not None and favorite is not None:
            game = {
                'date': date_str,
                'away': normalize_abbr(away_raw),
                'away_score': away_score,
                'home': normalize_abbr(home_raw),
                'home_score': home_score,
                'market_total': total,
                'market_spread': spread,
                'favorite': favorite,
            }
            games.append(game)
    
    return games


def parse_and_print(text, date_str):
    """Parse a page and print the results."""
    games = parse_covers_page(text, date_str)
    print(f"\n=== {date_str} ({len(games)} games) ===")
    for g in games:
        print(f"  {g['away']} {g['away_score']} @ {g['home']} {g['home_score']} | spread={g['market_spread']} total={g['market_total']} fav={g['favorite']}")
    return games


if __name__ == '__main__':
    # Test with saved page content
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            text = f.read()
        date_str = sys.argv[2] if len(sys.argv) > 2 else '2025-11-28'
        parse_and_print(text, date_str)
