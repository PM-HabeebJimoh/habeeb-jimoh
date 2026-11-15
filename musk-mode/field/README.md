# Field data kit: Nigeria health market

**Rule:** no consultant reports, no market-size estimates, no projections. Every number that decides this business comes from shelves, sales books, customers and lab tests that we collect ourselves.

- **Musk:** go to the floor. The location is the information.
- **Buffett:** scuttlebutt. In 1964 he checked Omaha restaurants and shops to see if people still used American Express before he bought the stock. Phil Fisher called this method "scuttlebutt".

## What we already know from measured data (not consultants)

| Fact | Value | How it was measured |
|---|---|---|
| Listed price, adult malaria course (artemether-lumefantrine) | ₦1,500 (generic Cevlar) to ₦6,750 (Coartem 80/480): **4.5× brand premium** | Collected 15 Nov 2026 from medplusnig.com, a Lagos online pharmacy (`data/online_prices_medplusnig_2026-11-15.csv`) |
| Listed price, amlodipine 10 mg × 28 | ₦1,000–1,400 generics vs ₦7,250 for brand Lofral 5 mg × 30: **5–7× brand premium** | Same source |
| PPMV shelf price of a WHO-prequalified adult ACT course | Median ₦600 (Kano) – ₦900 (Abia); ₦700 at Lagos PPMVs vs ₦4,800 at Lagos pharmacies | ACTwatch Lite 2024 outlet census (PSI), ~4,700 outlets in Abia, Kano, Lagos |
| Wholesale price of artemether-lumefantrine | ₦700–1,300 | Same census |
| PPMVs with any malaria test in stock | **Abia 0.1%, Lagos 0.4%, Kano 31%** | Same census |
| Malaria test price to the customer | Lagos ₦2,000 (retail median), Abia ₦1,500, Kano ₦300. In Abia/Lagos the test costs as much as or more than the drug | Same census |
| RDT wholesale price | ₦120 (Kano) – ₦300 (Lagos) | Same census |
| PPMV share of antimalarials sold | Abia 81%, Kano 74%, Lagos 29% (pharmacies 64% in Lagos) | Same census |

**What this kills:** my earlier plan priced a malaria test-and-treat at ₦3,000. Real PPMV prices for the drug alone are ₦600–900. That plan would have been 3–5× more expensive than the market. The real gaps are **(1) testing**, which costs more than the drug in the south so nobody tests, and **(2) the brand-trust premium**, where people pay 4.5–7× for brands because they can't tell which generics are real.

**Caveat:** the online prices come from one Lagos website and are not street prices. ACTwatch covers 3 states in 2024. Both are leads for what to measure, not conclusions.

## The 12 numbers that decide the business

| # | Number | Form | Kills the idea if |
|---|---|---|---|
| 1 | Adult malaria course shelf price, by outlet type | `price_basket` | — (baseline) |
| 2 | Brand ÷ generic price, same molecule | `price_basket` | < 2× → no trust premium to capture |
| 3 | Brand share of units sold | `price_basket` | < 20% → arbitrage too small |
| 4 | % of outlets offering a malaria test, and test price | `outlet_audit`, `mystery_shop` | ≥ 30% already test → no testing gap |
| 5 | Fevers per outlet per day (2-hour count + owner estimate) | `outlet_audit` | < 3 → no shop-based model works |
| 6 | Blood-pressure refills per outlet per week | `outlet_audit` | < 7 → chronic model too thin |
| 7 | Outlet gross margin on the basket | `price_basket` | — (tells you what owners will accept) |
| 8 | % of bought samples failing a quality check | `quality_samples` | < 10% fail → "verified" sells nothing |
| 9 | Customer spend per visit | `exit_interview` | — (sizes the wallet) |
| 10 | % who would switch to a tested generic at half the brand price | `exit_interview` | < 40% → no switching |
| 11 | Wholesaler credit days and minimum order | `wholesaler` | — (sets working capital) |
| 12 | % of visits paid with money from family abroad | `exit_interview` | < 15% → no diaspora payer |

`scripts/analyse.py` computes all 12 from the filled forms and prints ALIVE / DEAD / NO DATA for each hypothesis. It refuses to print a number with fewer than 10 observations.

## The four hypotheses the field data decides
- **H1 Trust arbitrage:** verified, batch-tested generics sold at generic prices take share from brands.
- **H2 Test-before-treat:** a cheap test (RDT costs ₦120–300 wholesale) bundled so testing is no longer more expensive than guessing.
- **H3 Chronic BP control:** monthly refills plus BP checks for the patients who stop on price.
- **H4 Diaspora payer:** family abroad pays for parents' chronic care (CBN: remittances were $21.8B in 2025).

**Profit is calculated only after this data exists.** No projection before it.

## Sampling (2 weeks, 2 contrasting areas)
Start where you live, and add one contrasting area. ACTwatch shows Lagos (pharmacy-led) and Kano (PPMV-led, more testing) behave differently.

| Per area | Count |
|---|---|
| Outlets audited (random walk from 3 start points; every outlet on the route) | 60: ~40 PPMVs, 15 pharmacies, 5 clinics/labs |
| 2-hour observation counts | 20 outlets |
| Exit interviews | 100 |
| Mystery shops (3 scripts × 10) | 30 |
| Wholesalers (open market + licensed) | 10 |
| Samples bought for quality testing (brand and generic AL and amlodipine) | 40 |

## How to collect
- Put the CSV headers into **KoboToolbox** (works offline on a phone) or Google Forms. Export to CSV with the same column names.
- **Mystery shopping:** buy, don't consume. Keep every pack for the quality test. No fake symptoms involving a real child. Describe the child's symptoms.
- **Quality:** check the NAFDAC Mobile Authentication scratch code where the pack has one. Get quotes from at least 2 labs for assay testing (the price per sample is unknown, so record it).
- **Consent:** ask before every exit interview, record nothing that identifies the person, and stop if asked.

## Weekly price tracker
`scripts/collect_online_prices.sh` re-collects listed online prices for the tracer basket (polite, one request every 2 seconds). Run it weekly to watch brand/generic spreads and inflation.

## Order of work
1. **Day 1–2:** load forms into Kobo, train 2 collectors on 5 outlets each, fix the forms.
2. **Day 3–10:** collect.
3. **Day 11:** send samples to the lab.
4. **Day 12–14:** run `analyse.py`. Read the verdicts. Only then design the business.
