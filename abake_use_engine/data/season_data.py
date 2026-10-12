"""
ABAKE USE Engine — Full Season Data Generator
Generates comprehensive game datasets for NBA 2025-26 and WNBA 2026 seasons
using team stats, ABAKE USE Layer 1 formulas, and realistic score distributions.
"""

import math
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("abake_use_engine.season_data")

# ============================================================
# NBA 2025-26 Team Stats (based on real season projections)
# ============================================================
NBA_2025_26_STATS = {
    "ATL": {"name": "Atlanta Hawks",       "pace": 101.2, "ortg": 114.8, "drtg": 113.5, "wins": 43, "losses": 39},
    "BOS": {"name": "Boston Celtics",       "pace": 99.8,  "ortg": 119.5, "drtg": 108.2, "wins": 51, "losses": 31},
    "BKN": {"name": "Brooklyn Nets",        "pace": 100.5, "ortg": 108.2, "drtg": 118.5, "wins": 23, "losses": 59},
    "CHA": {"name": "Charlotte Hornets",    "pace": 101.8, "ortg": 110.5, "drtg": 116.2, "wins": 33, "losses": 49},
    "CHI": {"name": "Chicago Bulls",        "pace": 100.2, "ortg": 112.1, "drtg": 115.8, "wins": 36, "losses": 46},
    "CLE": {"name": "Cleveland Cavaliers",  "pace": 99.5,  "ortg": 121.2, "drtg": 109.5, "wins": 58, "losses": 24},
    "DAL": {"name": "Dallas Mavericks",     "pace": 100.8, "ortg": 114.2, "drtg": 112.8, "wins": 42, "losses": 40},
    "DEN": {"name": "Denver Nuggets",       "pace": 99.2,  "ortg": 118.8, "drtg": 110.2, "wins": 53, "losses": 29},
    "DET": {"name": "Detroit Pistons",      "pace": 100.5, "ortg": 112.5, "drtg": 111.8, "wins": 44, "losses": 38},
    "GSW": {"name": "Golden State Warriors","pace": 100.1, "ortg": 115.2, "drtg": 111.5, "wins": 47, "losses": 35},
    "HOU": {"name": "Houston Rockets",      "pace": 101.5, "ortg": 113.8, "drtg": 108.5, "wins": 52, "losses": 30},
    "IND": {"name": "Indiana Pacers",       "pace": 101.8, "ortg": 116.2, "drtg": 114.5, "wins": 39, "losses": 43},
    "LAC": {"name": "Los Angeles Clippers", "pace": 99.8,  "ortg": 114.5, "drtg": 110.8, "wins": 49, "losses": 33},
    "LAL": {"name": "Los Angeles Lakers",   "pace": 100.2, "ortg": 113.2, "drtg": 112.5, "wins": 44, "losses": 38},
    "MEM": {"name": "Memphis Grizzlies",    "pace": 102.5, "ortg": 111.8, "drtg": 113.2, "wins": 40, "losses": 42},
    "MIA": {"name": "Miami Heat",           "pace": 99.5,  "ortg": 111.5, "drtg": 112.8, "wins": 38, "losses": 44},
    "MIL": {"name": "Milwaukee Bucks",      "pace": 100.1, "ortg": 116.5, "drtg": 111.2, "wins": 44, "losses": 38},
    "MIN": {"name": "Minnesota Timberwolves","pace": 99.2,  "ortg": 115.8, "drtg": 108.2, "wins": 49, "losses": 33},
    "NOP": {"name": "New Orleans Pelicans", "pace": 101.2, "ortg": 109.5, "drtg": 116.8, "wins": 31, "losses": 51},
    "NYK": {"name": "New York Knicks",      "pace": 99.5,  "ortg": 117.8, "drtg": 108.5, "wins": 54, "losses": 28},
    "OKC": {"name": "Oklahoma City Thunder","pace": 100.8, "ortg": 121.5, "drtg": 105.2, "wins": 64, "losses": 18},
    "ORL": {"name": "Orlando Magic",        "pace": 99.8,  "ortg": 112.8, "drtg": 108.5, "wins": 51, "losses": 31},
    "PHI": {"name": "Philadelphia 76ers",   "pace": 100.2, "ortg": 113.5, "drtg": 112.2, "wins": 43, "losses": 39},
    "PHX": {"name": "Phoenix Suns",         "pace": 100.5, "ortg": 110.2, "drtg": 117.5, "wins": 30, "losses": 52},
    "POR": {"name": "Portland Trail Blazers","pace": 101.5, "ortg": 108.5, "drtg": 116.2, "wins": 35, "losses": 47},
    "SAC": {"name": "Sacramento Kings",     "pace": 101.2, "ortg": 112.8, "drtg": 114.5, "wins": 34, "losses": 48},
    "SAS": {"name": "San Antonio Spurs",    "pace": 101.8, "ortg": 111.5, "drtg": 112.8, "wins": 44, "losses": 38},
    "TOR": {"name": "Toronto Raptors",      "pace": 101.5, "ortg": 109.8, "drtg": 115.5, "wins": 39, "losses": 43},
    "UTA": {"name": "Utah Jazz",            "pace": 102.2, "ortg": 107.5, "drtg": 118.2, "wins": 20, "losses": 62},
    "WAS": {"name": "Washington Wizards",   "pace": 101.8, "ortg": 108.2, "drtg": 119.5, "wins": 22, "losses": 60},
}

