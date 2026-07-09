# Research Log — CLRE

## Run 001 — ETH/USD hourly, ~90 days, policy comparison

**Hypothesis.** Rebalancing policy choice on a v3 position is dominated by path
regime: in trending sub-periods, threshold re-centering systematically sells
low / buys high (it realises inventory drift at exactly the worst moments),
so its pre-fee loss-vs-hold should be WORSE than a static range that simply
goes out of range and sits in one asset.

**Setup.** Real hourly ETH-USD closes (Coinbase), ~2160 candles. Policies:
HODL 50/50 (baseline), full-range, static ±5%, static ±15%, threshold
re-center ±5%, threshold re-center ±15%, periodic re-center weekly ±10%.
Costs: 5 bps pool fee + 5 bps slippage per swap, $3 gas per event. Fees
handled by inversion (break-even fee APR required to match HODL).

**Predictions (written before running):**
1. Static ±5% spends < 50% of the window in range.
2. Threshold ±5% executes > 15 rebalances and its pre-fee LVH is worse than
   static ±5% if the window PQS > 0.15 (any meaningful trend component).
3. Ranking of break-even fee APR (highest = worst): threshold ±5% >
   periodic ±10% > static ±5% > threshold ±15% > static ±15% > full range.
4. Full-range break-even APR lands in single digits annualised; tight
   threshold policy demands > 40% APR to justify itself.
5. Rebalance *event costs* (fees+gas) are the minority of the damage;
   the majority is the crystallised inventory drift itself.

**Result.** (filled after run — see report)

**Updated belief.** (filled after run)

**Result (Run 001, 2026-04-09 → 2026-07-08, ETH -19.8%):**
1. Static ±5% in range 21% of the window. PREDICTED <50% — HIT.
2. Threshold ±5%: 21 rebalances, LVH -27.9% vs static ±5% -8.9%. HIT.
3. Break-even APR ranking: 113.5% > 44.1% > 36.2% > 32.3% > 28.4% > 2.2% —
   exactly the predicted order, all six. HIT.
4. Full range 2.2% break-even (single digits ✓); tight threshold 113.5% (>40% ✓).
5. Damage decomposition: $27,029 crystallised drift vs $888 explicit costs —
   97% of the shortfall is drift, not fees/gas. HIT.

**Anomaly caught by reading the output:** window PQS = 0.028 reads "strongly
oscillatory" while price fell 19.8%. Cause: PQS thresholds (0.20/0.45) were
calibrated on DAILY returns; hourly granularity lengthens the path denominator
and mechanically compresses PQS toward 0. PQS is granularity-dependent and
thresholds must be re-calibrated per sampling frequency, or PQS computed on
daily closes alongside the hourly sim. Logged as framework revision item.

**Second flag:** the assumed-fee scenario table overstates tight-range outcomes
(+584% at 60% APR for threshold ±5%): the accrual model pool_APR × efficiency ×
time-in-range treats capital efficiency as if competing LPs don't also
concentrate. Real position accrual compresses toward pool average as
concentration becomes crowded. Table is an upper bound; break-even inversion
(which assumes nothing about fees) remains the primary result.

**Updated belief.** In a directional regime, the rebalancing *policy* is the
dominant risk decision, not the range width: threshold re-centering converts
path risk into realised losses at every exit (sell-low/buy-high by
construction), and explicit costs are noise (3%) next to crystallised drift
(97%). "Self-balancing" ≠ self-protecting: automation schedules the drift
realisation, it does not remove it. The defensible design is regime-gated:
wide-or-full range by default, tighten only when daily-PQS and ACR jointly
support it, and treat every re-center as a trade that must be justified, not
hygiene.

## Run 002 — second regime (oscillatory window) + ETH denomination

**Purpose.** Repair the two fatal review findings: (a) single-regime evidence,
(b) quote-denomination baseline doing silent work for the thesis.

