"""Synthetic XAUUSD generator — the honest stand-in for blocked market data.

WHY THIS EXISTS AND WHAT IT IS NOT
-----------------------------------
This sandbox has no egress to Stooq, Yahoo, Dukascopy or any broker feed, and
cannot install yfinance. So the pipeline is validated against a generator that
reproduces gold's *documented stylised facts* — and nothing more.

WHAT IT REPRODUCES (each one is a measured property of real XAUUSD):
  1. Near-zero signed-return autocorrelation      (efficient at the mean)
  2. Strong ABSOLUTE-return autocorrelation        (GARCH-type vol clustering)
  3. Fat tails, excess kurtosis ~5-9               (Student-t innovations)
  4. Session-dependent volatility multipliers      (Asia 0.65x, overlap 1.55x)
  5. Range/close-range ratio distribution          (intrabar path realism)
  6. Occasional jumps on the US data calendar      (Poisson jump component)
  7. Weak, unstable mean reversion after sweeps    (the only directional edge)

WHAT IT CANNOT REPRODUCE, and therefore what this backtest CANNOT prove:
  - Real regime shifts (2013 taper, 2020 COVID, 2022 hiking cycle)
  - True macro dependence (real yields, DXY, ETF flows, central-bank buying)
  - Genuine microstructure (order-book depth, spread widening in stress)
  - The actual, unknown level of directional predictability in real gold

CRITICAL HONESTY NOTE
---------------------
Property 7 is a deliberately INJECTED edge with a tunable strength. On synthetic
data the direction model will find it, and directional accuracy will look better
than real gold almost certainly is. That is a feature of the harness, not a
claim about markets: it lets us verify the machinery detects an edge WHEN ONE
EXISTS, and — with `edge=0.0` — verify it correctly reports ~50% when one does
not. Both runs are reported. Never quote the edge>0 number as a market result.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

from .core import Bar, Session, session_of

UTC = timezone.utc

SESSION_VOL = {
    Session.ASIA: 0.65,
    Session.LONDON: 1.30,
    Session.OVERLAP: 1.55,
    Session.NEWYORK: 1.15,
    Session.LATE: 0.55,
}


def generate(
    n: int = 12000,
    start: datetime | None = None,
    minutes: int = 60,
    s0: float = 2350.0,
    seed: int = 42,
    edge: float = 0.35,
    jump_prob: float = 0.0008,
) -> list[Bar]:
    """Generate n bars of synthetic XAUUSD with gold-like stylised facts.

    `edge` scales the injected post-sweep mean-reversion tendency:
      edge=0.0  -> a martingale; the correct answer for direction is ~50%
      edge=0.35 -> a modest, realistic-magnitude exploitable pattern
    """
    rng = random.Random(seed)
    ts = start or datetime(2021, 1, 4, 0, 0, tzinfo=UTC)
    bars: list[Bar] = []

    # GARCH(1,1)-ish latent volatility in log-return units per bar.
    base_var = (0.0016) ** 2
    var = base_var
    # a+b = 0.94: strong clustering but comfortably stationary. At 0.98 the
    # unconditional kurtosis explodes past 30, far above real gold's 5-9.
    omega, a, b = base_var * 0.10, 0.05, 0.85

    px = s0
    recent_highs: list[float] = []
    recent_lows: list[float] = []
    pending_reversion = 0.0

    while len(bars) < n:
        # Skip the weekend gap: gold closes ~21:00 UTC Fri, opens ~22:00 Sun.
        if ts.weekday() == 5 or (ts.weekday() == 4 and ts.hour >= 21) or \
           (ts.weekday() == 6 and ts.hour < 22):
            ts += timedelta(minutes=minutes)
            continue

        sess = session_of(ts)
        smult = SESSION_VOL[sess]

        # Student-t innovation for fat tails. nu=6 gives excess kurtosis ~3 in
        # the innovation, which combined with GARCH clustering lands the
        # unconditional series near gold's observed 5-9. nu=4 overshoots badly.
        nu = 6.0
        z = rng.gauss(0, 1)
        chi = sum(rng.gauss(0, 1) ** 2 for _ in range(6))
        t_inn = z / math.sqrt(chi / nu) if chi > 0 else z
        t_inn *= math.sqrt((nu - 2) / nu)          # unit variance
        # Truncate at 8 sigma. Real gold has fat tails, not infinite ones; an
        # untruncated t can emit a single print that alone sets the sample
        # kurtosis, which made results seed-dependent (kurt 4.6 vs 34.9).
        t_inn = max(-8.0, min(8.0, t_inn))

        sigma = math.sqrt(var) * smult
        ret = sigma * t_inn

        # Poisson jump, concentrated in the NY data window.
        if rng.random() < (jump_prob * (2.5 if sess == Session.OVERLAP else 1.0)):
            ret += rng.choice([-1, 1]) * sigma * rng.uniform(1.8, 3.0)

        # Injected edge: after a liquidity sweep, a partial reversion follows.
        ret += pending_reversion
        pending_reversion = 0.0

        # Cap total bar return against UNCONDITIONAL vol, not conditional.
        # Capping at 10 conditional sigma does nothing when the GARCH state is
        # itself elevated -- and that state variation is precisely what drives
        # unconditional kurtosis. Measured across 8 seeds, conditional capping
        # left kurtosis swinging 3.9-34.9; this caps it into gold's real 5-9.
        base_sigma = math.sqrt(base_var) * smult
        ret = max(-9.0 * base_sigma, min(9.0 * base_sigma, ret))

        o = px
        c = o * math.exp(ret)

        # Intrabar path: range is at least |body|, extended by a lognormal factor
        # calibrated so range/|body| has a realistic right tail.
        body = abs(c - o)
        ext = math.exp(rng.gauss(-0.35, 0.55))
        rng_size = body + o * sigma * ext
        up_share = rng.random()
        h = max(o, c) + rng_size * up_share * 0.55
        l = min(o, c) - rng_size * (1 - up_share) * 0.55
        h = max(h, o, c)
        l = min(l, o, c)

        vol = max(1.0, rng.gauss(1000 * smult, 250 * smult))
        bar = Bar(ts=ts, open=o, high=h, low=l, close=c, volume=vol,
                  spread=0.25 / max(smult, 0.4))
        bars.append(bar)

        # Sweep bookkeeping -> schedule the injected reversion for the NEXT bar.
        if len(recent_highs) >= 20:
            ph, pl = max(recent_highs[-20:]), min(recent_lows[-20:])
            if h > ph and c < ph and edge > 0:
                pending_reversion = -abs(sigma) * edge * rng.uniform(0.5, 1.5)
            elif l < pl and c > pl and edge > 0:
                pending_reversion = abs(sigma) * edge * rng.uniform(0.5, 1.5)
        recent_highs.append(h)
        recent_lows.append(l)
        if len(recent_highs) > 200:
            recent_highs.pop(0)
            recent_lows.pop(0)

        var = omega + a * (ret ** 2) + b * var
        px = c
        ts += timedelta(minutes=minutes)

    return bars


def stylised_facts(bars: list[Bar]) -> dict:
    """Measure the properties that justify (or refute) using this data."""
    from .core import logret, mean, stdev

    rets = [logret(bars[i - 1].close, bars[i].close) for i in range(1, len(bars))]
    absr = [abs(r) for r in rets]

    def ac(xs, lag):
        m = mean(xs)
        num = sum((xs[i] - m) * (xs[i - lag] - m) for i in range(lag, len(xs)))
        den = sum((x - m) ** 2 for x in xs)
        return num / den if den else 0.0

    m, sd = mean(rets), stdev(rets)
    kurt = mean([((r - m) / sd) ** 4 for r in rets]) if sd > 0 else 0.0

    sess_vol = {}
    for s in Session:
        sub = [abs(logret(bars[i - 1].close, bars[i].close))
               for i in range(1, len(bars)) if session_of(bars[i].ts) == s]
        if sub:
            sess_vol[s.value] = mean(sub)
    norm = mean(list(sess_vol.values())) if sess_vol else 1.0

    return {
        "n_bars": len(bars),
        "ret_autocorr_lag1": ac(rets, 1),
        "absret_autocorr_lag1": ac(absr, 1),
        "absret_autocorr_lag10": ac(absr, 10),
        "excess_kurtosis": kurt - 3.0,
        "session_vol_multipliers": {k: v / norm for k, v in sess_vol.items()},
        "pct_up_bars": mean([1.0 if b.close > b.open else 0.0 for b in bars]),
    }
