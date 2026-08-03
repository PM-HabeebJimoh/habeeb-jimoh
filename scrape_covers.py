#!/usr/bin/env python3
"""
Scrape NBA closing lines from Covers.com HTML output.
Parses the fetch_page output format to extract game data.
"""
import re
import json
import sys

def parse_covers_html(html_text):
    """Parse Covers.com matchups page to extract game data with closing lines."""
    games = []
    
    # Pattern: Team Score **Final** Score
    # We look for patterns like:
    # HOU **124** ... **124****Final 2OT** **125** ... OKC **125**
    # HOU +6.5  (closing spread)
    # o/u Margin  o23 (over by 23)
    # total score of 249 was **over 226** (closing total)
    
    # Strategy: Find all game blocks by looking for the pattern
    # "total score of X was **over Y**" or "total score of X was **under Y**"
    
    # Find away team, home team, scores, spread, total
    # The page structure is:
    # **AwayTeam @ HomeTeam**
    # AwayAbbr **AwayScore**
    # **AwayScore****Final** **HomeScore**
    # HomeAbbr **HomeScore**
    # Cover By +X
    # AwayOrHome +/-X (spread)
    # o/u Margin
    # o/uX (over/under margin)
    # total score of Total was **over/under ClosingTotal**
    
    # Let's find all the game blocks
    # Pattern for the matchup header: **Away @ Home**
    matchup_pattern = r'\*\*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+@\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\*\*'
    
    # Pattern for scores: Abbrev **Score** ... **AwayScore****Final** **HomeScore**
    # More reliable: find "total score of X was **over/under Y**"
    total_pattern = r'total score of (\d+) was \*\*(over|under)\s+(\d+\.?\d*)\*\*'
    
    # Pattern for spread: "covered the spread of **+/-X**" or similar
    spread_pattern = r'covered the spread of \*\*([+-]?\d+\.?\d*)\*\*'
    
    # Pattern for team abbreviations and scores
    # We need to find the team abbreviation mapping
    # Pattern: ![TeamName](...)\\nTeamAbbr **Score**
    team_score_pattern = r'([A-Z]{2,3})\s+\*\*(\d+)\*\*'
    
    # Find all totals first (these are the most reliable)
    totals = list(re.finditer(total_pattern, html_text))
    
    # Find all spreads
    spreads = list(re.finditer(spread_pattern, html_text))
    
    # Find all team scores
    team_scores = list(re.finditer(team_score_pattern, html_text))
    
    # Find matchup headers
    matchups = list(re.finditer(matchup_pattern, html_text))
    
    # Parse each game by finding the total info
    for i, total_match in enumerate(totals):
        actual_total = int(total_match.group(1))
        ou_result = total_match.group(2)
        closing_total = float(total_match.group(3))
        
        # Find the corresponding spread - should be nearby
        # The spread info appears before the total info
        spread_val = None
        for sp in spreads:
            # Find the spread that's closest before this total
            if sp.start() < total_match.start():
                spread_val = float(sp.group(1))
        
        # Find the team scores near this total
        # Look backwards from the total position to find the scores
        pre_text = html_text[:total_match.start()]
        
        # Find the last two team scores before this total
        nearby_scores = []
        for ts in team_scores:
            if ts.start() < total_match.start() and ts.start() > total_match.start() - 2000:
                nearby_scores.append((ts.group(1), int(ts.group(2)), ts.start()))
        
        # Get the last two scores (home and away)
        if len(nearby_scores) >= 2:
            away_info = nearby_scores[-2]
            home_info = nearby_scores[-1]
            away_abbr = away_info[0]
            away_score = away_info[1]
            home_abbr = home_info[0]
            home_score = home_info[1]
        else:
            continue
        
        # Find the spread - look for the covered spread text
        # "covered the spread of **+/-X**"
        spread_text = pre_text[-1500:]
        spread_matches = list(re.finditer(r'covered the spread of \*\*([+-]?\d+\.?\d*)\*\*', spread_text))
        closing_spread = float(spread_matches[-1].group(1)) if spread_matches else 0
        
        # Determine which team is the underdog based on the spread
        # The spread shown is typically from the team that covered
        # We need to figure out the full closing spread
        
        # Find the "Cover By" text to determine spread direction
        # Pattern: "Cover By +X" or similar
        cover_pattern = r'Cover By\s+([+-]?\d+\.?\d*)'
        cover_matches = list(re.finditer(cover_pattern, pre_text[-1500:]))
        
        # Find the spread line: "TeamAbbr +/-X" (the closing spread line)
        # This appears after the score
        spread_line_pattern = r'([A-Z]{2,3})\s+([+-]?\d+\.?\d*)'
        spread_line_matches = list(re.finditer(spread_line_pattern, pre_text[-1500:]))
        
        # The closing spread line is typically the last one before the total
        closing_spread_line = None
        for slm in spread_line_matches:
            if slm.group(1) in [away_abbr, home_abbr]:
                closing_spread_line = float(slm.group(2))
        
        games.append({
            'away_abbr': away_abbr,
            'away_score': away_score,
            'home_abbr': home_abbr,
            'home_score': home_score,
            'closing_total': closing_total,
            'closing_spread': closing_spread_line if closing_spread_line is not None else closing_spread,
            'ou_result': ou_result,
            'actual_total': actual_total,
        })
    
    return games


