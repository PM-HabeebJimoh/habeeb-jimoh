"""XAU-Q command line.

    python -m xau.cli facts                    # measure stylised facts of the data
    python -m xau.cli evaluate                 # full walk-forward, honest report
    python -m xau.cli falsify                  # prove the harness isn't broken
    python -m xau.cli predict                  # next-bar forecast card
    python -m xau.cli evaluate --csv XAUUSD_H1.csv   # your real data
"""

from __future__ import annotations

import argparse
import json
import sys

from .core import dedupe_and_check, load_csv
from .features import FeatureBuilder
from .backtest_july import format_july_report, run_july_h1
from .miner import TARGETS, build_rule_universe, evaluate_rules, reality_check
from .synth import generate, stylised_facts
from .walkforward import run_walkforward

BOLD, DIM, RED, GRN, YEL, RST = (
    "\033[1m", "\033[2m", "\033[31m", "\033[32m", "\033[33m", "\033[0m"
)


def _load(args) -> list:
    if args.csv:
        bars = load_csv(args.csv)
        bars, stats = dedupe_and_check(bars)
        print(f"{DIM}loaded {args.csv}: {json.dumps(stats)}{RST}\n")
        return bars
    return generate(n=args.n, seed=args.seed, edge=args.edge)


def cmd_facts(args) -> int:
    bars = _load(args)
    f = stylised_facts(bars)
    print(f"{BOLD}STYLISED FACTS{RST}  (what this data actually is)")
    print(f"  bars                      {f['n_bars']}")
    print(f"  signed-return AC(1)       {f['ret_autocorr_lag1']:+.4f}   "
          f"{DIM}real gold ~ -0.02..+0.03 -> direction is near-unpredictable{RST}")
    print(f"  |return| AC(1)            {f['absret_autocorr_lag1']:.4f}    "
          f"{DIM}real gold ~ 0.15-0.45 -> volatility IS predictable{RST}")
    print(f"  |return| AC(10)           {f['absret_autocorr_lag10']:.4f}")
    print(f"  excess kurtosis           {f['excess_kurtosis']:.2f}     "
          f"{DIM}real gold ~ 5-9{RST}")
    print(f"  up-bar fraction           {f['pct_up_bars']:.4f}")
    print(f"  session vol multipliers")
    for k, v in f["session_vol_multipliers"].items():
        print(f"      {k:<9} {v:.2f}x")
    print()
    print(f"{BOLD}READ THIS{RST}: |return| autocorrelation is {f['absret_autocorr_lag1']:.2f} "
          f"while signed-return autocorrelation is {f['ret_autocorr_lag1']:+.3f}.")
    print("That ratio is the entire thesis of this system. Magnitude is forecastable;")
    print("sign is close to a coin flip. Any product promising 85% on SIGN is selling you")
    print("the one thing this market does not contain.")
    return 0


