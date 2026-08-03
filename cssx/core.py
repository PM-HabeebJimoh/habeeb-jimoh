"""CSS-X core primitives: observations, signal scores, entity classes.

CSS-X is the crypto-market analogue of CSS v10.0. Where CSS v10.0 reads the
administrative exhaust of a corporation (liens, WARNs, UCC lapses), CSS-X reads
the *protocol exhaust* of a crypto asset: block production, validator sets,
oracle heartbeats, bridge reserves, LP depth, governance quorum, code commits.

The unifying thesis is unchanged: solvency is a data-emission process. Healthy
systems are legally, mechanically or economically *obliged* to emit certain
data. Death is the cessation of a mandatory emission.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


UTC = timezone.utc


def now() -> datetime:
    return datetime.now(UTC)


class AssetClass(str, Enum):
    """Determines which convergence path applies."""

    L1 = "l1"                # sovereign chain: validators, block production
    L2 = "l2"                # rollup: sequencer, bridge, proof posting
    DEFI = "defi"            # protocol with TVL, LPs, governance
    CEX = "cex"              # custodial exchange, proof-of-reserves
    STABLE = "stablecoin"    # peg-bearing claim
    TOKEN = "token"          # bare listed token / memecoin


class Tier(int, Enum):
    CONSENSUS = 1       # the chain itself stops being a chain
    LIQUIDITY = 2       # the claim stops being redeemable
    OPERATIONAL = 3     # the org behind it stops operating
    ABSENCE = 4         # mandatory emissions stop (the CSS-X innovation)


@dataclass
class Observation:
    """A raw, timestamped, source-attributed measurement.

    Every field is optional so that partial coverage degrades gracefully: an
    unmeasured signal scores 0 and reduces confidence, it never fabricates.
    """

    entity_id: str
    asset_class: AssetClass
    ts: datetime = field(default_factory=now)
    facts: dict[str, Any] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        v = self.facts.get(key, default)
        return default if v is None else v

    def has(self, *keys: str) -> bool:
        return all(self.facts.get(k) is not None for k in keys)


@dataclass
class SignalScore:
    layer: int
    name: str
    tier: Tier
    score: float
    measured: bool
    lead_time_days: tuple[int, int]
    rationale: str
    inputs: dict[str, Any] = field(default_factory=dict)

    @property
    def active(self) -> bool:
        return self.measured and self.score > 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "name": self.name,
            "tier": int(self.tier),
            "score": round(self.score, 4),
            "measured": self.measured,
            "lead_time_days": list(self.lead_time_days),
            "rationale": self.rationale,
            "inputs": self.inputs,
        }


def unmeasured(layer: int, name: str, tier: Tier, lead: tuple[int, int]) -> SignalScore:
    return SignalScore(layer, name, tier, 0.0, False, lead, "no data")


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def safe_ratio(num: float, den: float, default: float = 0.0) -> float:
    if den == 0 or den is None:
        return default
    return num / den


def shannon_entropy(weights: list[float]) -> float:
    """Entropy in bits of a weight vector (validator stake, LP shares, ...)."""
    total = sum(w for w in weights if w > 0)
    if total <= 0:
        return 0.0
    h = 0.0
    for w in weights:
        if w <= 0:
            continue
        p = w / total
        h -= p * math.log2(p)
    return h


def nakamoto_coefficient(weights: list[float], threshold: float = 0.3333) -> int:
    """Minimum number of holders needed to cross a control threshold."""
    total = sum(w for w in weights if w > 0)
    if total <= 0:
        return 0
    acc = 0.0
    for i, w in enumerate(sorted((w for w in weights if w > 0), reverse=True), 1):
        acc += w / total
        if acc > threshold:
            return i
    return len([w for w in weights if w > 0])
