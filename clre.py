"""
Concentrated Liquidity Rebalancing Engine (CLRE)
=================================================
Simulates Uniswap-v3-style concentrated LP positions over a real historical
price path, under competing rebalancing policies, with explicit costs, and
evaluates outcomes against an honestly-costed HODL baseline.

Design principles (research-discipline):
- Exact v3 position math; no linearized IL approximations.
- The unknown (fee income) is INVERTED: primary output is the fee yield each
  policy would have REQUIRED to break even vs HODL, which needs no volume
  assumption. A parameterized fee-APR grid is secondary and labeled as such.
- Costs are explicit and conservative: swap fee + slippage on every
  rebalancing swap, fixed gas per rebalance event.
- Diagnostics layer: realised vol, PQS (Kaufman Efficiency Ratio form,
  bounded 0..1), in/out-of-range PQS decomposition, ACR under assumed fees.

Units convention: token0 = ETH (base), token1 = USD (quote). Prices in quote
per base. Position value expressed in quote.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field


# ----------------------------------------------------------------------------
# Uniswap v3 position math (price-space form; ticks unnecessary for research)
# ----------------------------------------------------------------------------

def amounts_from_liquidity(L: float, P: float, Pa: float, Pb: float) -> tuple[float, float]:
    """Token amounts (x=base, y=quote) held by a position of liquidity L
    with range [Pa, Pb] at current price P."""
    sa, sb, sp = math.sqrt(Pa), math.sqrt(Pb), math.sqrt(P)
    if P <= Pa:
        x = L * (sb - sa) / (sa * sb)
        y = 0.0
    elif P >= Pb:
        x = 0.0
        y = L * (sb - sa)
    else:
        x = L * (sb - sp) / (sp * sb)
        y = L * (sp - sa)
    return x, y


def liquidity_for_value(V: float, P: float, Pa: float, Pb: float) -> float:
    """Liquidity L such that the position is worth V (in quote) at price P."""
    x1, y1 = amounts_from_liquidity(1.0, P, Pa, Pb)
    unit_value = x1 * P + y1
    if unit_value <= 0:
        raise ValueError("degenerate range")
    return V / unit_value


def position_value(L: float, P: float, Pa: float, Pb: float) -> float:
    x, y = amounts_from_liquidity(L, P, Pa, Pb)
    return x * P + y


def capital_efficiency(width: float) -> float:
    """Fee capital-efficiency multiplier of a geometric range [P/k, P*k]
    (k = 1 + width) versus full-range liquidity: 1 / (1 - k^(-1/2))."""
    k = 1.0 + width
    return 1.0 / (1.0 - k ** -0.5)


# ----------------------------------------------------------------------------
# Diagnostics: realised vol, PQS, ACR
# ----------------------------------------------------------------------------

def log_returns(prices: list[float]) -> list[float]:
    return [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]


def realised_vol(prices: list[float], periods_per_year: float) -> dict:
    r = log_returns(prices)
    n = len(r)
    mu = sum(r) / n
    var = sum((x - mu) ** 2 for x in r) / (n - 1)
    sd = math.sqrt(var)
    return {
        "sigma_period": sd,
        "sigma_window": sd * math.sqrt(n),
        "sigma_annual": sd * math.sqrt(periods_per_year),
        "n_returns": n,
    }


def pqs(returns: list[float]) -> float | None:
    """Path Quality Score = |net displacement| / total path length. Bounded 0..1.
    Near 0: oscillatory (LP-favourable). Near 1: trending (LP-hostile).
    Returns None when the subset is empty or has zero path length."""
    if not returns:
        return None
    L = sum(abs(r) for r in returns)
    if L == 0:
        return None
    return abs(sum(returns)) / L


def acr(organic_fee_yield_window: float, sigma_window: float,
        stress_haircut: float = 0.0) -> dict:
    """Adjusted Compensation Ratio. Both base and stress-adjusted reported.
    The haircut is a stated model assumption, never a measurement."""
    base = organic_fee_yield_window / sigma_window if sigma_window > 0 else float("inf")
    stressed = organic_fee_yield_window * (1 - stress_haircut) / sigma_window \
        if sigma_window > 0 else float("inf")
    return {"acr_base": base, "acr_stress": stressed, "haircut": stress_haircut}


# ----------------------------------------------------------------------------
# Cost model
# ----------------------------------------------------------------------------

@dataclass
class Costs:
    pool_fee: float = 0.0005      # 5 bps swap fee tier (ETH/USDC 0.05%)
    slippage: float = 0.0005      # 5 bps execution slippage assumption
    gas_usd: float = 3.0          # per rebalance event (mint+burn+swap, L2-ish)

    def swap_cost(self, swapped_value: float) -> float:
        return swapped_value * (self.pool_fee + self.slippage)


# ----------------------------------------------------------------------------
# Policies
# ----------------------------------------------------------------------------

@dataclass
class RebalanceEvent:
    t: int
    price: float
    value_before: float
    swapped_value: float
    cost: float
    reason: str


@dataclass
class PolicyResult:
    name: str
    values: list[float] = field(default_factory=list)   # value path (pre-fee)
    in_range: list[bool] = field(default_factory=list)  # per step
    events: list[RebalanceEvent] = field(default_factory=list)
    total_cost: float = 0.0


def simulate_hodl(prices: list[float], v0: float) -> PolicyResult:
    """50/50 at t0, never touched. THE baseline."""
    p0 = prices[0]
    res = PolicyResult(name="HODL 50/50")
    for p in prices:
        res.values.append(0.5 * v0 * (p / p0) + 0.5 * v0)
        res.in_range.append(True)
    return res


def _rebalance(v: float, p: float, width: float, x_cur: float, y_cur: float,
               costs: Costs) -> tuple[float, float, float, float, float]:
    """Re-center a position at price p with geometric width. Returns
    (L_new, Pa, Pb, swapped_value, cost). Swapped value is the quote value of
    the imbalance between current holdings and the new target composition."""
    Pa, Pb = p / (1.0 + width), p * (1.0 + width)
    # target composition at current value v (pre-cost) for the new range
    L_t = liquidity_for_value(v, p, Pa, Pb)
    x_t, y_t = amounts_from_liquidity(L_t, p, Pa, Pb)
    swapped_value = abs(x_t * p - x_cur * p)  # value of base bought/sold
    cost = costs.swap_cost(swapped_value) + costs.gas_usd
    v_net = max(v - cost, 0.0)
    L_new = liquidity_for_value(v_net, p, Pa, Pb)
    return L_new, Pa, Pb, swapped_value, cost


def simulate_lp(prices: list[float], v0: float, width: float, costs: Costs,
                mode: str, period: int = 0, name: str | None = None) -> PolicyResult:
    """
    mode:
      'static'    -- set range once at t0, never rebalance
      'threshold' -- re-center whenever price exits the range
      'periodic'  -- re-center every `period` steps regardless of price
      'full'      -- full-range (v2-style); width ignored
    Values are PRE-FEE (fees handled analytically outside the path sim).
    """
    p0 = prices[0]
    if mode == "full":
        Pa, Pb = p0 / 1e6, p0 * 1e6
        w = None
    else:
        Pa, Pb = p0 / (1.0 + width), p0 * (1.0 + width)
        w = width
    L = liquidity_for_value(v0, p0, Pa, Pb)
    res = PolicyResult(name=name or mode)
    for t, p in enumerate(prices):
        v = position_value(L, p, Pa, Pb)
        inr = Pa < p < Pb
        do_reb, reason = False, ""
        if mode == "threshold" and not inr and t > 0:
            do_reb, reason = True, ("exit_up" if p >= Pb else "exit_down")
        elif mode == "periodic" and period > 0 and t > 0 and t % period == 0:
            do_reb, reason = True, "periodic"
        if do_reb:
            x_c, y_c = amounts_from_liquidity(L, p, Pa, Pb)
            L, Pa, Pb, swapped, cost = _rebalance(v, p, w, x_c, y_c, costs)
            res.events.append(RebalanceEvent(t, p, v, swapped, cost, reason))
            res.total_cost += cost
            v = position_value(L, p, Pa, Pb)
            inr = True
        res.values.append(v)
        res.in_range.append(inr)
    return res


# ----------------------------------------------------------------------------
# Evaluation
# ----------------------------------------------------------------------------

def evaluate(res: PolicyResult, hodl: PolicyResult, prices: list[float],
             periods_per_year: float, width: float | None,
             assumed_pool_fee_aprs: list[float]) -> dict:
    v0, vT = res.values[0], res.values[-1]
    h0, hT = hodl.values[0], hodl.values[-1]
    n = len(prices) - 1
    years = n / periods_per_year
    lvh = (vT - hT) / h0                      # loss-vs-hold, pre-fees, net of costs
    time_in_range = sum(res.in_range) / len(res.in_range)
    # Break-even: fee income (as % of v0) the position needed to match HODL
    breakeven_window = max(hT - vT, 0.0) / v0
    breakeven_apr = breakeven_window / years if years > 0 else float("nan")
    # Secondary: outcome under assumed pool-level fee APRs. Position-level
    # accrual = pool APR x capital efficiency x time in range (stated model).
    eff = capital_efficiency(width) if width else 1.0
    fee_scenarios = {}
    for apr in assumed_pool_fee_aprs:
        fee_yield_window = apr * eff * time_in_range * years
        net_vs_hodl = lvh + fee_yield_window
        fee_scenarios[apr] = {"fee_yield_window": fee_yield_window,
                              "net_vs_hodl": net_vs_hodl}
    return {
        "name": res.name,
        "final_value": vT,
        "lvh_pre_fee": lvh,
        "n_rebalances": len(res.events),
        "total_cost": res.total_cost,
        "time_in_range": time_in_range,
        "capital_efficiency": eff,
        "breakeven_fee_apr": breakeven_apr,
        "fee_scenarios": fee_scenarios,
    }
