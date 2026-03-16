import streamlit as st
import plotly.graph_objects as go
from vomma_engine import VommaEngine
from datetime import datetime

st.set_page_config(page_title="Alpha Volatility Cockpit", layout="wide", page_icon="📡", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
:root{--bg:#f4f5f7;--card:#fff;--border:#dfe1e6;--blt:#ebecf0;--tx:#172b4d;--tx2:#6b778c;--mt:#97a0af;--ac:#0052cc;--gn:#00875a;--gnb:#e3fcef;--gbd:#abf5d1;--rd:#de350b;--rdb:#ffebe6;--rbd:#ffbdad;--am:#ff991f;--amb:#fffae6;--abd:#ffe380}
*{font-family:'DM Sans',system-ui,sans-serif}
[data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] *{font-family:'DM Sans',system-ui,sans-serif!important}
.stApp{background:var(--bg)!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.2rem;max-width:95%;padding-left:2rem;padding-right:2rem}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 16px}
[data-testid="stMetricLabel"]{color:var(--mt)!important;font-size:.75em!important;text-transform:uppercase;letter-spacing:.5px}
[data-testid="stMetricValue"]{color:var(--tx)!important;font-family:'JetBrains Mono',monospace!important}
.sec{font-size:.72em;font-weight:600;color:var(--mt);text-transform:uppercase;letter-spacing:.7px;margin:20px 0 14px;padding-bottom:10px;border-bottom:1px solid var(--blt)}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;margin-bottom:14px;overflow:hidden}
.cbody{padding:20px}
.badges{display:flex;gap:10px}
.bdg{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 16px;text-align:center;min-width:95px}
.bdg-l{font-size:.65em;color:var(--mt);text-transform:uppercase;letter-spacing:.7px;font-weight:600}
.bdg-v{font-size:1.25em;font-weight:700;margin-top:2px;font-family:'JetBrains Mono',monospace}
.bdg-s{font-size:.7em;margin-top:1px}
.vbar{padding:18px 22px;border-bottom:1px solid var(--blt)}
.vgrid{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--blt)}
.vcell{padding:14px 22px;text-align:center}
.vcl{font-size:.65em;color:var(--mt);text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.vcv{font-size:1.05em;font-weight:700;margin-top:3px}
.vsec{padding:16px 22px;border-bottom:1px solid var(--blt)}
.vsec:last-child{border-bottom:none}
.alert{border-radius:8px;padding:10px 14px;margin-top:7px}
.al-a{background:var(--amb);border:1px solid var(--abd)}
.al-a .at{color:#974f0c;font-weight:600;font-size:.82em}
.al-a .ab{color:#7a5b1e;font-size:.78em;margin-top:2px}
.al-r{background:var(--rdb);border:1px solid var(--rbd)}
.al-r .at{color:#bf2600;font-weight:600;font-size:.82em}
.al-r .ab{color:#8c2a0a;font-size:.78em;margin-top:2px}
.gauge{display:flex;height:20px;border-radius:6px;overflow:hidden;margin:6px 0;font-size:.68em;font-weight:600}
.gauge>div{flex:1;display:flex;align-items:center;justify-content:center;color:#fff}
.gn{background:var(--rd)}.gt{background:var(--am)}.gnr{background:var(--ac)}.grc{background:var(--gn)}
.etrack{background:var(--blt);border-radius:8px;height:28px;position:relative;overflow:hidden;margin:8px 0}
.efill{height:100%;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.82em;color:#fff}
.sig{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--blt)}
.sig:last-child{border-bottom:none}
.sn{font-weight:600;color:var(--tx);font-size:.88em}
.sm{color:var(--mt);font-size:.78em;margin-top:2px}
.pill{display:inline-block;padding:2px 10px;border-radius:12px;font-size:.75em;font-weight:600}
.pg{background:var(--gnb);color:var(--gn);border:1px solid var(--gbd)}
.pr{background:var(--rdb);color:var(--rd);border:1px solid var(--rbd)}
.vtbl{width:100%;border-collapse:collapse}
.vtbl th{text-align:left;padding:8px 18px;color:var(--mt);font-size:.7em;text-transform:uppercase;letter-spacing:.5px;font-weight:600;border-bottom:2px solid var(--border)}
.vtbl td{padding:10px 18px;border-bottom:1px solid var(--blt);color:var(--tx);font-size:.88em}
.vtbl tr:hover td{background:#f8f9fa}
.vtbl .act td{background:var(--gnb);font-weight:600;border-left:3px solid var(--gn)}
.mono{font-family:'JetBrains Mono',monospace;font-size:.88em}
.sc{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:8px}
.mgmt{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;height:100%}
.mgmt h4{color:var(--ac);font-size:.9em;margin:0 0 10px;padding-bottom:8px;border-bottom:1px solid var(--blt)}
.ml{color:var(--tx2);font-size:.82em;margin:5px 0;line-height:1.5}
.mv{color:var(--tx);font-weight:600}
.ftr{text-align:center;color:var(--mt);font-size:.75em;margin-top:36px;padding:18px 0;border-top:1px solid var(--border)}
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    return VommaEngine.fetch_all_data()

try:
    data = load_data()
    edge_score, signals, alerts = VommaEngine.calculate_edge(data)
    vrp, vrp_state, vrp_color, vrp_pct = VommaEngine.calculate_vrp(data)
    regime = "CONTANGO" if data.vix < data.vix3m else "BACKWARDATION"
    regime_tag = "NORMAL (VIX < VIX3M)" if regime == "CONTANGO" else "INVERTED (VIX > VIX3M)"
    vrc = "#ff991f" if 30 <= data.vix_rank <= 60 else ("#de350b" if data.vix_rank > 60 else "#00875a")
    ec = "#00875a" if edge_score >= 70 else ("#ff991f" if edge_score >= 40 else "#de350b")
    el = "Favorable" if edge_score >= 70 else ("Caution" if edge_score >= 40 else "Defensive")
    rc = "#00875a" if regime == "CONTANGO" else "#de350b"
except Exception as e:
    st.error(f"Engine error: {str(e)}")
    st.stop()

# HEADER
h1, h2 = st.columns([3, 2])
with h1:
    now = datetime.now().strftime("%A, %B %d, %Y  %I:%M %p")
    st.markdown(f'<div style="font-size:1.4em;font-weight:700;color:#172b4d;letter-spacing:-.3px">Volatility Cockpit</div><div style="color:#6b778c;font-size:.82em">{now}</div>', unsafe_allow_html=True)
with h2:
    st.markdown(f'<div class="badges" style="justify-content:flex-end"><div class="bdg"><div class="bdg-l">Edge</div><div class="bdg-v" style="color:{ec}">{edge_score}</div><div class="bdg-s" style="color:{ec}">{el}</div></div><div class="bdg"><div class="bdg-l">VIX Rank</div><div class="bdg-v" style="color:{vrc}">{data.vix_rank:.0f}%</div><div class="bdg-s" style="color:#97a0af">{"Low" if data.vix_rank<30 else ("Mid" if data.vix_rank<=60 else "High")}</div></div><div class="bdg"><div class="bdg-l">Vol Curve</div><div class="bdg-v" style="font-size:.85em;color:{rc};margin-top:4px">{regime_tag}</div></div></div>', unsafe_allow_html=True)

st.markdown('<hr style="margin:8px 0 18px;border-color:#dfe1e6">', unsafe_allow_html=True)

# TRADE TODAY
st.markdown('<div class="sec">Trade Today?</div>', unsafe_allow_html=True)

with st.expander("Verdict logic and thresholds"):
    st.markdown("""
- **Favorable** — Normal vol curve (VIX < VIX3M) + Edge >= 70 + VRP > 0. Full size, sell premium.
- **Caution** — Mixed signals. Reduce size, prefer defined risk.
- **Defensive** — Toxic Mix active or Edge < 40. No new short-vol, preserve capital.

Active alerts show specific actions from crossover signals and VRP state.
    """)

if regime == "CONTANGO" and edge_score >= 70 and vrp > 0:
    vt, vd, vb, vc = "FAVORABLE", "Conditions support selling premium", "#e3fcef", "#006644"
    stxt = "Sell 16\u0394 strangles at 45 DTE. Use 35% BP. Theta target: 0.1\u20130.3% NLV/day."
elif edge_score < 40 or signals.get('Toxic Mix (15 pts)', {}).get('status') == 'Red':
    vt, vd, vb, vc = "DEFENSIVE", "Toxic Mix active or Edge < 40. Preserve capital.", "#ffebe6", "#bf2600"
    stxt = "No new short-vol, preserve capital."
else:
    vt, vd, vb, vc = "CAUTION", "Mixed signals. Reduce size, be selective.", "#fffae6", "#974f0c"
    stxt = "Smaller size, prefer defined risk (spreads). Take profits at 50%. Manage at 21 DTE."

vi = {"FAVORABLE": "\U0001f7e2", "CAUTION": "\U0001f7e1", "DEFENSIVE": "\U0001f534"}.get(vt, "")

ah = ""
for a in alerts:
    p = a.split(':', 1)
    t = p[0]
    m = p[1].strip() if len(p) > 1 else ""
    sv = any(w in t for w in ["Toxic", "Structural", "Negative"])
    ah += f'<div class="alert {"al-r" if sv else "al-a"}"><div class="at">{t}</div><div class="ab">{m}</div></div>'
if not alerts:
    ah = '<div style="color:#97a0af;font-size:.82em;margin-top:6px">No active alerts.</div>'

st.markdown(f'<div class="card"><div class="vbar" style="background:{vb}"><div style="font-size:1.15em;font-weight:700;color:{vc}">{vi} {vt}</div><div style="color:#6b778c;font-size:.88em">{vd}</div></div><div class="vgrid"><div class="vcell"><div class="vcl">Vol Curve</div><div class="vcv" style="color:{rc}">{"Normal" if regime=="CONTANGO" else "Inverted"}</div></div><div class="vcell"><div class="vcl">Edge Score</div><div class="vcv" style="color:{ec}">{edge_score}</div></div><div class="vcell"><div class="vcl">VRP</div><div class="vcv" style="color:{vrp_color}">{vrp:+.1f}</div></div><div class="vcell"><div class="vcl">VIX Rank</div><div class="vcv" style="color:{vrc}">{data.vix_rank:.0f}%</div></div></div><div class="vsec"><div class="vcl" style="margin-bottom:4px">Strategy</div><div style="font-size:.88em;color:#172b4d">{stxt}</div></div><div class="vsec"><div class="vcl">Active Alerts</div>{ah}</div></div>', unsafe_allow_html=True)

st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

# VRP & EDGE
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="sec">Volatility Risk Premium (VRP)</div>', unsafe_allow_html=True)

    with st.expander("What is VRP?"):
        st.markdown("""
**VRP = VIX - Realized Vol (20d SPX).** The structural edge behind premium selling.

Implied Volatility exceeded Realized Volatility ~83-88% of the time for S&P 500 (1990-2023). This is the insurance premium the market systematically overpays for protection. Premium sellers harvest this structural edge.

**Thresholds:** > 5 pts = premium rich, 2-5 = normal, < 2 = thin (warning), < 0 = negative (structural edge absent).
        """)

    mx = max(data.vix, data.spx_rv_20d, 1)
    vw = data.vix / mx * 100
    rw = data.spx_rv_20d / mx * 100
    st.markdown(f'<div class="card cbody"><div style="display:flex;justify-content:space-between;font-size:.82em;margin-bottom:3px"><span style="color:#6b778c">Implied (VIX)</span><span class="mono" style="font-weight:600;color:#172b4d">{data.vix:.1f}</span></div><div style="background:#ebecf0;height:6px;border-radius:4px;margin-bottom:14px"><div style="background:#172b4d;width:{vw:.0f}%;height:100%;border-radius:4px"></div></div><div style="display:flex;justify-content:space-between;font-size:.82em;margin-bottom:3px"><span style="color:#6b778c">Realized (20d SPX)</span><span class="mono" style="font-weight:600;color:#172b4d">{data.spx_rv_20d:.1f}</span></div><div style="background:#ebecf0;height:6px;border-radius:4px;margin-bottom:18px"><div style="background:#97a0af;width:{rw:.0f}%;height:100%;border-radius:4px"></div></div><div style="border-top:1px solid #ebecf0;padding-top:14px;display:flex;align-items:baseline;gap:10px"><span style="font-size:.82em;color:#6b778c">VRP</span><span class="mono" style="font-size:1.6em;font-weight:700;color:{vrp_color}">{vrp:+.1f}</span><span style="font-size:.82em;font-weight:700;color:{vrp_color}">{vrp_state}</span></div><div class="gauge"><div class="gn">Negative</div><div class="gt">Thin</div><div class="gnr">Normal</div><div class="grc">Rich</div></div></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="sec">The Edge \u2014 Ratios & Crossovers</div>', unsafe_allow_html=True)

    with st.expander("Edge Score methodology"):
        st.markdown("""
**5 signals composed into the Edge Score (0-100).**

Each signal is a binary comparison: green = safe to trade, red = warning.

| Signal | Weight | Threshold |
|--------|--------|-----------|
| VVIX/VIX Ratio | 25 pts | <5 safe, 5-6 neutral, >6 regime risk |
| Slow Crossover | 25 pts | VIX < VIX3M = safe |
| Fast Crossover | 20 pts | VIX9D < VIX = safe |
| Toxic Mix | 15 pts | VIX < 16 AND SKEW > 130 = danger |
| VVIX Divergence | 15 pts | VVIX rising while VIX calm = hidden fear |

**Scoring:** >= 70 Favorable, 40-69 Caution, < 40 Defensive.
        """)

    st.markdown(f'<div class="etrack"><div class="efill" style="width:{edge_score}%;background:{ec}">{edge_score}/100</div></div>', unsafe_allow_html=True)

    sh = '<div class="card cbody" style="padding:16px 20px">'
    for k, v in signals.items():
        pc = "pg" if v['status'] == 'Green' else "pr"
        pt = "Safe" if v['status'] == 'Green' else "Warning"
        sh += f'<div class="sig"><div><div class="sn">{k}</div><div class="sm">{v["msg"]}</div></div><div style="display:flex;align-items:center;gap:8px"><span class="pill {pc}">{pt}</span></div></div>'
    sh += '</div>'
    st.markdown(sh, unsafe_allow_html=True)

# VOL COMPLEX
st.markdown('<div class="sec" style="margin-top:18px">Volatility Complex</div>', unsafe_allow_html=True)

with st.expander("Index descriptions and sparkline logic"):
    st.markdown("""
- **VIX** — 30-day implied vol of S&P 500. The main fear gauge.
- **VVIX** — Volatility of VIX options. Uncertainty about future VIX levels.
- **VIX9D** — 9-day implied vol. Reacts fastest to sudden events.
- **VIX3M** — 3-month implied vol. Structural trend indicator.
- **VIX6M** — 6-month implied vol. Long-term market expectations.
- **SKEW** — Tail risk asymmetry. High SKEW = market pricing crash risk.
- **P/C Ratio** — CBOE equity put/call ratio. >1.0 = fear (puts dominate), <0.7 = complacency.

**Sparkline color:** red = vol rising (risk increasing), green = vol falling (favorable).
    """)

ct = [("^VIX","VIX"),("^VVIX","VVIX"),("^VIX9D","VIX9D"),("^VIX3M","VIX3M"),("^VIX6M","VIX6M"),("^SKEW","SKEW"),("^CPC","P/C Ratio")]
cols = st.columns(4)
for i, (tk, nm) in enumerate(ct):
    if tk in data.history and len(data.history[tk]) > 1:
        h = data.history[tk]
        c = h[-1]
        pr = h[-2]
        if c == pr and len(h) > 2:
            for back in range(len(h)-3, -1, -1):
                if h[back] != c:
                    pr = h[back]
                    break
        ch = c - pr
        pc = (ch/pr)*100 if pr != 0 else 0
        cc = "#de350b" if ch > 0 else "#00875a"
        s = "+" if ch >= 0 else ""
        mn, mxx = min(h), max(h)
        d = mxx - mn if mxx != mn else 1
        pts = " ".join([f"{j*(100/(len(h)-1)):.1f},{28-((v-mn)/d)*28:.1f}" for j,v in enumerate(h)])
        cols[i%4].markdown(f'<div class="sc"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><span style="font-size:.82em;font-weight:700;color:#172b4d">{nm}</span><span class="mono" style="font-weight:700;color:#172b4d">{c:.2f}</span></div><svg viewBox="-1 -1 102 30" width="100%" height="24" preserveAspectRatio="none"><polyline points="{pts}" fill="none" stroke="{cc}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><div style="font-size:.75em;font-weight:600;text-align:right;margin-top:4px;color:{cc}">{s}{ch:.2f} ({s}{pc:.1f}%)</div></div>', unsafe_allow_html=True)

# VOL CURVE
st.markdown('<div class="sec" style="margin-top:18px">Implied Vol Curve (CBOE Indices)</div>', unsafe_allow_html=True)

with st.expander("How to read the vol curve"):
    st.markdown("""
This chart plots CBOE implied volatility indices: VIX (30-day) -> VIX3M (3-month) -> VIX6M (6-month) with interpolated midpoints.

**This is NOT the VIX futures term structure.** For actual VIX futures (contango/backwardation of VX contracts), see VIXCentral.com.

- **Upward slope** — Longer-term vol > short-term. Normal state, no immediate panic.
- **Inverted (VIX > VIX3M)** — Short-term fear exceeds longer-term. This IS the slow crossover signal.
- **Partial inversion** — VIX9D spike or back-end kink (VIX3M > VIX6M). Watch closely.

**Spreads:** Front (VIX3M - VIX) and Back (VIX6M - VIX3M) measure steepness. Green > +1.5, amber > 0, red < 0.

**Timing note:** VIX updates from 3:00 AM ET (premarket), but VIX3M/VIX6M only update during regular hours (9:30 AM - 4:15 PM ET). Before the open, VIX may spike while longer tenors still show yesterday's close, causing a temporary apparent inversion.
    """)

points = VommaEngine.get_curve_points(data)
lb = ['VIX','M1','M2','VIX3M','M4','M5','VIX6M']
fs = data.vix3m - data.vix
bs = data.vix6m - data.vix3m
fig = go.Figure()
fig.add_trace(go.Scatter(x=lb, y=points, mode='lines+markers', line=dict(color='#0052cc', width=2.5), marker=dict(size=5, color='#0052cc'), showlegend=False))
fig.add_trace(go.Scatter(x=['VIX','VIX3M','VIX6M'], y=[data.vix,data.vix3m,data.vix6m], mode='markers+text', marker=dict(size=11, color='#0052cc', line=dict(width=2, color='#fff')), text=['VIX','VIX3M','VIX6M'], textposition='top center', textfont=dict(size=10, color='#172b4d', family='DM Sans'), name='CBOE Indices'))
fig.add_hline(y=19.0, line_dash="dash", line_color="#97a0af", annotation_text="Hist. Mean (19)", annotation_position="bottom right", annotation_font=dict(size=10, color="#97a0af", family="DM Sans"))
fig.update_layout(template='plotly_white', paper_bgcolor='#fff', plot_bgcolor='#fafbfc', height=310, margin=dict(t=25,b=40,l=50,r=50), yaxis=dict(title='Implied Vol', gridcolor='#ebecf0'), xaxis=dict(gridcolor='#ebecf0'), font=dict(family='DM Sans', size=11), legend=dict(x=.01, y=.99, font=dict(size=10)))
fsc = "#00875a" if fs > 1.5 else ("#ff991f" if fs > 0 else "#de350b")
bsc = "#00875a" if bs > 1.5 else ("#ff991f" if bs > 0 else "#de350b")
shape = "Normal" if fs > 0 and bs > 0 else ("Inverted" if fs < 0 else "Partial Inversion")
st.markdown(f'<div class="card" style="padding:0"><div style="padding:12px 22px;border-bottom:1px solid #ebecf0;display:flex;gap:40px;font-size:.82em"><div><span style="color:#6b778c">Front Spread (VIX3M \u2212 VIX):</span> <strong style="color:{fsc}">{fs:+.2f} pts</strong></div><div><span style="color:#6b778c">Back Spread (VIX6M \u2212 VIX3M):</span> <strong style="color:{bsc}">{bs:+.2f} pts</strong></div><div><span style="color:#6b778c">Shape:</span> <strong style="color:#172b4d">{shape}</strong></div></div></div>', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# PORTFOLIO CALCULATOR
st.markdown('<div class="sec" style="margin-top:18px">Portfolio Calculator</div>', unsafe_allow_html=True)

with st.expander("Parameter definitions"):
    st.markdown("""
- **BP Usage** — Max buying power deployed. Scales with VIX: higher vol = more BP allowed (richer premium compensates risk).
- **Theta Target** — Daily time decay your portfolio should collect. Minimum always 0.1% NLV; max scales with VIX tier.
- **SPY BW Delta** — Max directional exposure in SPY beta-weighted terms. Keep near zero (delta neutral). Hard limit: +/-0.15% NLV.
- **Max Position** — Per-trade BPR cap. Defined risk (spreads, iron condors): 5% NLV. Undefined risk (strangles, naked): 7% NLV.
- **Capital Reserve** — Undeployed capital. Your oxygen during margin expansion in crashes. Never allocate 100%.
    """)

nlv = st.number_input("Net Liquidation Value ($)", min_value=0.0, value=0.0, step=1000.0, format="%.0f")
vn = data.vix
if nlv > 0:
    for lim,bp,tmn,tmx in [(15,.25,.001,.001),(20,.30,.001,.002),(30,.35,.001,.003),(40,.40,.001,.004),(999,.50,.001,.005)]:
        if vn < lim:
            break
    res = 1.0 - bp
    vtier = "< 15" if vn<15 else ("15-20" if vn<20 else ("20-30" if vn<30 else ("30-40" if vn<40 else "> 40")))
    p1,p2,p3 = st.columns(3)
    p1.metric("VIX Tier", vtier)
    p2.metric("BP Usage", f"{bp*100:.0f}% (${nlv*bp:,.0f})")
    p3.metric("Capital Reserve", f"{res*100:.0f}% (${nlv*res:,.0f})")
    p4,p5,p6 = st.columns(3)
    p4.metric("Theta Target /day", f"${nlv*tmn:,.0f} - ${nlv*tmx:,.0f}")
    p5.metric("SPY BW Delta Max", f"+/- ${nlv*0.0015:,.0f}")
    p6.metric("Max Pos (Defined)", f"${nlv*0.05:,.0f}")
else:
    st.info("Enter your NLV above to calculate parameters.")

# GUIDELINES TABLE
st.markdown('<div class="sec">Portfolio Guidelines</div>', unsafe_allow_html=True)

with st.expander("How to use this table"):
    st.markdown("""
The highlighted row matches the current VIX reading. As VIX rises, you can use more buying power and collect more theta because premium is richer and compensates for the higher risk.

- **BP Usage** — Maximum % of Net Liquidation Value deployed as buying power.
- **Target Theta** — Daily theta decay target as % of NLV. E.g., 0.2% NLV on a $100k account = $200/day.

These are guidelines, not hard rules. Always consider Edge Score, regime, and individual position risk.
    """)

rd = [("< 15","25%","0.1% NLV",vn<15),("15 \u2013 20","30%","0.1 \u2013 0.2% NLV",15<=vn<20),("20 \u2013 30","35%","0.1 \u2013 0.3% NLV",20<=vn<30),("30 \u2013 40","40%","0.1 \u2013 0.4% NLV",30<=vn<40),("> 40","50%","0.1 \u2013 0.5% NLV",vn>=40)]
tr = ""
for lv,bpp,th,act in rd:
    tr += f'<tr{" class=act" if act else ""}><td>{lv}</td><td>{bpp}</td><td>{th}</td></tr>'
st.markdown(f'<div class="card" style="padding:0"><table class="vtbl"><thead><tr><th>VIX Level</th><th>BP Usage</th><th>Target Theta</th></tr></thead><tbody>{tr}</tbody></table></div>', unsafe_allow_html=True)

# POSITION MANAGEMENT
st.markdown('<div class="sec" style="margin-top:18px">Position Management</div>', unsafe_allow_html=True)

with st.expander("Management philosophy"):
    st.markdown("""
Entry is only half the trade — management determines P&L.

- **50% Rule** — Close at 50% of max profit. Taking profits early avoids gamma risk and builds winning consistency.
- **21 DTE** — Manage (close or roll) at 21 DTE. Closing at half the duration captures ~75% of profit with significantly less risk.
- **Rolling** — Always roll for a credit ("death before debit"). Rolling the untested side raises win rate from 32% to 65%.
    """)

m1,m2,m3 = st.columns(3)
with m1:
    st.markdown('<div class="mgmt"><h4>Profit Taking</h4><div class="ml">Target: <span class="mv">50% of max profit</span></div><div class="ml">Taking profits early avoids gamma risk and builds consistency.</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="mgmt"><h4>DTE Discipline</h4><div class="ml">Entry: <span class="mv">45 DTE</span></div><div class="ml">Manage: <span class="mv">21 DTE</span> (close or roll)</div><div class="ml">Closing at half duration captures ~75% of profit.</div><div class="ml" style="color:#de350b">Avoid last week before expiry (gamma risk).</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="mgmt"><h4>Rolling Rules</h4><div class="ml">1. Roll untested side closer (collect credit)</div><div class="ml">2. Roll out in time to next month</div><div class="ml">3. Go inverted / straddle (last resort)</div><div class="ml" style="margin-top:6px">Win rate: 32% (stop) \u2192 <span class="mv">65% (rolling)</span></div><div class="ml"><span class="mv">Always roll for credit \u2014 never debit</span></div></div>', unsafe_allow_html=True)

st.markdown('<div class="ftr">Alpha Insight \u2014 Volatility Cockpit<br>Data: Yahoo Finance (CBOE indices) \u2022 Refreshes every 60s<br>For informational purposes only. Not financial advice.</div>', unsafe_allow_html=True)
