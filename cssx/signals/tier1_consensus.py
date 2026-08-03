"""TIER 1 — CONSENSUS CLAIM (the lethal state).

Crypto's analogue of the federal tax lien is not a piece of paper: it is the
chain's own refusal to advance. Tier 1 signals are near-absorbing states. They
are cheap to verify (any RPC endpoint) and impossible to spin.
"""

from __future__ import annotations

from ..core import (
    AssetClass,
    Observation,
    SignalScore,
    Tier,
    clamp,
    nakamoto_coefficient,
    safe_ratio,
    shannon_entropy,
    unmeasured,
)


# ---------------------------------------------------------------- Layer 101
def layer_101_block_production_halt(o: Observation) -> SignalScore:
    """L101 — BLOCK PRODUCTION HALT / FINALITY STALL ("the chain flatline").

    Measures: seconds since last finalized block versus the chain's own target
    block time. A chain that cannot finalize is, for every economic purpose,
    a chain that has stopped existing.

    Sources: public RPC `eth_getBlockByNumber`/`status`, Beacon API
    `/eth/v1/beacon/headers/finalized`, block explorer JSON. Cost: $0.
    """
    lead = (0, 3)
    if o.asset_class not in (AssetClass.L1, AssetClass.L2):
        return unmeasured(101, "block_production_halt", Tier.CONSENSUS, lead)
    if not o.has("seconds_since_final_block", "target_block_time_s"):
        return unmeasured(101, "block_production_halt", Tier.CONSENSUS, lead)

    gap = float(o.get("seconds_since_final_block"))
    target = max(float(o.get("target_block_time_s")), 0.1)
    ratio = gap / target

    if ratio >= 500:
        s, why = 0.90, "finality stalled >500x target block time — chain halted"
    elif ratio >= 100:
        s, why = 0.65, "finality stalled >100x target block time"
    elif ratio >= 20:
        s, why = 0.35, "degraded block production (>20x target)"
    else:
        s, why = 0.0, "block production nominal"

    # A halt with no public incident post is worse than an announced one.
    if s > 0 and o.get("incident_ack", False) is False:
        s = clamp(s * 1.1, 0, 0.92)
        why += "; no public incident acknowledgement"

    return SignalScore(101, "block_production_halt", Tier.CONSENSUS, s, True, lead, why,
                       {"gap_ratio": round(ratio, 2)})


# ---------------------------------------------------------------- Layer 102
def layer_102_validator_exodus(o: Observation) -> SignalScore:
    """L102 — VALIDATOR / STAKE EXODUS AND CENTRALISATION COLLAPSE.

    Measures: 30d change in active stake, exit-queue depth, and the Nakamoto
    coefficient of the stake distribution. Security is a budget; when the
    budget leaves, the chain is uninsured before it is dead.

    Sources: beacon chain API, staking module REST (`/staking/v1beta1/validators`),
    public validator-set snapshots. Cost: $0.
    """
    lead = (7, 60)
    if o.asset_class not in (AssetClass.L1, AssetClass.L2):
        return unmeasured(102, "validator_exodus", Tier.CONSENSUS, lead)
    if not o.has("stake_delta_30d_pct"):
        return unmeasured(102, "validator_exodus", Tier.CONSENSUS, lead)

    delta = float(o.get("stake_delta_30d_pct"))          # e.g. -0.35
    exit_q = float(o.get("exit_queue_pct_of_stake", 0.0))
    weights = o.get("validator_stake_weights", []) or []
    nk = nakamoto_coefficient(weights) if weights else None

    s = 0.0
    parts = []
    if delta <= -0.30:
        s += 0.35
        parts.append(f"stake -{abs(delta):.0%} in 30d")
    elif delta <= -0.15:
        s += 0.20
        parts.append(f"stake -{abs(delta):.0%} in 30d")

    if exit_q >= 0.15:
        s += 0.20
        parts.append(f"exit queue {exit_q:.0%} of stake")
    elif exit_q >= 0.05:
        s += 0.10
        parts.append(f"exit queue {exit_q:.0%} of stake")

    if nk is not None and nk <= 2:
        s += 0.20
        parts.append(f"nakamoto coefficient {nk} (capturable)")
    elif nk is not None and nk <= 4:
        s += 0.10
        parts.append(f"nakamoto coefficient {nk}")

    s = clamp(s, 0, 0.70)
    return SignalScore(102, "validator_exodus", Tier.CONSENSUS, s, True, lead,
                       "; ".join(parts) or "validator set stable",
                       {"stake_delta_30d_pct": delta, "nakamoto": nk})


