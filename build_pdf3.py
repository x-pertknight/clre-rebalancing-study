"""CLRE submission PDF v3 — disjoint regimes, synthetic mechanism test,
measured fee anchor, stated break-even convention, figure, post-adversarial."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable, Image,
                                KeepTogether)

OUT = "final/CLRE_v3_Rebalancing_Study_v3_Marco_Amendola.pdf"
INK = colors.HexColor("#1a1a1a"); ACC = colors.HexColor("#0e3a5a")
GRY = colors.HexColor("#5a5a5a"); LIN = colors.HexColor("#c9c9c9"); BG = colors.HexColor("#eef2f5")
ss = getSampleStyleSheet()
S = {
 "title": ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=18.5, leading=22.5, textColor=INK, alignment=TA_LEFT, spaceAfter=2),
 "sub":   ParagraphStyle("s", parent=ss["Normal"], fontName="Helvetica", fontSize=10, leading=13.5, textColor=GRY, spaceAfter=10),
 "h1":    ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=12.5, leading=15.5, textColor=ACC, spaceBefore=13, spaceAfter=5),
 "b":     ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica", fontSize=9.6, leading=13.4, textColor=INK, spaceAfter=6),
 "sm":    ParagraphStyle("sm", parent=ss["Normal"], fontName="Helvetica", fontSize=8.1, leading=10.8, textColor=GRY, spaceAfter=4),
 "c":     ParagraphStyle("c", parent=ss["Normal"], fontName="Helvetica", fontSize=8.3, leading=10.6, textColor=INK),
 "cb":    ParagraphStyle("cb", parent=ss["Normal"], fontName="Helvetica-Bold", fontSize=8.3, leading=10.6, textColor=INK),
}

def tbl(data, w):
    rows = [[Paragraph(str(c), S["cb"] if i == 0 else S["c"]) for c in r] for i, r in enumerate(data)]
    t = Table(rows, colWidths=w, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, LIN), ("BACKGROUND", (0, 0), (-1, 0), BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    return t

def footer(cv, doc):
    cv.saveState(); cv.setFont("Helvetica", 7.5); cv.setFillColor(GRY)
    cv.drawString(18 * mm, 12 * mm, "Marco Amendola · Concentrated-Liquidity Rebalancing Study v3 · July 2026")
    cv.drawRightString(192 * mm, 12 * mm, f"Page {doc.page}"); cv.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=20 * mm,
    title="Rebalancing a Concentrated-Liquidity Position: Policy, Costs, Evidence (v3)", author="Marco Amendola")
E = []
E.append(Paragraph("Rebalancing a Concentrated-Liquidity Position:<br/>Policy, Costs, Evidence", S["title"]))
E.append(Paragraph("Marco Amendola · July 2026 · Two <b>disjoint</b> 90-day regimes of real ETH-USD hourly data · 400 synthetic paths (OU / GBM) · USD- and ETH-denominated baselines · Measured pool fee anchor · Code, validation suite and research log ship with this document", S["sub"]))
E.append(HRFlowable(width="100%", thickness=0.8, color=ACC, spaceAfter=9))

E.append(Paragraph("Scope", S["h1"]))
E.append(Paragraph("This study answers <b>\u201chow should a Uniswap-v3-style LP position be rebalanced?\u201d</b> with measured evidence across two disjoint market regimes and a synthetic mechanism test. It is the decision layer \u2014 whether and how to rebalance, with explicit costs. A production system adds measured position-level fee accrual, tick-level data and broader validation on top; the architecture is built to take them. The theoretical anchor is loss-versus-rebalancing (Milionis, Moallemi, Roughgarden & Zhang, 2022): this work operationalises that cost into a per-policy, per-regime break-even that a desk can act on.", S["b"]))

E.append(Paragraph("Method", S["h1"]))
E.append(Paragraph("Exact v3 position mathematics (no linearised IL approximations), validated by a nine-test suite (value continuity at bounds, out-of-range composition, reduction to the v2 square-root law) and a reproduction gate: before any new run, the engine re-derived every published v2 number from archived inputs (exact) and from re-fetched data (0.00pp deviation on all rows; mode logged per window). Six policies were run over two real 90-day hourly ETH-USD windows \u2014 <b>A: trending</b> (9 Apr\u20138 Jul 2026, net \u221218.5%, \u03c3 55% ann., daily path-efficiency 0.120) and <b>B\u2032: oscillatory</b> (6 Aug\u20133 Nov 2024, net \u22122.3%, \u03c3 56% ann., daily path-efficiency 0.004) \u2014 against both a 50/50 HODL baseline (USD terms) and a 100%-ETH hold (ETH terms). B\u2032 was selected by a pre-registered mechanical scan (end \u2264 8 Apr 2026 for full disjointness from A; |net| \u2264 5%; \u03c3 \u2208 [40, 70]%; minimum daily path-efficiency; top-ranked window taken, no override). An erratum applies to v2: its windows A and B shared 53 of 90 days (\u224859% overlap), overstating evidential independence; B\u2032 repairs it and reproduces v2-B\u2019s conclusions on independent data. Every rebalance is charged 5+5 bps on swapped value plus gas. Fee income is <b>inverted, not assumed</b>: the primary output is the fee APR each policy required to match HODL. <b>Convention:</b> break-even APR is quoted on deposited capital over the full window; time-in-range dilution applies symmetrically to required and realized accrual, and in-range equivalents (BE \u00f7 TIR) are reported for static ranges. Predictions were pre-registered before every run: two of four Run-002 predictions failed and produced the main finding; Run 003 (disjoint window) went 5/5; Run 004 (synthetic) went 4/4 \u2014 all logged.", S["b"]))

E.append(Paragraph("Results \u2014 Window A: trending (ETH \u221218.5%)", S["h1"]))
E.append(tbl([
 ["Policy", "vs HODL (USD)", "vs 100% ETH (ETH terms)", "Rebal.", "Event costs", "Time in range", "Break-even fee APR"],
 ["Full range", "\u22120.47%", "+10.78%", "0", "$0", "100%", "1.9%"],
 ["Static \u00b115%", "\u22126.31%", "+3.62%", "0", "$0", "61%", "25.6%"],
 ["Static \u00b15%", "\u22128.25%", "+1.23%", "0", "$0", "24%", "33.5%"],
 ["Threshold re-center \u00b115%", "\u22128.88%", "+0.47%", "2", "$91", "100%", "36.1%"],
 ["Threshold re-center \u00b15%", "\u221227.45%", "\u221222.32%", "21", "$888", "100%", "111.6%"],
 ["Periodic weekly \u00b110%", "\u221211.54%", "\u22122.81%", "12", "$316", "96%", "46.9%"],
], [36 * mm, 23 * mm, 32 * mm, 13 * mm, 20 * mm, 22 * mm, 26 * mm]))
E.append(Spacer(1, 3))
E.append(Paragraph("Deposit $100,000; values pre-fee-income, net of rebalancing costs. ETH-terms column: position value in ETH at horizon vs holding 100% ETH \u2014 in a drawdown, every no-rebalance LP policy beats holding the asset in its own terms. Denomination is a first-order design choice, not a reporting detail. In-range-equivalent break-evens for the statics (BE \u00f7 TIR): \u00b115% \u2192 42.0%, \u00b15% \u2192 \u2248140%.", S["sm"]))

E.append(Paragraph("Results \u2014 Window B\u2032: oscillatory, disjoint (ETH \u22122.3%, \u03c3 matched)", S["h1"]))
E.append(tbl([
 ["Policy", "vs HODL (USD)", "vs 100% ETH (ETH terms)", "Rebal.", "Event costs", "Time in range", "Break-even fee APR"],
 ["Full range", "\u22120.01%", "+1.19%", "0", "$0", "100%", "0.0%"],
 ["Static \u00b115%", "\u22120.10%", "+1.09%", "0", "$0", "100%", "0.4%"],
 ["Static \u00b15%", "\u22120.29%", "+0.90%", "0", "$0", "67%", "1.2%"],
 ["Threshold re-center \u00b115%", "\u22126.90%", "\u22125.86%", "2", "$98", "100%", "28.3%"],
 ["Threshold re-center \u00b15%", "\u221226.34%", "\u221225.78%", "18", "$811", "100%", "108.0%"],
 ["Periodic weekly \u00b110%", "\u221211.41%", "\u221210.49%", "12", "$294", "91%", "46.8%"],
], [36 * mm, 23 * mm, 32 * mm, 13 * mm, 20 * mm, 22 * mm, 26 * mm]))
E.append(Spacer(1, 3))
E.append(Paragraph("Same conventions as window A. In-range-equivalent break-even for static \u00b15%: 1.2% \u00f7 0.67 \u2248 1.8%. Threshold \u00b15% damage decomposition on B\u2032: $811 explicit costs of a $26,344 shortfall \u2014 3.1% costs, 96.9% crystallised inventory drift \u2014 the same signature as window A. The five largest B\u2032 re-centers each swap \u2248 half the position at the extreme that forced the exit (max event cost $51.75).", S["sm"]))
E.append(Spacer(1, 4))
E.append(Image("final/fig_recenters.png", width=168 * mm, height=110.4 * mm))
E.append(Paragraph("Threshold \u00b15% re-center events over both windows. Upward triangles: re-centers triggered by an exit above the range (the policy buys back in at a local high); downward: exits below (it sells at a local low). The clustering at extremes is the mechanism, visible by eye in both regimes.", S["sm"]))

E.append(PageBreak())
E.append(Paragraph("Synthetic mechanism test \u2014 OU vs GBM (Run 004, pre-registered)", S["h1"]))
E.append(Paragraph("If exit-triggered re-centering at widths inside the oscillation amplitude is structurally short mean-reversion, it must lose on paths of <b>pure</b> mean reversion \u2014 the regime such a policy would most plausibly be defended for \u2014 with no trend to blame. 200 Ornstein\u2013Uhlenbeck paths (log-price, stationary sd 7%, half-life 9.2d, \u03c3 52% ann.) and 200 zero-drift GBM paths (same \u03c3), 2,160 hourly steps each, seed 42, identical costs. These are the study\u2019s first interval estimates.", S["b"]))
E.append(tbl([
 ["Process", "Policy", "Break-even APR, median", "5\u201395th percentile", "Rebalances (median)"],
 ["OU \u2014 pure mean reversion", "Full range", "0.1%", "[0.0%, 1.0%]", "0"],
 ["", "Static \u00b15%", "4.1%", "[0.0%, 23.6%]", "0"],
 ["", "Threshold \u00b15%", "116.5%", "[89.7%, 141.3%]", "24"],
 ["GBM \u2014 zero drift", "Full range", "1.4%", "[0.0%, 9.1%]", "0"],
 ["", "Static \u00b15%", "29.3%", "[1.0%, 77.7%]", "0"],
 ["", "Threshold \u00b15%", "115.9%", "[86.0%, 161.4%]", "24"],
], [42 * mm, 28 * mm, 38 * mm, 36 * mm, 28 * mm]))
E.append(Spacer(1, 3))
E.append(Paragraph("Threshold \u00b15% loses to static \u00b15% in 200 of 200 OU paths (paired). Its 5th-percentile break-even on pure mean reversion is 89.7% \u2014 the policy\u2019s best decile on its friendliest process is still unpayable. Both real windows (111.6%, 108.0%) sit inside the synthetic 5\u201395 bands. The regime-dependent object is the static tight range: median 4.1% on OU vs 29.3% on GBM.", S["sm"]))

E.append(Paragraph("The finding", S["h1"]))
E.append(Paragraph("The v2 pre-registered hypothesis was that exit-triggered re-centering fails in trends and recovers in oscillation. The data rejected it, and v3 upgrades the rejection from observed to structural. Threshold \u00b15% is the worst policy in <b>both</b> disjoint real regimes (break-even 111.6% trending, 108.0% oscillatory; explicit costs 3\u20134% of the damage, crystallised inventory drift 96\u201397%) and in <b>400 of 400</b> synthetic paths including pure mean reversion. Mechanism: when the trigger width sits inside the oscillation amplitude, every exit-triggered re-center buys a local extreme, and the reversion then exits it on the other side \u2014 the policy is structurally short mean-reversion at its own trigger scale, independent of the macro regime. The regime-dependent object is the static tight range: its break-even collapses from 33.5% (trending) to 1.2% (disjoint oscillatory); the order-of-magnitude difference lives in the range decision, not the re-centering decision.", S["b"]))

E.append(Paragraph("Fee adequacy \u2014 measured anchor", S["h1"]))
E.append(Paragraph("Pool-level fee APY (fees \u00f7 TVL) on the Uniswap v3 ETH/USDC 0.05% mainnet pool (0x88e6\u20265440), measured from the DeFiLlama daily series: <b>window A mean 14.9%</b> (median 12.0%, avg TVL $95M); <b>window B\u2032 mean 17.5%</b> (median 16.3%, avg TVL $151M). A Dune query computing the same metric from dex.trades and daily pool balances is published as query 7923963 (execution pending account credits \u2014 stated, not hidden). Against these measurements: threshold \u00b15% break-even requires sustained position-level capture of \u22486.2\u20137.5\u00d7 the pool average for 90 days. The uncrowded theoretical ceiling for a \u00b15% band is 41.5\u00d7 \u2014 but it assumes every competing dollar is full-range; on a major pool where liquidity is predominantly concentrated, realized multipliers compress toward \u22481\u00d7, and a sustained 6\u20137\u00d7 means near-zero competition at the tick for a quarter. Static \u00b15% on B\u2032 requires an in-range-equivalent 1.8% APR \u2248 0.10\u00d7 the measured pool average \u2014 adequacy fails only if pool fee yield collapses by more than \u224890% and stays there for the quarter. Positions whose adequacy depends on stress volume holding up are treated as marginal.", S["b"]))

E.append(Paragraph("Operating rule", S["h1"]))
E.append(Paragraph("(1) Never re-center on range exit at widths inside the measured oscillation amplitude \u2014 in either regime; v3 shows this is structural, not empirical luck. (2) In measured oscillatory regimes, hold a static tight range: fee-dense and nearly free (B\u2032: 1.2% break-even vs 17.5% measured pool APY). (3) In trending regimes, widen, go full-range, or exit \u2014 in asset terms, full-range LP outperformed holding the asset by 10.8% through the drawdown. (4) Re-center on regime change, not on price exit, using the path-efficiency gauge comparatively (A vs B\u2032: 0.120 vs 0.004 on daily returns \u2014 well over an order of magnitude of separation; absolute thresholds require per-frequency, per-window calibration, a finding this study reports rather than hides). (5) An exit-triggered \u201cself-balancing\u201d automation is a systematic executor of the worst trade in this study \u2014 and its trigger levels are publicly predictable on-chain, adding adversarial execution (MEV) as a structural cost of the policy itself, not an implementation detail.", S["b"]))

W1 = [Paragraph("Worst events, read by hand (threshold \u00b15%, window A)", S["h1"]), tbl([
 ["Hour", "Price", "Value before", "Value swapped", "Event cost", "Trigger"],
 ["66", "$2,306", "$101,235", "$50,617", "$53.62", "exit up"],
 ["118", "$2,354", "$98,662", "$49,331", "$52.33", "exit up"],
 ["84", "$2,196", "$97,511", "$48,755", "$51.76", "exit down"],
 ["601", "$2,351", "$96,049", "$48,024", "$51.02", "exit up"],
 ["498", "$2,238", "$94,928", "$47,464", "$50.46", "exit down"],
], [16 * mm, 22 * mm, 30 * mm, 30 * mm, 26 * mm, 24 * mm]), Spacer(1, 3)]
E.append(KeepTogether(W1))
E.append(Paragraph("Each of the five largest re-centers swaps roughly half the position at the price extreme that forced the exit; window B\u2032 shows the identical signature. Aggregates are where analysis starts, not where it ends.", S["sm"]))

W2 = [Paragraph("Stated limitations and production path", S["h1"]), tbl([
 ["This study (decision layer)", "Production extension"],
 ["Fee income inverted (break-even APR); pool-level anchor measured (DeFiLlama; Dune query 7923963 published), position-level accrual not yet measured", "Measured position-level accrual from pool events / subgraph"],
 ["Hourly closes; exits at close; Coinbase price as pool proxy. Bias direction: intra-hour wicks would add triggers and worsen fills for threshold policies \u2014 the study understates their damage (conclusion-conservative)", "Tick-level simulation on pool data; wick-accurate exits"],
 ["Two disjoint real windows, one pair; interval estimates from 400 synthetic paths, not yet from rolling real windows", "Multi-pair, rolling windows, bootstrap confidence intervals"],
 ["Regime gauge used comparatively; thresholds not universal", "Per-frequency, per-window threshold calibration"],
 ["Static costs (5+5 bps, fixed gas); MEV named as structural cost", "Depth-aware slippage; private execution for any re-center"],
], [92 * mm, 80 * mm])]
E.append(KeepTogether(W2))
E.append(Spacer(1, 8))
E.append(HRFlowable(width="100%", thickness=0.6, color=LIN, spaceAfter=5))
E.append(Paragraph("This package ships the engine, the nine-test validation suite, the reproduction gate, all run scripts, archived inputs, full run outputs and the research log \u2014 including the pre-registered predictions that failed and the belief updates they forced, and a v2 erratum. Prior published work: UMA oracle base-rate study (1.17M+ assertions) and related on-chain research under the handle Xpertknight (Dune). Research and decision support; not investment advice; no live trading recommendation.", S["sm"]))

doc.build(E, onFirstPage=footer, onLaterPages=footer)
print("built", OUT)
