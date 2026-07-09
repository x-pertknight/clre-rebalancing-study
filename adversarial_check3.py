"""Mechanical adversarial check for the v3 artifact: verifies every
load-bearing number in the PDF against runs/*.json. Run after any rebuild.
Exit criterion: FINDINGS must print 'none'."""
import json, subprocess, statistics as st
from clre import Costs, simulate_lp

txt = subprocess.run(["pdftotext", "final/CLRE_v3_Rebalancing_Study_v3_Marco_Amendola.pdf", "-"],
                     capture_output=True, text=True).stdout
r2 = json.load(open("runs/run002.json")); r3 = json.load(open("runs/run003.json"))
r4 = json.load(open("runs/run004.json")); fee = json.load(open("runs/fee_apr_measured.json"))
def q(v, p): s = sorted(v); return s[int(p * (len(s) - 1))]
f = []
for row in r2["A"]["rows"]:
    for s in (f"{row['be']*100:.1f}%", f"{abs(row['lvh_usd'])*100:.2f}%"):
        if s not in txt: f.append(f"A {row['name']}: {s} missing")
for row in r3["rows"]:
    if f"{row['be']*100:.1f}%" not in txt: f.append(f"B' {row['name']}: BE missing")
for proc in ("ou", "gbm"):
    for pol in ("full", "static5", "thr5"):
        v = r4[proc][pol]
        for s in (f"{st.median(v)*100:.1f}%", f"{q(v,.05)*100:.1f}%", f"{q(v,.95)*100:.1f}%"):
            if s not in txt: f.append(f"synth {proc}/{pol}: {s} missing")
wA = [w for w in fee["windows"] if w["label"].startswith("A")][0]
wB = [w for w in fee["windows"] if w["label"].startswith("B'")][0]
for val in (wA["fee_apy_mean"], wA["fee_apy_median"], wB["fee_apy_mean"], wB["fee_apy_median"]):
    if f"{val:.1f}%" not in txt: f.append(f"fee anchor {val:.1f}% missing")
d = json.load(open("runs/data_A_hourly_20260409_20260708.json"))
ev = sorted(simulate_lp(d["close"], 100_000.0, 0.05, Costs(), "threshold").events, key=lambda e: -e.cost)[:5]
for e in ev:
    if str(e.t) not in txt or f"${e.cost:.2f}" not in txt: f.append(f"worst event t={e.t} mismatch")
eqB5 = [r for r in r3["rows"] if r["name"] == "Static ±5%"][0]
req = (eqB5["be"] / eqB5["tir"]) / (wB["fee_apy_mean"] / 100)
assert req < 0.105, f"required capture {req:.4f}x drifted"
print("FINDINGS:", f if f else "none")
