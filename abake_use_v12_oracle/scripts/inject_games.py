#!/usr/bin/env python3
"""Inject new games into the all_games_with_real_lines.json dataset with deduplication."""

import json
import sys
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'all_games_with_real_lines.json')

# Covers.com abbreviation mapping to standard NBA abbreviations
COVERS_TO_NBA = {
    'GS': 'GSW', 'NO': 'NOP', 'SA': 'SAS', 'BK': 'BKN', 'NY': 'NYK',
    'PHO': 'PHX', 'LAC': 'LAC', 'LAL': 'LAL', 'OKC': 'OKC', 'HOU': 'HOU',
    'DEN': 'DEN', 'BOS': 'BOS', 'MIA': 'MIA', 'MIL': 'MIL', 'MIN': 'MIN',
    'DAL': 'DAL', 'DET': 'DET', 'IND': 'IND', 'ATL': 'ATL', 'CHA': 'CHA',
    'ORL': 'ORL', 'WAS': 'WAS', 'CLE': 'CLE', 'CHI': 'CHI', 'TOR': 'TOR',
    'PHI': 'PHI', 'BKN': 'BKN', 'NYK': 'NYK', 'POR': 'POR', 'SAC': 'SAC',
    'UTA': 'UTA', 'MEM': 'MEM', 'SAS': 'SAS', 'NOP': 'NOP', 'GSW': 'GSW',
    'PHX': 'PHX', 'LAC': 'LAC', 'OKC': 'OKC', 'MIL': 'MIL',
}

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_game_key(game):
    """Create a unique key for a game: (date, away, home)"""
    return (game['date'], game['away'], game['home'])

def get_existing_keys(data):
    """Get all existing game keys from the NBA dataset"""
    keys = set()
    for g in data['nba']:
        keys.add(get_game_key(g))
    return keys

def normalize_abbr(abbr):
    """Normalize a team abbreviation"""
    return COVERS_TO_NBA.get(abbr, abbr)

def add_games(new_games):
    """Add new games to the dataset, skipping duplicates.
    
    new_games: list of dicts with keys:
        date, away, away_score, home, home_score, market_total, market_spread, favorite
    
    Returns: (added_count, skipped_count, total_before, total_after)
    """
    data = load_data()
    existing_keys = get_existing_keys(data)
    total_before = len(data['nba'])
    
    added = 0
    skipped = 0
    
    for game in new_games:
        # Normalize abbreviations
        game['away'] = normalize_abbr(game['away'])
        game['home'] = normalize_abbr(game['home'])
        
        # Derive favorite from spread
        spread = game['market_spread']
        if spread > 0:
            game['favorite'] = game['home']
        elif spread < 0:
            game['favorite'] = game['away']
        else:
            game['favorite'] = game['home']  # pick'em, default to home
        
        key = get_game_key(game)
        if key in existing_keys:
            skipped += 1
        else:
            data['nba'].append(game)
            existing_keys.add(key)
            added += 1
    
    # Sort by date
    data['nba'].sort(key=lambda g: (g['date'], g['away']))
    data['metadata']['nba_count'] = len(data['nba'])
    data['metadata']['total_count'] = len(data['nba']) + len(data['wnba'])
    
    save_data(data)
    total_after = len(data['nba'])
    
    return added, skipped, total_before, total_after

if __name__ == '__main__':
    # Test by showing current state
    data = load_data()
    nba = data['nba']
    wnba = data['wnba']
    print("Current dataset:")
    print("  NBA: {} games".format(len(nba)))
    print("  WNBA: {} games".format(len(wnba)))
    print("  Total: {} games".format(len(nba) + len(wnba)))
    print("  NBA target: 1,230 games")
    print("  Coverage: {:.1f}%".format(len(nba) / 1230 * 100))
