#!/usr/bin/env python3
"""
ABAKE USE Engine — NBA 2025-26 Data Collection Script
Collects ALL game scores and closing lines from Yahoo Sports API.

Sources:
1. Yahoo Game IDs API — gets all game IDs for the season
2. Yahoo Game Odds API — gets closing lines (spread, total) for each game
3. Landofbasketball.com — gets ALL game scores as backup

This script uses 100% REAL data — no synthetic, simulated, or estimated values.
"""

import json
import re
import time
import os
import sys
from datetime import datetime, timedelta

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://sports.yahoo.com/",
}

# Team name → abbreviation mapping
TEAM_NAME_MAP = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GSW", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "L.A. Clippers": "LAC", "LA Lakers": "LAL",
    "L.A. Lakers": "LAL", "Los Angeles": "LAL", "Memphis": "MEM", "Miami": "MIA",
    "Milwaukee": "MIL", "Minnesota": "MIN", "New Orleans": "NOP", "New York": "NYK",
    "Oklahoma City": "OKC", "Orlando": "ORL", "Philadelphia": "PHI", "Phoenix": "PHX",
    "Portland": "POR", "Sacramento": "SAC", "San Antonio": "SAS", "Toronto": "TOR",
    "Utah": "UTA", "Washington": "WAS",
}

# Yahoo team ID → abbreviation mapping
YAHOO_TEAM_ID_MAP = {
    "nba.t.1": "ATL", "nba.t.2": "BOS", "nba.t.3": "NOP", "nba.t.4": "CHI",
    "nba.t.5": "CLE", "nba.t.6": "DAL", "nba.t.7": "DEN", "nba.t.8": "DET",
    "nba.t.9": "GSW", "nba.t.10": "HOU", "nba.t.11": "IND", "nba.t.12": "LAC",
    "nba.t.13": "LAL", "nba.t.14": "MEM", "nba.t.15": "MIA", "nba.t.16": "MIL",
    "nba.t.17": "MIN", "nba.t.18": "BKN", "nba.t.19": "NYK", "nba.t.20": "ORL",
    "nba.t.21": "PHI", "nba.t.22": "PHX", "nba.t.23": "POR", "nba.t.24": "SAC",
    "nba.t.25": "OKC", "nba.t.26": "SAS", "nba.t.27": "TOR", "nba.t.28": "UTA",
    "nba.t.29": "WAS", "nba.t.30": "CHA",
}


def get_all_game_ids():
    """Get all NBA game IDs for the 2025-26 season from Yahoo Sports API."""
    url = "https://graphite.sports.yahoo.com/v1/query/shangrila/leagueGameIdsByDate"
    params = {
        "startRange": "2025-10-21",
        "endRange": "2026-04-13",
        "leagues": "nba",
    }
    
    game_ids = []
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        data = resp.json()
        games = data.get("data", {}).get("leagues", [{}])[0].get("games", [])
        for g in games:
            gid = g.get("gameId", "")
            if gid.startswith("nba.g."):
                game_ids.append(gid)
        print(f"  ✅ Got {len(game_ids)} game IDs from Yahoo API")
    except Exception as e:
        print(f"  ❌ Error getting game IDs: {e}")
    
    return game_ids


def get_game_odds(game_id):
    """Get closing lines for a single game from Yahoo Sports API."""
    url = f"https://sports.yahoo.com/site/api/resource/sports.graphite.gameOdds;dataType=graphite;endpoint=graphite;gameIds={game_id}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        data = resp.json()
        games = data.get("data", {}).get("games", [])
        if not games:
            return None
        
        game = games[0]
        odds = game.get("gameOddsSummary", {})
        pregame_display = odds.get("pregameOddsDisplay", "")
        favorite_id = odds.get("favoriteId", "")
        underdog_pred_score = odds.get("underdogTeamPredictedScore")
        favorite_pred_score = odds.get("favoriteTeamPredictedScore")
        
        away = game.get("awayTeam", {})
        home = game.get("homeTeam", {})
        away_abbr = away.get("abbreviation", "")
        home_abbr = home.get("abbreviation", "")
        away_name = away.get("displayName", "")
        home_name = home.get("displayName", "")
        
        # Parse pregameOddsDisplay: "-6.5, O/U 225.5"
        spread = None
        total = None
        if pregame_display:
            spread_match = re.match(r'([+-]?\d+\.?\d*)', pregame_display)
            total_match = re.search(r'O/U\s+(\d+\.?\d*)', pregame_display)
            if spread_match:
                spread = float(spread_match.group(1))
            if total_match:
                total = float(total_match.group(1))
        
        # Determine favorite
        favorite_abbr = YAHOO_TEAM_ID_MAP.get(favorite_id, "")
        
        return {
            "game_id": game_id,
            "away_abbr": away_abbr,
            "home_abbr": home_abbr,
            "away_name": away_name,
            "home_name": home_name,
            "spread": spread,
            "total": total,
            "favorite_id": favorite_id,
            "favorite_abbr": favorite_abbr,
            "underdog_pred_score": underdog_pred_score,
            "favorite_pred_score": favorite_pred_score,
            "pregame_display": pregame_display,
        }
    except Exception as e:
        return None


