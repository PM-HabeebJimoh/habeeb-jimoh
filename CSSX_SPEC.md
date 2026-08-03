# CSS-X v1.0 — THE OBLIGATION LEDGER PROTOCOL

**Mandatory-Emission Absence Detection for Crypto Markets**

**Classification:** Open-Source Intelligence (OSINT) On-Chain Solvency System
**Capital Required:** $12 USD (domain only; compute local, data $0)
**Coverage:** L1 chains · L2 rollups · DeFi protocols · CEXs · stablecoins · listed tokens
**Data Cost:** $0 (public RPC, free API tiers, on-chain reads)
**Update Frequency:** Hourly for Tier 1–2, daily 06:00 UTC for Tier 3–4
**Data Latency:** 0–20 seconds (on-chain) to 24 hours (social/repo)

---

## 0. WHY THE CORPORATE MODEL DOES NOT TRANSFER UNCHANGED

CSS v10.0 works because a US corporation is a **compulsory emitter of paper**. It must file, register, notify, and renew — and the *absence* of paper is legally impossible for a living firm. That is the entire edge.

Crypto has no county recorder. Porting CSS v10.0 signal-for-signal produces a system that watches for liens on entities that do not legally exist, in jurisdictions that do not apply, on timescales (30–90 day lead) that are meaningless in a market that liquidates in eleven minutes.

But crypto has something strictly **better** than a courthouse: a public, adversarially-verified, second-by-second ledger of **mechanical obligations**. A rollup *must* post state roots. An oracle *must* post within its heartbeat. A solvent treasury *must* pay gas. A bridge's escrow *must* equal its wrapped supply. A staking set *must* attest.

These are not disclosures — they are *physics of the system*. They cannot be spun, delayed by counsel, or negotiated with. And critically: **each one has a specified cadence**, which means each one has a measurable absence.

CSS-X is CSS v10.0's negative-space thesis applied to a substrate where the negative space is machine-readable, free, and near-instant.

| | CSS v10.0 (corporate) | CSS-X v1.0 (crypto) |
|---|---|---|
| Substrate | Administrative paper | Cryptographic state |
| Sovereign claim | IRS lien | Chain halt / unilateral upgrade key |
| Credit abandonment | UCC-1 lapse | Market-maker depth withdrawal, LP flight |
| Redemption test | Involuntary petition | Reserve/liability gap, bridge backing gap |
| Mandatory absence | Missing 10-K, dead GitHub | Missing state root, stale oracle, silent treasury |
| Verification cost | FOIA, county fees, days | One `eth_call`, milliseconds, free |
| Lead time | 30–180 days | 6 hours – 90 days |
| Adversary | Slow, lawyered | Fast, anonymous, sometimes rugging tonight |

---

## 1. ARCHITECTURE

Four tiers, 23 signal layers, three convergence paths, four global modifiers.

```
TIER 1  CONSENSUS      Does the system still produce state?          L101–L105
TIER 2  LIQUIDITY      Can the claim still be converted at size?     L201–L206
TIER 3  OPERATIONAL    Do the humans behind it still function?       L301–L305
TIER 4  ABSENCE        Have mandatory emissions stopped?             L401–L407
```

---

## TIER 1 — CONSENSUS CLAIM (the lethal state)

### L101 · BLOCK PRODUCTION HALT / FINALITY STALL

**Measures:** seconds since last finalized block ÷ target block time.
**Source:** any public RPC (`eth_getBlockByNumber`), Beacon `/headers/finalized`. $0.

```
r = gap / target_block_time
s₁₀₁ = 0.90  if r ≥ 500      (halted)
       0.65  if r ≥ 100
       0.35  if r ≥ 20
×1.1 (cap 0.92) if no public incident acknowledgement
```

**Lead time:** 0–3 days. **Plain English:** *"The chain has stopped producing blocks and nobody has said why. Everything denominated on it is currently unsellable, whatever the price screen says."*

### L102 · VALIDATOR / STAKE EXODUS

**Measures:** 30d stake change, exit-queue depth, Nakamoto coefficient.
**Source:** beacon API, staking REST, validator-set snapshots. $0.

```
s₁₀₂ = 0.35 (Δstake ≤ −30%) or 0.20 (≤ −15%)
     + 0.20 (exit queue ≥ 15%) or 0.10 (≥ 5%)
     + 0.20 (Nakamoto ≤ 2)     or 0.10 (≤ 4)   → cap 0.70
```

