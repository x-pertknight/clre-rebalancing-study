"""Sanity tests. If any of these fail, no backtest output is trustworthy."""
import math
from clre import (amounts_from_liquidity, liquidity_for_value, position_value,
                  capital_efficiency, pqs, realised_vol, simulate_hodl,
                  simulate_lp, Costs)

EPS = 1e-9


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def test_value_matches_deposit():
    # A freshly sized position must be worth exactly the deposit.
    for P, w in [(2000, 0.05), (2000, 0.5), (1234.5, 0.01)]:
        Pa, Pb = P / (1 + w), P * (1 + w)
        L = liquidity_for_value(10_000, P, Pa, Pb)
        assert approx(position_value(L, P, Pa, Pb), 10_000)


def test_value_continuity_at_bounds():
    # Position value must be continuous crossing Pa and Pb.
    P, w = 2000.0, 0.05
    Pa, Pb = P / (1 + w), P * (1 + w)
    L = liquidity_for_value(10_000, P, Pa, Pb)
    for edge in (Pa, Pb):
        below = position_value(L, edge * (1 - 1e-9), Pa, Pb)
        above = position_value(L, edge * (1 + 1e-9), Pa, Pb)
        assert approx(below, above, 1e-5)


def test_out_of_range_composition():
    # Above range -> all quote; below range -> all base.
    P, w = 2000.0, 0.05
    Pa, Pb = P / (1 + w), P * (1 + w)
    L = liquidity_for_value(10_000, P, Pa, Pb)
    x, y = amounts_from_liquidity(L, Pb * 1.1, Pa, Pb)
    assert x == 0 and y > 0
    x, y = amounts_from_liquidity(L, Pa * 0.9, Pa, Pb)
    assert y == 0 and x > 0


def test_full_range_matches_sqrt_law():
    # v2 law: for 50/50 entry, V(P) = V0 * sqrt(P/P0) (up to tiny bound error).
    P0 = 2000.0
    res = simulate_lp([P0, P0 * 1.44], 10_000, 0.0, Costs(gas_usd=0),
                      mode="full", name="full")
    assert approx(res.values[-1], 10_000 * math.sqrt(1.44), 1e-3)


def test_lp_never_beats_hodl_pre_fee_without_rebalance():
    # Static concentrated LP value <= HODL value at every point (pre-fee).
    prices = [2000 * (1 + 0.001 * i) for i in range(200)]
    hodl = simulate_hodl(prices, 10_000)
    lp = simulate_lp(prices, 10_000, 0.05, Costs(gas_usd=0), mode="static")
    assert all(lv <= hv + 1e-6 for lv, hv in zip(lp.values, hodl.values))


def test_pqs_bounds_and_extremes():
    trend = [0.01] * 50
    assert approx(pqs(trend), 1.0)
    osc = [0.01, -0.01] * 50
    assert pqs(osc) < 0.02
    assert pqs([]) is None


def test_vol_scaling():
    r = realised_vol([100, 101, 100.5, 102, 101.2, 103], periods_per_year=8760)
    assert r["n_returns"] == 5
    assert approx(r["sigma_window"], r["sigma_period"] * math.sqrt(5))


def test_capital_efficiency_sane():
    # Narrower range -> higher efficiency; wide range -> approaches 1.
    assert capital_efficiency(0.02) > capital_efficiency(0.10) > capital_efficiency(1.0) > 1.0


def test_threshold_rebalance_pays_costs():
    # Force an exit and confirm costs were charged and range re-centered.
    prices = [2000.0] + [2000 * (1 + 0.002) ** i for i in range(1, 60)]
    costs = Costs()
    lp = simulate_lp(prices, 10_000, 0.02, costs, mode="threshold")
    assert lp.events, "expected at least one rebalance"
    assert lp.total_cost > 0
    assert all(e.cost >= costs.gas_usd for e in lp.events)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns:
        f()
        print(f"PASS {f.__name__}")
    print(f"\n{len(fns)}/{len(fns)} sanity tests passed")
