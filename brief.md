# STUDY-001 — How should a Uniswap-v3-style LP position be rebalanced?
## Origin
Internal study. Originating question, verbatim, asked verbally in an
interview context: "how would you craft a rebalancing in a v3 pool".
## External brief (verbatim)
N/A — no written external brief exists. Recorded 2026-07-09; this field is
closed, not pending.
## Acceptance criteria (v3)
- [ ] Reproduction gate passed before any new run (mode stated per window)
- [ ] ≥2 fully disjoint regimes/windows behind any path-dependent claim
- [ ] Dual denomination (USD + ETH terms) where sign-relevant
- [ ] Break-even convention stated explicitly in the artifact
- [ ] Every load-bearing empirical anchor measured or cited, none asserted
- [ ] Synthetic mechanism test with interval estimates
- [ ] Limitations + production path per gap
- [ ] Adversarial pass on v3, documented, separate from build
