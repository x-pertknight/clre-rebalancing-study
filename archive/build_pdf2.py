"""CLRE submission PDF v2 — two regimes, dual denomination, post-adversarial."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)

OUT = "/mnt/user-data/outputs/clre/CLRE_v3_Rebalancing_Study_v2_Marco_Amendola.pdf"
INK=colors.HexColor("#1a1a1a"); ACC=colors.HexColor("#0e3a5a")
GRY=colors.HexColor("#5a5a5a"); LIN=colors.HexColor("#c9c9c9"); BG=colors.HexColor("#eef2f5")
ss=getSampleStyleSheet()
S={
 "title":ParagraphStyle("t",parent=ss["Title"],fontName="Helvetica-Bold",fontSize=18.5,leading=22.5,textColor=INK,alignment=TA_LEFT,spaceAfter=2),
 "sub":ParagraphStyle("s",parent=ss["Normal"],fontName="Helvetica",fontSize=10,leading=13.5,textColor=GRY,spaceAfter=10),
 "h1":ParagraphStyle("h1",parent=ss["Heading1"],fontName="Helvetica-Bold",fontSize=12.5,leading=15.5,textColor=ACC,spaceBefore=13,spaceAfter=5),
 "b":ParagraphStyle("b",parent=ss["Normal"],fontName="Helvetica",fontSize=9.6,leading=13.4,textColor=INK,spaceAfter=6),
 "sm":ParagraphStyle("sm",parent=ss["Normal"],fontName="Helvetica",fontSize=8.1,leading=10.8,textColor=GRY,spaceAfter=4),
 "c":ParagraphStyle("c",parent=ss["Normal"],fontName="Helvetica",fontSize=8.3,leading=10.6,textColor=INK),
 "cb":ParagraphStyle("cb",parent=ss["Normal"],fontName="Helvetica-Bold",fontSize=8.3,leading=10.6,textColor=INK),
}
def tbl(data,w):
    rows=[[Paragraph(str(c),S["cb"] if i==0 else S["c"]) for c in r] for i,r in enumerate(data)]
    t=Table(rows,colWidths=w,repeatRows=1)
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.4,LIN),("BACKGROUND",(0,0),(-1,0),BG),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]))
    return t
def footer(cv,doc):
    cv.saveState(); cv.setFont("Helvetica",7.5); cv.setFillColor(GRY)
    cv.drawString(18*mm,12*mm,"Marco Amendola · Concentrated-Liquidity Rebalancing Study v2 · July 2026")
    cv.drawRightString(192*mm,12*mm,f"Page {doc.page}"); cv.restoreState()

doc=SimpleDocTemplate(OUT,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=20*mm,
    title="Rebalancing a Concentrated-Liquidity Position: Policy, Costs, Evidence (v2)",author="Marco Amendola")
E=[]
E.append(Paragraph("Rebalancing a Concentrated-Liquidity Position:<br/>Policy, Costs, Evidence", S["title"]))
E.append(Paragraph("Marco Amendola · July 2026 · Two 90-day regimes of real ETH-USD hourly data · USD- and ETH-denominated baselines · Code, validation suite and research log available on request", S["sub"]))
E.append(HRFlowable(width="100%",thickness=0.8,color=ACC,spaceAfter=9))

E.append(Paragraph("Scope", S["h1"]))
E.append(Paragraph("This study answers <b>\u201chow should a Uniswap-v3-style LP position be rebalanced?\u201d</b> with measured evidence across two opposite market regimes. It is the decision layer \u2014 whether and how to rebalance, with explicit costs. A production system adds measured fee accrual, tick-level data and broader validation on top; the architecture is built to take them. The theoretical anchor is loss-versus-rebalancing (Milionis, Moallemi, Roughgarden & Zhang, 2022): this work operationalises that cost into a per-policy, per-regime break-even that a desk can act on.", S["b"]))

E.append(Paragraph("Method", S["h1"]))
E.append(Paragraph("Exact v3 position mathematics (no linearised IL approximations), validated by a nine-test suite (value continuity at bounds, out-of-range composition, reduction to the v2 square-root law). Six policies were run over two real 90-day hourly ETH-USD windows selected to be regime opposites \u2014 <b>A: trending</b> (9 Apr\u20138 Jul 2026, net \u221218.5%, \u03c3 55% ann.) and <b>B: oscillatory</b> (2 Mar\u201331 May 2026, net +3.2%, \u03c3 52% ann., selected by daily path-efficiency scan) \u2014 against both a 50/50 HODL baseline (USD terms) and a 100%-ETH hold (ETH terms). Every rebalance is charged 5+5 bps on swapped value plus gas. Fee income is <b>inverted, not assumed</b>: the primary output is the organic fee APR each policy required to match HODL. Outcome predictions were logged before each run; two of four Run-002 predictions failed, and the failures \u2014 documented in the research log \u2014 are what produced the study\u2019s main finding.", S["b"]))

E.append(Paragraph("Results \u2014 Window A: trending (ETH \u221218.5%)", S["h1"]))
E.append(tbl([
 ["Policy","vs HODL (USD)","vs 100% ETH (ETH terms)","Rebal.","Event costs","Time in range","Break-even fee APR"],
 ["Full range","\u22120.47%","+10.78%","0","$0","100%","1.9%"],
 ["Static \u00b115%","\u22126.31%","+3.62%","0","$0","61%","25.6%"],
 ["Static \u00b15%","\u22128.25%","+1.23%","0","$0","24%","33.5%"],
 ["Threshold re-center \u00b115%","\u22128.88%","+0.47%","2","$91","100%","36.1%"],
 ["Threshold re-center \u00b15%","\u221227.45%","\u221222.32%","21","$888","100%","111.6%"],
 ["Periodic weekly \u00b110%","\u221211.54%","\u22122.81%","12","$316","96%","46.9%"],
],[36*mm,23*mm,32*mm,13*mm,20*mm,22*mm,26*mm]))
E.append(Spacer(1,3))
E.append(Paragraph("Deposit $100,000; values pre-fee-income, net of rebalancing costs. ETH-terms column: position value in ETH at horizon vs holding 100% ETH \u2014 in a drawdown, every no-rebalance LP policy beats holding the asset in its own terms. Denomination is a first-order design choice, not a reporting detail.", S["sm"]))

E.append(Paragraph("Results \u2014 Window B: oscillatory (ETH +3.2%, same volatility)", S["h1"]))
E.append(tbl([
 ["Policy","vs HODL (USD)","Rebal.","Event costs","Time in range","Break-even fee APR"],
 ["Full range","\u22120.01%","0","$0","100%","0.1%"],
 ["Static \u00b115%","\u22120.19%","0","$0","63%","0.8%"],
 ["Static \u00b15%","\u22120.53%","0","$0","21%","2.1%"],
 ["Threshold re-center \u00b115%","\u22125.79%","1","$55","100%","23.5%"],
 ["Threshold re-center \u00b15%","\u221230.87%","24","$1,116","100%","125.5%"],
 ["Periodic weekly \u00b110%","\u22129.41%","12","$296","99%","38.2%"],
],[44*mm,26*mm,15*mm,22*mm,26*mm,28*mm]))
E.append(Spacer(1,3))
E.append(Paragraph("For scale: sustained position-level organic accrual on major 5-bps pools rarely exceeds a few tens of percent APR. Break-evens of 2\u20133% are trivially reachable; break-evens above 100% are unreachable.", S["sm"]))

E.append(PageBreak())
E.append(Paragraph("The finding", S["h1"]))
E.append(Paragraph("The pre-registered hypothesis was that exit-triggered re-centering fails in trends and recovers in oscillation. <b>The data rejected it.</b> Threshold \u00b15% was the worst policy in BOTH regimes (break-even 111.6% trending, 125.5% oscillatory; explicit costs 3\u20134% of the damage, crystallised inventory drift 96\u201397%). Mechanism: when the trigger width sits inside the oscillation amplitude, every exit-triggered re-center buys a local extreme, and the reversion then exits it on the other side \u2014 the policy is structurally short mean-reversion at its own trigger scale, independent of the macro regime. The regime-dependent object is the <b>static</b> tight range: its break-even collapses from 33.5% (trending) to 2.1% (oscillatory) \u2014 the order-of-magnitude difference lives in the range decision, not the re-centering decision.", S["b"]))

E.append(Paragraph("Operating rule", S["h1"]))
E.append(Paragraph("(1) Never re-center on range exit at widths inside the measured oscillation amplitude \u2014 in either regime. (2) In measured oscillatory regimes, hold a static tight range: fee-dense and nearly free. (3) In trending regimes, widen, go full-range, or exit \u2014 in asset terms, full-range LP outperformed holding the asset by 10.8% through the drawdown. (4) Re-center on <i>regime change</i>, not on price exit, using the path-efficiency gauge comparatively (window A vs B: 0.120 vs 0.001 on daily returns \u2014 two orders of magnitude of separation; absolute thresholds require per-frequency, per-window calibration, a finding this study reports rather than hides). (5) An exit-triggered \u201cself-balancing\u201d automation is a systematic executor of the worst trade in this study \u2014 and its trigger levels are publicly predictable on-chain, adding adversarial execution (MEV) as a structural cost of the policy itself, not an implementation detail.", S["b"]))

E.append(Paragraph("Worst events, read by hand (threshold \u00b15%, window A)", S["h1"]))
E.append(tbl([
 ["Hour","Price","Value before","Value swapped","Event cost","Trigger"],
 ["53","$2,306","$101,235","$50,617","$53.62","exit up"],
 ["105","$2,354","$98,662","$49,331","$52.33","exit up"],
 ["71","$2,196","$97,511","$48,755","$51.76","exit down"],
 ["588","$2,351","$96,049","$48,024","$51.02","exit up"],
 ["485","$2,238","$94,928","$47,464","$50.46","exit down"],
],[15*mm,22*mm,30*mm,30*mm,25*mm,25*mm]))
E.append(Spacer(1,2))
E.append(Paragraph("Each of the five largest re-centers swaps roughly half the position at the price extreme that forced the exit. Aggregates are where analysis starts, not where it ends.", S["sm"]))

E.append(Paragraph("Compensation adequacy", S["h1"]))
E.append(Paragraph("Fee-to-volatility adequacy is reported with a stress adjustment: under a mid-range accrual scenario the static \u00b15% ratio reads nominally adequate but falls below adequacy after a 20% volume-compression haircut (a stated model assumption calibrated on historical stress windows, where fee volume disappoints exactly when volatility expands). Positions whose adequacy depends on stress volume holding up are treated as marginal.", S["b"]))

E.append(Paragraph("Stated limitations and production path", S["h1"]))
E.append(tbl([
 ["This study (decision layer)","Production extension"],
 ["Fee income inverted (break-even APR); no accrual assumed","Measured position-level accrual from pool events / subgraph"],
 ["Hourly closes; exits at close; Coinbase price as pool proxy","Tick-level simulation on pool data; wick-accurate exits"],
 ["Two regimes, one pair; single path per regime, no interval estimates","Multi-pair, rolling windows, bootstrap confidence intervals"],
 ["Regime gauge used comparatively; thresholds not universal","Per-frequency, per-window threshold calibration"],
 ["Static costs (5+5 bps, fixed gas); MEV named as structural cost","Depth-aware slippage; private execution for any re-center"],
],[80*mm,80*mm]))
E.append(Spacer(1,7))
E.append(HRFlowable(width="100%",thickness=0.5,color=LIN,spaceBefore=3,spaceAfter=5))
E.append(Paragraph("Engine, nine-test validation suite, both run scripts, full reports and the research log \u2014 including the pre-registered predictions that failed and the belief updates they forced \u2014 are available as a code package on request. Prior published work: UMA oracle base-rate study (1.17M+ assertions) and related on-chain research under the handle Xpertknight (Dune).", S["sm"]))
E.append(Paragraph("Research and decision support; not investment advice; no live trading recommendation.", S["sm"]))
doc.build(E,onFirstPage=footer,onLaterPages=footer)
print("built",OUT)
