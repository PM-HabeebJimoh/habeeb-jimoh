#!/usr/bin/env python3
"""
Build a complete NBA 2025-26 season dataset using:
1. Yahoo game IDs API for all game IDs
2. Yahoo game odds API for closing lines (spread, total, favorite)
3. ESPN scoreboard API for game scores

This script processes the raw data files that were fetched using fetch_page.
"""

import json
import re
import os
from datetime import datetime, timedelta

# ============================================================
# Team abbreviation mappings
# ============================================================
YAHOO_TEAM_MAP = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GSW", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "LA Lakers": "LAL", "Memphis": "MEM", "Miami": "MIA",
    "Milwaukee": "MIL", "Minnesota": "MIN", "New Orleans": "NOP", "New York": "NYK",
    "Oklahoma City": "OKC", "Orlando": "ORL", "Philadelphia": "PHI",
    "Phoenix": "PHX", "Portland": "POR", "Sacramento": "SAC",
    "San Antonio": "SAS", "Toronto": "TOR", "Utah": "UTA", "Washington": "WAS",
}

ESPN_TEAM_MAP = {
    "ATL": "ATL", "BOS": "BOS", "BKN": "BKN", "BK": "BKN", "CHA": "CHA",
    "CHI": "CHI", "CLE": "CLE", "DAL": "DAL", "DEN": "DEN", "DET": "DET",
    "GS": "GSW", "GSW": "GSW", "HOU": "HOU", "IND": "IND", "LAC": "LAC",
    "LAL": "LAL", "LA": "LAL", "MEM": "MEM", "MIA": "MIA", "MIL": "MIL",
    "MIN": "MIN", "NOP": "NOP", "NO": "NOP", "NY": "NYK", "NYK": "NYK",
    "OKC": "OKC", "ORL": "ORL", "PHI": "PHI", "PHO": "PHX", "PHX": "PHX",
    "POR": "POR", "SAC": "SAC", "SA": "SAS", "SAS": "SAS", "TOR": "TOR",
    "UTA": "UTA", "WAS": "WAS", "WSH": "WAS",
}

COVERS_NBA = {
    "ATL": "ATL", "BOS": "BOS", "BK": "BKN", "BKN": "BKN", "CHA": "CHA", "CHI": "CHI",
    "CLE": "CLE", "DAL": "DAL", "DEN": "DEN", "DET": "DET", "GS": "GSW", "GSW": "GSW",
    "HOU": "HOU", "IND": "IND", "LAC": "LAC", "LAL": "LAL", "LA": "LAL", "MEM": "MEM",
    "MIA": "MIA", "MIL": "MIL", "MIN": "MIN", "NOP": "NOP", "NO": "NOP", "NY": "NYK",
    "NYK": "NYK", "OKC": "OKC", "ORL": "ORL", "PHI": "PHI", "PHO": "PHX", "PHX": "PHX",
    "POR": "POR", "SAC": "SAC", "SA": "SAS", "SAS": "SAS", "TOR": "TOR", "UTA": "UTA",
    "WAS": "WAS", "WSH": "WAS",
}

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


def parse_yahoo_game_ids(json_text):
    """Parse Yahoo game IDs API response."""
    data = json.loads(json_text)
    games = []
    for league in data.get("data", {}).get("leagues", []):
        for game in league.get("games", []):
            games.append({
                "game_id": game["gameId"],
                "start_date": game.get("startDate", ""),
                "status": game.get("status", ""),
            })
    return games


def parse_yahoo_game_odds(json_text):
    """Parse Yahoo game odds API response."""
    data = json.loads(json_text)
    results = []
    for game in data.get("data", {}).get("games", []):
        odds = game.get("gameOddsSummary", {})
        away = game.get("awayTeam", {})
        home = game.get("homeTeam", {})
        
        pregame_odds = odds.get("pregameOddsDisplay", "")
        fav_id = odds.get("favoriteId", "")
        
        spread = None
        total = None
        match = re.match(r'([+-]?\d+\.?\d*),\s*O/U\s+(\d+\.?\d*)', pregame_odds)
        if match:
            spread = float(match.group(1))
            total = float(match.group(2))
        
        away_name = away.get("displayName", "")
        home_name = home.get("displayName", "")
        away_abbr = away.get("abbreviation", "")
        home_abbr = home.get("abbreviation", "")
        away_mapped = YAHOO_TEAM_MAP.get(away_name, away_abbr)
        home_mapped = YAHOO_TEAM_MAP.get(home_name, home_abbr)
        
        favorite = None
        if fav_id:
            if fav_id == away.get("teamId"):
                favorite = away_mapped
            elif fav_id == home.get("teamId"):
                favorite = home_mapped
        
        results.append({
            "game_id": game.get("gameId", ""),
            "away": away_mapped,
            "home": home_mapped,
            "market_total": total,
            "market_spread": abs(spread) if spread else None,
            "favorite": favorite,
            "spread_raw": spread,
            "pregame_odds": pregame_odds,
        })
    return results


def parse_covers_page(text, date_str):
    """Parse Covers.com matchup page and extract game data."""
    games = []
    
    # Find all spread matches (these anchor each game)
    spread_pattern = r'([\w.\s]+?)covered the spread of\s+\*\*([+-]?\d+\.?\d*)\*\*'
    total_pattern = r'total score of (\d+) was \*\*(?:over|under)\s+(\d+\.?\d*)\*\*'
    score_pattern = r'([A-Z]{2,3})\s+\*\*(\d+)\*\*'
    
    spread_matches = list(re.finditer(spread_pattern, text))
    total_matches = list(re.finditer(total_pattern, text))
    
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
        pre_text = text[max(0, spread_match.start() - 1500):spread_match.start()]
        score_matches = list(re.finditer(score_pattern, pre_text))
        
        if len(score_matches) >= 2:
            away_match = score_matches[-2]
            home_match = score_matches[-1]
            
            away_abbr = away_match.group(1)
            away_score = int(away_match.group(2))
            home_abbr = home_match.group(1)
            home_score = int(home_match.group(2))
            
            if away_score > 300 or home_score > 300:
                continue
            
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


def parse_espn_scoreboard(json_text, date_str):
    """Parse ESPN scoreboard API response."""
    data = json.loads(json_text)
    games = []
    
    for event in data.get("events", []):
        for comp in event.get("competitions", []):
            competitors = comp.get("competitors", [])
            if len(competitors) != 2:
                continue
            
            away_team = None
            home_team = None
            for team in competitors:
                abbr = team["team"]["abbreviation"]
                score = int(team["score"])
                mapped = ESPN_TEAM_MAP.get(abbr, abbr)
                if team["homeAway"] == "away":
                    away_team = {"abbr": mapped, "score": score}
                else:
                    home_team = {"abbr": mapped, "score": score}
            
            if away_team and home_team:
                games.append({
                    "date": date_str,
                    "away": away_team["abbr"],
                    "away_score": away_team["score"],
                    "home": home_team["abbr"],
                    "home_score": home_team["score"],
                })
    
    return games


if __name__ == "__main__":
    # Test with existing data
    print("Covers parser module loaded successfully")
    print(f"Team mappings: {len(YAHOO_TEAM_MAP)} Yahoo, {len(ESPN_TEAM_MAP)} ESPN, {len(COVERS_NBA)} Covers")
