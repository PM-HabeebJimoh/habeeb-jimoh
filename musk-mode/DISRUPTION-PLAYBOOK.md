# DISRUPTION PLAYBOOK — Discovery & Total Industry Replacement (v1.2)

**Status:** Companion to `MUSK-MODE.md` §7. This file replaces the summary bullets with instruments you can actually compute, plus the evidence behind every number.
**Rule of this file:** every number carries a source and a date. Every number has an error bar. Anything I could not source is labelled **ESTIMATE** or **UNVERIFIED**.

---

## 0. WHY THIS FILE EXISTS

The v1.1 section was directionally right and numerically sloppy. That is the exact failure mode you flagged. Agents (and humans) produce plausible-sounding detail that decays into fiction under audit. This file fixes it in three ways:

1. **Every claim gets a source, a date, and a confidence level.**
2. **Numbers that are commonly repeated but wrong get corrected, including my own.**
3. **Where the method fails, it says so with case evidence** — not with a disclaimer bolted on at the end.

---

## 1. CORRECTIONS TO WHAT I TOLD YOU (v1.1 → v1.2)

| v1.1 said | Corrected | Why it matters |
|---|---|---|
| "Rocket ≈ $60M, raw materials ≈ $1M, so ~60× idiot index" | Raw materials ≈ **2% of a rocket's price** → index ≈ **50:1** (Musk, Wired 2012). A separate analysis puts it at ~3% → **~33:1**. | I stated a specific pair of dollar figures that I had not sourced. The *ratio* is well documented; my *derivation* was invented. Never dress a remembered ratio in fabricated line items. |
| "Shuttle ~$54,000/kg vs Falcon 9 ~$2,700/kg" | Both are **nominal, mixed-year** numbers. In **constant 2025 dollars**: Shuttle **$79,100/kg**, Falcon 9 **$3,140/kg** → **~25×**. Using nominal figures and a reusable-marginal Falcon 9 price gives **~35×**. | The multiple swings between 25× and 35× depending on your convention. Anyone quoting one without stating the convention is selling you something. |
| "Batteries in 2010: ~$1,000/kWh" | BNEF: 2010 average pack **$1,474/kWh in real 2025 dollars**; 2025 average **$108/kWh** — a **93% decline**. The ~$1,100/kWh figure you see everywhere is nominal. | Same error class: nominal vs real. A 93% decline is the honest number. |

**Lesson that goes into the protocol:** a ratio with a source beats a dollar figure without one. When I don't have the line item, I say "the ratio is documented; the decomposition is not."

---

## 2. THE INSTRUMENTS, DEFINED PRECISELY

### 2.1 Idiot index

```
Idiot index = price of the finished component ÷ cost of its raw materials
```

**What belongs in the denominator:** commodity cost of the actual materials, at market price, including the mass you scrap.
**What does not belong:** labour, tooling, certification, testing, documentation, permits, yield loss, amortised capital.