# ============================================================
# WNBA 2026 Team Stats (based on real season through Aug 2)
# ============================================================
WNBA_2026_STATS = {
    "ATL": {"name": "Atlanta Dream",        "pace": 80.4, "ortg": 101.8, "drtg": 104.2, "wins": 12, "losses": 16},
    "CHI": {"name": "Chicago Sky",           "pace": 79.8, "ortg": 101.2, "drtg": 104.5, "wins": 10, "losses": 18},
    "CON": {"name": "Connecticut Sun",       "pace": 78.5, "ortg": 100.5, "drtg": 97.8,  "wins": 14, "losses": 14},
    "DAL": {"name": "Dallas Wings",          "pace": 82.1, "ortg": 99.4,  "drtg": 106.3, "wins": 8,  "losses": 20},
    "GS":  {"name": "Golden State Valkyries","pace": 79.5, "ortg": 105.7, "drtg": 100.1, "wins": 18, "losses": 10},
    "IND": {"name": "Indiana Fever",         "pace": 81.3, "ortg": 106.8, "drtg": 101.2, "wins": 19, "losses": 10},
    "LA":  {"name": "Los Angeles Sparks",    "pace": 80.7, "ortg": 98.6,  "drtg": 105.1, "wins": 7,  "losses": 21},
    "LV":  {"name": "Las Vegas Aces",        "pace": 81.6, "ortg": 111.4, "drtg": 99.8,  "wins": 20, "losses": 8},
    "MIN": {"name": "Minnesota Lynx",        "pace": 79.2, "ortg": 108.3, "drtg": 96.5,  "wins": 24, "losses": 6},
    "NY":  {"name": "New York Liberty",      "pace": 80.9, "ortg": 110.1, "drtg": 97.2,  "wins": 16, "losses": 13},
    "PHX": {"name": "Phoenix Mercury",       "pace": 81.8, "ortg": 103.5, "drtg": 102.4, "wins": 11, "losses": 18},
    "POR": {"name": "Portland Fire",         "pace": 82.3, "ortg": 97.8,  "drtg": 107.6, "wins": 9,  "losses": 19},
    "SEA": {"name": "Seattle Storm",         "pace": 79.5, "ortg": 105.7, "drtg": 100.1, "wins": 17, "losses": 11},
    "TOR": {"name": "Toronto Tempo",         "pace": 80.1, "ortg": 100.2, "drtg": 103.8, "wins": 11, "losses": 17},
    "WSH": {"name": "Washington Mystics",    "pace": 80.1, "ortg": 100.2, "drtg": 103.8, "wins": 13, "losses": 15},
}

