"""
Vomma — Volatility Cockpit
Streamlit frontend. Professional dark theme.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from vomma_engine import VommaEngine

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Vomma — Volatility Cockpit",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# CUSTOM CSS — DARK PROFESSIONAL THEME
# ==========================================

st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0d1117; }
    section[data-testid="stSidebar"] { background-color: #161b22; }

    /* Headers */
    h1, h2, h3 { color: #e6edf3 !important; }
    h1 { letter-spacing: -0.5px !important; }

    /* Remove default padding */
    .block-container { padding-top: 2rem; max-width: 1200px; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    [data-testid="stMetricValue"] { color: #e6edf3 !important; }

    /* Verdict cards */
    .verdict-favorable {
        background: linear-gradient(135deg, #0d1f0d, #0a2e0a);
        border: 1px solid #238636;
        border-radius: 12px; padding: 24px; margin: 16px 0;
    }
    .verdict-caution {
        background: linear-gradient(135deg, #1f1a0d, #2e2410);
        border: 1px solid #d29922;
        border-radius: 12px; padding: 24px; margin: 16px 0;
    }
    .verdict-defensive {
        background: linear-gradient(135deg, #1f0d0d, #2e0a0a);
        border: 1px solid #f85149;
        border-radius: 12px; padding: 24px; margin: 16px 0;
    }
    .verdict-title {
        font-size: 1.4em; font-weight: 700; margin-bottom: 8px;
    }
    .verdict-strategy {
        color: #8b949e; font-size: 0.95em; line-height: 1.6;
    }

    /* Signal badges */
    .badge-safe {
        display: inline-block; background: #238636; color: #fff;
        padding: 2px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600;
    }
    .badge-warn {
        display: inline-block; background: #da3633; color: #fff;
        padding: 2px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600;
    }
    .badge-neutral {
        display: inline-block; background: #d29922; color: #fff;
        padding: 2px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600;
    }

    /* Edge score bar */
    .edge-bar-bg {
        background: #21262d; border-radius: 8px; height: 32px;
        position: relative; overflow: hidden; margin: 8px 0;
    }
    .edge-bar-fill {
        height: 100%; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.9em; color: #fff;
        transition: width 0.5s;
    }

    /* VRP gauge */
    .vrp-bar {
        display: flex; height: 24px; border-radius: 6px; overflow: hidden;
        margin: 8px 0; font-size: 0.75em; font-weight: 600;
    }
    .vrp-neg { background: #da3633; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }
    .vrp-thin { background: #d29922; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }
    .vrp-norm { background: #388bfd; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }
    .vrp-rich { background: #238636; flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; }

    /* Signal row */
    .signal-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 10px 14px; border-bottom: 1px solid #21262d;
    }
    .signal-name { color: #e6edf3; font-weight: 500; }
    .signal-detail { color: #8b949e; font-size: 0.85em; }
    .signal-score { color: #e6edf3; font-weight: 600; min-width: 50px; text-align: right; }

    /* Alert box */
    .alert-box {
        background: #1c1206; border: 1px solid #d29922;
        border-radius: 8px; padding: 12px 16px; margin: 6px 0;
        color: #d29922; font-size: 0.9em;
    }
    .alert-box-red {
        background: #1c0606; border: 1px solid #f85149;
        border-radius: 8px; padding: 12px 16px; margin: 6px 0;
        color: #f85149; font-size: 0.9em;
    }

    /* Section card */
    .section-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 12px; padding: 24px; margin: 16px 0;
    }
    .section-title {
        color: #e6edf3; font-size: 1.15em; font-weight: 600;
        margin-bottom: 16px; padding-bottom: 8px;
        border-bottom: 1px solid #30363d;
    }

    /* Table styling */
    .vol-table { width: 100%; border-collapse: collapse; }
    .vol-table th {
        text-align: left; padding: 8px 12px; color: #8b949e;
        font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.5px;
        border-bottom: 1px solid #30363d;
    }
    .vol-table td {
        padding: 10px 12px; border-bottom: 1px solid #21262d;
        color: #e6edf3; font-size: 0.95em;
    }
    .vol-table tr:hover td { background: #1c2128; }
    .active-row td { background: #0d2818 !important; border-left: 3px solid #238636; }

    /* Management cards */
    .mgmt-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 10px; padding: 20px;
    }
    .mgmt-card h4 { color: #58a6ff; margin-bottom: 10px; }
    .mgmt-item { color: #8b949e; margin: 6px 0; font-size: 0.9em; line-height: 1.5; }
    .mgmt-value { color: #e6edf3; font-weight: 600; }

    /* Sparkline container */
    .spark-up { color: #3fb950; font-size: 0.85em; }
    .spark-down { color: #f85149; font-size: 0.85em; }
    .spark-flat { color: #8b949e; font-size: 0.85em; }

    /* Footer */
    .footer {
        text-align: center; color: #484f58; font-size: 0.8em;
        margin-top: 40px; padding: 20px; border-top: 1px solid #21262d;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA FETCH
# ==========================================

@st.cache_data(ttl=120, show_spinner=False)
def load_data():
    """Fetch all data. Returns serializable dict."""
    engine = VommaEngine()
    if not engine.fetch_all():
        return None

    vix_val = engine.vix.current if engine.vix else None
    rv = engine.realized_vol_20d()
    vrp_val = engine.vrp()
    vix_rank = engine.vix_rank()
    curve = engine.vol_curve()
    signals = engine.edge_signals()
    score = engine.edge_score()
    verdict = engine.trade_verdict()

    # Vol complex table data
    vol_complex = []
    for name in ["VIX", "VIX9D", "VIX3M", "VIX6M", "VVIX", "SKEW"]:
        idx = engine.index_data.get(name)
        if idx:
            vol_complex.append({
                "name": idx.name,
                "current": idx.current,
                "change": idx.change,
                "change_pct": idx.change_pct,
                "history_5d": idx.history_5d,
                "description": idx.description,
            })

    # Serialize everything to basic types
    result = {
        "timestamp": datetime.now().strftime("%A, %B %d, %Y — %I:%M %p"),
        "vix": vix_val,
        "realized_vol": rv,
        "vrp": vrp_val,
        "vrp_tier": engine.vrp_tier(vrp_val) if vrp_val is not None else "N/A",
        "vix_rank": vix_rank[0] if vix_rank else None,
        "vix_rank_tier": vix_rank[1] if vix_rank else "N/A",
        "curve_state": engine.curve_state_label(),
        "edge_score": score,
        "vol_complex": vol_complex,
        "signals": [
            {"name": s.name, "max": s.max_points, "score": s.score,
             "safe": s.is_safe, "value": s.value_str, "detail": s.detail}
            for s in signals
        ],
        "verdict": verdict.verdict,
        "strategy": verdict.strategy,
        "alerts": verdict.alerts,
        "curve": {
            "shape": curve.shape,
            "points": curve.points,
            "front": curve.front_spread,
            "back": curve.back_spread,
            "mean": curve.historical_mean,
        } if curve else None,
    }
    return result


# ==========================================
# HELPER: color for change
# ==========================================

def change_color(val):
    if val > 0:
        return "#f85149"  # Vol rising = risk = red
    elif val < 0:
        return "#3fb950"  # Vol falling = green
    return "#8b949e"


def edge_bar_color(score):
    if score >= 70:
        return "#238636"
    elif score >= 40:
        return "#d29922"
    return "#da3633"


def spread_color(val):
    if val > 1.5:
        return "#3fb950"
    elif val > 0:
        return "#d29922"
    return "#f85149"


# ==========================================
# LOAD DATA
# ==========================================

data = load_data()

if data is None:
    st.error("Failed to fetch volatility data. Check internet connection and try refreshing.")
    st.stop()

# ==========================================
# HEADER
# ==========================================

col_title, col_badges = st.columns([3, 2])

with col_title:
    st.markdown("# 📡 Vomma — Volatility Cockpit")
    st.caption(data["timestamp"])

with col_badges:
    b1, b2, b3 = st.columns(3)

    # Edge Score badge
    es = data["edge_score"]
    es_color = edge_bar_color(es)
    es_label = "Favorable" if es >= 70 else ("Caution" if es >= 40 else "Defensive")
    b1.markdown(f"""<div style="text-align:center; background:#161b22; border:1px solid {es_color};
        border-radius:8px; padding:8px;">
        <div style="color:#8b949e; font-size:0.75em;">EDGE</div>
        <div style="color:{es_color}; font-size:1.5em; font-weight:700;">{es}</div>
        <div style="color:{es_color}; font-size:0.8em;">{es_label}</div>
    </div>""", unsafe_allow_html=True)

    # VIX Rank badge
    vr = data["vix_rank"]
    vr_tier = data["vix_rank_tier"]
    vr_str = f"{vr:.0f}%" if vr is not None else "N/A"
    b2.markdown(f"""<div style="text-align:center; background:#161b22; border:1px solid #30363d;
        border-radius:8px; padding:8px;">
        <div style="color:#8b949e; font-size:0.75em;">VIX RANK</div>
        <div style="color:#e6edf3; font-size:1.5em; font-weight:700;">{vr_str}</div>
        <div style="color:#8b949e; font-size:0.8em;">{vr_tier}</div>
    </div>""", unsafe_allow_html=True)

    # Curve state
    cs = data["curve_state"]
    cs_color = "#3fb950" if "NORMAL" in cs else "#f85149"
    b3.markdown(f"""<div style="text-align:center; background:#161b22; border:1px solid #30363d;
        border-radius:8px; padding:8px;">
        <div style="color:#8b949e; font-size:0.75em;">VOL CURVE</div>
        <div style="color:{cs_color}; font-size:0.95em; font-weight:600; margin-top:6px;">{cs}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECTION 1: TRADE VERDICT
