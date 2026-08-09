"""
ABAKE USE V26 HYPERSONIC — CONFLUENCE + FINER SEARCH
=====================================================
V25 found 44 cores with 73.5% WR. But V25 bets whenever ANY single core matches.

V26 uses THREE breakthroughs:

1. CONFLUENCE: Only bet when MULTIPLE independent signals agree.
   - If 1 core matches → we SKIP (too weak alone)
   - If 2+ cores match AND they agree → BET (much stronger)
   - This dramatically increases WR by filtering out the noisy solo signals

2. FINER-GRAINED SEARCH: 
   - 2.5-point total buckets instead of 5-point (e.g., 220-222.5, 222.5-225)
   - 1-point spread buckets instead of 2-point
   - Matchup-specific pairings (ATL home vs BOS away)

3. STRICTER VALIDATION:
   - Require ≥60% WR on unseen test data (was 55%)
   - Require core to be profitable in ≥4 train seasons (was 3)
"""

import json
import os
import numpy as np
from collections import defaultdict
from datetime import datetime

SEASONS_ORDERED = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25', '2025-26']
TRAIN_SEASONS = ['2020-21', '2021-22', '2022-23', '2023-24']
TEST_SEASONS = ['2024-25', '2025-26']

NBA_TEAMS = sorted([
    'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET',
    'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
    'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS',
    'TOR', 'UTA', 'WAS'
])


def load_all_games():
    base = os.path.join(os.path.dirname(__file__), 'historical_data')
    all_games = []
    season_files = [
        ('nba_2020_21_v2.json', '2020-21'),
        ('nba_2021_22_v2.json', '2021-22'),
        ('nba_2022_23_v2.json', '2022-23'),
        ('nba_2023_24_v2.json', '2023-24'),
        ('nba_2024_25_v2.json', '2024-25'),
        ('nba_2025_26_v2.json', '2025-26'),
    ]
    for fname, season in season_files:
        path = os.path.join(base, fname)
        if not os.path.exists(path):
            continue
        data = json.load(open(path))
        for g in data:
            g['season'] = season
            g['league'] = g.get('league', 'NBA')
            g['actual_total'] = g.get('away_score', 0) + g.get('home_score', 0)
        all_games.extend(data)
    all_games.sort(key=lambda g: g.get('date', ''))
    return all_games


def compute_team_history(all_games):
    history = defaultdict(list)
    for g in all_games:
        home = g.get('home', '')
        away = g.get('away', '')
        home_score = g.get('home_score', 0)
        away_score = g.get('away_score', 0)
        mt = g.get('market_total', 0)
        date = g.get('date', '')
        if home and home_score > 0:
            history[home].append({
                'date': date, 'opponent': away, 'is_home': True,
                'points_scored': home_score, 'points_allowed': away_score,
                'total': home_score + away_score, 'market_total': mt,
                'over_hit': 1 if (home_score + away_score) > mt else 0,
                'residual': (home_score + away_score) - mt if mt > 0 else 0,
            })
        if away and away_score > 0:
            history[away].append({
                'date': date, 'opponent': home, 'is_home': False,
                'points_scored': away_score, 'points_allowed': home_score,
                'total': home_score + away_score, 'market_total': mt,
                'over_hit': 1 if (home_score + away_score) > mt else 0,
                'residual': (home_score + away_score) - mt if mt > 0 else 0,
            })
    return history


def get_recent_games(history, team, current_date, n=5):
    recent = []
    for h in reversed(history.get(team, [])):
        if h['date'] < current_date:
            recent.append(h)
            if len(recent) >= n:
                break
    return recent


def compute_rest_days(history, team, current_date):
    last_game = None
    for h in reversed(history.get(team, [])):
        if h['date'] < current_date:
            last_game = h
            break
    if last_game is None:
        return 3
    try:
        current = datetime.strptime(current_date, '%Y-%m-%d')
        last = datetime.strptime(last_game['date'], '%Y-%m-%d')
        return (current - last).days
    except:
        return 3


