"""Run the CLRE policy comparison on real hourly ETH-USD data and emit a report."""
import json, math, time, datetime as dt
import requests
from clre import (Costs, simulate_hodl, simulate_lp, evaluate,
                  realised_vol, pqs, log_returns, acr)

PERIODS_PER_YEAR = 24 * 365
V0 = 100_000.0
ASSUMED_POOL_FEE_APRS = [0.05, 0.15, 0.30, 0.60]   # pool-level organic fee APRs
STRESS_HAIRCUT = 0.20                               # stated model assumption


def fetch_coinbase_hourly(product="ETH-USD", days=90) -> tuple[list[int], list[float]]:
    """Paginate Coinbase Exchange candles (max 300/call). Returns (ts, closes) ascending."""
    end = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - dt.timedelta(days=days)
    out = {}
    cur = start
    while cur < end:
        chunk_end = min(cur + dt.timedelta(hours=300), end)
        r = requests.get(
            f"https://api.exchange.coinbase.com/products/{product}/candles",
            params={"granularity": 3600, "start": cur.isoformat(),
                    "end": chunk_end.isoformat()}, timeout=15)
        r.raise_for_status()
        for ts, low, high, o, c, vol in r.json():
            out[int(ts)] = float(c)
        cur = chunk_end
        time.sleep(0.15)
    ts_sorted = sorted(out)
    return ts_sorted, [out[t] for t in ts_sorted]