# ---------------------------------------------------------------- Layer 103
def layer_103_sequencer_or_upgrade_key(o: Observation) -> SignalScore:
    """L103 — SEQUENCER SINGLE POINT OF FAILURE / UNILATERAL UPGRADE KEY.

    Measures, for L2s and DeFi: whether one key can stop or rewrite the system,
    and whether the escape hatch (forced inclusion, timelock) actually works.
    This is the crypto equivalent of a sovereign lien: someone else already
    holds the authority to seize.

    Sources: L2Beat risk rows (public JSON), on-chain `owner()`/`admin()` slot
    reads, timelock contract `getMinDelay()`. Cost: $0.
    """
    lead = (0, 30)
    if o.asset_class not in (AssetClass.L2, AssetClass.DEFI, AssetClass.STABLE):
        return unmeasured(103, "unilateral_control", Tier.CONSENSUS, lead)
    if not o.has("upgrade_control"):
        return unmeasured(103, "unilateral_control", Tier.CONSENSUS, lead)

    control = str(o.get("upgrade_control"))              # eoa|multisig|timelock|immutable
    delay_h = float(o.get("timelock_delay_hours", 0.0))
    escape = bool(o.get("escape_hatch_working", True))
    seq_down_h = float(o.get("sequencer_downtime_24h_hours", 0.0))

    base = {"eoa": 0.55, "multisig": 0.30, "timelock": 0.10, "immutable": 0.0}.get(control, 0.20)
    s = base
    parts = [f"upgrade control = {control}"]
    if control in ("eoa", "multisig") and delay_h < 24:
        s += 0.10
        parts.append(f"timelock only {delay_h:.0f}h")
    if not escape:
        s += 0.15
        parts.append("escape hatch non-functional")
    if seq_down_h >= 6:
        s += 0.15
        parts.append(f"sequencer down {seq_down_h:.1f}h/24h")

    s = clamp(s, 0, 0.75)
    return SignalScore(103, "unilateral_control", Tier.CONSENSUS, s, True, lead,
                       "; ".join(parts), {"control": control, "escape_hatch": escape})


# ---------------------------------------------------------------- Layer 104
def layer_104_security_budget_inversion(o: Observation) -> SignalScore:
    """L104 — SECURITY BUDGET INVERSION (cost-to-attack < value-at-stake).

    Measures: annualised cost of a 33%/51% attack against the value the chain
    secures. When it is cheaper to buy the chain than to rob it elsewhere, the
    chain is economically insolvent even while producing blocks.

    Sources: staking APR + market cap (CoinGecko free tier), hashrate rental
    price boards, TVL from DefiLlama free API. Cost: $0.
    """
    lead = (14, 120)
    if o.asset_class not in (AssetClass.L1, AssetClass.L2):
        return unmeasured(104, "security_budget_inversion", Tier.CONSENSUS, lead)
    if not o.has("cost_to_attack_usd", "value_secured_usd"):
        return unmeasured(104, "security_budget_inversion", Tier.CONSENSUS, lead)

    cta = float(o.get("cost_to_attack_usd"))
    vs = float(o.get("value_secured_usd"))
    r = safe_ratio(cta, vs, default=1.0)

    if r < 0.05:
        s, why = 0.50, f"attack costs {r:.1%} of value secured — trivially capturable"
    elif r < 0.20:
        s, why = 0.30, f"attack costs {r:.1%} of value secured"
    elif r < 0.50:
        s, why = 0.15, f"thin security margin ({r:.1%})"
    else:
        s, why = 0.0, "security budget adequate"

    return SignalScore(104, "security_budget_inversion", Tier.CONSENSUS, s, True, lead, why,
                       {"cta_over_value": round(r, 4)})


# ---------------------------------------------------------------- Layer 105
def layer_105_stake_concentration_entropy(o: Observation) -> SignalScore:
    """L105 — HOLDER/STAKE ENTROPY COLLAPSE.

    Measures: Shannon entropy of the top-holder distribution versus its own
    90-day baseline. Falling entropy = the float is being reabsorbed by
    insiders or a single desk — the pre-condition of an orderly exit scam.

    Sources: explorer top-holder endpoints, on-chain balance queries. Cost: $0.
    """
    lead = (14, 90)
    if not o.has("holder_weights"):
        return unmeasured(105, "holder_entropy_collapse", Tier.CONSENSUS, lead)

    weights = o.get("holder_weights") or []
    h = shannon_entropy(weights)
    base = float(o.get("holder_entropy_baseline_90d", h))
    drop = base - h

    if base > 0 and drop / base >= 0.30:
        s, why = 0.30, f"holder entropy -{drop / base:.0%} vs 90d baseline"
    elif base > 0 and drop / base >= 0.15:
        s, why = 0.15, f"holder entropy -{drop / base:.0%} vs 90d baseline"
    else:
        s, why = 0.0, "holder distribution stable"

    return SignalScore(105, "holder_entropy_collapse", Tier.CONSENSUS, s, True, lead, why,
                       {"entropy_bits": round(h, 3), "baseline_bits": round(base, 3)})


TIER1_LAYERS = [
    layer_101_block_production_halt,
    layer_102_validator_exodus,
    layer_103_sequencer_or_upgrade_key,
    layer_104_security_budget_inversion,
    layer_105_stake_concentration_entropy,
]
