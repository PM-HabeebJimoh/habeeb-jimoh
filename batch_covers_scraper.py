#!/usr/bin/env python3
"""
Batch Covers.com NBA scraper — fetches and processes game data from Covers.com.
Uses the Covers.com parser to extract scores and closing lines.
Tracks progress and saves to all_games_with_real_lines.json.
"""

import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from covers_parser import parse_covers_page

DATA_FILE = "scraped_data/all_games_with_real_lines.json"
PROGRESS_FILE = "scraped_data/scraper_progress.json"

def normalize_date(d):
    """Normalize date string to YYYY-MM-DD format."""
    if isinstance(d, str) and d.startswith('202'):
        return d
    months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06'}
    parts = d.split()
    if len(parts) == 2:
        month = months.get(parts[0], '01')
        day = parts[1].zfill(2)
        return f'2026-{month}-{day}'
    return d

def load_data():
    """Load existing game data."""
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    """Save game data."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_progress():
    """Load scraper progress."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"scraped_dates": [], "failed_dates": [], "no_games_dates": []}

def save_progress(progress):
    """Save scraper progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def get_dates_with_data(data):
    """Get set of dates that already have game data."""
    dates = set()
    for g in data['nba']:
        dates.add(normalize_date(g['date']))
    return dates

def get_missing_dates(dates_with_data):
    """Get list of dates that still need to be scraped."""
    season_start = date(2025, 10, 21)
    season_end = date(2026, 4, 13)
    all_dates = []
    current = season_start
    while current <= season_end:
        d = current.strftime('%Y-%m-%d')
        if d not in dates_with_data:
            all_dates.append(d)
        current += timedelta(days=1)
    return all_dates

def add_games_to_data(data, games, date_str):
    """Add parsed games to the data, avoiding duplicates."""
    # Get existing game keys to avoid duplicates
    existing_keys = set()
    for g in data['nba']:
        key = f"{normalize_date(g['date'])}_{g['away']}_{g['home']}"
        existing_keys.add(key)
    
    added = 0
    for g in games:
        key = f"{date_str}_{g['away']}_{g['home']}"
        if key not in existing_keys:
            g['date'] = date_str  # Ensure consistent date format
            data['nba'].append(g)
            existing_keys.add(key)
            added += 1
    
    # Update metadata
    data['metadata']['nba_count'] = len(data['nba'])
    data['metadata']['total_count'] = len(data['nba']) + len(data['wnba'])
    data['metadata']['nba_coverage_pct'] = round(len(data['nba']) / 1230 * 100, 1)
    data['metadata']['total_coverage_pct'] = round(
        (len(data['nba']) + len(data['wnba'])) / 1447 * 100, 1
    )
    
    return added

def process_fetched_page(date_str, page_content):
    """Process a fetched Covers.com page and add games to data."""
    data = load_data()
    progress = load_progress()
    
    games = parse_covers_page(page_content, date_str)
    
    if games:
        added = add_games_to_data(data, games, date_str)
        save_data(data)
        progress['scraped_dates'].append(date_str)
        print(f"  ✅ {date_str}: {len(games)} games found, {added} new added")
    else:
        progress['no_games_dates'].append(date_str)
        print(f"  ⚠️  {date_str}: No games found (possibly off day)")
    
    save_progress(progress)
    
    # Print current stats
    nba_count = len(data['nba'])
    wnba_count = len(data['wnba'])
    total = nba_count + wnba_count
    print(f"  📊 Current: {nba_count} NBA + {wnba_count} WNBA = {total} total ({nba_count/1230*100:.1f}% NBA coverage)")
    
    return len(games)

def print_status():
    """Print current scraping status."""
    data = load_data()
    progress = load_progress()
    dates_with_data = get_dates_with_data(data)
    missing = get_missing_dates(dates_with_data)
    
    print(f"\n📊 Scraping Status:")
    print(f"  NBA games: {len(data['nba'])}/1,230 ({len(data['nba'])/1230*100:.1f}%)")
    print(f"  WNBA games: {len(data['wnba'])}/217 ({len(data['wnba'])/217*100:.1f}%)")
    print(f"  Total: {len(data['nba']) + len(data['wnba'])}/1,447 ({(len(data['nba']) + len(data['wnba']))/1447*100:.1f}%)")
    print(f"  Dates scraped: {len(progress['scraped_dates'])}")
    print(f"  Dates with no games: {len(progress['no_games_dates'])}")
    print(f"  Dates failed: {len(progress['failed_dates'])}")
    print(f"  Missing dates: {len(missing)}")
    print(f"\n  Next dates to scrape (first 20):")
    for d in missing[:20]:
        print(f"    {d}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            print_status()
        elif sys.argv[1] == "process" and len(sys.argv) > 2:
            # Process a page from a file
            date_str = sys.argv[2]
            page_file = sys.argv[3] if len(sys.argv) > 3 else f"scraped_data/pages/{date_str}.txt"
            with open(page_file) as f:
                content = f.read()
            process_fetched_page(date_str, content)
        elif sys.argv[1] == "missing":
            data = load_data()
            dates_with_data = get_dates_with_data(data)
            missing = get_missing_dates(dates_with_data)
            print(f"Missing dates ({len(missing)}):")
            for d in missing:
                print(d)
    else:
        print_status()
