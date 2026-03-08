import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vomma_engine import VommaEngine

st.set_page_config(page_title="Alpha Volatility Cockpit", layout="wide", page_icon="📈", initial_sidebar_state="collapsed")

# --- PANCERNY CSS ---
st.markdown("""
<style>
.stApp { background-color: #f8fafc !important; color: #0f172a !important; font-family: 'Inter', system-ui, sans-serif; }
header {visibility: hidden;}
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
.v-card { 
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); color: #0f172a !important; margin-bottom: 1rem;
}
.v-title { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b !important; margin-bottom: 12px; }
.text-green { color: #10b981 !important; font-weight: 600; }
.text-amber { color: #f59e0b !important; font-weight: 600; }
.text-red { color: #ef4444 !important; font-weight: 600; }
.text-gray { color: #64748b !important; font-weight: 600; }
.progress-bg { height: 6px; background: #e2e8f0; border-radius: 999px; overflow: hidden; width: 64px; display: inline-block; vertical-align: middle; margin: 0 8px; }
.progress-fill { height: 100%; border-radius: 999px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    return VommaEngine.fetch_all_data()

try:
    data = load_data()
    edge_score, signals, alerts = VommaEngine.calculate_edge(data)
    vrp, vrp_state, vrp_color, vrp_pct = VommaEngine.calculate_vrp(data)
    
    regime = "CONTANGO" if data.vix < data.vix3m else "BACKWARDATION"
    regime_tag = f"NORMAL (VIX < VIX3M)" if regime == "CONTANGO" else "INVERTED (VIX > VIX3M)"
    regime_color = "text-green" if regime == "CONTANGO" else "text-red"
    
    vix_rank_color = "#f59e0b" if 30 <= data.vix_rank <= 60 else ("#ef4444" if data.vix_rank > 60 else "#10b981")
    edge_color = "#10b981" if edge_score >= 70 else ("#f59e0b" if edge_score >= 40 else "#ef4444")
except Exception as e:
    st.error(f"Błąd silnika: {str(e)}")
    st.stop()

# ==========================================
# HEADER
# ==========================================
h_col1, h_col2 = st.columns([1, 1])
with h_col1:
    st.markdown("<div style='display:flex; align-items:center; gap:16px;'><h1 style='margin:0; font-size:1.5rem; color:#0f172a !important;'>Alpha</h1><div style='height:24px; width:1px; background:#e2e8f0;'></div><span style='color:#64748b !important; font-weight:500;'>Volatility Cockpit</span></div>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"""
<div style='display:flex; justify-content:flex-end; align-items:center; gap:16px;'>
    <div style='font-size:0.75rem;'><span style='color:#64748b !important; text-transform:uppercase;'>Edge</span>
        <div class='progress-bg'><div class='progress-fill' style='width:{edge_score}%; background:{edge_color};'></div></div><strong style='color:{edge_color}; font-size:0.9rem;'>{edge_score}</strong>
    </div>
    <div style='font-size:0.75rem;'><span style='color:#64748b !important; text-transform:uppercase;'>VIX Rank</span>
        <div class='progress-bg'><div class='progress-fill' style='width:{data.vix_rank}%; background:{vix_rank_color};'></div></div><strong style='color:{vix_rank_color}; font-size:0.9rem;'>{data.vix_rank:.0f}%</strong>
    </div>
    <div style='background:#ecfdf5; border:1px solid #a7f3d0; padding:4px 12px; border-radius:999px; font-size:0.75rem; font-weight:700; color:#059669 !important;'>{regime_tag}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin-top:10px; margin-bottom:20px; border-color:#e2e8f0;'>", unsafe_allow_html=True)

# ==========================================
# TRADE TODAY?
# ==========================================
st.markdown('<div class="v-title">Trade Today?</div>', unsafe_allow_html=True)

if regime == "CONTANGO" and edge_score >= 70 and vrp > 0:
    v_title, v_desc, v_color, v_bg = "FAVORABLE", "Favorable — conditions support selling premium", "text-green", "#ecfdf5"
    s_txt = "Sell 16Δ strangles at 45 DTE. Use 35% BP. Theta target: 0.1–0.3% NLV/day."
elif edge_score < 40 or signals['Toxic Mix (15 pts)']['status'] == 'Red':
    v_title, v_desc, v_color, v_bg = "DEFENSIVE", "Defensive — Toxic Mix active or Edge < 40.", "text-red", "#fef2f2"
    s_txt = "No new short-vol, preserve capital."
else:
    v_title, v_desc, v_color, v_bg = "CAUTION", "Caution — Mixed signals. Reduce size.", "text-amber", "#fefce8"
    s_txt = "Smaller size, prefer defined risk (spreads). Take profits at 50%."

alerts_html = ""
for a in alerts:
    parts = a.split(':', 1)
    title = parts[0]
    msg = parts[1] if len(parts)>1 else ""
    alerts_html += f"<div style='background:#fef3c7; border:1px solid #fde68a; padding:8px 12px; border-radius:6px; margin-top:8px;'><strong style='color:#d97706; font-size:0.8rem;'>{title}</strong><div style='color:#92400e; font-size:0.75rem;'>{msg}</div></div>"
if not alerts:
    alerts_html = "<div style='color:#64748b; font-size:0.8rem; margin-top:8px;'>No active alerts today.</div>"

st.markdown(f"""
<div class="v-card" style="padding:0;">
<div style="background:{v_bg}; padding:16px 20px; border-bottom:1px solid #e2e8f0;">
    <strong class="{v_color}" style="font-size:1rem;">{v_title}</strong><div style="font-size:0.8rem; color:#475569 !important;">{v_desc}</div>
</div>
<div style="display:flex; justify-content:space-between; padding:16px 20px; border-bottom:1px solid #e2e8f0; background:white;">
    <div><div style="font-size:0.7rem; color:#94a3b8 !important; text-transform:uppercase;">Vol Curve</div><div class="{regime_color}">{"Normal" if regime=="CONTANGO" else "Inverted"}</div></div>
    <div><div style="font-size:0.7rem; color:#94a3b8 !important; text-transform:uppercase;">Edge Score</div><div style="color:{edge_color}; font-weight:bold;">{edge_score}</div></div>
    <div><div style="font-size:0.7rem; color:#94a3b8 !important; text-transform:uppercase;">VRP</div><div style="color:{vrp_color}; font-weight:bold;">+{vrp:.1f}</div></div>
    <div><div style="font-size:0.7rem; color:#94a3b8 !important; text-transform:uppercase;">VIX Rank</div><div class="text-gray">{data.vix_rank:.0f}%</div></div>
</div>
<div style="padding:16px 20px; border-bottom:1px solid #e2e8f0; background:white;">
    <div style="font-size:0.7rem; color:#94a3b8 !important; text-transform:uppercase; margin-bottom:4px;">Strategy</div>
    <div style="font-size:0.85rem; color:#0f172a !important;">{s_txt}</div>
</div>
<div style="padding:16px 20px; background:white;">
    <div style="font-size:0.7rem; color:#94a3b8 !important; text-transform:uppercase;">Active Alerts</div>
    {alerts_html}
</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# VRP & THE EDGE
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="v-title">Volatility Risk Premium (VRP)</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="v-card">
<div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px; color:#64748b !important;"><span>Implied (VIX)</span><strong style="color:#0f172a !important;">{data.vix:.1f}</strong></div>
<div style="background:#f1f5f9; height:8px; border-radius:4px; margin-bottom:12px;"><div style="background:#0f172a; width:100%; height:100%; border-radius:4px;"></div></div>
<div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px; color:#64748b !important;"><span>Realized (20d SPX)</span><strong style="color:#0f172a !important;">{data.spx_rv_20d:.1f}</strong></div>
<div style="background:#f1f5f9; height:8px; border-radius:4px; margin-bottom:20px;"><div style="background:#94a3b8; width:70%; height:100%; border-radius:4px;"></div></div>
<hr style="border-color:#f1f5f9;">
<div style="display:flex; align-items:baseline; gap:12px;">
    <span style="font-size:0.8rem; color:#64748b !important;">VRP</span>
    <strong style="font-size:1.5rem; color:{vrp_color};">+{vrp:.1f}</strong>
    <span style="font-size:0.8rem; font-weight:700; color:{vrp_color};">{vrp_state}</span>
</div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="v-title">The Edge — Ratios & Crossovers</div>', unsafe_allow_html=True)
    edge_html = '<div class="v-card">'
    for k, v in signals.items():
        c = "text-green" if v['status'] == 'Green' else "text-red"
        dot = "🟢" if v['status'] == 'Green' else "🔴"
        edge_html += f"<div style='padding:6px 0; border-bottom:1px solid #f1f5f9;'><div style='font-size:0.8rem; font-weight:600; color:#0f172a !important;'>{k}</div><div class='{c}' style='font-size:0.75rem; margin-top:2px;'>{dot} {v['msg']}</div></div>"
    edge_html += '</div>'
    st.markdown(edge_html, unsafe_allow_html=True)

# ==========================================
# VOLATILITY COMPLEX (Tu był błąd wcięć!)
# ==========================================
st.markdown('<div class="v-title">Volatility Complex</div>', unsafe_allow_html=True)
complex_tickers = [("^VIX", "VIX"), ("^VVIX", "VVIX"), ("^VIX9D", "VIX9D"), ("^VIX3M", "VIX3M"), ("^VIX6M", "VIX6M"), ("^SKEW", "SKEW"), ("^CPC", "P/C Ratio")]

cols = st.columns(4)
for i, (ticker, name) in enumerate(complex_tickers):
    if ticker in data.history and len(data.history[ticker]) > 1:
        hist = data.history[ticker]
        curr = hist[-1]
        prev = hist[-2]
        chg = curr - prev
        pct = (chg/prev)*100 if prev != 0 else 0
        
        c_color = "#ef4444" if chg > 0 else "#10b981"
        c_class = "text-red" if chg > 0 else "text-green"
        
        min_v, max_v = min(hist), max(hist)
        diff = max_v - min_v if max_v != min_v else 1 
        
        svg_pts = ""
        for j, val in enumerate(hist):
            x = j * (100 / (len(hist)-1))
            y = 30 - ((val - min_v) / diff) * 30
            svg_pts += f"{x},{y} "
            
        card_html = f"""<div class="v-card" style="padding:12px;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
<span style="font-size:0.8rem; font-weight:700; color:#0f172a !important;">{name}</span>
<span style="font-size:0.8rem; font-weight:700; color:#0f172a !important;">{curr:.2f}</span>
</div>
<svg viewBox="-2 -2 104 34" width="100%" height="25" preserveAspectRatio="none">
<polyline points="{svg_pts}" fill="none" stroke="{c_color}" stroke-width="2" stroke-linecap="round"/>
</svg>
<div class="{c_class}" style="font-size:0.75rem; text-align:right; margin-top:4px;">{chg:+.2f} ({pct:+.1f}%)</div>
</div>"""
        cols[i % 4].markdown(card_html, unsafe_allow_html=True)

# ==========================================
# TERM STRUCTURE
# ==========================================
st.markdown('<div class="v-title" style="margin-top:16px;">Implied Vol Curve (CBOE Indices)</div>', unsafe_allow_html=True)
points = VommaEngine.get_curve_points(data)
labels = ['Spot', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6']
front_spread = data.vix3m - data.vix
back_spread = data.vix6m - data.vix3m

fig = go.Figure()
fig.add_trace(go.Scatter(x=labels, y=points, mode='lines+markers', line=dict(color='#3b82f6', width=3), marker=dict(size=6, color='#3b82f6'), showlegend=False))
anchors_x = ['Spot', 'M3', 'M6']
anchors_y = [data.vix, data.vix3m, data.vix6m]
fig.add_trace(go.Scatter(x=anchors_x, y=anchors_y, mode='markers', marker=dict(size=12, color='#1e3a8a', line=dict(width=2, color='white')), showlegend=False))
fig.add_hline(y=19.0, line_dash="dash", line_color="#9ca3af", annotation_text="Historical Mean (19.0)", annotation_position="bottom right")
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=320, margin=dict(t=20, b=20, l=10, r=10), yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a')), xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#0f172a')))

st.markdown(f"""
<div class="v-card" style="padding:0;">
<div style="padding:12px 20px; border-bottom:1px solid #e2e8f0; display:flex; gap:32px; font-size: 0.8rem;">
    <div><b style="color:#64748b !important;">Front Spread (VIX3M - Spot):</b> <span class="{'text-green' if front_spread > 0 else 'text-red'}">{front_spread:+.2f} pts</span></div>
    <div><b style="color:#64748b !important;">Back Spread (VIX6M - VIX3M):</b> <span class="{'text-green' if back_spread > 0 else 'text-red'}">{back_spread:+.2f} pts</span></div>
</div>
</div>
""", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# PORTFOLIO GUIDELINES
# ==========================================
st.markdown('<div class="v-title" style="margin-top:16px;">Portfolio Guidelines</div>', unsafe_allow_html=True)
st.markdown("""
<div class="v-card" style="padding:0; overflow-x:auto;">
<table style="width:100%; font-size:0.85rem; text-align:left; border-collapse: collapse; color:#0f172a !important;">
    <tr style="border-bottom: 1px solid #e2e8f0; color:#64748b !important;"><th style="padding:12px 20px;">VIX LEVEL</th><th style="padding:12px 20px;">BP USAGE</th><th style="padding:12px 20px;">TARGET THETA</th></tr>
    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding:12px 20px;">&lt; 15</td><td style="padding:12px 20px;">25%</td><td style="padding:12px 20px;">0.1% NLV</td></tr>
    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding:12px 20px;">15 – 20</td><td style="padding:12px 20px;">30%</td><td style="padding:12px 20px;">0.1 – 0.2% NLV</td></tr>
    <tr style="background:#ecfdf5; border-left:4px solid #10b981; font-weight:700;"><td style="padding:12px 20px;">20 – 30 (Active)</td><td style="padding:12px 20px;">35%</td><td style="padding:12px 20px;">0.1 – 0.3% NLV</td></tr>
    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding:12px 20px;">30 – 40</td><td style="padding:12px 20px;">40%</td><td style="padding:12px 20px;">0.1 – 0.4% NLV</td></tr>
    <tr><td style="padding:12px 20px;">&gt; 40</td><td style="padding:12px 20px;">50%</td><td style="padding:12px 20px;">0.1 – 0.5% NLV</td></tr>
</table>
</div>
""", unsafe_allow_html=True)
