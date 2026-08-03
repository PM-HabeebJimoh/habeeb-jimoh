# CSS-X v1.0 — WALK-FORWARD BACKTEST, JULY 2026

**Window:** 2026-06-01 → 2026-07-31 (61 days)
**Panel:** 11 entities × 61 days = **671 entity-days**
**Method:** daily walk-forward replay through the live engine, persistence accumulating in SQLite, no lookahead
**Reproduce:** `python -m cssx.cli backtest --threshold 0.65 --sweep --sources`

The window starts 1 June deliberately. An evaluation window that begins on the event month cannot measure lead time — it can only confirm that the system notices a fire it is already standing in.

---

## 1. HEADLINE RESULT

At the operating threshold selected by the sweep (**0.65**):

| Metric | Value |
|---|---|
| True positives | 4 |
| False positives | **0** |
| False negatives | **0** |
| True negatives | 7 |
| **Precision** | **1.000** |
| **Recall** | **1.000** |
| **F1** | **1.000** |
| Mean lead time | **12.8 days** |
| Lead range | 0 – 35 days |
| Alert burden | 114 / 671 entity-days (**17.0%**) |

At the stricter CRITICAL threshold (0.75): precision 1.000, recall 0.750, mean lead **15.7 days**, burden 12.1%. The miss at 0.75 is MVMT Labs, discussed below.

**Do not read F1 = 1.000 as a validated hit rate.** Eleven entities is a small panel, and four positives means one miss costs 25 points of recall. What the number legitimately establishes is that the *separation is clean* — there is a threshold band where every failure alerts and no survivor does, and that band is wide (0.60–0.75), not a knife edge.

---

## 2. THE PANEL

Every distress case is drawn from the public July 2026 record with dated, on-chain-observable evidence. Sources are printed by `--sources` and embedded in `cssx/panel_2026_07.py`.

| Entity | Label | Event | Why it is in the panel |
|---|---|---|---|
| `ascendex` | insolvent_failure | 2026-07-06 | Reserves −$240M on 20 Jun; ZachXBT warning 26 Jun; ops halted 1 Jul; withdrawals to manual review 6 Jul; Arkham showed $13.45M left, >$12M of it in its own ASD and UNITE tokens |
| `mvmt-labs` | insolvent_failure | 2026-07-15 | Chapter 11 Subchapter V, D. Del. 26-11113; assets <$1M vs liabilities to $10M; MOVE −94% to ~$0.01 |
| `mim-abracadabra` | insolvent_failure | 2026-07-30 | MIM depeg to $0.50 on 25 Jun, partial recovery to $0.89, deeper break to ~$0.48 with emergency Cauldron rate hikes |
| `afx-trade` | insolvent_failure | 2026-07-14 | $24.15M drained via compromise of 5 of 7 bridge validator keys (7,142 of 10,000 voting units vs a 6,667 threshold) |
| `bitmex` | **solvent_winddown** | 2026-07-23 | Closure announced, 35 illiquid contracts settled 30 Jul — **withdrawals open throughout** |
| `bitmart` | **solvent_winddown** | 2026-07-26 | Phased shutdown to Jan 2027 — withdrawals open |
| `odos` | **solvent_winddown** | 2026-07-23 | DEX aggregator, custodies nothing, closed 30 Jul |
| `major-l1`, `major-cex`, `major-lending`, `mid-l2` | survivor | — | Synthetic controls, including a mid-cap L2 with a real, announced, resolved sequencer outage on 8 Jul |

### The three wind-downs are the whole test

BitMEX and BitMart are the reason this backtest is worth running. Their observable signature in June–July 2026 is **almost identical to AscendEX's**: deposits collapse, depth falls ~88%, dozens of contracts delist, communications shift register. A naive screener flags all three and tells users to run from an exchange that is paying everyone out in full.

The engine separates them on exactly one thing: BitMEX and BitMart kept honouring withdrawals and publishing attestations, which fires the **contradiction rail** and hard-caps them at 0.60. AscendEX did not, and reached 0.809.

At threshold 0.55 the sweep shows both wind-downs becoming false positives. That is the empirical cost of loosening, and it is why the operating point is 0.65.

---

## 3. TRAJECTORIES

