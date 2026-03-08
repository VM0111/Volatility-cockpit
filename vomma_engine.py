import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
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
    spx_rv_20d: float
    vix_52w_high: float
    vix_52w_low: float
    vix_rank: float
    history: dict  

class VommaEngine:
    @staticmethod
    def fetch_all_data() -> MarketData:
        tickers = ["^VIX", "^VIX9D", "^VIX3M", "^VIX6M", "^VVIX", "^SKEW", "^GSPC"]
        
        # Pobieramy historię 1 rok
        data_1y = yf.download(tickers, period="1y", interval="1d", progress=False)['Close']
        
        # POPRAWKA: Zmiana fillna() na ffill() ze względu na nowe wersje biblioteki Pandas
        data_1y = data_1y.ffill()
        current = data_1y.iloc[-1]
        
        hist_5d = data_1y.tail(5).to_dict('series')
        
        vix_high = float(data_1y['^VIX'].max())
        vix_low = float(data_1y['^VIX'].min())
        
        # Zabezpieczenie przed dzieleniem przez zero
        if vix_high - vix_low == 0:
            vix_rank = 0.0
        else:
            vix_rank = ((float(current['^VIX']) - vix_low) / (vix_high - vix_low)) * 100

        # Realized Volatility (20-dniowa SPX)
        spx_returns = data_1y['^GSPC'].tail(21).pct_change().dropna()
        spx_rv = float(spx_returns.std() * np.sqrt(252) * 100)

        return MarketData(
            vix=float(current['^VIX']),
            vix9d=float(current['^VIX9D']),
            vix3m=float(current['^VIX3M']),
            vix6m=float(current['^VIX6M']),
            vvix=float(current['^VVIX']),
            skew=float(current['^SKEW']),
            spx_rv_20d=spx_rv,
            vix_52w_high=vix_high,
            vix_52w_low=vix_low,
            vix_rank=vix_rank,
            history={k: v.dropna().tolist() for k, v in hist_5d.items()}
        )

    @staticmethod
    def calculate_edge(data: MarketData):
        score = 100
        signals = {}

        ratio = data.vvix / data.vix
        if ratio > 6.0:
            score -= 20
            signals['vvix_vix'] = {"status": "Red", "msg": f"Ratio {ratio:.2f} > 6.0 (Regime risk)"}
        else:
            signals['vvix_vix'] = {"status": "Green", "msg": f"Ratio {ratio:.2f} < 6.0 (Safe)"}

        if data.vix > data.vix3m:
            score -= 20
            signals['slow_cross'] = {"status": "Red", "msg": "VIX > VIX3M (Structural fear)"}
        else:
            signals['slow_cross'] = {"status": "Green", "msg": "VIX < VIX3M (Contango)"}

        if data.vix9d > data.vix:
            score -= 15
            signals['fast_cross'] = {"status": "Red", "msg": "VIX9D > VIX (Panic pricing)"}
        else:
            signals['fast_cross'] = {"status": "Green", "msg": "VIX9D < VIX (Calm)"}

        if data.vix < 16 and data.skew > 130:
            score -= 15
            signals['toxic_mix'] = {"status": "Red", "msg": f"VIX < 16 & SKEW > 130 (Tail risk)"}
        else:
            signals['toxic_mix'] = {"status": "Green", "msg": "No Toxic Mix detected"}

        if data.vix3m > data.vix6m:
            score -= 15
            signals['ultra_slow'] = {"status": "Red", "msg": "VIX3M > VIX6M (Backwardation)"}
        else:
            signals['ultra_slow'] = {"status": "Green", "msg": "VIX3M < VIX6M (Normal)"}

        try:
            vix_change = (data.history['^VIX'][-1] / data.history['^VIX'][-2]) - 1
            vvix_change = (data.history['^VVIX'][-1] / data.history['^VVIX'][-2]) - 1
            if vvix_change > 0.02 and vix_change < 0.01:
                score -= 15
                signals['divergence'] = {"status": "Red", "msg": "VVIX rising, VIX calm"}
            else:
                signals['divergence'] = {"status": "Green", "msg": "No divergence"}
        except:
            signals['divergence'] = {"status": "Green", "msg": "No divergence data"}

        return score, signals

    @staticmethod
    def calculate_vrp(data: MarketData):
        vrp = data.vix - data.spx_rv_20d
        if vrp > 5:
            state = "PREMIUM RICH"
            color = "#10b981" 
        elif vrp > 2:
            state = "NORMAL"
            color = "#3b82f6" 
        elif vrp > 0:
            state = "THIN"
            color = "#f59e0b" 
        else:
            state = "NEGATIVE"
            color = "#ef4444" 
            
        return vrp, state, color

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
