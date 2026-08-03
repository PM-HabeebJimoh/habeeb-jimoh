"""Historical replay fixtures.

Each fixture encodes what CSS-X's data collectors would plausibly have observed
on a given date, using values consistent with the public record. They exist to
validate the *scoring topology* — that mechanical, shadow and hybrid paths fire
where they should and stay quiet where they should — not to claim retroactive
prediction. Every fixture also has a "healthy" control from the same era.
"""

from __future__ import annotations

from datetime import datetime

from .core import UTC, AssetClass, Observation


def _obs(eid, ac, day, **facts) -> Observation:
    return Observation(
        entity_id=eid,
        asset_class=ac,
        ts=datetime.fromisoformat(day).replace(tzinfo=UTC),
        facts=facts,
        sources={"note": "replay fixture reconstructed from public record"},
    )


# --------------------------------------------------------------- distress set
CEX_RESERVE_HOLE = _obs(
    "cex-reserve-hole", AssetClass.CEX, "2022-11-06",
    reserves_usd=5_800_000_000, liabilities_usd=9_000_000_000,
    self_token_reserve_share=0.55, attestation_window_dressing=True,
    depth_2pct_usd=1_200_000, circulating_mcap_usd=3_000_000_000,
    depth_delta_30d_pct=-0.72,
    peg_deviation_bps=650, deviation_persist_hours=36, stable_pool_skew=0.91,
    insider_to_cex_usd_30d=400_000_000, avg_daily_volume_usd=80_000_000,
    distinct_insider_wallets=5,
    days_since_attestation=310, promised_cadence_days=90,
    transparency_page_removed=True,
    unique_depositors_30d=900, depositors_baseline_90d=42_000,
    inflow_30d_usd=0, outflow_30d_usd=1_400_000_000,
    kl_divergence_bits=3.1, reassurance_density=0.41, post_cadence_delta=-0.2,
    withdrawal_failure_reports_7d=140, onchain_corroboration_rate=0.78,
    aged_account_share=0.62,
    days_since_treasury_tx=5, runway_months=1.5, treasury_stable_share=0.05,
    delistings_30d=1, enforcement_status="investigation",
    frontend_http_status=200, public_rpc_uptime_30d=1.0,
)

REFLEXIVE_STABLE = _obs(
    "reflexive-stablecoin", AssetClass.STABLE, "2022-05-09",
    peg_deviation_bps=420, deviation_persist_hours=18, stable_pool_skew=0.93,
    reserves_usd=1_500_000_000, liabilities_usd=18_000_000_000,
    self_token_reserve_share=0.70,
    depth_2pct_usd=9_000_000, circulating_mcap_usd=18_000_000_000,
    depth_delta_30d_pct=-0.55,
    self_collateral_share=0.82, distance_to_liq_band_pct=0.06,
    oi_over_mcap=0.55, perp_funding_8h_bps=-45,
    tvl_native_delta_30d_pct=-0.48,
    upgrade_control="multisig", timelock_delay_hours=0, escape_hatch_working=True,
    oracle_staleness_s=1800, oracle_heartbeat_s=600,
    kl_divergence_bits=2.7, reassurance_density=0.33,
    unique_depositors_30d=5_000, depositors_baseline_90d=60_000,
    inflow_30d_usd=50_000_000, outflow_30d_usd=3_000_000_000,
    withdrawal_failure_reports_7d=30, onchain_corroboration_rate=0.55,
    aged_account_share=0.5,
)

ABANDONED_DEFI = _obs(
    "abandoned-defi", AssetClass.DEFI, "2024-03-01",
    # Nothing mechanical is broken yet — pure Path B shadow convergence.
    commits_90d=0, unique_committers_90d=0, days_since_release=420,
    open_security_issues=4,
    proposals_90d=0, quorum_pass_rate=0.0, unique_voters_90d=7, forum_posts_30d=0,
    days_since_treasury_tx=120, runway_months=2.0, treasury_stable_share=0.04,
    days_since_attestation=500, promised_cadence_days=180, auditor_resigned=True,
    oracle_staleness_s=90_000, oracle_heartbeat_s=3600, dead_feed_count=2,
    unique_depositors_30d=40, depositors_baseline_90d=3_000,
    inflow_30d_usd=0, outflow_30d_usd=4_000_000,
    kl_divergence_bits=1.9, reassurance_density=0.1, post_cadence_delta=-0.9,
    frontend_http_status=404, public_rpc_uptime_30d=0.62, domain_expiry_days=22,
    docs_removed=True,
    tvl_native_delta_30d_pct=-0.66, top_lp_share=0.55,
    depth_2pct_usd=40_000, circulating_mcap_usd=90_000_000, depth_delta_30d_pct=-0.6,
    upgrade_control="eoa", timelock_delay_hours=0, escape_hatch_working=False,
)

