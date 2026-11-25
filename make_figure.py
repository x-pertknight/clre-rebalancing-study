"""Generate assets/breakeven.png for the README from the archived runs in runs/.

Every number in the figure is read from runs/*.json. The pool reference is the
DeFiLlama daily fee APY summary in runs/fee_apr_measured.json, for the same windows.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

RUNS_DIR = Path("runs")
OUT_PATH = Path("assets/breakeven.png")

INK, SOFT, GRID = "#1c1c1c", "#555555", "#e3e3e3"
BLUE, ORANGE, GREY = "#2a6fb0", "#d9822b", "#9aa3ad"
plt.rcParams["font.family"] = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


def _be(rows, name):
    return next(r for r in rows if r["name"] == name)["be"] * 100


def _median(sorted_vals):
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


def _percentile_lower(sorted_vals, p):
    # same rule as check_numbers.py: index int(p * (n - 1)) of the sorted values
    return sorted_vals[int((p / 100) * (len(sorted_vals) - 1))]


def load_values():
    run002 = json.loads((RUNS_DIR / "run002.json").read_text())["A"]
    run003 = json.loads((RUNS_DIR / "run003.json").read_text())
    run004 = json.loads((RUNS_DIR / "run004.json").read_text())
    fee = json.loads((RUNS_DIR / "fee_apr_measured.json").read_text())["windows"]
    thr5 = sorted(run004["ou"]["thr5"])
    return {
        "thr_A": _be(run002["rows"], "Threshold ±5%"),
        "thr_Bp": _be(run003["rows"], "Threshold ±5%"),
        "static_A": _be(run002["rows"], "Static ±5%"),
        "static_Bp": _be(run003["rows"], "Static ±5%"),
        "ou_median": _median(thr5) * 100,
        "ou_p5": _percentile_lower(thr5, 5) * 100,
        "ou_p95": _percentile_lower(thr5, 95) * 100,
        "ou_n": len(thr5),
        "fee_A": next(w for w in fee if w["label"].startswith("A"))["fee_apy_mean"],
        "fee_Bp": next(w for w in fee if w["label"].startswith("B'"))["fee_apy_mean"],
    }


def main():
    v = load_values()
    # (label, value, colour, header?) top to bottom
    rows = [
        ("Re-centered whenever price leaves the range", None, None),
        ("Trending window, Apr to Jul 2026", v["thr_A"], BLUE),
        ("Oscillating window, Aug to Nov 2024", v["thr_Bp"], BLUE),
        (f"Synthetic mean-reverting paths ({v['ou_n']})", v["ou_median"], BLUE),
        ("Static range, never moved", None, None),
        ("Trending window, Apr to Jul 2026", v["static_A"], GREY),
        ("Oscillating window, Aug to Nov 2024", v["static_Bp"], GREY),
    ]
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=160)
    fig.subplots_adjust(left=0.31, right=0.95, top=0.80, bottom=0.17)
    ys = list(range(len(rows)))[::-1]
    for (label, val, col), y in zip(rows, ys):
        if val is None:
            ax.text(0.03, y, label, transform=blended_transform_factory(fig.transFigure, ax.transData), ha="left", va="center",
                    fontsize=11.5, fontweight="bold", color=INK)
            continue
        ax.barh(y, val, height=0.62, color=col, zorder=3)
        # the synthetic row carries a percentile whisker, so its value label goes past the whisker
        xlab = (v["ou_p95"] if y == ys[3] else val) + 1.5
        ax.text(xlab, y, f"{val:.1f}%" + (" median" if y == ys[3] else ""), va="center", fontsize=11,
                fontweight="bold", color=INK, zorder=4)
        ax.text(-0.02, y, label, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=10.5, color=SOFT)
    # 5th to 95th percentile of the synthetic paths
    y_ou = ys[3]
    ax.plot([v["ou_p5"], v["ou_p95"]], [y_ou, y_ou], color=INK, lw=1.6, zorder=5)
    for x in (v["ou_p5"], v["ou_p95"]):
        ax.plot([x, x], [y_ou - 0.18, y_ou + 0.18], color=INK, lw=1.6, zorder=5)
    ax.text(v["ou_p5"], y_ou - 0.5, f"5th to 95th percentile: {v['ou_p5']:.1f}% to {v['ou_p95']:.1f}%",
            fontsize=9.5, color=SOFT, va="center")
    ax.set_xlim(0, 175)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    # what the pool actually paid over the same windows
    lo, hi = sorted((v["fee_A"], v["fee_Bp"]))
    ax.axvspan(lo, hi, ymin=0, ymax=(ys[1] + 0.5 + 0.6) / (len(rows) - 0.4 + 0.6), color=ORANGE, alpha=0.25, lw=0, zorder=1)
    for x in (lo, hi):
        ax.plot([x, x], [-0.6, ys[1] + 0.5], color=ORANGE, lw=1.6, zorder=2)
    ax.text(hi + 2, ys[6] - 0.05, "What the ETH/USDC 0.05% pool paid in the same windows:", fontsize=10,
            fontweight="bold", color=ORANGE, va="center")
    ax.text(hi + 2, ys[6] - 0.42, f"{v['fee_A']:.1f}% (2026) and {v['fee_Bp']:.1f}% (2024), mean daily fee APY",
            fontsize=10, color=ORANGE, va="center")
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100, 125, 150])
    ax.set_xticklabels([f"{t}%" for t in (0, 25, 50, 75, 100, 125, 150)], color=SOFT)
    ax.grid(axis="x", color=GRID, lw=1, zorder=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(axis="x", length=0)
    fig.text(0.03, 0.94, "Fee APR a ±5% Uniswap v3 range needs to break even", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Simulated on Coinbase ETH/USD hourly candles with exact v3 position math.",
             fontsize=11, color=SOFT)
    fig.text(0.03, 0.06, "Break-evens are APR. The pool figure is DeFiLlama apyBase (fees only, an APY).",
             fontsize=9.5, color=SOFT)
    fig.text(0.03, 0.03, "Mean-reverting paths: Ornstein-Uhlenbeck, seed 42, parameters in research_log.md.",
             fontsize=9.5, color=SOFT)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=160, facecolor="white")


if __name__ == "__main__":
    main()
