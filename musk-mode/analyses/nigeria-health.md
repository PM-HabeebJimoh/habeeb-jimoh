# Nigeria health — Musk mode, v2

Date: 2026-11-13 · Replaces v1 (a consultant-style market-entry scan that shrank "replace the industry" into "survey 20 pharmacies". That is the **cowardice** failure the protocol names.)

## Recommendation
**Don't build hospitals or clinics. Delete them from the critical path.** The goal is a **10× cut in the deaths that cost almost nothing to prevent**. Get there by turning the ~200,000 drug shops that already exist into certified test-and-treat nodes. Own the whole stack: medicine → kit → training → node → remote doctor → payment → data. Run it in a ladder: malaria first, then hypertension, then mothers.

## Gate 0

### The physics ceiling
A health system's output is **years of life**. Nigeria's life expectancy is **54.5 years** (World Bank, 2023), among the lowest in the world. The ceiling is not "a bit better than Ghana". It is the death rates middle-income countries already reach with the same molecules.

| Death type | Now | 10× target | Source |
|---|---|---|---|
| Malaria | ~31% of global deaths; 39% of global under-5 malaria deaths | ÷10 | WHO World Malaria Report 2024 (2023 data), via Guardian/ICIR · T2 |
| Maternal | 993–1,047 per 100k births; ~82,000 deaths = **28.5% of global maternal deaths** (2020) | < 100 per 100k | WHO/UN MMEIG via Africa Check · T2 |
| Under-5 | 102 per 1,000 (MICS 2021) | ~10 per 1,000 | MICS 2021 · T1 (via secondary) |

### Floor vs reality
- One full malaria cure (artemether-lumefantrine) costs **$0.22–0.57** per course (Global Fund pooled-procurement reference price, Q2 2024 · T1).
- Nigeria still carries ~31% of the world's malaria deaths. **ESTIMATE ≈ 185,000 a year**: 31% × ~597k global deaths, where the 597k is my memory of WMR 2024 (T4, so verify).
- **The idiot index here is on the outcome, not a part.** A death that a sub-$1 molecule prevents still happens. The molecule is not the cost. Diagnosis, delivery, quality and permission are, and all four are solvable without new science.
- **ESTIMATE floor per cured malaria episode** = rapid test (~$0.30–0.50, no reference price found) + drug course ($0.22–0.57) + ~10 minutes of node labour + logistics ≈ **$1–2**. Verification path: Global Fund rapid-test reference table, plus a shelf-price walk.

### Classification
| Layer | Type | Weapon |
|---|---|---|
| Molecules | 3, **already solved globally** | Buy direct from WHO-prequalified makers; delete the middlemen |
| Diagnosis at 200k nodes by non-doctors | **2 (capability)**: one protocol, one rapid test, decision support at scale; not proven at this size | Prototype in 50 nodes, fail cheap, measure |
| Legal right for a drug shop (PPMV) to test and treat | **4 (permission)**, the binding constraint | Certification strategy with named regulators, plus private safety data. **No cost weapon.** |
| Doctors | Staffing: 2.9–3.9 per 10k, ~4,000 leaving a year | Delete doctors from protocol cases; keep them for referral and remote oversight |

**Lesson from FSD and Vegas:** this is a Type 2+4 problem. Making drugs cheaper (a Type 3 weapon) alone would repeat the robotaxi mistake.

### Stated odds
- National 10× in 10 years: **5–10%** (my judgement, ESTIMATE).
- Rung 1, malaria test-and-treat at 50 nodes in one state: **~50%**.
- Worth it because the failure value is bounded (see below) and success means roughly 100k+ lives a year (ESTIMATE).

### Failure value
- A failed rung costs capital: bounded.
- A patient harmed by bad stock or a missed danger sign → regulators shut the network down and trust dies. That **destroys the ability to try again.** Rule: human-rated. **Prove it privately before scaling**: test every batch, refer every danger sign, publish the safety data.

### Three-failure test
If the mission is "Nigerians live to 70", it survives three public failures. If it is "a pharmacy business", it doesn't. Pick the mission, or don't start.

