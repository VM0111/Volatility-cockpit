"""
Volatility Cockpit — Streamlit Frontend
Light institutional UI. All sections from vomma.co 1:1.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from vomma_engine import VommaEngine

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(page_title="Volatility Cockpit", page_icon="📡", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# INSTITUTIONAL LIGHT CSS
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #f4f5f7;
    --card: #ffffff;
    --border: #dfe1e6;
    --border-light: #ebecf0;
    --text: #172b4d;
    --text-secondary: #6b778c;
    --text-muted: #97a0af;
    --accent: #0052cc;
    --green: #00875a;
    --green-bg: #e3fcef;
    --red: #de350b;
    --red-bg: #ffebe6;
    --amber: #ff991f;
    --amber-bg: #fffae6;
    --blue-bg: #deebff;
}

.stApp { background-color: var(--bg) !important; font-family: 'DM Sans', sans-serif !important; }
section[data-testid="stSidebar"] { background: var(--card); }
.block-container { padding-top: 1.5rem; max-width: 1180px; }

h1, h2, h3, h4 { color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
p, li, span, div { font-family: 'DM Sans', sans-serif; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* ---- Top Header Bar ---- */
.top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 0; margin-bottom: 8px;
}
.top-title { font-size: 1.6em; font-weight: 700; color: var(--text); letter-spacing: -0.3px; }
.top-subtitle { color: var(--text-secondary); font-size: 0.85em; margin-top: 2px; }

/* ---- Badge row ---- */
.badge-row { display: flex; gap: 12px; }
.badge {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 18px; text-align: center; min-width: 120px;
}
.badge-label { font-size: 0.7em; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
.badge-value { font-size: 1.35em; font-weight: 700; margin-top: 2px; }
.badge-sub { font-size: 0.75em; margin-top: 1px; }

/* ---- Cards ---- */
.card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 24px; margin-bottom: 16px;
}
.card-title {
    font-size: 1.05em; font-weight: 700; color: var(--text);
    margin-bottom: 14px; padding-bottom: 10px;
    border-bottom: 1px solid var(--border-light);
}

/* ---- Verdict ---- */
.verdict-card { border-radius: 10px; padding: 24px; margin: 12px 0; }
.verdict-favorable { background: var(--green-bg); border: 1px solid #abf5d1; }
.verdict-caution { background: var(--amber-bg); border: 1px solid #ffe380; }
.verdict-defensive { background: var(--red-bg); border: 1px solid #ffbdad; }
.verdict-label { font-size: 1.25em; font-weight: 700; margin-bottom: 6px; }
.verdict-strategy { color: var(--text-secondary); font-size: 0.92em; line-height: 1.6; }

/* ---- Alert ---- */
.alert-item {
    background: var(--amber-bg); border: 1px solid #ffe380;
    border-radius: 8px; padding: 12px 16px; margin: 6px 0;
}
.alert-title { font-weight: 600; color: #974f0c; font-size: 0.9em; }
.alert-body { color: #7a5b1e; font-size: 0.85em; margin-top: 3px; }
.alert-red { background: var(--red-bg); border-color: #ffbdad; }
.alert-red .alert-title { color: #bf2600; }
.alert-red .alert-body { color: #8c2a0a; }

/* ---- Gauge bar ---- */
.gauge-bar { display: flex; height: 22px; border-radius: 6px; overflow: hidden; margin: 8px 0; font-size: 0.72em; font-weight: 600; }
.gauge-neg { background: #de350b; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }
.gauge-thin { background: #ff991f; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }
.gauge-norm { background: #0065ff; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }
.gauge-rich { background: #00875a; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }

/* ---- Edge bar ---- */
.edge-track { background: var(--border-light); border-radius: 8px; height: 30px; position: relative; overflow: hidden; }
.edge-fill { height: 100%; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85em; color: #fff; }

/* ---- Signal rows ---- */
.sig-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 0; border-bottom: 1px solid var(--border-light);
}
.sig-row:last-child { border-bottom: none; }
.sig-name { font-weight: 600; color: var(--text); font-size: 0.92em; }
.sig-detail { color: var(--text-muted); font-size: 0.8em; margin-top: 2px; }
.sig-right { display: flex; align-items: center; gap: 12px; }
.pill { display: inline-block; padding: 3px 12px; border-radius: 12px; font-size: 0.78em; font-weight: 600; }
.pill-safe { background: var(--green-bg); color: var(--green); border: 1px solid #abf5d1; }
.pill-warn { background: var(--red-bg); color: var(--red); border: 1px solid #ffbdad; }
.sig-score { font-weight: 700; color: var(--text); font-size: 0.9em; min-width: 44px; text-align: right; }

/* ---- Vol table ---- */
.vtable { width: 100%; border-collapse: collapse; }
.vtable th {
    text-align: left; padding: 8px 12px; color: var(--text-muted);
    font-size: 0.72em; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600;
    border-bottom: 2px solid var(--border);
}
.vtable td { padding: 10px 12px; border-bottom: 1px solid var(--border-light); color: var(--text); font-size: 0.9em; }
.vtable tr:hover td { background: #f8f9fa; }
.vtable .active-row td { background: var(--green-bg); font-weight: 600; }

/* ---- Management cards ---- */
.mgmt-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; height: 100%;
}
.mgmt-card h4 { color: var(--accent); font-size: 0.95em; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border-light); }
.mgmt-line { color: var(--text-secondary); font-size: 0.85em; margin: 6px 0; line-height: 1.5; }
.mgmt-val { color: var(--text); font-weight: 600; }

/* ---- Footer ---- */
.app-footer { text-align: center; color: var(--text-muted); font-size: 0.78em; margin-top: 40px; padding: 20px 0; border-top: 1px solid var(--border); }

/* ---- Metrics override ---- */
[data-testid="stMetric"] { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.8em !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; }

/* ---- Expanders ---- */
.streamlit-expanderHeader { font-size: 0.88em !important; color: var(--text-secondary) !important; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# DATA LOAD (cached 2 min)
# ==========================================

@st.cache_data(ttl=120, show_spinner=False)
def load_data():
    engine = VommaEngine()
    if not engine.fetch_all():
        return None
    return engine.serialize()


data = load_data()

if data is None:
    st.error("Failed to fetch volatility data. Please refresh the page.")
    st.stop()

# safe helpers
def fmt(val, spec=".1f", suffix="", prefix=""):
    if val is None:
        return "N/A"
    return f"{prefix}{val:{spec}}{suffix}"

def signed(val, spec=".1f"):
    if val is None:
        return "N/A"
    return f"{'+' if val >= 0 else ''}{val:{spec}}"


# ==========================================
# HEADER
# ==========================================

h1, h2 = st.columns([3, 2])

with h1:
    st.markdown(f"""
    <div class="top-bar">
        <div>
            <div class="top-title">Volatility Cockpit</div>
            <div class="top-subtitle">{data['ts']}</div>
        </div>
    </div>""", unsafe_allow_html=True)

with h2:
    es = data["edge_score"]
    es_color = "#00875a" if es >= 70 else ("#ff991f" if es >= 40 else "#de350b")
    es_label = "Favorable" if es >= 70 else ("Caution" if es >= 40 else "Defensive")

    vr = data["vix_rank_pctl"]
    vr_str = f"{vr:.0f}%" if vr is not None else "N/A"
    vr_tier = data["vix_rank_tier"]

    cs = data["curve_state"]
    cs_color = "#00875a" if "NORMAL" in cs else "#de350b"

    st.markdown(f"""
    <div class="badge-row" style="justify-content:flex-end;">
        <div class="badge">
            <div class="badge-label">Edge</div>
            <div class="badge-value" style="color:{es_color};">{es}</div>
            <div class="badge-sub" style="color:{es_color};">{es_label}</div>
        </div>
        <div class="badge">
            <div class="badge-label">VIX Rank</div>
            <div class="badge-value">{vr_str}</div>
            <div class="badge-sub" style="color:var(--text-muted);">{vr_tier}</div>
        </div>
        <div class="badge">
            <div class="badge-label">Vol Curve</div>
            <div class="badge-value" style="font-size:0.85em; color:{cs_color}; margin-top:6px;">{cs}</div>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 1. TRADE TODAY?