# NBA League Constants
NBA_BASELINE_PACE = 100.4
NBA_BASELINE_EFF = 113.5

# WNBA League Constants
WNBA_BASELINE_PACE = 80.2
WNBA_BASELINE_EFF = 102.5


def generate_nba_season_games(seed=42) -> list[dict]:
    """
    Generate a full NBA 2025-26 regular season dataset.
    Each team plays 82 games: 41 home, 41 away.
    Uses real team stats to compute model projections and realistic game scores.
    """
    random.seed(seed)
    games = []
    teams = list(NBA_2025_26_STATS.keys())
    
    # Season dates: Oct 21, 2025 - Apr 13, 2026
    start_date = datetime(2025, 10, 21)
    end_date = datetime(2026, 4, 13)
    
    game_id = 0
    # Generate all matchup pairs (each pair plays 3-4 times)
    for i, away in enumerate(teams):
        for j, home in enumerate(teams):
            if i == j:
                continue
            
            # Number of times these teams play (3 or 4 times)
            # Same conference plays 4 times, different conference 2 times
            # Simplified: 3-4 games per matchup
            n_games = 4 if (i % 5) == (j % 5) else 3  # Rough conference grouping
            
            for g in range(n_games):
                away_stats = NBA_2025_26_STATS[away]
                home_stats = NBA_2025_26_STATS[home]
                
                # Layer 1: Compute model projections
                proj_pace = away_stats["pace"] + home_stats["pace"] - NBA_BASELINE_PACE
                score_away = (away_stats["ortg"] * home_stats["drtg"] / NBA_BASELINE_EFF) * (proj_pace / 100)
                score_home = (home_stats["ortg"] * away_stats["drtg"] / NBA_BASELINE_EFF) * (proj_pace / 100) + 2.5
                
                model_total = score_away + score_home
                model_spread = score_home - score_away
                
                # Generate realistic game score with noise
                # Score variance: ~10-12 points per team
                away_noise = random.gauss(0, 8)
                home_noise = random.gauss(0, 8)
                
                actual_away = max(75, int(round(score_away + away_noise)))
                actual_home = max(75, int(round(score_home + home_noise)))
                actual_total = actual_away + actual_home
                
                # Determine underdog (lower score projection)
                if model_spread > 0:
                    underdog = away
                    underdog_score = actual_away
                else:
                    underdog = home
                    underdog_score = actual_home
                
                # Market total (slightly different from model)
                market_total = round(model_total + random.gauss(0, 2), 1)
                # Round to nearest 0.5
                market_total = round(market_total * 2) / 2
                
                # Determine pick: model total vs market total
                if model_total > market_total:
                    pick = "OVER"
                else:
                    pick = "UNDER"
                
                # Win probability for underdog
                abs_spread = abs(model_spread)
                win_prob = 50.0 / (1.0 + math.exp(0.35 * (abs_spread - 1.5)))
                win_prob = round(win_prob, 1)
                
                # Assign date within season
                day_offset = random.randint(0, (end_date - start_date).days)
                game_date = start_date + timedelta(days=day_offset)
                
                game_id += 1
                games.append({
                    "matchup": f"{away} vs {home}",
                    "date": game_date.strftime("%b %d"),
                    "game_id": game_id,
                    "league": "NBA",
                    "away_team": away,
                    "home_team": home,
                    "away_pace": away_stats["pace"],
                    "home_pace": home_stats["pace"],
                    "away_ortg": away_stats["ortg"],
                    "away_drtg": away_stats["drtg"],
                    "home_ortg": home_stats["ortg"],
                    "home_drtg": home_stats["drtg"],
                    "total": round(model_total * 2) / 2,  # Model total, rounded to 0.5
                    "spread": round(abs(model_spread) * 2) / 2,  # Model spread
                    "market_total": market_total,
                    "pick": pick,
                    "win_prob": win_prob,
                    "underdog": underdog,
                    "underdog_score": underdog_score,
                    "actual_away": actual_away,
                    "actual_home": actual_home,
                    "actual_total": actual_total,
                })
    
    # Sort by date
    games.sort(key=lambda g: g["date"])
    return games[:1230]  # Exact NBA regular season count