def get_landofbasketball_scores():
    """Get ALL NBA 2025-26 game scores from landofbasketball.com."""
    url = "https://www.landofbasketball.com/results/2025_2026_scores_full.htm"
    
    games = []
    try:
        resp = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=30)
        text = resp.text
        
        # Parse the HTML to extract game data
        # Format: "Houston Rockets<br>[124]<br>-<br>Oklahoma City Thunder<br>[**125**]"
        # Bold score = winner
        
        # Find all date headings and game entries
        date_pattern = r'####\s+\[([A-Z][a-z]+ \d+, \d{4})\]'
        date_matches = list(re.finditer(date_pattern, text))
        
        # Alternative: parse by looking for game patterns
        # Pattern: Team Name<br>[score]<br>-<br>Team Name<br>[score]
        game_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:Rockets|Thunder|Warriors|Lakers|Cavaliers|Nets|Hornets|Heat|Magic|Raptors|Hawks|76ers|Celtics|Pistons|Bulls|Pelicans|Grizzlies|Wizards|Bucks|Clippers|Jazz|Spurs|Mavericks|Kings|Suns|Timberwolves|Trail Blazers|Nuggets|Pacers)?\s*<br>\[(\d+)\]<br>-<br>([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:Rockets|Thunder|Warriors|Lakers|Cavaliers|Nets|Hornets|Heat|Magic|Raptors|Hawks|76ers|Celtics|Pistons|Bulls|Pelicans|Grizzlies|Wizards|Bucks|Clippers|Jazz|Spurs|Mavericks|Kings|Suns|Timberwolves|Trail Blazers|Nuggets|Pacers)?\s*<br>\[\*{0,2}(\d+)\*{0,2}\]'
        
        # Simpler approach: find all score patterns
        # The page has format like: "Houston Rockets<br>[124]<br>-<br>Oklahoma City Thunder<br>[**125**]"
        # Let's parse it differently
        
        # Find all team-score pairs
        # Each game has: Away Team<br>[score]<br>-<br>Home Team<br>[**score**]
        # Bold (** **) means winner
        
        # Split by date headers
        sections = re.split(r'####\s+\[', text)
        
        for section in sections[1:]:  # Skip the first empty section
            date_match = re.match(r'([A-Z][a-z]+ \d+, \d{4})\]', section)
            if not date_match:
                continue
            date_str = date_match.group(1)
            
            # Find games in this section
            # Pattern: TeamName<br>[score]<br>-<br>TeamName<br>[score] or [**score**]
            game_matches = re.findall(
                r'([A-Z][a-z][a-z ]+(?:Rockets|Thunder|Warriors|Lakers|Cavaliers|Nets|Hornets|Heat|Magic|Raptors|Hawks|76ers|Celtics|Pistons|Bulls|Pelicans|Grizzlies|Wizards|Bucks|Clippers|Jazz|Spurs|Mavericks|Kings|Suns|Timberwolves|Trail Blazers|Nuggets|Pacers))\s*<br>\[(\d+)\]<br>-<br>([A-Z][a-z][a-z ]+(?:Rockets|Thunder|Warriors|Lakers|Cavaliers|Nets|Hornets|Heat|Magic|Raptors|Hawks|76ers|Celtics|Pistons|Bulls|Pelicans|Grizzlies|Wizards|Bucks|Clippers|Jazz|Spurs|Mavericks|Kings|Suns|Timberwolves|Trail Blazers|Nuggets|Pacers))\s*<br>\[\*{0,2}(\d+)\*{0,2}\]',
                section
            )
            
            for gm in game_matches:
                away_name = gm[0].strip()
                away_score = int(gm[1])
                home_name = gm[2].strip()
                home_score = int(gm[3])
                
                # Map team names to abbreviations
                away_abbr = TEAM_NAME_MAP.get(away_name, away_name)
                home_abbr = TEAM_NAME_MAP.get(home_name, home_name)
                
                games.append({
                    "date": date_str,
                    "away": away_abbr,
                    "away_score": away_score,
                    "home": home_abbr,
                    "home_score": home_score,
                })
        
        print(f"  ✅ Got {len(games)} game scores from landofbasketball.com")
    except Exception as e:
        print(f"  ❌ Error getting scores: {e}")
    
    return games


def main():
    print("=" * 80)
    print("  🏀 ABAKE USE — NBA 2025-26 Data Collection")
    print("=" * 80)
    
    # Step 1: Get all game IDs
    print("\n  📋 Step 1: Getting all game IDs from Yahoo Sports API...")
    game_ids = get_all_game_ids()
    
    if not game_ids:
        print("  ❌ No game IDs found. Exiting.")
        return
    
    # Save game IDs
    with open("scraped_data/nba_game_ids.json", "w") as f:
        json.dump(game_ids, f, indent=2)
    print(f"  📁 Saved {len(game_ids)} game IDs to scraped_data/nba_game_ids.json")
    
    # Step 2: Get closing lines for each game
    print(f"\n  📋 Step 2: Getting closing lines for {len(game_ids)} games...")
    odds_data = []
    success = 0
    fail = 0
    
    for i, gid in enumerate(game_ids):
        if (i + 1) % 50 == 0:
            print(f"  📊 Progress: {i+1}/{len(game_ids)} ({success} success, {fail} fail)")
        
        odds = get_game_odds(gid)
        if odds and odds.get("total") is not None:
            odds_data.append(odds)
            success += 1
        else:
            fail += 1
        
        # Rate limiting
        time.sleep(0.1)
    
    print(f"\n  ✅ Got closing lines for {success} games ({fail} failed)")
    
    # Save odds data
    with open("scraped_data/nba_yahoo_odds.json", "w") as f:
        json.dump(odds_data, f, indent=2)
    print(f"  📁 Saved odds data to scraped_data/nba_yahoo_odds.json")
    
    # Step 3: Get game scores from landofbasketball.com
    print(f"\n  📋 Step 3: Getting game scores from landofbasketball.com...")
    scores = get_landofbasketball_scores()
    
    # Save scores
    with open("scraped_data/nba_scores.json", "w") as f:
        json.dump(scores, f, indent=2)
    print(f"  📁 Saved scores to scraped_data/nba_scores.json")
    
    # Step 4: Combine data
    print(f"\n  📋 Step 4: Combining odds and scores...")
    combined = combine_data(odds_data, scores)
    
    # Save combined data
    with open("scraped_data/nba_2025_26_combined_v3.json", "w") as f:
        json.dump(combined, f, indent=2)
    print(f"  📁 Saved combined data to scraped_data/nba_2025_26_combined_v3.json")
    
    print(f"\n  🏆 Summary:")
    print(f"    Game IDs: {len(game_ids)}")
    print(f"    Odds data: {len(odds_data)}")
    print(f"    Scores: {len(scores)}")
    print(f"    Combined: {len(combined)}")


def combine_data(odds_data, scores):
    """Combine Yahoo odds data with landofbasketball.com scores."""
    # Build a lookup from scores by (away, home, date)
    scores_lookup = {}
    for s in scores:
        # Try multiple key formats
        key1 = (s["away"], s["home"])
        key2 = (s["away"], s["home"], s["date"])
        scores_lookup[key1] = s
        scores_lookup[key2] = s
    
    combined = []
    matched = 0
    unmatched = 0
    
    for odds in odds_data:
        away_abbr = odds["away_abbr"]
        home_abbr = odds["home_abbr"]
        
        # Map Yahoo abbreviations to our format
        away_map = {"GS": "GSW", "NY": "NYK", "BK": "BKN", "NO": "NOP", "SA": "SAS", "PHO": "PHX", "WSH": "WAS"}
        away = away_map.get(away_abbr, away_abbr)
        home = away_map.get(home_abbr, home_abbr)
        
        # Try to find matching score
        score = scores_lookup.get((away, home))
        
        if score:
            matched += 1
            combined.append({
                "date": score["date"],
                "away": away,
                "away_score": score["away_score"],
                "home": home,
                "home_score": score["home_score"],
                "market_total": odds["total"],
                "market_spread": abs(odds["spread"]) if odds["spread"] else None,
                "favorite": odds["favorite_abbr"],
                "game_id": odds["game_id"],
            })
        else:
            unmatched += 1
    
    print(f"  ✅ Matched: {matched}, Unmatched: {unmatched}")
    return combined


if __name__ == "__main__":
    main()
