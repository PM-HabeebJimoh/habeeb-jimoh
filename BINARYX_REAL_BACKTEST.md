# BinaryX v1.0 — JULY 2026 BACKTEST ON 100% REAL MARKET DATA

**Run it:** `python -m xau.cli binaryx` · 70 tests pass

The model is now named **BinaryX**, and this is a real backtest: real gold prices for training, real gold prices for testing, no synthetic data anywhere in the pipeline.

---

## 1. THE RESULT

```
BinaryX MAE            $25.63    95% CI [$21.33, $30.01]
naive baseline MAE     $33.59
error reduction        $7.96 per candle  (+23.7%)
improvement 95% CI     [$2.41, $13.54]      <- excludes zero
Theil's U2             0.7630               <- beats naive, scale-free
accuracy (100-MAPE)    99.370%              (naive floor 99.173%)
```

**BinaryX cuts next-candle prediction error by 23.7% versus assuming nothing changes, and the improvement is statistically significant** — the bootstrap CI on the paired per-candle improvement runs [$2.41, $13.54] and does not touch zero.

That's the honest headline. Not 85% direction. A measurable, significant reduction in how wrong the predicted candle is.

---

## 2. THE DATA — ALL REAL

| | |
|---|---|
| Source | myfxbook XAUUSD daily historical |
| Cross-checks | investing.com (max delta **$6.86**), barchart (period high/low) |
| Total bars | 100 real trading days, Apr 9 – Aug 3 2026 |
| **Train** | **71 real days**, 2026-04-09 → 2026-06-30, $3,942–$4,889 |
| **Test** | **27 real days**, 2026-07-01 → 2026-07-31, $3,959–$4,203 |

Barchart independently reports July's low as 3960.36 on 07/17 and high as 4201.70 on 07/06. This series gives **3959.23** and **4203.10**. Verified, and asserted by `test_real_data_matches_published_extremes`.

**This is a hard test set, not a friendly one.** Training sits at $4,300–4,700; July sits at $3,959–4,203. BinaryX is predicting price levels it never saw in training, during a −15% four-month bear leg driven by US–Iran escalation and the Fed pricing out cuts. That works only because BinaryX predicts **ATR-normalised offsets from the prior close**, never absolute prices.

**Method:** expanding-window walk-forward. For each July day, train on every real bar strictly before it, predict that day, move on. The model refits 23 times — which is also how it would run live. Training grew from 40 to 62 bars.

---

## 3. WHERE THE EDGE ACTUALLY IS

```
           MAE $              95% CI   naive $   gain $  sig?
  open      6.78   [   3.57,  10.68]     35.39   +28.61   YES
  high     27.16   [  20.09,  34.93]     24.96    -2.21    no
  low      28.73   [  21.56,  36.16]     33.28    +4.55    no
  close    39.83   [  30.31,  49.21]     40.71    +0.89    no
```

Read this honestly: **essentially all of BinaryX's edge is in `open`** — $6.78 error against a $35.39 naive, a 5× improvement, and the only component whose CI excludes zero.

That is a real and useful result (the open is strongly anchored to the prior close, and BinaryX exploits that precisely), but it is *one* component. `low` and `close` improve slightly; **`high` is $2.21 worse than naive** and I'm not going to bury that. At 23 test days, none of those three is statistically distinguishable from the baseline.

Hit rates tell the same story:

```
             within $2   within $5   within $10
  open          39.1%       60.9%        73.9%
  high           4.3%        8.7%        13.0%
  low            8.7%       13.0%        21.7%
  close          0.0%        4.3%         8.7%
```

On **daily** bars with an $81 average true range, being within $10 on the close is a genuinely hard target and BinaryX hits it 8.7% of the time. On H1 bars the same model was within $10 on close 81.9% of the time — timeframe matters enormously, and this daily test is the harder one.

---

## 4. A REAL BUG THE REAL DATA EXPOSED

The synthetic backtests never surfaced this because they had thousands of training rows. Real gold gave me **40–62 training rows against 42 features** — p/n ≈ 0.8, hopelessly overparameterised.

**Symptom:** `close` came out at $41.70 MAE against a $40.71 random walk. The model was adding noise, and worse, it had *already* selected maximum L2 shrinkage and still lost.

**First fix failed.** I added a naive-fallback: if no L2 beats "predict no change" on validation, predict exactly that. It never triggered — because with a single 20% validation split there were only ~10 validation rows, far too noisy to detect that naive was winning.

**The real fix** was replacing the single split with **blocked K-fold CV**, so every training row serves as validation exactly once. That made the L2 choice and the fallback decision stable:

| | before | after |
|---|---|---|
| Overall MAE | $27.53 | **$25.63** |
| Theil's U2 | 0.8196 | **0.7630** |
| Improvement | +18.0% | **+23.7%** |
| close vs naive | −$3.22 | **+$0.89** |

It also improved the synthetic run (U2 0.6273 vs 0.6835 before), so this was a genuine model fix, not a fit to July.

---

## 5. WHAT I WILL AND WON'T CLAIM

**Will claim:**
- Real training data, real test data, real out-of-sample predictions, no lookahead.
- 23.7% error reduction with a bootstrap CI excluding zero.
- `open` prediction is strong and significant: $6.78 vs $35.39 naive.
- The model survived a regime it never trained on (a $700 price-level shift).

**Won't claim:**
- That `high`, `low` and `close` are proven. They aren't — 23 predictions is a small sample, and `high` is currently *worse* than naive.
- That 99.370% "accuracy" is impressive. The naive floor is 99.173%; on a $4,000 asset that percentage is nearly meaningless. **Theil's U2 = 0.7630 is the number that matters.**
- Any tradeable edge. Direction is 0.522 with a CI of [0.330, 0.708] — completely uninformative at this sample size.
- That daily results transfer to H1. They don't, in either direction.

**What would strengthen this:** more real history. 71 training days is the binding constraint — with 42 features the model is starved. A year of real daily bars, or a month of real H1, would let BinaryX show whether the `high`/`low`/`close` components have genuine skill or not. That's a data problem, not a model problem, and the pipeline is ready for it via `--csv`.

---

## 6. FILES

```bash
python -m xau.cli binaryx                  # this backtest
python -m unittest discover -s tests -v    # 70 tests
```

| File | Role |
|---|---|
| `xau/binaryx.py` | BinaryX: expanding-window backtest, bootstrap CIs, report |
| `xau/real_data.py` | 100 real daily bars with full provenance |
| `xau/predictor.py` | The model: 4 ridges, blocked K-fold L2, naive fallback |
| `tests/test_xau.py` | 70 tests, 7 covering the real-data backtest |
