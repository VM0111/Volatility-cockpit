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
    cpc: float
    spx_rv_20d: float
    vix_rank: float
    history: dict  

class VommaEngine:
    @staticmethod
    def fetch_all_data() -> MarketData:
        tickers = ["^VIX", "^VIX9D", "^VIX3M", "^VIX6M", "^VVIX", "^SKEW", "^GSPC", "^CPC"]
        hist_data = {}
        
        # Pobieranie "kuloodporne" - każdy ticker osobno
        for t in tickers:
            try:
                df = yf.Ticker(t).history(period="1y")
                if not df.empty and 'Close' in df.columns:
                    hist_data[t] = df['Close']
            except Exception:
                pass
                
        if not hist_data:
            raise Exception("API Yahoo Finance nie odpowiada (Brak połączenia).")

        data_1y = pd.DataFrame(hist_data).ffill()
        
        if '^VIX' not in data_1y.columns:
            raise Exception("Brak danych bazowych VIX z Yahoo Finance. API może mieć awarię.")

        current = data_1y.iloc[-1]

        # Bezpieczne wyciąganie danych (Fallback na wypadek braku tickera z Yahoo)
        def safe_get(key, default):
            val = current.get(key, default)
            return float(val) if not pd.isna(val) else default

        vix_val = safe_get('^VIX', 20.0)
        vix9d_val = safe_get('^VIX9D', vix_val)
        vix3m_val = safe_get('^VIX3M', vix_val)
        vix6m_val = safe_get('^VIX6M', vix_val)
        vvix_val = safe_get('^VVIX', 100.0)
        skew_val = safe_get('^SKEW', 130.0)
        cpc_val = safe_get('^CPC', 0.85)

        vix_high = float(data_1y['^VIX'].max())
        vix_low = float(data_1y['^VIX'].min())
        
        if vix_high - vix_low == 0:
            vix_rank = 50.0
        else:
            vix_rank = ((vix_val - vix_low) / (vix_high - vix_low)) * 100

        # Bezpieczne obliczanie Realized Volatility dla S&P 500
        if '^GSPC' in data_1y.columns:
            spx_returns = data_1y['^GSPC'].tail(21).pct_change().dropna()
            spx_rv = float(spx_returns.std() * np.sqrt(252) * 100)
        else:
            spx_rv = vix_val  # Fallback
            
        # Build history from original per-ticker data (not ffilled DataFrame)
        # to avoid duplicate values from forward-fill on missing dates
        safe_history = {}
        for t_key, t_series in hist_data.items():
            clean = t_series.dropna()
            clean = clean[~clean.index.duplicated(keep='last')]
            safe_history[t_key] = clean.tail(6).tolist()

        return MarketData(
            vix=vix_val,
            vix9d=vix9d_val,
            vix3m=vix3m_val,
            vix6m=vix6m_val,
            vvix=vvix_val,
            skew=skew_val,
            cpc=cpc_val,
            spx_rv_20d=spx_rv,
            vix_rank=vix_rank,
            history=safe_history
        )

    @staticmethod
    def calculate_edge(data: MarketData):
        score = 100
        signals = {}
        active_alerts = []

        # 1. VVIX/VIX Ratio (25 pts)
        ratio = data.vvix / data.vix if data.vix > 0 else 0
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
        except Exception:
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

    @staticmethod
    def get_curve_points(data: MarketData):
        spot = data.vix
        m3 = data.vix3m
        m6 = data.vix6m
        m1 = spot + (m3 - spot) * (1/3)
        m2 = spot + (m3 - spot) * (2/3)
        m4 = m3 + (m6 - m3) * (1/3)
        m5 = m3 + (m6 - m3) * (2/3)
        return [spot, m1, m2, m3, m4, m5, m6]
