"""Generate assets/breakeven.png for the README."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS_DIR = Path("runs")
OUT_PATH = Path("assets/breakeven.png")


def _row(rows, name):
    return next(r for r in rows if r["name"] == name)


def _median(sorted_vals):
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


def _percentile_lower(sorted_vals, p):
    idx = int((p / 100) * (len(sorted_vals) - 1))
    return sorted_vals[idx]


def load_values():
    """Pull the three published break-even figures from the canonical runs/*.json."""
    run002 = json.loads((RUNS_DIR / "run002.json").read_text())
    trending_be = _row(run002["A"]["rows"], "Threshold ±5%")["be"] * 100

    run003 = json.loads((RUNS_DIR / "run003.json").read_text())
    oscillatory_be = _row(run003["rows"], "Threshold ±5%")["be"] * 100

    run004 = json.loads((RUNS_DIR / "run004.json").read_text())
    thr5 = sorted(run004["ou"]["thr5"])
    ou_median = _median(thr5) * 100
    ou_lo = _percentile_lower(thr5, 5) * 100
    ou_hi = _percentile_lower(thr5, 95) * 100

    return {
        "Trending 90d window, threshold ±5%": (trending_be, None, None),
        "Disjoint oscillatory window, threshold ±5%": (oscillatory_be, None, None),
        "OU synthetic median": (ou_median, ou_lo, ou_hi),
    }


def main():
    data = load_values()

    labels = list(data.keys())
    centers = [data[l][0] for l in labels]
    lo = [data[l][1] for l in labels]
    hi = [data[l][2] for l in labels]

    xerr = None
    if any(v is not None for v in lo):
        xerr = [
            [c - (l if l is not None else c) for c, l in zip(centers, lo)],
            [(h if h is not None else c) - c for c, h in zip(centers, hi)],
        ]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    y_pos = range(len(labels))
    ax.barh(y_pos, centers, xerr=xerr, color="#4C72B0", capsize=4)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Break-even fee APR (%)")

    ax.axvline(x=50, linestyle="--", color="gray")
    ax.text(
        50, 1.02, "typical good v3 pool",
        transform=ax.get_xaxis_transform(),
        ha="center", va="bottom", fontsize=9, color="gray",
    )

    ax.set_title(
        "Fee APR needed just to break even — "
        "exit-triggered re-centering, ±5% width"
    )
    fig.tight_layout()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=160)


if __name__ == "__main__":
    main()
