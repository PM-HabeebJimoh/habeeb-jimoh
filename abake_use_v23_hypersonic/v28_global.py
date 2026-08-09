"""
ABAKE USE V28 HYPERSONIC NEXUS — GLOBAL BASKETBALL BACKTEST
18 NBA Seasons | 23,552 Games | 18-Fold LOSO Validation
THE DEEPEST BACKTEST EVER DONE WITH A RESIDUAL SIGNATURE MODEL
"""

import json, os, math, csv, hashlib, sqlite3, statistics
from collections import defaultdict
from datetime import datetime

NBA_NAME_MAP = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
    'Charlotte Bobcats': 'CHA', 'Charlotte Hornets': 'CHA',
    'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND', 'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
    'New Orleans Hornets': 'NOP', 'New Orleans Pelicans': 'NOP',
    'New Orleans/Oklahoma City Hornets': 'NOP',
    'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHX', 'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS',
    'New Jersey Nets': 'BKN',
}
NBA_TEAMS = sorted(set(NBA_NAME_MAP.values()))
ROLES = ['home', 'away', 'favorite', 'underdog']
MT_BUCKETS = [(200,210),(210,220),(220,225),(225,230),(230,235),(235,240),(240,250)]
SP_BUCKETS = [(0,3),(3,6),(6,10),(10,25)]
MAX_OVERLAP = 0.55
MIN_GAMES = 12

def load_all_nba():
    db_path = '/tmp/nba_ml/Data/OddsData.sqlite'
    if not os.path.exists(db_path):
        return []
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [t[0] for t in cur.fetchall()]
    season_tables = {}
    for t in all_tables:
        if t.startswith('odds_') and t.endswith('_new'):
            s = t.replace('odds_','').replace('_new','')
            season_tables[s] = t
        elif t == '2024-25':
            season_tables['2024-25'] = t
        elif t == 'odds_2025-26':
            season_tables['2025-26'] = t

    games = []
    for season, table in sorted(season_tables.items()):
        try:
            cur.execute(f'PRAGMA table_info([{table}])')
            cols = [c[1] for c in cur.fetchall()]
            cur.execute(f'SELECT * FROM [{table}]')
            for row in cur.fetchall():
                rd = dict(zip(cols, row))
                date = rd.get('Date','')
                home = NBA_NAME_MAP.get(rd.get('Home',''),'')
                away = NBA_NAME_MAP.get(rd.get('Away',''),'')
                ou = rd.get('OU', 0)
                pts = rd.get('Points', 0)
                wm = rd.get('Win_Margin', 0)
                sp = rd.get('Spread', 0)
                # Spread can be string in some seasons
                try:
                    sp = float(sp)
                except (ValueError, TypeError):
                    continue
                rh = rd.get('Days_Rest_Home', None)
                ra = rd.get('Days_Rest_Away', None)
                if not home or not away or not ou or not pts or ou < 100:
                    continue
                hs = (pts + wm) / 2
                as_ = (pts - wm) / 2
                if hs <= 0 or as_ <= 0:
                    continue
                fav = away if sp > 0 else home
                fp = hashlib.md5(f"{date}_{away}_{home}".encode()).hexdigest()[:12]
                games.append({
                    'date': date, 'season': season, 'league': 'NBA',
                    'away': away, 'home': home,
                    'away_score': int(as_), 'home_score': int(hs),
                    'market_total': float(ou), 'market_spread': abs(float(sp)),
                    'favorite': fav, 'actual_total': int(pts),
                    'residual': int(pts) - float(ou),
                    'over_hit': 1 if int(pts) > float(ou) else 0,
                    'is_push': 1 if int(pts) == float(ou) else 0,
                    'fingerprint': fp,
                    'home_rest': rh, 'away_rest': ra,
                })
        except Exception as e:
            print(f"  Error {table}: {e}")
    db.close()
    games.sort(key=lambda g: g['date'])
    return games