def main():
    ts, prices = fetch_coinbase_hourly(days=90)
    with open("data_eth_usd_hourly.json", "w") as f:
        json.dump({"ts": ts, "close": prices}, f)
    n = len(prices)
    p0, pT = prices[0], prices[-1]
    rets = log_returns(prices)
    vol = realised_vol(prices, PERIODS_PER_YEAR)
    pqs_full = pqs(rets)

    costs = Costs()
    hodl = simulate_hodl(prices, V0)

    policies = [
        simulate_lp(prices, V0, 0.0,  costs, "full",      name="Full range (v2-style)"),
        simulate_lp(prices, V0, 0.15, costs, "static",    name="Static ±15%"),
        simulate_lp(prices, V0, 0.05, costs, "static",    name="Static ±5%"),
        simulate_lp(prices, V0, 0.15, costs, "threshold", name="Threshold re-center ±15%"),
        simulate_lp(prices, V0, 0.05, costs, "threshold", name="Threshold re-center ±5%"),
        simulate_lp(prices, V0, 0.10, costs, "periodic",  period=24 * 7,
                    name="Periodic weekly re-center ±10%"),
    ]
    widths = [None, 0.15, 0.05, 0.15, 0.05, 0.10]

    evals = [evaluate(r, hodl, prices, PERIODS_PER_YEAR, w, ASSUMED_POOL_FEE_APRS)
             for r, w in zip(policies, widths)]

    # In/out-of-range PQS decomposition for the static ±5% position
    st5 = policies[2]
    r_in = [rets[i - 1] for i in range(1, n) if st5.in_range[i]]
    r_out = [rets[i - 1] for i in range(1, n) if not st5.in_range[i]]
    pqs_in, pqs_out = pqs(r_in), pqs(r_out)

    # Worst rebalance events (read the failures by hand)
    thr5 = policies[4]
    worst = sorted(thr5.events, key=lambda e: -e.swapped_value)[:5]

    # ACR under the mid fee scenario for static ±5% (illustrative diagnostic)
    years = (n - 1) / PERIODS_PER_YEAR
    e5 = evals[2]
    fee_yield_window_mid = 0.15 * e5["capital_efficiency"] * e5["time_in_range"] * years
    acr_5 = acr(fee_yield_window_mid, vol["sigma_window"], STRESS_HAIRCUT)

    # ---------------- report ----------------
    L = []
    L.append("# CLRE Run 001 — ETH/USD hourly, 90 days\n")
    L.append(f"Window: {dt.datetime.fromtimestamp(ts[0], dt.timezone.utc):%Y-%m-%d} → "
             f"{dt.datetime.fromtimestamp(ts[-1], dt.timezone.utc):%Y-%m-%d} UTC · "
             f"{n} hourly closes · P0 ${p0:,.0f} → PT ${pT:,.0f} "
             f"({(pT/p0-1)*100:+.1f}%)\n")
    L.append(f"Deposit ${V0:,.0f} · costs: {costs.pool_fee*1e4:.0f} bps fee + "
             f"{costs.slippage*1e4:.0f} bps slippage per swap + ${costs.gas_usd:.0f} gas/event\n")
    L.append("## Regime diagnostics\n")
    L.append(f"- Realised vol: σ_hourly {vol['sigma_period']*100:.3f}% · "
             f"σ_window {vol['sigma_window']*100:.1f}% · "
             f"σ_annualised {vol['sigma_annual']*100:.0f}%")
    L.append(f"- PQS (full window): **{pqs_full:.3f}** "
             f"({'oscillatory' if pqs_full < 0.20 else 'mixed' if pqs_full < 0.45 else 'trending'})")
    pin = f"{pqs_in:.3f}" if pqs_in is not None else "n/a"
    pout = f"{pqs_out:.3f}" if pqs_out is not None else "n/a"
    L.append(f"- Static ±5% decomposition: in-range PQS {pin} · out-of-range PQS {pout} "
             f"(hourly-close approximation)\n")
    L.append("## Policy comparison (pre-fee, net of rebalance costs)\n")
    L.append("| Policy | Final value | LVH vs HODL | Rebalances | Rebal. cost | Time in range | Cap. eff. | Break-even fee APR |")
    L.append("|---|---|---|---|---|---|---|---|")
    L.append(f"| HODL 50/50 (baseline) | ${hodl.values[-1]:,.0f} | — | 0 | $0 | — | — | — |")
    for e in evals:
        L.append(f"| {e['name']} | ${e['final_value']:,.0f} | {e['lvh_pre_fee']*100:+.2f}% "
                 f"| {e['n_rebalances']} | ${e['total_cost']:,.0f} "
                 f"| {e['time_in_range']*100:.0f}% | {e['capital_efficiency']:.1f}x "
                 f"| {e['breakeven_fee_apr']*100:.1f}% |")
    L.append("\n**Break-even fee APR** = pool-level organic fee APR the position needed "
             "(after capital-efficiency and time-in-range scaling is *excluded* — this is "
             "the raw fee income on deposited capital required to match HODL). "
             "No volume data assumed; this is the inversion of the unknown.\n")
    L.append("## Net outcome under assumed pool fee APRs (secondary; stated model)\n")
    L.append("Position accrual model: pool APR × capital efficiency × time-in-range. "
             "This is an assumption, not a measurement.\n")
    hdr = "| Policy | " + " | ".join(f"{a*100:.0f}% APR" for a in ASSUMED_POOL_FEE_APRS) + " |"
    L.append(hdr)
    L.append("|---|" + "---|" * len(ASSUMED_POOL_FEE_APRS))
    for e in evals:
        row = [f"{e['fee_scenarios'][a]['net_vs_hodl']*100:+.2f}%" for a in ASSUMED_POOL_FEE_APRS]
        L.append(f"| {e['name']} | " + " | ".join(row) + " |")
    L.append("\n## ACR diagnostic (static ±5%, mid 15% APR scenario)\n")
    L.append(f"- Fee yield over window (modeled): {fee_yield_window_mid*100:.2f}%")
    L.append(f"- ACR base: **{acr_5['acr_base']:.2f}** · stress-adjusted "
             f"(haircut {STRESS_HAIRCUT*100:.0f}%, stated assumption): **{acr_5['acr_stress']:.2f}**\n")
    L.append("## Worst rebalances by hand (threshold ±5%) — read, not just counted\n")
    if worst:
        L.append("| t (hr) | Price | Value before | Swapped | Cost | Reason |")
        L.append("|---|---|---|---|---|---|")
        for e in worst:
            L.append(f"| {e.t} | ${e.price:,.0f} | ${e.value_before:,.0f} "
                     f"| ${e.swapped_value:,.0f} | ${e.cost:,.2f} | {e.reason} |")
    else:
        L.append("(no rebalance events)")
    L.append("\n## Cost decomposition (threshold ±5%)\n")
    e_thr5 = evals[4]
    drift_damage = -e_thr5["lvh_pre_fee"] * V0 - e_thr5["total_cost"]
    L.append(f"- Total shortfall vs HODL: ${-e_thr5['lvh_pre_fee']*V0:,.0f}")
    L.append(f"- Of which explicit rebalance costs (fees+slippage+gas): ${e_thr5['total_cost']:,.0f}")
    L.append(f"- Of which crystallised inventory drift: ${drift_damage:,.0f}")
    report = "\n".join(L) + "\n"
    with open("report_run001.md", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