def _print_eval(r, target: float) -> None:
    dm, rm, om = r.direction_metrics(), r.range_metrics(), r.ohlc_band_metrics()
    print(f"{BOLD}{'='*74}{RST}")
    print(f"{BOLD}XAU-Q WALK-FORWARD EVALUATION{RST}   "
          f"{r.folds} folds, {dm['n']} out-of-sample predictions")
    print(f"{BOLD}{'='*74}{RST}\n")

    print(f"{BOLD}1. DIRECTION (next candle up/down){RST}")
    lo, hi = dm["ci95"]
    verdict = GRN + "BEATS" if lo > 0.5 else RED + "DOES NOT BEAT"
    print(f"   accuracy, all bars     {dm['accuracy_all_bars']:.4f}   95% CI [{lo:.4f}, {hi:.4f}]")
    print(f"   majority baseline      {dm['majority_class_baseline']:.4f}")
    print(f"   edge over baseline     {dm['edge_over_baseline']:+.4f}")
    print(f"   Brier / log-loss       {dm['brier']:.4f} / {dm['log_loss']:.4f}")
    print(f"   verdict                {verdict} coin-flip at 95% confidence{RST}\n")

    print(f"   {BOLD}accuracy vs coverage{RST} "
          f"{DIM}(fire only on the most confident N%){RST}")
    print(f"   {'coverage':>9} {'n':>6} {'accuracy':>9} {'95% CI':>18}")
    seen = set()
    for row in sorted(dm["curve"], key=lambda x: -x["coverage"]):
        b = round(row["coverage"], 2)
        if b in seen:
            continue
        seen.add(b)
        star = f" {RED}<- claimed target{RST}" if row["accuracy"] >= target else ""
        print(f"   {row['coverage']:>9.3f} {row['n_fired']:>6} {row['accuracy']:>9.4f} "
              f"  [{row['ci_low']:.3f}, {row['ci_high']:.3f}]{star}")
    hit = [x for x in dm["curve"] if x["accuracy"] >= target and x["ci_low"] > 0.5]
    if not hit:
        print(f"\n   {RED}{BOLD}NO threshold reaches {target:.0%} directional accuracy "
              f"with a CI excluding chance.{RST}")
        print(f"   {DIM}This is the honest result. See §3 for what IS achievable.{RST}")
    print()

    print(f"{BOLD}2. RANGE / OHLC BANDS (conformal prediction){RST}")
    rlo, rhi = rm["ci95"]
    ok = GRN + "MET" if rlo <= target <= rhi or rm["empirical_coverage"] >= target else YEL + "OFF"
    print(f"   target coverage        {rm['target_coverage']:.4f}")
    print(f"   empirical coverage     {rm['empirical_coverage']:.4f}   "
          f"95% CI [{rlo:.4f}, {rhi:.4f}]   {ok}{RST}")
    print(f"   mean band width        {rm['mean_width_atr']:.3f} ATR")
    print(f"   MAE vs naive(=ATR)     {rm['mae_atr']:.3f} vs {rm['naive_mae_atr']:.3f} "
          f"-> {rm['skill_vs_naive']:+.1%} skill")
    if om:
        print(f"   next-bar HIGH inside band   {om['high_coverage']:.4f}")
        print(f"   next-bar LOW  inside band   {om['low_coverage']:.4f}")
        print(f"   BOTH inside (joint)         {om['joint_coverage']:.4f}")
        print(f"   mean high band width        ${om['mean_high_band_usd']:.2f}")
    print()

    print(f"{BOLD}3. BY SESSION{RST}")
    print(f"   {'session':<10} {'n':>6} {'dir acc':>8} {'95% CI':>18} {'range cov':>10}")
    for s, m in sorted(r.by_session().items(), key=lambda kv: -kv[1]["n"]):
        c = m["dir_ci95"]
        print(f"   {s:<10} {m['n']:>6} {m['dir_accuracy']:>8.4f}   "
              f"[{c[0]:.3f}, {c[1]:.3f}] {m['range_coverage']:>10.4f}")
    print()

    print(f"{BOLD}4. CALIBRATION{RST} {DIM}(does p=0.6 actually mean 60%?){RST}")
    print(f"   {'bin':<12} {'n':>6} {'predicted':>10} {'observed':>10}")
    for row in dm["reliability"]:
        print(f"   {row['bin']:<12} {row['n']:>6} {row['mean_pred']:>10.4f} "
              f"{row['observed']:>10.4f}")
    return None


def cmd_evaluate(args) -> int:
    bars = _load(args)
    r = run_walkforward(
        bars, train=args.train, calib=args.calib, test=args.test,
        purge=args.purge, alpha=1.0 - args.target, target_acc=args.target,
        progress=(lambda a, b: print(f"{DIM}fold {a}/{b}{RST}", end="\r", file=sys.stderr))
        if args.verbose else None,
    )
    print()
    _print_eval(r, args.target)
    return 0


def cmd_falsify(args) -> int:
    """Prove the harness reports ~50% when no edge exists and finds one when it does."""
    print(f"{BOLD}FALSIFICATION SUITE{RST}")
    print("A backtest that cannot fail is worthless. These two runs establish that")
    print("this harness reports the truth in both directions.\n")
    rows = []
    for label, edge, expect in (
        ("martingale (no edge exists)", 0.0, "~0.500"),
        ("strong planted edge", 2.5, ">0.550"),
    ):
        bars = generate(n=args.n, seed=args.seed, edge=edge)
        r = run_walkforward(bars, train=args.train, calib=args.calib,
                            test=args.test, purge=args.purge)
        dm = r.direction_metrics()
        best = dm["curve"][0]
        rows.append((label, expect, dm["accuracy_all_bars"], dm["ci95"],
                     best["accuracy"], best["coverage"]))
    print(f"{'scenario':<30} {'expect':>8} {'all-bar':>9} {'95% CI':>18} {'best sel':>9}")
    for lab, exp, acc, ci, ba, bc in rows:
        print(f"{lab:<30} {exp:>8} {acc:>9.4f}  [{ci[0]:.3f}, {ci[1]:.3f}] "
              f"{ba:>8.3f}@{bc:.0%}")
    print()
    print(f"{GRN}If row 1 is ~0.50 and row 2 is well above it, the pipeline is sound{RST}")
    print(f"{GRN}and any near-50% result on realistic data is a market fact, not a bug.{RST}")
    return 0


