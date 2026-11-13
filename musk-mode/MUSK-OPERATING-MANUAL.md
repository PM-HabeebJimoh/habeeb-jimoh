# MUSK OPERATING MANUAL — every activity, every sub-activity

**Version 1.3 · November 2026 · Companion to `MUSK-MODE.md` and `DISRUPTION-PLAYBOOK.md`**

**How to read this:** each section is one *activity class*. Under it are *sub-activities* (what he actually does, mechanically), each with a **concrete example** — because "be first-principles" is worthless as an instruction and "demand each component's cost chart with raw material price, supplier price, and responsible engineer" is an instruction you can execute on Monday.

**Evidence tags:** `[DOC]` = filings/primary documents · `[BIO]` = Isaacson 2023 / Vance 2015 · `[REP]` = reported by credible outlets · `[OBS]` = observable public record · `[DISPUTED]` = contested or varies by source.

---

# 1. PERSONAL OPERATING SYSTEM

### 1.1 Time allocation
- **Surge mode.** Normal cadence, then near-total immersion during a crisis. Sleeps at the plant during ramps (Fremont 2018, Nevada battery line). `[BIO]`
- **Time-boxing.** Calendar split into ~5-minute blocks; works through in sequence; re-prioritises hourly. `[BIO/DISPUTED in detail]`
- **Proximity over reports.** Physically goes to the constraint — factory floor, launch site, tunnel boring machine, data centre shell. The location *is* the information.
- **Serial monogamy of attention.** Weeks where one company gets everything, others get almost nothing. Delegation is discontinuous, not balanced.

**What to copy:** go to the physical location of the bottleneck before you read a report about it. A photo from the floor beats a status deck.

### 1.2 Learning a new domain
- **Read the textbooks, then argue with engineers.** When starting SpaceX, he read rocket propulsion fundamentals and then quizzed engineers on specifics — famously correcting a presenter's numbers. `[BIO]`
- **Build the cost model first.** Every new domain enters through its material and energy costs, not its literature review.
- **Recruit a translator.** Hires one domain expert, extracts the model, then generalises. (Boring Co.: 2 a.m. call to an engineer, 3 hours later demanding a decision on buying two $5M machines.) `[BIO/REP]`

### 1.3 Physical and psychological regimen
- Documented: long hours, high stress, admitted sleep deprivation during crunches; **he has publicly walked this back** ("sleep is important"). Don't copy the 2018 version — he doesn't. `[REP/OBS]`
- **No scheduled vacation norm**; works through holidays during ramps. `[REP]`
- **Caffeine and rapid context-switching**; runs multiple companies with direct technical involvement in each weekly.

**Copy:** the domain immersion + proximity. **Do not copy:** the sleep deprivation. He publicly regretted it.

---

# 2. REQUIREMENT SETTING

### 2.1 The master plan mechanism
- **Publish the plan.** Tesla Master Plan 1 (2006), 2 (2016), 3 (2023), 4 (Sept 1, 2025 — "sustainable abundance", AI + Optimus). SpaceX: Mars architecture. Publishing creates an external commitment device.
- **Explicitly admit incompleteness.** Musk said Master Plan Part 2 remains unfinished. `[OBS]`
- **10-year architecture, 18-month execution.** Long-horizon goal, short-horizon tactics.

### 2.2 Deleting requirements
- **Named owner rule:** every requirement must trace to a person, not a department. `[BIO]`
- **Question smart people's requirements hardest** — they are challenged least.
- **Physical-law test:** if it's not forbidden by physics, treat it as a recommendation. `[OBS/BIO]`
- **Specific deletion:** the fiberglass mats on the battery pack turned out to be **unnecessary** — discovered only after automating them ("fluffer bot"). `[REP, 2018]`

### 2.3 Setting the number
- **10× not 10%.** $/kg to orbit, cost per kWh, cars per week, GWh per year.
- **Deadline as a design tool.** Insane deadlines, publicly stated. **Systematically missed** — this is the method's price, not a bug you can remove. `[OBS]`
- **Metrics chosen before design:** cost per ton to orbit, miles per intervention, photons collected vs used. `[BIO]`

**Copy:** write the number and the owner. **Do not copy:** stating the date publicly if your credibility is the product.

---

# 3. DECISION-MAKING