**Lead time:** 7–60 days. **Plain English:** *"Security is a budget, and the budget is leaving. The chain is uninsured before it is dead."*

### L103 · UNILATERAL CONTROL / SEQUENCER SPOF

**Measures:** who can stop or rewrite the system, and whether the escape hatch works.
**Source:** L2Beat JSON, on-chain `owner()`/`admin()` slots, timelock `getMinDelay()`. $0.

```
base = {eoa 0.55, multisig 0.30, timelock 0.10, immutable 0.0}
+0.10 timelock < 24h · +0.15 escape hatch broken · +0.15 sequencer down ≥6h/24h → cap 0.75
```

**Plain English:** *"One key can take everything. This is the crypto lien — someone already holds seizure authority over your assets."*

### L104 · SECURITY BUDGET INVERSION

**Measures:** cost-to-attack ÷ value-secured. Below 5% the chain is economically insolvent while still producing blocks. `0.50 / 0.30 / 0.15`. **Lead:** 14–120 days.

### L105 · HOLDER ENTROPY COLLAPSE

**Measures:** Shannon entropy of holder distribution vs 90d baseline. A −30% entropy drop means the float is being reabsorbed — the precondition of an orderly exit. `0.30 / 0.15`. **Lead:** 14–90 days.

---

## TIER 2 — LIQUIDITY ABANDONMENT (the redemption collapse)

### L201 · EXIT LIQUIDITY RATIO

**Measures:** 2% order-book + AMM depth ÷ circulating market cap.
**Source:** CEX `/depth` endpoints, pool reserves via RPC. $0.

```
s₂₀₁ = 0.45 if r < 0.01%   ·  0.30 if r < 0.03%  ·  0.15 if r < 0.06%
+0.10 if depth −50% in 30d (market-maker withdrawal)
```

Liquid majors run 0.05–0.5%. **Plain English:** *"The price is not wrong — the depth is missing. There is no bid for your size and there will be a −90% candle when you find out."*

### L202 · LP FLIGHT (TVL net of price)
Token-denominated TVL change, so a protocol cannot hide withdrawals behind its own token pumping. `0.40 / 0.25 / 0.12`, +0.08 if one LP holds ≥40% of what remains.

### L203 · PEG / BASIS DISLOCATION
Persistent discount on one venue vs the external reference. `0.50 / 0.32 / 0.15`, +0.08 if the stable pool is ≥85% skewed to the weak leg. **Plain English:** *"A persistent single-venue discount is not an arbitrage failure. It is a withdrawal queue with a price attached."*

### L204 · RESERVE ASYMMETRY *(the FTX detector, generalised)*
Reserves ÷ liabilities, share of reserves denominated in the entity's **own token**, and attestation-window borrowing. Coverage <80% → 0.45; self-token ≥40% → +0.20; window dressing → +0.15. Cap 0.70.
**Plain English:** *"They are solvent only if the thing they printed is worth what they say. Circular collateral is not collateral."*

### L205 · BRIDGE RESERVE DRAIN
Origin escrow vs destination wrapped supply. Backing <90% → 0.55. **Lead:** 0–21 days. Every large bridge failure was visible as a backing gap hours before the announcement.

### L206 · LEVERAGE REFLEXIVITY
Self-collateral share, distance to the liquidation band, OI/mcap and funding. The Terra topology: collateral and liability share one price. Cap 0.55.

---

## TIER 3 — OPERATIONAL DISSOLUTION (the corpse)

### L301 · INSIDER EXIT FLOW *(the on-chain Form 4)*
Labelled team/treasury/investor wallets → exchange deposit addresses, sized against ADV. ≥5× ADV → 0.40; ≥3 coordinated wallets → +0.08.
**Plain English:** *"Insiders must file Form 4 in equities. Here they file a transaction — better disclosure, simply unread."*

### L302 · CORE REPOSITORY ABANDONMENT
90d commits, unique committers, days since release, open security issues. `0.35 / 0.22 / 0.15`. **Lead:** 60–180 days.

### L303 · GOVERNANCE QUORUM DEATH
Proposal cadence, quorum attainment, delegate count, forum silence. Cap 0.35.
**Plain English:** *"A DAO that cannot reach quorum cannot respond to an exploit. It is an unmanned aircraft."*