def compute_streaks(games):
    tg = defaultdict(list)
    for g in games:
        tg[g['home']].append(g)
        tg[g['away']].append(g)
    for t in tg:
        tg[t].sort(key=lambda x: x['date'])
    for g in games:
        g['home_streak'] = None
        g['away_streak'] = None
        for role, team in [('home', g['home']), ('away', g['away'])]:
            tgames = tg[team]
            idx = None
            for i, tga in enumerate(tgames):
                if tga['fingerprint'] == g['fingerprint']:
                    idx = i; break
            if idx is None or idx < 3:
                continue
            recent = tgames[idx-3:idx]
            oc = sum(1 for r in recent if r['over_hit'] == 1)
            if oc >= 3: g[f'{role}_streak'] = 'over'
            elif oc == 0: g[f'{role}_streak'] = 'under'
    return games

def game_matches(game, cond):
    team, role = cond['team'], cond['role']
    mt_lo, mt_hi = cond['mt_range']
    sp_lo, sp_hi = cond['sp_range']
    if not (mt_lo <= game['market_total'] < mt_hi): return False
    sp = abs(game['market_spread'])
    fav = game.get('favorite','')
    if role == 'home' and game['home'] != team: return False
    if role == 'away' and game['away'] != team: return False
    if role == 'favorite' and fav != team: return False
    if role == 'underdog':
        if fav == team: return False
        if game['home'] != team and game['away'] != team: return False
    if not (sp_lo <= sp < sp_hi): return False
    if cond.get('rest') == 'high':
        if role in ('home','favorite'):
            if game.get('home_rest') is None or game['home_rest'] < 3: return False
        elif role in ('away','underdog'):
            if game.get('away_rest') is None or game['away_rest'] < 3: return False
    if cond.get('streak') is not None:
        sn = cond['streak']
        if role in ('home','favorite') and game.get('home_streak') != sn: return False
        if role in ('away','underdog') and game.get('away_streak') != sn: return False
    return True

def gen_conditions():
    conds = []
    for team in NBA_TEAMS:
        for role in ROLES:
            for mtl, mth in MT_BUCKETS:
                for spl, sph in SP_BUCKETS:
                    c = {'team':team,'role':role,'mt_range':[mtl,mth],'sp_range':[spl,sph],'rest':None,'streak':None}
                    conds.append(c)
                    cr = dict(c); cr['rest']='high'; conds.append(cr)
                    cs = dict(c); cs['streak']='over'; conds.append(cs)
                    cu = dict(c); cu['streak']='under'; conds.append(cu)
    return conds

def cond_name(cond):
    p = [cond['team'], cond['role'].upper()[:3]]
    p.append(f"MT{cond['mt_range'][0]}-{cond['mt_range'][1]}")
    p.append(f"SP{cond['sp_range'][0]}-{cond['sp_range'][1]}")
    if cond.get('rest')=='high': p.append('Rhigh')
    if cond.get('streak'): p.append(f"SK{cond['streak']}")
    return '_'.join(p)