### 3.1 THE ALGORITHM (the core, 5 gates, in order) `[BIO]`
1. **Make requirements less dumb** — named human, question even Musk's own.
2. **Delete the part or process step** — over-delete; add back ~10% (Isaacson reports Musk saying 20% in some tellings — **treat as "≥10%, contested"**).
3. **Simplify / optimise** — only what survived.
4. **Accelerate cycle time** — only after 1–3.
5. **Automate last** — his own biggest documented error was skipping to 5.

### 3.2 First principles
- **Decompose to physics/commodity prices**, then rebuild. Rocket raw materials ≈ **2% of price** (Wired, 2012) → idiot index ~50:1. `[REP]`
- **Idiot index** = part price ÷ raw material cost. Actuator: supplier **$120k** → in-house **~$3.9k–5k**. NASA latch **$1,500** → bathroom-latch derivative **$30**. `[BIO]`
- **Question the spec, not just the quote.** "$250,000 valve" questioned down.
- **When the answer is "because the supplier says so," the answer is "build it."**

### 3.3 Decision velocity
- **Decide with incomplete information and reverse fast.** Announce, test, walk back. (Autopilot sensor removal, FSD hardware, pricing changes.)
- **Reverse decisions openly.** "Excessive automation was a mistake. To be precise, my mistake." `[2018 tweet]`
- **Kill your own features.** Solenoid valves, parts, and whole systems deleted after they were already designed.

**Copy:** the order. **Copy:** public reversal. **Do not copy:** deciding on Twitter before the SEC settlement (2018, $20M each; $41.53M distributed to investors in 2026). `[DOC]`

---

# 4. ORGANISATION & MANAGEMENT

### 4.1 Structure
- **Flat by subtraction.** Delete org layers as aggressively as parts. Twitter/X: **~80%** headcount reduction (≈8,000 → ≈1,500, Musk to BBC, Apr 2023). `[REP — verify; the oft-quoted 90% is UNVERIFIED]`
- **Engineers lead.** Product managers de-emphasised; engineering-led teams. `[BIO, Twitter 2022]`
- **Small hardcore teams** rather than large mediocre ones; "hardcore" ultimatums at X (2022).
- **Design and manufacturing co-located** — engineering desks on the factory floor so engineers feel their own design pain. `[BIO]`

### 4.2 Skip-levels and direct contact
- **Skip levels routinely** — talks to the person doing the work, not their manager.
- **Any employee can escalate to the top.** "If a significant problem arises, schedule meetings every 24 hours until resolved." `[BIO]`
- **The assembly-line rule:** a line worker should be able to grab a designer and ask *"why the fuck did you make it this way?"* `[BIO quote]`
- **Managers must be able to do the work.** "You can't lead a cavalry if you can't ride a horse." Software manager must code; solar-roof manager must install roofs. `[BIO]`

### 4.3 Meetings
- **Meetings are for decisions, not status.** Status goes in data.
- **Walk out / end the meeting** when the decision is made or the information is absent.
- **24-hour loop** on a blocker: meet daily until it's dead.
- **Cost charts in reviews:** every component, raw material cost, supplier cost, responsible engineer. Presenters are expected to know their numbers to more digits than the reviewer. `[BIO]`

### 4.4 Hiring & firing
- **Personally interviews key hires**, especially engineers. `[BIO]`
- **Attitude over credentials** — "skills can be taught; changing attitude requires a brain transplant." `[BIO]`
- **Proof of exceptional ability** over formal degrees (SpaceX hiring line). `[REP]`
- **Firing is fast and unsentimental**; "two strikes" pattern for staff who repeatedly fail. `[BIO]`
- **Documented cost:** mass firings followed by rehiring (Twitter, Supercharger team 2024); NLRB complaint over SpaceX open-letter firings; employees report fear-driven culture. `[REP]` **This is a real cost, not a rumour.**

### 4.5 Culture devices
- **"Maniacal sense of urgency"** as the stated operating principle. `[BIO]`
- **Camaraderie is dangerous** — it suppresses challenge. `[BIO]`
- **"Okay to be wrong, not okay to be confidently wrong."** `[BIO]`
- **Never ask others to do what you won't.**
- **Hardcore as a filter:** high expectations select for people who want the pace.

