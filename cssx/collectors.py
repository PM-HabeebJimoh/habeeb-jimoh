"""Zero-cost data collectors (stdlib only, no dependencies, no API keys).

Every collector is best-effort and fail-soft: a network error yields no fact
rather than a wrong fact, because in CSS-X an unmeasured signal scores 0 and a
fabricated one poisons the convergence. Nothing here costs money; all endpoints
have free public tiers.

    RPC (any EVM chain)  — eth_blockNumber, eth_getBlockByNumber, eth_call
    DefiLlama            — /protocol/{slug}, /v2/chains       (no key)
    CoinGecko            — /simple/price, /coins/{id}         (free tier)
    GitHub               — /repos/{owner}/{repo}/commits      (60 req/h)
    Etherscan-family     — balance / txlist                   (free key)
    Wayback / HTTP HEAD  — front-end and docs liveness        (no key)
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

UTC = timezone.utc
USER_AGENT = "cssx/1.0 (+research; contact via repo)"
DEFAULT_TIMEOUT = 12


class RateLimiter:
    """Trivial token-bucket so free tiers are respected, not abused."""

    def __init__(self, min_interval_s: float):
        self.min_interval = min_interval_s
        self._last = 0.0

    def wait(self) -> None:
        delta = time.time() - self._last
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self._last = time.time()


def _get_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> Any | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def _post_json(url: str, payload: dict, timeout: int = DEFAULT_TIMEOUT) -> Any | None:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


# --------------------------------------------------------------------- Tier 1
def rpc_block_freshness(rpc_url: str, target_block_time_s: float) -> dict:
    """L101 inputs: seconds since the newest block, via any public EVM RPC."""
    res = _post_json(rpc_url, {"jsonrpc": "2.0", "id": 1,
                               "method": "eth_getBlockByNumber",
                               "params": ["latest", False]})
    if not res or "result" not in res or not res["result"]:
        return {}
    try:
        ts = int(res["result"]["timestamp"], 16)
    except (KeyError, TypeError, ValueError):
        return {}
    gap = max(datetime.now(UTC).timestamp() - ts, 0)
    return {"seconds_since_final_block": gap,
            "target_block_time_s": target_block_time_s}


# --------------------------------------------------------------------- Tier 2
def defillama_tvl(slug: str) -> dict:
    """L202 inputs: 30d TVL change from DefiLlama's free protocol endpoint."""
    data = _get_json(f"https://api.llama.fi/protocol/{slug}")
    if not data:
        return {}
    series = data.get("tvl") or []
    if len(series) < 31:
        return {}
    now_tvl = float(series[-1].get("totalLiquidityUSD", 0) or 0)
    then_tvl = float(series[-31].get("totalLiquidityUSD", 0) or 0)
    if then_tvl <= 0:
        return {}
    return {"tvl_usd": now_tvl,
            "tvl_native_delta_30d_pct": (now_tvl - then_tvl) / then_tvl}


def coingecko_market(coin_id: str) -> dict:
    """L201/L203 inputs: mcap, volume and peg deviation for pegged assets."""
    data = _get_json(
        "https://api.coingecko.com/api/v3/coins/" + coin_id +
        "?localization=false&tickers=false&community_data=false&developer_data=false"
    )
    if not data:
        return {}
    md = data.get("market_data") or {}
    price = (md.get("current_price") or {}).get("usd")
    out: dict[str, Any] = {}
    if (md.get("market_cap") or {}).get("usd"):
        out["circulating_mcap_usd"] = float(md["market_cap"]["usd"])
    if (md.get("total_volume") or {}).get("usd"):
        out["avg_daily_volume_usd"] = float(md["total_volume"]["usd"])
    if price is not None:
        out["price_usd"] = float(price)
    return out


def peg_deviation_from_price(price_usd: float, peg: float = 1.0) -> dict:
    """L203 input: convert an observed price into basis-point deviation."""
    if peg <= 0:
        return {}
    return {"peg_deviation_bps": (price_usd - peg) / peg * 10_000}


