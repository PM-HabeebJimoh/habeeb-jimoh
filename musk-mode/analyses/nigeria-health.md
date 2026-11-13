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
