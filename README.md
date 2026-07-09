# CLRE — Concentrated-Liquidity Rebalancing Study (v3)

**Question:** how should a Uniswap-v3-style LP position be rebalanced, and
what does each policy actually cost?

**Headline (v3):** exit-triggered re-centering at widths inside the
oscillation amplitude is *structurally* short mean-reversion at its own
trigger scale. Threshold ±5% needed a **111.6%** fee APR to break even on a
trending 90d window and **108.0%** on a fully disjoint oscillatory window —
and loses on **200 of 200** pure mean-reverting (OU) synthetic paths, median
break-even 116.5% [5–95pct: 89.7–141.3]. Explicit costs are 3–4% of the
damage; the rest is inventory drift crystallised by the policy itself. The
regime-dependent object is the static tight range (33.5% trending → 1.2%
oscillatory), not the re-centering decision.

**Read first:** `final/CLRE_v3_Rebalancing_Study_v3_Marco_Amendola.pdf` (4 pages).

## Reproduce
```
python3 tests.py              # 9/9 sanity suite — required before any run
python3 reproduce_gate.py     # replays published numbers from archived inputs
python3 adversarial_check3.py # every PDF number verified against runs/*.json
```
Archived hourly inputs for every window ship in `runs/` — the gate runs
offline. Synthetic study: seed 42, parameters logged before the run.

## Structure
- `clre.py` — engine: exact v3 position math, policies, costs, evaluation
- `tests.py` — nine-test validation suite
- `reproduce_gate.py`, `adversarial_check3.py` — gates
- `run2.py`, `scan_windows.py`, `build_pdf3.py` — runs and artifact build
- `runs/` — archived inputs + full outputs (run002/003/004, gate, scan, fee anchor)
- `research_log.md` — pre-registered predictions (including the failed ones),
  two v2 errata, belief updates. The credibility artifact.
- `adversarial.md` — both adversarial passes, findings triaged, repairs
- `brief.md` — origin and acceptance criteria

## Method discipline
Predictions pre-registered before every run (Run 002: 2/4 failed — the
failures produced the main finding; Run 003: 5/5; Run 004: 4/4). Reproduction
gate before any new run. Fee income inverted (break-even APR), not assumed;
pool-level anchor measured (DeFiLlama series; Dune query 7923963 published).
Known limitations and the production path per gap are stated inside the PDF.

*Marco Amendola · July 2026 · on-chain research under [Xpertknight](https://dune.com/xpertknight) · not investment advice*
