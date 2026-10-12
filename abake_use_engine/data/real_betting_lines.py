"""
ABAKE USE Engine — Real Betting Lines Data
Scraped from Covers.com for NBA 2025-26 and WNBA 2026 seasons.
These are REAL closing lines from sportsbooks (Vegas closing lines).
"""

# NBA 2025-26 Real Closing Lines from Covers.com
# Format: (away_abbr, away_score, home_abbr, home_score, date, market_total, market_spread, spread_team)
# market_spread is the closing spread (positive = away is underdog, negative = away is favorite)
# spread_team indicates which team the spread is for

NBA_REAL_LINES = [
    # Oct 21, 2025
    ("HOU", 124, "OKC", 125, "Oct 21", 226.0, 6.5, "HOU"),   # HOU +6.5
    ("GSW", 119, "LAL", 109, "Oct 21", 227.5, 2.5, "GSW"),    # GS -2.5 (GSW favored)

    # Oct 22, 2025
    ("MIA", 121, "ORL", 125, "Oct 22", 215.0, 8.5, "MIA"),    # MIA +8.5
    ("CLE", 111, "NYK", 119, "Oct 22", 229.0, 2.0, "NYK"),    # NY +2 (NYK underdog)
    ("BKN", 117, "CHA", 136, "Oct 22", 228.0, 5.0, "CHA"),    # CHA -5 (CHA favored)
    ("PHI", 117, "BOS", 116, "Oct 22", 230.5, 6.0, "PHI"),    # PHI +6

    # Oct 23, 2025
    ("OKC", 141, "IND", 135, "Oct 23", 231.5, 7.5, "IND"),    # IND +7.5
    ("DEN", 131, "GSW", 137, "Oct 23", 232.5, 2.0, "GSW"),    # GS -2 (GSW favored)

    # Oct 24, 2025
    ("MIL", 122, "TOR", 116, "Oct 24", 235.5, 2.0, "MIL"),    # MIL +2
    ("ATL", 111, "ORL", 107, "Oct 24", 235.5, 6.0, "ATL"),    # ATL +6
    ("BOS", 95, "NYK", 105, "Oct 24", 231.0, 3.5, "NYK"),     # NY -3.5 (NYK favored)
    ("CLE", 131, "BKN", 124, "Oct 24", 231.0, 11.5, "BKN"),   # BK +11.5

    # Oct 25, 2025
    ("CHI", 110, "ORL", 98, "Oct 25", 232.5, 6.0, "CHI"),     # CHI +6
    ("CHA", 121, "PHI", 125, "Oct 25", 236.0, 5.0, "CHA"),    # CHA +5
    ("OKC", 117, "ATL", 100, "Oct 25", 236.5, 8.5, "OKC"),    # OKC -8.5 (OKC favored)
    ("IND", 103, "MEM", 128, "Oct 25", 240.5, 2.0, "MEM"),     # MEM -2 (MEM favored)

    # Oct 26, 2025
    ("BKN", 107, "SAS", 118, "Oct 26", 227.5, 10.5, "SAS"),   # SA -10.5 (SA favored)
    ("BOS", 113, "DET", 119, "Oct 26", 227.0, 2.5, "DET"),     # DET -2.5 (DET favored)
    ("CHA", 139, "WAS", 113, "Oct 26", 240.0, 1.5, "CHA"),     # CHA +1.5
    ("NYK", 107, "MIA", 115, "Oct 26", 230.5, 3.0, "MIA"),     # MIA +3

    # Oct 27, 2025
    ("CLE", 116, "DET", 95, "Oct 27", 231.0, 2.0, "CLE"),      # CLE -2 (CLE favored)
    ("ORL", 124, "PHI", 136, "Oct 27", 227.0, 6.5, "PHI"),     # PHI +6.5
    ("TOR", 103, "SAS", 121, "Oct 27", 232.5, 4.5, "SAS"),     # SA -4.5 (SA favored)
    ("BOS", 122, "NOP", 90, "Oct 27", 231.5, 4.5, "BOS"),      # BOS -4.5 (BOS favored)

    # Oct 28, 2025
    ("PHI", 139, "WAS", 134, "Oct 28", 239.5, 4.5, "PHI"),     # PHI -4.5 (PHI favored)
    ("CHA", 117, "MIA", 144, "Oct 28", 239.5, 4.5, "MIA"),     # MIA -4.5 (MIA favored)
    ("NYK", 111, "MIL", 121, "Oct 28", 229.5, 2.0, "MIL"),     # MIL +2
    ("SAC", 101, "OKC", 107, "Oct 28", 227.5, 9.0, "SAC"),     # SAC +9

    # Dec 1, 2025
    ("ATL", 98, "DET", 99, "Dec 01", 232.5, 9.5, "ATL"),       # ATL +9.5
    ("CLE", 135, "IND", 119, "Dec 01", 232.0, 5.0, "CLE"),      # CLE -5 (CLE favored)
    ("MIL", 126, "WAS", 129, "Dec 01", 232.5, 10.0, "WAS"),     # WAS +10
    ("LAC", 123, "MIA", 140, "Dec 01", 235.5, 6.0, "MIA"),      # MIA -6 (MIA favored)

    # NBA Finals 2026 (from Covers.com)
    ("NYK", 94, "SAS", 90, "Jun 08", 215.5, 5.5, "NYK"),       # NY +5.5
]