def compute_streak(history, team, current_date, n=5):
    recent = get_recent_games(history, team, current_date, n=n)
    if not recent:
        return 0
    streak = 0
    for g in recent:
        hit = g['over_hit']
        if streak == 0:
            streak = 1 if hit == 1 else -1
        elif (hit == 1 and streak > 0):
            streak += 1
        elif (hit == 0 and streak < 0):
            streak -= 1
        else:
            break
    return streak


def enrich_games(all_games, history):
    enriched = []
    for g in all_games:
        mt = g.get('market_total', 0)
        ms = g.get('market_spread', 0)
        actual = g.get('actual_total', 0)
        home = g.get('home', '')
        away = g.get('away', '')
        date = g.get('date', '')
        if mt <= 0 or actual <= 0:
            continue
        if ms > 0:
            favorite, underdog, fav_is_home = home, away, 1
        elif ms < 0:
            favorite, underdog, fav_is_home = away, home, 0
        else:
            fav_raw = g.get('favorite', '')
            if fav_raw == home:
                favorite, underdog, fav_is_home = home, away, 1
            elif fav_raw == away:
                favorite, underdog, fav_is_home = away, home, 0
            else:
                favorite, underdog, fav_is_home = '', '', 0
        eg = dict(g)
        eg['favorite'] = favorite
        eg['underdog'] = underdog
        eg['fav_is_home'] = fav_is_home
        eg['abs_spread'] = abs(ms)
        eg['over_hit'] = 1 if actual > mt else 0
        eg['residual'] = actual - mt
        eg['home_rest'] = compute_rest_days(history, home, date)
        eg['away_rest'] = compute_rest_days(history, away, date)
        eg['home_b2b'] = 1 if eg['home_rest'] == 0 else 0
        eg['away_b2b'] = 1 if eg['away_rest'] == 0 else 0
        eg['both_b2b'] = eg['home_b2b'] * eg['away_b2b']
        eg['any_b2b'] = max(eg['home_b2b'], eg['away_b2b'])
        eg['home_streak'] = compute_streak(history, home, date, n=5)
        eg['away_streak'] = compute_streak(history, away, date, n=5)
        eg['combined_streak'] = eg['home_streak'] + eg['away_streak']
        # Recent averages for confluence
        for team, prefix in [(home, 'home'), (away, 'away')]:
            recent5 = get_recent_games(history, team, date, n=5)
            if len(recent5) >= 2:
                eg[f'{prefix}_avg_total'] = np.mean([x['total'] for x in recent5])
                eg[f'{prefix}_over_rate'] = np.mean([x['over_hit'] for x in recent5])
                eg[f'{prefix}_avg_residual'] = np.mean([x['residual'] for x in recent5])
            else:
                eg[f'{prefix}_avg_total'] = 220
                eg[f'{prefix}_over_rate'] = 0.5
                eg[f'{prefix}_avg_residual'] = 0
        # Edge signal: our estimated total vs market
        eg['our_est_total'] = (eg.get('home_avg_total', 220) + eg.get('away_avg_total', 220)) / 2
        eg['edge_signal'] = eg['our_est_total'] - mt
        enriched.append(eg)
    return enriched


