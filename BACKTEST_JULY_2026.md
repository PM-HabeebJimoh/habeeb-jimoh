# XAU-Q BACKTEST — JULY 2026, H1 TIMEFRAME

**Reproduce:** `python -m xau.cli july` · **Tests:** `python -m unittest discover -s tests` (51 pass)

---

## 0. THE HEADLINE, INCLUDING THE BAD PART

The system **missed its 85% target on July 2026 H1 data**, and the miss is the most useful thing this run produced.

| Metric | July 2026 H1 | Main evaluation (n=5,250) |
|---|---|---|
| Range coverage (target 85%) | **82.13%** — CI [78.9, 85.0] | 85.12% — CI [84.1, 86.1] |
| Next-bar HIGH in band | 83.44% | 92.34% |
| Next-bar LOW in band | 85.25% | 92.48% |
| Joint (both) | 76.07% | 86.67% |
| Skill vs naive ATR | **−31.0%** | +15.7% |
| Daily roll-up vs **real** prices | 15/27 = 55.6% | — |

The 85% target sits exactly on the upper bound of the coverage CI, so this is a genuine shortfall, not noise. **Diagnosing it found a real bug in the conformal layer** (§4) that had been inflating coverage in the main evaluation too.

---

## 1. WHAT IS REAL HERE AND WHAT IS NOT

This matters more than any metric below.

**REAL — the daily OHLC.** All 30 daily bars (June 28 → July 31) are transcribed from published market data and cross-validated across three independent sources:

- **myfxbook** (primary) · **investing.com** (cross-check) · **barchart** (period high/low)
- Maximum inter-source disagreement on any OHLC field: **$6.86** — normal spot-gold broker dispersion
- Barchart independently reports July's low as 3960.36 on 07/17 and high as 4201.70 on 07/06. This series gives **3959.23 on 07/17** and **4203.10 on 07/06**. The month verifies end to end.

**NOT REAL — the intraday path.** No hourly XAUUSD feed is reachable from this sandbox. `synthesize_h1()` expands each real daily bar into 23 hourly bars **constrained to reproduce that day's true open, high, low and close exactly** — verified to **$0.00 error on all four fields across all 30 days**, asserted by `test_h1_reproduces_real_daily_ohlc_exactly`.

So:

- ✅ **Valid** — anything aggregating to a daily property: true ranges, the volatility regime, the monthly span, gap structure. The daily roll-up in §3 compares against real prices.
- ❌ **Invalid** — real hourly microstructure, genuine H1 autocorrelation, actual intraday sweeps.

**The H1 direction result (48.69%) is therefore meaningless and is not reported as a market finding.** It measures the ordering of a reconstruction. The report labels it in red and says so.

---

## 2. JULY 2026 MARKET CONTEXT (real)

```
trading days      27
open → close      $4,011.95 → $4,048.67   (+0.92%)
high / low        $4,203.10 (Jul 6) / $3,959.23 (Jul 17)   $243.87 span, 5.9%
mean daily TR     $81.17          max daily TR  $155.97
up / down days    14 / 13   (51.9% up)
```

A six-week consolidation straddling the 4074–4112 pivot zone; the July opening range never broke (forex.com, 1 Aug 2026). Backdrop: US–Iran escalation, Fed repricing toward a possible hike, gold ~25% below its January 2026 record of $5,595.

Note the up-day fraction: **51.9%**. Twenty-seven coin flips. This is the direction problem in miniature — a month of real gold gives you almost no directional signal to learn from.

---

## 3. THE EXTERNALLY VALID TEST — DAILY ROLL-UP

H1 bands aggregated per day, compared against **real** daily highs and lows:

**15 of 27 days contained = 55.6%, CI [37.3%, 72.4%]**

```
date          real H    real L    band H    band L   ok
2026-07-01   4115.56   3959.59   4089.98   3963.10   NO   <- both ends missed
2026-07-05   4201.54   4177.94   4209.01   4164.74   yes
2026-07-06   4203.10   4128.56   4221.46   4145.24   NO   <- month high day
2026-07-13   4103.38   3986.60   4102.90   3988.79   NO   <- missed by $0.48
2026-07-17   4023.95   3959.23   4025.73   3946.49   yes  <- month low captured
2026-07-22   4166.19   4076.62   4177.23   4061.55   yes
2026-07-31   4106.28   4020.99   4133.69   4050.06   NO
```

