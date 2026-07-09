# Adversarial Pass — STUDY-001 (warm context, prompt #1)
| # | Finding | Severity | Repair | Status |
|---|---|---|---|---|
| 1 | Scenario table contradicted conclusion (uncrowded-efficiency model) | fatal | table retired; break-even inversion sole lens | fixed v2 |
| 2 | Single regime (n=1 window) | fatal | second (oscillatory) window; hypothesis rejected, better finding | fixed v2 |
| 3 | Baseline denomination flattered thesis | repairable | ETH-terms column added | fixed v2 |
| 4 | Regime gauge misclassified own sample | repairable | comparative use; calibration limits stated | fixed v2 |
| 5 | LVR literature uncited | repairable | Milionis et al. 2022 anchored | fixed v2 |
| 6 | MEV treated as production detail | repairable | reframed as structural policy cost | fixed v2 |
| 7 | Single path per regime, no intervals; Coinbase proxy; toy cost model | cosmetic-to-repairable | disclosed in limitations; production path items | open |

# Adversarial Pass — STUDY-001 v3 (2026-07-09, post-build, separate from build pass)
Method: mechanical numbers-vs-text verification of every load-bearing figure
in the PDF against runs/*.json (adversarial_check3.py, ships with package);
derived-claim recomputation (in-range equivalents, capture multipliers,
uncrowded ceiling, haircut arithmetic); glyph render check at 150 dpi;
page-map orphan check; worst-events regeneration from canonical archived
inputs; prediction-order audit (pre-registration precedes results in log).

| # | Finding | Severity | Repair | Status |
|---|---|---|---|---|
| 8 | Worst-events table hours carried the v2 fetch indexing (+13h offset vs canonical archived dataset); prices, values and costs identical to the cent | repairable | table regenerated from archived window-A inputs (hours 66/118/84/601/498) | fixed v3 |
| 9 | "Cleared with a 90% haircut" true on exact values (required capture 0.0999×) but false if recomputed from the artifact's own rounded figures (1.79% vs 1.75%) | repairable | rephrased in exact, rounding-robust form: adequacy fails only beyond ≈90% sustained collapse | fixed v3 |
| 10 | Research log stated uncrowded ceiling 41.6×; engine formula gives 41.49× | cosmetic | corrected to 41.5× in log; doc already correct | fixed v3 |
| 11 | Window-A results table splits page 1→2 (header row repeats) | cosmetic | accepted; forcing KeepTogether orphans page 1 | accepted |

Carried finding closed: v1/v2 #7 (single path per regime, no interval
estimates) — CLOSED by Run 004 (400 synthetic paths, 5–95 pct intervals) and
by the disjoint-window repair (Run 003). Remaining open production items are
in the limitations table of the artifact itself.