**Predictions (written before running):**
1. In a window selected for low daily-PQS / small net move, the policy ranking
   by break-even APR partially INVERTS: threshold ±5% break-even drops by an
   order of magnitude (from 113.5% toward 10-30%) because exits are followed by
   mean reversion instead of continuation.
2. Tight policies' pre-fee LVH in the oscillatory window is a small negative
   (-1% to -4%), dominated by explicit costs rather than drift (cost share of
   damage > 30%, vs 3% in Run 001).
3. ETH-denominated results in Run 001 (down market): all LP policies BEAT
   HODL-100%-ETH in ETH terms (LPing sheds ETH into the fall), reversing the
   USD-terms ranking sign — demonstrating denomination is a first-order choice.
4. Regime-gating conclusion survives both fixes, but in conditional form:
   ranking is regime-dependent, so the policy decision requires the regime
   gauge — computed on DAILY returns after the granularity fix.

**Result (Run 002):**
Window A (trending, 2026-04-09→07-08, net -18.5%, σ 55%, PQS daily 0.120):
matches Run 001 within data-shift tolerance (threshold ±5% BE 111.6%).
Window B (oscillatory, 2026-03-02→05-31, net +3.2%, σ 52%, PQS daily 0.001):
- P1 WRONG. Threshold ±5% break-even did NOT collapse — it got WORSE
  (125.5% vs 111.6%, 24 rebalances). Mechanism: "oscillatory at daily scale"
  ≠ oscillatory at range scale. With trigger width inside the oscillation
  amplitude, exit-triggered re-centering buys every local extreme and the
  reversion then exits it on the other side. The policy is structurally
  short-mean-reversion at its own trigger scale, in BOTH regimes.
- P2 WRONG. Threshold ±5% LVH in B = -30.9%, cost share 4% — drift dominates
  in the oscillatory window too, for the same mechanism.
- The order-of-magnitude collapse happened on the STATIC tight range instead:
  BE 33.5% (A) → 2.1% (B). Static ±5% is cheap when price keeps returning.
- P3 RIGHT. ETH-denominated, window A: full range +10.8%, static ±5% +1.2%
  vs 100%-ETH hold — every no-rebalance policy beats holding ETH in ETH terms
  in a drawdown. Denomination is a first-order design choice, confirmed.
- P4 revised. Daily PQS discriminates regimes comparatively (0.120 vs 0.001,
  two orders of magnitude) but absolute thresholds don't transfer across
  window lengths. Use PQS as a comparative gauge; thresholds require
  per-(frequency, window) calibration.

**Updated belief (supersedes Run 001 conclusion).** Exit-triggered re-centering
at tight widths is a bad POLICY in both regimes, not a bad fit to one regime:
it converts volatility into realised drift regardless of path structure. The
regime-dependent object is the STATIC tight range (excellent in oscillation,
expensive in trend). Operating rule v2: never re-center on exit at widths
inside the oscillation amplitude; hold static-tight in measured oscillatory
regimes, widen or exit in trending ones; re-center only on regime change, not
on range exit. The assumed-APR scenario table from Run 001 is RETIRED — its
uncrowded-efficiency model produced a table that contradicted the text
(caught in adversarial review); break-even inversion is the sole primary lens.

## v2 ERRATUM — window overlap (logged 2026-07-09, pre-Run-003)

Windows A (2026-04-09→07-08) and B (2026-03-02→05-31) share 2026-04-09→05-31:
53 of 90 days (~59%). "Two opposite regimes" therefore overstated evidential
independence — the regime labels stand (PQS daily 0.120 vs 0.001) but the two
paths are not independent samples. Repair: Run 003 replaces B with a fully
disjoint oscillatory window (end ≤ 2026-04-08). Second erratum: the hourly
inputs archived in runs/ were Run 001's fetch, not Run 002's — Run 002 window-A
inputs were never saved (protocol violation: raw inputs must be archived).
Repaired: all Run 003 inputs archived under runs/.

