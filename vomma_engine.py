"""
Volatility Cockpit Engine
All data fetch, VRP, Edge Score, Vol Curve, Portfolio Calculator.
Data: Yahoo Finance (CBOE indices).
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# All CBOE tickers
TICKERS = {
    "^VIX": "VIX",
    "^VIX9D": "VIX9D",
    "^VIX3M": "VIX3M",
    "^VIX6M": "VIX6M",
    "^VVIX": "VVIX",
    "^SKEW": "SKEW",
    "^GSPC": "SPX",
}

# Optional tickers — may fail, that's OK
OPTIONAL_TICKERS = {
    "^PCCE": "PC_RATIO",
    "^VIXEQ": "VIXEQ",
}

DESCRIPTIONS = {
    "VIX": "30-day implied volatility of S&P 500. The main fear gauge.",
    "VIX9D": "9-day implied vol. Reacts fastest to sudden events.",
    "VIX3M": "3-month implied vol. Structural trend indicator.",
    "VIX6M": "6-month implied vol. Long-term market expectations.",
    "VVIX": "Volatility of VIX options. Uncertainty about future VIX levels.",
    "SKEW": "Tail risk asymmetry. High SKEW = market pricing crash risk.",
    "PC_RATIO": "CBOE equity put/call ratio. >1.0 = fear, <0.7 = complacency.",
    "VIXEQ": "S&P 500 constituent vol (avg IV of individual stocks). VIXEQ/VIX = implied correlation proxy.",
}


@dataclass
class IndexSnapshot:
    name: str
    current: float
    prev_close: float
    change: float
    change_pct: float
    history_5d: List[float]
    description: str


@dataclass
class EdgeSignal:
    name: str
    weight: int
    score: int
    is_safe: bool
    value_str: str
    detail: str
    explanation: str


class VommaEngine:
    def __init__(self):
        self.raw: Dict[str, pd.DataFrame] = {}
        self.snaps: Dict[str, IndexSnapshot] = {}

    # ------------------------------------------------------------------ fetch
    def fetch_all(self) -> bool:
        ok = 0
        for yf_t, name in {**TICKERS, **OPTIONAL_TICKERS}.items():
            try:
                df = yf.download(yf_t, period="1y", auto_adjust=True, progress=False, timeout=15)
                if df is None or df.empty:
                    continue
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                if "Close" not in df.columns:
                    continue
                self.raw[name] = df
                ok += 1
            except Exception:
                pass
        if ok < 3:
            return False
        self._build_snapshots()
        return True

    def _build_snapshots(self):
        for name, df in self.raw.items():
            if name == "SPX":
                continue
            closes = df["Close"].dropna()
            if len(closes) < 2:
                continue
            cur = float(closes.iloc[-1])
            prev = float(closes.iloc[-2])
            chg = cur - prev
            chg_p = (chg / prev * 100) if prev else 0.0
            h5 = closes.tail(5).tolist()
            self.snaps[name] = IndexSnapshot(
                name=name, current=cur, prev_close=prev,
                change=round(chg, 4), change_pct=round(chg_p, 2),
                history_5d=h5, description=DESCRIPTIONS.get(name, ""),
            )

    def _v(self, name: str) -> Optional[float]:
        s = self.snaps.get(name)
        return s.current if s else None

    # ------------------------------------------------------------- realized vol
    def realized_vol_20d(self) -> Optional[float]:
        df = self.raw.get("SPX")
        if df is None:
            return None
        c = df["Close"].dropna()
        if len(c) < 22:
            return None
        lr = np.log(c / c.shift(1)).dropna()
        return round(float(lr.tail(20).std() * np.sqrt(252) * 100), 2)

    # -------------------------------------------------------------------- VRP
    def vrp(self) -> Optional[float]:
        vix = self._v("VIX")
        rv = self.realized_vol_20d()
        if vix is None or rv is None:
            return None
        return round(vix - rv, 2)

    @staticmethod
    def vrp_tier(v: Optional[float]) -> str:
        if v is None: return "N/A"
        if v > 5: return "PREMIUM RICH"
        if v >= 2: return "NORMAL"
        if v >= 0: return "THIN"
        return "NEGATIVE"

    # -------------------------------------------------------------- VIX rank
    def vix_rank(self) -> Tuple[Optional[float], str]:
        vix = self._v("VIX")
        df = self.raw.get("VIX")
        if vix is None or df is None:
            return None, "N/A"
        c = df["Close"].dropna()
        if len(c) < 50:
            return None, "N/A"
        yr = c.tail(252)
        pctl = round(float((yr < vix).mean() * 100), 1)
        tier = "Low" if pctl <= 25 else ("Mid" if pctl <= 75 else "High")
        return pctl, tier

    # -------------------------------------------------------- curve state
    def curve_state(self) -> str:
        vix, vix3m = self._v("VIX"), self._v("VIX3M")
        if vix is None or vix3m is None:
            return "Unknown"
        return "NORMAL (VIX < VIX3M)" if vix < vix3m else "INVERTED (VIX > VIX3M)"

    # -------------------------------------------------------- vol curve
    def vol_curve_data(self) -> Optional[Dict]:
        vals = {}
        for n in ["VIX9D", "VIX", "VIX3M", "VIX6M"]:
            v = self._v(n)
            if v is None:
                return None
            vals[n] = v

        points = [
            ("VIX9D", 9, vals["VIX9D"]),
            ("VIX", 30, vals["VIX"]),
            ("VIX3M", 90, vals["VIX3M"]),
            ("VIX6M", 180, vals["VIX6M"]),
        ]
        front = round(vals["VIX3M"] - vals["VIX"], 2)
        back = round(vals["VIX6M"] - vals["VIX3M"], 2)

        if vals["VIX"] > vals["VIX3M"]:
            shape = "Inverted"
        elif vals["VIX9D"] > vals["VIX"] or vals["VIX3M"] > vals["VIX6M"]:
            shape = "Partial Inversion"
        else:
            shape = "Normal"

        hist_mean = 19.0
        df_vix = self.raw.get("VIX")
        if df_vix is not None:
            c = df_vix["Close"].dropna()
            if len(c) > 100:
                hist_mean = round(float(c.mean()), 1)

        return {
            "shape": shape, "points": points,
            "front": front, "back": back, "mean": hist_mean,
        }

    # -------------------------------------------------------------- VIXEQ/VIX
    def vixeq_vix_ratio(self) -> Optional[float]:
        vixeq = self._v("VIXEQ")
        vix = self._v("VIX")
        if vixeq is None or vix is None or vix == 0:
            return None
        return round(vixeq / vix, 2)

    # ----------------------------------------------------------- edge signals
    def edge_signals(self) -> List[EdgeSignal]:
        sigs = []

        # 1. VVIX/VIX Ratio (25)
        vvix, vix = self._v("VVIX"), self._v("VIX")
        if vvix is not None and vix is not None and vix > 0:
            r = round(vvix / vix, 2)
            if r < 5:
                sc, safe = 25, True
            elif r <= 6:
                sc, safe = 15, True
            else:
                sc, safe = 0, False
            sigs.append(EdgeSignal(
                "VVIX/VIX Ratio", 25, sc, safe, f"{r:.2f}",
                f"VVIX {vvix:.1f} / VIX {vix:.1f}",
                "<5 = safe, 5-6 = neutral, >6 = regime change risk.",
            ))
        else:
            sigs.append(EdgeSignal("VVIX/VIX Ratio", 25, 0, False, "N/A", "Data unavailable",
                "<5 safe, 5-6 neutral, >6 regime risk."))

        # 2. Slow Crossover — VIX vs VIX3M (25)
        vix3m = self._v("VIX3M")
        if vix is not None and vix3m is not None:
            safe = vix < vix3m
            sigs.append(EdgeSignal(
                "Slow Crossover (VIX vs VIX3M)", 25, 25 if safe else 0, safe,
                "Normal" if safe else "INVERTED",
                f"VIX {vix:.1f} vs VIX3M {vix3m:.1f}",
                "When VIX > VIX3M = deep structural fear. Spot vol exceeds 3-month expectations.",
            ))
        else:
            sigs.append(EdgeSignal("Slow Crossover", 25, 0, False, "N/A", "", "VIX vs VIX3M comparison."))

        # 3. Fast Crossover — VIX9D vs VIX (20)
        vix9d = self._v("VIX9D")
        if vix9d is not None and vix is not None:
            safe = vix9d < vix
            sigs.append(EdgeSignal(
                "Fast Crossover (VIX9D vs VIX)", 20, 20 if safe else 0, safe,
                "Normal" if safe else "ALERT",
                f"VIX9D {vix9d:.1f} vs VIX {vix:.1f}",
                "When VIX9D > VIX = short-term panic pricing. 9-day vol exceeds 30-day.",
            ))
        else:
            sigs.append(EdgeSignal("Fast Crossover", 20, 0, False, "N/A", "", "VIX9D vs VIX comparison."))

        # 4. Toxic Mix (15)
        skew = self._v("SKEW")
        if vix is not None and skew is not None:
            toxic = vix < 16 and skew > 130
            sigs.append(EdgeSignal(
                "Toxic Mix", 15, 0 if toxic else 15, not toxic,
                "ACTIVE" if toxic else "Clear",
                f"VIX {vix:.1f} (<16?) & SKEW {skew:.0f} (>130?)",
                "VIX < 16 AND SKEW > 130 simultaneously = hidden tail risk despite complacency.",
            ))
        else:
            sigs.append(EdgeSignal("Toxic Mix", 15, 0, False, "N/A", "", "VIX < 16 and SKEW > 130 check."))

        # 5. VVIX Divergence (15)
        if "VVIX" in self.raw and "VIX" in self.raw:
            vv5 = self.raw["VVIX"]["Close"].dropna().tail(5)
            vi5 = self.raw["VIX"]["Close"].dropna().tail(5)
            if len(vv5) >= 5 and len(vi5) >= 5:
                vv_chg = (float(vv5.iloc[-1]) / float(vv5.iloc[0]) - 1) * 100
                vi_chg = (float(vi5.iloc[-1]) / float(vi5.iloc[0]) - 1) * 100
                div = vv_chg > 2 and vi_chg < 1
                sigs.append(EdgeSignal(
                    "VVIX Divergence", 15, 0 if div else 15, not div,
                    "DIVERGING" if div else "Aligned",
                    f"VVIX 5d: {vv_chg:+.1f}%, VIX 5d: {vi_chg:+.1f}%",
                    "VVIX rising while VIX stays calm = hidden fear building.",
                ))
            else:
                sigs.append(EdgeSignal("VVIX Divergence", 15, 15, True, "N/A", "Insufficient data",
                    "VVIX rising while VIX calm = hidden fear."))
        else:
            sigs.append(EdgeSignal("VVIX Divergence", 15, 0, False, "N/A", "",
                "VVIX rising while VIX calm = hidden fear."))

        return sigs

    def edge_score(self) -> int:
        return sum(s.score for s in self.edge_signals())

    # -------------------------------------------------------- trade verdict
    def trade_verdict(self) -> Dict:
        score = self.edge_score()
        vrp_val = self.vrp()
        signals = self.edge_signals()
        cs = self.curve_state()

        alerts = []
        for s in signals:
            if not s.is_safe:
                if "Fast" in s.name:
                    alerts.append(("Fast Crossover (VIX9D > VIX)",
                        "Don't trade aggressively today. Take profits, preserve buying power."))
                elif "Slow" in s.name:
                    alerts.append(("Slow Crossover (VIX > VIX3M)",
                        "Structural fear active. Reduce exposure significantly."))
                elif "Toxic" in s.name:
                    alerts.append(("Toxic Mix Active",
                        "Hidden tail risk despite low VIX. No new short-vol positions."))
                elif "Divergence" in s.name:
                    alerts.append(("VVIX Divergence",
                        "Hidden fear building. Monitor closely, reduce size."))

        if vrp_val is not None and vrp_val < 0:
            alerts.append(("Negative VRP",
                "Structural premium selling edge is absent. Avoid selling vol."))

        toxic = any("Toxic" in s.name and not s.is_safe for s in signals)
        normal = "NORMAL" in cs

        if toxic or score < 40:
            verdict = "DEFENSIVE"
            strategy = "No new short-vol positions. Preserve capital. Close losers. Only defined-risk if trading at all."
        elif score >= 70 and normal and vrp_val is not None and vrp_val >= 2:
            verdict = "FAVORABLE"
            strategy = "Full size, sell premium. Strangles, iron condors at 45 DTE. Manage at 21 DTE, take profits at 50%."
        else:
            verdict = "CAUTION"
            strategy = "Smaller size, prefer defined risk (spreads). Take profits at 50%. Manage at 21 DTE."

        return {"verdict": verdict, "strategy": strategy, "alerts": alerts}

    # ----------------------------------------------------- portfolio calculator
    @staticmethod
    def vix_tier_label(vix_val: float) -> str:
        if vix_val < 15: return "< 15"
        if vix_val < 20: return "15 - 20"
        if vix_val < 30: return "20 - 30"
        if vix_val < 40: return "30 - 40"
        return "> 40"

    @staticmethod
    def portfolio_params(nlv: float, vix_val: float) -> Dict:
        tiers = [
            (15, 0.25, 0.001, 0.001),
            (20, 0.30, 0.001, 0.002),
            (30, 0.35, 0.001, 0.003),
            (40, 0.40, 0.001, 0.004),
            (999, 0.50, 0.001, 0.005),
        ]
        for lim, bp, tmin, tmax in tiers:
            if vix_val < lim:
                break
        reserve = 1.0 - bp
        return {
            "vix_tier": VommaEngine.vix_tier_label(vix_val),
            "bp_pct": bp * 100, "bp_dollar": nlv * bp,
            "theta_min": nlv * tmin, "theta_max": nlv * tmax,
            "spy_bw_delta": nlv * 0.0015,
            "max_defined": nlv * 0.05, "max_undefined": nlv * 0.07,
            "reserve_pct": reserve * 100, "reserve_dollar": nlv * reserve,
        }

    @staticmethod
    def guidelines_rows(current_vix: float) -> List[Dict]:
        rows = [
            {"level": "< 15", "bp": "25%", "theta": "0.1% NLV", "lo": 0, "hi": 15},
            {"level": "15 - 20", "bp": "30%", "theta": "0.1 - 0.2% NLV", "lo": 15, "hi": 20},
            {"level": "20 - 30", "bp": "35%", "theta": "0.1 - 0.3% NLV", "lo": 20, "hi": 30},
            {"level": "30 - 40", "bp": "40%", "theta": "0.1 - 0.4% NLV", "lo": 30, "hi": 40},
            {"level": "> 40", "bp": "50%", "theta": "0.1 - 0.5% NLV", "lo": 40, "hi": 999},
        ]
        for r in rows:
            r["active"] = r["lo"] <= current_vix < r["hi"]
        return rows

    # --------------------------------------------------------- serialize all
    def serialize(self) -> Dict:
        """Return everything as plain dict for Streamlit cache compatibility."""
        vrp_val = self.vrp()
        rv = self.realized_vol_20d()
        vr_pctl, vr_tier = self.vix_rank()
        vix = self._v("VIX")

        # Vol complex — ordered
        vol_order = ["VIX", "VVIX", "VIX9D", "VIX3M", "VIX6M", "SKEW", "PC_RATIO", "VIXEQ"]
        vol_complex = []
        for name in vol_order:
            s = self.snaps.get(name)
            if s:
                vol_complex.append({
                    "name": s.name, "current": s.current,
                    "change": s.change, "change_pct": s.change_pct,
                    "history_5d": s.history_5d, "description": s.description,
                })

        # Edge
        signals = self.edge_signals()
        sig_list = [{
            "name": s.name, "weight": s.weight, "score": s.score,
            "safe": s.is_safe, "value": s.value_str,
            "detail": s.detail, "explanation": s.explanation,
        } for s in signals]

        verdict = self.trade_verdict()
        curve = self.vol_curve_data()

        # VIXEQ/VIX ratio
        veq_ratio = self.vixeq_vix_ratio()

        return {
            "ts": datetime.now().strftime("%A, %B %d, %Y  %I:%M %p ET"),
            "vix": vix,
            "rv": rv,
            "vrp": vrp_val,
            "vrp_tier": self.vrp_tier(vrp_val),
            "vix_rank_pctl": vr_pctl,
            "vix_rank_tier": vr_tier,
            "curve_state": self.curve_state(),
            "edge_score": self.edge_score(),
            "vol_complex": vol_complex,
            "signals": sig_list,
            "verdict": verdict["verdict"],
            "strategy": verdict["strategy"],
            "alerts": verdict["alerts"],
            "curve": curve,
            "vixeq_vix_ratio": veq_ratio,
        }
