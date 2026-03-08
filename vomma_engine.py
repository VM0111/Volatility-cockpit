import yfinance as yf
import pandas as pd
import numpy as np
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')

@dataclass
class MarketData:
    vix: float
    vix9d: float
    vix3m: float
    vix6m: float
    vvix: float
    skew: float
    cpc: float  # Put/Call Ratio
    spx_rv_20d: float
    vix_rank: float
    history: dict  

class VommaEngine:
    @staticmethod
    def fetch_all_data() -> MarketData:
        # ^CPC to CBOE Put/Call Ratio. VIXEQ jest bardzo trudno dostępne w darmowym YF, 
        # więc zabezpieczamy się w kodzie.
        tickers = ["^VIX", "^VIX9D", "^VIX3M", "^VIX6M", "^VVIX", "^SKEW", "^GSPC", "^CPC"]
        
        data_1y = yf.download(tickers, period="1y", interval="1d", progress=False)['Close']
        data_1y = data_1y.ffill()
        
        current = data_1y.iloc[-1]
        hist_5d = data_1y.tail(6).to_dict('series') # 6 dni, by mieć 5 dni zmian
        
        vix_high = float(data_1y['^VIX'].max())
        vix_low = float(data_1y['^VIX'].min())
        
        if vix_high - vix_low == 0:
            vix_rank = 50.0
        else:
            vix_rank = ((float(current['^VIX']) - vix_low) / (vix_high - vix_low)) * 100

        spx_returns = data_1y['^GSPC'].tail(21).pct_change().dropna()
        spx_rv = float(spx_returns.std() * np.sqrt(252) * 100)

        # Pobieranie P/C ratio z zabezpieczeniem (czasami YF gubi te dane)
        cpc_val = float(current['^CPC']) if '^CPC' in current and not pd.isna(current['^CPC']) else 0.85

        return MarketData(
            vix=float(current['^VIX']),
            vix9d=float(current['^VIX9D']),
            vix3m=float(current['^VIX3M']),
            vix6m=float(current['^VIX6M']),
            vvix=float(current['^VVIX']),
            skew=float(current['^SKEW']),
            cpc=cpc_val,
            spx_rv_20d=spx_rv,
            vix_rank=vix_rank,
            history={k: v.dropna().tolist() for k, v in hist_5d.items()}
        )

    @staticmethod
    def calculate_edge(data: MarketData):
        # DOKŁADNE WAGI Z KODU HTML VOMMA (Max 100)
        score = 100
        signals = {}
        active_alerts = []

        # 1. VVIX/VIX Ratio (25 pts)
        ratio = data.vvix / data.vix
        if ratio > 6.0:
            score -= 25
            signals['VVIX/VIX Ratio (25 pts)'] = {"status": "Red", "msg": "Vol-of-vol relative to vol. >6 = regime change risk."}
            active_alerts.append("VVIX/VIX > 6.0: Institutions buying protection.")
        else:
            signals['VVIX/VIX Ratio (25 pts)'] = {"status": "Green", "msg": f"Ratio {ratio:.1f} < 6.0 = Safe"}

        # 2. Slow Crossover (25 pts)
        if data.vix > data.vix3m:
            score -= 25
            signals['Slow Crossover (25 pts)'] = {"status": "Red", "msg": "VIX > VIX3M. Deep structural fear."}
            active_alerts.append("Slow Crossover (VIX > VIX3M): Structural Backwardation.")
        else:
            signals['Slow Crossover (25 pts)'] = {"status": "Green", "msg": "VIX < VIX3M. Normal Contango."}

        # 3. Fast Crossover (20 pts)
        if data.vix9d > data.vix:
            score -= 20
            signals['Fast Crossover (20 pts)'] = {"status": "Red", "msg": "VIX9D > VIX. Short-term panic pricing."}
            active_alerts.append("Fast Crossover (VIX9D > VIX): Don't trade aggressively today. Take profits.")
        else:
            signals['Fast Crossover (20 pts)'] = {"status": "Green", "msg": "VIX9D < VIX. Calm short-term."}

        # 4. Toxic Mix (15 pts)
        if data.vix < 16 and data.skew > 130:
            score -= 15
            signals['Toxic Mix (15 pts)'] = {"status": "Red", "msg": "VIX < 16 AND SKEW > 130 = Hidden tail risk."}
            active_alerts.append("Toxic Mix Active: No new short-vol, preserve capital.")
        else:
            signals['Toxic Mix (15 pts)'] = {"status": "Green", "msg": "No Toxic Mix detected."}

        # 5. VVIX Divergence (15 pts)
        try:
            vix_change = (data.history['^VIX'][-1] / data.history['^VIX'][-2]) - 1
            vvix_change = (data.history['^VVIX'][-1] / data.history['^VVIX'][-2]) - 1
            if vvix_change > 0.02 and vix_change < 0.01:
                score -= 15
                signals['VVIX Divergence (15 pts)'] = {"status": "Red", "msg": "VVIX rising while VIX stays calm."}
            else:
                signals['VVIX Divergence (15 pts)'] = {"status": "Green", "msg": "No divergence."}
        except:
            signals['VVIX Divergence (15 pts)'] = {"status": "Green", "msg": "No divergence data."}

        return score, signals, active_alerts

    @staticmethod
    def calculate_vrp(data: MarketData):
        vrp = data.vix - data.spx_rv_20d
        if vrp > 5:
            state, color, pct = "PREMIUM RICH", "#10b981", 90
        elif vrp > 2:
            state, color, pct = "NORMAL", "#3b82f6", 65
        elif vrp > 0:
            state, color, pct = "THIN", "#f59e0b", 35
        else:
            state, color, pct = "NEGATIVE", "#ef4444", 10
        return vrp, state, color, pct
