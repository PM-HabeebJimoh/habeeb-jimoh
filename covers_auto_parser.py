#!/usr/bin/env python3
"""Parse Covers.com NBA matchup pages and extract game data with closing lines.
Uses the summary sentence format which is the most reliable extraction method.
"""
import json
import re
import os
import sys

DATA_FILE = "scraped_data/all_games_with_real_lines.json"

# Covers.com abbreviation mapping
COVERS_TO_STANDARD = {
    "NY": "NYK", "BK": "BKN", "NO": "NOP", "SA": "SAS",
    "GS": "GSW", "PHO": "PHX", "LA": "LAC",  # LA could be LAC or LAL, context-dependent
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

def parse_covers_page(content, date_str):
    """Parse a Covers.com page and extract game data."""
    games = []
    
    # Split content into game blocks using the summary sentence pattern
    # Pattern: "Team covered the spread of **X.X**. The total score of XXX was **over/under XXX.X**."
    # Also handle: "The spread for this game pushed at **+X**."
    
    # Find all summary sentences
    summary_pattern = r'(\w[\w\s\.]+?) covered the spread of \*\*([+-]?\d+\.?\d?)\*\*\. The total score of (\d+) was \*\*(over|under) (\d+\.?\d?)\*\*'
    push_pattern = r'The spread for this game pushed at \*\*([+-]?\d+\.?\d?)\*\*\. The total score of (\d+) was \*\*(over|under) (\d+\.?\d?)\*\*'
    
    # Find all game blocks by looking for the game header pattern
    # Pattern: "**ABBR1** **score1****Final** **score2**" or with OT
    # The markdown has format like: "DET **110**\n\n**110****Final** **104**\n\nCHA **104**"
    
    # Alternative approach: find all game blocks between "**Team @ Team**" headers
    # Actually, let's use the score table and summary sentence together
    
    # Find all games by looking for the score table pattern
    # The table has: | Team | 1 | 2 | 3 | 4 | Score |
    
    # Let me try a different approach - extract using the game header and summary sentence
    
    # Split by game blocks using "**XXX @ YYY**" pattern
    game_blocks = re.split(r'\*\*(\w[\w\s\.]+? @ \w[\w\s\.]+?)\*\*', content)
    
    # Actually, let me use a simpler approach - find all summary sentences and work backwards
    summaries = list(re.finditer(summary_pattern, content))
    
    for match in summaries:
        team_name = match.group(1).strip()
        spread_str = match.group(2)
        total_score = int(match.group(3))
        ou_direction = match.group(4)
        total_line = float(match.group(5))
        
        # The spread: if team covered with +X, they were underdog; if -X, they were favorite
        spread_val = float(spread_str)
        
        # Now find the game data before this summary
        # Look backwards from the match position to find the score table
        start_pos = max(0, match.start() - 2000)
        preceding_text = content[start_pos:match.start()]
        
        # Find the table with scores
        # Pattern: | ABBR | Q1 | Q2 | Q3 | Q4 | Score |
        table_pattern = r'\| (\w+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|\n\| (\w+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|'
        table_match = re.search(table_pattern, preceding_text)
        
        if not table_match:
            # Try with OT column
            table_pattern_ot = r'\| (\w+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|\n\| (\w+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|'
            table_match = re.search(table_pattern_ot, preceding_text)
            if table_match:
                # OT format: away_abbr, q1-q4, ot, total, home_abbr, q1-q4, ot, total
                away_abbr = table_match.group(1)
                away_score = int(table_match.group(7))
                home_abbr = table_match.group(8)
                home_score = int(table_match.group(14))
            else:
                continue
        else:
            away_abbr = table_match.group(1)
            away_score = int(table_match.group(6))
            home_abbr = table_match.group(7)
            home_score = int(table_match.group(12))
        
        # Convert abbreviations
        away = COVERS_TO_STANDARD.get(away_abbr, away_abbr)
        home = COVERS_TO_STANDARD.get(home_abbr, home_abbr)
        
        # Determine the favorite
        # The summary says "Team covered the spread of **-X.X**" or "Team covered the spread of **+X.X**"
        # If spread is negative (e.g., -6.5), the team was favored
        # If spread is positive (e.g., +6.5), the team was underdog
        
        # The team_name from the summary might be a full name like "Cleveland" or "L.A. Clippers"
        # We need to determine which team is the favorite based on the spread
        
        # The spread value tells us the closing line
        # If it's negative (e.g., CLE -16), CLE was favored by 16
        # If it's positive (e.g., CLE +8.5), CLE was underdog getting 8.5
        
        # Determine which team covered
        # The team_name should match one of the abbreviations
        # We need to figure out which team the summary refers to
        
        # Simple approach: use the spread value to determine the favorite
        # If the home team's spread is negative, home is favored
        # If the away team's spread is negative, away is favored
        
        # Actually, the summary always says "Team covered the spread of **X**"
        # The team that covered is the one whose name appears in the summary
        # We need to figure out which team (away or home) the summary refers to
        
        # For now, let's use a simpler approach:
        # The spread value from the summary tells us the market spread
        # If it's negative, the team that covered was the favorite
        # If it's positive, the team that covered was the underdog
        
        # The market_spread in our format is always positive (how much the favorite is favored by)
        # The favorite is the team with the negative spread
        
        if spread_val < 0:
            # The team that covered was the favorite
            market_spread = abs(spread_val)
            # We need to figure out which team is the favorite
            # The team that covered is the favorite, so it's the team mentioned in the summary
            # But we don't know which team that is from the summary alone
            # We need to check the score table to determine which team won
            # If the home team won by more than the spread, the home team is the favorite
            # If the away team won by more than the spread, the away team is the favorite
            
            # Actually, let me use the Cover By value
            # The "Cover By" line in the page tells us how much the team covered by
            # Let me look for it in the preceding text
            cover_by_pattern = r'Cover By ([+-]?\d+\.?\d?)'
            cover_match = re.search(cover_by_pattern, preceding_text)
            
            # Simplest approach: if the spread is negative and the team name in the summary
            # is the home team, then the home team is the favorite
            # But we don't have a reliable team name to abbreviation mapping
            
            # Let me use a different approach: look at the "Cover By" and the spread line
            # The page shows: "CLE -16" or "ATL +1" etc.
            # This is the closing line for the team
            
            # Let me look for the spread line in the preceding text
            # Pattern: "CLE -16" or "ATL +1" or "NY +3.5"
            spread_line_pattern = r'(\w{2,3}) ([+-]\d+\.?\d?)'
            spread_line_matches = re.findall(spread_line_pattern, preceding_text)
            
            # Find the team with the negative spread (the favorite)
            favorite = None
            for team_abbr, spread in spread_line_matches:
                if float(spread) < 0:
                    favorite = COVERS_TO_STANDARD.get(team_abbr, team_abbr)
                    break
            
            if favorite is None:
                # The underdog covered, so the other team is the favorite
                # Check if home or away is the favorite based on the spread
                for team_abbr, spread in spread_line_matches:
                    if float(spread) > 0:
                        # This team is the underdog, the other team is the favorite
                        underdog = COVERS_TO_STANDARD.get(team_abbr, team_abbr)
                        if underdog == home:
                            favorite = away
                        else:
                            favorite = home
                        break
            
            if favorite is None:
                # Fallback: use the score difference to determine favorite
                if home_score > away_score:
                    favorite = home
                else:
                    favorite = away
        else:
            # The team that covered was the underdog (positive spread)
            market_spread = abs(spread_val)
            # The underdog is the team mentioned in the summary
            # The favorite is the other team
            
            # Look for the spread line in the preceding text
            spread_line_pattern = r'(\w{2,3}) ([+-]\d+\.?\d?)'
            spread_line_matches = re.findall(spread_line_pattern, preceding_text)
            
            # Find the team with the negative spread (the favorite)
            favorite = None
            for team_abbr, spread in spread_line_matches:
                if float(spread) < 0:
                    favorite = COVERS_TO_STANDARD.get(team_abbr, team_abbr)
                    break
            
            if favorite is None:
                # Check for the other team with positive spread
                for team_abbr, spread in spread_line_matches:
                    if float(spread) > 0:
                        # This team is the underdog
                        underdog = COVERS_TO_STANDARD.get(team_abbr, team_abbr)
                        if underdog == home:
                            favorite = away
                        else:
                            favorite = home
                        break
            
            if favorite is None:
                # Fallback
                if home_score > away_score:
                    favorite = home
                else:
                    favorite = away
        
        game = {
            "date": date_str,
            "away": away,
            "away_score": away_score,
            "home": home,
            "home_score": home_score,
            "market_total": total_line,
            "market_spread": market_spread,
            "favorite": favorite
        }
        games.append(game)
    
    return games

def main():
    if len(sys.argv) < 2:
        print("Usage: python covers_auto_parser.py <content_file> <date>")
        print("  content_file: file containing the Covers.com page content")
        print("  date: date in YYYY-MM-DD format")
        sys.exit(1)
    
    content_file = sys.argv[1]
    date_str = sys.argv[2]
    
    with open(content_file) as f:
        content = f.read()
    
    games = parse_covers_page(content, date_str)
    print(f"Extracted {len(games)} games from {date_str}")
    
    for g in games:
        print(f"  {g['away']} {g['away_score']} @ {g['home']} {g['home_score']} | spread={g['market_spread']} total={g['market_total']} fav={g['favorite']}")
    
    if games:
        data = load_data()
        added = add_games(data, games)
        data['nba'].sort(key=lambda g: (g['date'], g['away']))
        save_data(data)
        print(f"Added {added} new games to dataset")

if __name__ == "__main__":
    main()
