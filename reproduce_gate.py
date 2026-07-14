"""Reproduction gate for Run 002/003 (protocol step: SMOKE/gate before new runs).

Mode per window (amended gate, 2026-07-09; path/coverage fix follow-up):
- Window A: EXACT mode — replay from runs/data_A_hourly_20260409_20260708.json
  (saved inputs). Pass criterion: every published run002.json A number matches
  to rel tol 1e-9.
- Window B: EXACT mode — replay from runs/data_B_hourly_20260302_20260531.json
  (saved inputs). Pass criterion: every published run002.json B number matches
  to rel tol 1e-9.
- Window B': EXACT mode — replay from runs/data_Bprime_hourly_20240806_20241103.json
  (saved inputs). Pass criterion: every published run003.json number matches
  to rel tol 1e-9. run003.json is a separate reference source from run002.json
  (Run 003, disjoint oscillatory window).
All three windows run entirely offline — the gate makes no network calls.
"""
import json, math, datetime as dt
from clre import (Costs, simulate_hodl, simulate_lp, evaluate,
                  realised_vol, pqs, log_returns)

PPY = 24 * 365
V0 = 100_000.0


def daily_from_hourly(ts, px):
    days = {}
    for t, p in zip(ts, px):
        d = dt.datetime.fromtimestamp(t, dt.timezone.utc).date()
        days[d] = p
    ks = sorted(days)
    return [days[k] for k in ks]


def run_window(ts, px):
    rets = log_returns(px)
    vol = realised_vol(px, PPY)
    daily = daily_from_hourly(ts, px)
    costs = Costs()
    hodl = simulate_hodl(px, V0)
    pol = [
        ("Full range",       simulate_lp(px, V0, 0.0,  costs, "full",      name="Full range"), None),
        ("Static ±15%",      simulate_lp(px, V0, 0.15, costs, "static",    name="Static ±15%"), 0.15),
        ("Static ±5%",       simulate_lp(px, V0, 0.05, costs, "static",    name="Static ±5%"), 0.05),
        ("Threshold ±15%",   simulate_lp(px, V0, 0.15, costs, "threshold", name="Threshold ±15%"), 0.15),
        ("Threshold ±5%",    simulate_lp(px, V0, 0.05, costs, "threshold", name="Threshold ±5%"), 0.05),
        ("Periodic wk ±10%", simulate_lp(px, V0, 0.10, costs, "periodic",  period=24 * 7, name="Periodic wk ±10%"), 0.10),
    ]
    hT = hodl.values[-1]
    p0, pT = px[0], px[-1]
    rows = []
    for name, res, w in pol:
        e = evaluate(res, hodl, px, PPY, w, [0.15])
        vT = e["final_value"]
        eth_lvh = (vT / pT - V0 / p0) / (V0 / p0)
        rows.append({"name": name, "vT": vT, "lvh_usd": e["lvh_pre_fee"],
                     "lvh_eth": eth_lvh, "nreb": e["n_rebalances"],
                     "cost": e["total_cost"], "tir": e["time_in_range"],
                     "be": e["breakeven_fee_apr"]})
    return {"n": len(px), "p0": p0, "pT": pT, "net": pT / p0 - 1,
            "sigma_ann": vol["sigma_annual"], "pqs_hourly": pqs(rets),
            "pqs_daily": pqs(log_returns(daily)), "hodl_T": hT, "rows": rows}


def compare(label, got, ref, mode):
    ok = True
    if mode == "exact":
        def chk(a, b):
            return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
    print(f"\n=== GATE {label} [{mode}] ===")
    for g, r in zip(got["rows"], ref["rows"]):
        if mode == "exact":
            fields = ["vT", "lvh_usd", "lvh_eth", "cost", "tir", "be"]
            row_ok = all(chk(g[f], r[f]) for f in fields) and g["nreb"] == r["nreb"]
            detail = ""
        else:
            d_be = abs(g["be"] - r["be"])
            d_lvh = abs(g["lvh_usd"] - r["lvh_usd"])
            row_ok = d_be <= 0.01 and d_lvh <= 0.003
            detail = f"  dBE={d_be*100:.2f}pp dLVH={d_lvh*100:.2f}pp"
        print(f"{'PASS' if row_ok else 'FAIL'}  {g['name']:<18} "
              f"BE {g['be']*100:6.1f}% (ref {r['be']*100:6.1f}%)  "
              f"LVH {g['lvh_usd']*100:7.2f}% (ref {r['lvh_usd']*100:7.2f}%)  "
              f"reb {g['nreb']}/{r['nreb']}{detail}")
        ok = ok and row_ok
    print(f"GATE {label}: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    ref = json.load(open("runs/run002.json"))
    ref_bprime = json.load(open("runs/run003.json"))

    # --- Window A: exact, from saved inputs ---
    d = json.load(open("runs/data_A_hourly_20260409_20260708.json"))
    ts_a, px_a = d["ts"], d["close"]
    t0 = dt.datetime.fromtimestamp(ts_a[0], dt.timezone.utc)
    t1 = dt.datetime.fromtimestamp(ts_a[-1], dt.timezone.utc)
    print(f"Saved A inputs: n={len(px_a)}  {t0.date()} -> {t1.date()}")
    got_a = run_window(ts_a, px_a)
    ok_a = compare("A (saved json)", got_a, ref["A"], "exact")

    # --- Window B: exact, from saved inputs ---
    d = json.load(open("runs/data_B_hourly_20260302_20260531.json"))
    ts_b, px_b = d["ts"], d["close"]
    t0 = dt.datetime.fromtimestamp(ts_b[0], dt.timezone.utc)
    t1 = dt.datetime.fromtimestamp(ts_b[-1], dt.timezone.utc)
    print(f"\nSaved B inputs: n={len(px_b)}  {t0.date()} -> {t1.date()}")
    got_b = run_window(ts_b, px_b)
    ok_b = compare("B (saved json)", got_b, ref["B"], "exact")

    # --- Window B': exact, from saved inputs, ref is run003.json (separate source) ---
    d = json.load(open("runs/data_Bprime_hourly_20240806_20241103.json"))
    ts_bp, px_bp = d["ts"], d["close"]
    t0 = dt.datetime.fromtimestamp(ts_bp[0], dt.timezone.utc)
    t1 = dt.datetime.fromtimestamp(ts_bp[-1], dt.timezone.utc)
    print(f"\nSaved B' inputs: n={len(px_bp)}  {t0.date()} -> {t1.date()}")
    got_bp = run_window(ts_bp, px_bp)
    ok_bp = compare("B' (saved json, ref run003.json)", got_bp, ref_bprime, "exact")

    json.dump({"A_saved": got_a, "B_saved": got_b, "Bprime_saved": got_bp,
               "gate": {"A": "exact:" + ("PASS" if ok_a else "FAIL"),
                        "B": "exact:" + ("PASS" if ok_b else "FAIL"),
                        "Bprime": "exact:" + ("PASS" if ok_bp else "FAIL")}},
              open("runs/gate003.json", "w"))
    print(f"\nOVERALL GATE: {'PASS' if ok_a and ok_b and ok_bp else 'FAIL'} — saved runs/gate003.json")
