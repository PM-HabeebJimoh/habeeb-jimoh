# Buffett lens on the node model: margin-of-safety stress, owner earnings, ROIC, intrinsic value.
# All inputs ESTIMATE unless noted. Base inputs mirror nigeria-health-model.py.
def node(fx=1347, vol=1.0, price=1.0, cogs=1.0):
    eps = dict(mal=60*vol, acute=30*vol, htn=40*vol, dm=10*vol)
    p = dict(mal=3000*price, acute=2500*price, htn=4000*price, dm=6000*price)
    share = dict(mal=1000, acute=1000, htn=1000, dm=1500)          # shop owner keeps (fixed NGN)
    c = dict(mal=1.0*cogs, acute=0.8*cogs, htn=0.7*cogs, dm=1.8*cogs)  # USD
    gm = sum(eps[k]*((p[k]-share[k])/fx - c[k]) for k in eps) + 10000/fx
    var_opex = 1100/100 + 450/40           # remote doctor + supervisor per node, USD
    maint = 600/5/12                       # replace solar/phone kit every 5 yrs
    return gm, gm - var_opex - maint
cases = {
 'Base':                       dict(),
 'Volume -50%':                dict(vol=0.5),
 'Naira -30% (1347->1924)':    dict(fx=1924),
 'Price -20%':                 dict(price=0.8),
 'COGS +20%':                  dict(cogs=1.2),
 'ALL FOUR (margin of safety)':dict(vol=0.5, fx=1924, price=0.8, cogs=1.2),
}
TAX = 0.30
for name, kw in cases.items():
    gm, contrib = node(**kw)
    for n, hq in [(5000, 250_000*12), (50000, 1_500_000*12)]:
        pre = n*contrib*12 - hq
        oe = pre*(1-TAX) if pre > 0 else pre
        print(f"{name:30s} n={n:>5}: GM/node ${gm:6.1f}/mo, contrib ${contrib:6.1f}/mo, owner earnings ${oe/1e6:7.1f}M/yr")
# invested capital to reach 50k nodes (base): capex + pre-breakeven losses + kit stock in nodes
capital = 50000*600 + 15e6 + 50000*150
gm, contrib = node(); oe = (50000*contrib*12 - 18e6)*(1-TAX)
print(f"\nBase 50k: invested ~${capital/1e6:.0f}M, owner earnings ${oe/1e6:.0f}M -> after-tax ROIC {oe/capital:.0%}")
# probability-weighted intrinsic value (USD), owner earnings reached in yr 10, perpetuity g=3%
def pv(oe, r, g=0.03, yrs=10): return oe/(r-g)/(1+r)**yrs
outcomes = [('Dies at pilot', 0.50, None, -0.6e6),
            ('Stalls ~5k nodes, stressed', 0.30, (5000, dict(vol=0.5, fx=1924, price=0.8, cogs=1.2), 3e6), None),
            ('5k nodes, base', 0.12, (5000, {}, 3e6), None),
            ('50k nodes, base', 0.08, (50000, {}, 18e6), None)]
for r in (0.15, 0.20):
    ev = 0
    for name, p, spec, loss in outcomes:
        if spec:
            n, kw, hq = spec; c = node(**kw)[1]; pre = n*c*12 - hq
            v = pv(pre*(1-TAX) if pre > 0 else pre, r)
        else: v = loss
        ev += p*v
    print(f"r={r:.0%}: probability-weighted value ${ev/1e6:.1f}M (pilot capital at risk ~$0.6M)")

print("\n--- Redesigned for margin of safety: shop owner gets 33% of price; prices re-indexed to FX quarterly ---")
def node2(vol=1.0, price=1.0, cogs=1.0, fx_shock=1.0, passthrough=True):
    fx = 1347*fx_shock
    idx = fx_shock if passthrough else 1.0          # NGN price follows FX
    eps = dict(mal=60*vol, acute=30*vol, htn=40*vol, dm=10*vol)
    p = {k: v*price*idx for k, v in dict(mal=3000, acute=2500, htn=4000, dm=6000).items()}
    c = dict(mal=1.0*cogs, acute=0.8*cogs, htn=0.7*cogs, dm=1.8*cogs)
    gm = sum(eps[k]*(p[k]*0.67/fx - c[k]) for k in eps) + 10000*idx/fx
    return gm - 1100/100 - 450/40 - 600/5/12
for name, kw in [('Base', {}), ('ALL FOUR, FX passed through, volume -50%', dict(vol=0.5, price=0.8, cogs=1.2, fx_shock=1.43)),
                 ('ALL FOUR, FX passed through, volume -60%', dict(vol=0.4, price=0.8, cogs=1.2, fx_shock=1.43))]:
    c = node2(**kw); be = 250_000*12/(c*12) if c > 0 else float('inf')
    print(f"{name:42s}: contrib ${c:6.1f}/node/mo; breakeven at 5k-node HQ cost = {be:,.0f} nodes")
import itertools
for price, cogs in [(1.0,1.0),(0.8,1.2)]:
    v = next(v/100 for v in range(1,300) if node2(vol=v/100, price=price, cogs=cogs, fx_shock=1.43) > 0)
    print(f"price x{price}, COGS x{cogs}, naira -30% passed through: per-node volume must be >= {v:.0%} of base "
          f"(= {60*v:.0f} malaria + {40*v:.0f} BP subscribers/mo)")
