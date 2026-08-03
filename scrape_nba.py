#!/usr/bin/env python3
"""
Covers.com NBA Scraper — Parse fetched pages and save to JSON.
Usage: python scrape_nba.py parse <page_file> <date_str>
       python scrape_nba.py build
"""
import re, json, os, sys
from datetime import datetime, timedelta

DATA_DIR = "/home/user/habeeb-jimoh/scraped_data"
PAGES_DIR = os.path.join(DATA_DIR, "pages")
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

def parse_covers_page(content, date_str):
    """Parse a Covers.com matchups page and extract NBA game data."""
    games = []
    
    # Find all "total score of" matches
    total_pat = r'total score of (\d+) was \*\*(?:over|under)\s+(\d+\.?\d*)\*\*'
    totals = list(re.finditer(total_pat, content))
    
    # Find all "covered the spread of" matches
    spread_pat = r'covered the spread of \*\*([+-]?\d+\.?\d*)\*\*'
    spreads = list(re.finditer(spread_pat, content))
    
    # Find all team-score pairs
    ts_pat = r'\b([A-Z]{2,3})\s+\*\*(\d+)\*\*'
    team_scores = list(re.finditer(ts_pat, content))
    
    # Group into game pairs
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
    used_spreads = set()
    
    for idx, (ti, tj) in enumerate(pairs):
        away = team_scores[ti].group(1)
        away_s = int(team_scores[ti].group(2))
        home = team_scores[tj].group(1)
        home_s = int(team_scores[tj].group(2))
        actual = away_s + home_s
        
        # Find matching total
        mt = None
        for t_idx, tm in enumerate(totals):
            if t_idx in used_totals: continue
            if int(tm.group(1)) == actual:
                mt = float(tm.group(2))
                used_totals.add(t_idx)
                break
        
        # Find spread in game block
        ms = None
        fav = None
        bs = team_scores[ti].start()
        be = team_scores[tj].end() + 500
        if idx + 1 < len(pairs):
            be = min(be, team_scores[pairs[idx+1][0]].start())
        block = content[bs:be]
        
        sm_list = list(re.finditer(spread_pat, block))
        if sm_list:
            sm = sm_list[0]
            sv = float(sm.group(1))
            
            # Find covered team name
            pre = block[:sm.start()]
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
            if not covered:
                covered = away
            
            if sv > 0:  # underdog covered
                fav = home if covered == away else away
                ms = abs(sv)
            else:  # favorite covered
                fav = covered
                ms = abs(sv)
        
        if mt and ms and fav:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            label = dt.strftime("%b %-d").replace(" 0", " ")
            games.append((away, away_s, home, home_s, label, mt, ms, fav))
    
    return games

def build_all():
    """Process all saved pages and build the complete game list."""
    all_games = []
    start = datetime(2025, 10, 21)
    end = datetime(2026, 4, 13)
    current = start
    dates_with = 0
    dates_without = 0
    
    while current <= end:
        ds = current.strftime("%Y-%m-%d")
        pf = os.path.join(PAGES_DIR, f"nba_{ds}.txt")
        if os.path.exists(pf):
            with open(pf) as f:
                content = f.read()
            games = parse_covers_page(content, ds)
            if games:
                all_games.extend(games)
                dates_with += 1
            else:
                dates_without += 1
        else:
            dates_without += 1
        current += timedelta(days=1)
    
    out = os.path.join(DATA_DIR, "nba_2025_26_all.json")
    with open(out, 'w') as f:
        json.dump(all_games, f, indent=2)
    
    print(f"Dates with games: {dates_with}")
    print(f"Dates without: {dates_without}")
    print(f"Total games: {len(all_games)}")
    print(f"Saved to: {out}")
    return all_games

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build_all()
    else:
        print("Usage: python scrape_nba.py build")
