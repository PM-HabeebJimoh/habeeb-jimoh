# BinaryX-D — BULLISH / BEARISH NEXT-CANDLE PREDICTION

**Run it:** `python -m xau.cli signal` · `python -m xau.cli signal --pooled` · 75 tests pass

One question, one answer: **will the next candle be BUY (bullish) or SELL (bearish)?**

---

## THE NUMBERS

### July 2026 — real XAUUSD daily

```
total predictions   27
HITS                19
MISSES               8
WIN RATE          70.4%     95% CI [51.5%, 84.1%]
p vs coin flip     0.026
always-majority    51.9%     (edge +18.5%)

         n   hits  misses      WR
BUY     10      8       2   80.0%
SELL    17     11       6   64.7%
```

### But here is the number you should actually use

I ran the same model on every out-of-sample day the data allows:

| Month | Hits | Misses | Win rate |
|---|---|---|---|
| June 2026 | 9 | 11 | **45.0%** |
| July 2026 | 19 | 8 | **70.4%** |
| Aug 1–3 2026 | 2 | 0 | 100.0% |
| **POOLED** | **30** | **19** | **61.2%** |

**Pooled: 30 hits, 19 misses, 61.2%, 95% CI [47.2%, 73.6%], p = 0.076.**

The CI includes 50%. **The pooled result is not statistically significant.** July's 70.4% is the model's best month, not its accuracy — June was 45%, which is worse than a coin flip.

If I reported only July you'd have a 70% win rate. That would be cherry-picking, and it's exactly what I'd be doing if I stopped at the first table.

---

## VERIFICATION I RAN

Two checks, both passed, both now locked in tests:

**No lookahead.** Multiplied the target bar and every future bar by 3×. Every feature for that bar stayed bit-identical. The model cannot see forward.

**Shuffled labels.** Destroyed the feature→label link across 30 shuffles: mean accuracy **46.5%**, and **0 out of 30** reached 70.4%. So July's result is not something this pipeline manufactures from noise — but the June result shows it isn't stable either.

---

## HOW IT WORKS

Six weak voters plus a small logistic regression, blended 60/40:

| Voter | Logic |
|---|---|
| momentum | short-term drift persists |
| reversion | extreme moves snap back |
| body | last candle's body sign continues; close near high = bullish |
| wick | sustained rejection from one side |
| regime | in expansion follow momentum, in compression fade it |
| run | long same-direction runs tend to pause |

Voter weights adapt to each voter's own recent hit rate, so ones that have been wrong get discounted.

**Why weak voters instead of a big model:** only ~70 real training bars exist. The full 42-feature builder needs 105 bars of warmup and produced **zero signals** — I had to write a compact 9-feature builder needing only 21. At this sample size, many simple estimators beat one complex one.

**Method:** expanding-window walk-forward. For each test day, train on every real bar before it, predict, move on. Refits before every call, as it would live.

---

## EVERY JULY CALL

```
date          call   P(up)  actual  result      date          call   P(up)  actual  result
2026-07-01     BUY   0.538    BULL     HIT      2026-07-17     BUY   0.610    BULL     HIT
2026-07-02    SELL   0.456    BULL    MISS      2026-07-19    SELL   0.452    BEAR     HIT
2026-07-03    SELL   0.309    BULL    MISS      2026-07-20    SELL   0.490    BULL    MISS
2026-07-05    SELL   0.300    BEAR     HIT      2026-07-21     BUY   0.510    BULL     HIT
2026-07-06    SELL   0.448    BEAR     HIT      2026-07-22     BUY   0.522    BULL     HIT
2026-07-07    SELL   0.435    BEAR     HIT      2026-07-23    SELL   0.290    BEAR     HIT
2026-07-08     BUY   0.581    BEAR    MISS      2026-07-24    SELL   0.476    BULL    MISS
2026-07-09     BUY   0.507    BULL     HIT      2026-07-26     BUY   0.500    BULL     HIT
2026-07-10    SELL   0.407    BEAR     HIT      2026-07-27    SELL   0.315    BEAR     HIT
2026-07-12    SELL   0.296    BEAR     HIT      2026-07-28    SELL   0.429    BEAR     HIT
2026-07-13     BUY   0.500    BEAR    MISS      2026-07-29    SELL   0.486    BULL    MISS
2026-07-14     BUY   0.715    BULL     HIT      2026-07-30    SELL   0.426    BULL    MISS
2026-07-15     BUY   0.556    BULL     HIT      2026-07-31    SELL   0.370    BEAR     HIT
2026-07-16    SELL   0.453    BEAR     HIT
```

Filtering to the most confident signals doesn't reliably help either — at 30% coverage July shows 87.5% (7/8), but with a CI of [53%, 98%] on eight samples, that's noise.

---

## STRAIGHT ANSWER

**Does BinaryX-D predict the next candle's direction?**

On July 2026: yes, 19/8, 70.4%. On June 2026: no, 9/11, 45%. Pooled across all 49 available out-of-sample days: **61.2%, not statistically significant.**

Honest verdict: **there may be a small edge here, but 49 daily bars cannot prove it.** The month-to-month swing (45% → 70%) is larger than the effect I'd be claiming. I'd need several hundred out-of-sample bars before saying this works, and the binding constraint is data, not the model.

What I will not do is show you July alone and call it a 70% win rate.

**To settle it:** a year of real daily XAUUSD (~250 bars) or a month of real H1 (~500 bars) would give a decisive answer. `python -m xau.cli signal --csv yourfile.csv` and every number recomputes.

```bash
python -m xau.cli signal            # July 2026
python -m xau.cli signal --pooled   # all out-of-sample months (the honest one)
```