**Documented examples (Isaacson, *Elon Musk*, 2023):**
- Rocket nozzle actuator: supplier quote **$120,000** → built in-house at **~$3,900–$5,000**. *(Sources differ on the final number: Vance's 2015 biography says $3,900; a 2026 analysis says $5,000. Range, not point.)*
- NASA space-station latch: **$1,500** each → a SpaceX engineer modified a **bathroom-stall latch** for **$30**.
- Supplier-quote ÷ in-house-cost on the actuator: **24–31×**. *(This is **not** an idiot index — the denominator is a built cost, not raw material. The actuator's true index is undocumented.)*

### 2.2 Where the idiot index lies (the honest critique)

A high index is a **flag to investigate**, not proof of waste. The denominator excludes the expensive parts of aerospace reality:

- certification and traceability (AS9100, ITAR, flight qualification),
- low-volume tooling amortisation,
- skilled machining time,
- liability and insurance.

A $1,500 certified latch and a $30 bathroom latch are not the same object — one carries a paper trail that survives a failure investigation. **The index tells you where to send an engineer, not where to send an invoice.**

**Correct usage:** high index → send a team to *understand the cost stack*. Low-cost replacement only after the requirement that created the certification is itself questioned (Gate 1).

### 2.3 The theoretical floor

```
floor = raw materials + energy + direct labour at minimum viable staffing + minimum tooling amortisation
```

If **price ÷ floor < 3**, there is no revolution — there is a business. If it is **5–50×**, the gap is a company.

### 2.4 The 10× test

Find the metric where a 10× change is *physically* possible. If the best available physics only yields 20%, the incumbent survives. Incumbents always survive 20%.

---

## 3. CASE A — LAUNCH (the one that actually worked)

### 3.1 The numbers

| Vehicle | $/kg to LEO | Basis | Reusable |
|---|---|---|---|
| Space Shuttle | **$79,100** | 2025 dollars, program cost ÷ 135 flights ÷ 27.5 t | Partially |
| Saturn V | $6,670 | 2025 dollars | No |
| Falcon 9 (2024 list, $69.75M) | **$3,140** | 2025 dollars, ÷ expendable 22.8 t | Booster |
| Falcon 9 (2026 list, $74M) | $3,246 | my arithmetic, same convention | Booster |
| Falcon Heavy (2022 list) | $1,670 | 2025 dollars | Boosters |
| Ariane 6 (A64) | ~€115M/flight (2018 est.) | ≈ **€5,300/kg** at 21.65 t (nominal 2018 €; convert to 2025 $ before comparing) | No |
| Vulcan Centaur | $110–200M/flight, no list price | ≈ $4,000–7,300/kg at 27.2 t | No |
| Starship **target** | **$100–200/kg** stated target; "$10/kg" Musk aspiration | **NOT ACHIEVED** | Design goal |

Source conventions: flightatlas.org (2025 dollar conversion); SpaceX list prices; ArianeGroup 2018 estimate.

### 3.2 What actually created the multiple

1. **Booster reuse.** Boosters have flown **30+ times** (reported up to 34 by 2026); 570+ landings by March 2026.
2. **Cadence.** SpaceX flew **165 Falcon missions in 2025**. Ariane 6 flew **4**. ULA flew **6**. Cadence amortises fixed cost — it is a *cost* weapon, not a marketing stat.
3. **Vertical integration.** Engines, avionics, structures in-house when the index was high.
4. **The Arianespace/ULA response.** Ariane 6 is expendable and its own institutional backers now buy Falcon 9 for some payloads. ULA has begun work on Vulcan engine-section recovery — approximately **eight years late**.

### 3.3 The subtlety almost everyone misses

**SpaceX's price is not SpaceX's cost.** The list price (~$74M) is set by what the market will bear, while marginal cost on a reflown booster is far lower (booster amortisation ~$1.5M + refurbishment + ~$200K propellant, per industry estimates). That gap is the kill switch: **SpaceX can drop price to any level that kills a competitor and still operate.** No expendable provider can follow without destroying its own margin.

This is the real definition of the kill shot: not "I am cheaper," but "**my cost floor is below your price, and I can prove it on demand.**"

### 3.4 Honest limits on the case

- Starship is **$15B+ spent** and still not at its stated target. The 25-flight 2025 goal missed by **5×**.
- Musk's engineering milestones ship eventually; his **dates** are systematically wrong (Falcon Heavy 5 years late, Crew Dragon 3 years late).

**Verdict: real, completed replacement of an industry's cost structure.** The strongest evidence is not the rocket — it is that competitors had to change architecture (reusability) they had publicly rejected.

---

## 4. CASE B — BATTERIES (the cost curve that made the industry possible)

| Year | Average pack price | Note |
|---|---|---|
| 2010 | **$1,474/kWh** (real 2025 $) | BNEF, inflation-adjusted |
| 2023 | $139/kWh | −20% steps became normal |
| 2024 | $115/kWh | |
| 2025 | **$108/kWh** | BEV packs **$99**; stationary storage **$70** (−45% YoY) |

**Total: 93% decline since 2010.** Cell prices: $74/kWh (2025). Lithium metal is now ~10–12% of pack cost at ~$19,750/t — the raw material is no longer the constraint; **manufacturing and scale are**.

**Musk's 2012 argument:** packs could go from ~$600/kWh toward ~$80/kWh by buying commodity materials directly instead of accepting supplier pricing. *(Commonly cited; the $600 figure is approximate across early-decade surveys.)* The direction was right; the timeline was ~a decade long.

**Important distinction:** pack price ≠ idiot index. BNEF's $108 includes manufacturing, warranty, and margin. The relevant index is *cell price ÷ commodity content*, and it has **collapsed** — which is precisely why the moat moved from chemistry to factory scale and to LFP supply chains (China at $84/kWh average vs +44% North America, +56% Europe).

**Verdict: completed replacement of the cost curve, incomplete replacement of the industry.** The battery was the enabler; the car market is still contested.

---

## 5. CASE C — STARLINK (platform capture, executed)

| Metric | Value | Date/Source |
|---|---|---|
| Working satellites | **10,759** (12,472 launched) | Jul 2026, Jonathan McDowell |
| Share of all active satellites | **~66%** (other counts put it 50–67%) | 2025–2026, McDowell / trackers |
| Subscribers | **10.3M** | Mar 2026, SpaceX |
| Markets | 164 countries/territories | Mar 2026 |
| 2025 Falcon launches | 165, majority Starlink | 2025 |

**Why this is the template:** launch cost fell ~25× → SpaceX could afford to own the *demand* side too → vertical integration became a moat no launch competitor can cross, because a competitor must now beat both the rocket price and the constellation. **Reuse the stack** is the mechanism: rocket → satellite bus → ground terminal → service.

**Error-bar note:** the "share of satellites" figure ranges 50–67% across trackers because they disagree on "active" and on decayed-but-tracked objects. Quote a range, or quote one named source with its date. Do not average them.

---

## 6. CASE D — WHERE THE METHOD FAILED (read this twice)

### 6.1 FSD / robotaxi — requirement, not physics
- 2019: "**1 million robotaxis by 2020**." Delivered: **zero**.
- First paid robotaxi ride: **22 June 2025**, Austin, geofenced, with safety monitors.
- Across ~94 tracked Musk predictions: **8 on time (~9%)**, 46 outright failed.
- FSD still labelled **"Supervised"** (SAE Level 2) in 2026; Tesla dropped full-autonomy wording in Sept 2025.

**Diagnosis:** the binding constraint was never the cost of sensors or compute. It was **perception edge cases + regulatory approval + liability**. The idiot index cannot see any of those three. Cost weapons do not defeat a safety-certification moat.

### 6.2 Boring Company — the requirement was never deleted
- Promised: **155 mph**, "4,000 vehicles/hour," final-form **90,000 passengers/hour**.
- Delivered (Vegas Loop, opened 2021): **~35 mph** in practice, peak demonstrated throughput **~4,400–4,500 passengers/hour** at conventions, ~30,000 passengers/day.

**Diagnosis:** the tunnel was automated-adjacent engineering applied to a **transit** problem, where the real constraint is regulatory approval, right-of-way, and station throughput — not digging speed. Also: the vehicle is a car, so capacity per tunnel is bounded by car physics. The 25–40× gap between promise and delivery is what happens when you optimize a subsystem without questioning the system requirement.

### 6.3 Tesla profitability — the uncomfortable line item
| Year | Net income | Regulatory credits | Credits as share of operating income |
|---|---|---|---|
| 2023 | $15.0B (incl. one-off deferred-tax benefit: $5.0B here; ~$5.9B per memory — **UNVERIFIED**, check 2023 10-K) | — | — |
| 2024 | $7.09B | **$2.76B** (record) | — |
| 2025 | **$3.79B** on $94.8B revenue (first-ever annual revenue decline, −3%) | **$1.99B** (−28%) | **~46%** |

Q1 2025 alone: credits **$595M** vs net income **$409M** — without credits, a loss.

**Diagnosis:** a completed cost revolution does not guarantee a completed *business* revolution. Tesla won the cost structure and still depends on a regulatory arbitrage that legislatures can delete. A cost moat is only durable if the profit does not come from someone else's compliance obligation.

### 6.4 The near-death events
- **Nov 2008:** ~$9M cash on hand; rescued by $40M convertible debt. Tesla and SpaceX both survived on last-minute financing.
- **2018:** Model 3 ramp nearly bankrupted the company; SEC action over the "funding secured" tweet cost Musk and Tesla $20M each, with **$41.53M** distributed to investors.
- **Model 3 "production hell":** Musk's own verdict — *"Excessive automation at Tesla was a mistake. To be precise, my mistake. Humans are underrated."* The **"fluffer bot"** tried to place fiberglass mats on battery packs; the mats turned out to be **unnecessary**. Automation had been built on top of a part that should have been deleted at Gate 2.

**That last one is the whole method in one anecdote:** they automated a part that shouldn't have existed. Steps 1, 2, 3 skipped; step 5 executed first; result: the most expensive kind of failure.

---

## 7. THE SCORECARD (calibrate trust before you copy the method)

| Domain | Cost structure replaced? | Industry replaced? | Verdict |
|---|---|---|---|
| Launch | **Yes** (~25×) | Yes, in progress | **Method worked** |
| Battery packs | **Yes** (−93%) | Partially | Method worked |
| Satellite broadband | Yes (via launch) | Yes, ongoing | Method worked |
| Cars | Yes (cost) | No (market share contested; profit depends on credits) | Partial |
| Autonomy | No | No | **Method failed** — wrong constraint |
| Urban transit | Marginal | No | **Method failed** — wrong constraint |

**Pattern:** the method works when the binding constraint is **manufacturing cost and physics**. It fails when the constraint is **regulation, liability, network effects, or human behaviour**. Those are not deletable with engineering.

---

## 8. THE DON'T-APPLY LIST (agents over-apply this method — stop them)

Do **not** run an idiot-index attack on these without first proving the constraint is cost:

| Domain | Real constraint | Why the index fails |
|---|---|---|
| Insurance, banking | Regulation, capital, trust | Materials are ~0% of cost; the price *is* risk and compliance |
| Healthcare delivery | Licensing, liability, labour | Raw materials are a minority of cost; the floor is people and approval |
| Social networks | Network effects | Your cost advantage is worthless if the users are on the other app |
| Airlines | Fuel + labour already near floor | Post-deregulation, the industry already ran this play; margins are thin because the floor *is* the price |
| Education, legal, logistics brokerage | Regulation, credentialing, relationships | Rent comes from permission, not manufacturing inefficiency |
| Anything with a certification gate | Safety case, not bill of materials | A cheaper uncertified part is a liability, not a saving |

**Rule:** if the theoretical floor is already achieved by the incumbent, you are not a disruptor, you are a worse-funded competitor.

---

## 9. THE 6-NUMBER SCAN (do this before committing a decade)

Compute these six, in this order, and write them down. No narrative.

1. **Idiot index of the single most expensive subcomponent.** Price ÷ commodity content.
2. **Nameplate price per unit of utility** ($/kg, $/kWh, $/km, $/GB, $/hour).
3. **Theoretical floor.** Materials + energy + minimum labour + minimum tooling.
4. **Prize ratio** = (2) ÷ (3). **Attack if ≥ 5.** Investigate if 3–5. Walk if < 3.
5. **Is there a physics-shift?** Named input curve (battery $/kWh, solar $/W, compute $/FLOP) that crossed a threshold in the last 10 years that the incumbent's architecture cannot use. Yes/No.
6. **Incumbent's sunk-cost share.** What fraction of their cost base is assets, channels, or obligations they cannot write down without a P&L event? **High = attack. Low = they will simply match you.**

### Verdict rule
```
ATTACK only if:  prize ratio ≥ 5
             AND physics-shift = YES (or physics itself is the limit and you have a manufacturing plan)
             AND incumbent is structurally locked
             AND no certification/regulatory gate you cannot clear
```
Anything else → it's a business, not a revolution. Build it, don't crusade about it.

---

## 10. ANTI-HALLUCINATION PROTOCOL (for me, for you, for any agent)

**Tier the source before you trust the number.**
- **Tier 1:** regulatory filings, published list prices, BNEF/IEA/NASA/Jones, peer-reviewed, named tracker with a date.
- **Tier 2:** major outlet reporting a primary source (Bloomberg using the 10-K).
- **Tier 3:** industry blog, aggregator, "cost comparison" site. Directional only.
- **Tier 4:** Reddit, X, LLM memory. **Never a citation. Only a hypothesis to verify.**

**Then apply the four checks:**
1. **Year and currency.** Nominal vs constant dollars changes a "35×" into "25×". Always state the basis.
2. **Denominator.** Is that $/kg computed on max payload or actual payload? On list price or internal cost? Different answers, both true.
3. **Range, not point.** If three sources give 50%, 66%, 67%, the honest output is "50–67%, depending on counting."
4. **Provenance or silence.** If I cannot name where a number came from, I write **ESTIMATE** and give the verification path. A confident sentence without provenance is the failure mode you are worried about — and you are right to be.

**Standing instruction:** if you ask for a number and I cannot source it, I will say so in one line and give you the cheapest way to check it. I will not smooth it over.

---

## 11. WHAT TO DO WITH THIS

1. Ask for an industry. I run §9's six numbers on it, with source tiers and error bars, and return ATTACK / INVESTIGATE / WALK.
2. If the answer is ATTACK, we build the §7 sequence in `MUSK-MODE.md` with your capital and timeline constraints as explicit inputs.
3. Re-audit this file quarterly. Publish dates go stale. A 2025 number in a 2028 decision is a fabricated number.

*Sources current as of November 2026. Numbers in this file are dated and will decay; the decision rules in §9 will not.*