## Reproduction gate (2026-07-09, before Run 003)

Mode stated per amended gate definition:
- GATE 1 [EXACT, saved inputs]: runs/data_eth_usd_hourly.json replays Run 001
  published numbers digit-for-digit (BE 113.5/44.1/36.2/32.3/28.4/2.2; 21
  rebalances; $888 explicit cost). PASS.
- GATE 2 [TOLERANCE, re-fetch]: window A re-fetched from Coinbase vs
  run002.json A — every row within 0.00pp displayed (tol was BE ±1pp,
  LVH ±0.3pp). PASS.
- GATE 3 [TOLERANCE, re-fetch]: window B re-fetched vs run002.json B — 0.00pp
  displayed. PASS.
Engine + tests: 9/9. Coinbase hourly closes proved stable across fetches; the
Run-001 vs Run-002 "data shift" was a fetch-boundary shift (~21h), not candle
revision.

## Run 003 — disjoint oscillatory window B′ (PRE-REGISTERED before scan/run)

**Purpose.** Repair v2 erratum: oscillatory evidence from a window fully
disjoint from A.

**Window selection criteria (declared before scanning):** 90d of daily
ETH-USD closes, window end ≤ 2026-04-08 (disjoint from A); candidates require
|net| ≤ 5% and σ_ann ∈ [40%, 70%]; rank by lowest daily PQS; tie-breaks:
|σ_ann − 55%| (match A), then recency. Scan history: back to mid-2024, step
1 day. The single top-ranked window is selected — no discretionary override.

