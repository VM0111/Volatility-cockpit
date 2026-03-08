import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vomma_engine import VommaEngine

st.set_page_config(page_title="Vomma — Volatility Cockpit", layout="wide", page_icon="📈", initial_sidebar_state="collapsed")

# --- Kopia CSS z HTML Vomma (Light Institutional) ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', system-ui, sans-serif; }
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; max-width: 1280px; }
    
    .v-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .v-card-header { padding: 16px 20px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
    .v-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin: 0; }
    
    .v-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid #f1f5f9; }
    .v-grid-item { padding: 12px 16px; border-right: 1px solid #f1f5f9; }
    .v-grid-item:last-child { border-right: none; }
    .v-grid-lbl { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; color: #94a3b8; }
    .v-grid-val { font-size: 0.875rem; font-weight: 700; margin-top: 4px; }
    
    .text-green { color: #10b981; }
    .text-amber { color: #f59e0b; }
    .text-red { color: #ef4444; }
    
    .alert-box { background: #fef3c7; border: 1px solid #fde68a; padding: 12px 16px; border-radius: 8px; margin: 16px 20px; }
    .alert-title { font-size: 0.75rem; font-weight: 600; color: #d97706; }
    .alert-msg { font-size: 0.7rem; color: #92400e; margin-top: 2px; }
    
    .progress-bg { height: 6px; background: #f1f5f9; border-radius: 999px; overflow: hidden; width: 64px; display: inline-block; margin: 0 8px; vertical-align: middle; }
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
    st.error("Błąd pobierania danych.")
    st.stop()

# --- HEADER Z HTML ---
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px;">
    <div style="display: flex; align-items: center; gap: 16px;">
        <h1 style="font-size: 1.125rem; font-weight: 700; margin: 0; color: #0f172a;">Vomma</h1>
        <div style="height: 16px; width: 1px; background: #e2e8f0;"></div>
        <span style="font-size: 0.75rem; color: #64748b;">Volatility Cockpit</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
        <div style="display: flex; align-items: center; font-size: 0.7rem;">
            <span style="color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Edge</span>
            <div class="progress-bg"><div class="progress-fill" style="width: {edge_score}%; background: {edge_color};"></div></div>
            <strong style="color: {edge_color};">{edge_score}</strong>
        </div>
        <div style="height: 16px; width: 1px; background: #e2e8f0;"></div>
        <div style="display: flex; align-items: center; font-size: 0.7rem;">
            <span style="color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">VIX Rank</span>
            <div class="progress-bg"><div class="progress-fill" style="width: {data.vix_rank}%; background: {vix_rank_color};"></div></div>
            <strong style="color: {vix_rank_color};">{data.vix_rank:.0f}%</strong>
        </div>
        <div style="height: 16px; width: 1px; background: #e2e8f0;"></div>
        <div style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 4px 12px; border-radius: 999px; font-size: 0.7rem; font-weight: 600; color: #059669;">
            {regime_tag}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TRADE TODAY VERDICT ---
if regime == "CONTANGO" and edge_score >= 70 and vrp > 0:
    v_title, v_desc, v_color, v_bg, s_txt = "FAVORABLE", "Favorable — conditions support selling premium", "text-green", "#ecfdf5", "Sell 16Δ strangles at 45 DTE. Use 35% BP. Theta target: 0.1–0.3% NLV/day."
elif edge_score < 40 or signals['Toxic Mix (15 pts)']['status'] == 'Red':
    v_title, v_desc, v_color, v_bg, s_txt = "DEFENSIVE", "Defensive — Toxic Mix active or Edge < 40.", "text-red", "#fef2f2", "No new short-vol, preserve capital."
else:
    v_title, v_desc, v_color, v_bg, s_txt = "CAUTION", "Caution — be selective", "text-amber", "#fefce8", "Smaller size, prefer defined risk (spreads). Take profits at 50%."

alerts_html = ""
for a in alerts:
    alerts_html += f"""<div class="alert-box"><div class="alert-title">{a.split(':')[0]}</div><div class="alert-msg">{a.split(':')[1]}</div></div>"""
if not alerts:
    alerts_html = """<div class="alert-box" style="background:#f8fafc; border-color:#e2e8f0;"><div class="alert-msg" style="color:#64748b;">No active alerts today.</div></div>"""

st.markdown(f"""
<p class="v-title" style="margin-bottom: 8px;">Trade Today?</p>
<div class="v-card">
    <div style="background: {v_bg}; padding: 16px 20px; border-bottom: 1px solid rgba(0,0,0,0.05);">
        <strong class="{v_color}" style="font-size: 0.875rem;">{v_title}</strong>
        <p style="margin: 4px 0 0 0; font-size: 0.75rem; color: #475569;">{v_desc}</p>
    </div>
    <div class="v-grid-4">
        <div class="v-grid-item"><div class="v-grid-lbl">Vol Curve</div><div class="v-grid-val {regime_color}">{"Normal" if regime=="CONTANGO" else "Inverted"}</div></div>
        <div class="v-grid-item"><div class="v-grid-lbl">Edge Score</div><div class="v-grid-val" style="color:{edge_color}">{edge_score}</div></div>
        <div class="v-grid-item"><div class="v-grid-lbl">VRP</div><div class="v-grid-val" style="color:{vrp_color}">+{vrp:.1f}</div></div>
        <div class="v-grid-item"><div class="v-grid-lbl">VIX Rank</div><div class="v-grid-val text-gray">{data.vix_rank:.0f}%</div></div>
    </div>
    <div style="padding: 12px 20px; border-bottom: 1px solid #f1f5f9;">
        <div class="v-grid-lbl" style="margin-bottom: 4px;">Strategy</div>
        <div style="font-size: 0.75rem; color: #0f172a;">{s_txt}</div>
    </div>
    <div style="padding-top: 12px;">
        <div class="v-grid-lbl" style="margin: 0 20px;">Active Alerts</div>
        {alerts_html}
    </div>
</div>
""", unsafe_allow_html=True)

# --- VRP i THE EDGE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"""
    <p class="v-title" style="margin-bottom: 8px;">Volatility Risk Premium (VRP)</p>
    <div class="v-card" style="padding: 20px;">
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:4px;"><span class="v-grid-lbl">Implied (VIX)</span><strong>{data.vix:.1f}</strong></div>
        <div style="background:#f1f5f9; height:8px; border-radius:4px; margin-bottom:12px;"><div style="background:#0f172a; width:100%; height:100%; border-radius:4px;"></div></div>
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:4px;"><span class="v-grid-lbl">Realized (20d SPX)</span><strong>{data.spx_rv_20d:.1f}</strong></div>
        <div style="background:#f1f5f9; height:8px; border-radius:4px; margin-bottom:20px;"><div style="background:#94a3b8; width:70%; height:100%; border-radius:4px;"></div></div>
        <hr style="border:none; border-top:1px solid #f1f5f9; margin: 0 -20px 16px -20px;">
        <div style="display:flex; align-items:baseline; gap:12px;">
            <span class="v-grid-lbl">VRP</span>
            <strong style="font-size:1.5rem; color:{vrp_color};">+{vrp:.1f}</strong>
            <span style="font-size:0.75rem; font-weight:700; color:{vrp_color};">{vrp_state}</span>
        </div>
        <div style="background:#f1f5f9; height:8px; border-radius:4px; margin-top:12px; position:relative; overflow:hidden;">
            <div style="position:absolute; left:0; width:20%; height:100%; background:rgba(239,68,68,0.3);"></div>
            <div style="position:absolute; left:20%; width:20%; height:100%; background:rgba(245,158,11,0.3);"></div>
            <div style="position:absolute; left:40%; width:30%; height:100%; background:rgba(148,163,184,0.3);"></div>
            <div style="position:absolute; left:70%; width:30%; height:100%; background:rgba(16,185,129,0.3);"></div>
            <div style="position:absolute; left:{vrp_pct}%; top:0; bottom:0; width:2px; background:#0f172a;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.55rem; color:#94a3b8; text-transform:uppercase; margin-top:4px;"><span>Negative</span><span>Thin</span><span>Normal</span><span>Rich</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<p class="v-title" style="margin-bottom: 8px;">The Edge — Ratios & Crossovers</p>', unsafe_allow_html=True)
    edge_html = '<div class="v-card" style="padding: 12px 20px;">'
    for k, v in signals.items():
        c = "text-green" if v['status'] == 'Green' else "text-red"
        dot = "🟢" if v['status'] == 'Green' else "🔴"
        edge_html += f"<div style='padding: 8px 0; border-bottom: 1px solid #f1f5f9;'><div style='font-size:0.75rem; font-weight:600;'>{k}</div><div class='{c}' style='font-size:0.7rem; margin-top:2px;'>{dot} {v['msg']}</div></div>"
    edge_html += '</div>'
    st.markdown(edge_html, unsafe_allow_html=True)

# --- VOLATILITY COMPLEX Z SPARKLINE'AMI ---
st.markdown('<p class="v-title" style="margin-bottom: 8px;">Volatility Complex</p>', unsafe_allow_html=True)

complex_tickers = {
    "^VIX": "VIX", "^VVIX": "VVIX", "^VIX9D": "VIX9D", 
    "^VIX3M": "VIX3M", "^VIX6M": "VIX6M", "^SKEW": "SKEW", "^CPC": "P/C Ratio"
}

complex_html = '<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">'
for ticker, name in complex_tickers.items():
    if ticker in data.history:
        curr = data.history[ticker][-1]
        prev = data.history[ticker][-2]
        chg = curr - prev
        pct = (chg/prev)*100 if prev != 0 else 0
        c_color = "#ef4444" if chg > 0 else "#10b981"
        c_class = "text-red" if chg > 0 else "text-green"
        
        # Tworzenie małego wykresu Sparkline do HTML za pomocą prostego SVG (najszybsze w Streamlit)
        hist = data.history[ticker][-5:]
        min_v, max_v = min(hist), max(hist)
        svg_pts = ""
        for i, val in enumerate(hist):
            x = i * 25
            y = 30 - ((val - min_v) / (max_v - min_v + 0.001)) * 30
            svg_pts += f"{x},{y} "
            
        complex_html += f"""
        <div class="v-card" style="margin-bottom:0; padding:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="font-size:0.8rem; font-weight:700;">{name}</span>
                <span style="font-size:0.8rem; font-weight:700;">{curr:.2f}</span>
            </div>
            <svg viewBox="-2 -2 104 34" width="100%" height="30" preserveAspectRatio="none">
                <polyline points="{svg_pts}" fill="none" stroke="{c_color}" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <div class="{c_class}" style="font-size:0.7rem; text-align:right; margin-top:8px;">{chg:+.2f} ({pct:+.1f}%)</div>
        </div>
        """
complex_html += '</div>'
st.markdown(complex_html, unsafe_allow_html=True)

# --- PORTFOLIO CALCULATOR ---
st.markdown('<p class="v-title" style="margin-bottom: 8px;">Portfolio Guidelines</p>', unsafe_allow_html=True)
st.markdown(f"""
<div class="v-card">
    <table style="width:100%; font-size:0.8rem; text-align:left; border-collapse: collapse;">
        <tr style="border-bottom: 1px solid #e2e8f0; color:#64748b;"><th style="padding:12px 20px;">VIX LEVEL</th><th style="padding:12px 20px;">BP USAGE</th><th style="padding:12px 20px;">TARGET THETA</th></tr>
        <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding:12px 20px;">&lt; 15</td><td style="padding:12px 20px;">25%</td><td style="padding:12px 20px;">0.1% NLV</td></tr>
        <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding:12px 20px;">15 – 20</td><td style="padding:12px 20px;">30%</td><td style="padding:12px 20px;">0.1 – 0.2% NLV</td></tr>
        <tr style="background:rgba(16,185,129,0.1); border-left:3px solid #10b981; font-weight:700;"><td style="padding:12px 20px;">20 – 30 (Active)</td><td style="padding:12px 20px;">35%</td><td style="padding:12px 20px;">0.1 – 0.3% NLV</td></tr>
        <tr style="border-bottom: 1px solid #f1f5f9;"><td style="padding:12px 20px;">30 – 40</td><td style="padding:12px 20px;">40%</td><td style="padding:12px 20px;">0.1 – 0.4% NLV</td></tr>
        <tr><td style="padding:12px 20px;">&gt; 40</td><td style="padding:12px 20px;">50%</td><td style="padding:12px 20px;">0.1 – 0.5% NLV</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)
