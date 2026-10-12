#!/usr/bin/env python3
"""
Covers.com page parser — V5 with summary sentence parsing.
Most reliable method: uses the "Team covered the spread of **-X.X**. 
The total score of XXX was **over/under XXX.X**." format.
"""

import re
import json

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

VALID_ABBRS = set(COVERS_NBA.keys())


def parse_covers_page_v5(text, date_str):
    """
    Parse a Covers.com matchup page using the summary sentence format.
    
    Strategy: Find all game blocks using "**Final**" markers, then extract
    scores, spread, and total from the summary sentence within each block.
    """
    games = []
    
    # Find all Final markers
    final_positions = [m.start() for m in re.finditer(r'\*\*Final\*\*', text)]
    final_positions_ot = [m.start() for m in re.finditer(r'\*\*Final OT\*\*', text)]
    
    # Combine and sort all Final positions
    all_positions = sorted(set(final_positions + final_positions_ot))
    
    for i, pos in enumerate(all_positions):
        # Get the game block: from start of this game to start of next game
        # Look backwards to find the start of this game block
        block_start = max(0, pos - 500)
        block_end = all_positions[i + 1] + 500 if i + 1 < len(all_positions) else len(text)
        block = text[block_start:block_end]
        
        # Extract scores from Final marker
        score_match = re.search(r'\*\*(\d+)\*\*\*\*(?:Final|Final OT)\*\*\s+\*\*(\d+)\*\*', block)
        if not score_match:
            continue
        
        away_score = int(score_match.group(1))
        home_score = int(score_match.group(2))
        
        # Extract team abbreviations from the block
        # Before Final: away team (last valid ABBR **score**)
        before = block[:score_match.start()]
        after = block[score_match.end():]
        
        # Find away team
        away_matches = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', before)
        valid_away = [(a, s) for a, s in away_matches if a in VALID_ABBRS]
        if not valid_away:
            continue
        away_abbr = valid_away[-1][0]
        
        # Find home team
        home_matches = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', after[:300])
        valid_home = [(a, s) for a, s in home_matches if a in VALID_ABBRS]
        if not valid_home:
            continue
        home_abbr = valid_home[0][0]
        
        # Extract spread and total from summary sentence
        # "Team covered the spread of **-X.X**. The total score of XXX was **over/under XXX.X**."
        summary_match = re.search(
            r'(\w[\w\s]*?)\s+covered the spread of\s+\*\*([+-]?\d+\.?\d*)\*\*\.\s+'
            r'The total score of\s+\d+\s+was\s+\*\*(?:over|under)\s+(\d+\.?\d*)\*\*',
            block
        )
        
        # Also try the "under XXX.X" or "over XXX.X" pattern
        total_alt = re.search(r'(?:under|over)\s+(\d+\.?\d*)', after[:500], re.IGNORECASE)
        
        # Also try spread line pattern: "ABBR -X.X" or "ABBR +X.X"
        spread_matches = re.findall(r'([A-Z]{2,3})\s+([+-]\d+\.?\d*)', after[:500])
        
        market_spread = None
        market_total = None
        favorite = None
        
        if summary_match:
            covering_team = summary_match.group(1).strip()
            spread_str = summary_match.group(2)
            market_total = float(summary_match.group(3))
            spread_val = float(spread_str)
            
            # The covering team is the one that covered the spread
            # If spread is negative, the covering team is the favorite
            # The spread value in the summary is from the perspective of the covering team
            # But we need to determine the favorite from the game data
            # The spread line in the game block shows: "ABBR -X.X" (favorite) or "ABBR +X.X" (underdog)
            
            # Use the spread line to determine the favorite
            for team_abbr, spread_val_str in spread_matches:
                sv = float(spread_val_str)
                if team_abbr not in VALID_ABBRS:
                    continue
                if abs(sv) < 0.5 or abs(sv) > 25:
                    continue
                
                if sv < 0:
                    favorite = team_abbr
                    market_spread = abs(sv)
                else:
                    if team_abbr == away_abbr:
                        favorite = home_abbr
                    else:
                        favorite = away_abbr
                    market_spread = abs(sv)
                break
            
            # If we still don't have the favorite from the spread line, use the summary
            if favorite is None:
                market_spread = abs(spread_val)
                # Try to determine favorite from the summary
                # If the covering team has a negative spread, they're the favorite
                if spread_val < 0:
                    # The covering team is the favorite
                    # Map team name to abbreviation
                    team_name_map = {
                        "Washington": "WAS", "Philadelphia": "PHI", "Portland": "POR",
                        "Toronto": "TOR", "Minnesota": "MIN", "New Orleans": "NOP",
                        "New York": "NYK", "Boston": "BOS", "Memphis": "MEM",
                        "San Antonio": "SAS", "Oklahoma City": "OKC", "Golden State": "GSW",
                        "Denver": "DEN", "Indiana": "IND", "Cleveland": "CLE",
                        "Orlando": "ORL", "Charlotte": "CHA", "L.A. Clippers": "LAC",
                        "Atlanta": "ATL", "Sacramento": "SAC", "Houston": "HOU",
                        "Brooklyn": "BKN", "Chicago": "CHI", "Detroit": "DET",
                        "Milwaukee": "MIL", "Miami": "MIA", "Dallas": "DAL",
                        "L.A. Lakers": "LAL", "Utah": "UTA", "Phoenix": "PHX",
                        "New Orleans": "NOP",
                    }
                    fav_name = covering_team
                    if fav_name in team_name_map:
                        favorite = team_name_map[fav_name]
                    else:
                        # Try to match from the game data
                        if fav_name in [away_abbr, home_abbr]:
                            favorite = fav_name
                        else:
                            # Skip this game
                            continue
                else:
                    # The covering team is the underdog
                    # The favorite is the other team
                    if covering_team == away_abbr:
                        favorite = home_abbr
                    elif covering_team == home_abbr:
                        favorite = away_abbr
                    else:
                        continue
        
        # If no summary sentence, try alternative methods
        if market_total is None and total_alt:
            market_total = float(total_alt.group(1))
        
        if market_spread is None:
            for team_abbr, spread_val_str in spread_matches:
                sv = float(spread_val_str)
                if team_abbr not in VALID_ABBRS:
                    continue
                if abs(sv) < 0.5 or abs(sv) > 25:
                    continue
                
                if sv < 0:
                    favorite = team_abbr
                    market_spread = abs(sv)
                else:
                    if team_abbr == away_abbr:
                        favorite = home_abbr
                    else:
                        favorite = away_abbr
                    market_spread = abs(sv)
                break
        
        if market_spread is None or market_total is None or favorite is None:
            continue
        
        # Normalize abbreviations
        away = COVERS_NBA.get(away_abbr, away_abbr)
        home = COVERS_NBA.get(home_abbr, home_abbr)
        fav = COVERS_NBA.get(favorite, favorite)
        
        games.append({
            "date": date_str,
            "away": away,
            "away_score": away_score,
            "home": home,
            "home_score": home_score,
            "market_total": market_total,
            "market_spread": market_spread,
            "favorite": fav,
        })
    
    return games


def add_games_to_dataset(games, date_str):
    """Add parsed games to the main dataset."""
    data_file = "scraped_data/all_games_with_real_lines.json"
    with open(data_file) as f:
        data = json.load(f)
    
    # Get existing game keys to avoid duplicates
    existing_keys = set()
    for g in data['nba']:
        key = f"{g['date']}_{g['away']}_{g['home']}"
        existing_keys.add(key)
    
    added = 0
    for g in games:
        key = f"{date_str}_{g['away']}_{g['home']}"
        if key not in existing_keys:
            data['nba'].append(g)
            existing_keys.add(key)
            added += 1
    
    # Update metadata
    data['metadata']['nba_count'] = len(data['nba'])
    data['metadata']['total_count'] = len(data['nba']) + len(data['wnba'])
    data['metadata']['nba_coverage_pct'] = round(len(data['nba']) / 1230 * 100, 1)
    data['metadata']['total_coverage_pct'] = round(
        (len(data['nba']) + len(data['wnba'])) / 1447 * 100, 1
    )
    
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return added


if __name__ == "__main__":
    # Test
    print("V5 parser ready. Use with batch_covers_scraper.py")