### Schedule
- Rung 1 at 50% probability: 6 months. Slip case: 9–18 months.
- National at 50% probability: 10 years. Slip case: 15–30 years.
- The plan survives the slip **only if every rung pays for itself.** Hence the ladder.

## The Algorithm on the health system

### 1. Requirements, with owners
| Requirement | Owner | Verdict |
|---|---|---|
| Malaria diagnosis needs a doctor | MDCN scope of practice. WHO already endorses community test-and-treat (iCCM) | **Delete** for uncomplicated, test-positive cases |
| Care happens in a facility | Nobody. 20–40% of ~34k public health centres function; people already go to drug shops first (up to 55% of under-5 illnesses) | **Delete** |
| The patient travels to care | Nobody | **Delete**: care sits within walking distance |
| Drugs pass through open markets and 4–6 hands | Nobody | **Delete**: maker → kit → node |
| Insurance must pay | ~10% enrolled | **Delete** as a prerequisite |
| Build new clinics | Nobody | **Delete**: about 200k nodes already exist |
| Drug shops can't test or treat | PCN (Registrar: name to verify) | **Renegotiate.** This is the Type 4 gate. PCN has reportedly piloted tiered drug-shop accreditation (T4 memory, verify) |
| Drugs must be NAFDAC-registered | NAFDAC (DG Prof. Mojisola Adeyeye) | **Keep**: safety |
| Danger signs go to a doctor | Clinical safety | **Keep** |

### 2. Delete
Hospital visits for protocol cases · new buildings · a doctor in the loop for protocol cases · the open-market chain · paper records · insurance as a gate · app-first.
Expected add-back (~10%): a remote doctor line for edge cases.

### 3. Simplify
- 1 kit, 1 price, 1 one-page protocol per condition.
- Start with the killers: malaria → childhood pneumonia/diarrhoea → hypertension → maternal danger signs.

### 4. Accelerate (bottleneck only)
- Line rate = **certified nodes per week**.
- Certify by observed competence (exam + 20 supervised cases), not years of schooling.

### 5. Automate last
Clinical decision support and AI triage on the phone come only after paper protocols hold safety at 50 nodes.

## The stack (Starlink logic: own the vertical, reuse it)
Molecules (direct from WHO-PQ makers) → kit → training/certification factory → node (shop owner keeps the shop, we own the standard) → rapid test → remote doctor → mobile-money payment → outcome data → procurement volume → lower molecule cost.

**Kill shot:** "Our price for a *cured* malaria episode is below the shelf price of the drug alone in the open market." Being cheaper isn't enough; you need to be able to prove that claim on demand.

## Ladder (master plan)
1. Malaria test-and-treat at certified nodes. Kit margin pays.
2. Use that to fund a monthly hypertension/diabetes subscription (recurring revenue, prevents strokes).
3. Use that to fund maternal care: antenatal visits, danger-sign referral, transport.
4. Use the volume to vertically integrate procurement, then local packaging and manufacturing of the top SKUs.
5. Use all of it to fund high-volume surgical "factory" hospitals (analogy hypothesis only, untested).

## Plan
1. **Go to the floor (week 1).** Owner: Habeeb. In one area, sit in 10 drug shops and time 10 fever visits end to end. Record what is sold, at what price, whether there is a test, and the NAFDAC number.
2. **Permission map (weeks 1–3).** Owner: Habeeb. Get the PCN drug-shop accreditation rules and the Kaduna/Kano task-shifting policy text. Request meetings with the PCN Registrar and the state Primary Health Care Board.
3. **Kit cost (weeks 2–4).** Owner: Habeeb + one licensed importer. Quote for rapid tests + ACT from WHO-prequalified makers, landed in naira.
4. **50-node prototype (6 months; slip 9–18).** Owner: clinical lead (hire) + Habeeb. Paper protocol, batch-tested stock, referral line, safety data collected privately.
5. **Take the data to the regulator.** Owner: Habeeb. Go from state approval to national. Only then build software and scale the certification factory.

## Bottleneck
The Type 4 gate: **the legal right for a certified drug shop to test and treat.** Everything else is cheap.

## Metric
**% of fevers in node catchments tested and correctly treated within 24 hours**, plus cost per cured episode. Later, under-5 mortality in the catchment.

