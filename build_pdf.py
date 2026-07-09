"""Build the CLRE submission PDF (reportlab platypus)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)

OUT = "/mnt/user-data/outputs/clre/CLRE_v3_Rebalancing_Study_Marco_Amendola.pdf"

INK = colors.HexColor("#1a1a1a")
ACCENT = colors.HexColor("#0e3a5a")
GREY = colors.HexColor("#5a5a5a")
LINE = colors.HexColor("#c9c9c9")
HEADBG = colors.HexColor("#eef2f5")

ss = getSampleStyleSheet()
S = {
    "title": ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold",
                            fontSize=19, leading=23, textColor=INK, alignment=TA_LEFT,
                            spaceAfter=2),
    "subtitle": ParagraphStyle("st", parent=ss["Normal"], fontName="Helvetica",
                               fontSize=10.5, leading=14, textColor=GREY, spaceAfter=10),
    "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold",
                         fontSize=13, leading=16, textColor=ACCENT,
                         spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                         fontSize=11, leading=14, textColor=INK,
                         spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=9.7, leading=13.6, textColor=INK, spaceAfter=6),
    "small": ParagraphStyle("sm", parent=ss["Normal"], fontName="Helvetica",
                            fontSize=8.2, leading=11, textColor=GREY, spaceAfter=4),
    "cell": ParagraphStyle("c", parent=ss["Normal"], fontName="Helvetica",
                           fontSize=8.6, leading=11, textColor=INK),
    "cellb": ParagraphStyle("cb", parent=ss["Normal"], fontName="Helvetica-Bold",
                            fontSize=8.6, leading=11, textColor=INK),
    "quote": ParagraphStyle("q", parent=ss["Normal"], fontName="Helvetica-Oblique",
                            fontSize=10.2, leading=14.5, textColor=ACCENT,
                            leftIndent=8, spaceBefore=4, spaceAfter=8),
}


def tbl(data, widths, header=True, align_right_from=1):
    rows = []
    for i, row in enumerate(data):
        st = S["cellb"] if (header and i == 0) else S["cell"]
        rows.append([Paragraph(str(c), st) for c in row])
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), HEADBG))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(20 * mm, 12 * mm,
                      "Marco Amendola  ·  Concentrated-Liquidity Rebalancing Study  ·  July 2026")
    canvas.drawRightString(190 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=20 * mm, rightMargin=20 * mm,
                        topMargin=18 * mm, bottomMargin=20 * mm,
                        title="Rebalancing a Concentrated-Liquidity Position: Policy, Costs, Evidence",
                        author="Marco Amendola")
E = []

# ---------------- Page 1 ----------------
E.append(Paragraph("Rebalancing a Concentrated-Liquidity Position:<br/>Policy, Costs, Evidence", S["title"]))
E.append(Paragraph("Marco Amendola · July 2026 · Backtest on real ETH-USD hourly data (90 days) · Code and full report available on request", S["subtitle"]))
E.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceAfter=10))

E.append(Paragraph("Scope", S["h1"]))
E.append(Paragraph(
    "This study answers the question <b>\u201chow should a Uniswap-v3-style LP position be rebalanced?\u201d</b> "
    "with measured evidence rather than convention. It is the decision layer \u2014 whether and how to rebalance, "
    "with explicit costs. A production system adds measured fee accrual, tick-level data, and multi-pair "
    "validation on top; the architecture is built to take them.", S["body"]))

E.append(Paragraph("Method", S["h1"]))
E.append(Paragraph(
    "A simulation engine implements exact v3 position mathematics (liquidity, token amounts, and position "
    "value in price space \u2014 no linearised impermanent-loss approximations), validated by nine sanity tests "
    "covering value continuity at range bounds, out-of-range composition, and reduction of the full-range case "
    "to the v2 square-root law. Six policies were run over the same real price path \u2014 2,156 hourly ETH-USD "
    "closes (Coinbase, 9 Apr \u2013 8 Jul 2026, ETH \u221219.8%) \u2014 against a 50/50 HODL baseline. Every "
    "rebalancing event is charged 5 bps pool fee + 5 bps slippage on the swapped value, plus fixed gas.", S["body"]))
E.append(Paragraph(
    "The central design choice: fee income is <b>not assumed \u2014 it is inverted</b>. The primary output is "
    "the organic fee APR each policy would have <i>required</i> to match HODL. This removes the volume "
    "assumption entirely; an assumed-APR scenario table is reported separately and labeled as an upper-bound "
    "model. All outcome predictions were logged before the run, and all six ranked as predicted.", S["body"]))

E.append(Paragraph("Results", S["h1"]))
E.append(tbl([
    ["Policy", "Final value", "vs HODL", "Rebal.", "Event costs", "Time in range", "Break-even fee APR"],
    ["HODL 50/50 (baseline)", "$90,112", "\u2014", "0", "$0", "\u2014", "\u2014"],
    ["Full range (v2-style)", "$89,567", "\u22120.54%", "0", "$0", "100%", "2.2%"],
    ["Static \u00b115%", "$83,127", "\u22126.98%", "0", "$0", "60%", "28.4%"],
    ["Static \u00b15%", "$81,215", "\u22128.90%", "0", "$0", "21%", "36.2%"],
    ["Threshold re-center \u00b115%", "$82,163", "\u22127.95%", "2", "$91", "100%", "32.3%"],
    ["Threshold re-center \u00b15%", "$62,195", "\u221227.92%", "21", "$888", "100%", "113.5%"],
    ["Periodic weekly re-center \u00b110%", "$79,257", "\u221210.86%", "12", "$291", "97%", "44.1%"],
], [46*mm, 21*mm, 18*mm, 13*mm, 19*mm, 21*mm, 25*mm]))
E.append(Spacer(1, 4))
E.append(Paragraph("Deposit $100,000. Values are pre-fee-income, net of rebalancing costs. "
                   "Break-even fee APR = organic fee income on deposited capital required to match HODL over the window, annualised.", S["small"]))

E.append(Paragraph("The finding that matters", S["h1"]))
E.append(Paragraph(
    "The tight self-rebalancing policy (threshold \u00b15%) lost $27,917 versus HODL across 21 re-centers. "
    "Explicit costs \u2014 swap fees, slippage, gas \u2014 account for <b>$888 of that: 3%</b>. The remaining "
    "<b>97% is inventory drift crystallised by the policy itself</b>: every re-center after a range exit is, "
    "by construction, a sell-low/buy-high trade. Automation does not remove this cost \u2014 it schedules it. "
    "A \u201cself-balancing\u201d position is a systematic executor of exactly the trades whose expected cost "
    "this study measures.", S["body"]))

E.append(PageBreak())

# ---------------- Page 2 ----------------
E.append(Paragraph("Reading the worst events by hand", S["h1"]))
E.append(Paragraph(
    "Aggregates are the start of the analysis, not the end. The five largest rebalances of the \u00b15% "
    "threshold policy were inspected individually: each swaps roughly half the position value at exactly "
    "the price extreme that forced the exit.", S["body"]))
E.append(tbl([
    ["Hour", "Price", "Value before", "Value swapped", "Event cost", "Trigger"],
    ["53", "$2,306", "$101,235", "$50,617", "$53.62", "exit up"],
    ["105", "$2,354", "$98,662", "$49,331", "$52.33", "exit up"],
    ["71", "$2,196", "$97,511", "$48,755", "$51.76", "exit down"],
    ["588", "$2,351", "$96,049", "$48,024", "$51.02", "exit up"],
    ["485", "$2,238", "$94,928", "$47,464", "$50.46", "exit down"],
], [16*mm, 22*mm, 30*mm, 30*mm, 26*mm, 26*mm]))
E.append(Spacer(1, 6))

E.append(Paragraph("Regime diagnostics", S["h1"]))
E.append(Paragraph(
    "Realised volatility over the window: 27.1% (55% annualised). Path efficiency was measured with a "
    "bounded path-quality score (net displacement over total path length, Kaufman\u2019s Efficiency Ratio "
    "form), decomposed for concentrated positions into in-range and out-of-range sub-periods \u2014 the "
    "in-range figure describes path quality while the position earns; the out-of-range figure describes "
    "uncompensated inventory drift while it does not. A calibration finding from this run is reported "
    "honestly rather than hidden: efficiency thresholds calibrated on daily returns read systematically "
    "lower on hourly data (the finer the sampling, the longer the measured path), so regime labels must be "
    "recalibrated per sampling frequency. This is logged as a framework revision item.", S["body"]))

E.append(Paragraph("Compensation adequacy", S["h1"]))
E.append(Paragraph(
    "Under a mid-range 15% pool fee APR scenario, the static \u00b15% position\u2019s fee-to-volatility ratio "
    "reads 1.19 \u2014 nominally adequate \u2014 but falls to 0.95 after a 20% stress volume-compression "
    "haircut (a stated model assumption calibrated from historical stress windows, in which fee volume "
    "disappoints precisely when volatility expands). Positions whose adequacy depends on stress volume "
    "holding up should be treated as marginal, not adequate.", S["body"]))

E.append(Paragraph("Operating conclusion", S["h1"]))
E.append(Paragraph(
    "In directional regimes, the rebalancing <b>policy</b> dominates the range <b>width</b> as the risk "
    "decision. The defensible design is regime-gated: default to wide or full range; tighten only when "
    "path-efficiency and compensation diagnostics jointly support it; and treat every re-center as a trade "
    "that must justify its expected drift cost \u2014 not as hygiene. Tight ranges with automatic re-centering "
    "should be reserved for regimes with measured oscillatory structure and fee intensity above the "
    "break-even threshold this engine computes per window.", S["body"]))

E.append(Paragraph("Stated limitations and production path", S["h1"]))
E.append(tbl([
    ["This study (decision layer)", "Production extension"],
    ["Fee income inverted (break-even APR); assumed-APR table labeled as upper bound",
     "Measured position-level fee accrual from pool events / subgraph"],
    ["Hourly closes; range entry/exit at close", "Tick-level simulation of range crossings"],
    ["Single pair, single 90-day window", "Multi-pair, multi-window, out-of-sample validation"],
    ["Regime gating specified as design conclusion", "Regime-switching policy backtest"],
    ["Static cost assumptions (5+5 bps, fixed gas)", "Venue-specific execution and MEV-aware rebalancing"],
], [82*mm, 82*mm]))
E.append(Spacer(1, 8))
E.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceBefore=4, spaceAfter=6))
E.append(Paragraph(
    "Engine, nine-test validation suite, run script, full run report and research log (with pre-registered "
    "predictions) are available as a code package on request. Prior published work: UMA oracle base-rate "
    "study (1.17M+ assertions) and related on-chain research under the handle Xpertknight (Dune).", S["small"]))
E.append(Paragraph(
    "This document is research and decision support. It is not investment advice and contains no live "
    "trading recommendation.", S["small"]))

doc.build(E, onFirstPage=footer, onLaterPages=footer)
print("built", OUT)
