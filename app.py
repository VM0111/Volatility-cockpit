import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vomma_engine import VommaEngine

# --- CONFIG ---
st.set_page_config(page_title="Alpha Volatility Cockpit", layout="wide", page_icon="📈", initial_sidebar_state="collapsed")

# --- INSTITUTIONAL LIGHT THEME CSS ---
st.markdown("""
<style>
    /* Global Tła i Fonty */
    .stApp { background-color: #f4f6f9; color: #111827; font-family: 'Inter', 'Helvetica Neue', sans-serif; }
    
    /* Ukrycie standardowych elementów Streamlit */
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; max-width: 1400px; }
    
    /* Karty i sekcje */
    .card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .card-title { font-size: 1.1rem; font-weight: 600; color: #374151; margin-bottom: 15px; border-bottom: 1px solid #f3f4f6; padding-bottom: 10px; }
    
    /* Header Główny */
    .main-header { display: flex; justify-content: space-between; background: #ffffff; padding: 20px; border: 1px solid #e5e7eb; border-radius: 6px; margin-bottom: 20px;}
    .stat-box { text-align: center; padding: 0 20px; border-right: 1px solid #e5e7eb; }
    .stat-box:last-child { border-right: none; }
    .stat-val { font-size: 2rem; font-weight: 700; color: #111827; }
    .stat-lbl { font-size: 0.85rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Kolory statusów */
    .text-green { color: #10b981 !important; font-weight: 600;}
    .text-red { color: #ef4444 !important; font-weight: 600;}
    .text-gray { color: #6b7280; }
    
    /* Tabele */
    .custom-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .custom-table th { text-align: left; padding: 8px; border-bottom: 2px solid #e5e7eb; color: #4b5563; }
    .custom-table td { padding: 10px 8px; border-bottom: 1px solid #f3f4f6; }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data(ttl=60)
def load_data():
    return VommaEngine.fetch_all_data()

try:
    data = load_data()
    edge_score, signals = VommaEngine.calculate_edge(data)
    vrp, vrp_state, vrp_color = VommaEngine.calculate_vrp(data)
    regime = "CONTANGO" if data.vix < data.vix3m else "BACKWARDATION"
    regime_color = "text-green" if regime == "CONTANGO" else "text-red"
except Exception as e:
    st.error(f"Błąd pobierania danych z rynku. Odśwież stronę. ({e})")
    st.stop()

# --- VERDICT LOGIC ---
if regime == "CONTANGO" and edge_score >= 70 and vrp > 0:
    verdict = "FAVORABLE"
    verdict_desc = "Favorable — conditions support selling premium."
    strategy_msg = "Sell 16Δ strangles at 45 DTE. Use 35% BP. Theta target: 0.1–0.3% NLV/day."
elif edge_score < 40 or signals['toxic_mix']['status'] == 'Red':
    verdict = "DEFENSIVE"
    verdict_desc = "Defensive — Toxic Mix active or Edge < 40. No new short-vol, preserve capital."
    strategy_msg = "Do not deploy new capital. Manage existing positions. Consider tail-hedging."
else:
    verdict = "CAUTION"
    verdict_desc = "Caution — Mixed signals. Reduce size, prefer defined risk."
    strategy_msg = "Trade Iron Condors or Jade Lizards. Keep BP under 25%."

# --- HEADER SECTION ---
st.markdown(f"""
<div class="main-header">
    <div style="flex: 2;">
        <h2 style="margin:0; font-size: 1.5rem;">Alpha Volatility Cockpit</h2>
        <div style="color: #6b7280; font-size: 0.9rem; margin-top: 5px;">Synthesizes all edge signals into a single actionable verdict.</div>
    </div>
    <div class="stat-box">
        <div class="stat-lbl">Edge Score</div>
        <div class="stat-val {'text-green' if edge_score >= 70 else 'text-red'}">{edge_score}</div>
    </div>
    <div class="stat-box">
        <div class="stat-lbl">VIX Rank</div>
        <div class="stat-val">{data.vix_rank:.0f}%</div>
    </div>
    <div class="stat-box">
        <div class="stat-lbl">Regime</div>
        <div class="stat-val {regime_color}">{regime}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- VERDICT ALERT ---
st.info(f"**{verdict}** — {verdict_desc} \n\n**Strategy:** {strategy_msg}")

col1, col2 = st.columns([1, 1])

# --- VOLATILITY RISK PREMIUM (VRP) ---
with col1:
    st.markdown("""<div class="card"><div class="card-title">Volatility Risk Premium (VRP)</div>""", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.9rem; color:#4b5563;'>VRP = VIX − Realized Vol. The structural reason premium selling works.</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <table class="custom-table" style="margin-top: 20px;">
        <tr><td>Implied (VIX)</td><td style="text-align:right; font-weight:bold;">{data.vix:.1f}</td></tr>
        <tr><td>Realized (20d SPX)</td><td style="text-align:right; font-weight:bold;">{data.spx_rv_20d:.1f}</td></tr>
        <tr><td style="font-weight:bold;">VRP</td><td style="text-align:right; font-weight:bold; color:{vrp_color};">+{vrp:.1f} ({state})</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

# --- THE EDGE - RATIOS & CROSSOVERS ---
with col2:
    st.markdown("""<div class="card"><div class="card-title">The Edge — Ratios & Crossovers</div>""", unsafe_allow_html=True)
    
    html_signals = "<table class='custom-table'>"
    for key, info in signals.items():
        color_class = "text-green" if info['status'] == "Green" else "text-red"
        symbol = "🟢" if info['status'] == "Green" else "🔴"
        name = key.replace('_', ' ').title()
        html_signals += f"<tr><td>{name}</td><td class='{color_class}'>{symbol} {info['msg']}</td></tr>"
    html_signals += "</table></div>"
    st.markdown(html_signals, unsafe_allow_html=True)

# --- VIX TERM STRUCTURE ---
st.markdown("""<div class="card"><div class="card-title">VIX Term Structure</div>""", unsafe_allow_html=True)

points = VommaEngine.get_curve_points(data)
labels = ['Spot', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6']

front_spread = data.vix3m - data.vix
back_spread = data.vix6m - data.vix3m

st.markdown(f"""
<div style="display:flex; justify-content: space-around; margin-bottom: 20px; font-size: 0.95rem;">
    <div><b>Front Spread (VIX3M - Spot):</b> <span class="{'text-green' if front_spread > 0 else 'text-red'}">{front_spread:+.2f} pts</span></div>
    <div><b>Back Spread (VIX6M - VIX3M):</b> <span class="{'text-green' if back_spread > 0 else 'text-red'}">{back_spread:+.2f} pts</span></div>
</div>
""", unsafe_allow_html=True)

fig = go.Figure()
# Interpolated lines (smaller dots)
fig.add_trace(go.Scatter(x=labels, y=points, mode='lines+markers', 
                         line=dict(color='#3b82f6', width=3), 
                         marker=dict(size=8, color='#3b82f6'), name='Curve'))

# Anchor points (Spot, M3, M6) - larger dots
anchors_x = ['Spot', 'M3', 'M6']
anchors_y = [data.vix, data.vix3m, data.vix6m]
fig.add_trace(go.Scatter(x=anchors_x, y=anchors_y, mode='markers', 
                         marker=dict(size=14, color='#1e3a8a', line=dict(width=2, color='white')), showlegend=False))

# Historical Mean Line (19.0)
fig.add_hline(y=19.0, line_dash="dash", line_color="#9ca3af", annotation_text="Historical Mean (19.0)", annotation_position="bottom right")

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    height=350, margin=dict(t=10, b=10, l=10, r=10),
    yaxis=dict(gridcolor='#e5e7eb'), xaxis=dict(gridcolor='#e5e7eb')
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- PORTFOLIO CALCULATOR & GUIDELINES ---
col3, col4 = st.columns([1, 1.5])

with col3:
    st.markdown("""<div class="card"><div class="card-title">Portfolio Calculator</div>""", unsafe_allow_html=True)
    nlv = st.number_input("Net Liquidation Value ($)", value=100000, step=5000)
    
    if data.vix < 15: bp_pct = 0.25; th_tgt = 0.001
    elif data.vix < 20: bp_pct = 0.30; th_tgt = 0.0015
    elif data.vix < 30: bp_pct = 0.35; th_tgt = 0.0025
    elif data.vix < 40: bp_pct = 0.40; th_tgt = 0.0035
    else: bp_pct = 0.50; th_tgt = 0.005
        
    st.markdown(f"""
    <table class="custom-table" style="margin-top: 15px;">
        <tr><td>BP Usage limit</td><td style="text-align:right; font-weight:bold;">{bp_pct*100:.0f}% (${nlv*bp_pct:,.0f})</td></tr>
        <tr><td>Theta Target/Day</td><td style="text-align:right; font-weight:bold;">{th_tgt*100:.2f}% (${nlv*th_tgt:,.0f})</td></tr>
        <tr><td>Max Position (Defined)</td><td style="text-align:right; font-weight:bold;">5% (${nlv*0.05:,.0f})</td></tr>
        <tr><td>SPY BW Delta Limit</td><td style="text-align:right; font-weight:bold;">±0.15%</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""<div class="card"><div class="card-title">Position Management</div>
    <div style="display: flex; gap: 20px;">
        <div style="flex:1;">
            <b>Profit Taking</b><br>
            <span class="text-gray">Target: 50% of max profit. Captures most edge, avoids rising gamma risk.</span>
        </div>
        <div style="flex:1;">
            <b>DTE Discipline</b><br>
            <span class="text-gray">Entry: 45 DTE<br>Manage: 21 DTE (close or roll).</span>
        </div>
        <div style="flex:1;">
            <b>Rolling</b><br>
            <span class="text-gray">Always roll for a credit — never debit. Roll untested side closer.</span>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
