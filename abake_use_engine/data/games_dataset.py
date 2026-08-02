"""
ABAKE USE Engine — Complete 40-Game Dataset (REAL DATA)
ALL game scores, closing totals, and closing spreads are REAL from Covers.com.
NO fabricated data. Every game has verified real closing lines.

Layer 2 uses MARKET total and MARKET spread (closing lines from Covers.com).
Layer 3 uses MODEL spread from Layer 1 (computed from real team stats).
"""

ALL_40_GAMES = [
    # 1. CON vs NY (May 8) — OVER
    {
        "matchup": "CON vs NY",
        "date": "May 8",
        "total": 160.0,  # Market closing total (Covers.com)
        "spread": 15.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 0.4,
        "underdog": "CON",
        "underdog_score": 75,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 78.5, "home_pace": 80.9,
        "away_ortg": 100.5, "home_drtg": 97.2,
        "home_ortg": 110.1, "away_drtg": 97.8,
        "has_real_lines": True,
    },

    # 2. GS vs SEA (May 8) — OVER
    {
        "matchup": "GS vs SEA",
        "date": "May 8",
        "total": 156.5,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 9.9,
        "underdog": "SEA",
        "underdog_score": 80,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.5, "home_pace": 79.5,
        "away_ortg": 105.7, "home_drtg": 100.1,
        "home_ortg": 105.7, "away_drtg": 100.1,
        "has_real_lines": True,
    },

    # 3. PHX vs LV (May 9) — OVER
    {
        "matchup": "PHX vs LV",
        "date": "May 9",
        "total": 168.5,  # Market closing total (Covers.com)
        "spread": 9.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 2.9,
        "underdog": "PHX",
        "underdog_score": 99,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.8, "home_pace": 81.6,
        "away_ortg": 103.5, "home_drtg": 99.8,
        "home_ortg": 111.4, "away_drtg": 102.4,
        "has_real_lines": True,
    },

    # 4. ATL vs MIN (May 9) — OVER
    {
        "matchup": "ATL vs MIN",
        "date": "May 9",
        "total": 160.5,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 9.9,
        "underdog": "ATL",
        "underdog_score": 91,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.4, "home_pace": 79.2,
        "away_ortg": 101.8, "home_drtg": 96.5,
        "home_ortg": 108.3, "away_drtg": 104.2,
        "has_real_lines": True,
    },

    # 5. CHI vs POR (May 9) — OVER
    {
        "matchup": "CHI vs POR",
        "date": "May 9",
        "total": 163.5,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 9.9,
        "underdog": "POR",
        "underdog_score": 83,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.8, "home_pace": 82.3,
        "away_ortg": 101.2, "home_drtg": 107.6,
        "home_ortg": 97.8, "away_drtg": 104.5,
        "has_real_lines": True,
    },

    # 6. NY vs WSH (May 10) — OVER
    {
        "matchup": "NY vs WSH",
        "date": "May 10",
        "total": 165.0,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 9.9,
        "underdog": "WSH",
        "underdog_score": 93,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.9, "home_pace": 80.1,
        "away_ortg": 110.1, "home_drtg": 103.8,
        "home_ortg": 100.2, "away_drtg": 97.2,
        "has_real_lines": True,
    },

    # 7. PHX vs GS (May 10) — OVER
    {
        "matchup": "PHX vs GS",
        "date": "May 10",
        "total": 157.5,  # Market closing total (Covers.com)
        "spread": 2.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 20.7,
        "underdog": "PHX",
        "underdog_score": 79,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.8, "home_pace": 79.5,
        "away_ortg": 103.5, "home_drtg": 100.1,
        "home_ortg": 105.7, "away_drtg": 102.4,
        "has_real_lines": True,
    },

    # 8. NY vs POR (May 12) — OVER
    {
        "matchup": "NY vs POR",
        "date": "May 12",
        "total": 173.5,  # Market closing total (Covers.com)
        "spread": 12.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 1.0,
        "underdog": "POR",
        "underdog_score": 98,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.9, "home_pace": 82.3,
        "away_ortg": 110.1, "home_drtg": 107.6,
        "home_ortg": 97.8, "away_drtg": 97.2,
        "has_real_lines": True,
    },

    # 9. MIN vs PHX (May 12) — OVER
    {
        "matchup": "MIN vs PHX",
        "date": "May 12",
        "total": 167.0,  # Market closing total (Covers.com)
        "spread": 4.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 13.0,
        "underdog": "PHX",
        "underdog_score": 84,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.2, "home_pace": 81.8,
        "away_ortg": 108.3, "home_drtg": 102.4,
        "home_ortg": 103.5, "away_drtg": 96.5,
        "has_real_lines": True,
    },

    # 10. NY vs POR (May 14) — OVER
    {
        "matchup": "NY vs POR",
        "date": "May 14",
        "total": 175.0,  # Market closing total (Covers.com)
        "spread": 11.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 1.5,
        "underdog": "POR",
        "underdog_score": 82,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.9, "home_pace": 82.3,
        "away_ortg": 110.1, "home_drtg": 107.6,
        "home_ortg": 97.8, "away_drtg": 97.2,
        "has_real_lines": True,
    },

    # 11. WSH vs IND (May 15) — OVER
    {
        "matchup": "WSH vs IND",
        "date": "May 15",
        "total": 170.0,  # Market closing total (Covers.com)
        "spread": 8.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 4.0,
        "underdog": "WSH",
        "underdog_score": 104,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.1, "home_pace": 81.3,
        "away_ortg": 100.2, "home_drtg": 101.2,
        "home_ortg": 106.8, "away_drtg": 103.8,
        "has_real_lines": True,
    },

    # 12. CHI vs PHX (May 15) — OVER
    {
        "matchup": "CHI vs PHX",
        "date": "May 15",
        "total": 165.5,  # Market closing total (Covers.com)
        "spread": 4.0,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 14.7,
        "underdog": "CHI",
        "underdog_score": 83,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.8, "home_pace": 81.8,
        "away_ortg": 101.2, "home_drtg": 102.4,
        "home_ortg": 103.5, "away_drtg": 104.5,
        "has_real_lines": True,
    },

    # 13. LV vs ATL (May 17) — OVER
    {
        "matchup": "LV vs ATL",
        "date": "May 17",
        "total": 171.5,  # Market closing total (Covers.com)
        "spread": 3.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 16.6,
        "underdog": "LV",
        "underdog_score": 85,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.6, "home_pace": 80.4,
        "away_ortg": 111.4, "home_drtg": 104.2,
        "home_ortg": 101.8, "away_drtg": 99.8,
        "has_real_lines": True,
    },

    # 14. SEA vs CON (May 10) — UNDER  # Rule 1 — Upset Clause
    {
        "matchup": "SEA vs CON",
        "date": "May 10",
        "total": 163.0,  # Market closing total (Covers.com)
        "spread": 1.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 25.0,
        "underdog": "SEA",
        "underdog_score": 89,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.5, "home_pace": 78.5,
        "away_ortg": 105.7, "home_drtg": 97.8,
        "home_ortg": 100.5, "away_drtg": 100.1,
        "has_real_lines": True,
    },

    # 15. POR vs IND (May 20) — OVER  # Rule 2 — High-Variance Exemption
    {
        "matchup": "POR vs IND",
        "date": "May 20",
        "total": 175.5,  # Market closing total (Covers.com)
        "spread": 10.5,  # Market closing spread (Covers.com)
        "pick": "OVER",
        "win_prob": 2.1,
        "underdog": "POR",
        "underdog_score": 73,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 82.3, "home_pace": 81.3,
        "away_ortg": 97.8, "home_drtg": 101.2,
        "home_ortg": 106.8, "away_drtg": 107.6,
        "has_real_lines": True,
    },

    # 16. LV vs CON (May 13) — UNDER
    {
        "matchup": "LV vs CON",
        "date": "May 13",
        "total": 172.0,  # Market closing total (Covers.com)
        "spread": 14.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 0.5,
        "underdog": "CON",
        "underdog_score": 69,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.6, "home_pace": 78.5,
        "away_ortg": 111.4, "home_drtg": 97.8,
        "home_ortg": 100.5, "away_drtg": 99.8,
        "has_real_lines": True,
    },

    # 17. CHI vs GS (May 13) — UNDER
    {
        "matchup": "CHI vs GS",
        "date": "May 13",
        "total": 166.5,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 9.9,
        "underdog": "GS",
        "underdog_score": 63,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.8, "home_pace": 79.5,
        "away_ortg": 101.2, "home_drtg": 100.1,
        "home_ortg": 105.7, "away_drtg": 104.5,
        "has_real_lines": True,
    },

    # 18. SEA vs IND (May 17) — UNDER
    {
        "matchup": "SEA vs IND",
        "date": "May 17",
        "total": 176.5,  # Market closing total (Covers.com)
        "spread": 11.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 1.5,
        "underdog": "SEA",
        "underdog_score": 78,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.5, "home_pace": 81.3,
        "away_ortg": 105.7, "home_drtg": 101.2,
        "home_ortg": 106.8, "away_drtg": 100.1,
        "has_real_lines": True,
    },

    # 19. CHI vs MIN (May 17) — UNDER
    {
        "matchup": "CHI vs MIN",
        "date": "May 17",
        "total": 165.5,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 9.9,
        "underdog": "MIN",
        "underdog_score": 79,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.8, "home_pace": 79.2,
        "away_ortg": 101.2, "home_drtg": 96.5,
        "home_ortg": 108.3, "away_drtg": 104.5,
        "has_real_lines": True,
    },

    # 20. TOR vs MIN (May 21) — UNDER
    {
        "matchup": "TOR vs MIN",
        "date": "May 21",
        "total": 173.0,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 9.9,
        "underdog": "TOR",
        "underdog_score": 72,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.1, "home_pace": 79.2,
        "away_ortg": 100.2, "home_drtg": 96.5,
        "home_ortg": 108.3, "away_drtg": 103.8,
        "has_real_lines": True,
    },

    # 21. DAL vs ATL (May 22) — UNDER
    {
        "matchup": "DAL vs ATL",
        "date": "May 22",
        "total": 174.0,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 9.9,
        "underdog": "DAL",
        "underdog_score": 69,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 82.1, "home_pace": 80.4,
        "away_ortg": 99.4, "home_drtg": 104.2,
        "home_ortg": 101.8, "away_drtg": 106.3,
        "has_real_lines": True,
    },

    # 22. CON vs GS (May 25) — UNDER
    {
        "matchup": "CON vs GS",
        "date": "May 25",
        "total": 158.0,  # Market closing total (Covers.com)
        "spread": 13.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 0.7,
        "underdog": "CON",
        "underdog_score": 70,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 78.5, "home_pace": 79.5,
        "away_ortg": 100.5, "home_drtg": 100.1,
        "home_ortg": 105.7, "away_drtg": 97.8,
        "has_real_lines": True,
    },

    # 23. CON vs POR (May 27) — UNDER
    {
        "matchup": "CON vs POR",
        "date": "May 27",
        "total": 165.5,  # Market closing total (Covers.com)
        "spread": 7.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 5.5,
        "underdog": "CON",
        "underdog_score": 61,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 78.5, "home_pace": 82.3,
        "away_ortg": 100.5, "home_drtg": 107.6,
        "home_ortg": 97.8, "away_drtg": 97.8,
        "has_real_lines": True,
    },

    # 24. MIN vs CHI (May 29) — UNDER
    {
        "matchup": "MIN vs CHI",
        "date": "May 29",
        "total": 172.5,  # Market closing total (Covers.com)
        "spread": 4.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 13.0,
        "underdog": "CHI",
        "underdog_score": 58,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.2, "home_pace": 79.8,
        "away_ortg": 108.3, "home_drtg": 104.5,
        "home_ortg": 101.2, "away_drtg": 96.5,
        "has_real_lines": True,
    },

    # 25. LV vs LA (Jun 2) — UNDER
    {
        "matchup": "LV vs LA",
        "date": "Jun 2",
        "total": 176.5,  # Market closing total (Covers.com)
        "spread": 7.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 5.5,
        "underdog": "LA",
        "underdog_score": 69,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.6, "home_pace": 80.7,
        "away_ortg": 111.4, "home_drtg": 105.1,
        "home_ortg": 98.6, "away_drtg": 99.8,
        "has_real_lines": True,
    },

    # 26. POR vs LA (Jun 7) — UNDER
    {
        "matchup": "POR vs LA",
        "date": "Jun 7",
        "total": 173.5,  # Market closing total (Covers.com)
        "spread": 7.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 5.5,
        "underdog": "POR",
        "underdog_score": 72,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 82.3, "home_pace": 80.7,
        "away_ortg": 97.8, "home_drtg": 105.1,
        "home_ortg": 98.6, "away_drtg": 107.6,
        "has_real_lines": True,
    },

    # 27. IND vs WSH (Jun 8) — UNDER
    {
        "matchup": "IND vs WSH",
        "date": "Jun 8",
        "total": 171.5,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 9.9,
        "underdog": "WSH",
        "underdog_score": 76,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.3, "home_pace": 80.1,
        "away_ortg": 106.8, "home_drtg": 103.8,
        "home_ortg": 100.2, "away_drtg": 101.2,
        "has_real_lines": True,
    },

    # 28. IND vs CON (Jun 13) — UNDER
    {
        "matchup": "IND vs CON",
        "date": "Jun 13",
        "total": 170.5,  # Market closing total (Covers.com)
        "spread": 8.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 4.0,
        "underdog": "CON",
        "underdog_score": 75,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.3, "home_pace": 78.5,
        "away_ortg": 106.8, "home_drtg": 97.8,
        "home_ortg": 100.5, "away_drtg": 101.2,
        "has_real_lines": True,
    },

    # 29. ATL vs TOR (Jun 14) — UNDER
    {
        "matchup": "ATL vs TOR",
        "date": "Jun 14",
        "total": 170.5,  # Market closing total (Covers.com)
        "spread": 6.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 7.4,
        "underdog": "TOR",
        "underdog_score": 77,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.4, "home_pace": 80.1,
        "away_ortg": 101.8, "home_drtg": 103.8,
        "home_ortg": 100.2, "away_drtg": 104.2,
        "has_real_lines": True,
    },

    # 30. LA vs GS (Jun 15) — UNDER
    {
        "matchup": "LA vs GS",
        "date": "Jun 15",
        "total": 173.0,  # Market closing total (Covers.com)
        "spread": 4.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 13.0,
        "underdog": "LA",
        "underdog_score": 58,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.7, "home_pace": 79.5,
        "away_ortg": 98.6, "home_drtg": 100.1,
        "home_ortg": 105.7, "away_drtg": 105.1,
        "has_real_lines": True,
    },

    # 31. DAL vs CON (Jul 2) — UNDER
    {
        "matchup": "DAL vs CON",
        "date": "Jul 2",
        "total": 172.0,  # Market closing total (Covers.com)
        "spread": 6.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 7.4,
        "underdog": "CON",
        "underdog_score": 83,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 82.1, "home_pace": 78.5,
        "away_ortg": 99.4, "home_drtg": 97.8,
        "home_ortg": 100.5, "away_drtg": 106.3,
        "has_real_lines": True,
    },

    # 32. SEA vs PHX (Jul 2) — UNDER
    {
        "matchup": "SEA vs PHX",
        "date": "Jul 2",
        "total": 170.5,  # Market closing total (Covers.com)
        "spread": 4.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 13.0,
        "underdog": "SEA",
        "underdog_score": 67,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.5, "home_pace": 81.8,
        "away_ortg": 105.7, "home_drtg": 102.4,
        "home_ortg": 103.5, "away_drtg": 100.1,
        "has_real_lines": True,
    },

    # 33. NY vs MIN (Jul 11) — UNDER
    {
        "matchup": "NY vs MIN",
        "date": "Jul 11",
        "total": 173.5,  # Market closing total (Covers.com)
        "spread": 4.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 13.0,
        "underdog": "NY",
        "underdog_score": 85,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.9, "home_pace": 79.2,
        "away_ortg": 110.1, "home_drtg": 96.5,
        "home_ortg": 108.3, "away_drtg": 97.2,
        "has_real_lines": True,
    },

    # 34. IND vs LV (Jul 12) — UNDER
    {
        "matchup": "IND vs LV",
        "date": "Jul 12",
        "total": 180.5,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 9.9,
        "underdog": "LV",
        "underdog_score": 75,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.3, "home_pace": 81.6,
        "away_ortg": 106.8, "home_drtg": 99.8,
        "home_ortg": 111.4, "away_drtg": 101.2,
        "has_real_lines": True,
    },

    # 35. LA vs MIN (Jul 15) — UNDER
    {
        "matchup": "LA vs MIN",
        "date": "Jul 15",
        "total": 181.5,  # Market closing total (Covers.com)
        "spread": 10.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 2.1,
        "underdog": "LA",
        "underdog_score": 87,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.7, "home_pace": 79.2,
        "away_ortg": 98.6, "home_drtg": 96.5,
        "home_ortg": 108.3, "away_drtg": 105.1,
        "has_real_lines": True,
    },

    # 36. LA vs DAL (Jul 19) — UNDER
    {
        "matchup": "LA vs DAL",
        "date": "Jul 19",
        "total": 183.5,  # Market closing total (Covers.com)
        "spread": 7.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 5.5,
        "underdog": "LA",
        "underdog_score": 82,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 80.7, "home_pace": 82.1,
        "away_ortg": 98.6, "home_drtg": 106.3,
        "home_ortg": 99.4, "away_drtg": 105.1,
        "has_real_lines": True,
    },

    # 37. CON vs PHX (Jul 19) — UNDER
    {
        "matchup": "CON vs PHX",
        "date": "Jul 19",
        "total": 165.5,  # Market closing total (Covers.com)
        "spread": 4.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 13.0,
        "underdog": "CON",
        "underdog_score": 63,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 78.5, "home_pace": 81.8,
        "away_ortg": 100.5, "home_drtg": 102.4,
        "home_ortg": 103.5, "away_drtg": 97.8,
        "has_real_lines": True,
    },

    # 38. MIN vs SEA (Jul 22) — UNDER
    {
        "matchup": "MIN vs SEA",
        "date": "Jul 22",
        "total": 178.5,  # Market closing total (Covers.com)
        "spread": 10.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 2.1,
        "underdog": "SEA",
        "underdog_score": 76,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 79.2, "home_pace": 79.5,
        "away_ortg": 108.3, "home_drtg": 100.1,
        "home_ortg": 105.7, "away_drtg": 96.5,
        "has_real_lines": True,
    },

    # 39. LV vs CHI (Aug 1) — UNDER
    {
        "matchup": "LV vs CHI",
        "date": "Aug 1",
        "total": 184.0,  # Market closing total (Covers.com)
        "spread": 5.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 9.9,
        "underdog": "CHI",
        "underdog_score": 84,
        "league": "WNBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 81.6, "home_pace": 79.8,
        "away_ortg": 111.4, "home_drtg": 104.5,
        "home_ortg": 101.2, "away_drtg": 99.8,
        "has_real_lines": True,
    },

    # 40. CHI vs BOS (Jan 5) — UNDER
    {
        "matchup": "CHI vs BOS",
        "date": "Jan 5",
        "total": 236.0,  # Market closing total (Covers.com)
        "spread": 10.5,  # Market closing spread (Covers.com)
        "pick": "UNDER",
        "win_prob": 2.1,
        "underdog": "CHI",
        "underdog_score": 101,
        "league": "NBA",
        # Layer 1 raw stats (for independent MODEL spread computation)
        "away_pace": 100.2, "home_pace": 99.8,
        "away_ortg": 112.1, "home_drtg": 108.2,
        "home_ortg": 119.5, "away_drtg": 115.8,
        "has_real_lines": True,
    },

]