## Next physical action this week
Sit in 10 drug shops and time 10 fever visits end to end.

---

# v3 addendum: the full replacement and the profit (2026-11-13)

## The full replacement: 8 layers on one network
| # | Layer | What it replaces | Profit mechanism |
|---|---|---|---|
| 1 | Certified test-and-treat nodes | Non-functional health centres, uncertified drug shops | Episode margin + chronic subscriptions + franchise fee |
| 2 | Procurement + wholesale | Open markets, 4–6 middlemen (up to 100% markup on FOB, T3) | Wholesale margin on the ~$1.8–2.0B drug market |
| 3 | Payer | Out-of-pocket chaos; 10% insured | Health plans priced on our own outcome data; NHIA capitation; donor pay-per-verified-cure |
| 4 | Diagnostics hubs | Fragmented labs | Referral volume from nodes |
| 5 | Focused-factory hospitals (C-section, cataract, hernia) | General hospitals | Guaranteed referral volume → high utilisation |
| 6 | Manufacturing (pack, then make top-20 SKUs) | 60–70% imported medicines | Idiot-index capture; naira-denominated cost kills FX risk |
| 7 | Training/certification factory | 6-year pipeline for protocol tasks | Certified workers for us and others |
| 8 | Replication across West Africa | — | Copy the whole factory (Gigafactory logic) |

## Unit economics (model: `nigeria-health-model.py`; every input ESTIMATE unless sourced)
- FX: ₦1,347/$ (CBN official, 6 Nov 2026).
- Per node per month at maturity: patients spend **$353**; our gross margin is **$122**; the shop owner nets **$100**.
- Margin mix: **hypertension subscription $61 (50%)** · malaria $29 (24%) · diabetes $15 · acute $9 · fee $7.
- **Malaria is the door. Chronic care is the profit.** That is Falcon 9 → Starlink: the low-margin product builds the network, the recurring product pays for it.

| Scale | Gross margin/yr | Opex/yr | EBITDA/yr | Capex |
|---|---|---|---|---|
| 50 nodes (pilot) | $0.1M | $0.3M | **−$0.2M** | $0.03M |
| 5,000 nodes | $7.3M | $4.3M | **$3.0M** | $3M |
| 50,000 nodes | $73M | $31M | **$42M** | $30M |

- Contribution per node ≈ $100/month; node payback ≈ **6 months**. Breakeven ≈ 250–2,500 nodes, depending on HQ cost.
- 50k nodes = 36M malaria episodes/yr (vs 66.7–68M cases, WMR 2024) and 2.0M hypertension subscribers (vs 27.5M hypertensive, 12% treated, 2.8% controlled; Adeloye 2021).

### Full stack at year ~10 (ESTIMATE ranges)
| Layer | EBITDA/yr |
|---|---|
| 1 Nodes | ~$40M |
| 2 Wholesale (10% of a $1.8–2.0B market, 15% GM, 5% opex) | ~$18–20M |
| 3 Payer + donor pay-per-cure | ~$10–30M |
| 4–5 Diagnostics + hospitals | ~$10–80M |
| **Total** | **~$80–170M** |

- Ceiling reference: total health expenditure ₦10.42T in 2024 (NHA) ≈ **$7.0B** at a ~₦1,480/$ 2024 average (ESTIMATE conversion); out-of-pocket 58.3% ≈ $4.1B.
- Capital to year ~7 (ESTIMATE): ~$75–100M = $30M node capex + $10–20M pre-breakeven losses + ~$33M wholesale inventory + first hospitals.

### Where the profit dies
1. **FX:** costs are in $, revenue in ₦. A 30% naira fall cuts malaria margin from $0.49 to ~$0.14 per episode. Fix: index prices; layer 6 (local manufacturing) is the structural fix.
2. **Volume per node:** halve hypertension subscribers and gross margin falls 25%.
3. **Price:** every price is a guess until the shop walk. If today's shelf price is lower than assumed, the kill shot weakens.
4. **Permission:** without accreditation the nodes are illegal. Revenue = 0.

---

# v4: Buffett lens (2026-11-14) — model: `nigeria-health-buffett.py`

