"""
Vomma-style Volatility Cockpit Engine
Backend: data fetch, VRP, Edge Score, Vol Curve, Portfolio Calculator.
All data from Yahoo Finance (CBOE indices).
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# CBOE indices on Yahoo Finance
TICKERS = {
    "^VIX": "VIX",
    "^VIX9D": "VIX9D",
    "^VIX3M": "VIX3M",
    "^VIX6M": "VIX6M",
    "^VVIX": "VVIX",
    "^SKEW": "SKEW",
    "^GSPC": "SPX",
}

TICKER_DESCRIPTIONS = {
    "VIX": "30-day implied vol of S&P 500. The main fear gauge.",
    "VIX9D": "9-day implied vol. Reacts fastest to sudden events.",
    "VIX3M": "3-month implied vol. Structural trend indicator.",
    "VIX6M": "6-month implied vol. Long-term market expectations.",
    "VVIX": "Volatility of VIX options. Uncertainty about future VIX.",
    "SKEW": "Tail risk asymmetry. High = market pricing crash risk.",
    "SPX": "S&P 500 index. Used for realized vol calculation.",
}

# ==========================================
# DATA MODELS
# ==========================================

@dataclass
class IndexData:
    name: str
    current: float
    prev_close: float
    change: float
    change_pct: float
    history_5d: list  # last 5 closes for sparkline
    description: str = ""


@dataclass
class EdgeSignal:
    name: str
    max_points: int
    score: int
    is_safe: bool
    value_str: str
    detail: str


@dataclass
class TradeVerdict:
    verdict: str  # FAVORABLE / CAUTION / DEFENSIVE
    strategy: str
    alerts: list


@dataclass
class VolCurveData:
    shape: str  # Normal / Inverted / Partial Inversion
    points: list  # [(label, days, value), ...]
    front_spread: float  # VIX3M - VIX
    back_spread: float  # VIX6M - VIX3M
    historical_mean: float  # ~19


@dataclass
class PortfolioParams:
    nlv: float
    vix_tier: str
    bp_usage_pct: float
    bp_usage_dollar: float
    theta_min: float
    theta_max: float
    spy_bw_delta: float
    max_pos_defined: float
    max_pos_undefined: float
    capital_reserve_pct: float
    capital_reserve_dollar: float


# ==========================================
# ENGINE
# ==========================================

class VommaEngine:
    """Fetches CBOE vol data and computes all dashboard metrics."""

    def __init__(self):
        self.raw_data: Dict[str, pd.DataFrame] = {}
        self.index_data: Dict[str, IndexData] = {}
        self.vix = None
        self.vix9d = None
        self.vix3m = None
        self.vix6m = None
        self.vvix = None
        self.skew = None
        self.spx_data = None

    def fetch_all(self) -> bool:
        """Fetch all indices. Returns True on success."""
        success_count = 0

        for yf_ticker, name in TICKERS.items():
            try:
                df = yf.download(
                    yf_ticker, period="1y", auto_adjust=True,
                    progress=False, timeout=15,
                )
                if df is None or df.empty:
                    logger.warning(f"Empty data for {yf_ticker}")
                    continue

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                if 'Close' not in df.columns:
                    continue

                self.raw_data[name] = df
                success_count += 1

            except Exception as e:
                logger.warning(f"Failed to fetch {yf_ticker}: {e}")

        if success_count < 3:
            return False

        # Extract current values
        self._extract_index_data()
        return True

    def _extract_index_data(self):
        """Build IndexData for each index from raw DataFrames."""
        for name, df in self.raw_data.items():
            if name == "SPX":
                self.spx_data = df
                continue

            closes = df['Close'].dropna()
            if len(closes) < 2:
                continue

            current = float(closes.iloc[-1])
            prev = float(closes.iloc[-2])
            change = current - prev
            change_pct = (change / prev) * 100 if prev != 0 else 0

            hist_5d = closes.tail(5).tolist()

            self.index_data[name] = IndexData(
                name=name,
                current=current,
                prev_close=prev,
                change=change,
                change_pct=change_pct,
                history_5d=hist_5d,
                description=TICKER_DESCRIPTIONS.get(name, ""),
            )

        # Set convenience attributes
        self.vix = self.index_data.get("VIX")
        self.vix9d = self.index_data.get("VIX9D")
        self.vix3m = self.index_data.get("VIX3M")
        self.vix6m = self.index_data.get("VIX6M")
        self.vvix = self.index_data.get("VVIX")
        self.skew = self.index_data.get("SKEW")

    # ---- REALIZED VOL ----

    def realized_vol_20d(self) -> Optional[float]:
        """20-day realized vol of SPX, annualized, in vol points (like VIX)."""
        if self.spx_data is None:
            return None
        closes = self.spx_data['Close'].dropna()
        if len(closes) < 21:
            return None
        log_ret = np.log(closes / closes.shift(1)).dropna()
        rv = float(log_ret.tail(20).std() * np.sqrt(252) * 100)
        return round(rv, 2)

    # ---- VRP ----

    def vrp(self) -> Optional[float]:
        """VRP = VIX - Realized Vol (20d)."""
        rv = self.realized_vol_20d()
        if rv is None or self.vix is None:
            return None
        return round(self.vix.current - rv, 2)

    def vrp_tier(self, vrp_val: float) -> str:
        if vrp_val > 5:
            return "PREMIUM RICH"
        elif vrp_val >= 2:
            return "NORMAL"
        elif vrp_val >= 0:
            return "THIN"
        else:
            return "NEGATIVE"

    # ---- VIX RANK ----

    def vix_rank(self) -> Optional[Tuple[float, str]]:
        """VIX percentile rank over last 252 trading days."""
        if "VIX" not in self.raw_data or self.vix is None:
            return None
        closes = self.raw_data["VIX"]['Close'].dropna()
        if len(closes) < 50:
            return None
        year = closes.tail(252)
        pctl = float((year < self.vix.current).mean() * 100)
        pctl = round(pctl, 1)
        if pctl <= 25:
            tier = "Low"
        elif pctl <= 75:
            tier = "Mid"
        else:
            tier = "High"
        return pctl, tier

    # ---- VOL CURVE ----

    def vol_curve(self) -> Optional[VolCurveData]:
        if not all([self.vix9d, self.vix, self.vix3m, self.vix6m]):
            return None

        points = [
            ("VIX9D", 9, self.vix9d.current),
            ("VIX", 30, self.vix.current),
            ("VIX3M", 90, self.vix3m.current),
            ("VIX6M", 180, self.vix6m.current),
        ]

        front = round(self.vix3m.current - self.vix.current, 2)
        back = round(self.vix6m.current - self.vix3m.current, 2)

        # Determine shape
        if self.vix.current > self.vix3m.current:
            shape = "Inverted"
        elif self.vix9d.current > self.vix.current:
            shape = "Partial Inversion"
        elif self.vix3m.current > self.vix6m.current:
            shape = "Partial Inversion"
        else:
            shape = "Normal"

        # Historical mean
        hist_mean = 19.0
        if "VIX" in self.raw_data:
            closes = self.raw_data["VIX"]['Close'].dropna()
            if len(closes) > 100:
                hist_mean = round(float(closes.mean()), 1)

        return VolCurveData(
            shape=shape, points=points,
            front_spread=front, back_spread=back,
            historical_mean=hist_mean,
        )

    # ---- EDGE SIGNALS ----

    def edge_signals(self) -> List[EdgeSignal]:
        signals = []

        # 1. VVIX/VIX Ratio (25 pts)
        if self.vvix and self.vix:
            ratio = self.vvix.current / self.vix.current
            if ratio < 5:
                score, safe = 25, True
            elif ratio <= 6:
                score, safe = 15, True
            else:
                score, safe = 0, False
            signals.append(EdgeSignal(
                "VVIX/VIX Ratio", 25, score, safe,
                f"{ratio:.2f}",
                f"<5 safe, 5-6 neutral, >6 regime risk"
            ))
        else:
            signals.append(EdgeSignal("VVIX/VIX Ratio", 25, 0, False, "N/A", "Data unavailable"))

        # 2. Slow Crossover — VIX vs VIX3M (25 pts)
        if self.vix and self.vix3m:
            safe = self.vix.current < self.vix3m.current
            score = 25 if safe else 0
            state = "Normal" if safe else "INVERTED"
            signals.append(EdgeSignal(
                "Slow Crossover (VIX vs VIX3M)", 25, score, safe,
                state,
                f"VIX {self.vix.current:.1f} vs VIX3M {self.vix3m.current:.1f}"
            ))
        else:
            signals.append(EdgeSignal("Slow Crossover", 25, 0, False, "N/A", ""))

        # 3. Fast Crossover — VIX9D vs VIX (20 pts)
        if self.vix9d and self.vix:
            safe = self.vix9d.current < self.vix.current
            score = 20 if safe else 0
            state = "Normal" if safe else "ALERT"
            signals.append(EdgeSignal(
                "Fast Crossover (VIX9D vs VIX)", 20, score, safe,
                state,
                f"VIX9D {self.vix9d.current:.1f} vs VIX {self.vix.current:.1f}"
            ))
        else:
            signals.append(EdgeSignal("Fast Crossover", 20, 0, False, "N/A", ""))

        # 4. Toxic Mix — VIX < 16 AND SKEW > 130 (15 pts)
        if self.vix and self.skew:
            toxic = self.vix.current < 16 and self.skew.current > 130
            safe = not toxic
            score = 15 if safe else 0
            signals.append(EdgeSignal(
                "Toxic Mix", 15, score, safe,
                "ACTIVE" if toxic else "Clear",
                f"VIX {self.vix.current:.1f} (<16?) & SKEW {self.skew.current:.0f} (>130?)"
            ))
        else:
            signals.append(EdgeSignal("Toxic Mix", 15, 0, False, "N/A", ""))

        # 5. VVIX Divergence (15 pts)
        if self.vvix and self.vix and "VVIX" in self.raw_data and "VIX" in self.raw_data:
            vvix_5d = self.raw_data["VVIX"]['Close'].dropna().tail(5)
            vix_5d = self.raw_data["VIX"]['Close'].dropna().tail(5)

            if len(vvix_5d) >= 5 and len(vix_5d) >= 5:
                vvix_chg = (float(vvix_5d.iloc[-1]) / float(vvix_5d.iloc[0]) - 1) * 100
                vix_chg = (float(vix_5d.iloc[-1]) / float(vix_5d.iloc[0]) - 1) * 100
                diverging = vvix_chg > 2 and vix_chg < 1
                safe = not diverging
                score = 15 if safe else 0
                signals.append(EdgeSignal(
                    "VVIX Divergence", 15, score, safe,
                    "DIVERGING" if diverging else "Aligned",
                    f"VVIX 5d: {vvix_chg:+.1f}%, VIX 5d: {vix_chg:+.1f}%"
                ))
            else:
                signals.append(EdgeSignal("VVIX Divergence", 15, 15, True, "Insufficient data", ""))
        else:
            signals.append(EdgeSignal("VVIX Divergence", 15, 0, False, "N/A", ""))

        return signals

    def edge_score(self) -> int:
        return sum(s.score for s in self.edge_signals())

    # ---- TRADE VERDICT ----

    def trade_verdict(self) -> TradeVerdict:
        score = self.edge_score()
        vrp_val = self.vrp()
        signals = self.edge_signals()
        curve = self.vol_curve()

        alerts = []

        # Check specific alerts
        for s in signals:
            if not s.is_safe:
                if "Fast" in s.name:
                    alerts.append("Fast Crossover (VIX9D > VIX) — don't trade aggressively. Take profits, preserve BP.")
                elif "Slow" in s.name:
                    alerts.append("Slow Crossover (VIX > VIX3M) — structural fear. Reduce exposure, go defensive.")
                elif "Toxic" in s.name:
                    alerts.append("Toxic Mix active — hidden tail risk despite low VIX. No new short-vol.")
                elif "Divergence" in s.name:
                    alerts.append("VVIX Divergence — hidden fear building. Monitor closely.")

        if vrp_val is not None and vrp_val < 0:
            alerts.append("Negative VRP — structural premium edge absent. Avoid selling vol.")

        # Determine verdict
        toxic_active = any("Toxic" in s.name and not s.is_safe for s in signals)
        normal_curve = curve and curve.shape == "Normal"

        if toxic_active or score < 40:
            verdict = "DEFENSIVE"
            strategy = "No new short-vol positions. Preserve capital. Close losers. Only defined-risk if trading at all."
        elif score >= 70 and normal_curve and vrp_val is not None and vrp_val >= 2:
            verdict = "FAVORABLE"
            strategy = "Full size, sell premium. Strangles, iron condors at 45 DTE. Manage at 21 DTE, take profits at 50%."
        else:
            verdict = "CAUTION"
            strategy = "Smaller size, prefer defined risk (spreads). Take profits at 50%. Manage at 21 DTE."

        return TradeVerdict(verdict=verdict, strategy=strategy, alerts=alerts)

    # ---- VOL CURVE STATE LABEL ----

    def curve_state_label(self) -> str:
        if not self.vix or not self.vix3m:
            return "Unknown"
        if self.vix.current < self.vix3m.current:
            return "NORMAL (VIX < VIX3M)"
        else:
            return "INVERTED (VIX > VIX3M)"

    # ---- PORTFOLIO CALCULATOR ----

    @staticmethod
    def vix_tier(vix_val: float) -> str:
        if vix_val < 15:
            return "< 15"
        elif vix_val < 20:
            return "15 – 20"
        elif vix_val < 30:
            return "20 – 30"
        elif vix_val < 40:
            return "30 – 40"
        else:
            return "> 40"

    @staticmethod
    def portfolio_params(nlv: float, vix_val: float) -> PortfolioParams:
        if vix_val < 15:
            bp_pct, theta_min, theta_max, reserve = 0.25, 0.001, 0.001, 0.75
        elif vix_val < 20:
            bp_pct, theta_min, theta_max, reserve = 0.30, 0.001, 0.002, 0.70
        elif vix_val < 30:
            bp_pct, theta_min, theta_max, reserve = 0.35, 0.001, 0.003, 0.65
        elif vix_val < 40:
            bp_pct, theta_min, theta_max, reserve = 0.40, 0.001, 0.004, 0.60
        else:
            bp_pct, theta_min, theta_max, reserve = 0.50, 0.001, 0.005, 0.50

        return PortfolioParams(
            nlv=nlv,
            vix_tier=VommaEngine.vix_tier(vix_val),
            bp_usage_pct=bp_pct * 100,
            bp_usage_dollar=nlv * bp_pct,
            theta_min=nlv * theta_min,
            theta_max=nlv * theta_max,
            spy_bw_delta=nlv * 0.0015,
            max_pos_defined=nlv * 0.05,
            max_pos_undefined=nlv * 0.07,
            capital_reserve_pct=reserve * 100,
            capital_reserve_dollar=nlv * reserve,
        )

    # ---- GUIDELINES TABLE ----

    @staticmethod
    def guidelines_table(current_vix: float) -> pd.DataFrame:
        rows = [
            {"VIX Level": "< 15", "BP Usage": "25%", "Target Theta": "0.1% NLV", "active": current_vix < 15},
            {"VIX Level": "15 – 20", "BP Usage": "30%", "Target Theta": "0.1 – 0.2% NLV", "active": 15 <= current_vix < 20},
            {"VIX Level": "20 – 30", "BP Usage": "35%", "Target Theta": "0.1 – 0.3% NLV", "active": 20 <= current_vix < 30},
            {"VIX Level": "30 – 40", "BP Usage": "40%", "Target Theta": "0.1 – 0.4% NLV", "active": 30 <= current_vix < 40},
            {"VIX Level": "> 40", "BP Usage": "50%", "Target Theta": "0.1 – 0.5% NLV", "active": current_vix >= 40},
        ]
        return pd.DataFrame(rows)