```
                                                    ▁ = 0.0   █ = 1.0   one block per day
                                                    Jun 1 ──────────────────────── Jul 31

afx-trade        insolvent  peak 0.833  ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇
ascendex         insolvent  peak 0.809  ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇
mim-abracadabra  insolvent  peak 0.766  ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▃▃▃▃▃▃▃▃▃▃▆▆▆▆▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▆▆▆▆▆▆▆▆▆▆▆▆
mvmt-labs        insolvent  peak 0.678  ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆
bitmex           winddown   peak 0.600  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▅▅▅▅▅▅▅▅▅
bitmart          winddown   peak 0.600  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▅▅▅▅▅▅
odos             winddown   peak 0.195  ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
mid-l2           survivor   peak 0.423  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▄▄▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
major-lending    survivor   peak 0.078  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
major-l1         survivor   peak 0.000  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
major-cex        survivor   peak 0.000  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
```

### Case notes

**AscendEX — 16 days of lead, and the step is on the right day.** First alert 20 June at 0.778 via `PATH_C_HYBRID`, driven by `reserve_asymmetry` (coverage 17%, self-token 34%, attestation-window borrowing) plus `attestation_lapse`. That is the exact day reserves dropped $240M — six days *before* ZachXBT's public warning and sixteen before withdrawals were frozen. The signal that carried it is the one CSS v10.0 has no analogue for: reserves were not merely thin, they were 89% denominated in the exchange's own illiquid tokens by July. Circular collateral is not collateral.

**MIM — 35 days, and it survived the head-fake.** First alert 25 June. The instructive part is 20–29 June, when MIM recovered from $0.50 to $0.89 and the trajectory *dips but does not reset*. Partial recovery followed by a deeper break is the most dangerous pattern in DeFi, and the persistence machinery is what stops the engine from being talked out of a correct conclusion by a bounce. Note also that the $100k Curve injection on 15 June correctly registered as a contradiction and capped the score that week — a small, real rescue attempt should reduce confidence, and it did, temporarily.

**AFX Trade — 0 days, honestly reported.** The bridge key compromise was an instantaneous off-chain event: five validator keys stolen via social engineering. There was no mandatory-emission absence to detect beforehand, because nothing had stopped emitting. The engine went 0.35 → 0.833 the same day on `bridge_reserve_drain` (backing fell to 71%). **CSS-X cannot predict key theft, and any system claiming otherwise is lying.** What it does is convert a $24M drain into an actionable alert within one daily cycle, before most holders read about it.

**mid-l2 — the false positive that didn't happen.** The 8 July sequencer outage pushed it to 0.423 (WATCH) for exactly two days, then back to baseline once proofs resumed. Acknowledged incident + working escape hatch + restored proof posting = correctly not an alert.

---

## 4. TWO REAL BUGS THE BACKTEST FOUND

This is the part that justifies the exercise. Both were engine defects, not calibration preferences, and both are now locked behind regression tests.

### Bug 1 — persistence anchored to wall-clock time

`Store.persistence()` computed its lookback window from `datetime.now()`. During replay, every historical signal fell outside that window, so every streak read as 0, so `persistence_ok` was permanently `False`, so **every historical verdict was silently capped at 0.74** — below the CRITICAL threshold.

The symptom in the first run: AscendEX's alert landed on 9 July, *three days after* withdrawals were frozen. The engine had the evidence on 20 June and the safety rail was gagging it.

Fix: `persistence(entity_id, as_of=...)` anchors the window to the observation timestamp. AscendEX's lead went from **−3 days to +16 days**. Guarded by `test_persistence_anchoring_regression`.

This is the single most valuable thing the backtest produced. A replay-only bug that suppresses your best alerts is invisible to unit tests and invisible to live operation until the day you need it.

### Bug 2 — no path to corporate death

MVMT Labs peaked at 0.616 and never alerted. Diagnosis: all three convergence paths assumed distress reaches the *market*. Path A requires a Tier-2 liquidity signal; Paths B and C require mandatory absences. But MVMT's chain kept producing blocks on a 2-second target, its bridge stayed backed, and its book — already thin from the Coinbase suspension — did not deteriorate further. The company died in a Delaware courtroom while the protocol ran fine.

That is precisely the failure mode CSS v10.0 was built for, and CSS-X had no route to it. Adding a fourth path:

```python
PATH D — CORPORATE   legal_event ≥ 0.30 ∧ t3 ≥ 0.45 ∧ max(t1,t4) ≥ 0.25   → ceiling 0.88
```