**Verdict:** Buffett would not invest today. The plan scores 1 of 6 on Berkshire's acquisition criteria. My own model also has **no margin of safety**: any single shock makes the network loss-making at scale. Fix: redesign the economics, prune 8 layers to 3, run the pilot as cheap information, then grow only from internal cash.

## Berkshire acquisition criteria (Berkshire annual report / 8-K filings)
| Criterion | Plan | Pass? |
|---|---|---|
| ≥ $75M pre-tax earnings | Projected only | ✗ |
| Demonstrated consistent earning power ("future projections are of no interest") | None | ✗ |
| Good ROE with little or no debt | 48% after-tax ROIC, but projected | ✗ (unproven) |
| Management in place | Not yet | ✗ |
| Simple business | Shops selling tests and pills | ✓ |
| Offering price | n/a | — |

## Margin of safety (owner earnings = after 30% tax, after maintenance capex)
| Case | Contribution/node/mo | Owner earnings @ 50k nodes |
|---|---|---|
| Base | $90 | $25M/yr (not the $42M EBITDA quoted in v3) |
| Volume −50% | $33 | $1M |
| Naira −30% | $15 | −$9M |
| Price −20% | $20 | −$6M |
| COGS +20% | $64 | $14M |
| All four | −$44 | −$44M |

**Cause:** the shop owner's cut is fixed in naira and our margin is the thin residual after dollar costs. **Redesign:** shop owner gets 33% of price; prices re-indexed to FX quarterly. Even then, with all shocks, a node needs **≥76% of base volume** (~46 malaria episodes + 30 BP subscribers a month) to break even. FX shock alone: ≥24%. **Margin of safety = only certify shops whose observed volume clears the stressed threshold.**

## Intrinsic value (probability-weighted, all ESTIMATE)
Probabilities: 50% die at pilot · 30% stall at 5k nodes stressed · 12% 5k nodes base · 8% 50k nodes base. Perpetuity from year 10, g = 3%.
Result: **$0.2–0.8M** expected value (USD discount rate 15–20%) vs **~$0.6M pilot capital at risk**. Thin. A good use of capital only as an information purchase, not as a scale bet.

## Moat audit
| Candidate moat | Strength today | Durable? |
|---|---|---|
| Trust brand ("drugs here are real") | 0 | **Yes**, the See's/Coke moat, if never broken |
| First regulatory accreditation | 0 | Temporary: regulators can accredit competitors |
| Procurement scale (GEICO low-cost) | 0 | Yes, at scale |
| Chronic-patient switching costs | 0 | Moderate |
| Network effects | Weak | No |

