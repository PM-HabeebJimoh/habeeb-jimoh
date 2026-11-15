"""Turn raw field data into the 12 decision numbers and apply the kill rules.

Usage: python3 -I analyse.py <dir with filled CSVs named like the templates in ../forms>
No projections, no assumptions: every number printed here comes from rows you collected.
A number with fewer than MIN_N observations is printed as "too few" instead of a value.
"""
import csv, os, sys, statistics as st

MIN_N = 10


def load(d, name):
    p = os.path.join(d, name)
    if not os.path.exists(p):
        return []
    rows = []
    for r in csv.DictReader(open(p, encoding="utf-8")):
        # template headers carry options in brackets, e.g. "outlet_type(PPMV|...)"; key on the part before "("
        rows.append({k.split("(")[0].strip(): (v or "").strip() for k, v in r.items() if k})
    return rows


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def med(vals):
    v = [x for x in vals if x is not None]
    return (st.median(v), len(v)) if len(v) >= MIN_N else (None, len(v))


def share(rows, key, yes="y"):
    v = [r[key].lower() for r in rows if r.get(key)]
    return (sum(x == yes for x in v) / len(v), len(v)) if len(v) >= MIN_N else (None, len(v))


def fmt(x, n, kind="ngn"):
    if x is None:
        return f"too few (n={n})"
    if kind == "pct":
        return f"{x:.0%} (n={n})"
    if kind == "x":
        return f"{x:.1f}x (n={n})"
    return f"₦{x:,.0f} (n={n})"


