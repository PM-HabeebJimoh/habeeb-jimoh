"""
ABAKE USE Engine — Complete 40-Game Dataset
The exact 40 matchups from the specification with all verified data points.
"""

# The complete 40-game dataset from the ABAKE USE specification
# Each game has: matchup, total, spread, pick, win_prob, underdog, underdog_score
# Total and Spread are the Model Game Total and Model Spread from Layer 1

ALL_40_GAMES = [
    # ============================================
    # CATEGORY A: Games Predicted OVER (13 games)
    # ============================================

    # 1. CHI vs LV (Aug 1) — OVER
    {
        "matchup": "CHI vs LV",
        "date": "Aug 1",
        "total": 162.0,
        "spread": 8.2,
        "pick": "OVER",
        "win_prob": 1.4,
        "underdog": "CHI",
        "underdog_score": 84,
        "league": "WNBA",
        # Raw Layer 1 inputs (for independent baseline verification)
        "away_pace": 79.8, "home_pace": 81.6,
        "away_ortg": 101.2, "home_drtg": 99.8,
        "home_ortg": 111.4, "away_drtg": 104.5,
    },

    # 2. PHX vs NY (Aug 1) — OVER
    {
        "matchup": "PHX vs NY",
        "date": "Aug 1",
        "total": 162.0,
        "spread": 7.0,
        "pick": "OVER",
        "win_prob": 3.8,
        "underdog": "PHX",
        "underdog_score": 92,
        "league": "WNBA",
    },

    # 3. WSH vs DAL (Jul 31) — OVER
    {
        "matchup": "WSH vs DAL",
        "date": "Jul 31",
        "total": 166.5,
        "spread": 3.5,
        "pick": "OVER",
        "win_prob": 8.2,
        "underdog": "WSH",
        "underdog_score": 81,
        "league": "WNBA",
    },

    # 4. WSH vs LV (Jul 22) — OVER
    {
        "matchup": "WSH vs LV",
        "date": "Jul 22",
        "total": 164.5,
        "spread": 6.5,
        "pick": "OVER",
        "win_prob": 4.5,
        "underdog": "WSH",
        "underdog_score": 100,
        "league": "WNBA",
    },

    # 5. GS vs WSH (Jul 21) — OVER
    {
        "matchup": "GS vs WSH",
        "date": "Jul 21",
        "total": 147.5,
        "spread": 8.5,
        "pick": "OVER",
        "win_prob": 2.1,
        "underdog": "WSH",
        "underdog_score": 90,
        "league": "WNBA",
    },

    # 6. GS vs WSH (Jul 19) — OVER
    {
        "matchup": "GS vs WSH",
        "date": "Jul 19",
        "total": 148.5,
        "spread": 8.5,
        "pick": "OVER",
        "win_prob": 2.3,
        "underdog": "WSH",
        "underdog_score": 69,
        "league": "WNBA",
    },

    # 7. IND vs GS (Jul 16) — OVER
    {
        "matchup": "IND vs GS",
        "date": "Jul 16",
        "total": 166.5,
        "spread": 2.5,
        "pick": "OVER",
        "win_prob": 10.5,
        "underdog": "IND",
        "underdog_score": 81,
        "league": "WNBA",
    },

    # 8. MIN vs PHX (Jul 14) — OVER
    {
        "matchup": "MIN vs PHX",
        "date": "Jul 14",
        "total": 169.5,
        "spread": 12.5,
        "pick": "OVER",
        "win_prob": 1.2,
        "underdog": "PHX",
        "underdog_score": 83,
        "league": "WNBA",
    },

    # 9. LV vs IND (Jul 13) — OVER
    {
        "matchup": "LV vs IND",
        "date": "Jul 13",
        "total": 162.0,
        "spread": 1.8,
        "pick": "OVER",
        "win_prob": 12.8,
        "underdog": "IND",
        "underdog_score": 81,
        "league": "WNBA",
    },

    # 10. DAL vs CHI (Jul 12) — OVER
    {
        "matchup": "DAL vs CHI",
        "date": "Jul 12",
        "total": 162.0,
        "spread": 6.2,
        "pick": "OVER",
        "win_prob": 5.1,
        "underdog": "CHI",
        "underdog_score": 81,
        "league": "WNBA",
    },

    # 11. TOR vs NY (Jul 12) — OVER
    {
        "matchup": "TOR vs NY",
        "date": "Jul 12",
        "total": 162.0,
        "spread": 5.0,
        "pick": "OVER",
        "win_prob": 6.8,
        "underdog": "TOR",
        "underdog_score": 83,
        "league": "WNBA",
    },

    # 12. MIN vs NY (Jul 11) — OVER
    {
        "matchup": "MIN vs NY",
        "date": "Jul 11",
        "total": 162.0,
        "spread": 2.6,
        "pick": "OVER",
        "win_prob": 10.2,
        "underdog": "MIN",
        "underdog_score": 82,
        "league": "WNBA",
    },

    # 13. LV vs PHX (Jul 11) — OVER
    {
        "matchup": "LV vs PHX",
        "date": "Jul 11",
        "total": 162.0,
        "spread": 7.0,
        "pick": "OVER",
        "win_prob": 3.8,
        "underdog": "PHX",
        "underdog_score": 81,
        "league": "WNBA",
    },

    # ============================================
    # CATEGORY B: Games Predicted UNDER (27 games)
    # ============================================

    # 14. POR vs IND (Aug 1) — SYSTEM SKIP (Rule 2: Chaos Exemption)
    {
        "matchup": "POR vs IND",
        "date": "Aug 1",
        "total": 170.0,
        "spread": 5.5,
        "pick": "UNDER",
        "win_prob": 5.0,
        "underdog": "POR",
        "underdog_score": None,
        "league": "WNBA",
    },

    # 15. ATL vs SEA (Jul 31) — SYSTEM SKIP (Rule 1: Upset Clause)
    {
        "matchup": "ATL vs SEA",
        "date": "Jul 31",
        "total": 178.5,
        "spread": 12.5,
        "pick": "UNDER",
        "win_prob": 24.3,
        "underdog": "ATL",
        "underdog_score": None,
        "league": "WNBA",
    },

    # 16. IND vs CON (Jul 23) — UNDER
    {
        "matchup": "IND vs CON",
        "date": "Jul 23",
        "total": 178.5,
        "spread": 10.5,
        "pick": "UNDER",
        "win_prob": 3.3,
        "underdog": "CON",
        "underdog_score": 88,
        "league": "WNBA",
    },

    # 17. SEA vs MIN (Jul 22) — UNDER
    {
        "matchup": "SEA vs MIN",
        "date": "Jul 22",
        "total": 179.5,
        "spread": 10.5,
        "pick": "UNDER",
        "win_prob": 3.3,
        "underdog": "SEA",
        "underdog_score": 76,
        "league": "WNBA",
    },

    # 18. TOR vs LV (Jul 21) — UNDER
    {
        "matchup": "TOR vs LV",
        "date": "Jul 21",
        "total": 182.5,
        "spread": 10.5,
        "pick": "UNDER",
        "win_prob": 3.3,
        "underdog": "TOR",
        "underdog_score": 83,
        "league": "WNBA",
    },

    # 19. DAL vs LA (Jul 19) — UNDER
    {
        "matchup": "DAL vs LA",
        "date": "Jul 19",
        "total": 182.5,
        "spread": 9.5,
        "pick": "UNDER",
        "win_prob": 4.5,
        "underdog": "LA",
        "underdog_score": 82,
        "league": "WNBA",
    },

    # 20. OKC vs BKN (Jul 19) — UNDER (Summer League)
    {
        "matchup": "OKC vs BKN",
        "date": "Jul 19",
        "total": 188.5,
        "spread": 3.5,
        "pick": "UNDER",
        "win_prob": 8.2,
        "underdog": "OKC",
        "underdog_score": 90,
        "league": "Summer",
    },

    # 21. TOR vs DEN (Jul 19) — UNDER (Summer League)
    {
        "matchup": "TOR vs DEN",
        "date": "Jul 19",
        "total": 188.5,
        "spread": 2.5,
        "pick": "UNDER",
        "win_prob": 10.5,
        "underdog": "TOR",
        "underdog_score": 89,
        "league": "Summer",
    },

    # 22. ORL vs BOS (Jul 18) — UNDER (Summer League)
    {
        "matchup": "ORL vs BOS",
        "date": "Jul 18",
        "total": 187.5,
        "spread": 1.5,
        "pick": "UNDER",
        "win_prob": 13.2,
        "underdog": "ORL",
        "underdog_score": 88,
        "league": "Summer",
    },

    # 23. MEM vs HOU (Jul 18) — UNDER (Summer League)
    {
        "matchup": "MEM vs HOU",
        "date": "Jul 18",
        "total": 186.5,
        "spread": 4.5,
        "pick": "UNDER",
        "win_prob": 6.8,
        "underdog": "MEM",
        "underdog_score": 87,
        "league": "Summer",
    },

    # 24. MIL vs PHI (Jul 18) — UNDER (Summer League)
    {
        "matchup": "MIL vs PHI",
        "date": "Jul 18",
        "total": 188.5,
        "spread": 4.5,
        "pick": "UNDER",
        "win_prob": 6.8,
        "underdog": "MIL",
        "underdog_score": 85,
        "league": "Summer",
    },

    # 25. LAC vs MIN (Jul 18) — UNDER (Summer League)
    {
        "matchup": "LAC vs MIN",
        "date": "Jul 18",
        "total": 187.5,
        "spread": 2.5,
        "pick": "UNDER",
        "win_prob": 10.5,
        "underdog": "LAC",
        "underdog_score": 89,
        "league": "Summer",
    },

    # 26. MIA vs DET (Jul 18) — UNDER (Summer League)
    {
        "matchup": "MIA vs DET",
        "date": "Jul 18",
        "total": 184.5,
        "spread": 3.5,
        "pick": "UNDER",
        "win_prob": 8.2,
        "underdog": "MIA",
        "underdog_score": 86,
        "league": "Summer",
    },

    # 27. CHI vs LA (Jul 17) — UNDER (Summer League)
    {
        "matchup": "CHI vs LA",
        "date": "Jul 17",
        "total": 182.5,
        "spread": 1.5,
        "pick": "UNDER",
        "win_prob": 13.2,
        "underdog": "CHI",
        "underdog_score": 82,
        "league": "Summer",
    },

    # 28. IND vs SEA (Jul 17) — UNDER
    {
        "matchup": "IND vs SEA",
        "date": "Jul 17",
        "total": 177.5,
        "spread": 8.5,
        "pick": "UNDER",
        "win_prob": 5.1,
        "underdog": "SEA",
        "underdog_score": 82,
        "league": "WNBA",
    },

    # 29. CLE vs CHI (Jul 17) — UNDER (Summer League)
    {
        "matchup": "CLE vs CHI",
        "date": "Jul 17",
        "total": 184.5,
        "spread": 3.5,
        "pick": "UNDER",
        "win_prob": 8.2,
        "underdog": "CLE",
        "underdog_score": 87,
        "league": "Summer",
    },

    # 30. CHA vs SAC (Jul 17) — UNDER (Summer League)
    {
        "matchup": "CHA vs SAC",
        "date": "Jul 17",
        "total": 183.5,
        "spread": 1.5,
        "pick": "UNDER",
        "win_prob": 13.2,
        "underdog": "CHA",
        "underdog_score": 83,
        "league": "Summer",
    },

    # 31. ATL vs MEM (Jul 17) — UNDER (Summer League)
    {
        "matchup": "ATL vs MEM",
        "date": "Jul 17",
        "total": 183.5,
        "spread": 2.5,
        "pick": "UNDER",
        "win_prob": 10.5,
        "underdog": "ATL",
        "underdog_score": 85,
        "league": "Summer",
    },

    # 32. DEN vs POR (Jul 17) — UNDER (Summer League)
    {
        "matchup": "DEN vs POR",
        "date": "Jul 17",
        "total": 186.5,
        "spread": 1.5,
        "pick": "UNDER",
        "win_prob": 13.2,
        "underdog": "DEN",
        "underdog_score": 84,
        "league": "Summer",
    },

    # 33. MIA vs TOR (Jul 17) — UNDER (Summer League)
    {
        "matchup": "MIA vs TOR",
        "date": "Jul 17",
        "total": 180.5,
        "spread": 2.5,
        "pick": "UNDER",
        "win_prob": 10.5,
        "underdog": "MIA",
        "underdog_score": 81,
        "league": "Summer",
    },

    # 34. HOU vs BKN (Jul 16) — UNDER (Summer League)
    {
        "matchup": "HOU vs BKN",
        "date": "Jul 16",
        "total": 181.5,
        "spread": 3.5,
        "pick": "UNDER",
        "win_prob": 8.2,
        "underdog": "HOU",
        "underdog_score": 82,
        "league": "Summer",
    },

    # 35. OKC vs DAL (Jul 16) — UNDER (Summer League)
    {
        "matchup": "OKC vs DAL",
        "date": "Jul 16",
        "total": 182.5,
        "spread": 2.5,
        "pick": "UNDER",
        "win_prob": 10.5,
        "underdog": "OKC",
        "underdog_score": 82,
        "league": "Summer",
    },

    # 36. CHI vs LAL (Jul 16) — UNDER (Summer League)
    {
        "matchup": "CHI vs LAL",
        "date": "Jul 16",
        "total": 180.5,
        "spread": 5.5,
        "pick": "UNDER",
        "win_prob": 5.5,
        "underdog": "CHI",
        "underdog_score": 83,
        "league": "Summer",
    },

    # 37. CHA vs MIL (Jul 15) — UNDER (Summer League)
    {
        "matchup": "CHA vs MIL",
        "date": "Jul 15",
        "total": 178.5,
        "spread": 5.5,
        "pick": "UNDER",
        "win_prob": 5.5,
        "underdog": "CHA",
        "underdog_score": 83,
        "league": "Summer",
    },

    # 38. PHI vs ORL (Jul 15) — UNDER (Summer League)
    {
        "matchup": "PHI vs ORL",
        "date": "Jul 15",
        "total": 184.5,
        "spread": 4.5,
        "pick": "UNDER",
        "win_prob": 6.8,
        "underdog": "PHI",
        "underdog_score": 82,
        "league": "Summer",
    },

    # 39. DET vs PHX (Jul 15) — UNDER (Summer League)
    {
        "matchup": "DET vs PHX",
        "date": "Jul 15",
        "total": 175.5,
        "spread": 2.5,
        "pick": "UNDER",
        "win_prob": 10.5,
        "underdog": "DET",
        "underdog_score": 82,
        "league": "Summer",
    },

    # 40. MIN vs IND (Jul 15) — UNDER
    {
        "matchup": "MIN vs IND",
        "date": "Jul 15",
        "total": 186.5,
        "spread": 2.5,
        "pick": "UNDER",
        "win_prob": 10.5,
        "underdog": "MIN",
        "underdog_score": 85,
        "league": "WNBA",
    },
]
