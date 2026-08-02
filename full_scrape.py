#!/usr/bin/env python3
"""
Comprehensive Covers.com scraper for ABAKE USE backtesting.
Scrapes WNBA and NBA game results with closing lines.
"""
import re
import json
import time
import sys

# Dates we need to scrape
WNBA_MISSING_DATES = [
    "2026-05-11", "2026-05-16", "2026-05-24", "2026-05-26", "2026-05-28",
    "2026-06-09", "2026-06-16", "2026-06-22", "2026-06-23", "2026-06-28",
    "2026-06-29", "2026-07-01", "2026-07-03", "2026-07-04", "2026-07-05",
    "2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10",
    "2026-07-20", "2026-07-21", "2026-07-24", "2026-07-25", "2026-07-26",
    "2026-07-27", "2026-07-28", "2026-07-29", "2026-07-30", "2026-08-02",
]

# NBA dates - entire 2025-26 regular season (Oct 21, 2025 - Apr 13, 2026)
# We'll generate all dates in the season
from datetime import date, timedelta

def generate_nba_dates():
    start = date(2025, 10, 21)
    end = date(2026, 4, 13)
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates

NBA_DATES = generate_nba_dates()

def parse_covers_games(html_text, league="WNBA"):
    """Parse Covers.com matchups page to extract game data."""
    games = []
    
    # Split by game blocks using "total score of" as delimiter
    total_pattern = r'total score of (\d+) was \*\*(over|under)\s+(\d+\.?\d*)\*\*'
    total_matches = list(re.finditer(total_pattern, html_text))
    
    for i, tm in enumerate(total_matches):
        actual_total = int(tm.group(1))
        ou_result = tm.group(2)
        closing_total = float(tm.group(3))
        
        # Get the text block for this game
        start_pos = total_matches[i-1].end() if i > 0 else 0
        game_text = html_text[start_pos:tm.start()]
        
        # Extract team scores: ABBR **Score**
        score_pattern = r'([A-Z]{2,3})\s+\*\*(\d+)\*\*'
        score_matches = list(re.finditer(score_pattern, game_text))
        
        if len(score_matches) >= 2:
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
        spread_line = list(re.finditer(r'([A-Z]{2,3})\s+([+-]?\d+\.?\d*)', game_text))
        
        closing_spread = 0
        for sl in spread_line:
            if sl.group(1) in [away_abbr, home_abbr]:
                val = float(sl.group(2))
                if abs(val) > 0:
                    closing_spread = abs(val)
        
        if closing_spread == 0 and spread_covered:
            closing_spread = abs(float(spread_covered[-1].group(1)))
        
        # Determine which team is the favorite
        # The spread is from the perspective of the team that covered
        # "covered the spread of **-X**" means the favorite covered
        # "covered the spread of **+X**" means the underdog covered
        fav_team = None
        if spread_covered:
            spread_val = float(spread_covered[-1].group(1))
            if spread_val < 0:
                # The team that covered was the favorite
                # We need to figure out which team that was
                # The team that covered is typically the one with the spread line
                for sl in spread_line:
                    if sl.group(1) in [away_abbr, home_abbr]:
                        team_abbr = sl.group(1)
                        team_spread = float(sl.group(2))
                        if team_spread < 0:
                            fav_team = team_abbr
                            break
            elif spread_val > 0:
                # The underdog covered, so the other team is the favorite
                for sl in spread_line:
                    if sl.group(1) in [away_abbr, home_abbr]:
                        team_abbr = sl.group(1)
                        team_spread = float(sl.group(2))
                        if team_spread > 0:
                            # This is the underdog, the other team is the favorite
                            if team_abbr == away_abbr:
                                fav_team = home_abbr
                            else:
                                fav_team = away_abbr
                            break
        
        if fav_team is None:
            # Default: home team is favorite if spread > 0
            fav_team = home_abbr
        
        games.append({
            'away_abbr': away_abbr,
            'away_score': away_score,
            'home_abbr': home_abbr,
            'home_score': home_score,
            'closing_total': closing_total,
            'closing_spread': closing_spread,
            'fav_team': fav_team,
            'ou_result': ou_result,
            'actual_total': actual_total,
            'league': league,
        })
    
    return games


if __name__ == '__main__':
    print(f"WNBA dates to scrape: {len(WNBA_MISSING_DATES)}")
    print(f"NBA dates to scrape: {len(NBA_DATES)}")
    print(f"Total dates: {len(WNBA_MISSING_DATES) + len(NBA_DATES)}")