def main(d):
    audit, basket = load(d, "outlet_audit.csv"), load(d, "price_basket.csv")
    exits, mystery = load(d, "exit_interview.csv"), load(d, "mystery_shop.csv")
    whole, quality = load(d, "wholesaler.csv"), load(d, "quality_samples.csv")
    types = {r["outlet_id"]: r.get("outlet_type", "") for r in audit}
    R = {}

    print("== 1. Adult malaria treatment course: shelf price by outlet type")
    for t in sorted(set(types.values())):
        m, n = med(num(r["sell_price_ngn"]) for r in basket
                   if r["item"] == "AL_adult_course" and types.get(r["outlet_id"]) == t)
        print(f"   {t:10s} {fmt(m, n)}")

    print("== 2-3. Brand premium on the same molecule (median brand price / median generic price)")
    for item in ("AL_adult_course", "amlodipine10_x28", "lisinopril10_x28", "metformin500_x60"):
        b, nb = med(num(r["sell_price_ngn"]) for r in basket if r["item"] == item and r["generic_or_brand"] == "brand")
        g, ng = med(num(r["sell_price_ngn"]) for r in basket if r["item"] == item and r["generic_or_brand"] == "generic")
        ratio = b / g if b and g else None
        R[f"brand_ratio_{item}"] = ratio
        print(f"   {item:20s} brand {fmt(b, nb)} | generic {fmt(g, ng)} | ratio {fmt(ratio, min(nb, ng), 'x')}")
    units = [(r["item"], r["generic_or_brand"], num(r["units_sold_last_week"])) for r in basket]
    for item in ("AL_adult_course", "amlodipine10_x28"):
        tot = sum(u for i, _, u in units if i == item and u)
        br = sum(u for i, g, u in units if i == item and g == "brand" and u)
        R[f"brand_share_{item}"] = br / tot if tot else None
        print(f"   brand share of units sold, {item}: {fmt(br / tot if tot else None, int(tot), 'pct')}")

    print("== 4. Malaria testing")
    R["test_offered"], n = share(audit, "offers_malaria_test")
    print(f"   outlets offering a test: {fmt(R['test_offered'], n, 'pct')}")
    m, n = med(num(r["test_price_ngn"]) for r in audit if r.get("offers_malaria_test") == "y")
    print(f"   test price to customer: {fmt(m, n)}")
    m, n = med(num(r["price_ngn"]) for r in whole if r["item"] == "RDT_test")
    print(f"   RDT wholesale price: {fmt(m, n)}")
    R["mystery_test_offered"], n = share(mystery, "test_offered")
    print(f"   mystery shoppers offered a test: {fmt(R['mystery_test_offered'], n, 'pct')}")
    R["wtp_test_300"], n = share(exits, "would_pay_for_test_if_ngn_300")
    print(f"   customers who would pay ₦300 for a test: {fmt(R['wtp_test_300'], n, 'pct')}")

    print("== 5-6. Volume per outlet (observed beats estimated)")
    obs, n = med(num(r["fevers_counted_2h_observation"]) for r in audit)
    est, n2 = med(num(r["fevers_per_day_owner_estimate"]) for r in audit)
    R["fevers_per_day_owner"] = est
    print(f"   fevers in a 2-hour observation: {fmt(obs, n, 'n') if obs is None else f'{obs:.0f} (n={n})'}")
    print(f"   fevers per day, owner estimate: {fmt(est, n2) if est is None else f'{est:.0f} (n={n2})'}")
    bp, n = med(num(r["bp_refills_per_week_owner_estimate"]) for r in audit)
    R["bp_refills_week"] = bp
    print(f"   BP refills per week, owner estimate: {fmt(bp, n) if bp is None else f'{bp:.0f} (n={n})'}")

    print("== 7. Outlet gross margin on the tracer basket (sell - purchase) / sell")
    margins = [(num(r["sell_price_ngn"]) - num(r["purchase_price_ngn"])) / num(r["sell_price_ngn"])
               for r in basket if num(r["sell_price_ngn"]) and num(r["purchase_price_ngn"]) is not None]
    m, n = med(margins)
    print(f"   median margin: {fmt(m, n, 'pct')}")

    print("== 8. Quality: share of purchased samples that FAIL any check")
    done = [r for r in quality if r.get("lab_test") in ("pass", "fail") or r.get("nafdac_mas_check") == "fail"]
    fails = [r for r in done if r.get("lab_test") == "fail" or r.get("nafdac_mas_check") == "fail" or r.get("visual_check") == "fail"]
    R["fail_rate"] = len(fails) / len(done) if len(done) >= MIN_N else None
    print(f"   failure rate: {fmt(R['fail_rate'], len(done), 'pct')}")
    for g in ("brand", "generic"):
        sub = [r for r in done if r.get("generic_or_brand") == g]
        if sub:
            print(f"   {g}: {sum(r in fails for r in sub)} of {len(sub)} failed")

    print("== 9-10. Customers")
    m, n = med(num(r["total_spent_ngn"]) for r in exits)
    print(f"   spend per visit: {fmt(m, n)}")
    R["switch"], n = share(exits, "would_switch_to_tested_generic_at_half_brand_price")
    print(f"   would switch to a tested generic at half the brand price: {fmt(R['switch'], n, 'pct')}")
    stopped = [r for r in exits if r.get("on_monthly_bp_drugs") in ("y", "n") and r.get("has_bp_or_diabetes") == "y"]
    R["bp_price_dropout"], n = share([r for r in stopped if r.get("stopped_bp_drugs_in_last_6m_because")],
                                      "stopped_bp_drugs_in_last_6m_because", yes="price")
    print(f"   BP patients who stopped drugs because of price: {fmt(R['bp_price_dropout'], n, 'pct')}")
    R["abroad"], n = share(exits, "money_source", yes="family_abroad")
    print(f"   visits paid with money from family abroad: {fmt(R['abroad'], n, 'pct')}")

    print("== 11. Wholesale terms")
    m, n = med(num(r["credit_days_offered"]) for r in whole)
    print(f"   credit days offered: {fmt(m, n) if m is None else f'{m:.0f} days (n={n})'}")

    print("\n== VERDICTS (a hypothesis lives only if the data clears its bar)")
    def v(name, ok, why):
        state = "NO DATA" if ok is None else ("ALIVE" if ok else "DEAD")
        print(f"   [{state:7s}] {name}: {why}")
    br = R.get("brand_ratio_amlodipine10_x28")
    v("H1 trust arbitrage (tested generics vs brands)",
      None if None in (br, R["fail_rate"], R["switch"]) else (br >= 2 and R["fail_rate"] >= 0.10 and R["switch"] >= 0.4),
      "needs brand/generic ratio >= 2, sample failure >= 10%, >= 40% would switch")
    v("H2 test-before-treat",
      None if None in (R["test_offered"], R["wtp_test_300"]) else (R["test_offered"] < 0.3 and R["wtp_test_300"] >= 0.5),
      "needs a testing gap (< 30% of outlets test) and >= 50% willing to pay ₦300")
    v("H3 chronic BP control",
      None if None in (R["bp_refills_week"], R["bp_price_dropout"]) else (R["bp_refills_week"] >= 7 and R["bp_price_dropout"] >= 0.25),
      "needs >= 7 BP refills/outlet/week and >= 25% of patients dropping out on price")
    v("H4 diaspora payer",
      None if R["abroad"] is None else R["abroad"] >= 0.15,
      "needs >= 15% of visits paid with money from abroad (then run the diaspora survey)")
    v("Volume floor for any shop-based model",
      None if R["fevers_per_day_owner"] is None else R["fevers_per_day_owner"] >= 3,
      "needs >= 3 fevers per outlet per day (verify against the 2-hour count)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
