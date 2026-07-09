"""Run 002: two-regime, dual-denomination policy comparison. Repairs review
findings #1-#3: adds oscillatory window, ETH-denominated baselines, and
daily-PQS regime labels alongside hourly."""
import json, math, time, datetime as dt
import requests
from clre import (Costs, simulate_hodl, simulate_lp, evaluate,
                  realised_vol, pqs, log_returns)

PPY = 24*365
V0 = 100_000.0

def fetch_hourly(start_iso, end_iso):
    start=dt.datetime.fromisoformat(start_iso).replace(tzinfo=dt.timezone.utc)
    end=dt.datetime.fromisoformat(end_iso).replace(tzinfo=dt.timezone.utc)
    out={}
    cur=start
    while cur<end:
        ce=min(cur+dt.timedelta(hours=300), end)
        r=requests.get("https://api.exchange.coinbase.com/products/ETH-USD/candles",
            params={"granularity":3600,"start":cur.isoformat(),"end":ce.isoformat()},timeout=15)
        r.raise_for_status()
        for ts,l,h,o,c,v in r.json(): out[int(ts)]=float(c)
        cur=ce; time.sleep(0.12)
    ks=sorted(out); return ks,[out[k] for k in ks]

def daily_from_hourly(ts, px):
    """Last close of each UTC day."""
    days={}
    for t,p in zip(ts,px):
        d=dt.datetime.fromtimestamp(t,dt.timezone.utc).date()
        days[d]=p
    ks=sorted(days); return [days[k] for k in ks]

def run_window(label, start_iso, end_iso):
    ts, px = fetch_hourly(start_iso, end_iso)
    n=len(px); p0,pT=px[0],px[-1]
    rets=log_returns(px)
    vol=realised_vol(px,PPY)
    daily=daily_from_hourly(ts,px)
    pqs_daily=pqs(log_returns(daily))
    costs=Costs()
    hodl=simulate_hodl(px,V0)
    pol=[
        ("Full range",            simulate_lp(px,V0,0.0, costs,"full",name="Full range"), None),
        ("Static ±15%",           simulate_lp(px,V0,0.15,costs,"static",name="Static ±15%"), 0.15),
        ("Static ±5%",            simulate_lp(px,V0,0.05,costs,"static",name="Static ±5%"), 0.05),
        ("Threshold ±15%",        simulate_lp(px,V0,0.15,costs,"threshold",name="Threshold ±15%"), 0.15),
        ("Threshold ±5%",         simulate_lp(px,V0,0.05,costs,"threshold",name="Threshold ±5%"), 0.05),
        ("Periodic wk ±10%",      simulate_lp(px,V0,0.10,costs,"periodic",period=24*7,name="Periodic wk ±10%"), 0.10),
    ]
    rows=[]
    hT=hodl.values[-1]
    eth_hodl_T = (V0/p0)*pT          # 100% ETH baseline, USD value at T
    for name,res,w in pol:
        e=evaluate(res,hodl,px,PPY,w,[0.15])
        vT=e["final_value"]
        # ETH-denominated: position value in ETH at T vs 100%-ETH hold (=V0/p0 ETH)
        eth_lvh=(vT/pT - V0/p0)/(V0/p0)
        cost_share = (res.total_cost / max(hT - vT, 1e-9)) if hT>vT else float('nan')
        rows.append({
            "name":name,"vT":vT,"lvh_usd":e["lvh_pre_fee"],"lvh_eth":eth_lvh,
            "nreb":e["n_rebalances"],"cost":e["total_cost"],
            "tir":e["time_in_range"],"be":e["breakeven_fee_apr"],
            "cost_share":cost_share})
    return {"label":label,"n":n,"p0":p0,"pT":pT,"net":pT/p0-1,
            "sigma_ann":vol["sigma_annual"],"pqs_hourly":pqs(rets),
            "pqs_daily":pqs_daily,"hodl_T":hT,
            "eth_hodl_lvh_usd":(eth_hodl_T-hT)/V0,
            "rows":rows,
            "start":dt.datetime.fromtimestamp(ts[0],dt.timezone.utc).date().isoformat(),
            "end":dt.datetime.fromtimestamp(ts[-1],dt.timezone.utc).date().isoformat()}

A=run_window("A — trending (ETH −20%)", "2026-04-09T00:00:00","2026-07-08T00:00:00")
B=run_window("B — oscillatory (ETH ~flat)","2026-03-02T00:00:00","2026-05-31T00:00:00")

for W in (A,B):
    print(f"\n=== Window {W['label']} | {W['start']}→{W['end']} | n={W['n']} | net {W['net']*100:+.1f}% | σ_ann {W['sigma_ann']*100:.0f}% | PQS daily {W['pqs_daily']:.3f} hourly {W['pqs_hourly']:.3f}")
    print(f"{'policy':<20}{'LVH usd':>9}{'LVH eth':>9}{'reb':>5}{'cost$':>8}{'TIR':>6}{'BE APR':>9}{'cost%dmg':>9}")
    for r in W["rows"]:
        cs = f"{r['cost_share']*100:.0f}%" if r['cost_share']==r['cost_share'] else "—"
        print(f"{r['name']:<20}{r['lvh_usd']*100:>8.2f}%{r['lvh_eth']*100:>8.2f}%{r['nreb']:>5}{r['cost']:>8.0f}{r['tir']*100:>5.0f}%{r['be']*100:>8.1f}%{cs:>9}")

json.dump({"A":A,"B":B}, open("run002.json","w"), default=str)
print("\nsaved run002.json")
