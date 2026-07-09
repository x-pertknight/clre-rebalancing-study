"""Scan daily ETH-USD history for a 90d window with oscillatory structure
(low daily PQS, small net displacement) to serve as Run 002 regime B."""
import requests, datetime as dt, math, time
from clre import pqs, log_returns

def fetch_daily(days=420):
    end = dt.datetime.now(dt.timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0)
    start = end - dt.timedelta(days=days)
    out={}
    cur=start
    while cur<end:
        ce=min(cur+dt.timedelta(days=290), end)
        r=requests.get("https://api.exchange.coinbase.com/products/ETH-USD/candles",
            params={"granularity":86400,"start":cur.isoformat(),"end":ce.isoformat()},timeout=15)
        r.raise_for_status()
        for ts,l,h,o,c,v in r.json(): out[int(ts)]=float(c)
        cur=ce; time.sleep(0.15)
    ks=sorted(out); return ks,[out[k] for k in ks]

ts, px = fetch_daily()
print("daily candles:", len(px), dt.datetime.fromtimestamp(ts[0],dt.timezone.utc).date(),
      "->", dt.datetime.fromtimestamp(ts[-1],dt.timezone.utc).date())
W=90
best=[]
for i in range(0, len(px)-W):
    win=px[i:i+W]
    r=log_returns(win)
    q=pqs(r)
    net=win[-1]/win[0]-1
    best.append((q, abs(net), i, net))
best.sort()
for q,an,i,net in best[:8]:
    d0=dt.datetime.fromtimestamp(ts[i],dt.timezone.utc).date()
    d1=dt.datetime.fromtimestamp(ts[i+W-1],dt.timezone.utc).date()
    print(f"dailyPQS={q:.3f} net={net*100:+.1f}%  {d0} -> {d1}")
