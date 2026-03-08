import streamlit as st
import plotly.graph_objects as go
from vomma_engine import VommaEngine
from datetime import datetime

st.set_page_config(page_title="Alpha Volatility Cockpit", layout="wide", page_icon="📡", initial_sidebar_state="collapsed")

# ==========================================
# CSS — Institutional Light Theme
# ==========================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
:root{--bg:#f4f5f7;--card:#fff;--border:#dfe1e6;--border-lt:#ebecf0;--text:#172b4d;--text2:#6b778c;--muted:#97a0af;--accent:#0052cc;--green:#00875a;--green-bg:#e3fcef;--green-bdr:#abf5d1;--red:#de350b;--red-bg:#ffebe6;--red-bdr:#ffbdad;--amber:#ff991f;--amber-bg:#fffae6;--amber-bdr:#ffe380;--blue-bg:#deebff}
*{font-family:'DM Sans',system-ui,sans-serif!important}
.stApp{background:var(--bg)!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.2rem;max-width:95%;padding-left:2rem;padding-right:2rem}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 16px}
[data-testid="stMetricLabel"]{color:var(--muted)!important;font-size:.75em!important;text-transform:uppercase;letter-spacing:.5px}
[data-testid="stMetricValue"]{color:var(--text)!important;font-family:'JetBrains Mono',monospace!important}
.streamlit-expanderHeader{font-size:.85em!important;color:var(--text2)!important}
[data-testid="stExpander"] details summary{padding-left:28px!important;position:relative}
[data-testid="stExpander"] details summary svg{position:absolute;left:6px;top:50%;transform:translateY(-50%)}
[data-testid="stExpander"] summary span{overflow:visible!important}
.st-emotion-cache-p5msec{padding-left:28px!important}
details summary span p{margin-left:4px!important}
.hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
.hdr-left{display:flex;align-items:baseline;gap:12px}
.hdr-title{font-size:1.4em;font-weight:700;color:var(--text);letter-spacing:-.3px}
.hdr-sub{color:var(--text2);font-size:.82em}
.badges{display:flex;gap:10px}
.bdg{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 16px;text-align:center;min-width:95px}
.bdg-lbl{font-size:.65em;color:var(--muted);text-transform:uppercase;letter-spacing:.7px;font-weight:600}
.bdg-val{font-size:1.25em;font-weight:700;margin-top:2px;font-family:'JetBrains Mono',monospace}
.bdg-sub{font-size:.7em;margin-top:1px}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;margin-bottom:14px;overflow:hidden}
.card-body{padding:20px}
.sec{font-size:.72em;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.7px;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--border-lt)}
.verdict-bar{padding:18px 22px;border-bottom:1px solid var(--border-lt)}
.v-label{font-size:1.15em;font-weight:700;margin-bottom:3px}
.v-desc{color:var(--text2);font-size:.88em;line-height:1.5}
.v-grid{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--border-lt)}
.v-cell{padding:14px 22px;text-align:center}
.v-cell-lbl{font-size:.65em;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.v-cell-val{font-size:1.05em;font-weight:700;margin-top:3px}
.v-section{padding:16px 22px;border-bottom:1px solid var(--border-lt)}
.v-section:last-child{border-bottom:none}
.alert{border-radius:8px;padding:10px 14px;margin-top:7px}
.alert-amber{background:var(--amber-bg);border:1px solid var(--amber-bdr)}
.alert-amber .a-title{color:#974f0c;font-weight:600;font-size:.82em}
.alert-amber .a-body{color:#7a5b1e;font-size:.78em;margin-top:2px}
.alert-red{background:var(--red-bg);border:1px solid var(--red-bdr)}
.alert-red .a-title{color:#bf2600;font-weight:600;font-size:.82em}
.alert-red .a-body{color:#8c2a0a;font-size:.78em;margin-top:2px}
.gauge{display:flex;height:20px;border-radius:6px;overflow:hidden;margin:6px 0;font-size:.68em;font-weight:600}
.gauge>div{flex:1;display:flex;align-items:center;justify-content:center;color:#fff}
.g-neg{background:var(--red)}.g-thin{background:var(--amber)}.g-norm{background:var(--accent)}.g-rich{background:var(--green)}
.edge-track{background:var(--border-lt);border-radius:8px;height:28px;position:relative;overflow:hidden;margin:8px 0}
.edge-fill{height:100%;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.82em;color:#fff;transition:width .4s}
.sig{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border-lt)}
.sig:last-child{border-bottom:none}
.sig-name{font-weight:600;color:var(--text);font-size:.88em}
.sig-msg{color:var(--muted);font-size:.78em;margin-top:2px}
.sig-right{display:flex;align-items:center;gap:8px}
.pill{display:inline-block;padding:2px 10px;border-radius:12px;font-size:.75em;font-weight:600}
.pill-g{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bdr)}
.pill-r{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bdr)}
.vtbl{width:100%;border-collapse:collapse}
.vtbl th{text-align:left;padding:8px 18px;color:var(--muted);font-size:.7em;text-transform:uppercase;letter-spacing:.5px;font-weight:600;border-bottom:2px solid var(--border)}
.vtbl td{padding:10px 18px;border-bottom:1px solid var(--border-lt);color:var(--text);font-size:.88em}
.vtbl tr:hover td{background:#f8f9fa}
.vtbl .act td{background:var(--green-bg);font-weight:600;border-left:3px solid var(--green)}
.mono{font-family:'JetBrains Mono',monospace;font-size:.88em}
.spark-card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:8px}
.spark-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.spark-name{font-size:.82em;font-weight:700;color:var(--text)}
.spark-val{font-size:.88em;font-weight:700;color:var(--text);font-family:'JetBrains Mono',monospace}
.spark-chg{font-size:.75em;font-weight:600;text-align:right;margin-top:4px}
.mgmt{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;height:100%}
.mgmt h4{color:var(--accent);font-size:.9em;margin:0 0 10px;padding-bottom:8px;border-bottom:1px solid var(--border-lt)}
.mgmt-ln{color:var(--text2);font-size:.82em;margin:5px 0;line-height:1.5}
.mgmt-v{color:var(--text);font-weight:600}
.ftr{text-align:center;color:var(--muted);font-size:.75em;margin-top:36px;padding:18px 0;border-top:1px solid var(--border)}
</style>""", unsafe_allow_html=True)

# ==========================================
# DATA
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    return VommaEngine.fetch_all_data()

try:
    data = load_data()
    edge_score, signals, alerts = VommaEngine.calculate_edge(data)
    vrp, vrp_state, vrp_color, vrp_pct = VommaEngine.calculate_vrp(data)
    regime = "CONTANGO" if data.vix < data.vix3m else "BACKWARDATION"
    regime_tag = "NORMAL (VIX < VIX3M)" if regime == "CONTANGO" else "INVERTED (VIX > VIX3M)"
    vix_rank_color = "#ff991f" if 30 <= data.vix_rank <= 60 else ("#de350b" if data.vix_rank > 60 else "#00875a")
    edge_color = "#00875a" if edge_score >= 70 else ("#ff991f" if edge_score >= 40 else "#de350b")
    edge_label = "Favorable" if edge_score >= 70 else ("Caution" if edge_score >= 40 else "Defensive")
    regime_color_css = "#00875a" if regime == "CONTANGO" else "#de350b"
except Exception as e:
    st.error(f"Engine error: {str(e)}")
    st.stop()

# ==========================================
# HEADER
# ==========================================
h1, h2 = st.columns([3, 2])
with h1:
    now = datetime.now().strftime("%A, %B %d, %Y  %I:%M %p")
    st.markdown(f'<div class="hdr-left"><span class="hdr-title">Volatility Cockpit</span></div><div class="hdr-sub">{now}</div>', unsafe_allow_html=True)
with h2:
    st.markdown(f"""<div class="badges" style="justify-content:flex-end;">
<div class="bdg"><div class="bdg-lbl">Edge</div><div class="bdg-val" style="color:{edge_color}">{edge_score}</div><div class="bdg-sub" style="color:{edge_color}">{edge_label}</div></div>
<div class="bdg"><div class="bdg-lbl">VIX Rank</div><div class="bdg-val" style="color:{vix_rank_color}">{data.vix_rank:.0f}%</div><div class="bdg-sub" style="color:var(--muted)">{'Low' if data.vix_rank<30 else ('Mid' if data.vix_rank<=60 else 'High')}</div></div>
<div class="bdg"><div class="bdg-lbl">Vol Curve</div><div class="bdg-val" style="font-size:.85em;color:{regime_color_css};margin-top:4px">{regime_tag}</div></div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr style="margin:8px 0 18px;border-color:#dfe1e6">', unsafe_allow_html=True)

# ==========================================
# TRADE TODAY?
# ==========================================
st.markdown('<div class="sec">Trade Today?</div>', unsafe_allow_html=True)

with st.expander("  Verdict logic and thresholds", expanded=False):
    st.markdown("""
- **Favorable** — Normal vol curve (VIX < VIX3M) + Edge >= 70 + VRP > 0. Full size, sell premium.
- **Caution** — Mixed signals. Reduce size, prefer defined risk.
- **Defensive** — Toxic Mix active or Edge < 40. No new short-vol, preserve capital.
    """)

if regime == "CONTANGO" and edge_score >= 70 and vrp > 0:
    v_title, v_desc, v_bg = "FAVORABLE", "Conditions support selling premium", "#e3fcef"
    v_color = "#006644"
    s_txt = "Sell 16\u0394 strangles at 45 DTE. Use 35% BP. Theta target: 0.1\u20130.3% NLV/day."
elif edge_score < 40 or signals.get('Toxic Mix (15 pts)', {}).get('status') == 'Red':
    v_title, v_desc, v_bg = "DEFENSIVE", "Toxic Mix active or Edge < 40. Preserve capital.", "#ffebe6"
    v_color = "#bf2600"
    s_txt = "No new short-vol, preserve capital."
else:
    v_title, v_desc, v_bg = "CAUTION", "Mixed signals. Reduce size, be selective.", "#fffae6"
    v_color = "#974f0c"
    s_txt = "Smaller size, prefer defined risk (spreads). Take profits at 50%. Manage at 21 DTE."

v_icon = {"FAVORABLE": "\U0001f7e2", "CAUTION": "\U0001f7e1", "DEFENSIVE": "\U0001f534"}.get(v_title, "")

# Alerts HTML
alerts_html = ""
for a in alerts:
    parts = a.split(':', 1)
    title = parts[0]
    msg = parts[1].strip() if len(parts) > 1 else ""
    is_severe = any(w in title for w in ["Toxic", "Structural", "Negative"])
    cls = "alert-red" if is_severe else "alert-amber"
    alerts_html += f'<div class="alert {cls}"><div class="a-title">{title}</div><div class="a-body">{msg}</div></div>'
if not alerts:
    alerts_html = '<div style="color:var(--muted);font-size:.82em;margin-top:6px">No active alerts.</div>'

st.markdown(f"""<div class="card">
<div class="verdict-bar" style="background:{v_bg}">
<div class="v-label" style="color:{v_color}">{v_icon} {v_title}</div>
<div class="v-desc">{v_desc}</div>
</div>
<div class="v-grid">
<div class="v-cell"><div class="v-cell-lbl">Vol Curve</div><div class="v-cell-val" style="color:{regime_color_css}">{"Normal" if regime=="CONTANGO" else "Inverted"}</div></div>
<div class="v-cell"><div class="v-cell-lbl">Edge Score</div><div class="v-cell-val" style="color:{edge_color}">{edge_score}</div></div>
<div class="v-cell"><div class="v-cell-lbl">VRP</div><div class="v-cell-val" style="color:{vrp_color}">{vrp:+.1f}</div></div>
<div class="v-cell"><div class="v-cell-lbl">VIX Rank</div><div class="v-cell-val" style="color:{vix_rank_color}">{data.vix_rank:.0f}%</div></div>
</div>
<div class="v-section"><div class="v-cell-lbl" style="margin-bottom:4px">Strategy</div><div style="font-size:.88em;color:var(--text)">{s_txt}</div></div>
<div class="v-section"><div class="v-cell-lbl">Active Alerts</div>{alerts_html}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

# ==========================================
# VRP & EDGE — side by side
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="sec">Volatility Risk Premium (VRP)</div>', unsafe_allow_html=True)
    with st.expander("  What is VRP?", expanded=False):
        st.markdown("**VRP = VIX - Realized Vol (20d SPX).** The structural edge behind premium selling. Implied Vol exceeded Realized Vol ~83-88% of the time for S&P 500 (1990-2023). Thresholds: >5 = rich, 2-5 = normal, <2 = thin, <0 = negative.")

    # Proportional bars
    max_v = max(data.vix, data.spx_rv_20d, 1)
    vix_w = data.vix / max_v * 100
    rv_w = data.spx_rv_20d / max_v * 100

    st.markdown(f"""<div class="card card-body">
<div style="display:flex;justify-content:space-between;font-size:.82em;margin-bottom:3px"><span style="color:var(--text2)">Implied (VIX)</span><span class="mono" style="font-weight:600;color:var(--text)">{data.vix:.1f}</span></div>
<div style="background:var(--border-lt);height:6px;border-radius:4px;margin-bottom:14px"><div style="background:var(--text);width:{vix_w:.0f}%;height:100%;border-radius:4px"></div></div>
<div style="display:flex;justify-content:space-between;font-size:.82em;margin-bottom:3px"><span style="color:var(--text2)">Realized (20d SPX)</span><span class="mono" style="font-weight:600;color:var(--text)">{data.spx_rv_20d:.1f}</span></div>
<div style="background:var(--border-lt);height:6px;border-radius:4px;margin-bottom:18px"><div style="background:var(--muted);width:{rv_w:.0f}%;height:100%;border-radius:4px"></div></div>
<div style="border-top:1px solid var(--border-lt);padding-top:14px;display:flex;align-items:baseline;gap:10px">
<span style="font-size:.82em;color:var(--text2)">VRP</span>
<span class="mono" style="font-size:1.6em;font-weight:700;color:{vrp_color}">{vrp:+.1f}</span>
<span style="font-size:.82em;font-weight:700;color:{vrp_color}">{vrp_state}</span>
</div>
<div class="gauge"><div class="g-neg">Negative</div><div class="g-thin">Thin</div><div class="g-norm">Normal</div><div class="g-rich">Rich</div></div>
</div>""", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="sec">The Edge — Ratios & Crossovers</div>', unsafe_allow_html=True)
    with st.expander("  Edge Score methodology", expanded=False):
        st.markdown("5 signals (total 100 pts): VVIX/VIX Ratio (25), Slow Crossover (25), Fast Crossover (20), Toxic Mix (15), VVIX Divergence (15). >=70 Favorable, 40-69 Caution, <40 Defensive.")

    st.markdown(f'<div class="edge-track"><div class="edge-fill" style="width:{edge_score}%;background:{edge_color}">{edge_score}/100</div></div>', unsafe_allow_html=True)

    sig_html = '<div class="card card-body" style="padding:16px 20px">'
    for k, v in signals.items():
        pill_cls = "pill-g" if v['status'] == 'Green' else "pill-r"
        pill_txt = "Safe" if v['status'] == 'Green' else "Warning"
        sig_html += f'<div class="sig"><div><div class="sig-name">{k}</div><div class="sig-msg">{v["msg"]}</div></div><div class="sig-right"><span class="pill {pill_cls}">{pill_txt}</span></div></div>'
    sig_html += '</div>'
    st.markdown(sig_html, unsafe_allow_html=True)

# ==========================================
# VOLATILITY COMPLEX
# ==========================================
st.markdown('<div class="sec" style="margin-top:18px">Volatility Complex</div>', unsafe_allow_html=True)

with st.expander("  Index descriptions and sparkline logic", expanded=False):
    st.markdown("""
- **VIX** — 30-day implied vol. The main fear gauge.
- **VVIX** — Vol-of-VIX. Uncertainty about future VIX levels.
- **VIX9D** — 9-day implied vol. Fastest to react.
- **VIX3M** — 3-month implied vol. Structural trend.
- **VIX6M** — 6-month implied vol. Long-term expectations.
- **SKEW** — Tail risk asymmetry. High = crash risk pricing.
- **P/C Ratio** — Put/Call ratio. >1.0 = fear, <0.7 = complacency.

Sparkline color: red = vol rising (risk), green = vol falling (favorable).
    """)

complex_tickers = [("^VIX", "VIX"), ("^VVIX", "VVIX"), ("^VIX9D", "VIX9D"), ("^VIX3M", "VIX3M"), ("^VIX6M", "VIX6M"), ("^SKEW", "SKEW"), ("^CPC", "P/C Ratio")]

cols = st.columns(4)
for i, (ticker, name) in enumerate(complex_tickers):
    if ticker in data.history and len(data.history[ticker]) > 1:
        hist = data.history[ticker]
        curr = hist[-1]
        prev = hist[-2]
        chg = curr - prev
        pct = (chg / prev) * 100 if prev != 0 else 0
        c_color = "#de350b" if chg > 0 else "#00875a"
        sign = "+" if chg >= 0 else ""

        min_v, max_v = min(hist), max(hist)
        diff = max_v - min_v if max_v != min_v else 1
        pts = " ".join([f"{j*(100/(len(hist)-1)):.1f},{28-((v-min_v)/diff)*28:.1f}" for j, v in enumerate(hist)])

        cols[i % 4].markdown(f"""<div class="spark-card">
<div class="spark-row"><span class="spark-name">{name}</span><span class="spark-val">{curr:.2f}</span></div>
<svg viewBox="-1 -1 102 30" width="100%" height="24" preserveAspectRatio="none"><polyline points="{pts}" fill="none" stroke="{c_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div class="spark-chg" style="color:{c_color}">{sign}{chg:.2f} ({sign}{pct:.1f}%)</div>
</div>""", unsafe_allow_html=True)

# ==========================================
# IMPLIED VOL CURVE
# ==========================================
st.markdown('<div class="sec" style="margin-top:18px">Implied Vol Curve (CBOE Indices)</div>', unsafe_allow_html=True)

with st.expander("  How to read the vol curve", expanded=False):
    st.markdown("""
Plots VIX9D -> VIX -> VIX3M -> VIX6M with interpolated midpoints. **NOT** VIX futures term structure.

- **Upward slope** = normal, no panic.
- **Inverted (VIX > VIX3M)** = structural fear (slow crossover).
- **Partial inversion** = VIX9D spike or back-end kink. Watch.

**Timing note:** VIX updates from 3 AM ET (premarket), VIX3M/VIX6M only during regular hours. Pre-open inversions may be temporary.
    """)

points = VommaEngine.get_curve_points(data)
labels_curve = ['VIX', 'M1', 'M2', 'VIX3M', 'M4', 'M5', 'VIX6M']
front_spread = data.vix3m - data.vix
back_spread = data.vix6m - data.vix3m

fig = go.Figure()
fig.add_trace(go.Scatter(x=labels_curve, y=points, mode='lines+markers', line=dict(color='#0052cc', width=2.5), marker=dict(size=5, color='#0052cc'), showlegend=False))
anchors_x = ['VIX', 'VIX3M', 'VIX6M']
anchors_y = [data.vix, data.vix3m, data.vix6m]
fig.add_trace(go.Scatter(x=anchors_x, y=anchors_y, mode='markers+text', marker=dict(size=11, color='#0052cc', line=dict(width=2, color='#fff')), text=['VIX', 'VIX3M', 'VIX6M'], textposition='top center', textfont=dict(size=10, color='#172b4d', family='DM Sans'), name='CBOE Indices'))
fig.add_hline(y=19.0, line_dash="dash", line_color="#97a0af", annotation_text="Hist. Mean (19)", annotation_position="bottom right", annotation_font=dict(size=10, color="#97a0af", family="DM Sans"))
fig.update_layout(template='plotly_white', paper_bgcolor='#fff', plot_bgcolor='#fafbfc', height=310, margin=dict(t=25, b=40, l=50, r=50), yaxis=dict(title='Implied Vol', gridcolor='#ebecf0'), xaxis=dict(gridcolor='#ebecf0'), font=dict(family='DM Sans', size=11), legend=dict(x=.01, y=.99, font=dict(size=10)))

fs_color = "#00875a" if front_spread > 1.5 else ("#ff991f" if front_spread > 0 else "#de350b")
bs_color = "#00875a" if back_spread > 1.5 else ("#ff991f" if back_spread > 0 else "#de350b")

st.markdown(f"""<div class="card" style="padding:0">
<div style="padding:12px 22px;border-bottom:1px solid var(--border-lt);display:flex;gap:40px;font-size:.82em">
<div><span style="color:var(--text2)">Front Spread (VIX3M - VIX):</span> <strong style="color:{fs_color}">{front_spread:+.2f} pts</strong></div>
<div><span style="color:var(--text2)">Back Spread (VIX6M - VIX3M):</span> <strong style="color:{bs_color}">{back_spread:+.2f} pts</strong></div>
<div><span style="color:var(--text2)">Shape:</span> <strong style="color:var(--text)">{"Normal" if front_spread>0 and back_spread>0 else ("Inverted" if front_spread<0 else "Partial Inversion")}</strong></div>
</div>
</div>""", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# PORTFOLIO CALCULATOR
# ==========================================
st.markdown('<div class="sec" style="margin-top:18px">Portfolio Calculator</div>', unsafe_allow_html=True)

with st.expander("  Parameter definitions", expanded=False):
    st.markdown("""
- **BP Usage** — Max buying power deployed. Scales with VIX.
- **Theta Target** — Daily time decay target. Min 0.1% NLV.
- **SPY BW Delta** — Max directional exposure. Hard limit: +/-0.15% NLV.
- **Max Position** — Defined risk: 5% NLV. Undefined: 7% NLV.
- **Capital Reserve** — Undeployed capital for margin expansion.
    """)

nlv = st.number_input("Net Liquidation Value ($)", min_value=0.0, value=0.0, step=1000.0, format="%.0f")
vix_now = data.vix

if nlv > 0:
    tiers = [(15, .25, .001, .001), (20, .30, .001, .002), (30, .35, .001, .003), (40, .40, .001, .004), (999, .50, .001, .005)]
    for lim, bp, tmin, tmax in tiers:
        if vix_now < lim:
            break
    reserve = 1.0 - bp
    p1, p2, p3 = st.columns(3)
    vt = f"< 15" if vix_now < 15 else (f"15 - 20" if vix_now < 20 else (f"20 - 30" if vix_now < 30 else (f"30 - 40" if vix_now < 40 else "> 40")))
    p1.metric("VIX Tier", vt)
    p2.metric("BP Usage", f"{bp*100:.0f}% (${nlv*bp:,.0f})")
    p3.metric("Capital Reserve", f"{reserve*100:.0f}% (${nlv*reserve:,.0f})")
    p4, p5, p6 = st.columns(3)
    p4.metric("Theta Target /day", f"${nlv*tmin:,.0f} - ${nlv*tmax:,.0f}")
    p5.metric("SPY BW Delta Max", f"+/- ${nlv*0.0015:,.0f}")
    p6.metric("Max Pos (Defined)", f"${nlv*0.05:,.0f}")
else:
    st.info("Enter your NLV above to calculate parameters.")

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# ==========================================
# PORTFOLIO GUIDELINES
# ==========================================
st.markdown('<div class="sec">Portfolio Guidelines</div>', unsafe_allow_html=True)

with st.expander("  How to use this table", expanded=False):
    st.markdown("Highlighted row matches current VIX. Higher VIX = more BP allowed because premium is richer. These are guidelines, not hard rules.")

rows_data = [
    ("\u003C 15", "25%", "0.1% NLV", vix_now < 15),
    ("15 \u2013 20", "30%", "0.1 \u2013 0.2% NLV", 15 <= vix_now < 20),
    ("20 \u2013 30", "35%", "0.1 \u2013 0.3% NLV", 20 <= vix_now < 30),
    ("30 \u2013 40", "40%", "0.1 \u2013 0.4% NLV", 30 <= vix_now < 40),
    ("\u003E 40", "50%", "0.1 \u2013 0.5% NLV", vix_now >= 40),
]
tbl_rows = ""
for level, bp_str, theta, active in rows_data:
    cls = ' class="act"' if active else ""
    tbl_rows += f"<tr{cls}><td>{level}</td><td>{bp_str}</td><td>{theta}</td></tr>"

st.markdown(f"""<div class="card" style="padding:0">
<table class="vtbl"><thead><tr><th>VIX Level</th><th>BP Usage</th><th>Target Theta</th></tr></thead>
<tbody>{tbl_rows}</tbody></table>
</div>""", unsafe_allow_html=True)

# ==========================================
# POSITION MANAGEMENT
# ==========================================
st.markdown('<div class="sec" style="margin-top:18px">Position Management</div>', unsafe_allow_html=True)

with st.expander("  Management philosophy", expanded=False):
    st.markdown("Entry is half the trade. 50% profit target avoids gamma risk. 21 DTE management captures ~75% of profit. Rolling for credit raises win rate from 32% to 65%.")

mc1, mc2, mc3 = st.columns(3)
with mc1:
    st.markdown("""<div class="mgmt"><h4>Profit Taking</h4>
<div class="mgmt-ln">Target: <span class="mgmt-v">50% of max profit</span></div>
<div class="mgmt-ln">Taking profits early avoids gamma risk and builds consistency.</div>
</div>""", unsafe_allow_html=True)
with mc2:
    st.markdown("""<div class="mgmt"><h4>DTE Discipline</h4>
<div class="mgmt-ln">Entry: <span class="mgmt-v">45 DTE</span></div>
<div class="mgmt-ln">Manage: <span class="mgmt-v">21 DTE</span> (close or roll)</div>
<div class="mgmt-ln">Closing at half duration captures ~75% of profit.</div>
<div class="mgmt-ln" style="color:#de350b">Avoid last week before expiry (gamma risk).</div>
</div>""", unsafe_allow_html=True)
with mc3:
    st.markdown("""<div class="mgmt"><h4>Rolling Rules</h4>
<div class="mgmt-ln">1. Roll untested side closer (collect credit)</div>
<div class="mgmt-ln">2. Roll out in time to next month</div>
<div class="mgmt-ln">3. Go inverted / straddle (last resort)</div>
<div class="mgmt-ln" style="margin-top:6px">Win rate: 32% (stop) \u2192 <span class="mgmt-v">65% (rolling)</span></div>
<div class="mgmt-ln"><span class="mgmt-v">Always roll for credit \u2014 never debit</span></div>
</div>""", unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""<div class="ftr">
Alpha Insight \u2014 Volatility Cockpit<br>
Data: Yahoo Finance (CBOE indices) \u2022 Refreshes every 60s<br>
For informational purposes only. Not financial advice.
</div>""", unsafe_allow_html=True)
