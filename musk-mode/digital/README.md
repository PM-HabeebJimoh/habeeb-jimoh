# Nigeria health: the digital-only disruption

Date: 2026-11-15 · Status: **hypothesis, backed by market data collected today; no profit number until the tests below run.**

## One line
Own nothing physical. Build the **trust-and-price layer for Nigerian medicine** on WhatsApp and the payment apps people already use. Anyone can check whether a medicine is genuine, what it should cost, and where a verified cheaper equivalent is. Relatives abroad can pay a verified pharmacy directly for a specific prescription.

## Real market data (collected 2026-11-15, files in `data/`)

| Finding | Number | Source |
|---|---|---|
| Same molecule, brand vs generic: adult malaria course | ₦1,500 vs ₦6,750 → **4.5×** | medplusnig.com listed prices |
| Same molecule: amlodipine, one month | ₦1,000–1,400 vs ₦7,250 → **5–7×** | same |
| Largest Nigerian health apps (installs) | Reliance Care, Hygeia, MyAXA Plus, Leadway Health, DrSavealife: **100K+ each**, all but one tied to insurance membership | Google Play, gl=NG |
| Largest Nigerian money apps | OPay **50M+**, Moniepoint **10M+** | Google Play |
| DrSavealife (consumer telemedicine) | Last update **Oct 2023** | Google Play |
| Doctoora (telemedicine/clinics) | Domain now serves a betting site: **dead** | doctoora.com, fetched today |
| Reliance Health | reliancehealth.com redirects to a domain-for-sale page; app updated 12 Nov 2026: **status unclear** | fetched today |
| Healthtracka Flourish Care Plan (remote diabetes/BP care, "for your loved ones") | **₦60,000–90,000 per quarter** | booking.healthtracka.com, rendered today |
| Healthtracka home lab packages | ₦35,000–90,000 | healthtracka.com |
| WellaHealth | Repositioned as "embedded healthcare: HMO & pharmacy fulfilment for businesses" | wellahealth.com |

## What the data says
1. **Nigerians are digital with money, not with health.** Money apps reach 50M+ installs; the best health apps reach about 100K+. That is a gap of roughly 100–500×. A new standalone health app is the wrong vehicle. **Delete the app.** Ride WhatsApp and the payment apps people already open daily.
2. **The price gap is trust, not cost.** People pay 4.5–7× for a brand of the same molecule because they can't tell which generic is real. Information can close that gap without owning a single shop.
3. **Remote chronic care already exists and is priced** (Healthtracka, ₦60–90k a quarter). Copying it is not a disruption. Digital consult apps have died or stalled (Doctoora, DrSavealife). Selling consultations is not the gap.

## Gate 0 (Musk)
- **Goal as a physical quantity:** every Nigerian pays the verified-generic price, not the brand-fear price, for the same molecule, and knows if a pack is genuine before paying. Measured spread today: 4.5–7×.
- **Type of impossibility:**
  - **Type 2 (capability):** no national medicine price and quality dataset exists. We build it from scrapes, receipts and lab-tested batches.
  - **Type 4 (permission):** only NAFDAC can declare a product genuine. We may only say "verified by NAFDAC's authentication code" or "this batch passed lab test X". Payments run through a licensed partner. Health data falls under the Nigeria Data Protection Act 2023.
  - **Not Type 3:** there is nothing to manufacture.
- **Floor:** the cost of information. Price data costs scraping plus user receipts, which is near zero. Quality data costs lab assays per batch; that price is unknown, so get quotes.
- **Failure value:** bounded. The only unbounded risk is telling someone a fake is safe. Never assert quality we didn't measure.

## The Algorithm
1. **Requirements with owners:** authenticity claims are owned by NAFDAC; payments by CBN through a licensed partner; data by NDPA. Everything else is negotiable.
2. **Delete:** shops, clinics, warehouses, delivery fleet, salaried doctors, inventory, a standalone app.
3. **Simplify:** one WhatsApp number. Send a photo of a pack or prescription and get back: genuine/unknown, fair price, a cheaper verified equivalent, and where to buy it.
4. **Accelerate:** the bottleneck is coverage of the price dataset. Weekly scrapes of every online pharmacy, plus every user receipt.
5. **Automate last:** OCR and automatic matching only after a human-run version has handled the first 1,000 checks.

## Buffett checks
- **Moat:** a data network effect. Every receipt and scan makes the price/quality map better, and a trust brand grows if the layer is never wrong. Weakness: low switching costs, so trust is everything.
- **Capital:** asset-light. No inventory, no stores, no fleet. Most failed Nigerian health startups (mPharma layoffs, 54gene) were capital-heavy.
- **FX:** relatives abroad pay in pounds or dollars and costs are in naira, so a weaker naira helps instead of killing us.
- **Circle of competence:** needs one pharmacist partner for product matching and one payments partner.
- **Inversion: how it dies:**
  - It calls a fake "verified" and someone is harmed.
  - Pharmacies fight price transparency. Counter: verified pharmacies get the customers.
  - NAFDAC builds the same thing.
  - People don't care enough to check.
- **Earnings:** none projected. Revenue hypotheses to test:
  1. A fee per order from verified pharmacies.
  2. A fee on relatives' direct payments.
  3. Quality generic makers paying for verified listing.

## Rejected alternative
**Diaspora-paid remote chronic care.** It already exists (Healthtracka ₦60–90k/quarter, Clafiya caregivers, Mobihealth "diaspora healthcare"). It isn't 10×; it's a me-too.

## Real-market tests (digital, 30 days, real people and real money)
The thresholds are decision rules set in advance, not data.

| # | Test | How | Kill if |
|---|---|---|---|
| T1 | Do people want to check medicines? | WhatsApp number posted in 10 Nigerian community/family groups; answer every check by hand | < 100 unique checks in 14 days, or < 20% come back |
| T2 | Is the spread real across the market? | Weekly scrape of 3+ online pharmacies + 200 receipt photos from users | Median brand/generic spread < 2× |
| T3 | Are cheap generics actually good? | Buy the 20 cheapest generics online; send to a lab | If lab cost per batch makes testing impossible → drop quality claims, keep only NAFDAC-code checks |
| T4 | Will relatives abroad pay a pharmacy directly? | One page: "pay mum's prescription at a verified pharmacy"; take refundable deposits | < 10 deposits from 500 visitors |
| T5 | Do people switch when shown a verified cheaper equivalent? | Track orders through 3 partner pharmacies | < 20% switch |

## Next physical action (this week)
Set up a WhatsApp Business number. Post one message in 10 groups you belong to: "Send a photo of any medicine. I'll tell you if NAFDAC can verify it, what it should cost, and whether a cheaper verified version exists." Answer every message yourself. Log each check in a spreadsheet: drug, price paid, where, verified or not.