STALLED_L2 = _obs(
    "stalled-rollup", AssetClass.L2, "2025-06-15",
    seconds_since_final_block=9_000, target_block_time_s=2,
    incident_ack=False,
    hours_since_state_root=96, expected_root_cadence_h=6,
    pending_withdrawals_usd=48_000_000,
    bridge_escrow_usd=210_000_000, wrapped_supply_usd=260_000_000,
    bridge_outflow_24h_pct=0.34,
    upgrade_control="multisig", timelock_delay_hours=2,
    escape_hatch_working=False, sequencer_downtime_24h_hours=14,
    depth_2pct_usd=300_000, circulating_mcap_usd=400_000_000, depth_delta_30d_pct=-0.65,
    stake_delta_30d_pct=-0.22, exit_queue_pct_of_stake=0.09,
    validator_stake_weights=[60, 20, 10, 5, 5],
    commits_90d=3, unique_committers_90d=1, days_since_release=200,
    days_since_treasury_tx=40, runway_months=4,
    unique_depositors_30d=800, depositors_baseline_90d=25_000,
    inflow_30d_usd=0, outflow_30d_usd=90_000_000,
)

# ---------------------------------------------------------------- control set
HEALTHY_L1 = _obs(
    "healthy-l1", AssetClass.L1, "2025-06-15",
    seconds_since_final_block=13, target_block_time_s=12, incident_ack=True,
    stake_delta_30d_pct=0.03, exit_queue_pct_of_stake=0.01,
    validator_stake_weights=[8, 7, 7, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    cost_to_attack_usd=40_000_000_000, value_secured_usd=60_000_000_000,
    holder_weights=[5, 5, 4, 4, 4, 4, 3, 3, 3, 3], holder_entropy_baseline_90d=3.3,
    depth_2pct_usd=180_000_000, circulating_mcap_usd=300_000_000_000,
    depth_delta_30d_pct=0.05,
    commits_90d=1400, unique_committers_90d=90, days_since_release=21,
    proposals_90d=12, quorum_pass_rate=0.9, unique_voters_90d=4000, forum_posts_30d=300,
    days_since_treasury_tx=1, runway_months=60, treasury_stable_share=0.4,
    unique_depositors_30d=900_000, depositors_baseline_90d=880_000,
    inflow_30d_usd=2_000_000_000, outflow_30d_usd=1_900_000_000,
    kl_divergence_bits=0.4, reassurance_density=0.01, post_cadence_delta=0.1,
    frontend_http_status=200, public_rpc_uptime_30d=0.999, domain_expiry_days=800,
    delistings_30d=0, enforcement_status="none",
)

HEALTHY_CEX = _obs(
    "healthy-cex", AssetClass.CEX, "2025-06-15",
    reserves_usd=11_000_000_000, liabilities_usd=10_200_000_000,
    self_token_reserve_share=0.06, attestation_window_dressing=False,
    depth_2pct_usd=60_000_000, circulating_mcap_usd=8_000_000_000, depth_delta_30d_pct=0.02,
    peg_deviation_bps=8, deviation_persist_hours=1,
    insider_to_cex_usd_30d=2_000_000, avg_daily_volume_usd=900_000_000,
    days_since_attestation=25, promised_cadence_days=30,
    unique_depositors_30d=310_000, depositors_baseline_90d=300_000,
    inflow_30d_usd=4_000_000_000, outflow_30d_usd=3_800_000_000,
    kl_divergence_bits=0.6, reassurance_density=0.02,
    withdrawal_failure_reports_7d=1, onchain_corroboration_rate=0.0,
    aged_account_share=0.4,
    days_since_treasury_tx=1, runway_months=48, treasury_stable_share=0.6,
    delistings_30d=0, enforcement_status="none",
    frontend_http_status=200, public_rpc_uptime_30d=0.999,
)

# A stressed-but-solvable case: real signals, real rescue evidence.
RESCUED_PROTOCOL = _obs(
    "rescued-protocol", AssetClass.DEFI, "2025-02-01",
    tvl_native_delta_30d_pct=-0.42, top_lp_share=0.30,
    depth_2pct_usd=900_000, circulating_mcap_usd=250_000_000, depth_delta_30d_pct=-0.4,
    commits_90d=210, unique_committers_90d=9, days_since_release=15,
    proposals_90d=4, quorum_pass_rate=0.75, unique_voters_90d=900, forum_posts_30d=140,
    days_since_treasury_tx=1, runway_months=18, treasury_stable_share=0.7,
    days_since_attestation=40, promised_cadence_days=90,
    verified_raise_30d_usd=25_000_000, large_withdrawal_honoured_7d=True,
    frontend_http_status=200, public_rpc_uptime_30d=0.99,
    upgrade_control="timelock", timelock_delay_hours=72, escape_hatch_working=True,
)

DISTRESS_FIXTURES = [CEX_RESERVE_HOLE, REFLEXIVE_STABLE, ABANDONED_DEFI, STALLED_L2]
CONTROL_FIXTURES = [HEALTHY_L1, HEALTHY_CEX, RESCUED_PROTOCOL]
ALL_FIXTURES = DISTRESS_FIXTURES + CONTROL_FIXTURES

# Persistence histories as the daily cron would have accumulated them.
FIXTURE_HISTORIES: dict[str, dict[int, int]] = {
    "cex-reserve-hole": {l: 12 for l in (201, 203, 204, 301, 404, 405, 406, 407)},
    "reflexive-stablecoin": {l: 6 for l in (201, 203, 204, 206, 401, 405, 406)},
    "abandoned-defi": {l: 30 for l in (302, 303, 305, 401, 403, 404, 405, 103, 202)},
    "stalled-rollup": {l: 5 for l in (101, 103, 205, 402, 201, 405)},
}