**Copy:** skip-levels, engineer-led teams, co-location, the "managers must do the work" rule.
**Do not copy blind:** the firing pattern. It works at high-margin, talent-surplus, mission-driven companies and destroys institutional knowledge everywhere else.

---

# 5. ENGINEERING & DESIGN

### 5.1 Part-count discipline
- **"The best part is no part. The best process is no process."** `[OBS]`
- **Deletion before optimisation** at every review.
- **Material reversal on evidence:** Starship switched from carbon fibre to stainless steel — cheaper, easier to weld outdoors, better at cryo temps. `[REP]` The lesson: question the *material requirement*, not just the supplier.

### 5.2 Prototyping philosophy
- **Build hardware early; blow it up; learn.** "Rapid unscheduled disassembly" is a data event.
- **Test articles over simulations** where simulation is unproven.
- **Prototype ≠ product.** The factory is the product.

### 5.3 Design for manufacturing
- **Designers sit with the line.**
- **Tolerances and cycle time are design variables**, not downstream concerns.
- **Design to the production rate you need**, not the rate you have — the machine that builds the machine is ~90% of the difficulty. `[BIO]`
- **Never hide behind "it's derived from the design."** If the design forces a bad process, the design is wrong.

### 5.4 Measuring
- **One number per subsystem.** Cost per unit, mass per unit, rate per hour, seconds per station.
- **Mass obsession:** every kilogram on a rocket costs roughly its launch price many times over; every kilogram on a car costs range.

---

# 6. MANUFACTURING & PRODUCTION (the real specialisation)

### 6.1 The core thesis
**"The machine that builds the machine"** — manufacturing engineering outranks product design. `[BIO/OBS]`

### 6.2 Practices
| Practice | Mechanism | Evidence |
|---|---|---|
| **Line rate as the goal** | Weekly output number; every constraint attacked in order | Fremont 5,000/week push 2018 |
| **Bottleneck hunting** | Find the slowest station; everything else is noise | Classic TOC, executed literally |
| **In-house when the index is high** | Vertical integration by arithmetic, not ideology | Engines, avionics, seats, casting |
| **Automation last** | Delete the part first, then simplify, then automate | Fluffer bot; Musk's own retraction |
| **Sleep at the constraint** | Physical presence during ramp | Fremont, Nevada, Shanghai |
| **Multi-site replication** | Copy the whole factory design across continents | Shanghai, Berlin, Texas, Shanghai Megafactory (40 GWh run-rate by Mar 2026) `[REP]` |

### 6.3 Production scaling numbers (dated, sourced)
- Falcon: **165 launches in 2025**; single booster **37 flights** (B1067, Aug 2026); fastest turnaround **~9 days**; landing success **~98%** (667/680 by Oct 2026). `[REP]`
- Tesla storage: **46.7 GWh deployed 2025** (+49%), Q4 2025 record **14.2 GWh**, energy revenue **$12.8B**, gross margin ~**28.7%**. `[REP]`
- xAI Colossus: **100k GPUs in 122 days** from an empty factory; doubled in ~92 more days; scaling toward 1M GPUs. `[REP]`

**Copy:** the doctrine. **Copy:** "sleep at the constraint" as metaphor — physically be where the problem is. **Don't copy:** over-automation; he already paid for that lesson with a year of Tesla's life.

---

# 7. CAPITAL & BUSINESS MODEL

### 7.1 Compensation structure
- **2018 CEO Performance Award:** no salary, no cash bonus, no time-vested equity. 12 tranches, each requiring **both** a market-cap milestone **and** an operational milestone; full vest required **$650B** market cap and 12 of 16 operational milestones. `[DOC: SEC DEF 14A]`
- **Outcome:** all 12 tranches certified achieved; Delaware Chancery rescinded the award; shareholders ratified twice; still unresolved in 2025–26 filings. `[DOC]`
- **Signal:** compensation = lottery ticket on a stated goal, not a salary.

### 7.2 Capital strategy
- **Reinvest everything; run near the edge.** Tesla survived 2008 with **~$9M cash** and $40M convertible debt; 2018 ramp nearly broke it. `[REP]`
- **Raise on vision, deploy on physics.**
- **Public-market critique:** Musk argued quarterly reporting pressure is structurally wrong for long-horizon engineering (2018 blog). Then went public anyway, twice. `[DOC/OBS]`
- **Government money: take it, don't depend on it.** Tesla's profitability leaned heavily on regulatory credits — **$2.76B in 2024**, **$1.99B in 2025** (~46% of 2025 operating income). `[DOC]` A structural dependency he criticises in others.

