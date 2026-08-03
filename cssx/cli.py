"""CSS-X command line.

    python -m cssx.cli replay              # score built-in historical fixtures
    python -m cssx.cli score entity.json   # score a JSON observation
    python -m cssx.cli layers              # list all signal layers
    python -m cssx.cli run --db cssx.db    # persist a scoring run (cron entry)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from .core import UTC, AssetClass, Observation
from .convergence import rank, score_entity
from .fixtures import ALL_FIXTURES, FIXTURE_HISTORIES
from .signals import ALL_LAYERS
from .store import Store

BANDS_COLOR = {
    "TERMINAL": "\033[1;31m", "CRITICAL": "\033[31m", "ELEVATED": "\033[33m",
    "WATCH": "\033[36m", "NOMINAL": "\033[32m",
}
RESET = "\033[0m"


def _fmt(v, color: bool = True) -> str:
    c = BANDS_COLOR.get(v.band, "") if color else ""
    r = RESET if color else ""
    head = (f"{c}{v.score:0.3f}  {v.band:<9}{r} {v.entity_id:<24} "
            f"[{v.asset_class.value}] via {v.path} "
            f"(conf {v.confidence:.2f}, cov {v.coverage:.0%}, absences {v.active_absences})")
    lines = [head, f"    {v.narrative}"]
    if v.contradictions:
        lines.append(f"    contradiction cap applied: {', '.join(v.contradictions)}")
    lines.append(f"    action: {v.action}")
    return "\n".join(lines)


def cmd_replay(args) -> int:
    verdicts = rank(ALL_FIXTURES, FIXTURE_HISTORIES)
    if args.json:
        print(json.dumps([v.to_dict() for v in verdicts], indent=2))
        return 0
    print("CSS-X v1.0 — historical replay\n" + "=" * 78)
    for v in verdicts:
        print(_fmt(v, not args.no_color))
        print()
    return 0


def _load_observation(path: str) -> Observation:
    with open(path) as f:
        blob = json.load(f)
    ts = blob.get("ts")
    return Observation(
        entity_id=blob["entity_id"],
        asset_class=AssetClass(blob["asset_class"]),
        ts=datetime.fromisoformat(ts).replace(tzinfo=UTC) if ts else datetime.now(UTC),
        facts=blob.get("facts", {}),
        sources=blob.get("sources", {}),
    )


def cmd_score(args) -> int:
    o = _load_observation(args.path)
    hist = json.loads(args.history) if args.history else None
    if hist:
        hist = {int(k): int(v) for k, v in hist.items()}
    v = score_entity(o, hist)
    print(json.dumps(v.to_dict(), indent=2) if args.json else _fmt(v, not args.no_color))
    return 0


def cmd_layers(args) -> int:
    print(f"{'LAYER':<7}{'TIER':<6}{'NAME':<30}LEAD (days)")
    for fn in ALL_LAYERS:
        doc = (fn.__doc__ or "").strip().splitlines()[0]
        print(f"  {doc}")
    return 0


def cmd_run(args) -> int:
    store = Store(args.db)
    obs = ALL_FIXTURES if args.demo else [_load_observation(p) for p in args.inputs]
    out = []
    for o in obs:
        hist = store.persistence(o.entity_id) or FIXTURE_HISTORIES.get(o.entity_id)
        v = score_entity(o, hist)
        store.record(o, v)
        out.append(v)
    for v in sorted(out, key=lambda x: x.score, reverse=True):
        print(_fmt(v, not args.no_color))
        print()
    alerts = [v for v in out if v.score >= args.alert_threshold]
    print(f"{len(alerts)} entities at or above alert threshold {args.alert_threshold}")
    store.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="cssx", description="CSS-X crypto distress convergence")
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("replay", help="score built-in historical fixtures")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_replay)

    s = sub.add_parser("score", help="score a JSON observation file")
    s.add_argument("path")
    s.add_argument("--history", help='JSON map of layer->consecutive active days')
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_score)

    l = sub.add_parser("layers", help="list signal layers")
    l.set_defaults(func=cmd_layers)

    run = sub.add_parser("run", help="scoring run with persistence (cron entry point)")
    run.add_argument("inputs", nargs="*", help="observation JSON files")
    run.add_argument("--db", default="cssx.db")
    run.add_argument("--demo", action="store_true", help="use built-in fixtures")
    run.add_argument("--alert-threshold", type=float, default=0.75)
    run.set_defaults(func=cmd_run)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
