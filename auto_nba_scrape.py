#!/usr/bin/env python3
"""
Automated NBA 2025-26 Season Data Builder
Fetches all NBA game data from Covers.com, parses it, and builds the game database.
"""
import os, sys, re, json
from datetime import datetime, timedelta

PAGES_DIR = "/home/user/habeeb-jimoh/scraped_data/pages"
DATA_DIR = "/home/user/habeeb-jimoh/scraped_data"
os.makedirs(PAGES_DIR, exist_ok=True)

TEAM_NAME_MAP = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GSW", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "L.A. Clippers": "LAC", "L.A. Lakers": "LAL",
    "Memphis": "MEM", "Miami": "MIA", "Milwaukee": "MIL", "Minnesota": "MIN",
    "New Orleans": "NOP", "New York": "NYK", "Oklahoma City": "OKC",
    "Orlando": "ORL", "Philadelphia": "PHI", "Phoenix": "PHX", "Portland": "POR",
    "Sacramento": "SAC", "San Antonio": "SAS", "Toronto": "TOR", "Utah": "UTA",
    "Washington": "WAS",
}

def parse_page(content, date_str):
    """Parse a Covers.com matchups page and extract NBA game data."""
    games = []
    total_pat = r"total score of (\\d+) was \\*\\*(?:over|under)\\s+(\\d+\\.?\\d*)\\*\\*"
    spread_pat = r"covered the spread of \\*\\*([+-]?\\d+\\.?\\d*)\\*\\*"
    ts_pat = r"\\b([A-Z]{2,3})\\s+\\*\\*(\\d+)\\*\\*"
    totals = list(re.finditer(total_pat, content))
    team_scores = list(re.finditer(ts_pat, content))
    pairs = []
    used = set()
    for i in range(len(team_scores)):
        if i in used: continue
        for j in range(i+1, len(team_scores)):
            if j in used: continue
            pairs.append((i, j))
            used.update([i, j])
            break
    used_totals = set()
    for idx, (ti, tj) in enumerate(pairs):
        away = team_scores[ti].group(1)
        away_s = int(team_scores[ti].group(2))
        home = team_scores[tj].group(1)
        home_s = int(team_scores[tj].group(2))
        actual = away_s + home_s
        mt = None
        for t_idx, tm in enumerate(totals):
            if t_idx in used_totals: continue
            if int(tm.group(1)) == actual:
                mt = float(tm.group(2))
                used_totals.add(t_idx)
                break
        ms = None
        fav = None
        bs = team_scores[ti].start()
        be = team_scores[tj].end() + 500
        if idx + 1 < len(pairs):
            be = min(be, team_scores[pairs[idx+1][0]].start())
        block = content[bs:be]
        sm_list = list(re.finditer(spread_pat, block))
        if sm_list:
            sv = float(sm_list[0].group(1))
            pre = block[:sm_list[0].start()]
            covered = None
            for name, abbr in TEAM_NAME_MAP.items():
                if name.lower() in pre[-120:].lower():
                    covered = abbr
                    break
            if not covered:
                for abbr in [away, home]:
                    if abbr.lower() in pre[-80:].lower():
                        covered = abbr
                        break
            if not covered: covered = away
            if sv > 0:
                fav = home if covered == away else away
                ms = abs(sv)
            else:
                fav = covered
                ms = abs(sv)
        if mt and ms and fav:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            label = dt.strftime("%b %-d").replace(" 0", " ")
            games.append((away, away_s, home, home_s, label, mt, ms, fav))
    return games

def process_all():
    """Process all saved pages and build the complete game database."""
    all_games = []
    for f in sorted(os.listdir(PAGES_DIR)):
        if f.startswith("nba_") and f.endswith(".txt"):
            date_str = f[4:-4]
            with open(os.path.join(PAGES_DIR, f)) as fh:
                content = fh.read()
            games = parse_page(content, date_str)
            all_games.extend(games)
    out = os.path.join(DATA_DIR, "nba_2025_26_all.json")
    with open(out, "w") as fh:
        json.dump(all_games, fh, indent=2)
    return all_games

if __name__ == "__main__":
    games = process_all()
    print(f"Total games: {len(games)}")
