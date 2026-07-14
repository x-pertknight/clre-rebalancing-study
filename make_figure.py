"""Generate assets/breakeven.png for the README."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS_DIR = Path("runs")
OUT_PATH = Path("assets/breakeven.png")

FALLBACK = {
    "Trending 90d window, threshold ±5%": (111.6, None, None),
    "Disjoint oscillatory window, threshold ±5%": (108.0, None, None),
    "OU synthetic median": (116.5, 89.7, 141.3),
}


def find_break_even_values():
    """Search runs/*.json for any key containing 'break_even' (case-insensitive)."""
    values = {}
    for path in sorted(RUNS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        _collect(data, path.stem, values)
    return values


def _collect(obj, source, values, prefix=""):
    if isinstance(obj, dict):
        for key, val in obj.items():
            if "break_even" in key.lower() and isinstance(val, (int, float)):
                values[f"{source}:{prefix}{key}"] = (val, None, None)
            else:
                _collect(val, source, values, prefix=f"{prefix}{key}.")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _collect(item, source, values, prefix=f"{prefix}[{i}].")


def main():
    data = find_break_even_values() or FALLBACK

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
