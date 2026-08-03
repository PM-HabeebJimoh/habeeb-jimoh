"""TIER 3 — OPERATIONAL DISSOLUTION (the corpse).

The humans and institutions behind the contract stop functioning: insiders
move to exchanges, the team stops shipping, the regulator moves, the listing
venues start delisting.
"""

from __future__ import annotations

from ..core import (
    AssetClass,
    Observation,
    SignalScore,
    Tier,
    clamp,
    unmeasured,
)


# ---------------------------------------------------------------- Layer 301
def layer_301_insider_exit_flow(o: Observation) -> SignalScore:
    """L301 — INSIDER / TREASURY EXIT FLOW TO CEX ("the on-chain Form 4").

    Measures: tokens moving from labelled team, treasury, or early-investor
    wallets into exchange deposit addresses, sized against average daily
    volume. Public companies must file Form 4; crypto insiders file a
    transaction — the disclosure is better, it is just unread.

    Sources: Etherscan/Solscan labelled address tags, unlock calendars,
    exchange deposit-address clustering. Cost: $0.
    """
    lead = (1, 30)
    if not o.has("insider_to_cex_usd_30d", "avg_daily_volume_usd"):
        return unmeasured(301, "insider_exit_flow", Tier.OPERATIONAL, lead)

    flow = float(o.get("insider_to_cex_usd_30d"))
    adv = max(float(o.get("avg_daily_volume_usd")), 1.0)
    r = flow / adv
    wallets = int(o.get("distinct_insider_wallets", 0))
    pre_unlock = bool(o.get("pre_unlock_positioning", False))

    if r >= 5:
        s, why = 0.40, f"insider→CEX flow = {r:.1f}x daily volume"
    elif r >= 2:
        s, why = 0.28, f"insider→CEX flow = {r:.1f}x daily volume"
    elif r >= 0.5:
        s, why = 0.15, f"insider→CEX flow = {r:.1f}x daily volume"
    else:
        s, why = 0.0, "no material insider distribution"

    if s > 0 and wallets >= 3:
        s = clamp(s + 0.08, 0, 0.45)
        why += f"; {wallets} distinct insider wallets acting in concert"
    if s > 0 and pre_unlock:
        why += "; positioning ahead of scheduled unlock"

    return SignalScore(301, "insider_exit_flow", Tier.OPERATIONAL, s, True, lead, why,
                       {"flow_over_adv": round(r, 3), "wallets": wallets})


# ---------------------------------------------------------------- Layer 302
def layer_302_repo_abandonment(o: Observation) -> SignalScore:
    """L302 — CORE REPOSITORY ABANDONMENT (technical entropy).

    Measures: commit velocity on core repos, unique active committers, days
    since last release, and open security issues. A protocol whose core client
    has not been touched in 90 days is running on inertia.

    Sources: GitHub REST API (60 req/h unauthenticated, 5,000 with a free PAT).
    Cost: $0.
    """
    lead = (60, 180)
    if not o.has("commits_90d"):
        return unmeasured(302, "repo_abandonment", Tier.OPERATIONAL, lead)

    c90 = int(o.get("commits_90d"))
    devs = int(o.get("unique_committers_90d", 0))
    rel = float(o.get("days_since_release", 0))
    sec_issues = int(o.get("open_security_issues", 0))

    if c90 == 0 and rel > 180:
        s, why = 0.35, f"zero commits in 90d, {rel:.0f}d since release"
    elif c90 < 5 and rel > 90:
        s, why = 0.22, f"{c90} commits in 90d, {rel:.0f}d since release"
    elif devs <= 1 and c90 < 30:
        s, why = 0.15, "single-maintainer bus factor with low velocity"
    else:
        s, why = 0.0, "active development"

    if s > 0 and sec_issues >= 3:
        s = clamp(s + 0.08, 0, 0.40)
        why += f"; {sec_issues} unresolved security issues"

    return SignalScore(302, "repo_abandonment", Tier.OPERATIONAL, s, True, lead, why,
                       {"commits_90d": c90, "committers": devs})


