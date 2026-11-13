# Nigeria health — Musk-mode scan

Date: 2026-11-13 · Status: **INVESTIGATE** (2-week kill test pending)

## Recommendation
Don't try to replace "the health industry." That is six industries, and four of them are limited by permission or labour, not cost. Go after one unit only: **the cash price of a correctly treated primary-care episode** (diagnosis plus quality-assured generic drug). Before spending money, run a 2-week price survey that can kill the idea.

## Premise check
- The protocol's own don't-apply list names healthcare delivery. Nigeria is a partial exception: **58–75% of health spending is out-of-pocket**, so patients pay cash at the shelf price. In a cash market, price competition works. In an insured market it does not.
- Restated goal: **cut the cash price of a correctly treated episode for the top 5 primary-care conditions by ≥5× in one LGA within 12 months** (slip case 18–36 months), with ≥95% of drug batches passing quality tests.

## Gate 0: segment classification

| Segment | Impossibility type | Binding constraint | Verdict |
|---|---|---|---|
| Generic essential medicines (price) | 3 Cost + 4 (NAFDAC registration) | Procurement/FX, fragmented import | **INVESTIGATE**: the only segment with a possible ≥5 prize ratio |
| Primary care by doctors | 4 + labour | 2.9–3.9 doctors/10k; ~4k leave per year | **WALK** on doctors. Use task-shifting (already legal under TSTS 2014/18/22) |
| Primary care by nurses/CHEWs | 4 (scope of practice), **partly open** | State-level domestication of TSTS | **Use as the delivery channel** |
| Health insurance | 4 + trust | ~10% enrolled | **WALK** (don't-apply list) |
| Local drug manufacturing | 3 + capital + FX | Capex; local output is low-end | **WALK for v1**: a failure here could cost the ability to try again |
| PHC power (solar vs diesel) | 3 | Already near parity | **Enabler, not the business**: prize ratio ~1–4 (ESTIMATE) |
| Hospitals and specialists | 4 + labour | Licensing, emigration | **WALK** |
| Diagnostics/labs | 3? | Unknown | **I don't know.** Cheapest check: price 5 tests at 10 labs |

### Six-number scan: generic medicines
1. Idiot index: **unknown.** An IRP is a supplier price, not raw material. Finding the real floor needs a landed-cost quote.
2. Price per unit of utility: shelf price ≈ **11.5× IRP** for cheapest generics (BusinessDay, ~2025; underlying report not identified, so this is a hypothesis). The 2004 WHO/HAI survey found **2–64× IRP**.
3. Floor: IRP is ≤ the floor's upper bound. **ESTIMATE: landed cost ≈ 1.5–3× IRP** once FX, tariffs and logistics are added. Verify with step 2 below.
4. Prize ratio ≈ 11.5 ÷ (1.5–3) ≈ **4–8×**. This straddles the attack line, so **INVESTIGATE**.
5. Physics shift: **PARTIAL.** It's cheap verification, point-of-care tests and solar+LFP (stationary storage $70/kWh, BNEF 2025), not a new drug-cost curve.
6. Incumbent lock-in: the market is **fragmented chaos, not a locked incumbent.** Open markets (Idumota, Sabon Gari) are moving to coordinated wholesale centres. DrugStoc, Remedial Health and Pharmarun are already attacking distribution, so distribution alone is not a revolution.

**Key fact (WHO/HAI 2004, stale):** Nigeria's *retail* markups were the **lowest** of the 8 countries surveyed. High prices came from **procurement**. So attack import and procurement, not pharmacy margins. Re-verify this with the new survey.

### Failure value
- Capital for one clinic: bounded. Acceptable.
- **Unbounded:** patient harm from bad stock or out-of-scope care → NAFDAC/PCN shutdown and lost trust. This is human-rated, so **prove it privately**: test every batch, use written clinical protocols, set up referral to doctors. Safety wins over speed.

## Requirements with owners

| Requirement | Owner | Verdict |
|---|---|---|
| Every clinic needs a doctor | Convention; TSTS policy (FMoH) says no for scoped tasks | **Delete** within TSTS scope; keep a doctor for referral |
| SKUs must be NAFDAC-registered | NAFDAC (DG Prof. Mojisola Adeyeye) | **Keep**: physics-grade for liability |
| Pharmacy needs a superintendent pharmacist | PCN | **Keep**: hire one |
| Must manufacture locally | "Industry"/policy narrative, no owner for v1 | **Delete for v1** |
| Need insurance to scale | No owner | **Delete**: cash, posted prices |
| Need an app/platform | No owner | **Delete**: automate last |

## Deleted
- "Replace the industry" as scope.
- Hospitals, specialists, insurance, local manufacturing (all v1).
- Doctor-in-every-clinic (where TSTS covers the task).
- Owned real estate; app/platform; national rollout.
- Over-delete check: likely add-back is a **doctor tele-referral line**. That's fine; it's the ~10%.

## Plan
1. **Price survey, weeks 1–2.** Owner: Habeeb. 10 tracer medicines + 5 conditions (malaria, hypertension, diabetes, UTI, childhood pneumonia), 20 outlets (pharmacies, PPMVs, private clinics) in **one LGA**, WHO/HAI method against the MSH IRP guide. **Kill rule: median < 3× IRP → WALK.**
2. **Landed-cost quote, weeks 1–3.** Owner: Habeeb + one licensed importer. Same 10 SKUs from WHO-prequalified generic makers, landed in naira, with NAFDAC status per SKU. That gives the real floor.
3. **Regulatory map, weeks 2–4.** Owner: Habeeb + hired superintendent pharmacist. What nurses/CHOs/CHEWs may do in the chosen state under domesticated TSTS (Kaduna and Kano have domesticated it).
4. **One-clinic pilot, 90 days (slip case 135–270).** Owner: lead nurse/CHO (to hire). Solar-powered, 5 conditions, batch-tested stock, prices posted on the wall.
5. **Only if the metric holds:** replicate clinic #2 from a written build sheet (the machine that builds the machine). Software last.

## Numbers

| Metric | Value | Source · date · tier |
|---|---|---|
| Out-of-pocket share | 58.3% (2024) / 58.8% (2023) NHA vs ~75% (2020) WHO; method dispute | NHA via Gazette, Dec 2025 (T2); WHO via Guardian (T2) |
| Insured | 21.73M ≈ 10–13% (denominator-dependent) | NHIA via Nairametrics, Q4 2025 (T2) |
| Doctors | 2.9–3.9 per 10k (WHO threshold 10–17) | Min. Pate 2025; State of Health report 2025 (T2) |
| Doctor emigration | 3,974–4,193 in 2024 | Ministry review via BusinessDay/AllAfrica (T2) |
| Medicines imported | 60–70% (NAFDAC says 60%) | NAFDAC via Premium Times; SOAS/ICIR (T2) |
| Generic price vs IRP | ~11.5× (current, unverified report); 2–64× (2004) | BusinessDay (T2, origin unknown); WHO/HAI 2004 (T1, stale) |
| Distribution markup | up to 100% on FOB | mPharma blog, undated (T3) |
| Substandard/falsified | 12–13% | NAFDAC survey 2021–22 (T2) |
| PHCs | ~34k; 20–40% functional; 40% of functional lack power | Dataphyte; SEforALL 2021–22 (T2/T3) |
| Pharma market | ~$1.8–2.0B (2025) → ~$9/person/yr (my arithmetic, ~220M) | Freyr (T3); KPMG Jul 2026 (T2) |
| Off-grid solar | ~$0.20/kWh lifetime, ≈ diesel | Heinrich Böll (T2) |

## Bottleneck
**Landed cost of quality-assured generics in naira.** If it isn't ≤ ⅓ of the median shelf price, there is no company, only a nicer pharmacy.

## Metric
**₦ per correctly treated episode** (5 tracer conditions), divided by the LGA median. Target ≤ 0.2 with ≥95% batch pass rate.

## Risks
- **Revenue shrink:** a 5× price cut on a ~$2B market only works if volume grows (unmet demand). Track volume per clinic per day.
- **FX:** a naira move ruins landed cost. Price in a band, hedge with local fill where it exists.
- **Copycats:** a cost floor only matters if it's below the competition's *price*, provably.

## Next physical action (this week)
Print a 10-drug price sheet and walk 20 outlets in one Lagos LGA. Record the price, brand, NAFDAC number and expiry for each.