# ==========================================

verdict = data["verdict"]
v_class = f"verdict-{verdict.lower()}"
v_icon = {"FAVORABLE": "🟢", "CAUTION": "🟡", "DEFENSIVE": "🔴"}.get(verdict, "⚪")
v_title_color = {"FAVORABLE": "#3fb950", "CAUTION": "#d29922", "DEFENSIVE": "#f85149"}.get(verdict, "#8b949e")

st.markdown(f"""
<div class="{v_class}">
    <div class="verdict-title" style="color:{v_title_color};">{v_icon} {verdict} — {'Full size, sell premium' if verdict == 'FAVORABLE' else ('Be selective' if verdict == 'CAUTION' else 'Preserve capital')}</div>
    <div class="verdict-strategy">{data['strategy']}</div>
</div>
""", unsafe_allow_html=True)

# Verdict metrics row
vc1, vc2, vc3, vc4 = st.columns(4)
curve_data = data.get("curve")
curve_shape_str = curve_data["shape"] if curve_data else "N/A"
vc1.metric("Vol Curve", curve_shape_str)
vc2.metric("Edge Score", f"{data['edge_score']} / 100")
vrp_str = f"+{data['vrp']}" if data['vrp'] is not None and data['vrp'] >= 0 else (f"{data['vrp']}" if data['vrp'] is not None else "N/A")
vc3.metric("VRP", vrp_str)
vc4.metric("VIX Rank", f"{data['vix_rank']:.0f}%" if data['vix_rank'] else "N/A")