### 7.3 Business-model design
- **Vertical integration as margin capture** where the index is high.
- **Platform capture:** Supercharger network, Starlink as an ISP rather than a satellite seller.
- **Sell the expensive thing only when cost justifies it** — price set by market, cost set by physics; the gap funds the next factory.

**Copy:** at-risk compensation tied to *operational* and *financial* milestones simultaneously. **Do not copy:** the balance-sheet risk if you aren't able to raise capital on narrative.

---

# 8. COMMUNICATION

### 8.1 Internal
- **Numbers, diagrams, first principles.** Presenters must know their data better than the reviewer.
- **Direct, unfiltered, often brutal.** Documented public cost: employees describe fear; several firings contested. `[REP]`
- **Email/announcement as a scalpel:** company-wide emails stating hardcore expectations, headcount, strategy. `[REP]`

### 8.2 External
- **Demo over deck.** Reveal the hardware, not the road map.
- **State the absurd number publicly** and accept the credibility cost.
- **X/Twitter as a direct channel** — bypasses PR. Same channel produced the SEC fine. `[DOC]`
- **Recruiting as content:** the mission statement is the ad ("make humanity multiplanetary", "sustainable abundance").

**Copy:** demo over deck; name the number. **Do not copy:** the unfiltered channel when you have material non-public information.

---

# 9. RISK, FAILURE & SAFETY

### 9.1 Failure doctrine
- **Failure is an option; being wrong confidently is not.** `[BIO]`
- **Fail cheap, fail early, instrument everything.** Test-to-destruction on early hardware.
- **Never fail on the same thing twice** — that's a process failure, not a physics failure.

### 9.2 Safety boundary (the part people misread)
- **Crewed systems get the opposite treatment.** Crew Dragon flew uncrewed demos, parachute tests to destruction, and a pad-abort test before people. `[REP]`
- **Cargo/prototype hardware: iterate in public. Human-rated hardware: prove it privately.**
- **Aviation-grade ambition** for Starship: airline-like turnaround — explicitly not there yet: **9-day** best booster turnaround vs an airliner's same-day multiple cycles. `[REP]`

### 9.3 Regulatory interface
- **Treat regulators as a requirement with a named human** — question, negotiate, sometimes ignore and litigate.
- **Documented consequences:** FAA launch-licence friction, NLRB complaints, EPA/state disputes over xAI's Memphis turbines. `[REP]`
- **Do not copy** the adversarial default unless you can absorb years of litigation.

---

# 10. COMPANY-BY-COMPANY ACTIVITY MAP

| Company | Core activity class | Signature practices | Key numbers (dated) |
|---|---|---|---|
| **SpaceX** | Cost-per-kg revolution + cadence | Booster reuse, vertical integration, test-to-failure, Starlink as demand anchor | $79.1k/kg (Shuttle, 2025$) → $3.1k/kg (F9); 165 launches 2025 |
| **Tesla Auto** | Machine that builds the machine | Gigafactory replication, casting, automation-last (learned), OTA software | 5,000/wk Model 3 target; 2018 near-death |
| **Tesla Energy** | Grid-scale manufacturing | Megapack line replication, LFP, storage-first margins | 46.7 GWh 2025; $12.8B rev |
| **Starlink** | Platform capture | Vertical stack: launch → sat → terminal → ISP | 10,759 working sats (Jul 2026); 10.3M subs |
| **xAI** | Brute-force infrastructure velocity | 122-day build, power-first, own the datacentre | 100k GPUs → 200k+; 1M target |
| **Boring Co.** | Manufacturing-cost attack on civil works | Cheap tunnel diameter, continuous boring, Prufrock | Promised 155 mph → delivered **~35 mph**; ~4,400–4,500 pax/hr demonstrated `[the gap]` |
| **Neuralink** | Regulated medical device | Robot surgeon (R1), N1 implant, PRIME trial | **28 of 30** enrolled (early 2026, per one tracker; other sources say 7 — **DISPUTED, verify**) |
| **X** | Org deletion at speed | ~80% headcount cut (Musk, BBC Apr 2023), engineering-led, hardcore ultimatum | Documented rehiring + litigation |
| **Optimus / FSD** | Capability moonshot | Dojo/compute, fleet data, iterating in public | FSD still **"Supervised"** (2026) |