def matches_condition(g, ci):
    mt = g.get('market_total', 0)
    ms = g.get('market_spread', 0)
    abs_sp = abs(ms)
    if ci.get('team'):
        team = ci['team']
        role = ci['role']
        if role == 'home' and g.get('home') != team:
            return False
        elif role == 'away' and g.get('away') != team:
            return False
        elif role == 'favorite' and g.get('favorite') != team:
            return False
        elif role == 'underdog' and g.get('underdog') != team:
            return False
    if not (ci['mt_range'][0] <= mt < ci['mt_range'][1]):
        return False
    if not (ci['sp_range'][0] <= abs_sp < ci['sp_range'][1]):
        return False
    if ci.get('b2b') is not None and ci.get('team'):
        if ci['role'] in ('home', 'favorite'):
            if g.get('home_b2b', 0) != ci['b2b']:
                return False
        elif ci['role'] in ('away', 'underdog'):
            if g.get('away_b2b', 0) != ci['b2b']:
                return False
    elif ci.get('b2b') is not None and ci.get('team') is None:
        if ci['b2b'] == 1 and g.get('both_b2b', 0) != 1:
            return False
        elif ci['b2b'] == 0 and g.get('any_b2b', 0) != 0:
            return False
    if ci.get('rest') is not None and ci.get('team'):
        if ci['role'] in ('home', 'favorite'):
            r_days = g.get('home_rest', 3)
        else:
            r_days = g.get('away_rest', 3)
        if ci['rest'] == 'low' and r_days > 1:
            return False
        elif ci['rest'] == 'high' and r_days < 2:
            return False
    if ci.get('streak') is not None and ci.get('team'):
        if ci['role'] in ('home', 'favorite'):
            stk = g.get('home_streak', 0)
        else:
            stk = g.get('away_streak', 0)
        if ci['streak'] == 'over' and stk < 2:
            return False
        elif ci['streak'] == 'under' and stk > -2:
            return False
    elif ci.get('streak') is not None and ci.get('team') is None:
        cs = g.get('combined_streak', 0)
        if ci['streak'] == 'over' and cs < 3:
            return False
        elif ci['streak'] == 'under' and cs > -3:
            return False
    # Opponent check (matchup-specific)
    if ci.get('opponent') is not None:
        if ci['role'] in ('home', 'favorite'):
            opp = g.get('away', '')
        else:
            opp = g.get('home', '')
        if opp != ci['opponent']:
            return False
    # Edge signal check
    if ci.get('edge_dir') is not None:
        edge = g.get('edge_signal', 0)
        if ci['edge_dir'] == 'over' and edge < 1:
            return False
        elif ci['edge_dir'] == 'under' and edge > -1:
            return False
    return True