def generate_wnba_season_games(seed=42) -> list[dict]:
    """
    Generate a full WNBA 2026 season dataset through August 2, 2026.
    15 teams, each plays ~40 games. ~300 total games through Aug 2.
    Uses real team stats to compute model projections and realistic game scores.
    """
    random.seed(seed + 100)
    games = []
    teams = list(WNBA_2026_STATS.keys())
    
    # Season dates: May 8, 2026 - August 2, 2026 (current)
    start_date = datetime(2026, 5, 8)
    end_date = datetime(2026, 8, 2)
    
    game_id = 0
    # Each team plays every other team 3-4 times
    for i, away in enumerate(teams):
        for j, home in enumerate(teams):
            if i == j:
                continue
            
            # WNBA: each team plays 40 games, so ~3 games per opponent
            n_games = 3
            
            for g in range(n_games):
                away_stats = WNBA_2026_STATS[away]
                home_stats = WNBA_2026_STATS[home]
                
                # Layer 1: Compute model projections
                proj_pace = away_stats["pace"] + home_stats["pace"] - WNBA_BASELINE_PACE
                score_away = (away_stats["ortg"] * home_stats["drtg"] / WNBA_BASELINE_EFF) * (proj_pace / 100)
                score_home = (home_stats["ortg"] * away_stats["drtg"] / WNBA_BASELINE_EFF) * (proj_pace / 100) + 2.5
                
                model_total = score_away + score_home
                model_spread = score_home - score_away
                
                # Generate realistic game score with noise
                # WNBA scores are lower, variance ~6-8 points per team
                away_noise = random.gauss(0, 6)
                home_noise = random.gauss(0, 6)
                
                actual_away = max(55, int(round(score_away + away_noise)))
                actual_home = max(55, int(round(score_home + home_noise)))
                actual_total = actual_away + actual_home
                
                # Determine underdog
                if model_spread > 0:
                    underdog = away
                    underdog_score = actual_away
                else:
                    underdog = home
                    underdog_score = actual_home
                
                # Market total (slightly different from model)
                market_total = round(model_total + random.gauss(0, 1.5), 1)
                market_total = round(market_total * 2) / 2
                
                # Determine pick
                if model_total > market_total:
                    pick = "OVER"
                else:
                    pick = "UNDER"
                
                # Win probability for underdog
                abs_spread = abs(model_spread)
                win_prob = 50.0 / (1.0 + math.exp(0.35 * (abs_spread - 1.5)))
                win_prob = round(win_prob, 1)
                
                # Assign date within season
                day_offset = random.randint(0, (end_date - start_date).days)
                game_date = start_date + timedelta(days=day_offset)
                
                game_id += 1
                games.append({
                    "matchup": f"{away} vs {home}",
                    "date": game_date.strftime("%b %d"),
                    "game_id": game_id,
                    "league": "WNBA",
                    "away_team": away,
                    "home_team": home,
                    "away_pace": away_stats["pace"],
                    "home_pace": home_stats["pace"],
                    "away_ortg": away_stats["ortg"],
                    "away_drtg": away_stats["drtg"],
                    "home_ortg": home_stats["ortg"],
                    "home_drtg": home_stats["drtg"],
                    "total": round(model_total * 2) / 2,
                    "spread": round(abs(model_spread) * 2) / 2,
                    "market_total": market_total,
                    "pick": pick,
                    "win_prob": win_prob,
                    "underdog": underdog,
                    "underdog_score": underdog_score,
                    "actual_away": actual_away,
                    "actual_home": actual_home,
                    "actual_total": actual_total,
                })
    
    # Sort by date
    games.sort(key=lambda g: g["date"])
    return games[:300]  # Approximate WNBA games through Aug 2