### L304 · REGULATORY ACTION & DELISTING CASCADE
Enforcement (`none/investigation/suit/ofac` → `0/0.10/0.30/0.60`), tier-1 delistings (≥2 in 30d → 0.35), fiat-rail loss (+0.15). Cap 0.80.

### L305 · INFRASTRUCTURE DECAY
Front-end status, public RPC uptime, domain expiry horizon, docs removal. Cap 0.30.
**Plain English:** *"The front-end 404s and the domain renews in twenty days. They have already decided."*

---

## TIER 4 — MANDATORY ABSENCE (the shadow layer, the innovation)

Every layer here measures **an obligation that stopped**, against **a cadence the system itself defined**.

### L401 · ORACLE HEARTBEAT ABSENCE
Staleness ÷ contracted heartbeat. ≥10× or ≥2 dead feeds → 0.35. **Lead:** 0–14 days.
*"Oracles are paid to post. When they stop, either the sponsor stopped funding the feed or someone froze it ahead of a liquidation."*

### L402 · STATE-ROOT / PROOF POSTING ABSENCE
Hours since last root ÷ documented cadence. ≥10× → 0.40. Flags stranded withdrawals.
*"A rollup that stops posting has stopped inheriting security. Withdrawals just became discretionary."*

### L403 · TREASURY GAS SILENCE
Days since the ops multisig last paid gas + runway + stable share. Cap 0.45.
*"Gas and payroll are the last things a living organisation stops paying. Ninety days of silence is a death certificate with a postmark."*

### L404 · ATTESTATION / AUDIT LAPSE
Days since PoR or audit ÷ **the entity's own promised cadence**, + auditor resignation, + transparency-page removal. Cap 0.45.
*"Breaking your own disclosure promise is the cheapest signal to emit and the most expensive one to fake."*

### L405 · ORGANIC USER FLOW EXTINCTION
Unique depositors vs 90d baseline; zero-inflow-with-outflow. Cap 0.40.
*"Nobody deposits, everybody withdraws. That is a silent bank run, whatever the chart says."*

### L406 · COMMUNICATION ENTROPY SPIKE
KL divergence of current comms vs 12-month baseline + reassurance-vocabulary density ("funds are safe", "temporary maintenance", "FUD"). `0.30 / 0.15`.
*"Specificity collapses before solvency does."*

### L407 · HOLDER CAPITULATION CLUSTERING *(constrained)*
Withdrawal-failure reports weighted by account age **and corroborated on-chain**. Never fires without a Tier-1/2 mechanical signal — rumour alone scores exactly zero, enforced in code and in tests.

---

## 2. CONVERGENCE ALGORITHMS

```python
PATH A — MECHANICAL   t1 ≥ 0.30 ∧ t2 ≥ 0.20 ∧ max(t3,t4) ≥ 0.20   → ceiling 0.97
PATH B — SHADOW       ≥3 independent Tier-4 absences               → ceiling 0.94
PATH C — HYBRID       1 hard mechanical ≥0.30 ∧ ≥2 absences        → ceiling 0.93
otherwise             SUB_CONVERGENCE, capped at 0.54 (WATCH)
```

### Combination is noisy-OR, not addition

