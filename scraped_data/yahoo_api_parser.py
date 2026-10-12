
import json, re

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

def parse_game_ids(json_text):
    data = json.loads(json_text)
    games = []
    for league in data.get("data", {}).get("leagues", []):
        for game in league.get("games", []):
            games.append(game["gameId"])
    return games

def parse_game_odds(json_text):
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