---

# 11. THE META-PROCESS (what actually makes it work)

1. **Immersion beats delegation.** He knows the machine better than its owner. That is the only reason "question everything" works instead of collapsing the org.
2. **Proximity beats abstraction.** Floor, pad, tunnel, datacentre.
3. **Deletion beats addition.** Every review ends with a smaller thing.
4. **Physics beats seniority.** Correctness is the currency; rank is not.
5. **Urgency beats elegance.** Ship the rough version; refine on data.
6. **Public commitment beats private intent.** Say the number out loud, then pay the credibility bill.

---

# 12. THE COST SIDE (documented, not whispered)

| Cost | Evidence |
|---|---|
| Systematic timeline inflation | ~94 tracked predictions: **8 on time (~9%)**, 46 outright failed `[REP]` |
| Human cost | Mass firings, rehires, fear culture, NLRB complaints, lawsuits over FSD advertising `[REP]` |
| Legal/regulatory | SEC: "funding secured" → $20M each + $41.53M investor distribution (2026) `[DOC]` |
| Balance-sheet fragility | 2008 ~$9M cash; 2018 near-bankruptcy; dependence on regulatory credits `[DOC/REP]` |
| Over-automation | "Excessive automation was a mistake… my mistake. Humans are underrated." `[2018]` |
| Promise-to-delivery gaps | Boring 155 mph → 35 mph; 1M robotaxis by 2020 → 0; FSD "unsupervised" repeatedly deferred `[REP]` |

**The honest read:** the method is extraordinarily productive at the cost of predictability and, in some periods, of the people around him. If you adopt the method, budget for both — don't pretend the second doesn't come with it.

---

# 13. THE PER-ACTIVITY CHECKLISTS (derived, executable)

**Requirement review**
- [ ] Name the human who owns it. No name → delete.
- [ ] What breaks if it disappears? Silence → delete.
- [ ] Is it physics or convention? Convention → delete or renegotiate.
- [ ] Is the number 10× or 10%? If 10%, why are we doing this?

**Design review**
- [ ] Part count, last version vs this version. Must fall.
- [ ] Which parts were deleted? If zero, we didn't try.
- [ ] Idiot index of the top 3 cost drivers.
- [ ] Which part exists only because a process exists that shouldn't?

**Production review**
- [ ] Rate per hour. Bottleneck station named.
- [ ] Days of inventory. Turns.
- [ ] Which station would a human beat a robot at? (Put the human there.)
- [ ] What did we automate before deleting?

**Org review**
- [ ] How many layers between the doer and the decider?
- [ ] Can every manager do the work they manage?
- [ ] When did the last skip-level happen?
- [ ] What did we delete this month?

**Capital review**
- [ ] Does compensation pay for milestones or attendance?
- [ ] What fraction of profit comes from something a legislature can delete?
- [ ] Cash runway at current burn, in weeks.

---

# 14. THE IMPOSSIBLE→POSSIBLE LAYER

Deleted from this file in v1.3 — it duplicated `IMPOSSIBLE-ENGINE.md` (four types, 50th-percentile rule, three-failure test, failure value). Read that file; one copy only.

---

# 15. SOURCE NOTES & STALENESS

- **Isaacson, *Elon Musk* (2023)** — the algorithm, idiot index, floor practices, Twitter.
- **Vance, *Elon Musk* (2015)** — early SpaceX cost hunting, actuator anecdote.
- **SEC DEF 14A filings 2018 & 2024–25** — compensation structure.
- **Tesla 10-K / quarterly updates** — credits, storage deployments, margins.
- **SpaceX/Jonathan McDowell trackers** — satellites, reuse counts.
- **Press reporting** — Bloomberg, Reuters, CNBC, The Guardian, Electrek for the gaps and the costs.

**Staleness rule:** every number here has a date. Anything undated in this file should be treated as **decayed**. Re-verify anything older than two quarters before you spend money on it.

**One disputed item flagged for you:** Neuralink patient count (7 vs 28 across sources, early 2026). Two credible-looking sources disagree by 4×; that is exactly the kind of number to verify at the primary source before repeating.
