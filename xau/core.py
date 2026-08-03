"""XAU-Q core: bars, sessions, and the arithmetic every other module shares.

Pure stdlib. No numpy, no pandas — this environment cannot install packages, and
the algorithms here are O(n) streaming anyway.

DESIGN RULE THAT GOVERNS THIS WHOLE PACKAGE
-------------------------------------------
Every feature is computed from bars strictly BEFORE the bar being predicted.
There is exactly one place where a bar index is turned into a feature vector
(`FeatureBuilder.at`), and it takes `i` meaning "predict bar i using bars
[0, i-1]". If a feature ever reads bars[i], that is a lookahead bug, and the
test suite has a dedicated shuffle-detector for it.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone, time
from enum import Enum
from typing import Iterable, Iterator, Sequence

UTC = timezone.utc


# --------------------------------------------------------------------------- bars
@dataclass(frozen=True)
class Bar:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0          # tick volume for spot gold; real volume for futures
    spread: float = 0.0          # in price units, if the feed provides it

    @property
    def range(self) -> float:
        return self.high - self.low

    @property
    def body(self) -> float:
        return self.close - self.open

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def typical(self) -> float:
        return (self.high + self.low + self.close) / 3.0

    def validate(self) -> None:
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"{self.ts}: open {self.open} outside [{self.low},{self.high}]")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"{self.ts}: close {self.close} outside [{self.low},{self.high}]")
        if self.high < self.low:
            raise ValueError(f"{self.ts}: high < low")


class Session(str, Enum):
    """Gold trades ~23h/day. Session identity is one of the few genuinely
    informative categorical features: Asian ranges compress, London expands,
    NY absorbs the US data calendar."""

    ASIA = "asia"        # 23:00-07:00 UTC
    LONDON = "london"    # 07:00-12:00 UTC
    OVERLAP = "overlap"  # 12:00-16:00 UTC  (London PM + NY AM, the volatility peak)
    NEWYORK = "newyork"  # 16:00-21:00 UTC
    LATE = "late"        # 21:00-23:00 UTC  (thin, gappy)


def session_of(ts: datetime) -> Session:
    h = ts.astimezone(UTC).hour
    if 23 <= h or h < 7:
        return Session.ASIA
    if 7 <= h < 12:
        return Session.LONDON
    if 12 <= h < 16:
        return Session.OVERLAP
    if 16 <= h < 21:
        return Session.NEWYORK
    return Session.LATE


# --------------------------------------------------------------------------- io
def load_csv(path: str, tz_utc: bool = True) -> list[Bar]:
    """Load OHLCV from CSV.

    Accepts the column names every common XAUUSD source uses:
      time/date/timestamp/datetime, open, high, low, close, volume/tickvol, spread
    Dukascopy, MT4/MT5 export, HistData, Stooq and TradingView exports all parse.
    """
    out: list[Bar] = []
    with open(path, newline="") as f:
        sample = f.read(8192)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        rdr = csv.DictReader(f, dialect=dialect)
        if not rdr.fieldnames:
            raise ValueError("empty csv")
        cols = {c.strip().lower().lstrip("<").rstrip(">"): c for c in rdr.fieldnames}

        def pick(*names: str) -> str | None:
            for n in names:
                if n in cols:
                    return cols[n]
            return None

        c_t = pick("time", "date", "timestamp", "datetime", "dtyyyymmdd")
        c_o, c_h = pick("open", "o"), pick("high", "h")
        c_l, c_c = pick("low", "l"), pick("close", "c", "price")
        c_v = pick("volume", "vol", "tickvol", "tickvolume")
        c_s = pick("spread")
        if not all([c_t, c_o, c_h, c_l, c_c]):
            raise ValueError(f"missing OHLC columns in {rdr.fieldnames}")

        c_time2 = pick("time") if c_t != cols.get("time") else None
        for row in rdr:
            raw = row[c_t].strip()
            if c_time2 and row.get(c_time2):
                raw = f"{raw} {row[c_time2].strip()}"
            ts = _parse_ts(raw)
            if tz_utc and ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            b = Bar(
                ts=ts,
                open=float(row[c_o]), high=float(row[c_h]),
                low=float(row[c_l]), close=float(row[c_c]),
                volume=float(row[c_v]) if c_v and row.get(c_v) else 0.0,
                spread=float(row[c_s]) if c_s and row.get(c_s) else 0.0,
            )
            b.validate()
            out.append(b)
    out.sort(key=lambda b: b.ts)
    return out


_TS_FORMATS = (
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
    "%Y.%m.%d %H:%M:%S", "%Y.%m.%d %H:%M", "%Y.%m.%d",
    "%d.%m.%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%Y%m%d %H%M%S", "%Y%m%d",
)


def _parse_ts(s: str) -> datetime:
    s = s.strip().replace("T", " ").rstrip("Z")
    for fmt in _TS_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s)
    except ValueError as e:
        raise ValueError(f"unparseable timestamp {s!r}") from e


def dedupe_and_check(bars: Sequence[Bar]) -> tuple[list[Bar], dict]:
    """Remove duplicate timestamps and report data-quality stats.

    Retail XAUUSD feeds are dirty: broker-specific weekend gaps, duplicated bars
    at rollover, zero-range prints during holidays. Silent bad data is the second
    most common source of fake backtest accuracy after lookahead.
    """
    seen: set[datetime] = set()
    clean: list[Bar] = []
    dupes = zero_range = 0
    for b in bars:
        if b.ts in seen:
            dupes += 1
            continue
        seen.add(b.ts)
        if b.range <= 0:
            zero_range += 1
        clean.append(b)
    gaps = 0
    if len(clean) > 2:
        deltas = [(clean[i + 1].ts - clean[i].ts).total_seconds() for i in range(len(clean) - 1)]
        med = sorted(deltas)[len(deltas) // 2]
        gaps = sum(1 for d in deltas if d > med * 3)
    return clean, {
        "n": len(clean), "duplicates_removed": dupes,
        "zero_range_bars": zero_range, "large_gaps": gaps,
        "start": clean[0].ts.isoformat() if clean else None,
        "end": clean[-1].ts.isoformat() if clean else None,
    }


# --------------------------------------------------------------------------- math
def mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def stdev(xs: Sequence[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def quantile(xs: Sequence[float], q: float) -> float:
    """Linear-interpolated quantile. Used everywhere in the conformal layer."""
    if not xs:
        return 0.0
    s = sorted(xs)
    if q <= 0:
        return s[0]
    if q >= 1:
        return s[-1]
    pos = q * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(s) - 1)
    frac = pos - lo
    return s[lo] * (1 - frac) + s[hi] * frac


def ewma(xs: Sequence[float], alpha: float) -> float:
    if not xs:
        return 0.0
    acc = xs[0]
    for x in xs[1:]:
        acc = alpha * x + (1 - alpha) * acc
    return acc


def true_range(prev_close: float, b: Bar) -> float:
    return max(b.high - b.low, abs(b.high - prev_close), abs(b.low - prev_close))


def atr(bars: Sequence[Bar], n: int) -> float:
    """Wilder ATR over the last n bars of `bars`. Caller guarantees len > n."""
    if len(bars) < n + 1:
        return mean([b.range for b in bars]) if bars else 0.0
    trs = [true_range(bars[i - 1].close, bars[i]) for i in range(len(bars) - n, len(bars))]
    return mean(trs)


def logret(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        return 0.0
    return math.log(b / a)


def sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# --------------------------------------------------------------------------- stats
def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score CI for a proportion.

    Reported on EVERY accuracy number in this package. A point estimate of
    "85% accuracy" on 200 samples has a CI of roughly [79%, 89%] — quoting the
    point estimate alone is how backtests lie.
    """
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def binomial_p_value(k: int, n: int, p0: float = 0.5) -> float:
    """One-sided P(X >= k) under Binomial(n, p0). Normal approx above n=1000."""
    if n == 0:
        return 1.0
    if n > 1000:
        mu, sd = n * p0, math.sqrt(n * p0 * (1 - p0))
        if sd == 0:
            return 1.0
        z = (k - 0.5 - mu) / sd
        return 0.5 * math.erfc(z / math.sqrt(2))
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * (p0 ** i) * ((1 - p0) ** (n - i))
    return min(1.0, total)


def sessions_iter(bars: Iterable[Bar]) -> Iterator[tuple[Bar, Session]]:
    for b in bars:
        yield b, session_of(b.ts)