# ==========================================

st.markdown("### Trade Today?")

with st.expander("What is this? How does the verdict work?", expanded=False):
    st.markdown("""
**Synthesizes all edge signals into a single actionable verdict.**

- **Favorable** — Normal vol curve (VIX < VIX3M) + Edge Score >= 70 + VRP >= 2. Full size, sell premium.
- **Caution** — Mixed signals. Reduce size, prefer defined risk.
- **Defensive** — Toxic Mix active or Edge < 40. No new short-vol, preserve capital.

Active alerts show specific actions from crossover signals and VRP state.
    """)

verdict = data["verdict"]
v_class = {"FAVORABLE": "verdict-favorable", "CAUTION": "verdict-caution", "DEFENSIVE": "verdict-defensive"}.get(verdict, "verdict-caution")
v_icon = {"FAVORABLE": "🟢", "CAUTION": "🟡", "DEFENSIVE": "🔴"}.get(verdict, "⚪")
v_color = {"FAVORABLE": "#006644", "CAUTION": "#974f0c", "DEFENSIVE": "#bf2600"}.get(verdict, "#333")

st.markdown(f"""<div class="verdict-card {v_class}">
    <div class="verdict-label" style="color:{v_color};">{v_icon}  {verdict} — {'Full size, sell premium' if verdict == 'FAVORABLE' else ('Be selective' if verdict == 'CAUTION' else 'Preserve capital')}</div>
    <div class="verdict-strategy">{data['strategy']}</div>
</div>""", unsafe_allow_html=True)