## Prune the stack (hurdle: FGN 10-year bond 17.05%, Oct 2026)
- **Keep:** L1 nodes + chronic subscriptions · L3 prepaid plan (float, short-tail; combined ratio < 100 or don't write it) · L7 training.
- **Partner, don't own:** L2 wholesale (thin margin, working-capital heavy) · L4 diagnostics.
- **Avoid:** L5 hospitals (capital- and labour-heavy: the airline problem) · L6 generic manufacturing (commodity vs India/China scale, FX, capex) · L8 regional replication (until Nigeria earns).

## Incentives
Shop owners profit from selling an antimalarial to every fever; test-and-treat cuts sales on negative tests. **Pay for the test and correct treatment, not per pill.** Same for us: earn on subscription and test fees, not drug volume.

## Inversion: how this dies
Dollar debt against naira revenue · scaling before per-node volume is proven · one batch of fake stock · shop owners selling side stock · harm leading to a regulator ban · government price controls · founder outside their circle of competence.

## Musk vs Buffett
Musk picks the target (10× fewer cheap deaths) and states the odds. Buffett decides how much money to risk and which layers to own. Conflicts: urgency vs patience, vertical integration vs capital-light, 10% bets vs Rule #1. **Resolution: Musk on the mission, Buffett on the money.** Bet only the pilot; scale from internal cash; own only high-ROIC layers.

---

# v5: Musk × Buffett master plan (2026-11-14) — model: `nigeria-health-compound.py`

**One line:** Musk sets the target and builds the machine. Buffett decides how much money is at risk and when the next rung unlocks. Seed with $0.5–1.5M of equity, run a lean HQ, certify only high-volume shops, and grow from internal cash. Model: 5,000 shops in ~3.5–5 years and 50,000 in ~6.5–10 years (slip case 1.5–3×: 10–30 years). No debt, no big raise until three years of proven earnings.

## The combined operating system
| # | Musk | Buffett | Combined rule |
|---|---|---|---|
| 1 | Physics ceiling, 10× target | Circle of competence | 10× target, executed only by people who know the domain (pharmacist + clinician as equity partners) |
| 2 | State the odds; take 10% shots | Rule #1: don't lose money | Take the 10% shot with only the money you can lose (pilot ≤ $0.6M) |
| 3 | Urgency | Patience, compounding | Maximum speed **that internal cash can fund** |
| 4 | Vertical integration where the idiot index is high | Avoid capital-heavy, low-ROIC businesses | Integrate a layer only if index ≥ 5 **and** stressed ROIC > 17% hurdle (FGN 10-yr) **and** funded from cash |
| 5 | Cost floor below the competitor's price (kill shot) | Low-cost-producer moat (GEICO) | The kill shot *is* the moat, if the cost advantage is structural |
| 6 | Delete parts and steps | Frugality (tiny Berkshire HQ) | HQ fixed cost ≤ $8k/month until breakeven |
| 7 | Requirements need a named owner | Incentives drive outcomes | Every actor is paid for the right outcome: shops for correct treatment, not pills |
| 8 | Prove crewed systems privately | Reputation is irreplaceable | Batch-test everything; one harm event can end the company |
| 9 | Fast public reversal | Inversion: avoid what kills you | Pre-write the kill list; reverse the moment a metric breaks |
| 10 | Demo over deck | Judge on demonstrated earnings | Raise outside money only on 3 years of audited unit economics |

## The master plan: Musk targets, Buffett gates
| Phase | Musk target | Capital | Buffett gate to unlock the next phase |
|---|---|---|---|
| 0 Proximity + permission (0–3 mo) | Shop walk, landed cost, PCN path | < $50k | ≥ 50% of shops above the stressed-volume threshold; prize ratio ≥ 5; permission path exists |
| 1 Pilot (50 shops, 6 mo; slip 9–18) | ≥ 80% of fevers tested; correct treatment | ≤ $0.6M equity | ≥ $81 contribution/shop/mo for 3 months; ≥ 95% batch pass; zero serious harm |
| 2 Compounding (→ 5,000) | Certification line rate (shops/week) | Internal cash only | 4 straight quarters of positive owner earnings; BP-subscriber retention measured |
| 3 Prepaid plan + partnered wholesale (→ 50,000) | 2M chronic subscribers | Equity only, after 3 years of proof | Claims < premiums (combined ratio < 100) |
| 4 Integrate (import → packaging → labs → focused hospitals) | Cost floor under every competitor | Per layer | Each layer: index ≥ 5 and stressed ROIC > 17% |
| 5 Replicate in West Africa | Copy the whole machine | Nigeria cash | Nigeria earning consistently |

## Compounding model (ESTIMATE inputs; shops capped by cash and 15%/month certification throughput)
| Case | Seed | HQ fixed | 5,000 shops | 50,000 shops |
|---|---|---|---|---|
| Base, $81/shop/mo | $0.5M | $8k/mo | 5.3 yrs | 9.6 yrs |
| Base, $81/shop/mo | $1.5M | $8k/mo | 3.7 yrs | 7.8 yrs |
| High-volume shops only, $100 | $1.0M | $8k/mo | 3.5 yrs | 6.6 yrs |
| Stressed, $40 | $5.0M | $8k/mo | 2.8 yrs | never |
| Base, $81, **fat HQ** | $0.5M | $20k/mo | 8.8 yrs | 13.0 yrs |
| No seed at all | $0 | either | never | never (fixed HQ cost exceeds 50-shop contribution) |

Breakeven shops = HQ fixed ÷ (contribution − $30): 157 at $8k HQ vs 392 at $20k HQ. The model has no saturation cap; ~200k drug shops exist, so ignore outputs above that.

**Reading:** the stressed case never reaches 50k. **The volume threshold for certification is the margin of safety, and a lean HQ is the cheapest acceleration.**