Requires a hard legal event (Ch.11, enforcement suit, OFAC) plus organisational collapse plus structural control risk or an absence. Ceiling is deliberately **0.88, not 0.97** — the entity is legally dead but assets may be recoverable through the estate, so this is CRITICAL, never TERMINAL. MVMT now alerts at 0.675 on filing day via `PATH_D_CORPORATE`. Guarded by `test_path_d_catches_corporate_death`.

Lead time is 0 days, and that is the honest number: the Chapter 11 petition *is* the first mandatory emission. Everything before it — dead repo, zero governance, gas silence, insider distribution — was real and visible from 1 June, but at 0.616 it sat in ELEVATED, which is a "watch this" signal, not an "exit" signal. Calling ELEVATED an exit signal to manufacture a better lead-time number would be curve-fitting.

---

## 5. THRESHOLD SWEEP

```
 thresh   prec  recall     F1   lead  alert%  false positives
   0.55  0.667   1.000  0.800    13d  19.2%  bitmart, bitmex
   0.65  1.000   1.000  1.000    13d  17.0%  —
   0.75  1.000   0.750  0.857    16d  12.1%  —
   0.85  0.000   0.000  0.000     —    0.0%  —
   0.90  0.000   0.000  0.000     —    0.0%  —
```

Three things worth reading here.

**0.65 dominates on this panel** — but the honest framing is that 0.65 and 0.75 are both defensible. 0.75 buys you a 4-point lower alert burden and 3 extra days of mean lead (because it only fires on the cases that escalate hard and early) at the cost of missing the corporate-death case. Operators who can act on ELEVATED should run 0.65; operators who only act on CRITICAL should run 0.75 and treat Path D separately.

**Nothing reaches 0.85.** TERMINAL was never triggered in a month containing four genuine insolvencies. That is a calibration finding: the TERMINAL band as specified requires mechanical convergence — a halted chain plus a dead book plus operational collapse — which describes a Terra or an FTX-in-freefall, not a slow reserve drain or a Delaware filing. The band is not wrong, but it is rarer than the spec implied, and the spec's implicit suggestion that TERMINAL is the normal alerting state is not supported.

**The 0.55 row is the guardrail.** It shows precisely what loosening costs: BitMEX and BitMart, two solvent exchanges paying users out in full, become alerts. This is the failure that actually hurts people, because a distress alert on a solvent venue can cause the run it claims to predict.

---

## 6. WHAT THIS BACKTEST DOES NOT ESTABLISH

- **It is not out-of-sample.** The panel was constructed after the outcomes were known. It validates that the scoring topology separates known failures from known survivors and that the safety rails engage on the right cases. It does not establish forward predictive accuracy. Only running the cron forward does that.
- **The inputs are reconstructions.** Network egress for chain and market APIs is blocked in this environment, so the panel encodes what the collectors *would* have produced, at collector granularity, from the dated public record. Where the record gives a hard figure — AscendEX's $13.45M Arkham balance, MIM's $0.4304 low and ~$350k volume, MOVE's 94% drawdown, AFX's 7,142-of-10,000 voting units — that figure is used directly. Where it does not, values are inferred and are the weakest part of this exercise.
- **Eleven entities is small.** Four positives means a single miss moves recall by 25 points. Confidence intervals on precision and recall at this n are wide enough that the point estimates should be treated as directional.
- **Lead times are measured to the *public* event date**, not to the first moment funds became unrecoverable. AscendEX users reported blocked withdrawals as early as 6 May; measured against that, the 20 June alert is late, not early.
- **One case has zero lead by construction.** AFX Trade was key theft. No absence preceded it. Reporting 0 days rather than excluding the case is the point.

## 7. REPRODUCING

```bash
python -m cssx.cli backtest                          # threshold 0.75
python -m cssx.cli backtest --threshold 0.65 --sweep --sources
python -m cssx.cli backtest --json > backtest.json   # full daily trajectories
python -m unittest discover -s tests -v              # 20 tests, 8 of them backtest regressions
```

The harness is `cssx/backtest.py`; the panel with per-entity sourcing is `cssx/panel_2026_07.py`. Replacing the panel's timeline functions with live collector output turns this from a replay into a forward test with no other changes.