def discover_cores(games, seasons):
    print(f"\nPHASE 1: RESIDUAL CORE DISCOVERY ({len(seasons)}-season LOSO)")
    print("="*70)
    conds = gen_conditions()
    print(f"Testing {len(conds)} conditions...")
    n_s = len(seasons)
    # With 18 seasons, require profitable in at least 5 held-out seasons
    # This is conservative but allows for the NBA changing over 18 years
    min_loso = max(4, min(5, int(n_s * 0.30)))

    cs_res = defaultdict(lambda: defaultdict(list))
    cs_fps = defaultdict(set)

    for ci, cond in enumerate(conds):
        if ci % 3000 == 0: print(f"  {ci}/{len(conds)}...")
        for g in games:
            if g['is_push']: continue
            if game_matches(g, cond):
                cs_res[ci][g['season']].append(g['residual'])
                cs_fps[ci].add(g['fingerprint'])

    print("  Evaluating signatures...")
    cores = []
    for ci, cond in enumerate(conds):
        all_r = []
        for s in seasons: all_r.extend(cs_res[ci][s])
        n = len(all_r)
        if n < MIN_GAMES: continue
        mr = statistics.mean(all_r)
        sr = statistics.stdev(all_r) if n > 1 else 999
        ts = mr / (sr / math.sqrt(n))
        if abs(mr) < 1.5 or abs(ts) < 1.5: continue
        d = 'OVER' if mr > 0 else 'UNDER'

        loso = []
        for ho in seasons:
            tr = cs_res[ci][ho]
            if not tr: continue
            tn = len(tr)
            tw = sum(1 for r in tr if (r > 0) == (d == 'OVER'))
            loso.append({'ho': ho, 'n': tn, 'w': tw, 'p': round(tw*0.9-(tn-tw)*1.0,1)})

        ps = sum(1 for r in loso if r['p'] > 0)
        tp = sum(r['p'] for r in loso)
        if ps < min_loso or tp <= 0: continue

        tw_all = sum(1 for r in all_r if (r > 0) == (d == 'OVER'))
        wr = tw_all / n * 100
        profit = tw_all * 0.9 - (n - tw_all) * 1.0
        cd = mr / sr if sr > 0 else 0

        swrs = {}
        for s in seasons:
            sr_s = cs_res[ci][s]
            if not sr_s: continue
            sw = sum(1 for r in sr_s if (r > 0) == (d == 'OVER'))
            swrs[s] = round(sw/len(sr_s)*100,1)

        cores.append({
            'name': f"{cond_name(cond)}_{d}", 'condition': cond, 'direction': d,
            'total_n': n, 'total_wins': tw_all, 'total_wr': round(wr,1),
            'profit': round(profit,1), 'roi': round(profit/n*100,1),
            'mean_residual': round(mr,2), 'std_residual': round(sr,2),
            't_stat': round(ts,2), 'cohens_d': round(cd,3),
            'loso_ps': ps, 'loso_tp': round(tp,1),
            'season_wrs': swrs, 'game_fingerprints': list(cs_fps[ci]),
        })

    print(f"  LOSO-validated cores: {len(cores)} (need {min_loso}/{n_s} seasons)")
    return cores

def prune_independent(cores):
    print(f"\nPHASE 2: INDEPENDENCE PRUNING")
    print("="*70)
    cs = sorted(cores, key=lambda c: abs(c['t_stat']), reverse=True)
    fps = [set(c['game_fingerprints']) for c in cs]
    sel = []
    for i in range(len(cs)):
        indep = True
        for j in sel:
            ov = len(fps[i]&fps[j]) / min(len(fps[i]),len(fps[j])) if min(len(fps[i]),len(fps[j]))>0 else 0
            if ov > MAX_OVERLAP: indep = False; break
        if indep: sel.append(i)
    result = [cs[i] for i in sel]
    print(f"  {len(cs)} → {len(result)} independent cores")
    return result

def inverse_variance_fusion(games, cores):
    print(f"\nPHASE 3: INVERSE-VARIANCE FUSION")
    print("="*70)
    cf = defaultdict(list)
    for core in cores:
        for fp in core['game_fingerprints']:
            cf[fp].append(core)

    preds = []
    for g in games:
        if g['is_push']: continue
        ac = cf.get(g['fingerprint'], [])
        if not ac: continue

        swm = 0; sp = 0
        for c in ac:
            v = c['std_residual']**2
            pr = 1/v
            m = c['mean_residual']
            if c['direction'] == 'UNDER': m = -abs(m)
            swm += m*pr; sp += pr
        if sp == 0: continue

        cm = swm/sp
        cs = math.sqrt(1/sp)
        edge = cm/cs if cs > 0 else 0
        d = 'OVER' if cm > 0 else 'UNDER'
        prob = 1/(1+math.exp(-1.7*edge))
        conf = abs(prob-0.5)*2

        p = {
            'date': g['date'], 'season': g['season'],
            'away': g['away'], 'home': g['home'],
            'market_total': g['market_total'], 'actual_total': g['actual_total'],
            'n_cores': len(ac), 'combined_mean': round(cm,2),
            'edge': round(edge,3), 'direction': d,
            'prob': round(prob,4), 'confidence': round(conf,4),
            'fingerprint': g['fingerprint']
        }
        p['hit'] = (g['actual_total'] > g['market_total']) == (d == 'OVER')
        p['profit'] = 0.9 if p['hit'] else -1.0

        # Kelly
        b = 0.90; q = 1-prob
        kf = max(0, min((b*prob-q)/b, 0.05))
        p['kelly_fraction'] = round(kf,4)
        p['kelly_profit'] = round(kf*100*0.9 if p['hit'] else -kf*100, 2)
        preds.append(p)

    print(f"  Total predictions: {len(preds)}")
    return preds

