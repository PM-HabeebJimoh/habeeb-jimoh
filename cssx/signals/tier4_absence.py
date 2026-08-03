"""TIER 4 — MANDATORY ABSENCE (the shadow layer).

This is the CSS-X innovation, inherited from CSS v10.0's negative-space
forensics and sharpened for crypto. Blockchains are *obligated emitters*: an
oracle must post, a rollup must publish proofs, a solvent treasury must pay
gas, an audited protocol must renew its audit. Each obligation that stops is a
bit of information destroyed. Distress is entropy collapse in the emission
stream, and it is visible before any price moves.
"""

from __future__ import annotations

from ..core import (
    AssetClass,
    Observation,
    SignalScore,
    Tier,
    clamp,
    safe_ratio,
    unmeasured,
)


# ---------------------------------------------------------------- Layer 401
def layer_401_oracle_heartbeat_absence(o: Observation) -> SignalScore:
    """L401 — ORACLE HEARTBEAT ABSENCE.

    Measures: time since the last oracle update against the feed's own
    contracted heartbeat, plus deviation-threshold misses. Oracles are paid to
    post; when they stop, either the sponsor stopped funding the feed or the
    feed was deliberately frozen ahead of a liquidation event.

    Sources: Chainlink `latestRoundData()` / feed registry, Pyth price account
    slots, RedStone manifests. Cost: $0.
    """
    lead = (0, 14)
    if not o.has("oracle_staleness_s", "oracle_heartbeat_s"):
        return unmeasured(401, "oracle_heartbeat_absence", Tier.ABSENCE, lead)

    stale = float(o.get("oracle_staleness_s"))
    hb = max(float(o.get("oracle_heartbeat_s")), 1.0)
    r = stale / hb
    feeds_dead = int(o.get("dead_feed_count", 0))

    if r >= 10 or feeds_dead >= 2:
        s, why = 0.35, f"oracle {r:.1f}x past heartbeat ({feeds_dead} dead feeds)"
    elif r >= 3:
        s, why = 0.20, f"oracle {r:.1f}x past heartbeat"
    else:
        s, why = 0.0, "oracle posting on schedule"

    return SignalScore(401, "oracle_heartbeat_absence", Tier.ABSENCE, s, True, lead, why,
                       {"staleness_ratio": round(r, 2), "dead_feeds": feeds_dead})


# ---------------------------------------------------------------- Layer 402
def layer_402_proof_posting_absence(o: Observation) -> SignalScore:
    """L402 — STATE-ROOT / PROOF POSTING ABSENCE (rollup obligation gap).

    Measures: elapsed time since the last state root or validity proof was
    posted to L1, versus the protocol's documented cadence. A rollup that stops
    posting has stopped inheriting security — withdrawals become discretionary.

    Sources: L1 contract event logs (`StateBatchAppended`, `OutputProposed`)
    via free RPC / explorer API. Cost: $0.
    """
    lead = (0, 21)
    if o.asset_class != AssetClass.L2:
        return unmeasured(402, "proof_posting_absence", Tier.ABSENCE, lead)
    if not o.has("hours_since_state_root", "expected_root_cadence_h"):
        return unmeasured(402, "proof_posting_absence", Tier.ABSENCE, lead)

    gap = float(o.get("hours_since_state_root"))
    cad = max(float(o.get("expected_root_cadence_h")), 0.1)
    r = gap / cad
    pending = float(o.get("pending_withdrawals_usd", 0.0))

    if r >= 10:
        s, why = 0.40, f"no state root for {gap:.0f}h ({r:.0f}x cadence)"
    elif r >= 4:
        s, why = 0.25, f"state root {r:.1f}x overdue"
    elif r >= 2:
        s, why = 0.12, f"state root {r:.1f}x overdue"
    else:
        s, why = 0.0, "proofs posted on cadence"

    if s > 0 and pending > 0:
        why += f"; ${pending:,.0f} of withdrawals stranded"

    return SignalScore(402, "proof_posting_absence", Tier.ABSENCE, s, True, lead, why,
                       {"overdue_ratio": round(r, 2)})