def cmd_predict(args) -> int:
    bars = _load(args)
    fb = FeatureBuilder()
    r = run_walkforward(bars[:-1], train=args.train, calib=args.calib,
                        test=args.test, purge=args.purge,
                        alpha=1.0 - args.target, target_acc=args.target)
    if not r.predictions:
        print("not enough data")
        return 1
    p = r.predictions[-1]
    last = bars[-2]
    print(f"{BOLD}NEXT-BAR FORECAST CARD{RST}   {p.ts}  session={p.session}")
    print(f"  reference close          ${p.close_prev:,.2f}   ATR(14) ${p.atr_at_pred:,.2f}")
    print()
    print(f"  {BOLD}DIRECTION{RST}")
    print(f"    P(up)                  {p.p_up:.3f}")
    d = {1: "UP", 0: "DOWN", None: "ABSTAIN"}[p.decision]
    col = GRN if p.decision is not None else YEL
    print(f"    decision               {col}{d}{RST}")
    if p.decision is None:
        print(f"    {DIM}below the confidence band -> the system declines to call it{RST}")
    print()
    print(f"  {BOLD}RANGE / OHLC ({args.target:.0%} conformal){RST}")
    print(f"    predicted true range   {p.range_pred:.3f} ATR  "
          f"(${p.range_pred * p.atr_at_pred:,.2f})")
    print(f"    range band             [{p.range_lo:.3f}, {p.range_hi:.3f}] ATR")
    print(f"    expected HIGH in       [${p.high_lo:,.2f}, ${p.high_hi:,.2f}]")
    print(f"    expected LOW  in       [${p.low_lo:,.2f}, ${p.low_hi:,.2f}]")
    return 0


def cmd_july(args) -> int:
    # July has only 690 H1 bars, so it uses its own smaller folds unless the
    # user explicitly overrides them.
    res = run_july_h1(
        warmup=args.warmup,
        train=args.train if args.train != 2500 else 600,
        calib=args.calib if args.calib != 700 else 250,
        test=args.test if args.test != 250 else 60,
        purge=args.purge if args.purge != 30 else 12,
        target=args.target,
    )
    if args.json:
        import json
        res = {k: v for k, v in res.items() if k != "by_session"}
        print(json.dumps(res, indent=2, default=str))
        return 0
    print(format_july_report(res, not args.no_color))
    return 0


def cmd_mine(args) -> int:
    """Exhaustive rule search with multiple-testing correction."""
    bars = _load(args)
    rules = build_rule_universe()
    n_tests = len(rules) * len(TARGETS)
    print(f"{BOLD}EXHAUSTIVE RULE SEARCH{RST}")
    print(f"  {len(rules)} rules x {len(TARGETS)} target formulations "
          f"= {n_tests} hypothesis tests")
    print(f"  {DIM}Bonferroni, Benjamini-Hochberg FDR, and White's Reality "
          f"Check applied{RST}\n")
    print(f"  {'target':<28}{'base':>7}{'best':>8}{'n':>7}{'CIlo':>7}"
          f"{'BH':>4}{'RCp':>7}  tradeable")
    for t in TARGETS:
        res = evaluate_rules(bars, t, rules)
        if not res:
            print(f"  {t.name:<28}  (insufficient samples)")
            continue
        rc = reality_check(res)
        b = res[0]
        nbh = sum(1 for r in res if r.survives_bh)
        flag = "" if t.tradeable else f" {YEL}<- not tradeable{RST}"
        print(f"  {t.name:<28}{b.base_rate:>7.3f}{b.acc_test:>8.4f}"
              f"{b.n_test:>7}{b.ci_test[0]:>7.3f}{nbh:>4}"
              f"{rc['reality_check_p']:>7.3f}{flag}")
    print()
    print(f"  {DIM}Run with --edge 0 to repeat the identical search on data with{RST}")
    print(f"  {DIM}PROVABLY ZERO edge. Compare the best accuracies.{RST}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="xau", description="XAU-Q gold forecasting")
    p.add_argument("--csv", help="XAUUSD OHLCV csv (else synthetic)")
    p.add_argument("--n", type=int, default=9000)
    p.add_argument("--seed", type=int, default=11)
    p.add_argument("--edge", type=float, default=0.35,
                   help="synthetic planted edge; 0 = pure martingale")
    p.add_argument("--train", type=int, default=2500)
    p.add_argument("--calib", type=int, default=700)
    p.add_argument("--test", type=int, default=250)
    p.add_argument("--purge", type=int, default=30)
    p.add_argument("--target", type=float, default=0.85)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--no-color", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--warmup", type=int, default=1400)
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, helptext in (
        ("facts", cmd_facts, "measure the data's stylised facts"),
        ("evaluate", cmd_evaluate, "full walk-forward evaluation"),
        ("falsify", cmd_falsify, "prove the harness can fail"),
        ("predict", cmd_predict, "next-bar forecast card"),
        ("july", cmd_july, "backtest July 2026 on H1 (real daily anchors)"),
        ("mine", cmd_mine, "exhaustive rule search, multiple-testing corrected"),
    ):
        sp = sub.add_parser(name, help=helptext)
        sp.set_defaults(func=fn)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
