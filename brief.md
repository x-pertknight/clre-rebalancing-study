# STUDY-001 — How should a Uniswap-v3-style LP position be rebalanced?
## Research question
How should a rebalancing policy for a Uniswap v3 position be designed, and
what does each policy cost?
## Acceptance criteria (v3)
- [ ] Reproduction gate passed before any new run (mode stated per window)
- [ ] ≥2 fully disjoint regimes/windows behind any path-dependent claim
- [ ] Dual denomination (USD + ETH terms) where sign-relevant
- [ ] Break-even convention stated explicitly in the artifact
- [ ] Every load-bearing empirical anchor measured or cited, none asserted
- [ ] Synthetic mechanism test with interval estimates
- [ ] Limitations + production path per gap
- [ ] Review pass on v3, documented, separate from the build
