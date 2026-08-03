# EXHAUSTIVE RULE SEARCH — CAN ANYTHING BEAT 85% ON NEXT-CANDLE DIRECTION?

**Reproduce:** `python -m xau.cli mine` · `python -m xau.cli mine --edge 0` · 57 tests pass

You asked me to check every angle and run hundreds of formulas. I built **404 rules × 8 target formulations = 3,232 hypothesis tests**, with Bonferroni, Benjamini-Hochberg FDR control, and White's Reality Check.

**I found rules above 85%. Every one of them is either not a direction prediction, or not real. Here is the proof, including the experiment that would have let me claim victory if I'd stopped early.**

---

## 1. WHAT WAS SEARCHED

| Family | Count | Examples |
|---|---|---|
| Single-feature thresholds | 232 | `mom_10>0.8`, `close_loc<=0.25`, `squeeze>0.35` |
| Two-feature interactions | 80 | `(nr_rank<0.2)&(squeeze>0.3)` |
| Session-conditional | 50 | `overlap & range_pctile>0.8 → long` |
| Triple conditions | 20 | `overlap & nr_rank<0.2 & mom_10>0.3` |
| Session bias | 10 | `london_long`, `asia_short` |
| Classic TA patterns | 8 | pin bars, NR7 breakout, gap fade, exhaustion |
| Sweep patterns | 4 | liquidity sweep fade / follow |

Across 8 target formulations, because *"direction of the next candle"* is not one question — and the answer depends entirely on which one you mean.

---

## 2. THE HEADLINE TABLE (realistic data)

```
target                         base    best      n   CIlo  BH    RCp  tradeable
dir_open_close                0.508  0.7185    238  0.658  10  0.000   YES
dir_close_close               0.508  0.7185    238  0.658  10  0.000   YES
high_gt_prev_close            1.000  1.0000   4702  0.999 184  0.000   no
low_lt_prev_close             1.000  1.0000   4702  0.999 184  0.000   no
barrier_0.25up_2.0dn_8        0.947  0.9856    278  0.964 184  0.000   YES
barrier_0.5up_3.0dn_12        0.918  0.9748    159  0.937 184  0.000   YES
barrier_1.0up_1.0dn_6         0.526  0.7273    198  0.661  84  0.000   YES
range_gt_half_atr             0.709  0.9240    789  0.903 174  0.000   no
```

At face value: **71.85% on classic direction, 98.56% on a barrier target.** Both far past 85% in the barrier case, and both with Reality Check p = 0.000.

If I stopped here, you'd have your 85%. Four further experiments say don't.

---

## 3. FALSIFICATION #1 — THE SAME SEARCH ON PURE NOISE

I re-ran the **identical 404-rule search** on data with **provably zero** directional edge (`edge=0.0`, a martingale by construction).

```
data                    best acc      n   CIlow  BHsurv    RC p
martingale edge=0         0.5840    125   0.496       0   0.262
martingale seed 2         0.6392     97   0.540       0   0.029
realistic edge=0.35       0.6388    299   0.583       2   0.008
```

**The martingale scored 63.92%. The "real" data scored 63.88%.** Identical, and the noise run was *higher*.

Across ten independent noise seeds:

```
seed 50: 0.5694    seed 55: 0.6220
seed 51: 0.5972    seed 56: 0.5714
seed 52: 0.5625    seed 57: 0.6027
seed 53: 0.6022    seed 58: 0.5698
seed 54: 0.5681    seed 59: 0.5811
                   mean 0.5846, max 0.6220
```

**Searching 404 rules on pure noise routinely produces 58–64% "accuracy."** That is the null distribution of the maximum. Any mined direction rule in that band is a search artifact, full stop. This is now locked in `test_best_of_search_on_noise_is_high`.

This is how essentially every 85%-accuracy trading product is manufactured. Not usually by fraud — by searching hard and reporting the maximum.

---

## 4. FALSIFICATION #2 — THE FAIR-ODDS CONTROL BROKE

I included a symmetric barrier (`+1.0 / −1.0 ATR within 6 bars`) as a control. By construction it *must* be ~50%. Its base rate measured **0.5021** on zero-edge data — correct.

But the best mined rule on it scored **72.73%**, with 84 rules surviving BH correction and Reality Check p = 0.000.

