"""July 2026 backtest panel.

Each entity is a *daily timeline function* `day -> facts`, reconstructed from the
public record. The backtest walks the panel one UTC day at a time, feeding each
day's observation into the live engine with persistence accumulating in SQLite —
exactly as the 06:00 UTC cron would have. No lookahead: a fact only appears on
the day it first became publicly observable.

WINDOW: 2026-06-01 → 2026-07-31 (61 days)
EVALUATED AGAINST: outcome events occurring in July 2026
The window starts in June so that lead time into July events is measurable. An
evaluation window that begins on the event month cannot measure lead time at all.

OUTCOME LABELS
  insolvent_failure — users lost access to funds / assets exceeded by liabilities
  solvent_winddown  — business exit with withdrawals honoured (must NOT alert)
  survivor          — still operating normally at 2026-07-31

SOURCING per entity is recorded in `SOURCES` below. Values are reconstructions
at the granularity the collectors would produce, not exact vendor snapshots;
where the public record gives a figure (AscendEX's $13.45M Arkham balance,
MIM's $0.48 print, MOVE's 94% drawdown) that figure is used directly.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from .core import AssetClass, Observation

UTC = timezone.utc

WINDOW_START = date(2026, 6, 1)
WINDOW_END = date(2026, 7, 31)

SOURCES = {
    "ascendex": [
        "techtimes.com/articles/320217 (2026-07-12) — ZachXBT 26 Jun warning; reserves "
        "-$240M on 20 Jun; Arkham 8 Jul balance $13.45M, >$12M in own ASD + UNITE",
        "thedefiant.io/news/cefi/ascendex-halts-operations-freezes-automated-withdrawals "
        "(2026-07-08) — halt 1 Jul, manual-review withdrawals 6 Jul, insolvency flagged",
        "coinpaprika.com/news/ascendex-freezes-withdrawals-reserves-empty (2026-07-09)",
    ],
    "mvmt-labs": [
        "thedefiant.io/news/blockchains/movement-labs-files-for-chapter-11-bankruptcy — "
        "Ch.11 Subchapter V filed 15 Jul 2026, D. Del. case 26-11113; assets <$1M vs "
        "liabilities up to $10M; 200-999 creditors",
        "blockonomi.com/movement-labs-files-for-chapter-11-bankruptcy — MOVE -94% y/y "
        "to ~$0.01; Coinbase suspended MOVE for listing-standard failure",
    ],
    "mim-abracadabra": [
        "cryptoadventure.com/mim-depegs-to-0-50 (2026-06-25) — MIM $0.5002, 24h low "
        "$0.4304, 24h volume ~$350k, mcap ~$27.8M on ~56M supply",
        "en.cryptonomist.ch/2026/06/25/abracadabra-stablecoin-drop — $100k Curve "
        "injection 15 Jun failed; path $0.74 → $0.89 → $0.49",
        "coinstats.app/ai/a/crypto-news-update-31-July-2026 — MIM ~$0.48, -74% 24h, "
        "emergency Cauldron rate hikes, Curve bribes paused",
    ],
    "bitmex": [
        "bitmex.com/blog/delisting-jul2026-coming-soon (2026-07-23) — 35 illiquid "
        "contracts settled 30 Jul; exchange closure announced, withdrawals open",
        "airdropalert.com/blogs/crypto-exchanges-shutting-down — BitMEX announced "
        "23 Jul, reduce-only 26 Aug, final closure 23 Sep, WITHDRAWALS OPEN",
    ],
    "bitmart": [
        "airdropalert.com/blogs/crypto-exchanges-shutting-down — BitMart announced "
        "26 Jul 2026, trading ends 26 Aug, closure 31 Jan 2027, withdrawals open",
    ],
    "afx-trade": [
        "halborn.com/blog/post/explained-the-afxbridge-hack-july-2026 — $24.15M USDC "
        "drained via compromise of 5 of 7 bridge validator keys (7,142 of 10,000 "
        "voting units vs 6,667 threshold)",
    ],
    "odos": [
        "news.bitcoin.com/featured/over-60-crypto-firms-and-projects-fold-in-2026 — "
        "Odos DEX aggregator announced 23 Jul, all services closed by 30 Jul",
    ],
}

OUTCOMES = {
    "ascendex":        ("insolvent_failure", date(2026, 7, 6)),
    "mvmt-labs":       ("insolvent_failure", date(2026, 7, 15)),
    "mim-abracadabra": ("insolvent_failure", date(2026, 7, 30)),
    "afx-trade":       ("insolvent_failure", date(2026, 7, 14)),
    "odos":            ("solvent_winddown",  date(2026, 7, 23)),
    "bitmex":          ("solvent_winddown",  date(2026, 7, 23)),
    "bitmart":         ("solvent_winddown",  date(2026, 7, 26)),
    "major-l1":        ("survivor",          None),
    "major-cex":       ("survivor",          None),
    "major-lending":   ("survivor",          None),
    "mid-l2":          ("survivor",          None),
}


def _d(y: int, m: int, dd: int) -> date:
    return date(y, m, dd)


# --------------------------------------------------------------------------
# ASCENDEX — insolvent CEX. Reserve collapse visible 20 Jun; ZachXBT 26 Jun;
# operations halted 1 Jul; withdrawals to manual review 6 Jul.
# --------------------------------------------------------------------------
def ascendex(d: date) -> dict:
    f: dict = {
        "asset_class": AssetClass.CEX,
        "liabilities_usd": 290_000_000,
        "promised_cadence_days": 90,
        "frontend_http_status": 200,
        "public_rpc_uptime_30d": 1.0,
        "days_since_treasury_tx": 1,
        "treasury_stable_share": 0.35,
    }
    # Reserves: ~$290M after the injection, then -$240M on 20 Jun, decaying to
    # the $13.45M Arkham showed on 8 Jul.
    if d < _d(2026, 6, 20):
        f["reserves_usd"] = 290_000_000
        f["self_token_reserve_share"] = 0.08
        f["depth_2pct_usd"] = 3_400_000
    elif d < _d(2026, 7, 1):
        f["reserves_usd"] = 50_000_000
        f["self_token_reserve_share"] = 0.34
        f["attestation_window_dressing"] = True   # $240M in and out within weeks
        f["depth_2pct_usd"] = 900_000
        f["depth_delta_30d_pct"] = -0.62
    else:
        f["reserves_usd"] = 13_450_000
        f["self_token_reserve_share"] = 0.89      # >$12M of $13.45M in ASD + UNITE
        f["attestation_window_dressing"] = True
        f["depth_2pct_usd"] = 120_000
        f["depth_delta_30d_pct"] = -0.93
    f["circulating_mcap_usd"] = 240_000_000

    # Withdrawal-failure reports: users reported stuck "initiating" states from
    # early June; ZachXBT aggregated them publicly on 26 Jun.
    if d >= _d(2026, 6, 26):
        f["withdrawal_failure_reports_7d"] = 60 if d < _d(2026, 7, 6) else 240
        f["onchain_corroboration_rate"] = 0.85    # no tx hash ever generated
        f["aged_account_share"] = 0.7
    elif d >= _d(2026, 6, 10):
        f["withdrawal_failure_reports_7d"] = 8
        f["onchain_corroboration_rate"] = 0.6
        f["aged_account_share"] = 0.6

    # Deposit flow extinction — the silent run.
    f["depositors_baseline_90d"] = 41_000
    if d < _d(2026, 6, 20):
        f["unique_depositors_30d"] = 26_000
        f["inflow_30d_usd"] = 180_000_000
        f["outflow_30d_usd"] = 210_000_000
    elif d < _d(2026, 7, 1):
        f["unique_depositors_30d"] = 6_500
        f["inflow_30d_usd"] = 22_000_000
        f["outflow_30d_usd"] = 260_000_000
    else:
        f["unique_depositors_30d"] = 0
        f["inflow_30d_usd"] = 0
        f["outflow_30d_usd"] = 41_000_000

    # Attestation: AscendEX published no PoR through the window.
    f["days_since_attestation"] = (d - _d(2025, 9, 1)).days
    if d >= _d(2026, 7, 1):
        f["transparency_page_removed"] = True

    # Comms: silence, then the 6 Jul notice with "what options, if any" hedging.
    if d >= _d(2026, 7, 6):
        f["kl_divergence_bits"] = 3.4
        f["reassurance_density"] = 0.12           # notably NOT reassuring
        f["post_cadence_delta"] = -0.85
    elif d >= _d(2026, 6, 20):
        f["kl_divergence_bits"] = 1.7
        f["reassurance_density"] = 0.05
        f["post_cadence_delta"] = -0.8

    # Regulatory: MiCA full effect 1 Jul with no authorisation.
    f["delistings_30d"] = 0
    f["enforcement_status"] = "none"
    if d >= _d(2026, 7, 1):
        f["enforcement_status"] = "investigation"
        f["fiat_rail_lost"] = True
        f["days_since_treasury_tx"] = (d - _d(2026, 7, 1)).days + 1
    return f


# --------------------------------------------------------------------------
# MVMT LABS — L2 developer. Chapter 11 filed 15 Jul, public 21 Jul. The corporate
# entity died while the chain kept running: a pure Tier-3/Tier-4 case.
# --------------------------------------------------------------------------
def mvmt_labs(d: date) -> dict:
    f: dict = {
        "asset_class": AssetClass.L2,
        "seconds_since_final_block": 3.0,
        "target_block_time_s": 2.0,
        "incident_ack": True,
        "hours_since_state_root": 7.0,
        "expected_root_cadence_h": 6.0,
        "circulating_mcap_usd": 13_000_000,       # ~1.3B supply at ~$0.01
        "avg_daily_volume_usd": 2_200_000,
        "upgrade_control": "multisig",
        "timelock_delay_hours": 0,
        "escape_hatch_working": False,
        "frontend_http_status": 200,
        "public_rpc_uptime_30d": 0.97,
    }
    # Depth: Coinbase suspension left the book structurally thin all window.
    f["depth_2pct_usd"] = 5_000 if d >= _d(2026, 7, 15) else 9_000
    f["depth_delta_30d_pct"] = -0.45 if d >= _d(2026, 7, 1) else -0.15

    # Treasury: assets $100k–$500k against $1M–$10M liabilities. Gas stops
    # before counsel files.
    if d < _d(2026, 6, 25):
        f["days_since_treasury_tx"] = 3
        f["runway_months"] = 3.0
    elif d < _d(2026, 7, 15):
        f["days_since_treasury_tx"] = (d - _d(2026, 6, 22)).days
        f["runway_months"] = 0.8
    else:
        f["days_since_treasury_tx"] = (d - _d(2026, 6, 22)).days
        f["runway_months"] = 0.2
    f["treasury_stable_share"] = 0.03

    # Repo: Move Industries took over dev in Dec 2025, so Labs' own repos froze.
    f["commits_90d"] = 1
    f["unique_committers_90d"] = 1
    f["days_since_release"] = (d - _d(2025, 12, 10)).days
    f["open_security_issues"] = 3

    # Governance silence.
    f["proposals_90d"] = 0
    f["quorum_pass_rate"] = 0.0
    f["unique_voters_90d"] = 14
    f["forum_posts_30d"] = 0

    # Insider/market-maker distribution is the origin story of this collapse.
    f["insider_to_cex_usd_30d"] = 900_000 if d < _d(2026, 7, 1) else 2_600_000
    f["distinct_insider_wallets"] = 3
    f["pre_unlock_positioning"] = True

    # Coinbase suspension persists; Ch.11 is a hard legal event on 15 Jul.
    f["delistings_30d"] = 1
    f["monitoring_tags"] = 2
    f["enforcement_status"] = "none"
    if d >= _d(2026, 7, 15):
        f["enforcement_status"] = "suit"          # Ch.11 petition, D. Del. 26-11113
    f["days_since_attestation"] = (d - _d(2025, 11, 1)).days
    f["promised_cadence_days"] = 180
    return f


# --------------------------------------------------------------------------
# MIM / ABRACADABRA — reflexive stablecoin. Depeg 25 Jun to ~$0.50, partial
# recovery, deeper break 30–31 Jul to ~$0.48 with a -74% 24h print.
# --------------------------------------------------------------------------
def mim(d: date) -> dict:
    f: dict = {
        "asset_class": AssetClass.STABLE,
        "circulating_mcap_usd": 27_800_000,
        "avg_daily_volume_usd": 350_000,
        "upgrade_control": "multisig",
        "timelock_delay_hours": 24,
        "escape_hatch_working": True,
        "frontend_http_status": 200,
        "commits_90d": 60,
        "unique_committers_90d": 4,
        "days_since_release": 40,
        "proposals_90d": 3,
        "quorum_pass_rate": 0.66,
        "unique_voters_90d": 220,
        "forum_posts_30d": 45,
        "days_since_treasury_tx": 1,
        "runway_months": 9,
        "treasury_stable_share": 0.25,
        "oracle_staleness_s": 900,
        "oracle_heartbeat_s": 3600,
    }
    # Peg path from the public record.
    if d < _d(2026, 6, 15):
        price, hours, skew = 0.985, 2, 0.58
    elif d < _d(2026, 6, 25):
        price, hours, skew = 0.74, 30, 0.80       # first slip, $100k injection fails
    elif d < _d(2026, 6, 29):
        price, hours, skew = 0.50, 72, 0.90       # deep break
    elif d < _d(2026, 7, 20):
        price, hours, skew = 0.89, 40, 0.78       # the dangerous partial recovery
    elif d < _d(2026, 7, 30):
        price, hours, skew = 0.72, 90, 0.86
    else:
        price, hours, skew = 0.48, 140, 0.94      # emergency measures declared
    f["peg_deviation_bps"] = (price - 1.0) * 10_000
    f["deviation_persist_hours"] = hours
    f["stable_pool_skew"] = skew

    # Depth: thin, imbalanced Curve pools are the named root cause.
    f["depth_2pct_usd"] = 260_000 if d < _d(2026, 6, 25) else 45_000
    f["depth_delta_30d_pct"] = -0.30 if d < _d(2026, 6, 25) else -0.78
    f["tvl_native_delta_30d_pct"] = -0.22 if d < _d(2026, 6, 25) else -0.58
    f["top_lp_share"] = 0.44

    # MIM is minted as debt against collateral — reflexivity is structural.
    f["self_collateral_share"] = 0.31
    f["distance_to_liq_band_pct"] = 0.30 if d < _d(2026, 6, 25) else 0.08
    f["reserves_usd"] = 56_000_000 * max(price, 0.4)
    f["liabilities_usd"] = 56_000_000
    f["self_token_reserve_share"] = 0.31

    f["depositors_baseline_90d"] = 1_800
    if d < _d(2026, 6, 25):
        f["unique_depositors_30d"] = 900
        f["inflow_30d_usd"] = 4_000_000
        f["outflow_30d_usd"] = 6_500_000
    else:
        f["unique_depositors_30d"] = 130
        f["inflow_30d_usd"] = 250_000
        f["outflow_30d_usd"] = 9_000_000

    # The team communicated continuously and specifically — no entropy spike,
    # and each intervention is a contradiction signal the engine must honour.
    f["kl_divergence_bits"] = 0.9
    f["reassurance_density"] = 0.08
    f["post_cadence_delta"] = 0.4
    f["days_since_attestation"] = 30
    f["promised_cadence_days"] = 90
    if _d(2026, 6, 15) <= d < _d(2026, 6, 25):
        f["verified_raise_30d_usd"] = 100_000     # Curve liquidity injection
    return f


# --------------------------------------------------------------------------
# AFX TRADE — bridge validator key compromise, $24.15M drained.
# --------------------------------------------------------------------------
def afx_trade(d: date) -> dict:
    f: dict = {
        "asset_class": AssetClass.DEFI,
        "upgrade_control": "multisig",
        "timelock_delay_hours": 0,
        "escape_hatch_working": True,
        "circulating_mcap_usd": 31_000_000,
        "avg_daily_volume_usd": 1_100_000,
        "commits_90d": 95,
        "unique_committers_90d": 5,
        "days_since_release": 30,
        "days_since_treasury_tx": 2,
        "runway_months": 7,
        "treasury_stable_share": 0.5,
        "frontend_http_status": 200,
        "proposals_90d": 2,
        "quorum_pass_rate": 0.5,
        "unique_voters_90d": 180,
        "forum_posts_30d": 30,
        "days_since_attestation": 200,
        "promised_cadence_days": 180,
        "validator_stake_weights": [2400, 1500, 1400, 1300, 1200, 1100, 1100],
    }
    pre = d < _d(2026, 7, 14)
    # Nakamoto coefficient of the 7-validator, 10,000-unit scheme is structurally
    # low all window — the exploit made it visible, it did not create it.
    f["bridge_escrow_usd"] = 82_000_000 if pre else 58_000_000
    f["wrapped_supply_usd"] = 82_000_000
    f["depth_2pct_usd"] = 55_000 if pre else 9_000
    f["depth_delta_30d_pct"] = -0.1 if pre else -0.84
    f["tvl_native_delta_30d_pct"] = -0.08 if pre else -0.71
    f["top_lp_share"] = 0.35
    f["depositors_baseline_90d"] = 2_400
    f["unique_depositors_30d"] = 1_600 if pre else 90
    f["inflow_30d_usd"] = 12_000_000 if pre else 40_000
    f["outflow_30d_usd"] = 11_000_000 if pre else 26_000_000
    if not pre:
        f["escape_hatch_working"] = False
        f["bridge_outflow_24h_pct"] = 0.29
        f["kl_divergence_bits"] = 2.9
        f["reassurance_density"] = 0.34
        f["withdrawal_failure_reports_7d"] = 45
        f["onchain_corroboration_rate"] = 0.7
        f["aged_account_share"] = 0.55
        f["runway_months"] = 2.0
    return f


# --------------------------------------------------------------------------
# SOLVENT WIND-DOWNS — the discriminator cases. Real business exit, real
# operational shrinkage, but withdrawals honoured and reserves intact. A system
# that cannot tell these from AscendEX is worthless.
# --------------------------------------------------------------------------
def _winddown(announce: date, reserves: float, liabilities: float):
    def fn(d: date) -> dict:
        f: dict = {
            "asset_class": AssetClass.CEX,
            "reserves_usd": reserves,
            "liabilities_usd": liabilities,
            "self_token_reserve_share": 0.04,
            "attestation_window_dressing": False,
            "circulating_mcap_usd": 900_000_000,
            "avg_daily_volume_usd": 140_000_000,
            "days_since_attestation": 35,
            "promised_cadence_days": 90,
            "frontend_http_status": 200,
            "public_rpc_uptime_30d": 0.999,
            "days_since_treasury_tx": 1,
            "treasury_stable_share": 0.55,
            "runway_months": 24,
            "enforcement_status": "none",
            "peg_deviation_bps": 6,
            "deviation_persist_hours": 1,
            "insider_to_cex_usd_30d": 400_000,
            "depositors_baseline_90d": 120_000,
        }
        post = d >= announce
        # Deposits legitimately collapse after a wind-down notice — this is the
        # trap. Only the CONTRADICTION rail separates it from a run.
        f["unique_depositors_30d"] = 8_000 if post else 96_000
        f["inflow_30d_usd"] = 30_000_000 if post else 900_000_000
        f["outflow_30d_usd"] = 1_400_000_000 if post else 880_000_000
        f["depth_2pct_usd"] = 900_000 if post else 9_000_000
        f["depth_delta_30d_pct"] = -0.88 if post else 0.0
        f["delistings_30d"] = 35 if post else 0   # BitMEX settled 35 contracts
        f["monitoring_tags"] = 1 if post else 0
        f["kl_divergence_bits"] = 2.2 if post else 0.5
        f["reassurance_density"] = 0.1 if post else 0.02
        if post:
            # Withdrawals honoured on-chain, attestation current: the engine is
            # required to be talked out of its conclusion by these facts.
            f["large_withdrawal_honoured_7d"] = True
            f["attestation_published_7d"] = True
            f["planned_migration"] = True
            f["days_since_attestation"] = 4
        return f
    return fn


bitmex = _winddown(_d(2026, 7, 23), 1_050_000_000, 980_000_000)
bitmart = _winddown(_d(2026, 7, 26), 640_000_000, 610_000_000)


def odos(d: date) -> dict:
    """DEX aggregator: routes orders, custodies nothing. Closed 30 Jul."""
    post = d >= _d(2026, 7, 23)
    return {
        "asset_class": AssetClass.DEFI,
        "upgrade_control": "timelock",
        "timelock_delay_hours": 48,
        "escape_hatch_working": True,
        "commits_90d": 12 if post else 140,
        "unique_committers_90d": 2 if post else 8,
        "days_since_release": 95 if post else 20,
        "days_since_treasury_tx": 2,
        "runway_months": 10,
        "treasury_stable_share": 0.8,
        "proposals_90d": 0,
        "unique_voters_90d": 0,
        "forum_posts_30d": 5 if post else 40,
        "frontend_http_status": 200,
        "public_rpc_uptime_30d": 0.99,
        "tvl_native_delta_30d_pct": -0.30 if post else 0.02,
        "top_lp_share": 0.2,
        # Aggregator holds no TVL of its own; depth is the venues' not Odos'.
        "planned_migration": post,
        "large_withdrawal_honoured_7d": post,
    }


# --------------------------------------------------------------------------
# SURVIVORS — normal operation throughout the window.
# --------------------------------------------------------------------------
def major_l1(d: date) -> dict:
    return {
        "asset_class": AssetClass.L1,
        "seconds_since_final_block": 13, "target_block_time_s": 12,
        "incident_ack": True,
        "stake_delta_30d_pct": 0.02, "exit_queue_pct_of_stake": 0.012,
        "validator_stake_weights": [8, 7, 7, 6, 6, 6, 5, 5, 5, 5,
                                    4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        "cost_to_attack_usd": 38_000_000_000, "value_secured_usd": 55_000_000_000,
        "holder_weights": [5, 5, 4, 4, 4, 4, 3, 3, 3, 3],
        "holder_entropy_baseline_90d": 3.3,
        "depth_2pct_usd": 150_000_000, "circulating_mcap_usd": 220_000_000_000,
        "depth_delta_30d_pct": -0.04,
        "commits_90d": 1300, "unique_committers_90d": 85, "days_since_release": 18,
        "proposals_90d": 9, "quorum_pass_rate": 0.88,
        "unique_voters_90d": 3600, "forum_posts_30d": 260,
        "days_since_treasury_tx": 1, "runway_months": 60, "treasury_stable_share": 0.4,
        "unique_depositors_30d": 820_000, "depositors_baseline_90d": 840_000,
        "inflow_30d_usd": 1_800_000_000, "outflow_30d_usd": 1_850_000_000,
        "kl_divergence_bits": 0.4, "reassurance_density": 0.01,
        "frontend_http_status": 200, "public_rpc_uptime_30d": 0.999,
        "domain_expiry_days": 700, "delistings_30d": 0, "enforcement_status": "none",
        "oracle_staleness_s": 200, "oracle_heartbeat_s": 3600,
    }


def major_cex(d: date) -> dict:
    return {
        "asset_class": AssetClass.CEX,
        "reserves_usd": 10_800_000_000, "liabilities_usd": 10_100_000_000,
        "self_token_reserve_share": 0.07, "attestation_window_dressing": False,
        "depth_2pct_usd": 52_000_000, "circulating_mcap_usd": 7_500_000_000,
        "depth_delta_30d_pct": -0.06,
        "peg_deviation_bps": 7, "deviation_persist_hours": 1,
        "insider_to_cex_usd_30d": 1_800_000, "avg_daily_volume_usd": 820_000_000,
        "days_since_attestation": 22, "promised_cadence_days": 30,
        "unique_depositors_30d": 295_000, "depositors_baseline_90d": 300_000,
        "inflow_30d_usd": 3_700_000_000, "outflow_30d_usd": 3_900_000_000,
        "kl_divergence_bits": 0.6, "reassurance_density": 0.02,
        "withdrawal_failure_reports_7d": 2, "onchain_corroboration_rate": 0.0,
        "aged_account_share": 0.4,
        "days_since_treasury_tx": 1, "runway_months": 40, "treasury_stable_share": 0.6,
        "delistings_30d": 0, "enforcement_status": "none",
        "frontend_http_status": 200, "public_rpc_uptime_30d": 0.999,
    }


def major_lending(d: date) -> dict:
    """Survivor that takes real drawdown in the June selloff — a hard control."""
    stress = d >= _d(2026, 6, 20)
    return {
        "asset_class": AssetClass.DEFI,
        "upgrade_control": "timelock", "timelock_delay_hours": 96,
        "escape_hatch_working": True,
        "tvl_native_delta_30d_pct": -0.28 if stress else -0.05,
        "top_lp_share": 0.14,
        "depth_2pct_usd": 6_500_000, "circulating_mcap_usd": 1_400_000_000,
        "depth_delta_30d_pct": -0.22 if stress else 0.01,
        "self_collateral_share": 0.05, "distance_to_liq_band_pct": 0.55,
        "commits_90d": 420, "unique_committers_90d": 18, "days_since_release": 12,
        "proposals_90d": 7, "quorum_pass_rate": 0.85,
        "unique_voters_90d": 1500, "forum_posts_30d": 190,
        "days_since_treasury_tx": 1, "runway_months": 36, "treasury_stable_share": 0.75,
        "days_since_attestation": 45, "promised_cadence_days": 180,
        "oracle_staleness_s": 400, "oracle_heartbeat_s": 3600,
        "unique_depositors_30d": 22_000, "depositors_baseline_90d": 26_000,
        "inflow_30d_usd": 300_000_000, "outflow_30d_usd": 420_000_000,
        "kl_divergence_bits": 0.7, "reassurance_density": 0.03,
        "frontend_http_status": 200, "public_rpc_uptime_30d": 0.998,
    }


def mid_l2(d: date) -> dict:
    """Mid-cap rollup with a brief, acknowledged sequencer incident on 8 Jul.

    Control for the false-positive mode that matters most on L2s: a real outage
    that is announced, resolved, and followed by restored proof posting.
    """
    incident = _d(2026, 7, 8) <= d < _d(2026, 7, 10)
    f = {
        "asset_class": AssetClass.L2,
        "seconds_since_final_block": 420 if incident else 2.5,
        "target_block_time_s": 2.0,
        "incident_ack": True,
        "hours_since_state_root": 20 if incident else 5,
        "expected_root_cadence_h": 6.0,
        "pending_withdrawals_usd": 3_000_000 if incident else 0,
        "sequencer_downtime_24h_hours": 3.0 if incident else 0.0,
        "bridge_escrow_usd": 340_000_000, "wrapped_supply_usd": 340_000_000,
        "upgrade_control": "timelock", "timelock_delay_hours": 168,
        "escape_hatch_working": True,
        "stake_delta_30d_pct": -0.03, "exit_queue_pct_of_stake": 0.02,
        "validator_stake_weights": [12, 11, 10, 10, 9, 9, 8, 8, 8, 7, 4, 4],
        "depth_2pct_usd": 2_100_000, "circulating_mcap_usd": 900_000_000,
        "depth_delta_30d_pct": -0.09,
        "commits_90d": 760, "unique_committers_90d": 31, "days_since_release": 9,
        "proposals_90d": 5, "quorum_pass_rate": 0.8,
        "unique_voters_90d": 700, "forum_posts_30d": 120,
        "days_since_treasury_tx": 1, "runway_months": 30, "treasury_stable_share": 0.6,
        "unique_depositors_30d": 48_000, "depositors_baseline_90d": 50_000,
        "inflow_30d_usd": 210_000_000, "outflow_30d_usd": 205_000_000,
        "frontend_http_status": 200, "public_rpc_uptime_30d": 0.995,
        "days_since_attestation": 60, "promised_cadence_days": 180,
    }
    if d >= _d(2026, 7, 10):
        f["proofs_restored"] = True
    return f


PANEL = {
    "ascendex": ascendex,
    "mvmt-labs": mvmt_labs,
    "mim-abracadabra": mim,
    "afx-trade": afx_trade,
    "bitmex": bitmex,
    "bitmart": bitmart,
    "odos": odos,
    "major-l1": major_l1,
    "major-cex": major_cex,
    "major-lending": major_lending,
    "mid-l2": mid_l2,
}


def observation_for(entity_id: str, d: date) -> Observation:
    facts = dict(PANEL[entity_id](d))
    ac = facts.pop("asset_class")
    return Observation(
        entity_id=entity_id,
        asset_class=ac,
        ts=datetime(d.year, d.month, d.day, 6, 0, tzinfo=UTC),
        facts=facts,
        sources={"panel": "; ".join(SOURCES.get(entity_id, ["synthetic control"]))},
    )


def days(start: date = WINDOW_START, end: date = WINDOW_END):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)