def parse_covers_simple(html_text):
    """Simpler parser that extracts game data from Covers.com HTML."""
    games = []
    
    # The most reliable pattern is:
    # "total score of X was **over Y**" or "total score of X was **under Y**"
    # This gives us the closing total directly
    
    # Find all game blocks
    # Each game block contains:
    # 1. Team names and scores
    # 2. Spread info
    # 3. Total info
    
    # Split the text by game blocks (look for "total score of" markers)
    total_pattern = r'total score of (\d+) was \*\*(over|under)\s+(\d+\.?\d*)\*\*'
    
    # Find all total matches
    total_matches = list(re.finditer(total_pattern, html_text))
    
    for i, tm in enumerate(total_matches):
        actual_total = int(tm.group(1))
        ou_result = tm.group(2)
        closing_total = float(tm.group(3))
        
        # The text before this total match contains the game info
        start_pos = total_matches[i-1].end() if i > 0 else 0
        game_text = html_text[start_pos:tm.start()]
        
        # Extract team scores from the game text
        # Pattern: ABBR **Score**
        score_pattern = r'([A-Z]{2,3})\s+\*\*(\d+)\*\*'
        score_matches = list(re.finditer(score_pattern, game_text))
        
        if len(score_matches) >= 2:
            # Last two are the final scores
            away_abbr = score_matches[-2].group(1)
            away_score = int(score_matches[-2].group(2))
            home_abbr = score_matches[-1].group(1)
            home_score = int(score_matches[-1].group(2))
        else:
            continue
        
        # Extract closing spread
        # Pattern: "covered the spread of **+/-X**"
        spread_covered = list(re.finditer(r'covered the spread of \*\*([+-]?\d+\.?\d*)\*\*', game_text))
        
        # Pattern: TeamAbbr +/-X (the closing spread line)
        spread_line = list(re.finditer(r'(?:^|\n)\s*([A-Z]{2,3})\s+([+-]?\d+\.?\d*)', game_text))
        
        # Find the spread line that's near the scores
        closing_spread = 0
        for sl in spread_line:
            if sl.group(1) in [away_abbr, home_abbr]:
                closing_spread = float(sl.group(2))
        
        # If we couldn't find the spread line, try the covered spread
        if closing_spread == 0 and spread_covered:
            closing_spread = float(spread_covered[-1].group(1))
        
        games.append({
            'away_abbr': away_abbr,
            'away_score': away_score,
            'home_abbr': home_abbr,
            'home_score': home_score,
            'closing_total': closing_total,
            'closing_spread': abs(closing_spread),
            'ou_result': ou_result,
            'actual_total': actual_total,
        })
    
    return games


if __name__ == '__main__':
    # Read HTML from stdin
    html = sys.stdin.read()
    games = parse_covers_simple(html)
    print(json.dumps(games, indent=2))