**A fair coin cannot be predicted at 72.7%.** When your control breaks, your methodology is broken — the corrections are being overwhelmed because the rules are heavily correlated (they share features), which violates the independence Bonferroni and the Reality Check assume. Correlated hypotheses are the failure mode that defeats standard multiple-testing correction.

---

## 5. FALSIFICATION #3 — THE 100% TARGET WAS DEGENERATE

`high_gt_prev_close` scored **100.0000% on 4,702 samples**. Perfect accuracy is always a bug.

It was: my synthetic generator sets each bar's open exactly equal to the prior close (no gaps). So `high ≥ open == prev_close` is a **tautology**. Verified: base rate exactly 1.0.

On real gold this target runs ~75–85% — genuinely high, and genuinely useless, because knowing the high gets touched tells you nothing about where you exit.

---

## 6. FALSIFICATION #4 — THE BARRIER TARGETS, AND THE MOST IMPORTANT NUMBER HERE

The asymmetric barriers are the one place >85% is *real*. On **zero-edge** data:

```
barrier                      base rate on pure noise
+0.25 / −2.0 ATR in 8            0.9443
+0.5  / −3.0 ATR in 12           0.9205
+0.25 / −4.0 ATR in 16           0.9772
+0.1  / −3.0 ATR in 10           0.9893
```

**97.7% accuracy on a martingale.** No prediction involved — a small upside target is simply hit before a distant downside one, by geometry. You can dial the accuracy to any number you want by widening the stop. That's how "98% win rate" systems are built.

Then I ran full trade accounting, and initially got **positive EV** (+0.07 ATR/trade) on zero-edge data — impossible, so a bug. Two rounds of digging:

1. Ambiguous bars (both barriers touched in one bar) were being discarded rather than resolved. Fixed with a 50/50 coin flip. EV fell but stayed positive.
2. **The real cause:** intrabar path artifacts in the generator. Testing barriers on **closes only**, where high/low placement cannot interfere:

```
barrier                    acc   EV/trade
+0.25/−2.0 in  8        0.8259    -0.2449
+0.5 /−3.0 in 12        0.8514    -0.2465
+0.25/−4.0 in 16        0.9133    -0.3380
```

**91.33% accuracy. −0.34 ATR per trade.** That is the entire lesson of this exercise in one line: you win small 91% of the time and lose enormous 9% of the time. Locked in `test_close_only_barrier_has_negative_ev`, which asserts accuracy > 75% **and** EV < 0 simultaneously.

---

## 7. WHAT I ACTUALLY FOUND

**The honest answer to "can you beat 85% on next-candle direction?" is no**, and the search made that stronger rather than weaker:

| Claim | Verdict |
|---|---|
| 71.85% on classic direction | ❌ Noise search produces 58–64%; the fair-odds control hit 72.7% |
| 100% on high>prev_close | ❌ Tautology in the generator |
| 98.56% on asymmetric barrier | ⚠️ **Real accuracy, negative expectancy** — 91% accurate at −0.34 ATR/trade |
| 92.4% on range>0.5 ATR | ✅ Real, but that's **volatility**, not direction — consistent with the 85.12% conformal result |

The one target where high accuracy is both real *and* survives scrutiny is the volatility/range family — exactly what the conformal system already delivers at 85.12%, and exactly what the AC(1) measurements predicted before any of this search: signed-return autocorrelation −0.002, absolute-return autocorrelation +0.21.

**Every road leads back to the same place.** I attacked it from 3,232 directions and the structure didn't move.

---

## 8. WHY I'M CONFIDENT THIS IS THE LIMIT, NOT MY LIMIT

The strongest evidence isn't that I failed to find an edge. It's that **I found several, and each one dissolved under a test that a motivated seller would simply not run**:

- Re-running the search on data that provably has no edge
- Including a fair-odds control and believing it when it broke
- Checking whether a 100% result was too good to be true
- Converting accuracy into expectancy

Those four checks are the difference between this document and a product page. If you take one thing from this work, take the close-only barrier table: **91% accurate, −0.34 ATR per trade.** Accuracy and profitability are different quantities, and anyone selling you the first is hoping you won't ask about the second.

**Real caveat:** this is synthetic data. Real gold could contain a genuine directional pattern my generator doesn't reproduce. But the falsification framework here is the thing that transfers — point it at real H1 data via `--csv` and it will tell you the truth about that data the same way.

```bash
python -m xau.cli mine              # the full search
python -m xau.cli mine --edge 0     # the same search on provable noise
python -m unittest discover -s tests -v
```
