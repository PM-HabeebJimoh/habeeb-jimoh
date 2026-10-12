#!/usr/bin/env python3
"""
ABAKE USE — Yahoo NBA Game IDs + Odds Scraper
Uses fetch_page tool output to extract game IDs and odds.
"""

import json
import re
import sys

# We'll build the game IDs list by parsing the Yahoo API response
# The game IDs API returns all game IDs in a single response (15 chunks)

def extract_game_ids_from_text(text):
    """Extract game IDs from Yahoo API response text."""
    pattern = r'"gameId":"(nba\.g\.\d+)"'
    return re.findall(pattern, text)

def extract_odds_from_text(text):
    """Extract odds data from Yahoo game odds API response."""
    try:
        # Remove markdown code block markers
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        games = data.get("data", {}).get("games", [])
        if not games:
            return None
        
        game = games[0]
        odds = game.get("gameOddsSummary", {})
        away = game.get("awayTeam", {})
        home = game.get("homeTeam", {})
        
        return {
            "game_id": game.get("gameId", ""),
            "away_abbr": away.get("abbreviation", ""),
            "home_abbr": home.get("abbreviation", ""),
            "pregame_display": odds.get("pregameOddsDisplay", ""),
            "favorite_id": odds.get("favoriteId", ""),
            "underdog_pred_score": odds.get("underdogTeamPredictedScore"),
            "favorite_pred_score": odds.get("favoriteTeamPredictedScore"),
        }
    except Exception as e:
        return None

if __name__ == "__main__":
    # This script is meant to be called from the fetch_page-based workflow
    pass
