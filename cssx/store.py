"""SQLite persistence: observations, signal history, persistence counters."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .core import UTC, Observation, AssetClass
from .convergence import Verdict

SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    entity_id   TEXT PRIMARY KEY,
    asset_class TEXT NOT NULL,
    label       TEXT,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS observations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id   TEXT NOT NULL,
    ts          TEXT NOT NULL,
    facts       TEXT NOT NULL,
    sources     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS signal_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id   TEXT NOT NULL,
    ts          TEXT NOT NULL,
    layer       INTEGER NOT NULL,
    score       REAL NOT NULL,
    measured    INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS verdicts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id   TEXT NOT NULL,
    ts          TEXT NOT NULL,
    score       REAL NOT NULL,
    band        TEXT NOT NULL,
    path        TEXT NOT NULL,
    payload     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_sig_entity ON signal_history(entity_id, layer, ts);
CREATE INDEX IF NOT EXISTS ix_verdict_entity ON verdicts(entity_id, ts);
"""


class Store:
    def __init__(self, path: str | Path = "cssx.db"):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ------------------------------------------------------------------ write
    def upsert_entity(self, entity_id: str, asset_class: AssetClass, label: str = "") -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO entities VALUES (?,?,?,?)",
            (entity_id, asset_class.value, label, datetime.now(UTC).isoformat()),
        )
        self.conn.commit()

    def record(self, o: Observation, verdict: Verdict) -> None:
        self.upsert_entity(o.entity_id, o.asset_class)
        ts = o.ts.isoformat()
        self.conn.execute(
            "INSERT INTO observations (entity_id, ts, facts, sources) VALUES (?,?,?,?)",
            (o.entity_id, ts, json.dumps(o.facts, default=str), json.dumps(o.sources)),
        )
        self.conn.executemany(
            "INSERT INTO signal_history (entity_id, ts, layer, score, measured) VALUES (?,?,?,?,?)",
            [(o.entity_id, ts, s.layer, s.score, int(s.measured)) for s in verdict.signals],
        )
        self.conn.execute(
            "INSERT INTO verdicts (entity_id, ts, score, band, path, payload) VALUES (?,?,?,?,?,?)",
            (o.entity_id, ts, verdict.score, verdict.band, verdict.path,
             json.dumps(verdict.to_dict())),
        )
        self.conn.commit()

    # ------------------------------------------------------------------- read
    def persistence(self, entity_id: str, max_days: int = 30,
                    as_of: datetime | None = None) -> dict[int, int]:
        """Consecutive days (distinct dates) each layer has been active.

        `as_of` anchors the lookback window. It MUST be supplied when replaying
        history: anchoring to wall-clock `now()` silently truncates every streak
        older than `max_days`, which permanently pins `persistence_ok` to False
        and caps every historical verdict at 0.74. That bug was found by the
        July 2026 backtest, where it suppressed a 12-day-lead AscendEX alert
        down to a 3-day-late one.
        """
        anchor = as_of or datetime.now(UTC)
        since = (anchor - timedelta(days=max_days)).isoformat()
        rows = self.conn.execute(
            "SELECT layer, ts, score FROM signal_history "
            "WHERE entity_id=? AND ts>=? AND ts<=? ORDER BY layer, ts DESC",
            (entity_id, since, anchor.isoformat()),
        ).fetchall()

        by_layer: dict[int, list[tuple[str, float]]] = {}
        for r in rows:
            by_layer.setdefault(r["layer"], []).append((r["ts"][:10], r["score"]))

        out: dict[int, int] = {}
        for layer, series in by_layer.items():
            seen: set[str] = set()
            streak = 0
            for day, score in series:
                if day in seen:
                    continue
                seen.add(day)
                if score > 0:
                    streak += 1
                else:
                    break
            out[layer] = streak
        return out

    def latest_verdicts(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT payload FROM verdicts ORDER BY ts DESC, id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [json.loads(r["payload"]) for r in rows]

    def close(self) -> None:
        self.conn.close()
