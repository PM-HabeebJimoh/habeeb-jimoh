# ABAKE USE Engine — Enterprise Basketball Analytics

**Dynamic Pacing & Possession Scaling Engine**

A production-grade basketball game analysis system that treats basketball games as fluid possession windows, contracting or expanding based on coaching styles, fatigue, and point spreads. The engine implements the complete ABAKE USE mathematical framework with all 4 layers and operational filter rules.

## 🏗️ Architecture

```
abake_use_engine/
├── core/
│   ├── engine.py          # ABAKE USE Engine — Core mathematical framework
│   └── __init__.py
├── data/
│   ├── services.py        # Data fetching (ESPN API, Basketball-Reference)
│   ├── analytics.py       # Team stats database & derived analytics
│   └── __init__.py
├── templates/
│   └── index.html         # Web dashboard
├── static/
│   ├── css/
│   └── js/
├── app.py                 # Flask web application
└── __init__.py
tests/
└── test_engine.py         # 33 comprehensive tests
run_engine.py              # CLI runner
requirements.txt
setup.py
```

## 📐 Mathematical Framework

### Layer 1: Independent Line Generation (Linear Predictors)

```
P = Away Pace + Home Pace - League Baseline Pace
S_A = (Away ORtg × Home DRtg / League Eff) × (P / 100)
S_H = (Home ORtg × Away DRtg / League Eff) × (P / 100) + 2.5
Model Total = S_A + S_H
Model Spread = S_H - S_A
```

### Layer 2: Implied Team Distribution (The Split)

```
Base Line = (Total / 2) - (Spread / 2)
```

### Layer 3: Dynamic Scaling Cushions (Pacing Buffers)

```
Scaled_OVER = Base Line - (0.45 × Spread)    # Underdog OVER target
Scaled_UNDER = Base Line + (0.40 × Spread)   # Underdog UNDER target
```

### Operational Filter Rules

- **Rule 1**: Upset Clause — If UNDER and win_prob > 15%, SKIP
- **Rule 2**: Chaos Exemption — Skip high-variance matches or missing data
- **Rule 3**: Over Execution — OVER pick → underdog OVER bet against scaled line
- **Rule 4**: Under Execution — UNDER pick → underdog UNDER bet against scaled line

### League Constants

| League | Baseline Pace | Baseline Efficiency |
|--------|--------------|-------------------|
| WNBA | 80.2 | 102.5 |
| NBA Summer League | 84.5 | 98.2 |

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the engine (CLI)
python run_engine.py

# Start the web application
python -m abake_use_engine.app

# Run tests
python -m pytest tests/ -v
```

## 🌐 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Web dashboard |
| `GET /api/engine/status` | Engine status & configuration |
| `GET /api/today/games` | Today's games across all leagues |
| `GET /api/today/process` | Process today's games through ABAKE USE |
| `GET /api/today/summary` | Today's summary statistics |
| `GET /api/verify/profiles` | Run 3 verification profiles |
| `POST /api/process` | Process custom matchups |

## ✅ Verification

All 3 specification profiles pass:

| Profile | Matchup | Expected | Result |
|---------|---------|----------|--------|
| 1 | CHI vs LV | HIT | ✅ HIT |
| 2 | IND vs CON | HIT | ✅ HIT |
| 3 | ATL vs SEA | SYSTEM SKIP | ✅ SYSTEM SKIP |

## 🧪 Testing

33 comprehensive tests covering:
- Layer 1: Independent Line Generation (7 tests)
- Layer 2: Implied Team Distribution (2 tests)
- Layer 3: Dynamic Scaling Cushions (4 tests)
- Operational Filter Rules (7 tests)
- Execution Profiles (3 tests)
- Batch Processing (1 test)
- Edge Cases (9 tests)

## 📊 Today's Games (August 2, 2026)

| # | Matchup | Status | Pick | Total | Spread | Scaled Line |
|---|---------|--------|------|-------|--------|-------------|
| 1 | LV vs CHI | ✅ HIT | UNDER | 183.5 | 6.5 | 91.10 |
| 2 | NYL vs PHX | ⚠️ SKIP | UNDER | 177.5 | 2.5 | — |
| 3 | IND vs MIN | ⏳ PENDING | UNDER | 193.5 | 5.5 | 96.20 |
| 4 | LAS vs POR | ⚠️ SKIP | UNDER | 185.5 | 1.5 | — |
| 5 | CON vs DAL | ⏳ PENDING | UNDER | 172.5 | 11.5 | 85.10 |
| 6 | TOR vs GS | ⏳ PENDING | OVER | 164.5 | 12.5 | 70.38 |
