# CSS-X v1.0

Crypto-market analogue of CSS v10.0. Detects distress as **mandatory-emission absence**: a rollup that stops posting state roots, an oracle past its heartbeat, a treasury that stops paying gas, a bridge whose escrow no longer matches its wrapped supply.

Full methodology: [`../CSSX_SPEC.md`](../CSSX_SPEC.md)

## Quick start

Zero dependencies. Python 3.11+, stdlib only.

```bash
python -m cssx.cli replay                 # score built-in archetypes vs controls
python -m cssx.cli layers                 # list all 23 signal layers
python -m cssx.cli score examples/observation.example.json \
    --history '{"302":30,"403":30,"404":30,"401":12}'
python -m cssx.cli run --demo --db cssx.db --alert-threshold 0.75
python -m cssx.cli backtest --threshold 0.65 --sweep --sources
python -m unittest discover -s tests -v
```

Backtest results and methodology: [`../BACKTEST_2026_07.md`](../BACKTEST_2026_07.md)

## Library use

```python
from cssx import Observation, AssetClass, score_entity

o = Observation("some-rollup", AssetClass.L2, facts={
    "hours_since_state_root": 96, "expected_root_cadence_h": 6,
    "bridge_escrow_usd": 210e6, "wrapped_supply_usd": 260e6,
    "seconds_since_final_block": 9000, "target_block_time_s": 2,
})
v = score_entity(o, persistence_history={101: 5, 205: 5, 402: 5})
print(v.score, v.band, v.path, v.narrative)
```

## Layout

| File | Role |
|---|---|
| `core.py` | Observation / SignalScore primitives, entropy & Nakamoto helpers |
| `signals/tier1_consensus.py` | L101–L105 — does the system still produce state |
| `signals/tier2_liquidity.py` | L201–L206 — can the claim still be converted |
| `signals/tier3_operational.py` | L301–L305 — do the humans still function |
| `signals/tier4_absence.py` | L401–L407 — have mandatory emissions stopped |
| `convergence.py` | 3 paths, noisy-OR combination, persistence / independence / contradiction / coverage |
| `collectors.py` | Free-tier collectors: RPC, DefiLlama, CoinGecko, GitHub, Chainlink, explorers |
| `store.py` | SQLite persistence and consecutive-day streak computation |
| `fixtures.py` | Distress archetypes + healthy controls for replay |
| `panel_2026_07.py` | July 2026 backtest panel with per-entity sourcing |
| `backtest.py` | Walk-forward harness: confusion matrix, lead time, alert burden, sweep |
| `cli.py` | `replay` / `score` / `layers` / `run` / `backtest` |

## Design rules enforced in code and tests

- Unmeasured signals score **0** and lower confidence — never imputed.
- Unconfirmed signals are capped at **0.74** (cannot reach CRITICAL).
- Correlated signals are damped ×0.55 within their cluster.
- Live solvency evidence caps any score at **0.60**.
- Social/rumour signals **cannot fire alone** — hard-tested.
- Not price prediction, not investment advice, no named live entities.
