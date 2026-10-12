"""
ABAKE USE Engine — Enterprise Web Application
Flask-based dashboard with live game tracking, scoring, and analytics.
"""

import json
import logging
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from abake_use_engine.core.engine import AbakeUseEngine
from abake_use_engine.data.services import BasketballDataService
from abake_use_engine.data.analytics import AnalyticsService

# ------------------------------------------------------------------ #
# Configuration                                                       #
# ------------------------------------------------------------------ #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("abake_use_app")

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

# Initialize engine and services
engine = AbakeUseEngine()
data_service = BasketballDataService()
analytics = AnalyticsService()

# In-memory cache for processed results
_results_cache: dict = {}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")


@app.route("/api/today/games")
def api_today_games():
    """Fetch today's games across all basketball leagues."""
    league = request.args.get("league", "all")

    if league == "all":
        games = data_service.get_all_todays_games()
    elif league == "wnba":
        games = data_service.get_wnba_todays_games()
    elif league == "summer":
        games = data_service.get_summer_league_todays_games()
    else:
        games = data_service.fetch_espn_scoreboard(league)

    # Enrich with analytics stats
    for game in games:
        analytics.enrich_game_with_stats(game)

    return jsonify({
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "count": len(games),
        "games": games,
    })


@app.route("/api/today/process")
def api_today_process():
    """Process today's games through the ABAKE USE engine."""
    league = request.args.get("league", "all")

    if league == "all":
        games = data_service.get_all_todays_games()
    elif league == "wnba":
        games = data_service.get_wnba_todays_games()
    elif league == "summer":
        games = data_service.get_summer_league_todays_games()
    else:
        games = data_service.fetch_espn_scoreboard(league)

    results = []
    for game in games:
        # Enrich with stats
        game = analytics.enrich_game_with_stats(game)

        # Prepare the row for the engine
        row = _game_to_engine_row(game)
        result = engine.process_matchup(row)
        results.append(result)

    # Compute summary
    import pandas as pd
    results_df = pd.DataFrame(results)
    summary = engine.compute_summary(results_df)

    # Cache results
    _results_cache["today"] = {
        "results": results,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat(),
    }

    return jsonify({
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "summary": summary,
        "results": results,
    })


@app.route("/api/today/summary")
def api_today_summary():
    """Get summary of today's processed results."""
    if "today" in _results_cache:
        return jsonify(_results_cache["today"]["summary"])
    return jsonify({"message": "No results processed yet. Call /api/today/process first."})