# Verdict metrics
vc1, vc2, vc3, vc4 = st.columns(4)
curve_d = data.get("curve")
vc1.metric("Vol Curve", curve_d["shape"] if curve_d else "N/A")
vc2.metric("Edge Score", f"{es} / 100")
vc3.metric("VRP", signed(data["vrp"]))
vc4.metric("VIX Rank", vr_str)

# Alerts
if data["alerts"]:
    st.markdown("**Active Alerts**")
    for title, body in data["alerts"]:
        is_severe = any(w in title for w in ["Toxic", "Slow", "Negative"])
        cls = "alert-red" if is_severe else "alert-item"
        st.markdown(f"""<div class="alert-item {cls}">
            <div class="alert-title">{title}</div>
            <div class="alert-body">{body}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 2. VRP
# ==========================================

st.markdown("### Volatility Risk Premium (VRP)")

with st.expander("What is VRP? Why does it matter?", expanded=False):
    st.markdown("""
**VRP = VIX - Realized Vol** — the gap between what the market prices (implied) and what actually happens (realized).

Implied Volatility exceeded Realized Volatility in ~83-88% of cases for S&P 500 (1990-2023). 
This is the insurance premium — the market systematically overpays for protection. Premium sellers harvest this structural edge.

**Thresholds:** > 5 pts = premium rich, 2-5 = normal, < 2 = thin (warning), < 0 = negative (structural edge absent).
    """)

vr1, vr2, vr3 = st.columns(3)
vr1.metric("Implied (VIX)", fmt(data["vix"], ".1f"))
vr2.metric("Realized (20d SPX)", fmt(data["rv"], ".1f"))

vrp_val = data["vrp"]
vrp_t = data["vrp_tier"]
vrp_color = {"PREMIUM RICH": "#00875a", "NORMAL": "#0052cc", "THIN": "#ff991f", "NEGATIVE": "#de350b"}.get(vrp_t, "#6b778c")
vr3.markdown(f"""<div style="background:var(--card); border:1px solid var(--border); border-radius:8px; padding:14px 18px;">
    <div style="color:var(--text-muted); font-size:0.78em; text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">VRP</div>
    <div style="color:{vrp_color}; font-size:1.8em; font-weight:700;">{signed(vrp_val)}</div>
    <div style="color:{vrp_color}; font-size:0.82em; font-weight:600;">{vrp_t}</div>
</div>""", unsafe_allow_html=True)

st.markdown("""<div class="gauge-bar">
    <div class="gauge-neg">Negative</div><div class="gauge-thin">Thin</div>
    <div class="gauge-norm">Normal</div><div class="gauge-rich">Rich</div>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. VOLATILITY COMPLEX
# ==========================================

st.markdown("### Volatility Complex")

with st.expander("Index descriptions, sparkline logic, and VIXEQ/VIX ratio", expanded=False):
    st.markdown("""
**8 key indicators fetched from Yahoo Finance:**

- **VIX** — 30-day implied vol of S&P 500. The main fear gauge.
- **VVIX** — Volatility of VIX options. Uncertainty about future VIX levels.
- **VIX9D** — 9-day implied vol. Reacts fastest to sudden events.
- **VIX3M** — 3-month implied vol. Structural trend indicator.
- **VIX6M** — 6-month implied vol. Long-term expectations.
- **SKEW** — Tail risk asymmetry. High SKEW = market pricing crash risk.
- **P/C Ratio** — CBOE equity put/call ratio. >1.0 = fear (puts dominate), <0.7 = complacency.
- **VIXEQ** — S&P 500 constituent vol index (avg IV of individual stocks). VIXEQ/VIX ratio is an implied correlation proxy: high ratio = dispersion (stock-picking), low ratio = correlation spike (systemic risk).

**Sparklines** — 5-day price history. Red = vol rising (risk increasing), green = vol falling (favorable).

**Change** — Daily move vs previous close (absolute + percentage).
    """)

# Build table rows
rows_html = ""
for item in data["vol_complex"]:
    c = item["change"]
    cp = item["change_pct"]
    cc = "#de350b" if c > 0 else ("#00875a" if c < 0 else "#6b778c")
    s = "+" if c >= 0 else ""
    sp = "+" if cp >= 0 else ""

    # Mini sparkline with plotly
    h5 = item["history_5d"]
    if len(h5) >= 2:
        trend = h5[-1] - h5[0]
        tc = "#de350b" if trend > 0 else ("#00875a" if trend < 0 else "#6b778c")
        # Generate inline SVG sparkline
        mn, mx = min(h5), max(h5)
        rng = mx - mn if mx != mn else 1
        w, ht = 80, 24
        pts = []
        for i, v in enumerate(h5):
            x = i * (w / (len(h5) - 1))
            y = ht - ((v - mn) / rng) * ht
            pts.append(f"{x:.1f},{y:.1f}")
        polyline = " ".join(pts)
        spark = f'<svg width="{w}" height="{ht}" style="vertical-align:middle;"><polyline points="{polyline}" fill="none" stroke="{tc}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    else:
        spark = ""

    name_display = item["name"].replace("PC_RATIO", "P/C Ratio")

    rows_html += f"""<tr>
        <td><strong>{name_display}</strong></td>
        <td style="font-weight:600; font-family:'JetBrains Mono',monospace; font-size:0.9em;">{item['current']:.2f}</td>
        <td style="color:{cc}; font-family:'JetBrains Mono',monospace; font-size:0.85em;">{s}{c:.2f} ({sp}{cp:.1f}%)</td>
        <td>{spark}</td>
    </tr>"""

# VIXEQ/VIX ratio footer
veq_ratio = data.get("vixeq_vix_ratio")
veq_note = ""
if veq_ratio is not None:
    veq_note = f'<div style="padding:8px 12px; color:var(--text-secondary); font-size:0.82em;">VIXEQ/VIX implied correlation proxy: <strong>{veq_ratio:.2f}</strong></div>'

st.markdown(f"""<div class="card">
    <table class="vtable">
        <thead><tr><th>Index</th><th>Current</th><th>Change</th><th>5d Sparkline</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    {veq_note}
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 4. EDGE SCORE
# ==========================================

st.markdown("### The Edge — Ratios & Crossovers")

with st.expander("How is the Edge Score calculated?", expanded=False):
    st.markdown("""
**5 edge signals composed into the Edge Score (0-100).**

Each signal is a binary comparison: green = safe to trade, red = warning.

| Signal | Weight | Threshold |
|--------|--------|-----------|
| VVIX/VIX Ratio | 25 pts | <5 safe, 5-6 neutral, >6 regime risk |
| Slow Crossover (VIX vs VIX3M) | 25 pts | VIX < VIX3M = safe |
| Fast Crossover (VIX9D vs VIX) | 20 pts | VIX9D < VIX = safe |
| Toxic Mix | 15 pts | VIX < 16 AND SKEW > 130 = danger |
| VVIX Divergence | 15 pts | VVIX rising while VIX calm = hidden fear |

**Scoring:** >= 70 = Favorable, 40-69 = Caution, < 40 = Defensive.

Crossovers show current state, not the moment of crossing. Confirm timing on TradingView.
    """)

bar_color = "#00875a" if es >= 70 else ("#ff991f" if es >= 40 else "#de350b")
st.markdown(f"""<div class="edge-track">
    <div class="edge-fill" style="width:{es}%; background:{bar_color};">{es} / 100</div>
</div>""", unsafe_allow_html=True)

sig_html = ""
for s in data["signals"]:
    pill_cls = "pill-safe" if s["safe"] else "pill-warn"
    sig_html += f"""<div class="sig-row">
        <div>
            <div class="sig-name">{s['name']}</div>
            <div class="sig-detail">{s['detail']}</div>
        </div>
        <div class="sig-right">
            <span class="pill {pill_cls}">{s['value']}</span>
            <span class="sig-score">{s['score']}/{s['weight']}</span>
        </div>
    </div>"""

st.markdown(f'<div class="card">{sig_html}</div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 5. IMPLIED VOL CURVE
# ==========================================

st.markdown("### Implied Vol Curve (CBOE Indices)")

with st.expander("What does this chart show? How to read it?", expanded=False):
    st.markdown("""
**This plots 4 CBOE implied volatility indices:** VIX9D (9-day) -> VIX (30-day) -> VIX3M (3-month) -> VIX6M (6-month).

Four real data points (larger dots), three linearly interpolated (smaller dots).

**This is NOT the VIX futures term structure.** For actual VIX futures (contango/backwardation of VX contracts), see VIXCentral.com.

- **Upward slope** — Longer-term > short-term. Normal, no immediate panic.
- **Inverted (VIX > VIX3M)** — Short-term fear exceeds longer-term. This IS the slow crossover signal.
- **Partial inversion** — VIX9D spike or back-end kink. Watch closely.

**Spreads:** Front (VIX3M - VIX) and Back (VIX6M - VIX3M) measure steepness. Green >+1.5, amber >0, red <0.

**Timing note:** VIX updates from 3:00 AM ET (premarket), but VIX3M/VIX6M only update during regular hours (9:30 AM - 4:15 PM ET). Before the open, VIX may spike while longer tenors show yesterday's close — causing temporary apparent inversion.
    """)

cv = data.get("curve")
if cv:
    labels = [p[0] for p in cv["points"]]
    days = [p[1] for p in cv["points"]]
    vals = [p[2] for p in cv["points"]]

    # Interpolated midpoints
    mid_days = [(days[i] + days[i+1]) / 2 for i in range(len(days)-1)]
    mid_vals = [(vals[i] + vals[i+1]) / 2 for i in range(len(vals)-1)]

    # All points for smooth line
    all_d, all_v = [], []
    for i in range(len(days)):
        all_d.append(days[i])
        all_v.append(vals[i])
        if i < len(mid_days):
            all_d.append(mid_days[i])
            all_v.append(mid_vals[i])

    fig = go.Figure()

    # Line
    fig.add_trace(go.Scatter(
        x=all_d, y=all_v, mode='lines',
        line=dict(color='#0052cc', width=2.5), showlegend=False,
    ))
    # Real data points
    fig.add_trace(go.Scatter(
        x=days, y=vals, mode='markers+text',
        marker=dict(color='#0052cc', size=11, line=dict(color='#fff', width=2)),
        text=labels, textposition='top center',
        textfont=dict(color='#172b4d', size=11, family='DM Sans'),
        name='CBOE Indices (real data)',
    ))
    # Interpolated dots
    fig.add_trace(go.Scatter(
        x=mid_days, y=mid_vals, mode='markers',
        marker=dict(color='#0052cc', size=5, opacity=0.4),
        name='Interpolated',
    ))
    # Historical mean
    fig.add_hline(
        y=cv["mean"], line=dict(color='#97a0af', width=1, dash='dash'),
        annotation_text=f'Historical Mean ({cv["mean"]:.0f})',
        annotation_position='right',
        annotation_font=dict(color='#97a0af', size=10, family='DM Sans'),
    )

    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='#ffffff', plot_bgcolor='#fafbfc',
        height=340,
        margin=dict(l=50, r=60, t=30, b=50),
        xaxis=dict(title='Days to Expiry', gridcolor='#ebecf0', tickvals=days, ticktext=labels),
        yaxis=dict(title='Implied Volatility', gridcolor='#ebecf0'),
        legend=dict(x=0.01, y=0.99, font=dict(size=10, family='DM Sans')),
        font=dict(family='DM Sans'),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Spreads
    def spread_color(v):
        if v > 1.5: return "#00875a"
        if v > 0: return "#ff991f"
        return "#de350b"

    sc1, sc2, sc3 = st.columns(3)
    sc1.markdown(f"""<div style="text-align:center;">
        <div style="color:var(--text-muted); font-size:0.75em; text-transform:uppercase; letter-spacing:0.5px;">Shape</div>
        <div style="font-size:1.1em; font-weight:600; color:var(--text); margin-top:4px;">{cv['shape']}</div>
    </div>""", unsafe_allow_html=True)
    sc2.markdown(f"""<div style="text-align:center;">
        <div style="color:var(--text-muted); font-size:0.75em; text-transform:uppercase; letter-spacing:0.5px;">Front Spread (VIX3M - VIX)</div>
        <div style="font-size:1.2em; font-weight:700; color:{spread_color(cv['front'])}; margin-top:4px;">{cv['front']:+.2f} pts</div>
    </div>""", unsafe_allow_html=True)
    sc3.markdown(f"""<div style="text-align:center;">
        <div style="color:var(--text-muted); font-size:0.75em; text-transform:uppercase; letter-spacing:0.5px;">Back Spread (VIX6M - VIX3M)</div>
        <div style="font-size:1.2em; font-weight:700; color:{spread_color(cv['back'])}; margin-top:4px;">{cv['back']:+.2f} pts</div>
    </div>""", unsafe_allow_html=True)
else:
    st.warning("Vol curve data unavailable.")

st.markdown("---")

# ==========================================
# 6. PORTFOLIO CALCULATOR
# ==========================================

st.markdown("### Portfolio Calculator")

with st.expander("What do these parameters mean?", expanded=False):
    st.markdown("""
Position sizing and risk parameters based on your Net Liquidation Value and current VIX.

- **BP Usage** — Max buying power deployed. Scales with VIX: higher vol = more BP allowed (richer premium compensates risk).
- **Theta Target** — Daily time decay your portfolio should collect. Minimum always 0.1% NLV; max scales with VIX tier.
- **SPY BW Delta** — Max directional exposure in SPY beta-weighted terms. Keep near zero. Hard limit: +/-0.15% NLV.
- **Max Position** — Per-trade BPR cap. Defined risk: 5% NLV. Undefined: 7% NLV.
- **Capital Reserve** — Undeployed capital. Your oxygen during margin expansion in crashes.
    """)

nlv = st.number_input("Net Liquidation Value ($)", min_value=0.0, value=0.0, step=1000.0, format="%.0f")
vix_now = data["vix"] if data["vix"] else 20.0

if nlv > 0:
    pp = VommaEngine.portfolio_params(nlv, vix_now)
    p1, p2, p3 = st.columns(3)
    p1.metric("VIX Tier", pp["vix_tier"])
    p2.metric("BP Usage", f"{pp['bp_pct']:.0f}% (${pp['bp_dollar']:,.0f})")
    p3.metric("Capital Reserve", f"{pp['reserve_pct']:.0f}% (${pp['reserve_dollar']:,.0f})")
    p4, p5, p6 = st.columns(3)
    p4.metric("Theta Target /day", f"${pp['theta_min']:,.0f} - ${pp['theta_max']:,.0f}")
    p5.metric("SPY BW Delta Max", f"+/- ${pp['spy_bw_delta']:,.0f}")
    p6.metric("Max Position (Defined)", f"${pp['max_defined']:,.0f}")
    st.caption(f"Max position undefined risk: ${pp['max_undefined']:,.0f}")
else:
    st.info("Enter your NLV above to calculate portfolio parameters.")

st.markdown("---")

# ==========================================
# 7. PORTFOLIO GUIDELINES
# ==========================================

st.markdown("### Portfolio Guidelines")

with st.expander("How to read this table", expanded=False):
    st.markdown("""
The highlighted row matches the current VIX reading. As VIX rises, you can use more buying power and collect more theta — because premium is richer and compensates for the higher risk.

- **BP Usage** — Maximum % of NLV deployed as buying power.
- **Target Theta** — Daily theta decay target as % of NLV. E.g., 0.2% NLV on a $100k account = $200/day.

These are guidelines, not hard rules. Always consider Edge Score, regime, and individual position risk.
    """)

gl_rows = VommaEngine.guidelines_rows(vix_now)
gl_html = ""
for r in gl_rows:
    cls = ' class="active-row"' if r["active"] else ""
    gl_html += f'<tr{cls}><td>{r["level"]}</td><td>{r["bp"]}</td><td>{r["theta"]}</td></tr>'

st.markdown(f"""<div class="card">
    <table class="vtable">
        <thead><tr><th>VIX Level</th><th>BP Usage</th><th>Target Theta</th></tr></thead>
        <tbody>{gl_html}</tbody>
    </table>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 8. POSITION MANAGEMENT
# ==========================================

st.markdown("### Position Management")

with st.expander("Management philosophy", expanded=False):
    st.markdown("""
Entry is only half the trade — management determines P&L.

- **50% Rule** — Close at 50% of max profit. Taking profits early avoids gamma risk and builds winning consistency.
- **21 DTE** — Manage (close or roll) at 21 DTE. Closing at half the duration captures ~75% of profit with significantly less risk.
- **Rolling** — Always roll for a credit ("death before debit"). Rolling the untested side raises win rate from 32% to 65%.
    """)

mc1, mc2, mc3 = st.columns(3)

with mc1:
    st.markdown("""<div class="mgmt-card">
        <h4>Profit Taking</h4>
        <div class="mgmt-line">Target: <span class="mgmt-val">50% of max profit</span></div>
        <div class="mgmt-line">Taking profits early avoids gamma risk and builds winning consistency.</div>
    </div>""", unsafe_allow_html=True)

with mc2:
    st.markdown("""<div class="mgmt-card">
        <h4>DTE Discipline</h4>
        <div class="mgmt-line">Entry: <span class="mgmt-val">45 DTE</span></div>
        <div class="mgmt-line">Manage: <span class="mgmt-val">21 DTE</span> (close or roll)</div>
        <div class="mgmt-line">Closing at half duration captures ~75% of profit with less risk.</div>
        <div class="mgmt-line" style="color:var(--red);">Avoid last week before expiration (gamma risk).</div>
    </div>""", unsafe_allow_html=True)

with mc3:
    st.markdown("""<div class="mgmt-card">
        <h4>Rolling Rules</h4>
        <div class="mgmt-line">1. Roll untested side closer (collect credit)</div>
        <div class="mgmt-line">2. Roll out in time to next month</div>
        <div class="mgmt-line">3. Go inverted / straddle (last resort)</div>
        <div class="mgmt-line" style="margin-top:8px;">Win rate: 32% (stop) -> <span class="mgmt-val">65% (rolling)</span></div>
        <div class="mgmt-line"><span class="mgmt-val">Always roll for credit — never debit</span></div>
    </div>""", unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================

st.markdown("""<div class="app-footer">
    Volatility Cockpit &mdash; Alpha Insight<br>
    Data: Yahoo Finance (CBOE indices) &bull; Auto-refreshes every 2 minutes<br>
    For informational purposes only. Not financial advice.
</div>""", unsafe_allow_html=True)