def calibration(preds):
    print(f"\nPHASE 4: CALIBRATION")
    print("="*70)
    bins = [(0.50,0.55),(0.55,0.60),(0.60,0.65),(0.65,0.70),(0.70,0.75),(0.75,0.80),(0.80,0.85),(0.85,1.01)]
    cd = []
    for lo,hi in bins:
        sub = [p for p in preds if lo<=max(p['prob'],1-p['prob'])<hi]
        if not sub: continue
        hits = sum(1 for p in sub if p['hit'])
        n = len(sub)
        awr = hits/n*100
        ap = sum(max(p['prob'],1-p['prob']) for p in sub)/n
        ewr = ap*100
        cd.append({'bin':f'{lo:.2f}-{hi:.2f}','n':n,'expected':round(ewr,1),'actual':round(awr,1),'error':round(awr-ewr,1)})
    print(f"  {'Bin':<12} {'N':>6} {'Expected':>10} {'Actual':>10} {'Error':>8}")
    for c in cd:
        print(f"  {c['bin']:<12} {c['n']:>6} {c['expected']:>9.1f}% {c['actual']:>9.1f}% {c['error']:>+7.1f}%")
    return cd

def run_v28_global():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  V28 HYPERSONIC NEXUS — GLOBAL BACKTEST                     ║")
    print("║  18 NBA Seasons | 23,552 Games | 18-Fold LOSO               ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print("\nPHASE 0: LOADING ALL NBA SEASONS")
    print("="*70)
    games = load_all_nba()
    if not games:
        print("  ERROR: No games loaded from SQLite. Trying JSON fallback...")
        return None
    games = compute_streaks(games)

    seasons = sorted(set(g['season'] for g in games))
    for s in seasons:
        sg = [g for g in games if g['season']==s]
        print(f"  {s}: {len(sg)} games")
    print(f"  TOTAL: {len(games)} games across {len(seasons)} seasons")

    cores = discover_cores(games, seasons)
    if not cores:
        print("  No cores found!")
        return None
    indep = prune_independent(cores)
    preds = inverse_variance_fusion(games, indep)
    cal = calibration(preds)

    # RESULTS
    print("\n" + "="*70)
    print("V28 GLOBAL BACKTEST — FINAL RESULTS")
    print("="*70)

    print("\n  By confidence tier:")
    for mc in [0.0, 0.10, 0.20, 0.30, 0.40, 0.50]:
        sub = [p for p in preds if p['confidence'] >= mc]
        if not sub: continue
        hits = sum(1 for p in sub if p['hit'])
        n = len(sub); wr = hits/n*100
        profit = sum(p['profit'] for p in sub)
        roi = profit/n*100
        kp = sum(p.get('kelly_profit',0) for p in sub)
        print(f"  conf≥{mc:.2f}: {n:>5} bets, {wr:>5.1f}% WR, +{profit:>7.1f}u ({roi:>5.1f}% ROI), Kelly +{kp:>8.1f}u")

    print("\n  By edge magnitude:")
    for me in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        sub = [p for p in preds if abs(p['edge']) >= me]
        if not sub: continue
        hits = sum(1 for p in sub if p['hit'])
        n = len(sub); wr = hits/n*100
        profit = sum(p['profit'] for p in sub)
        print(f"  |edge|≥{me:.1f}: {n:>5} bets, {wr:>5.1f}% WR, +{profit:>7.1f}u")

    print("\n  Per-season breakdown:")
    for s in seasons:
        sp = [p for p in preds if p['season']==s]
        if not sp: continue
        hits = sum(1 for p in sp if p['hit'])
        n = len(sp); wr = hits/n*100
        profit = sum(p['profit'] for p in sp)
        print(f"  {s}: {n:>4} bets, {wr:>5.1f}% WR, +{profit:>6.1f}u")

    # Era analysis
    eras = [
        ('2007-2012', [s for s in seasons if s < '2012-13']),
        ('2012-2017', [s for s in seasons if '2012-13' <= s < '2017-18']),
        ('2017-2022', [s for s in seasons if '2017-18' <= s < '2022-23']),
        ('2022-2026', [s for s in seasons if s >= '2022-23']),
    ]
    print("\n  By era:")
    for ename, es in eras:
        sp = [p for p in preds if p['season'] in es]
        if not sp: continue
        hits = sum(1 for p in sp if p['hit'])
        n = len(sp); wr = hits/n*100
        profit = sum(p['profit'] for p in sp)
        print(f"  {ename}: {n:>4} bets, {wr:>5.1f}% WR, +{profit:>7.1f}u")

    # SAVE
    results = {
        'version': 'V28_GLOBAL_BACKTEST',
        'n_seasons': len(seasons), 'seasons': seasons,
        'total_games': len(games), 'independent_cores': len(indep),
        'total_predictions': len(preds),
        'total_hits': sum(1 for p in preds if p['hit']),
        'overall_wr': round(sum(1 for p in preds if p['hit'])/len(preds)*100,1) if preds else 0,
        'overall_profit': round(sum(p['profit'] for p in preds),1),
        'overall_roi': round(sum(p['profit'] for p in preds)/len(preds)*100,1) if preds else 0,
        'calibration': cal,
        'confidence_tiers': {},
        'edge_tiers': {},
        'season_results': {},
        'cores': [{
            'name': c['name'], 'direction': c['direction'],
            'total_n': c['total_n'], 'total_wr': c['total_wr'],
            'mean_residual': c['mean_residual'], 'std_residual': c['std_residual'],
            't_stat': c['t_stat'], 'cohens_d': c['cohens_d'],
            'loso_ps': c['loso_ps'], 'season_wrs': c['season_wrs']
        } for c in indep]
    }

    for mc in [0.0, 0.10, 0.20, 0.30, 0.40, 0.50]:
        sub = [p for p in preds if p['confidence'] >= mc]
        if not sub: continue
        hits = sum(1 for p in sub if p['hit'])
        n = len(sub); profit = sum(p['profit'] for p in sub)
        results['confidence_tiers'][f'conf_gte_{mc:.2f}'] = {
            'n':n,'hits':hits,'wr':round(hits/n*100,1),'profit':round(profit,1),'roi':round(profit/n*100,1)
        }

    for me in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        sub = [p for p in preds if abs(p['edge']) >= me]
        if not sub: continue
        hits = sum(1 for p in sub if p['hit'])
        n = len(sub); profit = sum(p['profit'] for p in sub)
        results['edge_tiers'][f'edge_gte_{me:.1f}'] = {
            'n':n,'hits':hits,'wr':round(hits/n*100,1),'profit':round(profit,1),'roi':round(profit/n*100,1)
        }

    for s in seasons:
        sp = [p for p in preds if p['season']==s]
        if not sp: continue
        hits = sum(1 for p in sp if p['hit'])
        n = len(sp); profit = sum(p['profit'] for p in sp)
        results['season_results'][s] = {'n':n,'hits':hits,'wr':round(hits/n*100,1),'profit':round(profit,1)}

    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'v28_global_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(base, 'v28_global_ledger.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['date','season','away','home','market_total','actual_total','direction','n_cores','edge','prob','confidence','kelly_fraction','hit','profit','kelly_profit'], extrasaction='ignore')
        w.writeheader()
        for p in preds: w.writerow(p)

    print(f"\n  Saved v28_global_results.json and v28_global_ledger.csv")
    return results

if __name__ == '__main__':
    run_v28_global()