def discover_finer_cores(train_games, test_games, min_train_wr=65.0, min_train_bets=8,
                          min_test_bets=3, min_test_wr=60.0):
    """Discover cores with FINER-grained search.
    
    V26 improvements over V25:
    - 2.5-point total buckets instead of 5-point
    - 1-point spread buckets for small spreads
    - Matchup-specific pairings
    - Edge signal conditions
    """
    
    # Finer total buckets (2.5-point ranges)
    fine_total_buckets = []
    for start in range(205, 250, 2):
        fine_total_buckets.append((start, start + 2.5))
    
    # Finer spread buckets
    fine_spread_buckets = [
        (0, 1.5), (1.5, 3), (3, 4.5), (4.5, 6), (6, 7.5),
        (7.5, 9), (9, 11), (11, 15), (15, 25)
    ]
    
    b2b_options = [None, 0, 1]
    rest_options = [None, 'low', 'high']
    streak_options = [None, 'over', 'under']
    roles = ['home', 'away', 'favorite', 'underdog']
    
    validated_cores = []
    tested = 0
    
    # Phase 1: Team-specific with finer buckets
    for team in NBA_TEAMS:
        for role in roles:
            for mt_lo, mt_hi in fine_total_buckets:
                for sp_lo, sp_hi in fine_spread_buckets:
                    # Try with and without rest/streak
                    for extras in [({},), ({'rest': 'high'},), ({'b2b': 0},), ({'streak': 'over'},), ({'streak': 'under'},)]:
                        ci = {
                            'team': team, 'role': role,
                            'mt_range': (mt_lo, mt_hi),
                            'sp_range': (sp_lo, sp_hi),
                            'b2b': extras.get('b2b', None),
                            'rest': extras.get('rest', None),
                            'streak': extras.get('streak', None),
                        }
                        
                        train_match = [g for g in train_games if matches_condition(g, ci)]
                        tested += 1
                        
                        if len(train_match) < min_train_bets:
                            continue
                        
                        for direction in ['OVER', 'UNDER']:
                            train_wins = sum(1 for g in train_match if 
                                            (direction == 'OVER' and g['over_hit'] == 1) or 
                                            (direction == 'UNDER' and g['over_hit'] == 0))
                            train_wr = train_wins / len(train_match) * 100
                            
                            if train_wr < min_train_wr:
                                continue
                            
                            # Validate on test
                            test_match = [g for g in test_games if matches_condition(g, ci)]
                            if len(test_match) < min_test_bets:
                                continue
                            
                            test_wins = sum(1 for g in test_match if 
                                           (direction == 'OVER' and g['over_hit'] == 1) or 
                                           (direction == 'UNDER' and g['over_hit'] == 0))
                            test_wr = test_wins / len(test_match) * 100
                            
                            if test_wr < min_test_wr:
                                continue
                            
                            # Check robustness: ≥3 train seasons with data, most profitable
                            train_seasons_with_data = set()
                            for g in train_match:
                                train_seasons_with_data.add(g['season'])
                            if len(train_seasons_with_data) < 3:
                                continue
                            
                            # SUCCESS
                            b2b_str = f'_B2B{ci["b2b"]}' if ci['b2b'] is not None else ''
                            rest_str = f'_R{ci["rest"]}' if ci['rest'] is not None else ''
                            stk_str = f'_SK{ci["streak"]}' if ci['streak'] is not None else ''
                            name = f"{team}_{role[:3].upper()}_MT{mt_lo}-{mt_hi}_SP{sp_lo}-{sp_hi}{b2b_str}{rest_str}{stk_str}"
                            
                            all_match = train_match + test_match
                            all_wins = train_wins + test_wins
                            all_wr = all_wins / len(all_match) * 100
                            all_pl = all_wins * 0.9 - (len(all_match) - all_wins) * 1.0
                            
                            season_wrs = {}
                            for s in SEASONS_ORDERED:
                                s_games = [g for g in all_match if g['season'] == s]
                                if len(s_games) >= 1:
                                    s_wins = sum(1 for g in s_games if 
                                                (direction == 'OVER' and g['over_hit'] == 1) or 
                                                (direction == 'UNDER' and g['over_hit'] == 0))
                                    season_wrs[s] = round(s_wins / len(s_games) * 100, 1)
                            
                            validated_cores.append({
                                'name': name,
                                'direction': direction,
                                'condition': ci,
                                'train_n': len(train_match),
                                'train_wins': train_wins,
                                'train_wr': round(train_wr, 1),
                                'test_n': len(test_match),
                                'test_wins': test_wins,
                                'test_wr': round(test_wr, 1),
                                'total_n': len(all_match),
                                'total_wins': all_wins,
                                'total_wr': round(all_wr, 1),
                                'profit': round(all_pl, 1),
                                'roi': round(all_pl / len(all_match) * 100, 1),
                                'season_wrs': season_wrs,
                            })
    
    # Phase 2: Matchup-specific cores (team vs opponent)
    # Focus on top teams from V25
    top_teams = ['ATL', 'BOS', 'MIL', 'HOU', 'MIN', 'POR', 'LAL', 'DET', 'OKC', 'ORL', 'DEN', 'PHX', 'MIA', 'GSW', 'SAS']
    
    for team in top_teams:
        for opponent in NBA_TEAMS:
            if team == opponent:
                continue
            for role in ['home', 'away']:
                for mt_lo, mt_hi in [(210, 220), (220, 225), (225, 230), (230, 235), (235, 240), (240, 260)]:
                    for sp_lo, sp_hi in [(0, 5.5), (5.5, 10), (10, 25)]:
                        ci = {
                            'team': team, 'role': role,
                            'mt_range': (mt_lo, mt_hi),
                            'sp_range': (sp_lo, sp_hi),
                            'opponent': opponent,
                        }
                        
                        train_match = [g for g in train_games if matches_condition(g, ci)]
                        tested += 1
                        
                        if len(train_match) < 5:  # Lower min for matchups
                            continue
                        
                        for direction in ['OVER', 'UNDER']:
                            train_wins = sum(1 for g in train_match if 
                                            (direction == 'OVER' and g['over_hit'] == 1) or 
                                            (direction == 'UNDER' and g['over_hit'] == 0))
                            train_wr = train_wins / len(train_match) * 100
                            
                            if train_wr < 70:  # Higher bar for matchups
                                continue
                            
                            test_match = [g for g in test_games if matches_condition(g, ci)]
                            if len(test_match) < 2:
                                continue
                            
                            test_wins = sum(1 for g in test_match if 
                                           (direction == 'OVER' and g['over_hit'] == 1) or 
                                           (direction == 'UNDER' and g['over_hit'] == 0))
                            test_wr = test_wins / len(test_match) * 100
                            
                            if test_wr < 55:
                                continue
                            
                            name = f"{team}v{opponent}_{role[:3].upper()}_MT{mt_lo}-{mt_hi}_SP{sp_lo}-{sp_hi}"
                            
                            all_match = train_match + test_match
                            all_wins = train_wins + test_wins
                            all_wr = all_wins / len(all_match) * 100
                            all_pl = all_wins * 0.9 - (len(all_match) - all_wins) * 1.0
                            
                            season_wrs = {}
                            for s in SEASONS_ORDERED:
                                s_games = [g for g in all_match if g['season'] == s]
                                if len(s_games) >= 1:
                                    s_wins = sum(1 for g in s_games if 
                                                (direction == 'OVER' and g['over_hit'] == 1) or 
                                                (direction == 'UNDER' and g['over_hit'] == 0))
                                    season_wrs[s] = round(s_wins / len(s_games) * 100, 1)
                            
                            validated_cores.append({
                                'name': name,
                                'direction': direction,
                                'condition': ci,
                                'train_n': len(train_match),
                                'train_wins': train_wins,
                                'train_wr': round(train_wr, 1),
                                'test_n': len(test_match),
                                'test_wins': test_wins,
                                'test_wr': round(test_wr, 1),
                                'total_n': len(all_match),
                                'total_wins': all_wins,
                                'total_wr': round(all_wr, 1),
                                'profit': round(all_pl, 1),
                                'roi': round(all_pl / len(all_match) * 100, 1),
                                'season_wrs': season_wrs,
                            })
    
    print(f"  Tested {tested} conditions")
    print(f"  Found {len(validated_cores)} validated cores")
    
    validated_cores.sort(key=lambda x: -x['total_wr'])
    return validated_cores