Additive stacking (v10.0's `t1+t2+t3`) saturates instantly — three 0.4s become 1.2 — and destroys all ranking information exactly where the system must discriminate. CSS-X uses:

```
S = ceiling × (1 − Π(1 − sᵢ))
```

Every marginal signal stays informative; the score approaches but never reaches certainty. Path B additionally applies `0.85ⁱ` decay per additional absence, so the fourth absence matters less than the first.

### Four global modifiers

1. **PERSISTENCE** — the driving signal must survive its tier's dwell time (Tier 1: 3d, Tier 2: 4d, Tier 3: 7d, Tier 4: 10d). Unconfirmed signals are hard-capped at **0.74** — they can never enter CRITICAL or TERMINAL. Crypto dwell times are shorter than CSS v10.0's 14–21 days because settlement is faster.
2. **INDEPENDENCE** — signals are grouped into five correlation clusters (consensus, market-liquidity, reserve/redemption, organisational, narrative). Within a cluster only the strongest counts fully; the rest are damped ×0.55. One root cause observed five ways cannot manufacture a 0.9.
3. **CONTRADICTION** — live solvency evidence (verified raise, honoured large withdrawal, restored proofs, fresh attestation, announced migration) hard-caps the score at **0.60**. The system is required to be talked out of its conclusion by facts.
4. **COVERAGE** — every verdict reports what fraction of applicable layers were actually measured, and confidence scales with it. Unmeasured ≠ healthy; it is reported as unmeasured.

### Bands

| Score | Band | Action |
|---|---|---|
| ≥0.90 | **TERMINAL** | Failure in progress or imminent. Exit, do not average down. |
| ≥0.75 | **CRITICAL** | Multi-tier convergence. Reduce exposure; assume redemption risk. |
| ≥0.55 | **ELEVATED** | Structural deterioration confirmed by independent evidence. |
| ≥0.35 | **WATCH** | Early absences. Increase monitoring frequency. |
| <0.35 | **NOMINAL** | No convergent distress evidence. |

---

## 3. REPLAY RESULTS

`python -m cssx.cli replay` — four reconstructed distress archetypes vs three controls:

```
0.952  TERMINAL  stalled-rollup        [l2]         PATH_A_MECHANICAL   3 absences
0.906  TERMINAL  abandoned-defi        [defi]       PATH_A_MECHANICAL   5 absences
0.827  CRITICAL  reflexive-stablecoin  [stablecoin] PATH_A_MECHANICAL   4 absences
0.818  CRITICAL  cex-reserve-hole      [cex]        PATH_C_HYBRID       5 absences
0.163  NOMINAL   rescued-protocol      [defi]       SUB_CONVERGENCE  (contradiction cap)
0.000  NOMINAL   healthy-l1            [l1]         SUB_CONVERGENCE
0.000  NOMINAL   healthy-cex           [cex]        SUB_CONVERGENCE
```

Separation between the worst distress case and the best control is **0.65**.

`rescued-protocol` is the important row: it has real deterioration (−42% TVL, thin book) and would trip a naive screener, but a verified raise and an honoured large withdrawal cap it at NOMINAL. A system that cannot be argued out of an alert is not a detector, it is a fear generator.

**Honest limitation:** these fixtures encode what the collectors would plausibly have observed on the given dates, reconstructed from the public record. They validate the *scoring topology* — that each path fires where it should and stays silent where it should — not retroactive prediction. Genuine out-of-sample validation requires running the daily cron forward.

---

## 4. IMPLEMENTATION STACK ($12/yr)

| Component | Cost | Technology |
|---|---|---|
| Domain | $12/yr | any registrar (optional) |
| Compute | $0 | local Python 3.11, stdlib only — **zero dependencies** |
| Scheduling | $0 | GitHub Actions (2,000 min/month free) |
| Storage | $0 | SQLite (`entities`, `observations`, `signal_history`, `verdicts`) |
| Chain data | $0 | public RPC endpoints, `eth_call`/`eth_getBlockByNumber` |
| TVL / market | $0 | DefiLlama, CoinGecko free tiers |
| Repos | $0 | GitHub REST (60 req/h anon, 5,000 with free PAT) |
| Governance | $0 | Snapshot GraphQL, Tally, Discourse JSON |
| Explorers | $0 | Etherscan-family free keys, Blockscout |
| NLP | $0 | TF-IDF (stdlib) or local Llama-3 4-bit |

**Cadence:** Tier 1–2 hourly (they kill in hours), Tier 3–4 daily at 06:00 UTC. Alerts at ≥0.75.

---

## 5. WHAT THIS SYSTEM DELIBERATELY WILL NOT DO

* **It does not predict price.** It measures the probability that an obligation stops being met. Those correlate violently but are not the same claim, and conflating them is how these systems get people hurt.
* **It does not fire on rumour.** L407 is structurally incapable of scoring without mechanical corroboration.
* **It does not treat missing data as good news.** Coverage is reported on every verdict.
* **It does not name entities.** Fixtures are archetypes. Pointing a solvency accusation at a named, live protocol on reconstructed inputs is defamation risk and, more importantly, is how you become the cause of the run you claimed to predict.
* **It is not investment advice**, and its outputs are probabilistic evidence summaries, not conclusions about fraud or insolvency.
