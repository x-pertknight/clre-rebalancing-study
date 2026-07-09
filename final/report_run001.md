# CLRE Run 001 — ETH/USD hourly, 90 days

Window: 2026-04-09 → 2026-07-08 UTC · 2156 hourly closes · P0 $2,165 → PT $1,737 (-19.8%)

Deposit $100,000 · costs: 5 bps fee + 5 bps slippage per swap + $3 gas/event

## Regime diagnostics

- Realised vol: σ_hourly 0.584% · σ_window 27.1% · σ_annualised 55%
- PQS (full window): **0.028** (oscillatory)
- Static ±5% decomposition: in-range PQS 0.079 · out-of-range PQS 0.016 (hourly-close approximation)

## Policy comparison (pre-fee, net of rebalance costs)

| Policy | Final value | LVH vs HODL | Rebalances | Rebal. cost | Time in range | Cap. eff. | Break-even fee APR |
|---|---|---|---|---|---|---|---|
| HODL 50/50 (baseline) | $90,112 | — | 0 | $0 | — | — | — |
| Full range (v2-style) | $89,567 | -0.54% | 0 | $0 | 100% | 1.0x | 2.2% |
| Static ±15% | $83,127 | -6.98% | 0 | $0 | 60% | 14.8x | 28.4% |
| Static ±5% | $81,215 | -8.90% | 0 | $0 | 21% | 41.5x | 36.2% |
| Threshold re-center ±15% | $82,163 | -7.95% | 2 | $91 | 100% | 14.8x | 32.3% |
| Threshold re-center ±5% | $62,195 | -27.92% | 21 | $888 | 100% | 41.5x | 113.5% |
| Periodic weekly re-center ±10% | $79,257 | -10.86% | 12 | $291 | 97% | 21.5x | 44.1% |

**Break-even fee APR** = pool-level organic fee APR the position needed (after capital-efficiency and time-in-range scaling is *excluded* — this is the raw fee income on deposited capital required to match HODL). No volume data assumed; this is the inversion of the unknown.

## Net outcome under assumed pool fee APRs (secondary; stated model)

Position accrual model: pool APR × capital efficiency × time-in-range. This is an assumption, not a measurement.

| Policy | 5% APR | 15% APR | 30% APR | 60% APR |
|---|---|---|---|---|
| Full range (v2-style) | +0.69% | +3.15% | +6.84% | +14.22% |
| Static ±15% | +4.00% | +25.98% | +58.95% | +124.88% |
| Static ±5% | +1.83% | +23.27% | +55.45% | +119.79% |
| Threshold re-center ±15% | +10.28% | +46.72% | +101.39% | +210.74% |
| Threshold re-center ±5% | +23.12% | +125.20% | +278.31% | +584.54% |
| Periodic weekly re-center ±10% | +14.66% | +65.68% | +142.21% | +295.28% |

## ACR diagnostic (static ±5%, mid 15% APR scenario)

- Fee yield over window (modeled): 32.17%
- ACR base: **1.19** · stress-adjusted (haircut 20%, stated assumption): **0.95**

## Worst rebalances by hand (threshold ±5%) — read, not just counted

| t (hr) | Price | Value before | Swapped | Cost | Reason |
|---|---|---|---|---|---|
| 53 | $2,306 | $101,235 | $50,617 | $53.62 | exit_up |
| 105 | $2,354 | $98,662 | $49,331 | $52.33 | exit_up |
| 71 | $2,196 | $97,511 | $48,755 | $51.76 | exit_down |
| 588 | $2,351 | $96,049 | $48,024 | $51.02 | exit_up |
| 485 | $2,238 | $94,928 | $47,464 | $50.46 | exit_down |

## Cost decomposition (threshold ±5%)

- Total shortfall vs HODL: $27,917
- Of which explicit rebalance costs (fees+slippage+gas): $888
- Of which crystallised inventory drift: $27,029