# WNBA 2026 Real Closing Lines from bettingsos.com/oddsshark search results
# Format: (away_abbr, away_score, home_abbr, home_score, date, market_total, market_spread, spread_team)
WNBA_REAL_LINES = [
    # Aug 1, 2026
    ("LV", None, "CHI", None, "Aug 01", 183.5, 6.5, "LV"),      # LV -6.5
    ("NY", None, "PHX", None, "Aug 01", 177.5, 2.5, "NY"),       # NY -2.5

    # Aug 2, 2026
    ("MIN", None, "IND", None, "Aug 02", 193.5, 5.5, "MIN"),     # MIN -5.5
    ("LA", None, "POR", None, "Aug 02", 185.5, 1.5, "LA"),       # LA -1.5
    ("DAL", None, "CON", None, "Aug 02", 172.5, 11.5, "DAL"),    # DAL -11.5
    ("GS", None, "TOR", None, "Aug 02", 164.5, 12.5, "GS"),      # GS -12.5

    # Jul 30, 2026
    ("MIN", None, "TOR", None, "Jul 30", None, 11.5, "MIN"),     # MIN -11.5
    ("CON", None, "CHI", None, "Jul 30", None, 4.5, "CHI"),      # CHI -4.5
    ("NY", None, "LV", None, "Jul 30", None, 5.5, "LV"),         # LV -5.5

    # Jul 31, 2026
    ("DAL", None, "WAS", None, "Jul 31", None, 3.5, "DAL"),      # DAL -3.5
    ("SEA", None, "ATL", None, "Jul 31", None, 12.5, "ATL"),     # ATL -12.5
    ("IND", None, "POR", None, "Jul 31", None, 7.5, "IND"),      # IND -7.5

    # Jul 16, 2026
    ("WSH", None, "POR", None, "Jul 16", 163.0, 6.5, "WSH"),    # WSH -6.5

    # Jul 17, 2026
    ("DAL", None, "NY", None, "Jul 17", 177.0, 2.5, "DAL"),      # DAL -2.5
    ("CHI", None, "LA", None, "Jul 17", 183.5, None, None),
    ("IND", None, "SEA", None, "Jul 17", 173.5, None, None),
]


# Team abbreviation mapping (Covers.com → ABAKE USE)
COVERS_TO_ABAKE = {
    "HOU": "HOU", "OKC": "OKC", "GS": "GSW", "GSW": "GSW",
    "LAL": "LAL", "MIA": "MIA", "ORL": "ORL", "CLE": "CLE",
    "NY": "NYK", "NYK": "NYK", "BK": "BKN", "BKN": "BKN",
    "CHA": "CHA", "PHI": "PHI", "BOS": "BOS", "IND": "IND",
    "DEN": "DEN", "MIL": "MIL", "TOR": "TOR", "ATL": "ATL",
    "SAC": "SAC", "SAS": "SAS", "DET": "DET", "WAS": "WAS",
    "NOP": "NOP", "MEM": "MEM", "LAC": "LAC", "MIN": "MIN",
    "PHX": "PHX", "POR": "POR", "UTA": "UTA", "NO": "NOP",
    "CHI": "CHI", "LV": "LV", "CON": "CON", "DAL": "DAL",
    "SEA": "SEA", "LA": "LA", "GS": "GS", "WSH": "WSH",
}