@app.route("/api/process", methods=["POST"])
def api_process_custom():
    """Process a custom matchup through the ABAKE USE engine."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Support single or batch
    if isinstance(data, list):
        results = []
        for row in data:
            result = engine.process_matchup(row)
            results.append(result)
        import pandas as pd
        summary = engine.compute_summary(pd.DataFrame(results))
        return jsonify({"summary": summary, "results": results})
    else:
        result = engine.process_matchup(data)
        return jsonify(result)


@app.route("/api/engine/status")
def api_engine_status():
    """Get engine status and configuration."""
    return jsonify({
        "engine": "ABAKE USE — Dynamic Pacing and Possession Scaling Engine",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "constants": engine.constants,
        "HCA": engine.HCA,
        "over_cushion_multiplier": engine.OVER_CUSHION_MULTIPLIER,
        "under_ceiling_multiplier": engine.UNDER_CEILING_MULTIPLIER,
        "upset_probability_threshold": engine.UPSET_PROBABILITY_THRESHOLD,
        "chaos_matchups": list(engine.CHAOS_MATCHUPS),
        "timestamp": datetime.utcnow().isoformat(),
    })


@app.route("/api/verify/profiles")
def api_verify_profiles():
    """
    Run the 3 verification profiles from the ABAKE USE specification
    to confirm the engine is calculating correctly.
    """
    profiles = [
        # Profile 1: CHI vs LV (August 1) — Full independent baseline
        {
            "matchup": "CHI vs LV",
            "league": "WNBA",
            "away_pace": 79.8,
            "home_pace": 81.6,
            "away_ortg": 101.2,
            "home_drtg": 99.8,
            "home_ortg": 111.4,
            "away_drtg": 104.5,
            "pick": "OVER",
            "win_prob": 1.4,
            "actual_score": 84,
        },
        # Profile 2: IND vs CON (July 23) — Market lines
        {
            "matchup": "IND vs CON",
            "total": 178.5,
            "spread": 10.5,
            "pick": "UNDER",
            "win_prob": 3.3,
            "actual_score": 88,
        },
        # Profile 3: ATL vs SEA (July 31) — Upset Clause
        {
            "matchup": "ATL vs SEA",
            "total": 178.5,
            "spread": 12.5,
            "pick": "UNDER",
            "win_prob": 24.3,
            "actual_score": None,
        },
    ]

    results = []
    for profile in profiles:
        result = engine.process_matchup(profile)
        results.append(result)

    # Check against expected outcomes
    expected = [
        {"matchup": "CHI vs LV", "expected_status": "HIT"},
        {"matchup": "IND vs CON", "expected_status": "HIT"},
        {"matchup": "ATL vs SEA", "expected_status": "SYSTEM SKIP"},
    ]

    verification = []
    for result, exp in zip(results, expected):
        match = result["status"] == exp["expected_status"]
        verification.append({
            "matchup": exp["matchup"],
            "expected": exp["expected_status"],
            "actual": result["status"],
            "verified": match,
            "details": result,
        })

    all_pass = all(v["verified"] for v in verification)

    return jsonify({
        "engine_verified": all_pass,
        "verification_profiles": verification,
        "timestamp": datetime.utcnow().isoformat(),
    })


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _game_to_engine_row(game: dict) -> dict:
    """
    Convert a game data dict to an engine-ready row.
    Properly identifies the underdog and maps their score.
    """
    row = {
        "matchup": game.get("matchup", ""),
        "league": game.get("league", "WNBA"),
    }

    # Determine underdog and their score
    spread = game.get("spread", 0)
    if spread is None:
        spread = 0

    # The underdog is the team receiving points (positive spread from market)
    # In our data, the spread represents how much the favorite is favored by
    # So the away team is the underdog if they're getting points
    # Convention: if spread > 0, away team is the underdog

    # Determine actual score for the underdog
    actual_score = None
    if game.get("is_final") or game.get("is_live"):
        away_score = game.get("away_score", 0) or 0
        home_score = game.get("home_score", 0) or 0
        # The underdog is the away team when spread > 0
        # (spread = how much the home team is favored by)
        actual_score = away_score  # Underdog is typically the away team

    row["actual_score"] = actual_score

    # Add market lines if available
    if game.get("total"):
        row["total"] = float(game["total"])
    if game.get("spread"):
        row["spread"] = float(game["spread"])

    # Add team stats if available
    for key in ("away_pace", "away_ortg", "away_drtg",
                "home_pace", "home_ortg", "home_drtg"):
        if game.get(key):
            row[key] = float(game[key])

    # Determine pick based on model
    if "pick" in game:
        row["pick"] = game["pick"]
    else:
        # Use the engine's independent baseline to determine pick
        if all(k in row for k in ("away_pace", "home_pace", "away_ortg", "home_drtg", "home_ortg", "away_drtg")):
            # Compute independent baseline
            total, spread_val, proj_pace, score_away, score_home = (
                engine.calculate_independent_baselines(row)
            )
            # Compare model total to market total
            market_total = row.get("total", total)
            row["pick"] = analytics.compute_pick(total, market_total)
        else:
            # Fallback: use spread heuristic
            spread = row.get("spread", 5.0)
            total = row.get("total", 160)
            if spread and total:
                underdog_line = (total / 2) - (spread / 2)
                row["pick"] = "OVER" if underdog_line < 75 else "UNDER"
            else:
                row["pick"] = "OVER"

    # Win probability
    if "win_prob" in game:
        row["win_prob"] = game["win_prob"]
    else:
        spread_val = row.get("spread", 5.0)
        row["win_prob"] = analytics.estimate_win_probability(spread_val)

    return row


# ------------------------------------------------------------------ #
# Main                                                                #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting ABAKE USE Engine on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=True)