Two observations worth more than the aggregate. **July 13 missed by $0.48** — a rounding-distance failure on a $4,100 instrument. And the misses cluster on **high-range days**: July 1 ($156 TR, the month's largest), July 6 (the month high), July 29 ($121 TR). The bands are systematically too narrow exactly when the market moves most, which is the failure mode that matters and the one §4 explains.

---

## 4. THE BUG THIS RUN FOUND

Diagnosing the coverage shortfall exposed a defect in the conformal layer that was present in the main evaluation too.

**Symptom:** July H1 coverage came in at **79.8%** against an 85% target, stable across four different fold configurations (600/250, 400/200, 300/150, and 2600-bar warmup). Stability across configs ruled out small-sample noise.

**First hypothesis — regime mismatch — was wrong.** Warmup ATR was $13.36 against July's $6.77, a 2× mismatch. I rescaled the warmup generator to match ($7.23 vs $6.77) and coverage got **worse**: 77.4%. Recording this because it would have been easy to ship the rescale as "the fix" and never notice it did nothing.

**Isolating the real cause.** Running split-conformal directly on the H1 true-range series with a constant predictor gave **89.6%** coverage. The conformal mathematics was fine. So the defect had to be in how the scale divisor was applied.

**The actual bug.** `walkforward.py` normalised residuals by `max(0.35, abs(prediction))`. That makes intervals adaptive — tight in quiet regimes, wide in violent ones — but it only preserves exchangeability if model error is *proportional to the model's own prediction*. When the ridge under-predicts on a fat-tailed target, the normalised residual distribution shifts between calibration and test, and **the conformal guarantee is void.** Setting the scale to a constant restored coverage to **83.4%** immediately.

**The fix** blends mostly-constant with lightly-adaptive scaling, with the adaptive component clamped to [0.5, 2.0] so a bad point prediction cannot distort the divisor:

```python
sca = [0.75 + 0.25 * clamp_scale(abs(p) / cal_scale) for p in rca_pred]
```

July coverage improved 79.8% → **82.13%**, and critically the main evaluation held at **85.12% with +15.7% skill** — verified by `test_main_evaluation_not_regressed_by_scale_fix`. The remaining 3-point July gap is honest: 610 predictions with a 250-bar calibration block cannot pin a quantile as tightly as 5,250 with 700.

---

## 5. WHY SKILL IS −31% (and why that number is misleading in *both* directions)

The naive baseline assumes next bar's true range equals ATR(14). On a **reconstructed** intraday path the bar-to-bar TR sequence is smooth by construction, which makes ATR(14) an unusually strong predictor. The baseline is inflated, not the model degraded.

But I won't use that to dismiss the result. The correct reading is that **−31% skill on reconstructed intraday data tells you nothing reliable about real H1 skill**, in either direction. The only defensible skill measurement in this package remains the +15.7% from the main evaluation, and that is on synthetic data too.

---

## 6. WHAT I WOULD AND WOULD NOT CLAIM FROM THIS RUN

**Would claim:**
- The daily data is real and verified against three sources.
- The H1 reconstruction is exact to $0.00 against real daily OHLC.
- The conformal scale bug was real, is fixed, and is now regression-tested.
- July 2026 gold moved +0.92% with 51.9% up days — a directionally uninformative month.

**Would not claim:**
- That 82.13% is the system's true H1 coverage. It is coverage on a reconstructed path with a small calibration block.
- Anything at all about H1 direction.
- That −31% skill reflects real intraday performance.

**What would settle it:** one month of real H1 XAUUSD (≈690 bars, free from Dukascopy or any MT5 export) run through `python -m xau.cli evaluate --csv XAUUSD_H1_202607.csv`. Every number recomputes and the reconstruction caveat disappears entirely. That is a five-minute job the moment a file is available.

---

## 7. FILES

| File | Role |
|---|---|
| `xau/july2026.py` | Real daily OHLC + provenance + H1 reconstruction bridge |
| `xau/backtest_july.py` | July driver, daily roll-up, report formatter |
| `xau/walkforward.py` | Conformal scale fix (§4) |
| `tests/test_xau.py` | 6 new July regressions incl. the exactness assertion |

```bash
python -m xau.cli july              # the report above
python -m xau.cli july --json       # machine-readable
python -m unittest discover -s tests -v
```