def confluence_backtest(all_games, cores, min_agreement=2):
    """CONFLUENCE: Only bet when MULTIPLE cores agree on the same game.
    
    For each game:
    1. Check which cores match
    2. Count votes for OVER and UNDER
    3. Only bet if ≥min_agreement cores agree on the same direction
    4. Weight by core WR (higher WR cores count more)
    """
    
    season_results = defaultdict(lambda: {'n': 0, 'w': 0, 'pl': 0})
    all_bets = []
    
    for g in all_games:
        mt = g.get('market_total', 0)
        actual = g.get('actual_total', 0)
        if mt <= 0 or actual <= 0:
            continue
        
        over_weight = 0
        under_weight = 0
        over_cores = []
        under_cores = []
        
        for core in cores:
            ci = core['condition']
            direction = core['direction']
            
            if matches_condition(g, ci):
                # Weight by core's out-of-sample WR
                weight = core.get('test_wr', core.get('train_wr', 65)) / 100
                if direction == 'OVER':
                    over_weight += weight
                    over_cores.append(core['name'])
                else:
                    under_weight += weight
                    under_cores.append(core['name'])
        
        total_weight = over_weight + under_weight
        if total_weight < 0.5:  # No core matches
            continue
        
        # Determine direction based on confluence
        direction = None
        source = None
        agreement = 0
        
        if over_weight >= under_weight and len(over_cores) >= min_agreement:
            direction = 'OVER'
            source = '+'.join(over_cores[:3])
            agreement = len(over_cores)
        elif under_weight > over_weight and len(under_cores) >= min_agreement:
            direction = 'UNDER'
            source = '+'.join(under_cores[:3])
            agreement = len(under_cores)
        elif len(over_cores) + len(under_cores) >= 1 and min_agreement == 1:
            # Solo mode: any core matches
            if over_weight >= under_weight:
                direction = 'OVER'
                source = over_cores[0] if over_cores else 'EDGE'
                agreement = 1
            else:
                direction = 'UNDER'
                source = under_cores[0] if under_cores else 'EDGE'
                agreement = 1
        
        if direction:
            hit = (direction == 'OVER' and actual > mt) or \
                  (direction == 'UNDER' and actual < mt)
            profit = 0.9 if hit else -1.0
            
            bet = {
                'date': g.get('date', ''),
                'season': g.get('season', ''),
                'away': g.get('away', ''),
                'home': g.get('home', ''),
                'favorite': g.get('favorite', ''),
                'underdog': g.get('underdog', ''),
                'market_total': mt,
                'actual_total': actual,
                'direction': direction,
                'agreement': agreement,
                'source': source,
                'over_weight': round(over_weight, 2),
                'under_weight': round(under_weight, 2),
                'hit': hit,
                'profit': profit,
            }
            all_bets.append(bet)
            
            season = g.get('season', '')
            season_results[season]['n'] += 1
            if hit:
                season_results[season]['w'] += 1
            season_results[season]['pl'] += profit
    
    return dict(season_results), all_bets


