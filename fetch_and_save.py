#!/usr/bin/env python3
"""
Batch fetch and save Covers.com pages for NBA 2025-26 season.
Run this to generate the list of URLs to fetch, then manually fetch each
using the fetch_page tool and save the content.
"""
import os, json, re
from datetime import datetime, timedelta

PAGES_DIR = "/home/user/habeeb-jimoh/scraped_data/pages"
os.makedirs(PAGES_DIR, exist_ok=True)

def save_page(date_str, content):
    """Save a fetched page to disk."""
    filepath = os.path.join(PAGES_DIR, f"nba_{date_str}.txt")
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath

def get_existing_dates():
    """Get list of dates that have already been scraped."""
    existing = []
    for f in os.listdir(PAGES_DIR):
        if f.startswith("nba_") and f.endswith(".txt"):
            date_str = f[4:-4]  # Extract date from filename
            existing.append(date_str)
    return sorted(existing)

def get_missing_dates():
    """Get list of dates that still need to be scraped."""
    start = datetime(2025, 10, 21)
    end = datetime(2026, 4, 13)
    all_dates = []
    current = start
    while current <= end:
        all_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    existing = set(get_existing_dates())
    missing = [d for d in all_dates if d not in existing]
    return missing

def generate_urls():
    """Generate URLs for all missing dates."""
    missing = get_missing_dates()
    urls = []
    for d in missing:
        url = f"https://www.covers.com/sports/nba/matchups?selectedDate={d}"
        urls.append((d, url))
    return urls

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "missing":
            missing = get_missing_dates()
            print(f"Missing dates: {len(missing)}")
            for d in missing[:20]:
                print(f"  {d}")
            if len(missing) > 20:
                print(f"  ... and {len(missing)-20} more")
        elif sys.argv[1] == "existing":
            existing = get_existing_dates()
            print(f"Existing dates: {len(existing)}")
        elif sys.argv[1] == "save" and len(sys.argv) > 3:
            # Save a page: python fetch_and_save.py save 2025-10-21 "content"
            date_str = sys.argv[2]
            content = sys.argv[3]
            save_page(date_str, content)
            print(f"Saved page for {date_str}")
    else:
        urls = generate_urls()
        print(f"Total URLs to fetch: {len(urls)}")
        for d, url in urls[:5]:
            print(f"  {d}: {url}")