# ---------------------------------------------------------------- Layer 303
def layer_303_governance_quorum_death(o: Observation) -> SignalScore:
    """L303 — GOVERNANCE QUORUM DEATH.

    Measures: proposal cadence, quorum attainment rate, forum activity and
    delegate participation. A DAO that cannot reach quorum cannot respond to
    an exploit — it is an unmanned aircraft.

    Sources: Snapshot GraphQL (free), Tally API, on-chain Governor events,
    Discourse forum JSON. Cost: $0.
    """
    lead = (30, 120)
    if o.asset_class not in (AssetClass.DEFI, AssetClass.L1, AssetClass.L2, AssetClass.TOKEN):
        return unmeasured(303, "governance_quorum_death", Tier.OPERATIONAL, lead)
    if not o.has("proposals_90d"):
        return unmeasured(303, "governance_quorum_death", Tier.OPERATIONAL, lead)

    props = int(o.get("proposals_90d"))
    quorum_rate = float(o.get("quorum_pass_rate", 1.0))
    voters = int(o.get("unique_voters_90d", 0))
    forum = int(o.get("forum_posts_30d", 0))

    s = 0.0
    parts = []
    if props == 0:
        s += 0.20
        parts.append("no governance proposals in 90d")
    if quorum_rate < 0.34 and props > 0:
        s += 0.15
        parts.append(f"only {quorum_rate:.0%} of proposals reached quorum")
    if voters <= 20:
        s += 0.10
        parts.append(f"{voters} unique voters in 90d")
    if forum == 0:
        s += 0.05
        parts.append("forum silent for 30d")

    s = clamp(s, 0, 0.35)
    return SignalScore(303, "governance_quorum_death", Tier.OPERATIONAL, s, True, lead,
                       "; ".join(parts) or "governance functioning",
                       {"proposals_90d": props, "quorum_rate": quorum_rate})


# ---------------------------------------------------------------- Layer 304
def layer_304_regulatory_and_listing_action(o: Observation) -> SignalScore:
    """L304 — REGULATORY ACTION & VENUE DELISTING CASCADE.

    Measures: enforcement actions, OFAC designation, banking-rail loss, and
    delisting/monitoring-tag events across major venues. Two venues delisting
    inside 30 days is a near-deterministic precursor of a liquidity black hole.

    Sources: SEC/CFTC litigation RSS, OFAC SDN list, exchange announcement
    RSS/JSON feeds, CourtListener API. Cost: $0.
    """
    lead = (0, 60)
    if not o.has("delistings_30d"):
        return unmeasured(304, "regulatory_listing_action", Tier.OPERATIONAL, lead)

    delist = int(o.get("delistings_30d"))
    tags = int(o.get("monitoring_tags", 0))
    enforcement = str(o.get("enforcement_status", "none"))   # none|investigation|suit|ofac
    banking = bool(o.get("fiat_rail_lost", False))

    s = 0.0
    parts = []
    if delist >= 2:
        s += 0.35
        parts.append(f"{delist} tier-1 venue delistings in 30d")
    elif delist == 1:
        s += 0.18
        parts.append("one tier-1 venue delisting")
    if tags >= 1:
        s += 0.07
        parts.append(f"{tags} exchange monitoring tags")

    s += {"none": 0.0, "investigation": 0.10, "suit": 0.30, "ofac": 0.60}.get(enforcement, 0.0)
    if enforcement != "none":
        parts.append(f"enforcement status: {enforcement}")
    if banking:
        s += 0.15
        parts.append("fiat on/off ramp lost")

    s = clamp(s, 0, 0.80)
    return SignalScore(304, "regulatory_listing_action", Tier.OPERATIONAL, s, True, lead,
                       "; ".join(parts) or "no regulatory or listing action",
                       {"delistings_30d": delist, "enforcement": enforcement})


# ---------------------------------------------------------------- Layer 305
def layer_305_infra_decay(o: Observation) -> SignalScore:
    """L305 — INFRASTRUCTURE DECAY (RPC, docs, domain, front-end).

    Measures: public RPC availability, docs/front-end HTTP status, domain
    expiry horizon, and IPFS pin liveness. A protocol whose front-end 404s and
    whose domain renews in 20 days has already decided.

    Sources: HTTP HEAD probes, WHOIS expiry, Wayback Machine API, IPFS gateway
    checks. Cost: $0.
    """
    lead = (14, 90)
    if not o.has("frontend_http_status"):
        return unmeasured(305, "infra_decay", Tier.OPERATIONAL, lead)

    status = int(o.get("frontend_http_status"))
    rpc_up = float(o.get("public_rpc_uptime_30d", 1.0))
    domain_days = float(o.get("domain_expiry_days", 365))
    docs_gone = bool(o.get("docs_removed", False))

    s = 0.0
    parts = []
    if status >= 400 or status == 0:
        s += 0.20
        parts.append(f"front-end returns {status}")
    if rpc_up < 0.90:
        s += 0.12
        parts.append(f"public RPC uptime {rpc_up:.0%}")
    if domain_days < 30:
        s += 0.10
        parts.append(f"domain expires in {domain_days:.0f}d")
    if docs_gone:
        s += 0.08
        parts.append("documentation removed")

    s = clamp(s, 0, 0.30)
    return SignalScore(305, "infra_decay", Tier.OPERATIONAL, s, True, lead,
                       "; ".join(parts) or "infrastructure healthy",
                       {"frontend": status, "rpc_uptime": rpc_up})


TIER3_LAYERS = [
    layer_301_insider_exit_flow,
    layer_302_repo_abandonment,
    layer_303_governance_quorum_death,
    layer_304_regulatory_and_listing_action,
    layer_305_infra_decay,
]
