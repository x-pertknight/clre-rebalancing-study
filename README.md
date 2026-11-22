# Uniswap v3 rebalancing: a simulation on Coinbase ETH/USD hourly candles

[![reproduce](https://github.com/x-pertknight/clre-rebalancing-study/actions/workflows/reproduce.yml/badge.svg)](https://github.com/x-pertknight/clre-rebalancing-study/actions/workflows/reproduce.yml)

CLRE (Concentrated Liquidity Rebalancing Engine) is the simulator in `clre.py`. It replays Coinbase ETH/USD hourly candles through exact Uniswap v3 position math. It does not use onchain pool data. The only pool data is a daily fee APY series for one pool, taken from the DeFiLlama yields API and used as a reference point.

Should you auto-rebalance a tight Uniswap v3 position? Mostly no.

- At a width of ±5%, re-centering on exit needs a 111.6% fee APR just to break even on a trending 90-day window, and 108.0% on a separate oscillating one.
- Explicit costs (gas and swap fees) are only 3 to 4% of the damage. The rest is the policy itself. Re-centering at its own trigger scale is structurally short realized variance, a discrete LVR maximiser (Milionis et al. 2022), whatever the path structure. The v2 label "short mean reversion" was falsified by the OU control and retracted. The research log keeps the retraction.
- What does depend on the regime is the static tight range (33.5% trending, 1.2% oscillating), not the re-centering decision.

![Break-even fee APR](assets/breakeven.png)

Question. How should a Uniswap v3 style LP position be rebalanced, and what does each policy actually cost?

Full result. A ±5% threshold policy loses on 200 of 200 pure mean-reverting (OU) synthetic paths, with a median break-even of 116.5% (5th to 95th percentile 89.7 to 141.3).

Read first. `final/CLRE_v3.1_Rebalancing_Study_Marco_Amendola.pdf` (4 pages).

## Reproduce

```
bash reproduce.sh
```

It runs offline with the Python standard library and `pdftotext`, and exits non zero on any mismatch:

* `tests.py`: the 9 sanity tests.
* `reproduce_gate.py`: replays the published break even numbers from the archived inputs in `runs/` (111.6%, 125.5% and 108.0% for the ±5% threshold policy on windows A, B and B').
* `check_numbers.py`: checks every load bearing number in the PDF against `runs/*.json`, and recomputes the fee summary in `runs/fee_apr_measured.json` from the daily values in `runs/fee_apy_daily.csv`.

The same script runs in GitHub Actions on every push and pull request. Rerunning `run2.py` or `scan_windows.py` fetches Coinbase candles over the network; that is not part of `reproduce.sh` or CI. The synthetic study uses seed 42, with parameters logged before the run. The fetch scripts, the PDF build and the figure need the packages in requirements.txt.

## Structure

- `clre.py`. Engine: exact v3 position math, policies, costs, evaluation.
- `tests.py`. Nine-test validation suite.
- `reproduce.sh`, `reproduce_gate.py`, `check_numbers.py`. Gates.
- `run2.py`, `scan_windows.py`, `build_pdf3.py`. Runs and PDF build. A rerun of `run2.py` writes to `out/` and never overwrites the reference runs. Superseded scripts and earlier PDF versions are in `archive/`.
- `make_figure.py`. README figure.
- `runs/`. Archived inputs and full outputs (run002, run003, run004, run004b, gate, scan, fee anchor).
- `research_log.md`. Pre-registered predictions including the failed ones, two v2 errata, belief updates.
- `review.md`. Both review passes, findings triaged, repairs.
- `brief.md`. Research question and acceptance criteria.

## Method

Predictions were registered before every run. Run 002 failed 2 of 4, and the failures produced the main finding. Run 003 hit 5 of 5 and run 004 hit 4 of 4. The reproduction gate runs before any new run. Fee income is inverted into a break-even APR, not assumed. The pool level reference is the DeFiLlama daily fee APY series for the Uniswap v3 ETH/USDC 0.05% pool. The daily series is in `runs/fee_apy_daily.csv` and its summary in `runs/fee_apr_measured.json`. Known limitations, and how each gap would be closed in production, are stated in the PDF.

## What this means in practice

The break-even numbers are a bar. A pool clears it only if its sustained fee APR exceeds the break-even for your width and regime. For scale, the one pool measured here, Uniswap v3 ETH/USDC 0.05%, had a mean daily fee APY of 14.9% from 9 April to 7 July 2026 (90 days, 95th percentile day 36.3%) and 17.5% from 6 August to 2 November 2024 (89 days, 95th percentile day 30.0%). DeFiLlama labels this yield APY (apyBase, fees only), while the break even figures in this study are APRs. The daily series is in `runs/fee_apy_daily.csv` and its summary in `runs/fee_apr_measured.json`. Before turning on any auto-rebalancing policy:

1. Measure the pool's realised fee APR over a window at least as long as your expected holding period (the daily series used here is in `runs/fee_apy_daily.csv`).
2. Compare it to the break-even for your width from this study.
3. If it does not clear, a static range, re-chosen only when the regime changes, beat every re-centering policy tested here.

Marco Amendola, July 2026. Not investment advice.

Code is MIT licensed. Text and data are CC BY 4.0.
