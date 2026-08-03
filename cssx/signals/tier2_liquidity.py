"""TIER 2 — LIQUIDITY ABANDONMENT (the redemption collapse).

The crypto analogue of "the bank stopped renewing the UCC-1" is "the market
maker pulled the book". These signals measure whether the claim can still be
converted at scale — the only property that matters in a run.
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


# ---------------------------------------------------------------- Layer 201
def layer_201_exit_liquidity_ratio(o: Observation) -> SignalScore:
    """L201 — EXIT LIQUIDITY RATIO (marketcap ÷ 2% depth).

    Measures: how many dollars of order-book + AMM depth exist per dollar of
    circulating value. This is the single best predictor of a -90% gap: the
    price is not wrong, the *depth* is missing.

    Sources: CEX public depth endpoints (Binance/OKX/Coinbase `/depth`),
    on-chain pool reserves via RPC. Cost: $0.
    """
    lead = (3, 45)
    if not o.has("depth_2pct_usd", "circulating_mcap_usd"):
        return unmeasured(201, "exit_liquidity_ratio", Tier.LIQUIDITY, lead)

    depth = float(o.get("depth_2pct_usd"))
    mcap = float(o.get("circulating_mcap_usd"))
    r = safe_ratio(depth, mcap, default=1.0)          # healthy majors ~ 0.3–2%
    d30 = float(o.get("depth_delta_30d_pct", 0.0))

    # Calibration note: liquid majors run 0.05–0.5% of mcap in 2% depth, so the
    # distress thresholds sit an order of magnitude below that band.
    if r < 0.0001:
        s, why = 0.45, f"2% depth is {r:.4%} of mcap — no exit"
    elif r < 0.0003:
        s, why = 0.30, f"2% depth is {r:.4%} of mcap"
    elif r < 0.0006:
        s, why = 0.15, f"thin book ({r:.4%} of mcap)"
    else:
        s, why = 0.0, "depth adequate"

    if s > 0 and d30 <= -0.50:
        s = clamp(s + 0.10, 0, 0.50)
        why += f"; depth -{abs(d30):.0%} in 30d (MM withdrawal)"

    return SignalScore(201, "exit_liquidity_ratio", Tier.LIQUIDITY, s, True, lead, why,
                       {"depth_over_mcap": round(r, 6), "depth_delta_30d": d30})


# ---------------------------------------------------------------- Layer 202
def layer_202_lp_flight(o: Observation) -> SignalScore:
    """L202 — LP FLIGHT / TVL EVAPORATION NET OF PRICE.

    Measures: TVL change *decomposed* — token-denominated TVL removes the
    illusion that a protocol is fine because its own token pumped, and exposes
    real principal withdrawal.

    Sources: DefiLlama free API (`/protocol/{slug}`), pool contract reserves.
    Cost: $0.
    """
    lead = (5, 60)
    if o.asset_class not in (AssetClass.DEFI, AssetClass.L2, AssetClass.STABLE, AssetClass.TOKEN):
        return unmeasured(202, "lp_flight", Tier.LIQUIDITY, lead)
    if not o.has("tvl_native_delta_30d_pct"):
        return unmeasured(202, "lp_flight", Tier.LIQUIDITY, lead)

    dn = float(o.get("tvl_native_delta_30d_pct"))
    top_lp = float(o.get("top_lp_share", 0.0))
    inflow = float(o.get("net_inflow_7d_usd", 0.0))

    if dn <= -0.60:
        s, why = 0.40, f"token-denominated TVL -{abs(dn):.0%} in 30d"
    elif dn <= -0.35:
        s, why = 0.25, f"token-denominated TVL -{abs(dn):.0%} in 30d"
    elif dn <= -0.20:
        s, why = 0.12, f"TVL -{abs(dn):.0%} in 30d"
    else:
        s, why = 0.0, "TVL stable in native terms"

    if s > 0 and top_lp >= 0.40:
        s = clamp(s + 0.08, 0, 0.45)
        why += f"; single LP holds {top_lp:.0%} of remaining liquidity"
    if s > 0 and inflow < 0:
        why += "; net outflow continuing"

    return SignalScore(202, "lp_flight", Tier.LIQUIDITY, s, True, lead, why,
                       {"tvl_native_delta_30d_pct": dn, "top_lp_share": top_lp})


# ---------------------------------------------------------------- Layer 203
def layer_203_peg_and_basis_stress(o: Observation) -> SignalScore:
    """L203 — PEG DEVIATION / VENUE BASIS DISLOCATION (the withdrawal-halt tell).

    Measures: persistent discount of the on-venue or on-chain price against the
    external reference. A token trading at 0.93 on one exchange and 1.00
    everywhere else is not arbitrage failure — it is a withdrawal queue.

    Sources: multi-venue tickers (free public endpoints), Curve/Uniswap pool
    ratios via RPC. Cost: $0.
    """
    lead = (1, 30)
    if not o.has("peg_deviation_bps"):
        return unmeasured(203, "peg_basis_stress", Tier.LIQUIDITY, lead)

    dev = abs(float(o.get("peg_deviation_bps")))
    hours = float(o.get("deviation_persist_hours", 0.0))
    pool_skew = float(o.get("stable_pool_skew", 0.5))   # share of the weak asset

    s = 0.0
    parts = []
    if dev >= 500 and hours >= 24:
        s = 0.50
        parts.append(f"{dev:.0f}bps depeg persisting {hours:.0f}h")
    elif dev >= 200 and hours >= 12:
        s = 0.32
        parts.append(f"{dev:.0f}bps deviation for {hours:.0f}h")
    elif dev >= 75 and hours >= 6:
        s = 0.15
        parts.append(f"{dev:.0f}bps deviation for {hours:.0f}h")

    if s > 0 and pool_skew >= 0.85:
        s = clamp(s + 0.08, 0, 0.55)
        parts.append(f"stable pool {pool_skew:.0%} skewed to weak leg")

    return SignalScore(203, "peg_basis_stress", Tier.LIQUIDITY, s, True, lead,
                       "; ".join(parts) or "peg/basis within tolerance",
                       {"deviation_bps": dev, "persist_hours": hours})


# ---------------------------------------------------------------- Layer 204
def layer_204_reserve_asymmetry(o: Observation) -> SignalScore:
    """L204 — RESERVE ASYMMETRY (the FTX/Celsius detector, generalised).

    Measures: attested reserves vs on-chain liabilities, the share of reserves
    denominated in the entity's *own* token, and whether reserve wallets show
    the pre-audit "snapshot borrow" pattern (large inbound before attestation,
    outbound after).

    Sources: labelled reserve wallets (Arkham/Etherscan free tiers), published
    PoR JSON, exchange liability disclosures. Cost: $0.
    """
    lead = (6, 90)
    if o.asset_class not in (AssetClass.CEX, AssetClass.STABLE, AssetClass.DEFI):
        return unmeasured(204, "reserve_asymmetry", Tier.LIQUIDITY, lead)
    if not o.has("reserves_usd", "liabilities_usd"):
        return unmeasured(204, "reserve_asymmetry", Tier.LIQUIDITY, lead)

    res = float(o.get("reserves_usd"))
    liab = float(o.get("liabilities_usd"))
    cover = safe_ratio(res, liab, default=1.0)
    self_token = float(o.get("self_token_reserve_share", 0.0))
    window = bool(o.get("attestation_window_dressing", False))

    s = 0.0
    parts = []
    if cover < 0.80:
        s += 0.45
        parts.append(f"reserves cover only {cover:.0%} of liabilities")
    elif cover < 0.95:
        s += 0.28
        parts.append(f"reserves cover {cover:.0%} of liabilities")
    elif cover < 1.0:
        s += 0.12
        parts.append(f"marginal shortfall ({cover:.1%})")

    if self_token >= 0.40:
        s += 0.20
        parts.append(f"{self_token:.0%} of reserves are the entity's own token (circular collateral)")
    elif self_token >= 0.20:
        s += 0.10
        parts.append(f"{self_token:.0%} self-token reserves")

    if window:
        s += 0.15
        parts.append("attestation-window borrowing pattern detected")

    s = clamp(s, 0, 0.70)
    return SignalScore(204, "reserve_asymmetry", Tier.LIQUIDITY, s, True, lead,
                       "; ".join(parts) or "reserves adequate",
                       {"coverage": round(cover, 4), "self_token_share": self_token})


# ---------------------------------------------------------------- Layer 205
def layer_205_bridge_reserve_drain(o: Observation) -> SignalScore:
    """L205 — BRIDGE / CANONICAL RESERVE DRAIN.

    Measures: escrow backing on the origin chain against wrapped supply on the
    destination chain. Every large bridge failure in history was visible as a
    backing gap hours before the announcement.

    Sources: escrow contract balances + wrapped-token `totalSupply()` via free
    RPC on both chains. Cost: $0.
    """
    lead = (0, 21)
    if not o.has("bridge_escrow_usd", "wrapped_supply_usd"):
        return unmeasured(205, "bridge_reserve_drain", Tier.LIQUIDITY, lead)

    esc = float(o.get("bridge_escrow_usd"))
    wrp = float(o.get("wrapped_supply_usd"))
    backing = safe_ratio(esc, wrp, default=1.0)
    outflow_24h = float(o.get("bridge_outflow_24h_pct", 0.0))

    if backing < 0.90:
        s, why = 0.55, f"wrapped supply only {backing:.0%} backed"
    elif backing < 0.98:
        s, why = 0.30, f"backing gap ({backing:.1%})"
    elif outflow_24h >= 0.30:
        s, why = 0.20, f"{outflow_24h:.0%} of bridge escrow exited in 24h"
    else:
        s, why = 0.0, "bridge fully backed"

    return SignalScore(205, "bridge_reserve_drain", Tier.LIQUIDITY, s, True, lead, why,
                       {"backing": round(backing, 4), "outflow_24h_pct": outflow_24h})


# ---------------------------------------------------------------- Layer 206
def layer_206_leverage_reflexivity(o: Observation) -> SignalScore:
    """L206 — LEVERAGE REFLEXIVITY / LIQUIDATION SPIRAL PROXIMITY.

    Measures: the fraction of protocol collateral that is the protocol's own
    token, plus how far spot sits above the volume-weighted liquidation band.
    This is the Luna/Terra topology: collateral and liability share one price.

    Sources: lending market subgraphs / on-chain position reads, perp open
    interest and funding from public exchange endpoints. Cost: $0.
    """
    lead = (2, 30)
    if not o.has("self_collateral_share"):
        return unmeasured(206, "leverage_reflexivity", Tier.LIQUIDITY, lead)

    self_c = float(o.get("self_collateral_share"))
    dist = float(o.get("distance_to_liq_band_pct", 1.0))
    funding = float(o.get("perp_funding_8h_bps", 0.0))
    oi_mcap = float(o.get("oi_over_mcap", 0.0))

    s = 0.0
    parts = []
    if self_c >= 0.50:
        s += 0.30
        parts.append(f"{self_c:.0%} of collateral is the protocol's own token")
    elif self_c >= 0.25:
        s += 0.15
        parts.append(f"{self_c:.0%} reflexive collateral")

    if dist <= 0.10:
        s += 0.25
        parts.append(f"spot only {dist:.0%} above liquidation band")
    elif dist <= 0.25:
        s += 0.12
        parts.append(f"spot {dist:.0%} above liquidation band")

    if oi_mcap >= 0.50 and funding <= -30:
        s += 0.10
        parts.append("crowded short-funding with OI > 50% of mcap")

    s = clamp(s, 0, 0.55)
    return SignalScore(206, "leverage_reflexivity", Tier.LIQUIDITY, s, True, lead,
                       "; ".join(parts) or "leverage structure benign",
                       {"self_collateral_share": self_c, "distance_to_liq": dist})


TIER2_LAYERS = [
    layer_201_exit_liquidity_ratio,
    layer_202_lp_flight,
    layer_203_peg_and_basis_stress,
    layer_204_reserve_asymmetry,
    layer_205_bridge_reserve_drain,
    layer_206_leverage_reflexivity,
]