# ---------------------------------------------------------------- Layer 403
def layer_403_treasury_gas_silence(o: Observation) -> SignalScore:
    """L403 — TREASURY GAS SILENCE (the operational pulse).

    Measures: days since the treasury/ops multisig last paid gas or executed a
    payment, and treasury runway in months. Payroll and gas are the last things
    a living organisation stops paying. Silence here is a death certificate
    with a 30-day postmark.

    Sources: multisig transaction history via explorer API, Safe transaction
    service (free), stablecoin balance reads. Cost: $0.
    """
    lead = (14, 90)
    if not o.has("days_since_treasury_tx"):
        return unmeasured(403, "treasury_gas_silence", Tier.ABSENCE, lead)

    days = float(o.get("days_since_treasury_tx"))
    runway = float(o.get("runway_months", 99))
    stable_share = float(o.get("treasury_stable_share", 1.0))

    s = 0.0
    parts = []
    if days >= 90:
        s += 0.30
        parts.append(f"no treasury transaction in {days:.0f} days")
    elif days >= 45:
        s += 0.18
        parts.append(f"no treasury transaction in {days:.0f} days")

    if runway < 3:
        s += 0.20
        parts.append(f"{runway:.1f} months runway")
    elif runway < 6:
        s += 0.10
        parts.append(f"{runway:.1f} months runway")

    if stable_share < 0.10:
        s += 0.08
        parts.append(f"only {stable_share:.0%} of treasury in stables (reflexive funding)")

    s = clamp(s, 0, 0.45)
    return SignalScore(403, "treasury_gas_silence", Tier.ABSENCE, s, True, lead,
                       "; ".join(parts) or "treasury active",
                       {"days_since_tx": days, "runway_months": runway})


# ---------------------------------------------------------------- Layer 404
def layer_404_attestation_lapse(o: Observation) -> SignalScore:
    """L404 — ATTESTATION / AUDIT LAPSE (the promised disclosure that stops).

    Measures: days since the last proof-of-reserves attestation or security
    audit relative to the cadence the entity itself publicly promised. Breaking
    your own disclosure promise is the cheapest possible signal to emit and the
    most expensive one to fake.

    Sources: entity PoR pages, auditor publication feeds, Wayback diffs of the
    "transparency" page. Cost: $0.
    """
    lead = (30, 120)
    if not o.has("days_since_attestation"):
        return unmeasured(404, "attestation_lapse", Tier.ABSENCE, lead)

    days = float(o.get("days_since_attestation"))
    promised = float(o.get("promised_cadence_days", 90))
    auditor_resigned = bool(o.get("auditor_resigned", False))
    page_removed = bool(o.get("transparency_page_removed", False))

    r = safe_ratio(days, max(promised, 1.0), default=0.0)
    s = 0.0
    parts = []
    if r >= 3:
        s += 0.30
        parts.append(f"attestation {r:.1f}x past promised cadence ({days:.0f}d)")
    elif r >= 1.5:
        s += 0.18
        parts.append(f"attestation overdue ({days:.0f}d vs {promised:.0f}d promised)")

    if auditor_resigned:
        s += 0.15
        parts.append("auditor resigned or withdrew opinion")
    if page_removed:
        s += 0.10
        parts.append("transparency page removed from site")

    s = clamp(s, 0, 0.45)
    return SignalScore(404, "attestation_lapse", Tier.ABSENCE, s, True, lead,
                       "; ".join(parts) or "attestations current",
                       {"overdue_ratio": round(r, 2)})


# ---------------------------------------------------------------- Layer 405
def layer_405_user_flow_extinction(o: Observation) -> SignalScore:
    """L405 — ORGANIC USER FLOW EXTINCTION (deposits stop, only exits remain).

    Measures: unique depositing addresses and gross inflow over 30 days versus
    baseline, and the deposit/withdrawal address ratio. A venue where nobody
    deposits and everybody withdraws is in a silent run, whatever the price
    chart says.

    Sources: exchange deposit-address clustering, protocol event logs
    (`Deposit`/`Withdraw`), free RPC log queries. Cost: $0.
    """
    lead = (6, 45)
    if not o.has("unique_depositors_30d", "depositors_baseline_90d"):
        return unmeasured(405, "user_flow_extinction", Tier.ABSENCE, lead)

    d30 = float(o.get("unique_depositors_30d"))
    base = max(float(o.get("depositors_baseline_90d")), 1.0)
    ratio = d30 / base
    inflow = float(o.get("inflow_30d_usd", 0.0))
    outflow = float(o.get("outflow_30d_usd", 0.0))
    net = safe_ratio(inflow - outflow, max(outflow, 1.0), default=0.0)

    s = 0.0
    parts = []
    if ratio <= 0.10:
        s += 0.30
        parts.append(f"depositors at {ratio:.0%} of baseline")
    elif ratio <= 0.35:
        s += 0.18
        parts.append(f"depositors at {ratio:.0%} of baseline")

    if inflow == 0 and outflow > 0:
        s += 0.15
        parts.append("zero inflow with continuing outflow")
    elif net <= -0.60:
        s += 0.10
        parts.append(f"net flow {net:.0%} of outflow")

    s = clamp(s, 0, 0.40)
    return SignalScore(405, "user_flow_extinction", Tier.ABSENCE, s, True, lead,
                       "; ".join(parts) or "organic flow intact",
                       {"depositor_ratio": round(ratio, 3)})


