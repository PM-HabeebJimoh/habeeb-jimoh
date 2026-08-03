"""Walk-forward backtest harness.

Replays the panel one UTC day at a time through the live engine, with
persistence accumulating in a real SQLite store exactly as the daily cron would.
No lookahead: day D's verdict sees only facts observable on day D and signal
history from days < D.

Metrics reported:
  * Confusion matrix at the alert threshold (default CRITICAL, 0.75)
  * Precision / recall / F1 on `insolvent_failure` labels
  * Lead time: days between first alert and the outcome event
  * Alert burden: alerts per entity-day (a screener nobody can action is useless)
  * Per-day score trajectories for every entity
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .convergence import score_entity
from .panel_2026_07 import (
    OUTCOMES,
    PANEL,
    SOURCES,
    WINDOW_END,
    WINDOW_START,
    days,
    observation_for,
)
from .store import Store

ALERT_DEFAULT = 0.75
POSITIVE_LABEL = "insolvent_failure"


@dataclass
class EntityResult:
    entity_id: str
    label: str
    event_date: date | None
    trajectory: list[tuple[date, float, str, str]] = field(default_factory=list)
    first_alert: date | None = None
    first_alert_score: float = 0.0
    first_alert_path: str = ""
    first_alert_narrative: str = ""
    peak_score: float = 0.0
    peak_date: date | None = None
    alert_days: int = 0

    @property
    def alerted(self) -> bool:
        return self.first_alert is not None

    @property
    def lead_days(self) -> int | None:
        if self.first_alert is None or self.event_date is None:
            return None
        return (self.event_date - self.first_alert).days


def run_backtest(
    threshold: float = ALERT_DEFAULT,
    start: date = WINDOW_START,
    end: date = WINDOW_END,
    db_path: str | None = None,
) -> dict[str, Any]:
    tmpdir = None
    if db_path is None:
        tmpdir = tempfile.mkdtemp(prefix="cssx-bt-")
        db_path = os.path.join(tmpdir, "backtest.db")
    store = Store(db_path)

    results = {
        eid: EntityResult(eid, OUTCOMES[eid][0], OUTCOMES[eid][1])
        for eid in PANEL
    }

    for d in days(start, end):
        for eid in PANEL:
            o = observation_for(eid, d)
            hist = store.persistence(eid, as_of=o.ts)  # only days <= d
            v = score_entity(o, hist)
            store.record(o, v)

            r = results[eid]
            r.trajectory.append((d, v.score, v.band, v.path))
            if v.score > r.peak_score:
                r.peak_score, r.peak_date = v.score, d
            if v.score >= threshold:
                r.alert_days += 1
                if r.first_alert is None:
                    r.first_alert = d
                    r.first_alert_score = v.score
                    r.first_alert_path = v.path
                    r.first_alert_narrative = v.narrative

    store.close()

    positives = [r for r in results.values() if r.label == POSITIVE_LABEL]
    negatives = [r for r in results.values() if r.label != POSITIVE_LABEL]
    tp = [r for r in positives if r.alerted]
    fn = [r for r in positives if not r.alerted]
    fp = [r for r in negatives if r.alerted]
    tn = [r for r in negatives if not r.alerted]

    precision = len(tp) / max(len(tp) + len(fp), 1)
    recall = len(tp) / max(len(tp) + len(fn), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)

    leads = [r.lead_days for r in tp if r.lead_days is not None]
    entity_days = len(PANEL) * len(list(days(start, end)))
    alert_days_total = sum(r.alert_days for r in results.values())

    return {
        "window": [start.isoformat(), end.isoformat()],
        "days": len(list(days(start, end))),
        "entities": len(PANEL),
        "threshold": threshold,
        "confusion": {"tp": len(tp), "fp": len(fp), "tn": len(tn), "fn": len(fn)},
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "lead_days": {
            "values": {r.entity_id: r.lead_days for r in tp},
            "mean": sum(leads) / len(leads) if leads else None,
            "min": min(leads) if leads else None,
            "max": max(leads) if leads else None,
        },
        "alert_burden": {
            "entity_days": entity_days,
            "alert_entity_days": alert_days_total,
            "rate": alert_days_total / max(entity_days, 1),
        },
        "results": results,
        "db_path": db_path,
    }


def threshold_sweep(levels=(0.55, 0.65, 0.75, 0.85, 0.90)) -> list[dict]:
    out = []
    for t in levels:
        r = run_backtest(threshold=t)
        out.append({
            "threshold": t,
            "precision": r["precision"],
            "recall": r["recall"],
            "f1": r["f1"],
            "confusion": r["confusion"],
            "mean_lead": r["lead_days"]["mean"],
            "alert_rate": r["alert_burden"]["rate"],
            "fp_entities": sorted(
                e.entity_id for e in r["results"].values()
                if e.label != POSITIVE_LABEL and e.alerted
            ),
        })
    return out


def _sparkline(traj: list[tuple[date, float, str, str]]) -> str:
    blocks = "▁▂▃▄▅▆▇█"
    return "".join(blocks[min(int(s * 8), 7)] for _, s, _, _ in traj)


def format_report(bt: dict[str, Any], color: bool = True) -> str:
    L: list[str] = []
    C = {"TERMINAL": "\033[1;31m", "CRITICAL": "\033[31m", "ELEVATED": "\033[33m",
         "WATCH": "\033[36m", "NOMINAL": "\033[32m"} if color else {}
    R = "\033[0m" if color else ""

    w0, w1 = bt["window"]
    L.append("=" * 82)
    L.append(f"CSS-X v1.0 — WALK-FORWARD BACKTEST   {w0} → {w1}")
    L.append(f"{bt['days']} days × {bt['entities']} entities = "
             f"{bt['alert_burden']['entity_days']} entity-days   "
             f"alert threshold {bt['threshold']:.2f}")
    L.append("=" * 82)

    c = bt["confusion"]
    L.append("")
    L.append("CONFUSION MATRIX (label = insolvent_failure)")
    L.append(f"  true positives  {c['tp']:>2}    false positives {c['fp']:>2}")
    L.append(f"  false negatives {c['fn']:>2}    true negatives  {c['tn']:>2}")
    L.append(f"  precision {bt['precision']:.3f}   recall {bt['recall']:.3f}   "
             f"F1 {bt['f1']:.3f}")

    ld = bt["lead_days"]
    if ld["mean"] is not None:
        L.append("")
        L.append(f"LEAD TIME  mean {ld['mean']:.1f}d   "
                 f"range {ld['min']}–{ld['max']}d")
        for eid, v in sorted(ld["values"].items(), key=lambda kv: -(kv[1] or 0)):
            L.append(f"  {eid:<18} {v:>3}d before event")

    ab = bt["alert_burden"]
    L.append("")
    L.append(f"ALERT BURDEN  {ab['alert_entity_days']}/{ab['entity_days']} "
             f"entity-days in alert ({ab['rate']:.1%})")

    L.append("")
    L.append("PER-ENTITY TRAJECTORIES  (▁ = 0.0, █ = 1.0; one block per day)")
    L.append("-" * 82)
    order = {"insolvent_failure": 0, "solvent_winddown": 1, "survivor": 2}
    for r in sorted(bt["results"].values(),
                    key=lambda x: (order[x.label], -x.peak_score)):
        band = r.trajectory[-1][2]
        col = C.get(band, "")
        mark = "ALERT" if r.alerted else "  —  "
        L.append(f"{col}{r.entity_id:<18}{R} {r.label:<18} peak {r.peak_score:.3f} "
                 f"[{mark}]")
        L.append(f"  {_sparkline(r.trajectory)}")
        if r.alerted:
            lead = f", {r.lead_days}d lead" if r.lead_days is not None else ""
            L.append(f"  first alert {r.first_alert} @ {r.first_alert_score:.3f} "
                     f"via {r.first_alert_path}{lead}")
            L.append(f"  {r.first_alert_narrative[:200]}")
        L.append("")

    return "\n".join(L)


def format_sweep(sweep: list[dict]) -> str:
    L = ["THRESHOLD SWEEP", "-" * 82,
         f"{'thresh':>7} {'prec':>6} {'recall':>7} {'F1':>6} {'lead':>6} "
         f"{'alert%':>7}  false positives"]
    for s in sweep:
        lead = f"{s['mean_lead']:.0f}d" if s["mean_lead"] is not None else "  — "
        L.append(f"{s['threshold']:>7.2f} {s['precision']:>6.3f} {s['recall']:>7.3f} "
                 f"{s['f1']:>6.3f} {lead:>6} {s['alert_rate']:>6.1%}  "
                 f"{', '.join(s['fp_entities']) or '—'}")
    return "\n".join(L)


def format_sources() -> str:
    L = ["EVIDENCE BASIS", "-" * 82]
    for eid, srcs in SOURCES.items():
        label, ev = OUTCOMES[eid]
        L.append(f"{eid}  [{label}"
                 + (f", event {ev}]" if ev else "]"))
        for s in srcs:
            L.append(f"    - {s}")
        L.append("")
    L.append("Entities without sources listed are synthetic controls "
             "(major-l1, major-cex, major-lending, mid-l2).")
    return "\n".join(L)


def to_json(bt: dict[str, Any]) -> str:
    payload = {k: v for k, v in bt.items() if k != "results"}
    payload["results"] = {
        eid: {
            "label": r.label,
            "event_date": r.event_date.isoformat() if r.event_date else None,
            "alerted": r.alerted,
            "first_alert": r.first_alert.isoformat() if r.first_alert else None,
            "first_alert_score": r.first_alert_score,
            "first_alert_path": r.first_alert_path,
            "lead_days": r.lead_days,
            "peak_score": r.peak_score,
            "peak_date": r.peak_date.isoformat() if r.peak_date else None,
            "alert_days": r.alert_days,
            "trajectory": [[d.isoformat(), round(s, 4), b, p]
                           for d, s, b, p in r.trajectory],
        }
        for eid, r in bt["results"].items()
    }
    return json.dumps(payload, indent=2)
