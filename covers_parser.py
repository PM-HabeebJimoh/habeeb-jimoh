#!/usr/bin/env python3
"""
Covers.com NBA scraper — parses game data from Covers.com matchup pages.
V4: Uses the actual page structure to extract games correctly.
"""

import re
import json
import os

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

# All valid Covers.com NBA abbreviations
VALID_ABBRS = set(COVERS_NBA.keys())


def parse_covers_page(text, date_str):
    """
    Parse a Covers.com matchup page to extract game data.
    
    Page structure per game:
    1. "AwayTeam @ HomeTeam"
    2. "AWAY_ABBR **away_score**"
    3. "**away_score****Final** **home_score**"
    4. "HOME_ABBR **home_score**"
    5. "Cover By +X.X" or similar
    6. "ABBR -X.X" or "ABBR +X.X" (spread line)
    7. "o/u Margin"
    8. "uX.X" or "oX.X" (over/under margin)
    9. "under XXX.X" or "over XXX.X" (total line)
    """
    games = []
    
    # Split by "Boxscore" to separate games (each game has a "Boxscore" link)
    # Or use "Cover By" as a game separator
    # Actually, let's use the "o/u Margin" pattern as a game separator
    # because each game has exactly one
    
    # Better: find all game blocks using the "Final" pattern
    # Each game section starts with "Team @ Team" and ends before the next one
    
    # Strategy: Find all pairs of (away_abbr, away_score, home_abbr, home_score)
    # Then find the spread and total for each pair
    
    # Step 1: Find all score pairs
    # Pattern: "ABBR1 **score1**\n**score1****Final** **score2**\nABBR2 **score2**"
    
    # Find all "Final" markers
    final_positions = [(m.start(), m.end()) for m in re.finditer(r'\*\*Final\*\*', text)]
    
    for i, (final_start, final_end) in enumerate(final_positions):
        # Get text before and after "Final"
        # Look backwards for away team score
        before = text[max(0, final_start - 200):final_start]
        # Look forwards for home team score, spread, and total
        # The end of this game section is the start of the next game
        if i + 1 < len(final_positions):
            after_end = final_positions[i + 1][0]
        else:
            after_end = min(len(text), final_end + 800)
        after = text[final_end:after_end]
        
        # Extract away team score from before "Final"
        # Pattern: "ABBR **score**"
        away_matches = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', before)
        if not away_matches:
            continue
        
        # Take the last match (closest to "Final")
        away_abbr, away_score = away_matches[-1]
        
        # Extract home team score from after "Final"
        # Pattern: "ABBR **score**"
        home_matches = re.findall(r'([A-Z]{2,3})\s+\*\*(\d+)\*\*', after[:200])
        if not home_matches:
            continue
        
        # Take the first match (closest to "Final")
        home_abbr, home_score = home_matches[0]
        
        # Find the spread in the "after" section
        # Pattern: "ABBR -X.X" or "ABBR +X.X"
        # The spread appears after "Cover By" line
        spread_matches = re.findall(r'([A-Z]{2,3})\s+([+-]?\d+\.?\d*)', after[:400])
        
        # Find the total in the "after" section
        # Pattern: "under XXX.X" or "over XXX.X"
        total_match = re.search(r'(?:under|over)\s+(\d+\.?\d*)', after[:500], re.IGNORECASE)
        
        if not total_match or not spread_matches:
            continue
        
        total_value = float(total_match.group(1))
        
        # Find the correct spread (first one that's a valid spread value)
        market_spread = None
        favorite = None
        
        for team_abbr, spread_val in spread_matches:
            sv = float(spread_val)
            if abs(sv) < 0.5 or abs(sv) > 25:
                continue
            
            if sv < 0:
                # Negative spread = this team is the favorite
                favorite = team_abbr
                market_spread = abs(sv)
            elif sv > 0:
                # Positive spread = this team is the underdog
                if team_abbr == away_abbr:
                    favorite = home_abbr
                else:
                    favorite = away_abbr
                market_spread = abs(sv)
            break
        
        if market_spread is None or favorite is None:
            continue
        
        # Normalize abbreviations
        away = COVERS_NBA.get(away_abbr, away_abbr)
        home = COVERS_NBA.get(home_abbr, home_abbr)
        fav = COVERS_NBA.get(favorite, favorite)
        
        games.append({
            "date": date_str,
            "away": away,
            "away_score": int(away_score),
            "home": home,
            "home_score": int(home_score),
            "market_total": total_value,
            "market_spread": market_spread,
            "favorite": fav,
        })
    
    return games


if __name__ == "__main__":
    # Test with the actual Nov 24 data from Covers.com
    test_data = """Cleveland @ Toronto

CLE **99**

**99****Final** **110**

TOR **110**

Cover By +9.5

TOR -1.5

o/u Margin

u22.5

under 231.5

Boxscore

Detroit @ Indiana

DET **122**

**122****Final** **117**

IND **117**

Cover By +5

IND +10

o/u Margin

o2

over 237

Boxscore

New York @ Brooklyn

NY **113**

**113****Final** **100**

BK **100**

Cover By +0.5

NY -12.5

o/u Margin

u15.5

under 228.5

Boxscore

Dallas @ Miami

DAL **102**

**102****Final** **106**

MIA **106**

Cover By +3.5

DAL +7.5

o/u Margin

u32

under 240

Boxscore"""
    
    print("Testing v4 parser:")
    games = parse_covers_page(test_data, "2025-11-24")
    for g in games:
        print(f"  {g['away']} {g['away_score']} @ {g['home']} {g['home_score']} | Fav: {g['favorite']} -{g['market_spread']} | Total: {g['market_total']}")
