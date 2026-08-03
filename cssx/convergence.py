"""CSS-X convergence engine.

Three paths, mirroring CSS v10.0 but re-derived for crypto's failure topology:

  Path A — MECHANICAL convergence (the chain/venue itself is breaking):
           Tier1 ∧ Tier2 ∧ (Tier3 ∨ Tier4)
  Path B — SHADOW convergence (nothing mechanical yet; obligations stopped):
           ≥3 independent Tier-4 absences
  Path C — HYBRID convergence (1 hard mechanical + ≥2 absences)

Then four global modifiers that most naive scoring systems omit and which are
the difference between a screener and a system:

  * PERSISTENCE  — a signal must survive N consecutive daily observations.
                   Crypto moves faster than corporate paper, so N is 3–10 days,
                   not 14–21.
  * INDEPENDENCE — correlated signals are down-weighted so that one root cause
                   observed five ways cannot manufacture a 0.9.
  * CONTRADICTION— live evidence of solvency (verified raise, honoured
                   large withdrawal, restored proofs) hard-caps the score.
  * COVERAGE     — the score is reported with a confidence that reflects how
                   many applicable layers were actually measured.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .core import AssetClass, Observation, SignalScore, Tier, clamp
from .signals import ALL_LAYERS


# Correlation clusters: signals sharing a root cause. Within a cluster only the
# strongest signal counts fully; the rest are damped.
CLUSTERS: list[set[int]] = [
    {101, 102, 104},          # consensus/security complex
    {201, 202, 203},          # market liquidity complex
    {204, 205, 405},          # reserve/redemption complex
    {302, 303, 305, 403},     # organisational activity complex
    {406, 407},               # narrative complex
]

CLUSTER_DAMPING = 0.55

# Minimum consecutive days a tier's evidence must persist before it can drive
# an alert. Faster than CSS v10.0 because crypto settlement is faster.
PERSISTENCE_DAYS = {Tier.CONSENSUS: 3, Tier.LIQUIDITY: 4, Tier.OPERATIONAL: 7, Tier.ABSENCE: 10}

ALERT_BANDS = [
    (0.90, "TERMINAL", "Failure in progress or imminent. Exit, do not average down."),
    (0.75, "CRITICAL", "Multi-tier convergence. Reduce exposure; assume redemption risk."),
    (0.55, "ELEVATED", "Structural deterioration confirmed by independent evidence."),
    (0.35, "WATCH", "Early absences detected. Increase monitoring frequency."),
    (0.00, "NOMINAL", "No convergent distress evidence."),
]


@dataclass
class Verdict:
    entity_id: str
    asset_class: AssetClass
    score: float
    band: str
    action: str
    path: str
    confidence: float
    coverage: float
    persistence_ok: bool
    tier_scores: dict[int, float]
    active_absences: int
    signals: list[SignalScore] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    narrative: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "asset_class": self.asset_class.value,
            "score": round(self.score, 4),
            "band": self.band,
            "action": self.action,
            "path": self.path,
            "confidence": round(self.confidence, 3),
            "coverage": round(self.coverage, 3),
            "persistence_ok": self.persistence_ok,
            "tier_scores": {str(k): round(v, 4) for k, v in self.tier_scores.items()},
            "active_absences": self.active_absences,
            "contradictions": self.contradictions,
            "narrative": self.narrative,
            "signals": [s.to_dict() for s in self.signals if s.measured],
        }


def evaluate_signals(o: Observation) -> list[SignalScore]:
    return [layer(o) for layer in ALL_LAYERS]


def _damp_clusters(signals: list[SignalScore]) -> dict[int, float]:
    """Return effective (independence-adjusted) scores keyed by layer id."""
    eff = {s.layer: s.score for s in signals}
    for cluster in CLUSTERS:
        members = [(lid, eff.get(lid, 0.0)) for lid in cluster if eff.get(lid, 0.0) > 0]
        if len(members) <= 1:
            continue
        members.sort(key=lambda kv: kv[1], reverse=True)
        for lid, val in members[1:]:
            eff[lid] = val * CLUSTER_DAMPING
    return eff


def _tier_max(signals: list[SignalScore], eff: dict[int, float], tier: Tier) -> float:
    return max((eff[s.layer] for s in signals if s.tier == tier), default=0.0)


def _detect_contradictions(o: Observation) -> list[str]:
    c = []
    if o.get("verified_raise_30d_usd", 0) and float(o.get("verified_raise_30d_usd")) > 0:
        c.append("verified capital raise in last 30 days")
    if o.get("large_withdrawal_honoured_7d", False):
        c.append("large withdrawal honoured on-chain in last 7 days")
    if o.get("proofs_restored", False):
        c.append("state-root / proof posting restored")
    if o.get("attestation_published_7d", False):
        c.append("fresh reserve attestation published")
    if o.get("planned_migration", False):
        c.append("announced, verifiable chain/contract migration explains inactivity")
    return c


def _coverage(signals: list[SignalScore]) -> float:
    applicable = [s for s in signals]
    measured = [s for s in signals if s.measured]
    return len(measured) / max(len(applicable), 1)


def _noisy_or(values: list[float], ceiling: float) -> float:
    """Combine independent evidence multiplicatively rather than additively.

    Additive stacking saturates instantly (three 0.4s become 1.2) and destroys
    all ranking information at the top of the book — exactly where the system
    must discriminate. Noisy-OR keeps every marginal signal informative while
    asymptotically approaching, but never reaching, certainty.
    """
    p = 1.0
    for v in values:
        p *= (1.0 - clamp(v, 0.0, 0.97))
    return clamp((1.0 - p) * ceiling, 0.0, ceiling)


def _path_a(t1: float, t2: float, t3: float, t4: float) -> float:
    """Mechanical: consensus AND liquidity AND (operational OR absence)."""
    if t1 >= 0.30 and t2 >= 0.20 and max(t3, t4) >= 0.20:
        return _noisy_or([t1, t2, max(t3, t4), 0.6 * min(t3, t4)], ceiling=0.97)
    return 0.0


def _path_b(absence_scores: list[float]) -> float:
    """Shadow: three or more independent mandatory-emission absences."""
    active = sorted((s for s in absence_scores if s > 0), reverse=True)
    if len(active) >= 3:
        # Diminishing weight per additional absence: 1.0, 0.85, 0.72, ...
        weighted = [v * (0.85 ** i) for i, v in enumerate(active)]
        return _noisy_or(weighted, ceiling=0.94)
    return 0.0


def _path_c(hard: float, absence_scores: list[float]) -> float:
    """Hybrid: one hard mechanical signal plus two or more absences."""
    active = sorted((s for s in absence_scores if s > 0), reverse=True)
    if hard >= 0.30 and len(active) >= 2:
        return _noisy_or([hard] + [v * 0.8 for v in active[:3]], ceiling=0.93)
    return 0.0


def _band(score: float) -> tuple[str, str]:
    for threshold, band, action in ALERT_BANDS:
        if score >= threshold:
            return band, action
    return "NOMINAL", ALERT_BANDS[-1][2]


def _narrate(v_signals: list[SignalScore], path: str, band: str) -> str:
    top = sorted((s for s in v_signals if s.active), key=lambda s: s.score, reverse=True)[:4]
    if not top:
        return "No active distress signals. All measured obligations are being met."
    bullets = "; ".join(f"{s.name} ({s.score:.2f}): {s.rationale}" for s in top)
    return f"[{band} via {path}] {bullets}."


def score_entity(
    o: Observation,
    persistence_history: dict[int, int] | None = None,
) -> Verdict:
    """Score one entity from one observation (+ optional persistence history).

    `persistence_history` maps layer id -> consecutive days the layer has been
    active. Without it, persistence is assumed unmet for slow tiers, which
    makes the system conservative by default rather than trigger-happy.
    """
    signals = evaluate_signals(o)
    eff = _damp_clusters(signals)
    hist = persistence_history or {}

    # Rumour containment: L407 (social capitulation) may never contribute unless
    # a mechanical Tier-1/2 signal corroborates it. Applied before tier maxima so
    # it cannot leak into the absence tier.
    mechanical_present = any(
        eff.get(s.layer, 0) > 0 for s in signals if s.tier in (Tier.CONSENSUS, Tier.LIQUIDITY)
    )
    if not mechanical_present:
        eff[407] = 0.0

    t1 = _tier_max(signals, eff, Tier.CONSENSUS)
    t2 = _tier_max(signals, eff, Tier.LIQUIDITY)
    t3 = _tier_max(signals, eff, Tier.OPERATIONAL)
    t4 = _tier_max(signals, eff, Tier.ABSENCE)

    absence_scores = [eff.get(s.layer, 0.0) for s in signals if s.tier == Tier.ABSENCE]
    hard = max(
        eff.get(lid, 0.0) for lid in (101, 102, 103, 201, 203, 204, 205, 304)
    )

    a, b, c = _path_a(t1, t2, t3, t4), _path_b(absence_scores), _path_c(hard, absence_scores)
    raw, path = max(((a, "PATH_A_MECHANICAL"), (b, "PATH_B_SHADOW"), (c, "PATH_C_HYBRID")),
                    key=lambda kv: kv[0])
    if raw == 0.0:
        # Below convergence: report the damped evidence mass, capped in WATCH.
        raw = clamp(max(t1, t2, t3, t4) * 0.65, 0, 0.54)
        path = "SUB_CONVERGENCE"

    # Persistence gate: the driving tier must have survived its dwell time.
    driving_layers = [s.layer for s in signals if s.active and eff.get(s.layer, 0) > 0]
    persistence_ok = True
    if path != "SUB_CONVERGENCE" and driving_layers:
        needed = [
            (lid, PERSISTENCE_DAYS[next(s.tier for s in signals if s.layer == lid)])
            for lid in driving_layers
        ]
        persistence_ok = any(hist.get(lid, 0) >= days for lid, days in needed)
        if not persistence_ok:
            raw = min(raw, 0.74)   # cannot enter TERMINAL/CRITICAL unconfirmed

    contradictions = _detect_contradictions(o)
    if contradictions:
        raw = min(raw, 0.60)

    coverage = _coverage(signals)
    confidence = clamp(0.35 + 0.5 * coverage + (0.15 if persistence_ok else 0.0))
    score = clamp(raw)

    band, action = _band(score)
    return Verdict(
        entity_id=o.entity_id,
        asset_class=o.asset_class,
        score=score,
        band=band,
        action=action,
        path=path,
        confidence=confidence,
        coverage=coverage,
        persistence_ok=persistence_ok,
        tier_scores={1: t1, 2: t2, 3: t3, 4: t4},
        active_absences=len([s for s in absence_scores if s > 0]),
        signals=signals,
        contradictions=contradictions,
        narrative=_narrate(
            [s for s in signals if eff.get(s.layer, 0) > 0], path, band
        ),
    )


def rank(observations: Iterable[Observation],
         histories: dict[str, dict[int, int]] | None = None) -> list[Verdict]:
    histories = histories or {}
    verdicts = [score_entity(o, histories.get(o.entity_id)) for o in observations]
    return sorted(verdicts, key=lambda v: v.score, reverse=True)