# Alerts
if data["alerts"]:
    for alert in data["alerts"]:
        alert_class = "alert-box-red" if "Toxic" in alert or "Slow Crossover" in alert or "Negative" in alert else "alert-box"
        st.markdown(f'<div class="{alert_class}">{alert}</div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECTION 2: VRP
# ==========================================

st.markdown("### Volatility Risk Premium (VRP)")
st.caption("VRP = VIX − Realized Vol (20d SPX). The structural edge behind premium selling.")

vrp_c1, vrp_c2, vrp_c3 = st.columns(3)
vrp_c1.metric("Implied (VIX)", f"{data['vix']:.1f}" if data['vix'] else "N/A")
vrp_c2.metric("Realized (20d SPX)", f"{data['realized_vol']:.1f}" if data['realized_vol'] else "N/A")

vrp_val = data["vrp"]
vrp_tier = data["vrp_tier"]
vrp_color = {"PREMIUM RICH": "#3fb950", "NORMAL": "#388bfd", "THIN": "#d29922", "NEGATIVE": "#f85149"}.get(vrp_tier, "#8b949e")
vrp_c3.markdown(f"""<div style="background:#161b22; border:1px solid #30363d; border-radius:8px; padding:12px 16px;">
    <div style="color:#8b949e; font-size:0.8em;">VRP</div>
    <div style="color:{vrp_color}; font-size:1.8em; font-weight:700;">{vrp_str}</div>
    <div style="color:{vrp_color}; font-size:0.85em; font-weight:600;">{vrp_tier}</div>
</div>""", unsafe_allow_html=True)

# VRP scale bar
st.markdown("""<div class="vrp-bar">
    <div class="vrp-neg">Negative</div>
    <div class="vrp-thin">Thin</div>
    <div class="vrp-norm">Normal</div>
    <div class="vrp-rich">Rich</div>
</div>""", unsafe_allow_html=True)
st.caption("Thresholds: > 5 pts = premium rich, 2–5 = normal, < 2 = thin, < 0 = negative.")

st.markdown("---")

# ==========================================
# SECTION 3: VOLATILITY COMPLEX
# ==========================================

st.markdown("### Volatility Complex")
st.caption("CBOE volatility indices. Sparkline color: red = vol rising, green = vol falling.")

vol_rows = ""
for item in data["vol_complex"]:
    chg = item["change"]
    chg_pct = item["change_pct"]
    cc = change_color(chg)
    sign = "+" if chg >= 0 else ""
    sign_p = "+" if chg_pct >= 0 else ""

    # Simple sparkline using Unicode blocks
    hist = item["history_5d"]
    if len(hist) >= 2:
        trend = hist[-1] - hist[0]
        if trend > 0:
            spark_class = "spark-down"  # vol rising = red for trader
            spark_html = f'<span class="spark-down">▲ rising</span>'
        elif trend < 0:
            spark_html = f'<span class="spark-up">▼ falling</span>'
        else:
            spark_html = f'<span class="spark-flat">— flat</span>'
    else:
        spark_html = ""

    vol_rows += f"""<tr>
        <td><strong>{item['name']}</strong><br><span style="color:#8b949e;font-size:0.8em;">{item['description'][:60]}</span></td>
        <td style="font-weight:600; font-size:1.1em;">{item['current']:.2f}</td>
        <td style="color:{cc};">{sign}{chg:.2f} ({sign_p}{chg_pct:.1f}%)</td>
        <td>{spark_html}</td>
    </tr>"""

st.markdown(f"""<div class="section-card">
    <table class="vol-table">
        <thead><tr><th>Index</th><th>Current</th><th>Change</th><th>5d Trend</th></tr></thead>
        <tbody>{vol_rows}</tbody>
    </table>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECTION 4: EDGE SCORE
# ==========================================

st.markdown("### The Edge — Ratios & Crossovers")
st.caption("5 signals composited into Edge Score (0–100). Green = safe, Red = warning.")

# Edge bar
es = data["edge_score"]
bar_color = edge_bar_color(es)
st.markdown(f"""<div class="edge-bar-bg">
    <div class="edge-bar-fill" style="width:{es}%; background:{bar_color};">{es}/100</div>
</div>""", unsafe_allow_html=True)

# Signal rows
signal_html = ""
for s in data["signals"]:
    badge = f'<span class="badge-safe">{s["value"]}</span>' if s["safe"] else f'<span class="badge-warn">{s["value"]}</span>'
    signal_html += f"""<div class="signal-row">
        <div>
            <div class="signal-name">{s['name']}</div>
            <div class="signal-detail">{s['detail']}</div>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            {badge}
            <div class="signal-score">{s['score']}/{s['max']}</div>
        </div>
    </div>"""

st.markdown(f'<div class="section-card">{signal_html}</div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECTION 5: IMPLIED VOL CURVE
# ==========================================

st.markdown("### Implied Vol Curve (CBOE Indices)")
st.caption("VIX9D → VIX → VIX3M → VIX6M. NOT the VIX futures term structure.")

if data["curve"]:
    cv = data["curve"]
    labels = [p[0] for p in cv["points"]]
    days = [p[1] for p in cv["points"]]
    vals = [p[2] for p in cv["points"]]

    # Interpolated points
    interp_days = []
    interp_vals = []
    for i in range(len(days) - 1):
        mid_day = (days[i] + days[i+1]) / 2
        mid_val = (vals[i] + vals[i+1]) / 2
        interp_days.append(mid_day)
        interp_vals.append(mid_val)

    fig = go.Figure()

    # Interpolated line + small dots
    all_days = []
    all_vals = []
    for i in range(len(days)):
        all_days.append(days[i])
        all_vals.append(vals[i])
        if i < len(interp_days):
            all_days.append(interp_days[i])
            all_vals.append(interp_vals[i])

    fig.add_trace(go.Scatter(
        x=all_days, y=all_vals,
        mode='lines',
        line=dict(color='#58a6ff', width=2.5),
        showlegend=False,
    ))

    # Real data points (large)
    fig.add_trace(go.Scatter(
        x=days, y=vals,
        mode='markers+text',
        marker=dict(color='#58a6ff', size=12, line=dict(color='#fff', width=1.5)),
        text=labels,
        textposition='top center',
        textfont=dict(color='#e6edf3', size=11),
        name='CBOE Indices',
    ))

    # Interpolated dots (small)
    fig.add_trace(go.Scatter(
        x=interp_days, y=interp_vals,
        mode='markers',
        marker=dict(color='#58a6ff', size=5, opacity=0.5),
        showlegend=False,
    ))

    # Historical mean line
    fig.add_hline(
        y=cv["mean"], line=dict(color='#8b949e', width=1, dash='dash'),
        annotation_text=f'Mean ({cv["mean"]:.0f})',
        annotation_position='right',
        annotation_font=dict(color='#8b949e', size=10),
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0d1117',
        plot_bgcolor='#161b22',
        height=350,
        margin=dict(l=50, r=50, t=30, b=50),
        xaxis=dict(
            title='Days',
            gridcolor='#21262d',
            tickvals=days,
            ticktext=labels,
        ),
        yaxis=dict(
            title='Implied Vol',
            gridcolor='#21262d',
        ),
        legend=dict(x=0.02, y=0.98, font=dict(size=10)),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Spreads
    sp1, sp2, sp3 = st.columns(3)
    fc = spread_color(cv["front"])
    bc = spread_color(cv["back"])
    sp1.markdown(f"""<div style="text-align:center; padding:10px;">
        <div style="color:#8b949e; font-size:0.8em;">SHAPE</div>
        <div style="color:#e6edf3; font-size:1.1em; font-weight:600;">{cv['shape']}</div>
    </div>""", unsafe_allow_html=True)
    sp2.markdown(f"""<div style="text-align:center; padding:10px;">
        <div style="color:#8b949e; font-size:0.8em;">FRONT SPREAD (VIX3M − VIX)</div>
        <div style="color:{fc}; font-size:1.3em; font-weight:700;">{cv['front']:+.2f} pts</div>
    </div>""", unsafe_allow_html=True)
    sp3.markdown(f"""<div style="text-align:center; padding:10px;">
        <div style="color:#8b949e; font-size:0.8em;">BACK SPREAD (VIX6M − VIX3M)</div>
        <div style="color:{bc}; font-size:1.3em; font-weight:700;">{cv['back']:+.2f} pts</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECTION 6: PORTFOLIO CALCULATOR
# ==========================================

st.markdown("### Portfolio Calculator")
st.caption("Position sizing based on Net Liquidation Value and current VIX tier.")

nlv_input = st.number_input(
    "Net Liquidation Value ($)", min_value=0.0, value=0.0,
    step=1000.0, format="%.0f",
)

vix_val = data["vix"] if data["vix"] else 20.0

if nlv_input > 0:
    params = VommaEngine.portfolio_params(nlv_input, vix_val)

    pc1, pc2, pc3 = st.columns(3)
    pc1.metric("VIX Tier", params.vix_tier)
    pc2.metric("BP Usage", f"{params.bp_usage_pct:.0f}% (${params.bp_usage_dollar:,.0f})")
    pc3.metric("Capital Reserve", f"{params.capital_reserve_pct:.0f}% (${params.capital_reserve_dollar:,.0f})")

    pd1, pd2, pd3 = st.columns(3)
    pd1.metric("Theta Target", f"${params.theta_min:,.0f} – ${params.theta_max:,.0f} / day")
    pd2.metric("SPY BW Delta Max", f"± ${params.spy_bw_delta:,.0f}")
    pd3.metric("Max Position (Defined)", f"${params.max_pos_defined:,.0f}")

    st.caption(f"Max position undefined risk: ${params.max_pos_undefined:,.0f}")
else:
    st.info("Enter your NLV above to calculate portfolio parameters.")

st.markdown("---")

# ==========================================
# SECTION 7: PORTFOLIO GUIDELINES
# ==========================================

st.markdown("### Portfolio Guidelines")
st.caption("Active row matches current VIX. Higher VIX = more BP allowed (richer premium compensates risk).")

guidelines_df = VommaEngine.guidelines_table(vix_val)

rows_html = ""
for _, row in guidelines_df.iterrows():
    cls = ' class="active-row"' if row["active"] else ""
    rows_html += f"""<tr{cls}>
        <td>{row['VIX Level']}</td>
        <td>{row['BP Usage']}</td>
        <td>{row['Target Theta']}</td>
    </tr>"""

st.markdown(f"""<div class="section-card">
    <table class="vol-table">
        <thead><tr><th>VIX Level</th><th>BP Usage</th><th>Target Theta</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECTION 8: POSITION MANAGEMENT
# ==========================================

st.markdown("### Position Management")
st.caption("Rules for managing open positions. Entry is only half the trade.")

mc1, mc2, mc3 = st.columns(3)

with mc1:
    st.markdown("""<div class="mgmt-card">
        <h4>Profit Taking</h4>
        <div class="mgmt-item">Target: <span class="mgmt-value">50% of max profit</span></div>
        <div class="mgmt-item">Taking profits early avoids gamma risk and builds winning consistency.</div>
    </div>""", unsafe_allow_html=True)

with mc2:
    st.markdown("""<div class="mgmt-card">
        <h4>DTE Discipline</h4>
        <div class="mgmt-item">Entry: <span class="mgmt-value">45 DTE</span></div>
        <div class="mgmt-item">Manage: <span class="mgmt-value">21 DTE</span> (close or roll)</div>
        <div class="mgmt-item">Avoid last week before expiry (gamma risk).</div>
    </div>""", unsafe_allow_html=True)

with mc3:
    st.markdown("""<div class="mgmt-card">
        <h4>Rolling Rules</h4>
        <div class="mgmt-item">1. Roll untested side closer (collect credit)</div>
        <div class="mgmt-item">2. Roll out in time to next month</div>
        <div class="mgmt-item">3. Go inverted / straddle (last resort)</div>
        <div class="mgmt-item" style="margin-top:8px;">Rule: <span class="mgmt-value">Always roll for credit — never debit</span></div>
        <div class="mgmt-item">Win rate: 32% (stop) → <span class="mgmt-value">65% (rolling)</span></div>
    </div>""", unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================

st.markdown("""<div class="footer">
    Alpha Insight — Volatility Cockpit<br>
    Data: Yahoo Finance (CBOE indices) | Refreshes every 2 minutes<br>
    For informational purposes only. Not financial advice.
</div>""", unsafe_allow_html=True)