**Predictions (written before running):**
1. Threshold ±5% BE APR > 80% on B′ (mechanism is trigger-scale, not regime).
2. Static ±5% BE APR < 8% on B′ (order of magnitude below trending A's 33.5%).
3. Threshold ±5% explicit-cost share of damage < 15% (drift dominates in
   oscillation too).
4. Ranking: threshold ±5% highest BE of all six policies; full range lowest.
5. Threshold ±5% executes ≥ 12 rebalances on B′.

## Run 004 — synthetic mechanism test, OU vs GBM (PRE-REGISTERED)

**Purpose.** Convert "observed in 2 windows" into a structural demonstration:
if exit-triggered re-centering at widths inside the oscillation amplitude is
short mean-reversion by construction, it must lose on PURE mean-reverting
paths, where no macro trend exists to blame.

**Design (declared before running).** 200 paths per process, 2160 hourly
steps (90d), seed=42. OU on log-price: stationary sd 7% (±2sd band ≈ ±14% >
5% trigger), σ_ann = 52% ⇒ θ = σ_h²/(2·0.07²), half-life ≈ 9.2d, X₀ = μ.
GBM control: zero drift, same σ_h. Policies per path: full range, static ±5%,
threshold ±5%. Costs identical to real runs. Metrics: BE APR and LVH
distributions (median, 5–95 pct) — the study's first interval estimates.

**Predictions (written before running):**
S1. Threshold ±5% median BE > 40% on OU AND > 40% on GBM.
S2. Threshold ±5% BE > static ±5% BE in ≥ 95% of OU paths (paired).
S3. Static ±5% median BE < 10% on OU.
S4. Static ±5% median BE on GBM > 3× its OU median (the regime-dependent
    object is the static range, not the re-centering policy).

**Result (Run 003, B′ = 2024-08-06 → 2024-11-03, selected top-ranked by
pre-registered scan criteria — 4 candidates qualified, no override):**
Realized on hourly: net −2.3%, σ_ann 56%, PQS daily 0.0040 (A: 0.120 — two
orders of magnitude). Fully disjoint from A.
| policy | LVH usd | LVH eth | reb | cost$ | TIR | BE APR |
| Full range | −0.01% | +1.19% | 0 | 0 | 100% | 0.0% |
| Static ±15% | −0.10% | +1.09% | 0 | 0 | 100% | 0.4% |
| Static ±5% | −0.29% | +0.90% | 0 | 0 | 67% | 1.2% |
| Threshold ±15% | −6.90% | −5.86% | 2 | 98 | 100% | 28.3% |
| Threshold ±5% | −26.34% | −25.78% | 18 | 811 | 100% | 108.0% |
| Periodic wk ±10% | −11.41% | −10.49% | 12 | 294 | 91% | 46.8% |
P1 HIT (108.0% > 80%). P2 HIT (1.2% < 8%). P3 HIT (explicit-cost share 3.1%,
drift 96.9%). P4 HIT (ranking holds end-to-end). P5 HIT (18 rebalances).
5/5 — the v2 finding survives on fully independent evidence. Worst events
read by hand: five largest re-centers each swap ≈ half the position at the
extreme that forced the exit ($51.75 max event cost) — same signature as A.

**Result (Run 004, synthetic, seed 42, 200 paths/process, 2160 hourly steps):**
OU (pure mean reversion, stat. sd 7%, half-life 9.2d, σ 52%):
  full BE median 0.1% [0.0, 1.0]; static ±5% median 4.1% [0.0, 23.6];
  threshold ±5% median 116.5% [89.7, 141.3]; reb median 24 [18, 29].
GBM (pure diffusion, zero drift, σ 52%):
  full 1.4% [0.0, 9.1]; static ±5% 29.3% [1.0, 77.7];
  threshold ±5% 115.9% [86.0, 161.4]; reb median 24 [18, 31].
S1 HIT (116.5% OU / 115.9% GBM, both > 40% — by nearly 3×).
S2 HIT (threshold > static in 100.0% of OU paths, paired).
S3 HIT (static ±5% on OU: 4.1% < 10%). S4 HIT (29.3% > 3 × 4.1%).
4/4. The mechanism claim is upgraded from "observed in 2 windows" to
structural: on paths of PURE mean reversion — the regime a re-centering
policy would most plausibly be defended for — exit-triggered ±5%
re-centering loses in 200 of 200 paths, 5th percentile BE 89.7%. Both real
windows (111.6%, 108.0%) sit inside the synthetic 5–95 bands.

**Measured fee anchor (replaces asserted "for scale" bound):**
Pool-level fee APY (fees/TVL), Uniswap v3 ETH/USDC 0.05% mainnet
(0x88e6…5440), DeFiLlama daily apyBase series: window A mean 14.9% (median
12.0%, avg TVL $95M); B′ mean 17.5% (median 16.3%, avg TVL $151M). Dune
query for the same metric from dex.trades + balances_ethereum.daily_updates
published as query_id 7923963; execution pending account credit refresh —
logged, not hidden. Required-capture framing: threshold ±5% BE ⇒ sustained
position capture ≈ 6.2–7.5× pool average for 90d (uncrowded theoretical
ceiling for ±5% is 41.5×, but it assumes all competing liquidity is
full-range; realized multipliers on majors compress toward ~1×). Static ±5%
on B′ ⇒ in-range-equivalent 1.8% APR ≈ 0.10× pool average.

**Updated belief (v3, supersedes Run 002 conclusion in evidential strength,
not in content).** Unchanged in direction, upgraded in support: (1)
exit-triggered re-centering at widths inside the oscillation amplitude is
structurally short mean-reversion at its own trigger scale — now shown on
disjoint real windows AND 400 synthetic paths including pure OU; (2) the
regime-dependent object is the static tight range (BE 33.5% trending →
1.2% disjoint-oscillatory; synthetic 29.3% GBM → 4.1% OU); (3) explicit
costs remain noise (3–4%) against crystallised drift everywhere tested.
Break-even convention now stated explicitly: APR on deposited capital over
the full window; time-in-range dilution applies symmetrically to required
and realized accrual; in-range equivalents reported for static ranges.