# --------------------------------------------------------------------- Tier 3
def github_activity(owner: str, repo: str, token: str | None = None) -> dict:
    """L302 inputs: 90d commit count, unique committers, days since release."""
    since = (datetime.now(UTC) - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    base = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def fetch(path: str):
        req = urllib.request.Request(base + path, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as r:
                return json.loads(r.read().decode())
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            return None

    commits = fetch(f"/commits?since={since}&per_page=100")
    out: dict[str, Any] = {}
    if isinstance(commits, list):
        out["commits_90d"] = len(commits)
        authors = {
            (c.get("author") or {}).get("login")
            or ((c.get("commit") or {}).get("author") or {}).get("email")
            for c in commits
        }
        out["unique_committers_90d"] = len([a for a in authors if a])

    releases = fetch("/releases?per_page=1")
    if isinstance(releases, list) and releases:
        published = releases[0].get("published_at")
        if published:
            dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            out["days_since_release"] = (datetime.now(UTC) - dt).days
    return out


def http_liveness(url: str) -> dict:
    """L305 inputs: front-end HTTP status (0 means unreachable)."""
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as r:
            return {"frontend_http_status": r.status}
    except urllib.error.HTTPError as e:
        return {"frontend_http_status": e.code}
    except (urllib.error.URLError, TimeoutError, OSError):
        return {"frontend_http_status": 0}


# --------------------------------------------------------------------- Tier 4
def erc20_total_supply(rpc_url: str, token_address: str, decimals: int = 18) -> float | None:
    """Helper for L205: wrapped-token totalSupply() via eth_call."""
    res = _post_json(rpc_url, {
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": token_address, "data": "0x18160ddd"}, "latest"],
    })
    if not res or not res.get("result") or res["result"] == "0x":
        return None
    try:
        return int(res["result"], 16) / (10 ** decimals)
    except ValueError:
        return None


def chainlink_staleness(rpc_url: str, feed_address: str, heartbeat_s: float) -> dict:
    """L401 inputs: oracle staleness via latestRoundData() updatedAt."""
    res = _post_json(rpc_url, {
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": feed_address, "data": "0xfeaf968c"}, "latest"],
    })
    if not res or not res.get("result"):
        return {}
    raw = res["result"][2:]
    if len(raw) < 64 * 5:
        return {}
    try:
        updated_at = int(raw[64 * 3:64 * 4], 16)     # 4th return word
    except ValueError:
        return {}
    if updated_at == 0:
        return {}
    gap = max(datetime.now(UTC).timestamp() - updated_at, 0)
    return {"oracle_staleness_s": gap, "oracle_heartbeat_s": heartbeat_s}


def wallet_last_activity(explorer_api: str, address: str, api_key: str = "") -> dict:
    """L403 inputs: days since the treasury/ops wallet last transacted.

    `explorer_api` is any Etherscan-compatible base URL (Etherscan, Basescan,
    Arbiscan, Blockscout). Free keys are sufficient.
    """
    url = (f"{explorer_api}?module=account&action=txlist&address={address}"
           f"&page=1&offset=1&sort=desc&apikey={api_key}")
    data = _get_json(url)
    if not data or data.get("status") != "1" or not data.get("result"):
        return {}
    try:
        ts = int(data["result"][0]["timeStamp"])
    except (KeyError, IndexError, ValueError, TypeError):
        return {}
    days = (datetime.now(UTC).timestamp() - ts) / 86_400
    return {"days_since_treasury_tx": days}


COLLECTORS = {
    "rpc_block_freshness": rpc_block_freshness,
    "defillama_tvl": defillama_tvl,
    "coingecko_market": coingecko_market,
    "github_activity": github_activity,
    "http_liveness": http_liveness,
    "chainlink_staleness": chainlink_staleness,
    "wallet_last_activity": wallet_last_activity,
}
