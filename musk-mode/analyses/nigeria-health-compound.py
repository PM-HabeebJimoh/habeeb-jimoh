# Self-funded compounding: Musk's "machine that builds the machine" under Buffett's "no outside money until proven".
# ESTIMATE inputs. contribution = per-node monthly cash after shop share, COGS, doctor, supervisor, maintenance.
def run(contrib, start=50, cash=0.0, months=180, cap=0.15, capex=750, tax=0.30, inject=None):
    n, out = start, {}
    for m in range(1, months+1):
        hq = 20_000 + 30*n
        pre = n*contrib - hq
        cash += pre*(1-tax) if pre > 0 else pre
        if inject and m == inject[0]: cash += inject[1]
        new = int(min(max(cash, 0)//capex, n*cap))      # cash-limited and certification-throughput-limited
        cash -= new*capex; n += new
        for t in (500, 5_000, 50_000):
            if n >= t and t not in out: out[t] = m
    return out, n
for name, c, kw in [('Base (redesigned, $81/node)', 81, {}),
                    ('Only high-volume shops certified ($100)', 100, {}),
                    ('Stressed ($40/node)', 40, {}),
                    ('Base + $20M raised at month 36 after proof', 81, dict(inject=(36, 20e6)))]:
    out, n = run(c, **kw)
    fmt = lambda t: f"{out[t]/12:.1f} yrs" if t in out else "never (15 yrs)"
    print(f"{name:45s} 500: {fmt(500):>14} | 5k: {fmt(5_000):>14} | 50k: {fmt(50_000):>14}")