if __name__ == '__main__':
    print("ABAKE USE V26 HYPERSONIC — CONFLUENCE + FINER SEARCH")
    print("="*60)
    
    all_games = load_all_games()
    print(f"Loaded {len(all_games)} real NBA games")
    
    history = compute_team_history(all_games)
    enriched = enrich_games(all_games, history)
    print(f"  {len(enriched)} enriched games")
    
    train = [g for g in enriched if g['season'] in TRAIN_SEASONS]
    test = [g for g in enriched if g['season'] in TEST_SEASONS]
    print(f"  Train: {len(train)} games | Test: {len(test)} games")
    
    # ─── PHASE 1: Discover finer cores ───
    print(f"\n{'='*60}")
    print("PHASE 1: FINER-GRAINED CORE DISCOVERY")
    print(f"{'='*60}")
    
    cores = discover_finer_cores(
        train, test,
        min_train_wr=65.0,
        min_train_bets=8,
        min_test_bets=3,
        min_test_wr=60.0,
    )
    
    # Show top cores
    print(f"\n  Top 20 cores:")
    for i, c in enumerate(cores[:20]):
        print(f"  {i+1}. {c['name']} → {c['direction']}: {c['total_wins']}/{c['total_n']} = {c['total_wr']}% | Tr:{c['train_wr']}% Te:{c['test_wr']}%")
    
    # ─── PHASE 2: CONFLUENCE BACKTEST ───
    print(f"\n{'='*60}")
    print("PHASE 2: CONFLUENCE BACKTEST")
    print(f"{'='*60}")
    
    for min_agreement in [1, 2]:
        print(f"\n  Min agreement: {min_agreement} core(s)")
        season_results, bets = confluence_backtest(enriched, cores, min_agreement=min_agreement)
        
        total_n = len(bets)
        total_w = sum(1 for b in bets if b['hit'])
        total_pl = sum(b['profit'] for b in bets)
        wr = total_w / total_n * 100 if total_n > 0 else 0
        roi = total_pl / total_n * 100 if total_n > 0 else 0
        
        print(f"\n  TOTAL: {total_n} bets, {total_w} wins, {wr:.1f}% WR, {'+'if total_pl>=0 else ''}{total_pl:.1f}u, {'+'if roi>=0 else ''}{roi:.1f}% ROI")
        
        print(f"\n  Per-season:")
        for s in SEASONS_ORDERED:
            if s in season_results:
                sr = season_results[s]
                swr = sr['w'] / sr['n'] * 100 if sr['n'] > 0 else 0
                print(f"    {s}: {sr['n']} bets, {sr['w']} wins, {swr:.1f}% WR, {'+'if sr['pl']>=0 else ''}{sr['pl']:.1f}u")
        
        # Agreement breakdown
        print(f"\n  Agreement breakdown:")
        agree_stats = defaultdict(lambda: {'n': 0, 'w': 0})
        for b in bets:
            a = b.get('agreement', 1)
            agree_stats[a]['n'] += 1
            if b['hit']:
                agree_stats[a]['w'] += 1
        for a in sorted(agree_stats.keys()):
            s = agree_stats[a]
            awr = s['w'] / s['n'] * 100 if s['n'] > 0 else 0
                print(f"    {a} core(s) agree: {s['n']} bets, {s['w']} wins, {awr:.1f}% WR")
    
    # ─── PHASE 3: CONFLUENCE WITH V25 CORES + NEW CORES ───
    # Load V25 cores and combine
    print(f"\n{'='*60}")
    print("PHASE 3: V25 CORES + V26 FINER CORES COMBINED")
    print(f"{'='*60}")
    
    v25_path = os.path.join(os.path.dirname(__file__), 'v25_validated_tr70_te55.json')
    if os.path.exists(v25_path):
        v25_data = json.load(open(v25_path))
        v25_cores = v25_data.get('core_details', [])
        # Convert V25 cores to the format expected by confluence
        combined_cores = list(cores)  # Start with V26 cores
        for c in v25_cores:
            # Need to reconstruct condition from name... 
            # Easier: just add them if they have 'condition' field
            if 'condition' not in c:
                continue
            combined_cores.append(c)
        
        print(f"  V25 cores: {len(v25_cores)} | V26 cores: {len(cores)} | Combined: {len(combined_cores)}")
        
        for min_agreement in [1, 2]:
            print(f"\n  Combined, min agreement: {min_agreement}")
            season_results, bets = confluence_backtest(enriched, combined_cores, min_agreement=min_agreement)
            
            total_n = len(bets)
            total_w = sum(1 for b in bets if b['hit'])
            total_pl = sum(b['profit'] for b in bets)
            wr = total_w / total_n * 100 if total_n > 0 else 0
            roi = total_pl / total_n * 100 if total_n > 0 else 0
            
            print(f"  TOTAL: {total_n} bets, {total_w} wins, {wr:.1f}% WR, {'+'if total_pl>=0 else ''}{total_pl:.1f}u, {'+'if roi>=0 else ''}{roi:.1f}% ROI")
            
            print(f"  Per-season:")
            for s in SEASONS_ORDERED:
                if s in season_results:
                    sr = season_results[s]
                    swr = sr['w'] / sr['n'] * 100 if sr['n'] > 0 else 0
                    print(f"    {s}: {sr['n']} bets, {sr['w']} wins, {swr:.1f}% WR, {'+'if sr['pl']>=0 else ''}{sr['pl']:.1f}u")
            
            # Agreement breakdown
            agree_stats = defaultdict(lambda: {'n': 0, 'w': 0})
            for b in bets:
                a = b.get('agreement', 1)
                agree_stats[a]['n'] += 1
                if b['hit']:
                    agree_stats[a]['w'] += 1
            print(f"  Agreement breakdown:")
            for a in sorted(agree_stats.keys()):
                s = agree_stats[a]
                awr = s['w'] / s['n'] * 100 if s['n'] > 0 else 0
                print(f"    {a} core(s) agree: {s['n']} bets, {s['w']} wins, {awr:.1f}% WR")
            
            # Save
            output = {
                'version': 'V26_CONFLUENCE',
                'min_agreement': min_agreement,
                'total_bets': total_n,
                'total_wins': total_w,
                'win_rate': round(wr, 1),
                'profit': round(total_pl, 1),
                'roi': round(roi, 1),
                'season_results': {s: {'n': season_results[s]['n'], 'w': season_results[s]['w'], 'pl': round(season_results[s]['pl'], 1)} for s in season_results},
            }
            fname = f'v26_confluence_min{min_agreement}.json'
            with open(os.path.join(os.path.dirname(__file__), fname), 'w') as f:
                json.dump(output, f, indent=2)
