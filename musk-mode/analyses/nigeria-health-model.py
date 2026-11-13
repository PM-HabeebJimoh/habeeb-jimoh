# Node-network unit economics. Every input not sourced is an ESTIMATE.
FX = 1347  # NGN/USD, CBN official 6 Nov 2026
# --- per-node monthly volume at maturity (ESTIMATE) ---
mal_eps, acute_eps = 60, 30          # malaria test-and-treat, other acute (pneumonia/diarrhoea/UTI)
htn_subs, dm_subs = 40, 10           # hypertension, diabetes monthly subscribers
# --- prices to patient, NGN (ESTIMATE; must sit below today's shelf price -> verify in shop walk) ---
p_mal, p_acute, p_htn, p_dm = 3000, 2500, 4000, 6000
node_share = {'mal':1000,'acute':1000,'htn':1000,'dm':1500}  # shop owner keeps this
# --- COGS USD (ACT from Global Fund PPM Q2-2024 $0.22-0.57; rest ESTIMATE) ---
c_mal = 0.40 + 0.40 + 0.20   # RDT + ACT + logistics/QA
c_acute = 0.80
c_htn = 0.50 + 0.20          # monthly generic + BP/QA
c_dm = 1.50 + 0.30           # metformin + strips/QA
fee = 10000                  # franchise/certification fee per node per month, NGN
def node_month():
    rev = {k:(p-node_share[k])/FX for k,p in [('mal',p_mal),('acute',p_acute),('htn',p_htn),('dm',p_dm)]}
    gm = (mal_eps*(rev['mal']-c_mal) + acute_eps*(rev['acute']-c_acute)
          + htn_subs*(rev['htn']-c_htn) + dm_subs*(rev['dm']-c_dm) + fee/FX)
    gross_rev = (mal_eps*p_mal + acute_eps*p_acute + htn_subs*p_htn + dm_subs*p_dm)/FX
    node_income = (mal_eps*1000 + acute_eps*1000 + htn_subs*1000 + dm_subs*1500 - fee)/FX
    return gross_rev, gm, node_income
gr, gm, ni = node_month()
print(f"Per node/month: patient spend ${gr:,.0f}, our gross margin ${gm:,.0f}, shop owner net ${ni:,.0f}")
# --- network costs (ESTIMATE) ---
capex_node = 600            # training + solar/LFP + phone + test kit stock
doc_cost = 1100             # remote doctor $/month (~NGN1.5M), 1 per 100 nodes
sup_cost = 450              # field supervisor $/month, 1 per 40 nodes
for nodes, hq in [(50, 25_000), (5_000, 250_000), (50_000, 1_500_000)]:
    opex = nodes/100*doc_cost + nodes/40*sup_cost + hq
    ebitda_m = nodes*gm - opex
    print(f"{nodes:>6} nodes: GM ${nodes*gm*12/1e6:7.1f}M/yr, opex ${opex*12/1e6:6.1f}M/yr, "
          f"EBITDA ${ebitda_m*12/1e6:7.1f}M/yr, capex ${nodes*capex_node/1e6:5.1f}M, "
          f"patients' spend ${nodes*gr*12/1e6:7.1f}M/yr")
print(f"Node payback on capex: {capex_node/(gm - doc_cost/100 - sup_cost/40):.1f} months")
# scale checks vs national totals
print(f"50k nodes malaria eps/yr: {50_000*mal_eps*12/1e6:.0f}M vs 66.7-68M cases (WMR 2024)")
print(f"50k nodes HTN subs: {50_000*htn_subs/1e6:.1f}M vs 27.5M hypertensive, 12% treated (Adeloye 2021)")
the_usd = 10.42e12/1480; print(f"THE 2024 ~ ${the_usd/1e9:.1f}B at ~NGN1,480/$ (2024 avg, ESTIMATE); OOP 58.3% = ${the_usd*0.583/1e9:.1f}B")
