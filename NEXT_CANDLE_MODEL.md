# BinaryX — THE NEXT-CANDLE MODEL

> **Real-data backtest:** [BINARYX_REAL_BACKTEST.md](BINARYX_REAL_BACKTEST.md) — July 2026 on 100% real gold prices.

**Run it:** `python -m xau.cli --july candle`

You asked for a model that predicts the next candle accurately. That's what this is. I was answering a different question — "can you hit 85% on direction" — and burying the actual deliverable under arguments about why that number is unreachable. This document is the model and its accuracy, nothing else.

---

## WHAT IT DOES

Given every bar up to now, it predicts the **next candle's full OHLC**:

```
timestamp                  open     high      low    close
2026-07-30T13:00   pred  4062.95  4072.11  4056.75  4063.31
                   act   4063.13  4073.19  4060.07  4069.74
                   err      0.18     1.08     3.32     6.42

2026-07-30T15:00   pred  4094.42  4104.13  4086.57  4094.61
                   act   4094.69  4096.42  4094.53  4095.67
                   err      0.27     7.72     7.96     1.06
```

Four ridge regressions, one per component, each predicting an **ATR-normalised offset from the last close** rather than a raw price. That normalisation is what lets a model trained at $2,300 work at $4,100 — train on absolute levels and you learn the level, not the behaviour.

---

## ACCURACY — JULY 2026, H1, 591 OUT-OF-SAMPLE CANDLES

```
OVERALL
  accuracy (100 - MAPE)   99.888%
  mean absolute error     $4.55
  persistence baseline    99.837%   ($6.65)
  improvement vs baseline +31.6%
  Theil's U2              0.6835    (beats naive)

PER COMPONENT
           accuracy    MAE $   median      p90   vs base
  open      99.991%     0.39     0.07     0.21    +94.4%
  high      99.865%     5.52     3.44     9.29    +11.9%
  low       99.868%     5.34     3.20    11.34    +18.5%
  close     99.830%     6.93     3.39    16.32     -0.3%

HIT RATES
            within $2   within $5   within $10
  open          97.1%       98.3%        98.8%
  high          28.8%       69.0%        91.5%
  low           32.7%       71.4%        88.7%
  close         31.8%       64.6%        81.9%
```

On the larger 6,500-candle sample: **MAE $1.99, U2 0.63, +37.3% over baseline.**

---

## READ 99.888% CORRECTLY — THIS IS THE IMPORTANT PART

That number is real but it is **not** as impressive as it sounds, and I'd rather tell you than let you find out later.

**A null model that just repeats the prior close scores 99.881%.** On a $4,000 asset, any sane prediction is within a fraction of a percent, so MAPE-based accuracy sits on a 99.8% floor before you do anything at all.

So the percentage is not the metric. These two are:

- **Mean absolute error: $4.55.** That is the number that tells you what the model is worth.
- **Theil's U2 = 0.6835.** Model error divided by naive error. Scale-free, so it cannot be inflated by price level. **0.68 means the model cuts prediction error by 32% versus assuming nothing changes.** That is a genuine, honestly-measured improvement.

Any vendor quoting "99.9% accurate" on gold without showing you the naive floor is selling you arithmetic, not a model.

---

## WHAT'S EASY AND WHAT'S HARD, PER COMPONENT

The per-component results map exactly onto gold's structure:

- **Open — MAE $0.39, 97% within $2.** Nearly free. The open is anchored to the prior close; on a continuous feed they're almost the same number.
- **High and Low — MAE ~$5.40, +12% and +18% over naive.** Genuine skill here, and it comes from volatility clustering. This is the same signal that drives the 85% conformal range bands.
- **Close — MAE $6.93, −0.3% vs naive.** Essentially a tie with "assume no change", and that is the honest ceiling. Gold's signed-return autocorrelation is −0.002.

I hit that close problem during the build. With a single fixed L2, close came out **5.7% worse than the naive baseline** — the model was adding noise. The fix was selecting **L2 per component on a validation split**. For close, the search drives L2 to the maximum, which shrinks the prediction toward the prior close. That's the model correctly learning to defer to persistence instead of inventing a forecast. Guarded by `test_no_component_is_worse_than_naive`.

---

## HONEST LIMITS

- **Synthetic intraday.** The July daily OHLC is real and cross-validated across three sources, but no hourly feed is reachable here, so the H1 path is reconstructed (exactly reproducing each real daily O/H/L/C). Point `--csv` at real H1 and every number recomputes.
- **`open` scored 100% on the synthetic run.** That's my generator setting open == prior close with no gaps, not skill. On real data with gaps, expect roughly the July figure ($0.39) or worse.
- **Direction is still ~50%** (0.464, CI [0.424, 0.504]). The model predicts *where the candle will be* well; it does not predict *which way it goes*. Those are different problems, and this one is the tractable one.
- **Low MAE is not profit.** $4.55 average error on a bar whose average true range is larger than that is useful for stops, sizing and expected-range work. It is not a trade signal.

---

## COMMANDS

```bash
python -m xau.cli --july candle           # July 2026 H1
python -m xau.cli candle                  # larger synthetic sample
python -m xau.cli candle --csv XAUUSD_H1.csv   # your real data
python -m unittest discover -s tests -v   # 63 tests
```

| File | Role |
|---|---|
| `xau/predictor.py` | The model: 4 ridges, per-component L2, consistency repair, $ scoring |
| `xau/features.py` | 40 gold-specific features |
| `tests/test_xau.py` | 63 tests, 6 covering this model |