# ---------------------------------------------------------------- Layer 406
def layer_406_comms_entropy_spike(o: Observation) -> SignalScore:
    """L406 — COMMUNICATION ENTROPY SPIKE (the crypto 10-K vagueness test).

    Measures: KL divergence between the entity's current public communications
    (blog, X, Discord announcements) and its own 12-month baseline, combined
    with the density of reassurance vocabulary ("funds are safe", "temporary
    maintenance", "FUD"). Specificity collapses before solvency does.

    Sources: RSS/blog scrape, Nitter/X public timeline, Discord announcement
    export, local Llama-3 or plain TF-IDF. Cost: $0.
    """
    lead = (14, 90)
    if not o.has("kl_divergence_bits"):
        return unmeasured(406, "comms_entropy_spike", Tier.ABSENCE, lead)

    kl = float(o.get("kl_divergence_bits"))
    reassure = float(o.get("reassurance_density", 0.0))    # 0–1
    cadence_drop = float(o.get("post_cadence_delta", 0.0))  # negative = quieter

    if kl > 2.5 and reassure > 0.25:
        s, why = 0.30, f"KL {kl:.1f} bits with {reassure:.0%} reassurance vocabulary"
    elif kl > 1.5:
        s, why = 0.15, f"KL {kl:.1f} bits vs 12m baseline"
    else:
        s, why = 0.0, "communications consistent with baseline"

    if s > 0 and cadence_drop <= -0.70:
        s = clamp(s + 0.08, 0, 0.35)
        why += "; posting cadence collapsed"

    return SignalScore(406, "comms_entropy_spike", Tier.ABSENCE, s, True, lead, why,
                       {"kl_bits": kl, "reassurance": reassure})


# ---------------------------------------------------------------- Layer 407
def layer_407_social_capitulation(o: Observation) -> SignalScore:
    """L407 — HOLDER CAPITULATION CLUSTERING (withdrawal-failure reports).

    Measures: synchronised first-hand reports of failed withdrawals across
    Reddit/X/Discord, weighted by account age and corroborated by on-chain
    absence of the claimed payouts. Rumour becomes evidence only when the chain
    confirms the missing transfer.

    Constraint: only counted when at least one Tier-1/2 mechanical signal is
    also active — this layer can never fire alone.

    Sources: Reddit API, public X search, Discord exports, plus on-chain
    verification of withdrawal claims. Cost: $0.
    """
    lead = (2, 30)
    if not o.has("withdrawal_failure_reports_7d"):
        return unmeasured(407, "social_capitulation", Tier.ABSENCE, lead)

    reports = int(o.get("withdrawal_failure_reports_7d"))
    verified = float(o.get("onchain_corroboration_rate", 0.0))
    aged = float(o.get("aged_account_share", 0.0))

    if reports >= 25 and verified >= 0.50:
        s, why = 0.28, f"{reports} withdrawal-failure reports, {verified:.0%} on-chain corroborated"
    elif reports >= 10 and verified >= 0.30:
        s, why = 0.16, f"{reports} reports, {verified:.0%} corroborated"
    else:
        s, why = 0.0, "no corroborated withdrawal failures"

    if s > 0 and aged < 0.30:
        s *= 0.6
        why += "; discounted for low aged-account share (brigading risk)"

    return SignalScore(407, "social_capitulation", Tier.ABSENCE, s, True, lead, why,
                       {"reports": reports, "corroboration": verified})


TIER4_LAYERS = [
    layer_401_oracle_heartbeat_absence,
    layer_402_proof_posting_absence,
    layer_403_treasury_gas_silence,
    layer_404_attestation_lapse,
    layer_405_user_flow_extinction,
    layer_406_comms_entropy_spike,
    layer_407_social_capitulation,
]
