# ============================================================
# Wfx PRO — SMC + FIBONACCI — v6.3.4
# ============================================================


# ============================================================
# SECTION: STDLIB IMPORTS
# ============================================================
from pathlib import Path
from datetime import datetime, timedelta
import json
import traceback
import time
import pytz


# ============================================================
# SECTION: THIRD-PARTY IMPORTS
# ============================================================
import numpy as np
import pandas as pd
from colorama import init
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live


# ============================================================
# SECTION: CONFIG BOOTSTRAP
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config_v6.3.4.json"
STATE_FILE = BASE_DIR / "state_v6.3.4.json"
ERROR_LOG = BASE_DIR / "error_v6.3.4.log"


# ============================================================
# SECTION: DEFAULT_CONFIG
# ============================================================
DEFAULT_CONFIG = {
    # ----- SYMBOL & TIMEFRAMES -----
    "SYMBOL": "XAUUSD.vxc",
    "TIMEFRAME_ENTRY": "M5",
    "TIMEFRAME_SMC": "M15",
    "TIMEFRAME_TREND": "M15",
    "TIMEFRAME_HTF": "H1",
    "FVG_TIMEFRAME": "M5",

    # ----- RISK MANAGEMENT -----
    "MAX_DAILY_LOSS_PCT": 20.0,
    "MAX_OPEN_POSITIONS": 3,
    "MAX_PER_MODEL": 2,

    # ----- MODEL TOGGLES -----
    "USE_MODEL_CONTINUATION": True,
    "USE_MODEL_REVERSAL": True,
    "USE_MODEL_SWEEP": True,

    # ----- MAX POSISI PER MODEL -----
    "MAX_POSITIONS_CONTINUATION": 2,
    "MAX_POSITIONS_REVERSAL": 2,
    "MAX_POSITIONS_SWEEP": 2,

    # ----- SL / TP -----
    "SL_ATR_MULT": 1.5,
    "TP_RR_TP1": 1.0,
    "TP_RR_TP2": 2.0,
    "TP_RR_TP3": 3.0,
    "MIN_RR_TP3": 1.0,
    "HARD_MAX_RR_TP3": 8.0,
    "MIN_SL_DISTANCE": 4.0,
    "MAX_SL_POINTS": 15.0,

    # ----- TRADE MANAGEMENT -----
    "USE_BREAK_EVEN": True,
    "USE_TRAILING": True,
    "BE_TRIGGER_ATR": 1.5,
    "BE_OFFSET_PRICE": 0.10,
    "TRAIL_TRIGGER_ATR": 2.0,
    "TRAIL_SECURE_PCT": 50,

    # ----- PARTIAL CLOSE -----
    "PARTIAL_MODE": "PERCENT",
    "PARTIAL_PCT_1": 33,
    "PARTIAL_PCT_2": 33,
    "PARTIAL_LOT_1": 0.01,
    "PARTIAL_LOT_2": 0.01,
    "PARTIAL_MIN_LOT": 0.03,

    # ----- ENTRY FILTERS -----
    "MIN_CONFLUENCE": 75,
    "USE_FIB_GATE": False,
    "USE_SESSION_FILTER": True,
    "SESSION_TIMEZONE": "Asia/Jakarta",
    "USE_ATR_FILTER": True,
    "MIN_ATR_VALUE": 1.0,
    "EMA_FAST": 20,
    "EMA_MID": 50,
    "EMA_SLOW": 100,
    "WICK_RATIO_MIN": 0.45,

    # ----- SMC / ZONE -----
    "SMC_ZONE_SENSITIVITY": 0.10,
    "SMC_MAX_ZONES": 20,
    "SWEEP_LOOKBACK": 50,
    "SWEEP_MIN_DISPLACEMENT_ATR": 0.50,
    "SWING_STRICTNESS": 1,
    "ZONE_TOLERANCE_ATR": 1.0,
    "MIN_SWING_SIZE": 1.0,
    "SWING_FIB_LOOKBACK": 50,
    "SMC_ATR_PERIOD": 50,
    "ATR_PERIOD": 14,
    "ZONE_OVERLAP_ATR": 1.0,
    "ZONE_BODY_RATIO_MIN": 0.25,

    # ----- FVG -----
    "USE_FVG": True,
    "USE_FVG_MITIGATION": True,
    "FVG_MIN_GAP_ATR": 0.05,
    "FVG_MIN_GAP_PRICE": 0.01,

    # ----- FIBONACCI ENTRY ZONES -----
    "FIB_ZONE_CONTINUATION": [0.382, 0.786],
    "FIB_ZONE_REVERSAL": [0.5, 0.886],
    "FIB_ZONE_SWEEP": [0.382, 0.786],

    # ----- ANTI RE-ENTRY -----
    "MIN_REENTRY_ATR": 2.0,
    "LOSS_REENTRY_ATR": 2.0,
    "RETRACE_MIN_PERCENT": 20.0,

    # ----- LOT SIZING -----
    "LOT_SIZE": 0.01,
    "LOT_TIER_1": 0.01,
    "LOT_TIER_2": 0.03,
    "LOT_TIER_3": 0.06,
    "MIN_LOT_SIZE": 0.01,
    "MAX_LOT_SIZE": 0.06,
    "HARD_LOT_CAP": 0.06,

    # ----- CONFLUENCE SCORES -----
    "CONFLUENCE_HTF_SCORE": 20,
    "CONFLUENCE_POI_SCORE": 20,
    "CONFLUENCE_CHOCH_SCORE": 15,
    "CONFLUENCE_WICK_SCORE": 10,
    "CONFLUENCE_FIB_SCORE": 15,
    "CONFLUENCE_SESSION_SCORE": 10,
    "CONFLUENCE_FVG_SCORE": 5,
    "CONFLUENCE_RR_SCORE": 10,
    "CONFLUENCE_TIER_1": 75,
    "CONFLUENCE_TIER_2": 80,
    "CONFLUENCE_TIER_3": 90,
    "CONFLUENCE_RR_THRESHOLD": 2.0,

    # ----- GUARDS -----
    "MARGIN_SAFETY_PCT": 30.0,

    # ----- ORDER RETRY -----
    "TRADE_DEVIATION": 20,
    "ORDER_RETRY_COUNT": 3,
    "ORDER_RETRY_DELAY": 0.50,
    "POST_ORDER_SETTLE_DELAY": 0.50,
    "RECONNECT_RETRIES": 5,
    "RECONNECT_DELAY": 5,

    # ----- MAIN LOOP TIMING -----
    "MAIN_LOOP_INTERVAL": 1.0,
    "SMC_UPDATE_INTERVAL": 60,
    "META_REBUILD_INTERVAL": 15,
    "STATS_REFRESH_INTERVAL": 10,
    "STARTUP_DELAY": 2,

    # ----- SESSION FILTER -----
    "SESSION_FILTER": {
        "ENABLED": True,
        "ASIA": {"ENABLED": True, "START": "07:00", "END": "15:00"},
        "LONDON": {"ENABLED": True, "START": "15:00", "END": "23:00"},
        "NEW_YORK": {"ENABLED": True, "START": "20:00", "END": "04:00"},
        "LONDON_NEW_YORK_OVERLAP": {"ENABLED": True, "START": "20:00", "END": "23:00"}
    },

    # ----- MISC -----
    "MAGIC": 777777,
    "USE_AUTO_TRADE": True,
    "STATS_LOOKBACK_DAYS": 30,
    "STATS_INCLUDE_MANUAL": True,

    # ----- MANUAL RECOVERY -----
    "USE_MANUAL_RECOVERY": True,
    "MANUAL_PROFILE": {
        "SL_TP_MODE": "ATR",
        "RR": 1.5,
        "FIB_TP_EXT": 1.618,
        "MIN_SL_PRICE": 3.0,
        "MAX_SL_PRICE": 20.0,
        "CHECK_INTERVAL": 5,
        "OVERRIDE_EXISTING": False,
    },

    # ----- FIB SL -----
    "USE_FIB_SL": False,
    "SL_BUFFER": 1.0,
}


# ============================================================
# SECTION: CONFIG HELPERS
# ============================================================
def _deep_merge(default, current):
    if isinstance(default, dict) and isinstance(current, dict):
        result = dict(default)
        for key, value in current.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = _deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    return current


def load_or_create_config(path=CONFIG_FILE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_CONFIG, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print("[OK] Config created:", path)
        return dict(DEFAULT_CONFIG)
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(current, dict):
            raise ValueError("root not dict")
        print("[OK] Config loaded:", path)
    except Exception:
        backup = path.with_suffix(path.suffix + ".broken")
        try:
            path.replace(backup)
            print("[WARN] Config corrupted, backed up:", backup)
        except OSError:
            pass
        path.write_text(json.dumps(DEFAULT_CONFIG, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        return dict(DEFAULT_CONFIG)
    merged = _deep_merge(DEFAULT_CONFIG, current)
    if merged != current:
        path.write_text(json.dumps(merged, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print("[OK] Config updated:", path)
    return merged


def load_state(path=STATE_FILE):
    path = Path(path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state, path=STATE_FILE):
    path = Path(path)
    try:
        path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError:
        pass


def log_error(exc_text):
    try:
        from datetime import datetime as _dt
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{_dt.now()}]\n{exc_text}\n")
    except Exception:
        pass


# ============================================================
# SECTION: BOOTSTRAP
# ============================================================
print("=" * 60)
print("WEENfx PRO - v6.3.4")
print("=" * 60)

CONFIG = load_or_create_config()

import MetaTrader5 as mt5

init(autoreset=True)
console = Console()

runtime_message_text = ""


def timeframe_from_name(value):
    if isinstance(value, int):
        return value
    mapping = {
        "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    return mapping.get(str(value).upper(), mt5.TIMEFRAME_M5)


def apply_config(c):
    g = globals()
    for key, value in c.items():
        if key in ("SESSION_FILTER", "SESSION_TIMEZONE", "MANUAL_PROFILE"):
            continue
        if key in ("TIMEFRAME_ENTRY", "TIMEFRAME_HTF", "TIMEFRAME_SMC",
                   "TIMEFRAME_TREND", "FVG_TIMEFRAME"):
            g[key] = timeframe_from_name(value)
        else:
            g[key] = value


apply_config(CONFIG)

SESSION_CONFIG = CONFIG.get("SESSION_FILTER", DEFAULT_CONFIG["SESSION_FILTER"])
MANUAL_PROFILE = CONFIG.get("MANUAL_PROFILE", DEFAULT_CONFIG["MANUAL_PROFILE"])
WIB = pytz.timezone(CONFIG.get("SESSION_TIMEZONE", "Asia/Jakarta"))
SESSION_STATUS = "OUT OF SESSION"


def runtime_message(message):
    global runtime_message_text
    try:
        txt = str(message)
        txt = txt.replace("[", "(").replace("]", ")")
        runtime_message_text = txt[:250]
    except Exception:
        runtime_message_text = ""


def connect_mt5():
    print("[..] Connecting to MT5...")
    retries = int(CONFIG.get("RECONNECT_RETRIES", 5))
    delay = float(CONFIG.get("RECONNECT_DELAY", 5))
    for attempt in range(1, retries + 1):
        if mt5.initialize():
            print("[OK] MT5 Connected")
            return True
        print(f"[WARN] MT5 init failed ({attempt}/{retries})")
        time.sleep(delay)
    return False


if not connect_mt5():
    print("[ERR] MT5 failed to initialize!")
    quit()

_account_info = mt5.account_info()
if _account_info is None:
    print("[ERR] account_info() None")
    quit()


# ============================================================
# SECTION: DATA LAYER
# ============================================================
def get_data(tf, bars=300):
    rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, bars)
    if rates is None:
        return pd.DataFrame()
    return pd.DataFrame(rates)


def get_closed_data(tf, bars=300):
    df = get_data(tf, bars + 1)
    if df is None or df.empty or len(df) < 3:
        return pd.DataFrame()
    return df.iloc[:-1].copy().reset_index(drop=True)


def get_last_closed_candle_time(tf):
    df = get_closed_data(tf, bars=2)
    if df is None or df.empty:
        return None
    return df['time'].iloc[-1]


def get_live_price():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick:
        return tick.bid, tick.ask
    return None, None


# ============================================================
# SECTION: STATE PERSISTENCE
# ============================================================
POSITION_META = {}
PARTIAL_STATE = {}
FVG_STATE = {}

_state = load_state()
_today_wib = datetime.now(WIB).date()
_state_date = _state.get("daily_date")

if _state_date == str(_today_wib):
    daily_start_balance = float(_state.get("daily_start_balance", _account_info.balance))
    trading_disabled_today = bool(_state.get("trading_disabled_today", False))
else:
    daily_start_balance = float(_account_info.balance)
    trading_disabled_today = False
daily_date = _today_wib

_pm_saved = _state.get("position_meta", {})
if isinstance(_pm_saved, dict):
    for k, v in _pm_saved.items():
        try:
            POSITION_META[int(k)] = v
        except (ValueError, TypeError):
            continue

_ps_saved = _state.get("partial_state", {})
if isinstance(_ps_saved, dict):
    for k, v in _ps_saved.items():
        try:
            PARTIAL_STATE[int(k)] = v
        except (ValueError, TypeError):
            continue

_fvg_saved = _state.get("fvg_state", {})
if isinstance(_fvg_saved, dict):
    FVG_STATE = _fvg_saved


def persist_state():
    try:
        save_state({
            "daily_date": str(daily_date),
            "daily_start_balance": daily_start_balance,
            "trading_disabled_today": trading_disabled_today,
            "position_meta": {str(k): v for k, v in POSITION_META.items()},
            "partial_state": {str(k): v for k, v in PARTIAL_STATE.items()},
            "fvg_state": FVG_STATE,
        })
    except Exception:
        pass


persist_state()


# ============================================================
# SECTION: TREND DETECTION
# ============================================================
def trend_m5():
    df = get_closed_data(TIMEFRAME_TREND)
    if df.empty:
        return "SIDEWAYS"
    df['ema20'] = df['close'].ewm(span=int(CONFIG.get("EMA_FAST", 20))).mean()
    df['ema50'] = df['close'].ewm(span=int(CONFIG.get("EMA_MID", 50))).mean()
    if df['ema20'].iloc[-1] > df['ema50'].iloc[-1]:
        return "BULLISH"
    elif df['ema20'].iloc[-1] < df['ema50'].iloc[-1]:
        return "BEARISH"
    return "SIDEWAYS"


def get_higher_timeframe_trend():
    df = get_closed_data(TIMEFRAME_HTF, bars=100)
    if df is None or df.empty:
        return "SIDEWAYS"
    df['ema20'] = df['close'].ewm(span=int(CONFIG.get("EMA_FAST", 20))).mean()
    df['ema50'] = df['close'].ewm(span=int(CONFIG.get("EMA_MID", 50))).mean()
    df['ema100'] = df['close'].ewm(span=int(CONFIG.get("EMA_SLOW", 100))).mean()
    ema20 = df['ema20'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    ema100 = df['ema100'].iloc[-1]
    if ema20 > ema50 > ema100:
        return "BULLISH"
    elif ema20 < ema50 < ema100:
        return "BEARISH"
    elif ema20 > ema50:
        return "BULLISH"
    elif ema20 < ema50:
        return "BEARISH"
    fallback = trend_m5()
    if fallback != "SIDEWAYS":
        return fallback
    return "SIDEWAYS"


# ============================================================
# SECTION: ATR
# ============================================================
def atr_value(df, period=None):
    if period is None:
        period = int(CONFIG.get("ATR_PERIOD", 14))
    if df is None or len(df) < period + 1:
        return None
    prev_close = df['close'].shift(1)
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - prev_close).abs(),
        (df['low'] - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    value = atr.iloc[-1]
    return float(value) if pd.notna(value) else None


def get_atr_current(df=None):
    if df is None:
        df = get_closed_data(TIMEFRAME_ENTRY, bars=100)
    return atr_value(df)


def calculate_atr_series(df, period=None):
    if period is None:
        period = int(CONFIG.get("SMC_ATR_PERIOD", 50))
    df['tr'] = np.maximum(df['high'] - df['low'],
                          np.maximum(abs(df['high'] - df['close'].shift(1)),
                                     abs(df['low'] - df['close'].shift(1))))
    df['atr'] = df['tr'].rolling(window=period).mean()
    return df


# ============================================================
# SECTION: SWING & STRUCTURE
# ============================================================
def detect_swing_points(df, lookback=10):
    highs = []
    lows = []
    if df is None or len(df) < lookback * 2 + 1:
        return highs, lows
    for i in range(lookback, len(df) - lookback):
        is_high = True
        is_low = True
        for j in range(i - lookback, i + lookback + 1):
            if j != i and j < len(df):
                if df['high'].iloc[j] >= df['high'].iloc[i]:
                    is_high = False
                if df['low'].iloc[j] <= df['low'].iloc[i]:
                    is_low = False
        if is_high:
            highs.append((i, df['high'].iloc[i]))
        if is_low:
            lows.append((i, df['low'].iloc[i]))
    return highs, lows


def detect_choch(df, swing_strictness=3):
    if df is None or len(df) < 20:
        return None
    highs, lows = detect_swing_points(df, swing_strictness)
    if len(highs) >= 2 and len(lows) >= 2:
        close = float(df['close'].iloc[-1])
        prev_high = float(highs[-2][1])
        prev_low = float(lows[-2][1])
        if close > prev_high:
            return "BULL_CHoCH"
        if close < prev_low:
            return "BEAR_CHoCH"
    try:
        recent = df.tail(20).iloc[:-1]
        recent_high = float(recent['high'].max())
        recent_low = float(recent['low'].min())
        close = float(df['close'].iloc[-1])
        if close > recent_high:
            return "BULL_CHoCH"
        if close < recent_low:
            return "BEAR_CHoCH"
    except Exception:
        pass
    try:
        recent = df.tail(10).iloc[:-1]
        recent_high = float(recent['high'].max())
        recent_low = float(recent['low'].min())
        close = float(df['close'].iloc[-1])
        if close > recent_high:
            return "BULL_CHoCH"
        if close < recent_low:
            return "BEAR_CHoCH"
    except Exception:
        pass
    return None


# ============================================================
# SECTION: PATTERN
# ============================================================
def _signal_candle(df):
    if df is None or len(df) < 1:
        return None
    return df.iloc[-1]


def detect_rejection_wick(df):
    candle = _signal_candle(df)
    if candle is None:
        return None
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    lower_wick = min(candle['open'], candle['close']) - candle['low']
    total_range = candle['high'] - candle['low']
    if total_range <= 0:
        return None
    if lower_wick / total_range >= float(CONFIG.get("WICK_RATIO_MIN", 0.45)) and lower_wick >= upper_wick:
        return "BULL"
    if upper_wick / total_range >= float(CONFIG.get("WICK_RATIO_MIN", 0.45)) and upper_wick >= lower_wick:
        return "BEAR"
    return None


def update_fvg_state(df, atr=None):
    global FVG_STATE
    if not CONFIG.get("USE_FVG_MITIGATION", True):
        return
    if df is None or len(df) < 3:
        return
    try:
        a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if atr is None:
            atr = atr_value(df)
        min_gap = 0.0 if atr is None else max(
            float(CONFIG.get("FVG_MIN_GAP_PRICE", 0.01)),
            atr * float(CONFIG.get("FVG_MIN_GAP_ATR", 0.05))
        )
        if c['low'] > a['high'] + min_gap and b['close'] > b['open']:
            fvg_id = f"bull_{int(c['time'])}"
            FVG_STATE[fvg_id] = {
                "top": float(c['low']),
                "bottom": float(a['high']),
                "type": "BULL",
                "bar_time": int(c['time']),
            }
        if c['high'] < a['low'] - min_gap and b['close'] < b['open']:
            fvg_id = f"bear_{int(c['time'])}"
            FVG_STATE[fvg_id] = {
                "top": float(a['low']),
                "bottom": float(c['high']),
                "type": "BEAR",
                "bar_time": int(c['time']),
            }
        current_low = float(df['low'].iloc[-1])
        current_high = float(df['high'].iloc[-1])
        to_remove = []
        for fvg_id, fvg in FVG_STATE.items():
            if fvg["type"] == "BULL":
                if current_low <= fvg["bottom"]:
                    to_remove.append(fvg_id)
            else:
                if current_high >= fvg["top"]:
                    to_remove.append(fvg_id)
        for fvg_id in to_remove:
            FVG_STATE.pop(fvg_id, None)
    except Exception:
        log_error(f"update_fvg_state: {traceback.format_exc()}")


def get_active_fvg(direction=None):
    result = []
    for fvg_id, fvg in FVG_STATE.items():
        if direction and fvg["type"] != direction:
            continue
        result.append(fvg)
    return result


def fake_breakout_filter(df):
    if len(df) < 2:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]
    body = abs(last['close'] - last['open'])
    range_candle = last['high'] - last['low']
    if range_candle == 0:
        return False
    body_ratio = body / range_candle
    if body_ratio < float(CONFIG.get("ZONE_BODY_RATIO_MIN", 0.25)):
        return True
    if prev['close'] == last['close']:
        return True
    return False


# ============================================================
# SECTION: SMC ZONES
# ============================================================
def detect_demand_zones(df, sensitivity=None):
    zones = []
    df = calculate_atr_series(df.copy())
    if len(df) < 20:
        return []
    if sensitivity is None:
        sensitivity = float(CONFIG.get("SMC_ZONE_SENSITIVITY", 0.10))
    overlap_atr = float(CONFIG.get("ZONE_OVERLAP_ATR", 1.0))
    for i in range(10, len(df) - 5):
        try:
            if df['close'].iloc[i] < df['open'].iloc[i]:
                body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
                atr_val = df['atr'].iloc[i]
                if atr_val is None or atr_val == 0 or pd.isna(atr_val):
                    continue
                if body_size > atr_val * sensitivity:
                    future_high = df['high'].iloc[i + 1:i + 6].max()
                    if future_high > df['high'].iloc[i]:
                        zone_low = df['low'].iloc[i]
                        zone_high = df['high'].iloc[i]
                        strength = min(100, int((body_size / atr_val) * 50))
                        if not any(abs(z[0] - zone_low) < atr_val * overlap_atr for z in zones):
                            zones.append((zone_low, zone_high, strength, "DEMAND"))
        except (KeyError, ValueError, TypeError):
            continue
    return zones[-int(CONFIG.get("SMC_MAX_ZONES", 20)):] if zones else []


def detect_supply_zones(df, sensitivity=None):
    zones = []
    df = calculate_atr_series(df.copy())
    if len(df) < 20:
        return []
    if sensitivity is None:
        sensitivity = float(CONFIG.get("SMC_ZONE_SENSITIVITY", 0.10))
    overlap_atr = float(CONFIG.get("ZONE_OVERLAP_ATR", 1.0))
    for i in range(10, len(df) - 5):
        try:
            if df['close'].iloc[i] > df['open'].iloc[i]:
                body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
                atr_val = df['atr'].iloc[i]
                if atr_val is None or atr_val == 0 or pd.isna(atr_val):
                    continue
                if body_size > atr_val * sensitivity:
                    future_low = df['low'].iloc[i + 1:i + 6].min()
                    if future_low < df['low'].iloc[i]:
                        zone_low = df['low'].iloc[i]
                        zone_high = df['high'].iloc[i]
                        strength = min(100, int((body_size / atr_val) * 50))
                        if not any(abs(z[0] - zone_low) < atr_val * overlap_atr for z in zones):
                            zones.append((zone_low, zone_high, strength, "SUPPLY"))
        except (KeyError, ValueError, TypeError):
            continue
    return zones[-int(CONFIG.get("SMC_MAX_ZONES", 20)):] if zones else []


def price_in_smc_zone(price, zones, zone_type=None, tolerance=0.0):
    if not zones or price is None:
        return False, None
    for zone in zones:
        try:
            zone_low, zone_high, strength, z_type = zone
            if zone_type and z_type != zone_type:
                continue
            if zone_low <= price <= zone_high:
                return True, zone
            if tolerance > 0:
                if zone_low - tolerance <= price <= zone_high + tolerance:
                    return True, zone
        except (ValueError, TypeError):
            continue
    return False, None


# ============================================================
# SECTION: LIQUIDITY SWEEP
# ============================================================
def smart_liquidity_sweep(df, direction, lookback=None, atr_raw=None):
    if lookback is None:
        lookback = int(CONFIG.get("SWEEP_LOOKBACK", 50))
    if df is None or len(df) < lookback + 3:
        return False
    if atr_raw is None:
        atr_raw = atr_value(df)
    if atr_raw is None or atr_raw <= 0:
        return False
    min_displacement = atr_raw * float(CONFIG.get("SWEEP_MIN_DISPLACEMENT_ATR", 0.50))
    try:
        reference = df.iloc[-lookback - 1:-1]
        recent_high = float(reference['high'].max())
        recent_low = float(reference['low'].min())
        for offset in (1, 2):
            if offset > len(df):
                continue
            candle = df.iloc[-offset]
            body = abs(candle['close'] - candle['open'])
            if direction == "BUY":
                swept = candle['low'] < recent_low and candle['close'] > recent_low
                if swept and body >= min_displacement:
                    return True
            if direction == "SELL":
                swept = candle['high'] > recent_high and candle['close'] < recent_high
                if swept and body >= min_displacement:
                    return True
    except Exception:
        return False
    return False


# ============================================================
# SECTION: FIBONACCI
# ============================================================
def fib_retracement(swing_low, swing_high, level):
    diff = swing_high - swing_low
    return swing_low + diff * (1 - level)


def fib_extension(swing_low, swing_high, level):
    diff = swing_high - swing_low
    return swing_low + diff * level


def fib_extension_sell(swing_low, swing_high, level):
    diff = swing_high - swing_low
    return swing_high - diff * level


def find_last_swing_for_fib(df, direction, lookback=None):
    if lookback is None:
        lookback = int(CONFIG.get("SWING_FIB_LOOKBACK", 50))
    if df is None or len(df) < 30:
        return None, None
    highs, lows = detect_swing_points(df, int(CONFIG.get("SWING_STRICTNESS", 1)))
    if direction == "BUY":
        if highs and lows:
            last_low_idx, last_low_price = lows[-1]
            future_highs = [h for h in highs if h[0] > last_low_idx]
            if future_highs:
                swing_high_price = max(h[1] for h in future_highs)
                if swing_high_price > last_low_price:
                    return last_low_price, swing_high_price
        recent = df.tail(lookback)
        if len(recent) < 10:
            return None, None
        swing_low_price = float(recent['low'].min())
        swing_high_price = float(recent['high'].max())
        if swing_high_price > swing_low_price:
            return swing_low_price, swing_high_price
        return None, None
    else:
        if highs and lows:
            last_high_idx, last_high_price = highs[-1]
            future_lows = [l for l in lows if l[0] > last_high_idx]
            if future_lows:
                swing_low_price = min(l[1] for l in future_lows)
                if swing_low_price < last_high_price:
                    return swing_low_price, last_high_price
        recent = df.tail(lookback)
        if len(recent) < 10:
            return None, None
        swing_low_price = float(recent['low'].min())
        swing_high_price = float(recent['high'].max())
        if swing_high_price > swing_low_price:
            return swing_low_price, swing_high_price
        return None, None


def in_fib_zone(price, swing_low, swing_high, zone_low, zone_high):
    if None in (price, swing_low, swing_high):
        return False
    level_a = fib_retracement(swing_low, swing_high, zone_low)
    level_b = fib_retracement(swing_low, swing_high, zone_high)
    lo, hi = min(level_a, level_b), max(level_a, level_b)
    return lo <= price <= hi


def resolve_fib_sl(swing_low, swing_high, direction, entry):
    if not USE_FIB_SL:
        return None
    if None in (swing_low, swing_high):
        return None
    if swing_high <= swing_low:
        return None
    min_sl_dist = float(CONFIG.get("MIN_SL_DISTANCE", 4.0))
    sl_buffer = float(CONFIG.get("SL_BUFFER", 1.0))
    sl_fib = fib_retracement(swing_low, swing_high, 0.786)
    if direction == "BUY":
        sl = sl_fib - sl_buffer
        if sl >= entry:
            return None
        if (entry - sl) < min_sl_dist:
            sl = entry - min_sl_dist
        return sl
    else:
        sl = sl_fib + sl_buffer
        if sl <= entry:
            return None
        if (sl - entry) < min_sl_dist:
            sl = entry + min_sl_dist
        return sl


# ============================================================
# SECTION: SESSION
# ============================================================
def _minutes(hhmm):
    h, m = map(int, str(hhmm).split(":"))
    return h * 60 + m


def _in_time_range(now_minutes, start, end):
    start_m = _minutes(start)
    end_m = _minutes(end)
    if start_m == end_m:
        return True
    if start_m < end_m:
        return start_m <= now_minutes < end_m
    return now_minutes >= start_m or now_minutes < end_m


def detect_sessions():
    global SESSION_STATUS
    now = datetime.now(WIB)
    now_minutes = now.hour * 60 + now.minute
    active = []
    for name in ("ASIA", "LONDON", "NEW_YORK", "LONDON_NEW_YORK_OVERLAP"):
        cfg = SESSION_CONFIG.get(name, {})
        if _in_time_range(now_minutes, cfg.get("START", "00:00"), cfg.get("END", "00:00")):
            active.append(name)
    if "LONDON_NEW_YORK_OVERLAP" in active:
        SESSION_STATUS = "LONDON + NEW YORK (OVERLAP)"
    elif "NEW_YORK" in active:
        SESSION_STATUS = "NEW YORK"
    elif "LONDON" in active:
        SESSION_STATUS = "LONDON"
    elif "ASIA" in active:
        SESSION_STATUS = "ASIA"
    else:
        SESSION_STATUS = "OUT OF SESSION"
    return active


def in_session():
    active = detect_sessions()
    if not USE_SESSION_FILTER or not SESSION_CONFIG.get("ENABLED", True):
        return True
    for name in active:
        if SESSION_CONFIG.get(name, {}).get("ENABLED", False):
            return True
    return False


def get_session_status_text():
    active = detect_sessions()
    enabled = [n for n in active if SESSION_CONFIG.get(n, {}).get("ENABLED", False)]
    if not active:
        return SESSION_STATUS, "NO ACTIVE SESSION", False
    if not USE_SESSION_FILTER or not SESSION_CONFIG.get("ENABLED", True):
        return SESSION_STATUS, ", ".join(active), True
    return SESSION_STATUS, ", ".join(active), bool(enabled)


# ============================================================
# SECTION: DAILY LOSS
# ============================================================
def check_daily_loss():
    global daily_start_balance, daily_date, trading_disabled_today
    now = datetime.now(WIB).date()
    if now != daily_date:
        daily_date = now
        account = mt5.account_info()
        daily_start_balance = account.balance if account else daily_start_balance
        trading_disabled_today = False
        runtime_message("New trading day. Daily reset.")
        persist_state()
    account = mt5.account_info()
    if account is None:
        return 0.0, 0.0
    daily_pnl = account.balance - daily_start_balance
    daily_loss_percent = (-daily_pnl / daily_start_balance) * 100 if daily_pnl < 0 and daily_start_balance > 0 else 0
    was_disabled = trading_disabled_today
    if daily_loss_percent >= float(CONFIG.get("MAX_DAILY_LOSS_PCT", 20.0)):
        trading_disabled_today = True
    if trading_disabled_today != was_disabled:
        persist_state()
    return daily_pnl, round(daily_loss_percent, 2)


# ============================================================
# SECTION: MODEL BASE CLASS
# ============================================================
class BaseModel:
    NAME = "BASE"
    FIB_ZONE = [0.382, 0.786]
    ZONE_TOLERANCE_ATR = 1.0
    HTF_REQUIRED = True

    def __init__(self, ctx):
        self.ctx = ctx
        self.result = {
            "model": self.NAME,
            "passed": False,
            "direction": None,
            "reason": "",
            "swing_low": None,
            "swing_high": None,
            "fib_ok": False,
            "poi_zone": None,
            "choch": None,
            "wick": None,
            "sweep": False,
            "gate_progress": {
                "htf": False, "zone": False, "confirm": False,
                "swing": False, "fib": False,
            },
            "gate_score": 0,
            "gate_total": 5,
        }

    def _diag(self, reason):
        self.result["reason"] = reason

    def _finalize_gate_score(self):
        gp = self.result.get("gate_progress", {})
        self.result["gate_score"] = sum(1 for v in gp.values() if v)
        self.result["gate_total"] = len(gp)

    def gate_htf(self):
        if not self.HTF_REQUIRED:
            self.result["gate_progress"]["htf"] = True
            return True
        htf = self.ctx.get("htf_trend", "SIDEWAYS")
        if htf not in ("BULLISH", "BEARISH"):
            self._diag(f"HTF={htf}")
            return False
        self.result["gate_progress"]["htf"] = True
        return True

    def gate_zone(self, direction):
        df_ltf = self.ctx["df_ltf"]
        atr_now = self.ctx.get("atr_now", 3.0)
        tolerance = atr_now * self.ZONE_TOLERANCE_ATR
        entry_price = df_ltf['close'].iloc[-1]
        if direction == "BUY":
            in_poi, zone = price_in_smc_zone(entry_price, self.ctx["demand_zones"], "DEMAND", tolerance=tolerance)
        else:
            in_poi, zone = price_in_smc_zone(entry_price, self.ctx["supply_zones"], "SUPPLY", tolerance=tolerance)
        if not in_poi:
            self._diag(f"no-POI({direction})")
            return False
        self.result["poi_zone"] = zone
        self.result["gate_progress"]["zone"] = True
        return True

    def gate_confirmation(self, direction, has_sweep):
        choch_ok = (
            (direction == "BUY" and self.ctx.get("choch_ltf") == "BULL_CHoCH") or
            (direction == "SELL" and self.ctx.get("choch_ltf") == "BEAR_CHoCH")
        )
        wick_ok = (
            (direction == "BUY" and self.ctx.get("wick_ltf") == "BULL") or
            (direction == "SELL" and self.ctx.get("wick_ltf") == "BEAR")
        )
        self.result["confirm_detail"] = {
            "sweep": has_sweep, "choch": choch_ok, "wick": wick_ok,
            "count": sum([has_sweep, choch_ok, wick_ok]),
        }
        if self.NAME == "SWEEP":
            if has_sweep and (wick_ok or choch_ok):
                self.result["gate_progress"]["confirm"] = True
                return True
            self._diag(f"no-confirm(sweep={has_sweep},wick={wick_ok},choch={choch_ok})")
            return False
        confirmations = sum([has_sweep, choch_ok, wick_ok])
        if confirmations >= 2:
            self.result["gate_progress"]["confirm"] = True
            return True
        self._diag(f"confirm={confirmations}/3 (need 2)")
        return False

    def gate_swing(self, direction):
        df_ltf = self.ctx["df_ltf"]
        swing_low, swing_high = find_last_swing_for_fib(df_ltf, direction)
        if swing_low is None:
            self._diag(f"no-Swing({direction})")
            return False
        size = abs(swing_high - swing_low)
        if size < float(CONFIG.get("MIN_SWING_SIZE", 1.0)):
            self._diag(f"swing-small({size:.1f})")
            return False
        self.result["swing_low"] = swing_low
        self.result["swing_high"] = swing_high
        self.result["gate_progress"]["swing"] = True
        return True

    def gate_fib(self, direction):
        df_ltf = self.ctx["df_ltf"]
        entry_price = df_ltf['close'].iloc[-1]
        zone_lo, zone_hi = self.FIB_ZONE
        fib_ok = in_fib_zone(entry_price, self.result["swing_low"], self.result["swing_high"], zone_lo, zone_hi)
        if USE_FIB_GATE and not fib_ok:
            self._diag(f"no-FibZone({zone_lo}-{zone_hi})")
            return False
        if not USE_FIB_GATE and not fib_ok:
            self._diag(f"flag-fib-out({zone_lo}-{zone_hi})")
        self.result["fib_ok"] = fib_ok
        if not USE_FIB_GATE or fib_ok:
            self.result["gate_progress"]["fib"] = True
        return True

    def evaluate(self):
        raise NotImplementedError


# ============================================================
# SECTION: CONTINUATION MODEL
# ============================================================
class ContinuationModel(BaseModel):
    NAME = "CONTINUATION"
    FIB_ZONE = CONFIG.get("FIB_ZONE_CONTINUATION", [0.382, 0.786])
    ZONE_TOLERANCE_ATR = float(CONFIG.get("ZONE_TOLERANCE_ATR", 1.0))
    HTF_REQUIRED = True

    def evaluate(self):
        if not self.gate_htf():
            self._finalize_gate_score()
            return self.result
        htf = self.ctx.get("htf_trend", "SIDEWAYS")
        direction = "BUY" if htf == "BULLISH" else "SELL"
        self.result["direction"] = direction
        if not self.gate_zone(direction):
            self._finalize_gate_score()
            return self.result
        has_sweep = self.ctx.get("sweep_buy", False) if direction == "BUY" else self.ctx.get("sweep_sell", False)
        if not self.gate_confirmation(direction, has_sweep):
            self._finalize_gate_score()
            return self.result
        self.result["choch"] = self.ctx.get("choch_ltf")
        self.result["wick"] = self.ctx.get("wick_ltf")
        self.result["sweep"] = has_sweep
        if not self.gate_swing(direction):
            self._finalize_gate_score()
            return self.result
        if not self.gate_fib(direction):
            self._finalize_gate_score()
            return self.result
        self.result["passed"] = True
        self._finalize_gate_score()
        return self.result


# ============================================================
# SECTION: REVERSAL MODEL
# ============================================================
class ReversalModel(BaseModel):
    NAME = "REVERSAL"
    FIB_ZONE = CONFIG.get("FIB_ZONE_REVERSAL", [0.5, 0.886])
    ZONE_TOLERANCE_ATR = float(CONFIG.get("ZONE_TOLERANCE_ATR", 1.0))
    HTF_REQUIRED = False

    def evaluate(self):
        mss = self.ctx.get("choch_ltf")
        rej = self.ctx.get("wick_ltf")
        sweep_buy = self.ctx.get("sweep_buy", False)
        sweep_sell = self.ctx.get("sweep_sell", False)
        direction = None
        if mss == "BULL_CHoCH":
            direction = "BUY"
        elif mss == "BEAR_CHoCH":
            direction = "SELL"
        elif rej == "BULL":
            direction = "BUY"
        elif rej == "BEAR":
            direction = "SELL"
        elif sweep_buy:
            direction = "BUY"
        elif sweep_sell:
            direction = "SELL"
        if direction is None:
            self._diag("no-Sweep/CHoCH/wick")
            self._finalize_gate_score()
            return self.result
        self.result["direction"] = direction
        has_sweep = (direction == "BUY" and sweep_buy) or (direction == "SELL" and sweep_sell)
        if not self.gate_zone(direction):
            self._finalize_gate_score()
            return self.result
        if not self.gate_confirmation(direction, has_sweep):
            self._finalize_gate_score()
            return self.result
        self.result["choch"] = mss
        self.result["wick"] = rej
        self.result["sweep"] = has_sweep
        if not self.gate_swing(direction):
            self._finalize_gate_score()
            return self.result
        if not self.gate_fib(direction):
            self._finalize_gate_score()
            return self.result
        self.result["passed"] = True
        self._finalize_gate_score()
        return self.result


# ============================================================
# SECTION: SWEEP MODEL
# ============================================================
class SweepModel(BaseModel):
    NAME = "SWEEP"
    FIB_ZONE = CONFIG.get("FIB_ZONE_SWEEP", [0.382, 0.786])
    ZONE_TOLERANCE_ATR = float(CONFIG.get("ZONE_TOLERANCE_ATR", 1.0))
    HTF_REQUIRED = False

    def evaluate(self):
        sweep_buy = self.ctx.get("sweep_buy", False)
        sweep_sell = self.ctx.get("sweep_sell", False)
        direction = None
        if sweep_buy:
            direction = "BUY"
        elif sweep_sell:
            direction = "SELL"
        if direction is None:
            self._diag("no-Sweep")
            self._finalize_gate_score()
            return self.result
        self.result["direction"] = direction
        if not self.gate_confirmation(direction, has_sweep=True):
            self._finalize_gate_score()
            return self.result
        if not self.gate_zone(direction):
            self._finalize_gate_score()
            return self.result
        self.result["choch"] = self.ctx.get("choch_ltf")
        self.result["wick"] = self.ctx.get("wick_ltf")
        self.result["sweep"] = True
        if not self.gate_swing(direction):
            self._finalize_gate_score()
            return self.result
        if not self.gate_fib(direction):
            self._finalize_gate_score()
            return self.result
        self.result["passed"] = True
        self._finalize_gate_score()
        return self.result


# ============================================================
# SECTION: CONFLUENCE SCORE
# ============================================================
def calculate_confluence(model_result, ctx, session_ok):
    if not model_result or not model_result.get("passed"):
        return 0, []
    score = 0
    met = []
    direction = model_result["direction"]
    htf = ctx.get("htf_trend", "SIDEWAYS")
    want_htf = "BULLISH" if direction == "BUY" else "BEARISH"
    if htf == want_htf:
        score += int(CONFIG.get("CONFLUENCE_HTF_SCORE", 20))
        met.append("HTF")
    if model_result.get("poi_zone"):
        score += int(CONFIG.get("CONFLUENCE_POI_SCORE", 20))
        met.append("POI")
    if model_result.get("choch"):
        score += int(CONFIG.get("CONFLUENCE_CHOCH_SCORE", 15))
        met.append("CHoCH")
    if model_result.get("wick"):
        score += int(CONFIG.get("CONFLUENCE_WICK_SCORE", 10))
        met.append("WICK")
    if model_result.get("fib_ok"):
        score += int(CONFIG.get("CONFLUENCE_FIB_SCORE", 15))
        met.append("FIB")
    if session_ok:
        score += int(CONFIG.get("CONFLUENCE_SESSION_SCORE", 10))
        met.append("SESSION")
    if CONFIG.get("USE_FVG", True):
        fvg_dir = "BULL" if direction == "BUY" else "BEAR"
        active_fvgs = get_active_fvg(fvg_dir)
        if active_fvgs:
            score += int(CONFIG.get("CONFLUENCE_FVG_SCORE", 5))
            met.append(f"FVG({len(active_fvgs)})")
    met.append("RR_PENDING")
    return score, met


def add_rr_score(score, met, rr):
    if "RR_PENDING" in met:
        met.remove("RR_PENDING")
    if rr >= float(CONFIG.get("CONFLUENCE_RR_THRESHOLD", 2.0)):
        score += int(CONFIG.get("CONFLUENCE_RR_SCORE", 10))
        met.append("RR")
    return score, met


def evaluate_all_models(ctx, session_ok):
    models = []
    if CONFIG.get("USE_MODEL_CONTINUATION", True):
        models.append(ContinuationModel(ctx))
    if CONFIG.get("USE_MODEL_REVERSAL", False):
        models.append(ReversalModel(ctx))
    if CONFIG.get("USE_MODEL_SWEEP", False):
        models.append(SweepModel(ctx))
    results = []
    for model in models:
        r = model.evaluate()
        r.setdefault("confluence", 0)
        r.setdefault("confluence_met", [])
        if r.get("passed"):
            score, met = calculate_confluence(r, ctx, session_ok)
            r["confluence"] = score
            r["confluence_met"] = met
        results.append(r)
    return results


# ============================================================
# SECTION: SL RESOLVER
# ============================================================
def resolve_sl(entry, direction, atr_raw, swing_low=None, swing_high=None):
    try:
        entry = float(entry)
        atr_raw = float(atr_raw)
    except (TypeError, ValueError):
        return None, "INVALID_INPUT"
    if entry <= 0:
        return None, "INVALID_ENTRY"
    if atr_raw <= 0:
        return None, "NO_ATR"
    direction = str(direction).upper()
    if not CONFIG.get("USE_FIB_SL", False):
        atr_mult = float(CONFIG.get("SL_ATR_MULT", 1.5))
        min_sl_distance = float(CONFIG.get("MIN_SL_DISTANCE", 4.0))
        max_sl_points = float(CONFIG.get("MAX_SL_POINTS", 15.0))
        sl_distance = atr_raw * atr_mult
        sl_distance = max(sl_distance, min_sl_distance)
        sl_distance = min(sl_distance, max_sl_points)
        if direction == "BUY":
            sl = entry - sl_distance
        elif direction == "SELL":
            sl = entry + sl_distance
        else:
            return None, "INVALID_DIRECTION"
        return float(sl), "ATR"
    try:
        swing_low = float(swing_low)
        swing_high = float(swing_high)
    except (TypeError, ValueError):
        return None, "INVALID_FIB_SWING"
    if swing_low <= 0 or swing_high <= 0:
        return None, "INVALID_FIB_SWING"
    if swing_high <= swing_low:
        return None, "INVALID_FIB_RANGE"
    sl = resolve_fib_sl(swing_low, swing_high, direction, entry)
    if sl is None:
        return None, "FIB_SL_FAILED"
    return float(sl), "FIB"


# ============================================================
# SECTION: TP RESOLVER
# ============================================================
def resolve_tp(entry, sl, direction):
    risk = abs(entry - sl)
    if risk <= 0:
        return None
    rr1 = float(CONFIG.get("TP_RR_TP1", 1.0))
    rr2 = float(CONFIG.get("TP_RR_TP2", 2.0))
    rr3 = float(CONFIG.get("TP_RR_TP3", 3.0))
    if direction == "BUY":
        tp1 = entry + risk * rr1
        tp2 = entry + risk * rr2
        tp3 = entry + risk * rr3
    else:
        tp1 = entry - risk * rr1
        tp2 = entry - risk * rr2
        tp3 = entry - risk * rr3
    return {"tp1": tp1, "tp2": tp2, "tp3": tp3, "mode": "RR", "risk": risk,
            "rr1": rr1, "rr2": rr2, "rr3": rr3}


def validate_tp(tp_plan, entry, sl, direction):
    if tp_plan is None:
        return False, 0.0, None
    min_rr = float(CONFIG.get("MIN_RR_TP3", 1.2))
    hard_max_rr = float(CONFIG.get("HARD_MAX_RR_TP3", 8.0))
    risk = abs(entry - sl)
    if risk <= 0:
        return False, 0.0, tp_plan
    reward = abs(tp_plan["tp3"] - entry)
    rr = reward / risk
    if rr > hard_max_rr:
        return False, rr, tp_plan
    if rr >= min_rr:
        return True, rr, tp_plan
    if direction == "BUY":
        adjusted = entry + risk * min_rr
        if adjusted < tp_plan["tp3"]:
            new_plan = dict(tp_plan)
            new_plan["tp3"] = adjusted
            return True, min_rr, new_plan
    else:
        adjusted = entry - risk * min_rr
        if adjusted > tp_plan["tp3"]:
            new_plan = dict(tp_plan)
            new_plan["tp3"] = adjusted
            return True, min_rr, new_plan
    return False, rr, tp_plan


# ============================================================
# SECTION: LOT CALCULATOR
# ============================================================
def _clamp_lot(raw_lot, symbol_info=None):
    if symbol_info is None:
        symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        return float(CONFIG.get("LOT_SIZE", 0.01))
    broker_min = float(symbol_info.volume_min or 0.01)
    broker_max = float(symbol_info.volume_max or 100.0)
    broker_step = float(symbol_info.volume_step or 0.01)
    hard_cap = float(CONFIG.get("HARD_LOT_CAP", 0.06))
    eff_max = min(float(CONFIG.get("MAX_LOT_SIZE", 0.06)), hard_cap, broker_max)
    eff_min = max(float(CONFIG.get("MIN_LOT_SIZE", 0.01)), broker_min)
    lot = max(eff_min, min(eff_max, float(raw_lot)))
    if broker_step > 0:
        lot = round(lot / broker_step) * broker_step
    return round(lot, 8)


def calculate_lot_by_confluence(confluence_score, symbol_info=None):
    if confluence_score >= float(CONFIG.get("CONFLUENCE_TIER_3", 90)):
        lot = float(CONFIG.get("LOT_TIER_3", 0.06))
    elif confluence_score >= float(CONFIG.get("CONFLUENCE_TIER_2", 80)):
        lot = float(CONFIG.get("LOT_TIER_2", 0.03))
    elif confluence_score >= float(CONFIG.get("CONFLUENCE_TIER_1", 75)):
        lot = float(CONFIG.get("LOT_TIER_1", 0.01))
    else:
        lot = float(CONFIG.get("LOT_SIZE", 0.01))
    return _clamp_lot(lot, symbol_info)


# ============================================================
# SECTION: GUARDS
# ============================================================
def check_margin_guard(lot, symbol_info=None):
    try:
        if symbol_info is None:
            symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            return True, "no symbol"
        account = mt5.account_info()
        if account is None:
            return True, "no account"
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            return True, "no tick"
        try:
            margin_needed = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, SYMBOL, lot, tick.ask)
        except Exception:
            margin_needed = None
        if margin_needed is None or margin_needed <= 0:
            return True, "skip"
        free_margin = float(account.margin_free)
        if free_margin <= 0:
            return False, "no free margin"
        usage_pct = (margin_needed / free_margin) * 100.0
        safety_pct = float(CONFIG.get("MARGIN_SAFETY_PCT", 30.0))
        if usage_pct > safety_pct:
            return False, f"margin {usage_pct:.1f}% > {safety_pct:.0f}%"
        return True, f"margin {usage_pct:.1f}%"
    except Exception:
        return True, "skip err"


# ============================================================
# SECTION: RISK CALCULATOR
# ============================================================
def calculate_risk(model_result, entry, atr_raw, symbol_info, session_ok):
    result = {
        "ok": False, "reason": "", "sl": None, "sl_source": "",
        "tp_plan": None, "rr": 0.0, "lot": 0.0,
        "confluence": model_result.get("confluence", 0),
        "confluence_met": model_result.get("confluence_met", []),
    }
    direction = model_result["direction"]

    def _price_float(value):
        try:
            if value is None or str(value).strip() == "":
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    swing_low = _price_float(model_result.get("swing_low"))
    swing_high = _price_float(model_result.get("swing_high"))

    sl, sl_source = resolve_sl(entry, direction, atr_raw, swing_low=swing_low, swing_high=swing_high)
    if sl is None:
        result["reason"] = "SL=0 skip"
        return result
    result["sl"] = sl
    result["sl_source"] = sl_source

    tp_plan = resolve_tp(entry, sl, direction)
    if tp_plan is None:
        result["reason"] = "TP=None skip"
        return result

    tp_valid, rr, tp_plan = validate_tp(tp_plan, entry, sl, direction)
    if not tp_valid:
        if rr > float(CONFIG.get("HARD_MAX_RR_TP3", 8.0)):
            result["reason"] = f"RR too high 1:{rr:.1f}"
        else:
            result["reason"] = f"RR < min (actual {rr:.2f})"
        return result
    result["tp_plan"] = tp_plan
    result["rr"] = rr

    conf_score = result["confluence"]
    conf_met = result["confluence_met"]
    conf_score, conf_met = add_rr_score(conf_score, conf_met, rr)
    result["confluence"] = conf_score
    result["confluence_met"] = conf_met

    min_conf = float(CONFIG.get("MIN_CONFLUENCE", 75))
    if conf_score < min_conf:
        result["reason"] = f"conf {conf_score}% < {int(min_conf)}%"
        return result

    lot = calculate_lot_by_confluence(conf_score, symbol_info)
    result["lot"] = lot

    margin_ok, margin_reason = check_margin_guard(lot, symbol_info)
    if not margin_ok:
        result["reason"] = margin_reason
        return result

    result["ok"] = True
    return result


# ============================================================
# SECTION: PARTIAL CLOSE PLAN
# ============================================================
def _round_to_step(vol, step):
    if step <= 0:
        return vol
    return round(vol / step) * step


def register_partial_plan(ticket, tp_plan, orig_volume, model_name, entry_price, direction):
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        return
    vol_min = float(symbol_info.volume_min or 0.01)
    vol_step = float(symbol_info.volume_step or 0.01)
    lot = float(orig_volume)
    min_lot_for_partial = float(CONFIG.get("PARTIAL_MIN_LOT", 0.03))
    if lot < min_lot_for_partial:
        runtime_message(f"Partial #{ticket}: lot {lot} < min {min_lot_for_partial}, skip")
        return
    mode = str(CONFIG.get("PARTIAL_MODE", "PERCENT")).upper()
    if mode == "LOT":
        raw1 = float(CONFIG.get("PARTIAL_LOT_1", 0.01))
        raw2 = float(CONFIG.get("PARTIAL_LOT_2", 0.01))
    else:
        pct1 = float(CONFIG.get("PARTIAL_PCT_1", 33))
        pct2 = float(CONFIG.get("PARTIAL_PCT_2", 33))
        raw1 = lot * (pct1 / 100.0)
        raw2 = lot * (pct2 / 100.0)
    v1 = _round_to_step(raw1, vol_step)
    v2 = _round_to_step(raw2, vol_step)
    tp1_en = v1 >= vol_min and v1 < lot
    tp2_en = v2 >= vol_min and v2 < lot
    total_vol = (v1 if tp1_en else 0) + (v2 if tp2_en else 0)
    if total_vol >= lot:
        if tp2_en:
            v2 = 0.0
            tp2_en = False
            total_vol = v1 if tp1_en else 0
        if total_vol >= lot and tp1_en:
            v1 = 0.0
            tp1_en = False
    if not (tp1_en or tp2_en):
        runtime_message(f"Partial #{ticket}: lot {lot} terlalu kecil untuk partial")
        return
    PARTIAL_STATE[ticket] = {
        "tp1": tp_plan["tp1"], "tp2": tp_plan["tp2"], "tp3": tp_plan["tp3"],
        "tp1_done": False, "tp2_done": False, "tp3_done": False,
        "tp1_enabled": tp1_en, "tp2_enabled": tp2_en,
        "vol1": v1, "vol2": v2, "orig_volume": lot,
        "model": model_name, "entry": entry_price, "direction": direction, "mode": mode,
    }
    persist_state()
    marks = []
    if tp1_en: marks.append(f"TP1({v1:g})")
    if tp2_en: marks.append(f"TP2({v2:g})")
    runtime_message(f"Partial #{ticket} lot {lot} [{mode}]: {'/'.join(marks)} (TP3=broker)")


# ============================================================
# SECTION: REBUILD
# ============================================================
def rebuild_position_meta():
    try:
        positions = mt5.positions_get(symbol=SYMBOL) or []
        active_tickets = {int(p.ticket) for p in positions}
        changed = False

        for tk in list(POSITION_META.keys()):
            try:
                ticket = int(tk)
            except Exception:
                POSITION_META.pop(tk, None)
                changed = True
                continue
            if ticket not in active_tickets:
                POSITION_META.pop(tk, None)
                changed = True

        magic = int(CONFIG.get("MAGIC", 777777))

        for pos in positions:
            ticket = int(pos.ticket)
            old = POSITION_META.get(ticket, {})
            comment_upper = str(getattr(pos, "comment", "") or "").upper()

            if "CONTINUATION" in comment_upper:
                model_name = "CONTINUATION"
            elif "REVERSAL" in comment_upper:
                model_name = "REVERSAL"
            elif "SWEEP" in comment_upper:
                model_name = "SWEEP"
            else:
                old_model = str(old.get("model", "")).upper()
                if old_model in ("CONTINUATION", "REVERSAL", "SWEEP", "MANUAL", "RECOVERED"):
                    model_name = old_model
                elif int(getattr(pos, "magic", 0) or 0) != magic:
                    model_name = "MANUAL"
                else:
                    model_name = "RECOVERED"

            current_volume = float(getattr(pos, "volume", 0.0) or 0.0)
            old_orig = float(old.get("orig_volume", 0.0) or 0.0)
            orig_volume = max(old_orig, current_volume) if old_orig > 0 else current_volume

            max_move = float(old.get("max_move", 0.0) or 0.0)
            try:
                entry = float(pos.price_open)
                sl = float(pos.sl or 0.0)
                if sl > 0:
                    if pos.type == mt5.POSITION_TYPE_BUY and sl < entry:
                        max_move = max(max_move, entry - sl)
                    elif pos.type == mt5.POSITION_TYPE_SELL and sl > entry:
                        max_move = max(max_move, sl - entry)
            except Exception:
                pass

            if model_name in ("CONTINUATION", "REVERSAL", "SWEEP"):
                source = "position_comment_rebuild"
            elif old.get("source"):
                source = old.get("source")
            elif model_name == "MANUAL":
                source = "manual_position"
            else:
                source = "position_meta_rebuild"

            new_meta = {
                "model": model_name,
                "sl_source": old.get("sl_source", "RECOVERED"),
                "orig_volume": orig_volume,
                "max_move": max_move,
                "source": source,
            }
            if old != new_meta:
                POSITION_META[ticket] = new_meta
                changed = True
                runtime_message(f"Recovered meta #{ticket} ({model_name}) lot={current_volume:g}")

        if changed:
            persist_state()
    except Exception:
        log_error(f"rebuild_position_meta: {traceback.format_exc()}")


def rebuild_partial_plans():
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions:
            if PARTIAL_STATE:
                PARTIAL_STATE.clear()
                persist_state()
            return

        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            runtime_message("Partial recovery: symbol_info unavailable")
            return

        vol_min = float(symbol_info.volume_min or 0.01)
        vol_step = float(symbol_info.volume_step or 0.01)
        active_tickets = {int(p.ticket) for p in positions}

        changed = False
        for ticket in list(PARTIAL_STATE.keys()):
            try:
                ticket_int = int(ticket)
            except Exception:
                PARTIAL_STATE.pop(ticket, None)
                changed = True
                continue
            if ticket_int not in active_tickets:
                PARTIAL_STATE.pop(ticket, None)
                changed = True

        for pos in positions:
            ticket = int(pos.ticket)
            meta = POSITION_META.get(ticket, {})
            model_name = str(meta.get("model", "")).upper()
            if model_name not in ("CONTINUATION", "REVERSAL", "SWEEP", "MANUAL", "RECOVERED"):
                model_name = "RECOVERED"
                POSITION_META[ticket] = {
                    "model": model_name, "sl_source": "RECOVERED",
                    "orig_volume": float(pos.volume), "max_move": 0.0,
                    "source": "partial_recovery",
                }
                meta = POSITION_META[ticket]
                changed = True

            try:
                entry = float(pos.price_open)
            except Exception:
                continue
            if entry <= 0:
                continue

            direction = "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL"

            try:
                broker_sl = float(pos.sl or 0.0)
            except Exception:
                broker_sl = 0.0

            if broker_sl > 0 and abs(entry - broker_sl) > 0:
                risk = abs(entry - broker_sl)
            else:
                atr_fb = get_atr_current()
                if atr_fb is None or atr_fb <= 0:
                    atr_fb = 3.0
                risk = atr_fb * float(CONFIG.get("SL_ATR_MULT", 1.5))
                runtime_message(f"Recovery #{ticket}: SL broker tidak ada, pakai ATR risk={risk:.2f}")

            if risk <= 0:
                runtime_message(f"Recovery #{ticket}: risk=0, skip")
                continue

            try:
                tp3 = float(pos.tp or 0.0)
            except Exception:
                tp3 = 0.0

            if tp3 <= 0:
                rr3 = float(CONFIG.get("TP_RR_TP3", 3.0))
                if direction == "BUY":
                    tp3 = entry + (risk * rr3)
                else:
                    tp3 = entry - (risk * rr3)
                runtime_message(f"Recovery #{ticket}: TP broker tidak ada, pakai RR TP3={tp3:.2f}")

            rr1 = float(CONFIG.get("TP_RR_TP1", 1.0))
            rr2 = float(CONFIG.get("TP_RR_TP2", 2.0))
            if direction == "BUY":
                tp1 = entry + (risk * rr1)
                tp2 = entry + (risk * rr2)
            else:
                tp1 = entry - (risk * rr1)
                tp2 = entry - (risk * rr2)

            current_volume = float(pos.volume)
            old_orig_volume = float(meta.get("orig_volume", 0.0) or 0.0)
            if old_orig_volume > 0:
                orig_volume = max(old_orig_volume, current_volume)
            else:
                orig_volume = current_volume
                meta["orig_volume"] = orig_volume
                POSITION_META[ticket] = meta
                changed = True

            old_plan = PARTIAL_STATE.get(ticket)
            plan_valid = False
            if isinstance(old_plan, dict):
                required = ("tp1", "tp2", "tp3", "tp1_done", "tp2_done", "tp3_done",
                            "tp1_enabled", "tp2_enabled", "vol1", "vol2",
                            "orig_volume", "model", "entry", "direction")
                plan_valid = all(key in old_plan for key in required)

            if plan_valid:
                old_plan["tp3"] = tp3
                old_plan["model"] = model_name
                old_plan["entry"] = entry
                old_plan["direction"] = direction
                old_plan["orig_volume"] = max(float(old_plan.get("orig_volume", 0.0) or 0.0), orig_volume)
                continue

            mode = str(CONFIG.get("PARTIAL_MODE", "PERCENT")).upper()
            if mode == "LOT":
                raw1 = float(CONFIG.get("PARTIAL_LOT_1", 0.01))
                raw2 = float(CONFIG.get("PARTIAL_LOT_2", 0.01))
            else:
                pct1 = float(CONFIG.get("PARTIAL_PCT_1", 33))
                pct2 = float(CONFIG.get("PARTIAL_PCT_2", 33))
                raw1 = orig_volume * pct1 / 100.0
                raw2 = orig_volume * pct2 / 100.0

            v1 = round(_round_to_step(raw1, vol_step), 8)
            v2 = round(_round_to_step(raw2, vol_step), 8)

            tp1_enabled = (v1 >= vol_min and v1 < orig_volume)
            tp2_enabled = (v2 >= vol_min and v2 < orig_volume)

            total_partial = (v1 if tp1_enabled else 0.0) + (v2 if tp2_enabled else 0.0)
            if total_partial >= orig_volume:
                if tp2_enabled:
                    v2 = 0.0
                    tp2_enabled = False
                total_partial = v1 if tp1_enabled else 0.0
                if total_partial >= orig_volume:
                    v1 = 0.0
                    tp1_enabled = False

            if not (tp1_enabled or tp2_enabled):
                runtime_message(f"Recovery #{ticket}: partial tidak tersedia (lot={orig_volume:g})")
                tp1_enabled = False
                tp2_enabled = False
                v1 = 0.0
                v2 = 0.0

            current_ratio = current_volume / orig_volume if orig_volume > 0 else 1.0
            old_tp1_done = False
            old_tp2_done = False
            old_tp3_done = False
            if isinstance(old_plan, dict):
                old_tp1_done = bool(old_plan.get("tp1_done", False))
                old_tp2_done = bool(old_plan.get("tp2_done", False))
                old_tp3_done = bool(old_plan.get("tp3_done", False))
            if current_ratio < 0.99:
                old_tp1_done = True
            if current_ratio < 0.60:
                old_tp2_done = True

            PARTIAL_STATE[ticket] = {
                "tp1": float(tp1), "tp2": float(tp2), "tp3": float(tp3),
                "tp1_done": old_tp1_done, "tp2_done": old_tp2_done, "tp3_done": old_tp3_done,
                "tp1_enabled": tp1_enabled, "tp2_enabled": tp2_enabled,
                "vol1": float(v1), "vol2": float(v2),
                "orig_volume": float(orig_volume), "model": model_name,
                "entry": float(entry), "direction": direction, "mode": mode,
            }
            changed = True
            runtime_message(f"RECOVER PARTIAL #{ticket} {model_name} TP1={tp1:.2f} TP2={tp2:.2f} TP3={tp3:.2f} V1={v1:g} V2={v2:g}")

        if changed:
            persist_state()
    except Exception:
        log_error(f"rebuild_partial_plans: {traceback.format_exc()}")


# ============================================================
# SECTION: ORDER EXECUTION HELPERS
# ============================================================
def _retryable_retcode(retcode):
    """Retcode broker yang layak di-retry (hard-code nilai MT5)."""
    retry_codes = {
        10004,  # TRADE_RETCODE_REQUOTE
        10020,  # TRADE_RETCODE_PRICE_CHANGED
        10021,  # TRADE_RETCODE_PRICE_OFF
        10012,  # TRADE_RETCODE_TIMEOUT
        10031,  # TRADE_RETCODE_CONNECTION
        10024,  # TRADE_RETCODE_TOO_MANY_REQUESTS
        10026,  # TRADE_RETCODE_SERVER_BUSY
        10018,  # TRADE_RETCODE_TRADE_CONTEXT_BUSY
    }
    return retcode in retry_codes


def _order_send_retry(request, retries=None):
    retries = int(CONFIG.get("ORDER_RETRY_COUNT", 3) if retries is None else retries)
    delay = float(CONFIG.get("ORDER_RETRY_DELAY", 0.50))
    last_result = None
    for attempt in range(max(1, retries)):
        try:
            result = mt5.order_send(request)
        except Exception:
            result = None
            log_error(f"order_send exception attempt={attempt + 1}: {traceback.format_exc()}")
        last_result = result
        if result is not None:
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return result
            if not _retryable_retcode(result.retcode):
                return result
        if attempt < retries - 1:
            time.sleep(delay)
    return last_result


def _get_supported_filling(symbol_info):
    try:
        fm = int(symbol_info.filling_mode)
    except Exception:
        fm = 0
    modes = []
    if fm & 1:
        modes.append(mt5.ORDER_FILLING_FOK)
    if fm & 2:
        modes.append(mt5.ORDER_FILLING_IOC)
    modes.append(mt5.ORDER_FILLING_RETURN)
    if len(modes) == 1:
        modes = [mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]
    return modes


def _close_partial(position, close_volume, symbol_info):
    try:
        close_volume = max(symbol_info.volume_min,
                           round(close_volume / symbol_info.volume_step) * symbol_info.volume_step)
        close_volume = min(close_volume, position.volume)
        if close_volume < symbol_info.volume_min:
            log_error(f"_close_partial #{position.ticket}: vol {close_volume} < min {symbol_info.volume_min}")
            return False

        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            log_error(f"_close_partial #{position.ticket}: no tick")
            return False
        price = tick.bid if position.type == 0 else tick.ask
        filling_modes = _get_supported_filling(symbol_info)
        last_rc = None

        for filling in filling_modes:
            req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": position.ticket,
                "symbol": SYMBOL,
                "volume": close_volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
                "price": price,
                "deviation": int(CONFIG.get("TRADE_DEVIATION", 20)),
                "magic": int(CONFIG.get("MAGIC", 777777)),
                "comment": "PARTIAL_V6",
                "type_filling": filling,
                "type_time": mt5.ORDER_TIME_GTC,
            }
            res = _order_send_retry(req)
            if res is None:
                last_rc = "None"
                continue
            if res.retcode == mt5.TRADE_RETCODE_DONE:
                return True
            last_rc = res.retcode
            if not _retryable_retcode(res.retcode) and res.retcode not in (mt5.TRADE_RETCODE_INVALID_FILL,):
                break

        log_error(f"_close_partial #{position.ticket}: ALL FAIL rc={last_rc}")
        return False
    except Exception:
        log_error(f"_close_partial: {traceback.format_exc()}")
        return False


# ============================================================
# SECTION: MANAGE PARTIAL CLOSE
# ============================================================
def manage_partial_close():
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions:
            if PARTIAL_STATE:
                PARTIAL_STATE.clear()
                persist_state()
            return
        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            return

        active_tickets = {int(p.ticket) for p in positions}

        missing_partial = False
        for pos in positions:
            if int(pos.ticket) not in PARTIAL_STATE:
                missing_partial = True
                break
        if missing_partial:
            rebuild_position_meta()
            rebuild_partial_plans()

        changed = False
        for tk in list(PARTIAL_STATE.keys()):
            try:
                ticket = int(tk)
            except Exception:
                PARTIAL_STATE.pop(tk, None)
                changed = True
                continue
            if ticket not in active_tickets:
                PARTIAL_STATE.pop(tk, None)
                changed = True
        if changed:
            persist_state()

        if not PARTIAL_STATE:
            return

        for pos in positions:
            ticket = int(pos.ticket)
            plan = PARTIAL_STATE.get(ticket)
            if not plan:
                continue
            tick = mt5.symbol_info_tick(SYMBOL)
            if tick is None:
                continue
            current = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask

            if plan.get("tp1_enabled", False) and not plan.get("tp1_done", False):
                tp1 = float(plan.get("tp1", 0.0))
                if tp1 > 0:
                    hit = ((pos.type == mt5.POSITION_TYPE_BUY and current >= tp1) or
                           (pos.type == mt5.POSITION_TYPE_SELL and current <= tp1))
                    if hit:
                        vol = float(plan.get("vol1", 0.0))
                        if vol > 0 and vol < float(pos.volume):
                            if _close_partial(pos, vol, symbol_info):
                                plan["tp1_done"] = True
                                persist_state()
                                runtime_message(f"TP1 hit #{ticket} @ {tp1:.2f} vol {vol:g}")
                        continue

            if plan.get("tp1_done", False) and plan.get("tp2_enabled", False) and not plan.get("tp2_done", False):
                tp2 = float(plan.get("tp2", 0.0))
                if tp2 > 0:
                    hit = ((pos.type == mt5.POSITION_TYPE_BUY and current >= tp2) or
                           (pos.type == mt5.POSITION_TYPE_SELL and current <= tp2))
                    if hit:
                        vol = float(plan.get("vol2", 0.0))
                        if vol > 0 and vol < float(pos.volume):
                            if _close_partial(pos, vol, symbol_info):
                                plan["tp2_done"] = True
                                persist_state()
                                runtime_message(f"TP2 hit #{ticket} @ {tp2:.2f} vol {vol:g}")
                        continue

            if plan.get("tp2_done", False) and not plan.get("tp3_done", False):
                tp3 = float(plan.get("tp3", 0.0))
                if tp3 > 0:
                    hit = ((pos.type == mt5.POSITION_TYPE_BUY and current >= tp3) or
                           (pos.type == mt5.POSITION_TYPE_SELL and current <= tp3))
                    if hit:
                        plan["tp3_done"] = True
                        persist_state()
                        runtime_message(f"TP3 hit #{ticket} @ {tp3:.2f} (broker close)")
    except Exception:
        log_error(f"manage_partial_close: {traceback.format_exc()}")


# ============================================================
# SECTION: BREAK EVEN
# ============================================================
def manage_break_even():
    if not CONFIG.get("USE_BREAK_EVEN", True):
        return
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        return
    symbol_info = mt5.symbol_info(SYMBOL)
    digits = symbol_info.digits if symbol_info else 2
    atr_now = get_atr_current()
    if atr_now is None or atr_now <= 0:
        return
    be_trigger = atr_now * float(CONFIG.get("BE_TRIGGER_ATR", 1.5))

    for pos in positions:
        meta = POSITION_META.get(pos.ticket, {})
        model_name = meta.get("model", "")
        if not model_name:
            continue
        if pos.sl and pos.sl > 0:
            if pos.type == 0 and pos.sl >= pos.price_open:
                continue
            if pos.type == 1 and pos.sl <= pos.price_open:
                continue
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            continue
        price = tick.bid if pos.type == 0 else tick.ask
        if pos.type == 0:
            move = price - pos.price_open
        else:
            move = pos.price_open - price
        if move < be_trigger:
            continue
        if pos.type == 0:
            new_sl = round(pos.price_open + float(CONFIG.get("BE_OFFSET_PRICE", 0.10)), digits)
            old_sl = pos.sl if pos.sl and pos.sl > 0 else -1e9
            if new_sl > old_sl and new_sl < price:
                result = _order_send_retry({
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "sl": new_sl,
                    "tp": pos.tp,
                })
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    runtime_message(f"BE {model_name} BUY #{pos.ticket} SL→{new_sl}")
        else:
            new_sl = round(pos.price_open - float(CONFIG.get("BE_OFFSET_PRICE", 0.10)), digits)
            old_sl = pos.sl if pos.sl and pos.sl > 0 else 1e9
            if new_sl < old_sl and new_sl > price:
                result = _order_send_retry({
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "sl": new_sl,
                    "tp": pos.tp,
                })
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    runtime_message(f"BE {model_name} SELL #{pos.ticket} SL→{new_sl}")


# ============================================================
# SECTION: TRAILING SL
# ============================================================
def manage_trailing_sl():
    if not CONFIG.get("USE_TRAILING", True):
        return
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        return
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        return
    digits = symbol_info.digits
    atr_now = get_atr_current()
    if atr_now is None or atr_now <= 0:
        return
    trail_trigger = atr_now * float(CONFIG.get("TRAIL_TRIGGER_ATR", 2.5))
    secure_pct = float(CONFIG.get("TRAIL_SECURE_PCT", 50))

    for pos in positions:
        meta = POSITION_META.get(pos.ticket, {})
        model_name = meta.get("model", "")
        if not model_name:
            continue
        if pos.type == 0:
            current_move = pos.price_current - pos.price_open
        else:
            current_move = pos.price_open - pos.price_current
        max_move = float(meta.get("max_move", 0.0))
        if current_move > max_move:
            max_move = current_move
            meta["max_move"] = max_move
            POSITION_META[pos.ticket] = meta
            persist_state()
        if max_move < trail_trigger:
            continue
        secure_move = max_move * (secure_pct / 100.0)
        if secure_move <= 0:
            continue
        if pos.type == 0:
            new_sl = round(pos.price_open + secure_move, digits)
            old_sl = pos.sl if pos.sl and pos.sl > 0 else -1e9
            if new_sl > old_sl and new_sl < pos.price_current:
                result = _order_send_retry({
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "sl": new_sl,
                    "tp": pos.tp,
                })
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    runtime_message(f"TRAIL {model_name} BUY #{pos.ticket} SL→{new_sl} max={max_move:.2f}")
        else:
            new_sl = round(pos.price_open - secure_move, digits)
            old_sl = pos.sl if pos.sl and pos.sl > 0 else 1e9
            if new_sl < old_sl and new_sl > pos.price_current:
                result = _order_send_retry({
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "sl": new_sl,
                    "tp": pos.tp,
                })
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    runtime_message(f"TRAIL {model_name} SELL #{pos.ticket} SL→{new_sl} max={max_move:.2f}")


# ============================================================
# SECTION: MANUAL RECOVERY
# ============================================================
def calculate_dynamic_sl(atr=None):
    if atr is None:
        atr = get_atr_current()
    if atr is None or atr <= 0:
        return 4.0
    sl = atr * float(CONFIG.get("SL_ATR_MULT", 1.5))
    return max(4.0, min(20.0, sl))


def _recover_manual_position(pos, symbol_info, atr_raw, digits):
    direction = "BUY" if pos.type == 0 else "SELL"
    entry = float(pos.price_open)
    mode = str(MANUAL_PROFILE.get("SL_TP_MODE", "HYBRID")).upper()
    min_sl_price = float(MANUAL_PROFILE.get("MIN_SL_PRICE", 3.0))
    max_sl_price = float(MANUAL_PROFILE.get("MAX_SL_PRICE", 20.0))

    if mode in ("FIB", "HYBRID") and USE_FIB_SL:
        try:
            df_entry = get_closed_data(TIMEFRAME_ENTRY, bars=100)
            swing_low, swing_high = find_last_swing_for_fib(df_entry, direction)
            if swing_low is not None and swing_high is not None:
                fib_sl = resolve_fib_sl(swing_low, swing_high, direction, entry)
                if fib_sl is not None:
                    sl_dist = abs(entry - fib_sl)
                    if min_sl_price <= sl_dist <= max_sl_price:
                        ext_level = float(MANUAL_PROFILE.get("FIB_TP_EXT", 1.618))
                        if direction == "BUY":
                            tp_price = fib_extension(swing_low, swing_high, ext_level)
                        else:
                            tp_price = fib_extension_sell(swing_low, swing_high, ext_level)
                        valid = ((direction == "BUY" and fib_sl < entry and tp_price > entry) or
                                 (direction == "SELL" and fib_sl > entry and tp_price < entry))
                        if valid:
                            return True, "FIB", round(fib_sl, digits), round(tp_price, digits)
        except Exception as e:
            runtime_message(f"Manual FIB calc: {e}")

    if mode in ("ATR", "HYBRID"):
        sl_price_dist = calculate_dynamic_sl(atr=atr_raw)
        sl_price_dist = max(min_sl_price, min(max_sl_price, sl_price_dist))
        rr = float(MANUAL_PROFILE.get("RR", 1.5))
        tp_dist = sl_price_dist * rr
        if direction == "BUY":
            sl_price = entry - sl_price_dist
            tp_price = entry + tp_dist
        else:
            sl_price = entry + sl_price_dist
            tp_price = entry - tp_dist
        return True, "ATR", round(sl_price, digits), round(tp_price, digits)
    return False, "NONE", 0.0, 0.0


def recover_manual_entries():
    if not CONFIG.get("USE_MANUAL_RECOVERY", True):
        return
    try:
        positions = mt5.positions_get(symbol=SYMBOL) or []
        if not positions:
            return
        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            return
        digits = symbol_info.digits
        df_entry = get_closed_data(TIMEFRAME_ENTRY, bars=100)
        atr_raw = atr_value(df_entry)
        override = bool(MANUAL_PROFILE.get("OVERRIDE_EXISTING", False))
        magic = int(CONFIG.get("MAGIC", 777777))

        for pos in positions:
            if int(getattr(pos, "magic", 0) or 0) == magic:
                continue
            if not override and (float(pos.sl or 0.0) != 0.0 or float(pos.tp or 0.0) != 0.0):
                continue
            ok, method, sl_price, tp_price = _recover_manual_position(pos, symbol_info, atr_raw, digits)
            if not ok:
                continue
            new_sl = sl_price if (override or pos.sl == 0) else pos.sl
            new_tp = tp_price if (override or pos.tp == 0) else pos.tp
            result = _order_send_retry({
                "action": mt5.TRADE_ACTION_SLTP,
                "position": pos.ticket,
                "sl": new_sl,
                "tp": new_tp,
            })
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                runtime_message(f"Manual #{pos.ticket} SL:{new_sl} TP:{new_tp} [{method}]")
                POSITION_META[pos.ticket] = {
                    "model": "MANUAL", "sl_source": method,
                    "source": "manual_recovery",
                    "orig_volume": float(pos.volume), "max_move": 0.0,
                }
                persist_state()
    except Exception:
        log_error(f"recover_manual_entries: {traceback.format_exc()}")


# ============================================================
# SECTION: RETRACE AFTER TP3
# ============================================================
def get_choch_m15():
    try:
        df_smc = get_closed_data(TIMEFRAME_SMC, bars=100)
        if df_smc is None or df_smc.empty:
            return None
        return detect_choch(df_smc, int(CONFIG.get("SWING_STRICTNESS", 1)))
    except Exception:
        return None


def check_reentry_after_tp3(direction, current_price):
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        return True, "no positions"
    ref_entry = None
    ref_tp3 = None
    for p in positions:
        meta_p = POSITION_META.get(p.ticket, {})
        if meta_p.get("model") not in ("CONTINUATION", "REVERSAL", "SWEEP"):
            continue
        p_dir = "BUY" if p.type == 0 else "SELL"
        if p_dir != direction:
            continue
        plan = PARTIAL_STATE.get(p.ticket, {})
        if not plan or not plan.get("tp3_done"):
            continue
        entry = float(p.price_open)
        tp3 = float(plan.get("tp3", 0))
        if tp3 <= 0:
            continue
        if direction == "SELL":
            if ref_entry is None or entry > ref_entry:
                ref_entry = entry
                ref_tp3 = tp3
        else:
            if ref_entry is None or entry < ref_entry:
                ref_entry = entry
                ref_tp3 = tp3
    if ref_entry is None or ref_tp3 is None:
        return True, "no tp3-hit reference"
    total_move = abs(ref_entry - ref_tp3)
    if total_move <= 0:
        return True, "zero move"
    retrace_pct = float(CONFIG.get("RETRACE_MIN_PERCENT", 20.0)) / 100.0
    if direction == "SELL":
        retrace_price = ref_tp3 + (total_move * retrace_pct)
        if current_price < retrace_price:
            return False, f"TP3 hit — retrace {current_price:.2f} < min {retrace_price:.2f}"
    else:
        retrace_price = ref_tp3 - (total_move * retrace_pct)
        if current_price > retrace_price:
            return False, f"TP3 hit — retrace {current_price:.2f} > min {retrace_price:.2f}"
    choch_m15 = get_choch_m15()
    want = "BEAR_CHoCH" if direction == "SELL" else "BULL_CHoCH"
    if choch_m15 != want:
        return False, f"TP3 hit — no fresh CHoCH M15 ({choch_m15})"
    return True, "tp3-hit + choch + retrace OK"


# ============================================================
# SECTION: ANTI RE-ENTRY
# ============================================================
def get_positions_by_model(model_name, direction):
    result = []
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        return result
    for p in positions:
        meta = POSITION_META.get(p.ticket, {})
        if meta.get("model") != model_name:
            continue
        p_dir = "BUY" if p.type == 0 else "SELL"
        if p_dir != direction:
            continue
        result.append(p)
    return result


def can_reentry(model_name, direction, entry_price, atr_now):
    positions = mt5.positions_get(symbol=SYMBOL) or []
    max_global = int(CONFIG.get("MAX_OPEN_POSITIONS", 3))
    if max_global > 0 and len(positions) >= max_global:
        return False, f"max global ({max_global})"
    max_model_map = {
        "CONTINUATION": int(CONFIG.get("MAX_POSITIONS_CONTINUATION", CONFIG.get("MAX_PER_MODEL", 2))),
        "REVERSAL": int(CONFIG.get("MAX_POSITIONS_REVERSAL", CONFIG.get("MAX_PER_MODEL", 2))),
        "SWEEP": int(CONFIG.get("MAX_POSITIONS_SWEEP", CONFIG.get("MAX_PER_MODEL", 2))),
    }
    max_model = max_model_map.get(model_name, int(CONFIG.get("MAX_PER_MODEL", 2)))
    same_model = get_positions_by_model(model_name, direction)
    if len(same_model) >= max_model:
        return False, f"max {model_name} ({max_model})"
    if not same_model:
        return True, "ok (no same-direction)"
    tp3_hit_exists = any(PARTIAL_STATE.get(p.ticket, {}).get("tp3_done") for p in same_model)
    if tp3_hit_exists:
        ok, reason = check_reentry_after_tp3(direction, entry_price)
        if not ok:
            return False, reason
        return True, "ok (TP3 retrace + CHoCH)"
    if atr_now is None or atr_now <= 0:
        return False, "ATR invalid"
    min_dist = atr_now * float(CONFIG.get("MIN_REENTRY_ATR", 2.0))
    loss_trigger = atr_now * float(CONFIG.get("LOSS_REENTRY_ATR", 2.0))
    if direction == "BUY":
        reference = min(float(p.price_open) for p in same_model)
        adverse_move = reference - float(entry_price)
    else:
        reference = max(float(p.price_open) for p in same_model)
        adverse_move = float(entry_price) - reference
    if adverse_move < loss_trigger:
        return False, f"{direction} averaging move {adverse_move:+.2f} < trigger {loss_trigger:.2f}"
    if adverse_move < min_dist:
        return False, f"{direction} re-entry distance {adverse_move:.2f} < min {min_dist:.2f}"
    return True, f"ok ({direction} averaging {adverse_move:+.2f})"


# ============================================================
# SECTION: OPEN TRADE
# ============================================================
def open_trade(model_result, risk_data, symbol_info=None):
    try:
        symbol_info = symbol_info or mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            runtime_message("Symbol not found")
            return False
        model_name = model_result["model"]
        direction = model_result["direction"]
        atr_now = get_atr_current()
        if atr_now is None or atr_now <= 0:
            runtime_message("ATR=0 skip")
            return False
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            runtime_message("No tick")
            return False
        preview_entry = tick.ask if direction == "BUY" else tick.bid
        can_open, reason = can_reentry(model_name, direction, preview_entry, atr_now)
        if not can_open:
            runtime_message(f"Skip entry — {reason}")
            return False
        if not symbol_info.visible:
            mt5.symbol_select(SYMBOL, True)
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            runtime_message("No tick")
            return False
        digits = symbol_info.digits
        entry = tick.ask if direction == "BUY" else tick.bid
        sl, sl_source = resolve_sl(entry, direction, atr_now,
                                    swing_low=model_result.get("swing_low"),
                                    swing_high=model_result.get("swing_high"))
        if sl is None:
            runtime_message("SL=0 skip")
            return False
        tp_plan = resolve_tp(entry, sl, direction)
        if tp_plan is None:
            runtime_message("TP=None skip")
            return False
        tp_valid, rr_est, tp_plan = validate_tp(tp_plan, entry, sl, direction)
        if not tp_valid:
            runtime_message(f"Skip RR (actual {rr_est:.2f})")
            return False
        lot = risk_data.get("lot", float(CONFIG.get("LOT_SIZE", 0.01)))
        entry = round(entry, digits)
        sl = round(sl, digits)
        tp3 = round(tp_plan["tp3"], digits)
        if direction == "BUY":
            if sl >= entry or tp3 <= entry:
                runtime_message(f"BAD SL/TP BUY")
                return False
        else:
            if sl <= entry or tp3 >= entry:
                runtime_message(f"BAD SL/TP SELL")
                return False
        order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
        filling_modes = _get_supported_filling(symbol_info)
        last_rc = None
        for filling in filling_modes:
            req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL, "volume": lot, "type": order_type,
                "price": entry, "sl": sl, "tp": tp3,
                "deviation": int(CONFIG.get("TRADE_DEVIATION", 20)),
                "magic": int(CONFIG.get("MAGIC", 777777)),
                "type_filling": filling, "type_time": mt5.ORDER_TIME_GTC,
                "comment": f"Wfx_{model_name}",
            }
            result = _order_send_retry(req)
            if result is None:
                last_rc = "None"
                continue
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                runtime_message(f"OK {model_name} {direction} @{entry} SL:{sl}({sl_source}) TP:{tp3} Lot:{lot}")
                time.sleep(float(CONFIG.get("POST_ORDER_SETTLE_DELAY", 0.50)))
                poss = mt5.positions_get(symbol=SYMBOL)
                if poss:
                    latest = max(poss, key=lambda p: p.time)
                    POSITION_META[latest.ticket] = {
                        "model": model_name, "sl_source": sl_source,
                        "orig_volume": float(lot), "max_move": 0.0,
                    }
                    register_partial_plan(latest.ticket, tp_plan, lot, model_name,
                                          entry_price=latest.price_open, direction=direction)
                    persist_state()
                return True
            last_rc = result.retcode
            if _retryable_retcode(result.retcode):
                continue
        runtime_message(f"ALL FAIL rc={last_rc} | {direction} E{entry} SL{sl} TP{tp3}")
        return False
    except Exception:
        log_error(f"open_trade: {traceback.format_exc()}")
        return False


# ============================================================
# SECTION: STATS
# ============================================================
def _parse_model_from_comment(comment):
    if not comment:
        return "UNKNOWN"
    c = comment.upper()
    for tag in ("CONTINUATION", "REVERSAL", "SWEEP"):
        if tag in c:
            return tag
    if "MANUAL" in c:
        return "MANUAL"
    return "UNKNOWN"


def fetch_trade_history(lookback_days=None, magic=None):
    if lookback_days is None:
        lookback_days = int(CONFIG.get("STATS_LOOKBACK_DAYS", 7))
    include_manual = bool(CONFIG.get("STATS_INCLUDE_MANUAL", True))
    ea_magic = int(CONFIG.get("MAGIC", 777777))
    try:
        date_from = datetime.now() - timedelta(days=lookback_days)
        date_to = datetime.now() + timedelta(days=1)
        deals = mt5.history_deals_get(date_from, date_to)
        if deals is None or len(deals) == 0:
            return []
        positions_map = {}
        for d in deals:
            if d.symbol != SYMBOL:
                continue
            if magic is not None:
                if d.magic != magic:
                    continue
            else:
                is_ea = (d.magic == ea_magic)
                is_manual = (d.magic == 0 or d.magic not in (ea_magic,))
                if not is_ea and not (include_manual and is_manual):
                    continue
            pid = d.position_id
            if pid not in positions_map:
                positions_map[pid] = {
                    "profit": 0.0, "volume": 0.0,
                    "time_open": d.time, "time_close": d.time,
                    "comment": "", "direction": None, "magic": d.magic,
                }
            positions_map[pid]["profit"] += float(d.profit) + float(d.swap) + float(d.commission)
            if d.entry == mt5.DEAL_ENTRY_IN:
                positions_map[pid]["volume"] = float(d.volume)
                positions_map[pid]["time_open"] = d.time
                positions_map[pid]["comment"] = d.comment
                positions_map[pid]["direction"] = "BUY" if d.type == 0 else "SELL"
                positions_map[pid]["magic"] = d.magic
            if d.entry == mt5.DEAL_ENTRY_OUT:
                positions_map[pid]["time_close"] = d.time
        result = []
        for pid, info in positions_map.items():
            if info["direction"] is None or info["volume"] == 0:
                continue
            model = _parse_model_from_comment(info["comment"])
            if model == "UNKNOWN":
                if info["magic"] == 0:
                    model = "MANUAL"
                elif info["magic"] != ea_magic:
                    model = "MANUAL"
                else:
                    model = "UNKNOWN"
            result.append({
                "ticket": pid, "model": model, "direction": info["direction"],
                "profit": info["profit"], "volume": info["volume"],
                "time_open": info["time_open"], "time_close": info["time_close"],
                "magic": info["magic"],
            })
        return result
    except Exception:
        log_error(f"fetch_history: {traceback.format_exc()}")
        return []


def compute_stats(trades):
    stats = {"total": len(trades), "wins": 0, "losses": 0, "be": 0,
             "profit_total": 0.0, "profit_wins": 0.0, "profit_losses": 0.0,
             "winrate": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "profit_factor": 0.0}
    for t in trades:
        p = t["profit"]
        stats["profit_total"] += p
        if p > 0.01:
            stats["wins"] += 1
            stats["profit_wins"] += p
        elif p < -0.01:
            stats["losses"] += 1
            stats["profit_losses"] += abs(p)
        else:
            stats["be"] += 1
    if stats["total"] > 0:
        stats["winrate"] = (stats["wins"] / stats["total"]) * 100
    if stats["wins"] > 0:
        stats["avg_win"] = stats["profit_wins"] / stats["wins"]
    if stats["losses"] > 0:
        stats["avg_loss"] = stats["profit_losses"] / stats["losses"]
    if stats["profit_losses"] > 0:
        stats["profit_factor"] = stats["profit_wins"] / stats["profit_losses"]
    elif stats["profit_wins"] > 0:
        stats["profit_factor"] = 999.0
    return stats


def stats_per_model(trades):
    by_model = {}
    for t in trades:
        m = t["model"]
        by_model.setdefault(m, []).append(t)
    return {m: compute_stats(ts) for m, ts in by_model.items()}


STATS_CACHE = {"trades": [], "global": {}, "per_model": {}, "last_refresh": 0}


def refresh_stats(force=False):
    now = time.time()
    interval = float(CONFIG.get("STATS_REFRESH_INTERVAL", 10))
    if not force and (now - STATS_CACHE["last_refresh"]) < interval:
        return
    try:
        trades = fetch_trade_history()
        STATS_CACHE["trades"] = trades
        STATS_CACHE["global"] = compute_stats(trades)
        STATS_CACHE["per_model"] = stats_per_model(trades)
        STATS_CACHE["last_refresh"] = now
    except Exception:
        log_error(f"refresh_stats: {traceback.format_exc()}")


# ============================================================
# SECTION: DIAGNOSTIC STATE
# ============================================================
DIAG_STATE = {
    "swing_buy": False, "swing_sell": False,
    "demand_zones": 0, "supply_zones": 0,
    "htf_trend": "SIDEWAYS", "choch": None, "rej_wick": None,
    "sweep_buy": False, "sweep_sell": False,
}


# ============================================================
# SECTION: MODEL SCORES
# ============================================================
MODEL_SCORES = {}
for _model_name, _flag_name, _default in (
    ("CONTINUATION", "USE_MODEL_CONTINUATION", True),
    ("REVERSAL", "USE_MODEL_REVERSAL", False),
    ("SWEEP", "USE_MODEL_SWEEP", False),
):
    MODEL_SCORES[_model_name] = {
        "enabled": bool(CONFIG.get(_flag_name, _default)),
        "confluence": 0, "rr": 0.0, "direction": "-",
        "valid": False, "status": "WAIT", "reason": "Waiting for closed candle",
        "met": [], "gate_score": 0, "gate_total": 5, "gates": {},
    }


# ============================================================
# SECTION: GATE PROGRESS (GLOBAL)
# ============================================================
GATE_PROGRESS = {}


# ============================================================
# SECTION: UI STATE
# ============================================================
best_model_global = {}

SIGNAL_STATE = {
    "status": "WAITING",
    "model": "-",
    "direction": "-",
    "confluence": 0,
    "rr": 0.0,
    "entry": None,
    "sl": None,
    "lot": 0.0,
    "reason": "Waiting for closed candle",
    "gate_score": 0,
    "gate_total": 5,
}


# ============================================================
# SECTION: UI HELPERS
# ============================================================
def rich_status(value, on_color="green", off_color="red"):
    return Text("ON", style=on_color) if value else Text("OFF", style=off_color)


def rich_direction(value):
    if value in ("BULLISH", "BUY"):
        return Text(str(value), style="green")
    if value in ("BEARISH", "SELL"):
        return Text(str(value), style="red")
    return Text(str(value), style="yellow")


def _style_pnl(value):
    return "green" if value > 0 else ("red" if value < 0 else "white")


def render_stats_panel():
    g = STATS_CACHE["global"]
    per = STATS_CACHE["per_model"]
    tbl = Table.grid(expand=True, padding=(0, 1))
    tbl.add_column(style="cyan", no_wrap=True)
    tbl.add_column(ratio=1)
    if g.get("total", 0) == 0:
        tbl.add_row("Stats", Text(f"No trades ({CONFIG.get('STATS_LOOKBACK_DAYS', 7)}d)", style="dim"))
        return tbl
    tbl.add_row("Total", Text(f"{g['total']} trades", style="bold white"))
    wr_style = "green" if g["winrate"] >= 50 else ("yellow" if g["winrate"] >= 40 else "red")
    tbl.add_row("WinRate", Text(f"{g['winrate']:.1f}% ({g['wins']}W / {g['losses']}L / {g['be']}BE)", style=wr_style))
    tbl.add_row("Total P/L", Text(f"${g['profit_total']:.2f}", style=_style_pnl(g["profit_total"])))
    pf = g["profit_factor"]
    pf_style = "green" if pf >= 1.5 else ("yellow" if pf >= 1.0 else "red")
    pf_txt = "inf" if pf >= 999 else f"{pf:.2f}"
    tbl.add_row("PF", Text(pf_txt, style=pf_style))
    if g["wins"] > 0:
        tbl.add_row("Avg Win", Text(f"${g['avg_win']:.2f}", style="green"))
    if g["losses"] > 0:
        tbl.add_row("Avg Loss", Text(f"${g['avg_loss']:.2f}", style="red"))
    tbl.add_row("", Text("-" * 20, style="dim"))
    for model in ("CONTINUATION", "REVERSAL", "SWEEP", "MANUAL"):
        if model in per:
            s = per[model]
            style = "green" if s["profit_total"] >= 0 else "red"
            wr_s = "green" if s["winrate"] >= 50 else "yellow"
            line = Text()
            line.append(f"{model[:4]} ", style="bold cyan")
            line.append(f"{s['total']}t ", style="white")
            line.append(f"{s['winrate']:.0f}% ", style=wr_s)
            line.append(f"${s['profit_total']:.1f}", style=style)
            tbl.add_row("", line)
        else:
            tbl.add_row("", Text(f"{model[:4]} - no trades", style="dim"))
    return tbl


def render_diagnostic_panel():
    tbl = Table.grid(expand=True, padding=(0, 1))
    tbl.add_column(style="cyan", no_wrap=True)
    tbl.add_column(ratio=1)
    gate_ok = lambda b: Text("OK" if b else "X", style="green" if b else "red")
    tbl.add_row("Swing BUY", gate_ok(DIAG_STATE["swing_buy"]))
    tbl.add_row("Swing SELL", gate_ok(DIAG_STATE["swing_sell"]))
    tbl.add_row("Demand Zones", Text(f"{DIAG_STATE['demand_zones']}",
                                     style="cyan" if DIAG_STATE['demand_zones'] > 0 else "red"))
    tbl.add_row("Supply Zones", Text(f"{DIAG_STATE['supply_zones']}",
                                     style="cyan" if DIAG_STATE['supply_zones'] > 0 else "red"))
    htf = DIAG_STATE["htf_trend"]
    tbl.add_row("HTF Trend", Text(htf, style="green" if htf in ("BULLISH", "BEARISH") else "red"))
    choch = DIAG_STATE["choch"] or "-"
    tbl.add_row("CHoCH", Text(choch, style="green" if choch != "-" else "dim"))
    wick = DIAG_STATE["rej_wick"] or "-"
    tbl.add_row("RejWick", Text(wick, style="green" if wick != "-" else "dim"))
    tbl.add_row("Sweep BUY", gate_ok(DIAG_STATE["sweep_buy"]))
    tbl.add_row("Sweep SELL", gate_ok(DIAG_STATE["sweep_sell"]))
    tbl.add_row("FVG Bull", Text(f"{len(get_active_fvg('BULL'))}",
                                  style="green" if get_active_fvg('BULL') else "dim"))
    tbl.add_row("FVG Bear", Text(f"{len(get_active_fvg('BEAR'))}",
                                  style="red" if get_active_fvg('BEAR') else "dim"))
    tbl.add_row("", Text("-" * 20, style="dim"))
    for _ in range(2):
        tbl.add_row("", Text(""))
    return tbl


def render_model_scores_panel():
    tbl = Table.grid(expand=True, padding=(0, 1))
    tbl.add_column(style="cyan", no_wrap=True)
    for _ in range(3):
        tbl.add_column(ratio=1, justify="center")

    def _header_col(m):
        is_active = best_model_global.get("model") == m
        t = Text(m[:4], style="bold yellow" if is_active else "bold cyan")
        if is_active:
            t.append(" <", style="bold yellow")
        return t

    tbl.add_row("", _header_col("CONTINUATION"), _header_col("REVERSAL"), _header_col("SWEEP"))
    rows = {"Gate": [], "Conf": [], "RR": [], "Dir": [], "Status": [], "Reason": []}
    for m in ("CONTINUATION", "REVERSAL", "SWEEP"):
        s = MODEL_SCORES.get(m, {})
        enabled = s.get("enabled", CONFIG.get({
            "CONTINUATION": "USE_MODEL_CONTINUATION",
            "REVERSAL": "USE_MODEL_REVERSAL",
            "SWEEP": "USE_MODEL_SWEEP",
        }[m], False))
        if not enabled:
            rows["Gate"].append(Text("OFF", style="dim"))
            rows["Conf"].append(Text("-", style="dim"))
            rows["RR"].append(Text("-", style="dim"))
            rows["Dir"].append(Text("-", style="dim"))
            rows["Status"].append(Text("DISABLED", style="dim"))
            rows["Reason"].append(Text("model off", style="dim"))
            continue
        gs, gt = s.get("gate_score", 0), s.get("gate_total", 5)
        gate_style = "bold green" if gs >= gt else ("yellow" if gs >= gt - 1 else "dim")
        rows["Gate"].append(Text(f"{gs}/{gt}", style=gate_style))
        conf = float(s.get("confluence", 0) or 0)
        conf_style = "bold green" if conf >= float(CONFIG.get("MIN_CONFLUENCE", 75)) else ("yellow" if conf > 0 else "dim")
        rows["Conf"].append(Text(f"{conf:.0f}%", style=conf_style))
        rr = float(s.get("rr", 0) or 0)
        rr_style = "green" if rr >= 2 else ("cyan" if rr >= 1.2 else "dim")
        rows["RR"].append(Text(f"1:{rr:.1f}", style=rr_style))
        d = s.get("direction", "-") or "-"
        rows["Dir"].append(Text(d, style="green" if d == "BUY" else "red" if d == "SELL" else "dim"))
        status = s.get("status", "WAIT")
        status_style = {"READY": "bold green", "RISK_OK": "green", "GATE": "yellow", "BLOCKED": "yellow", "WAIT": "dim"}.get(status, "dim")
        rows["Status"].append(Text(status, style=status_style))
        rows["Reason"].append(Text(str(s.get("reason", ""))[:28], style="white", overflow="fold"))
    for label in ("Gate", "Conf", "RR", "Dir", "Status", "Reason"):
        tbl.add_row(Text(label, style="dim"), *rows[label])
    return tbl


def render_gate_progress_panel():
    tbl = Table.grid(expand=True, padding=(0, 1))
    tbl.add_column(style="cyan", no_wrap=True, width=14)
    tbl.add_column(ratio=1)
    tbl.add_column(ratio=1)
    tbl.add_column(ratio=1)

    def _bar(gates):
        order = ("htf", "zone", "confirm", "swing", "fib")
        return "".join("✓" if gates.get(k, False) else "✗" for k in order)

    def _style(score, total):
        if score >= total:
            return "bold green"
        if score >= total - 1:
            return "yellow"
        if score >= total - 2:
            return "cyan"
        return "dim"

    tbl.add_row(
        Text("MODEL", style="dim"),
        Text("PROGRESS", style="dim"),
        Text("SCORE", style="dim"),
        Text("MISSING", style="dim"),
    )
    order = ("htf", "zone", "confirm", "swing", "fib")
    for model_name in ("CONTINUATION", "REVERSAL", "SWEEP"):
        gp = GATE_PROGRESS.get(model_name, {})
        if not gp.get("enabled", True):
            tbl.add_row(Text(f"{model_name[:4]} OFF", style="dim"),
                        Text("[-----]", style="dim"), Text("-", style="dim"),
                        Text("DISABLED", style="dim"))
            continue
        score = gp.get("score", 0)
        total = gp.get("total", 5)
        gates = gp.get("gates", {})
        direction = gp.get("direction", "-")
        bar = _bar(gates)
        style = _style(score, total)
        missing = [k for k in order if not gates.get(k, False)]
        missing_txt = ",".join(missing) if missing else "READY"
        label = f"{model_name[:4]} {direction}"
        score_txt = f"{score}/{total}"
        if score >= total:
            score_style = "bold green"
            missing_style = "bold green"
        elif score >= total - 1:
            score_style = "bold yellow"
            missing_style = "yellow"
        else:
            score_style = "white"
            missing_style = "dim"
        tbl.add_row(
            Text(label, style=style),
            Text(f"[{bar}]", style=style),
            Text(score_txt, style=score_style),
            Text(missing_txt, style=missing_style, overflow="fold"),
        )
    return tbl


def _hstack_panels(panels, ratios=None, spacing=0):
    if not panels:
        return Text("")
    if ratios is None:
        ratios = [1] * len(panels)
    if len(ratios) != len(panels):
        ratios = [1] * len(panels)
    grid = Table.grid(expand=True, padding=(0, spacing), pad_edge=False)
    for r in ratios:
        grid.add_column(ratio=r, overflow="fold", vertical="top")
    grid.add_row(*panels)
    return grid


def render_rich_dashboard(*, account, positions, bid, ask, price_direction,
                          current_session, session_trade_allowed,
                          trend, htf_trend, atr_val, atr_ok,
                          best_model, fakeout, daily_pnl, daily_loss_percent,
                          trading_disabled_today):
    global best_model_global
    if best_model:
        best_model_global = dict(best_model)

    now = datetime.now(WIB).strftime("%H:%M:%S WIB")
    trade_txt = Text("ON", style="bold green") if CONFIG.get("USE_AUTO_TRADE", True) else Text("OFF", style="bold red")
    session_txt = Text(current_session, style="bold green" if session_trade_allowed else "bold yellow")

    header = Table.grid(expand=True)
    header.add_column(ratio=1)
    header.add_column(justify="center", ratio=1)
    header.add_column(justify="right", ratio=1)
    title = Text("WEENfx PRO - v6.3.4", style="bold cyan")
    symbol = Text(SYMBOL, style="bold white")
    right = Text()
    right.append(now, style="white")
    right.append("  TRADE ", style="dim")
    right.append(trade_txt)
    header.add_row(title, symbol, right)
    header_panel = Panel(header, border_style="cyan", padding=(0, 1))

    price = Text()
    price.append("PRICE ", style="bold cyan")
    if bid is not None:
        pc = "green" if price_direction == "UP" else "red" if price_direction == "DN" else "yellow"
        price.append(f"{bid:.2f} {price_direction}", style=f"bold {pc}")
    else:
        price.append("--", style="yellow")
    price.append(f"  BID {bid:.2f}" if bid is not None else "  BID --")
    price.append(f"  ASK {ask:.2f}" if ask is not None else "  ASK --")
    price.append(f"  ATR {atr_val:.2f}")
    price.append("  HTF ", style="dim")
    price.append(f"{htf_trend}", style="green" if htf_trend == "BULLISH" else "red" if htf_trend == "BEARISH" else "yellow")
    price.append("  Trend ", style="dim")
    price.append(f"{trend}", style="green" if trend == "BULLISH" else "red" if trend == "BEARISH" else "yellow")
    price.append("  Session ", style="dim")
    price.append(session_txt)
    price.append("  ")
    price.append("ALLOWED" if session_trade_allowed else "BLOCKED",
                 style="bold green" if session_trade_allowed else "bold red")
    price_panel = Panel(price, border_style="cyan", padding=(0, 1))

    market = Table.grid(expand=True, padding=(0, 1))
    market.add_column(style="cyan", no_wrap=True, width=12)
    market.add_column(ratio=1)
    market.add_row("Bias", rich_direction(trend))
    market.add_row("HTF", rich_direction(htf_trend))
    market.add_row("ATR", Text(f"{atr_val:.2f}  {'OK' if atr_ok else 'LOW'}",
                               style="green" if atr_ok else "red"))
    market.add_row("Confluence", Text(f"Min {int(CONFIG.get('MIN_CONFLUENCE', 75))}%", style="cyan"))
    market.add_row("Session", session_txt)
    market.add_row("", Text(""))

    signal = Table.grid(expand=True, padding=(0, 1))
    signal.add_column(style="cyan", no_wrap=True, width=10)
    signal.add_column(ratio=1)
    ss = SIGNAL_STATE
    status = ss.get("status", "WAITING")
    status_style = "bold green" if status in ("READY", "EXECUTED") else "yellow" if status in ("BLOCKED", "WAIT_RISK", "WAIT_REENTRY") else "dim"
    signal.add_row("STATUS", Text(status, style=status_style))
    signal.add_row("MODEL", Text(f"{ss.get('model','-')} {ss.get('direction','-')}", style="bold cyan"))
    signal.add_row("Gate", Text(f"{ss.get('gate_score',0)}/{ss.get('gate_total',5)}",
                                style="green" if ss.get('gate_score',0) >= ss.get('gate_total',5) else "yellow"))
    signal.add_row("Conf", Text(f"{ss.get('confluence',0):.0f}%",
                                style="green" if ss.get('confluence',0) >= float(CONFIG.get('MIN_CONFLUENCE',75)) else "yellow"))
    signal.add_row("RR", Text(f"1:{ss.get('rr',0):.1f}", style="cyan"))
    if ss.get("entry") is not None:
        signal.add_row("Entry", Text(f"{ss['entry']:.2f}", style="white"))
        signal.add_row("SL", Text(f"{ss['sl']:.2f}" if ss.get("sl") is not None else "-", style="red"))
        signal.add_row("Lot", Text(f"{ss.get('lot',0):g}", style="white"))
    else:
        signal.add_row("Entry", Text("-", style="dim"))
        signal.add_row("SL", Text("-", style="dim"))
        signal.add_row("Lot", Text("-", style="dim"))
    signal.add_row("Reason", Text(str(ss.get("reason", ""))[:42], style="white", overflow="fold"))

    try:
        diag_panel = Panel(render_diagnostic_panel(), title="DIAGNOSTIC",
                           border_style="yellow", expand=True)
    except Exception as e:
        diag_panel = Panel(Text(f"diag err: {e}", style="red"), border_style="red")

    try:
        scores_panel = Panel(render_model_scores_panel(),
                             title=f"MODEL SCORES  [Min Conf {int(CONFIG.get('MIN_CONFLUENCE',75))}%]",
                             border_style="cyan", expand=True)
    except Exception as e:
        scores_panel = Panel(Text(f"scores err: {e}", style="red"), border_style="red")

    try:
        gate_panel = Panel(render_gate_progress_panel(),
                           title="GATE PROGRESS  (early signal indicator)",
                           border_style="magenta", expand=True)
    except Exception as e:
        gate_panel = Panel(Text(f"gate err: {e}", style="red"), border_style="red")

    pos_table = Table(expand=True, show_header=True, header_style="bold cyan",
                      box=None, padding=(0, 1), pad_edge=False)
    pos_table.add_column("#", justify="center", width=4, no_wrap=True)
    pos_table.add_column("TYPE", justify="center", width=8, no_wrap=True)
    pos_table.add_column("LOT", justify="right", width=9, no_wrap=True)
    pos_table.add_column("ENTRY", justify="right", ratio=2, no_wrap=True)
    pos_table.add_column("CURRENT", justify="right", ratio=2, no_wrap=True)
    pos_table.add_column("SL", justify="right", ratio=2, no_wrap=True)
    pos_table.add_column("TP", justify="right", ratio=2, no_wrap=True)
    pos_table.add_column("P/L", justify="right", ratio=2, no_wrap=True)
    pos_table.add_column("MODEL", justify="left", width=14, no_wrap=True)
    pos_table.add_column("PART", justify="left", width=14, no_wrap=True)
    pos_table.add_column("STATUS", justify="left", ratio=2, no_wrap=True)

    if positions:
        for i, pos in enumerate(positions, 1):
            ptype = "BUY" if pos.type == 0 else "SELL"
            pstyle = "green" if pos.type == 0 else "red"
            tick_price = (bid if pos.type == 0 else ask) if (bid is not None and ask is not None) else pos.price_current
            pnl = float(pos.profit)
            meta = POSITION_META.get(pos.ticket, {})
            model_tag = meta.get("model", "?")
            if pos.magic != int(CONFIG.get("MAGIC", 777777)) and model_tag == "?":
                model_tag = "MANUAL"
            status = "OPEN"
            plan = PARTIAL_STATE.get(pos.ticket)
            part_display = "-"
            if plan:
                tp1_done = plan.get("tp1_done", False)
                tp2_done = plan.get("tp2_done", False)
                tp3_done = plan.get("tp3_done", False)
                marks = ["Y" if tp1_done else "N",
                         "Y" if tp2_done else "N",
                         "Y" if tp3_done else "N"]
                part_display = "1-2-3:" + ",".join(marks)
                if tp2_done:
                    status = "TP2 DONE"
                elif tp1_done:
                    status = "TP1 DONE"
                else:
                    status = "P:123"
            if pos.sl and ((pos.type == 0 and pos.sl >= pos.price_open) or
                           (pos.type == 1 and pos.sl <= pos.price_open)):
                status = "BE ACTIVE"
            tp_display = f"{pos.tp:.2f}" if pos.tp and pos.tp > 0 else "-"
            pos_table.add_row(
                str(i), Text(ptype, style=f"bold {pstyle}"), f"{pos.volume:g}",
                f"{pos.price_open:.2f}", f"{tick_price:.2f}", f"{pos.sl:.2f}",
                tp_display, Text(f"${pnl:.2f}", style="green" if pnl >= 0 else "red"),
                Text(model_tag[:10], style="cyan"),
                Text(part_display, style="yellow"),
                Text(status, style="green" if status != "OPEN" else "yellow"))
    else:
        pos_table.add_row("-", "-", "-", "-", "-", "-", "-",
                          Text("$0.00"), "-", "-", "NO POSITIONS")

    total_pnl = sum(float(p.profit) for p in positions) if positions else 0.0
    total_lot = sum(float(p.volume) for p in positions) if positions else 0.0
    buys = sum(1 for p in positions if p.type == 0) if positions else 0
    sells = sum(1 for p in positions if p.type == 1) if positions else 0
    maxpos = str(CONFIG.get("MAX_OPEN_POSITIONS", 3))
    pos_summary = Text()
    pos_summary.append(f"TOTAL P/L ${total_pnl:.2f}", style="green" if total_pnl >= 0 else "red")
    pos_summary.append(f"  | BUY {buys} | SELL {sells} | LOT {total_lot:g} | {len(positions) if positions else 0}/{maxpos}")
    pos_group = Group(pos_table, pos_summary)

    risk = Table.grid(expand=True, padding=(0, 1))
    risk.add_column(style="cyan", no_wrap=True, width=14)
    risk.add_column(ratio=1)
    risk.add_row("AutoTrade", rich_status(CONFIG.get("USE_AUTO_TRADE", True)))
    risk.add_row("SL", Text(f"{'FIB' if CONFIG.get('USE_FIB_SL') else 'ATR'} ×{CONFIG.get('SL_ATR_MULT', 1.5)}", style="cyan"))
    risk.add_row("TP RR", Text(f"1:{CONFIG.get('TP_RR_TP1',1.0)}/1:{CONFIG.get('TP_RR_TP2',2.0)}/1:{CONFIG.get('TP_RR_TP3',3.0)}"))
    risk.add_row("BE", Text(f"ATR×{CONFIG.get('BE_TRIGGER_ATR',1.5)}", style="cyan"))
    risk.add_row("Trail", Text(f"ATR×{CONFIG.get('TRAIL_TRIGGER_ATR',2.5)} s{CONFIG.get('TRAIL_SECURE_PCT',50)}%"))
    risk.add_row("Partial", Text(f"{CONFIG.get('PARTIAL_MODE', 'PERCENT')} "
                                  f"{CONFIG.get('PARTIAL_PCT_1', 33)}/{CONFIG.get('PARTIAL_PCT_2', 33)}",
                                  style="magenta"))
    risk.add_row("FVG Mit", Text("ON" if CONFIG.get("USE_FVG_MITIGATION", True) else "OFF",
                                  style="green" if CONFIG.get("USE_FVG_MITIGATION", True) else "dim"))
    risk.add_row("Daily", Text(f"${daily_pnl:.2f} / {daily_loss_percent:.2f}%"))
    risk.add_row("FakeBrk", Text("FAKE!" if fakeout else "clear",
                                  style="red" if fakeout else "green"))

    account_panel = Table.grid(expand=True, padding=(0, 1))
    account_panel.add_column(style="cyan", no_wrap=True, width=14)
    account_panel.add_column(ratio=1)
    account_panel.add_row("Balance", Text(f"${float(account.balance) if account else 0:.2f}", style="white"))
    account_panel.add_row("Equity", Text(f"${float(account.equity) if account else 0:.2f}", style="white"))
    account_panel.add_row("Free Margin",
                          Text(f"${float(account.margin_free) if account else 0:.2f}", style="white"))
    account_panel.add_row("Margin Lvl",
                          Text(f"{float(account.margin_level) if account and account.margin_level else 0:.1f}%",
                               style="white"))
    account_panel.add_row("Leverage",
                          Text(f"1:{account.leverage if account else 0}", style="white"))
    account_panel.add_row("Daily", Text(f"${daily_pnl:.2f}", style=_style_pnl(daily_pnl)))

    sess = Table.grid(expand=True, padding=(0, 1))
    sess.add_column(style="cyan", no_wrap=True, width=10)
    sess.add_column(ratio=1)
    for key, label in (("ASIA", "ASIA"), ("LONDON", "LONDON"),
                       ("NEW_YORK", "NEW YORK"), ("LONDON_NEW_YORK_OVERLAP", "OVERLAP")):
        cfg = SESSION_CONFIG.get(key, {})
        active = key in detect_sessions()
        enabled = cfg.get("ENABLED", False)
        state = "ACTIVE" if active else ("ENABLED" if enabled else "OFF")
        style = "bold green" if active and enabled else "green" if enabled else "dim"
        sess.add_row(label, Text(f"{cfg.get('START', '--:--')}-{cfg.get('END', '--:--')}  {state}", style=style))
    for _ in range(3):
        sess.add_row("", Text(""))

    stats_grid = render_stats_panel()

    row_market_signal = _hstack_panels([
        Panel(market, title="MARKET", border_style="cyan", expand=True),
        Panel(signal, title="SIGNAL", border_style="yellow", expand=True),
    ], ratios=[1, 1])

    row_diag_scores = _hstack_panels([
        diag_panel,
        scores_panel,
    ], ratios=[1, 1])

    row_risk_account = _hstack_panels([
        Panel(risk, title="RISK", border_style="green", expand=True),
        Panel(account_panel, title="ACCOUNT", border_style="cyan", expand=True),
    ], ratios=[2, 1])

    row_session_stats = _hstack_panels([
        Panel(sess, title="SESSION", border_style="yellow", expand=True),
        Panel(stats_grid, title=f"STATS ({CONFIG.get('STATS_LOOKBACK_DAYS', 7)}d)",
              border_style="cyan", expand=True),
    ], ratios=[1, 2])

    status_text = Text()
    status = "MONITORING" if positions else "WAITING MODEL"
    if trading_disabled_today:
        status = "DISABLED (daily loss)"
    elif not session_trade_allowed and CONFIG.get("USE_SESSION_FILTER", True):
        status = "OUTSIDE SESSION"
    status_text.append("* " + status, style="bold green" if positions else "bold yellow")
    status_text.append(f"  |  Trend {trend}  |  HTF {htf_trend}  |  Bias {trend}")
    status_panel = Panel(status_text, border_style="cyan", padding=(0, 1))

    event_parts = []
    if runtime_message_text:
        status_line = Text()
        status_line.append("EVENT ", style="bold cyan")
        status_line.append(runtime_message_text, style="white")
        event_parts.append(Panel(status_line, border_style="dim", padding=(0, 1)))

    parts = [
        header_panel,
        price_panel,
        row_market_signal,
        row_diag_scores,
        gate_panel,
        Panel(pos_group, title=f"POSITIONS  {len(positions) if positions else 0}/{maxpos}",
              border_style="white", padding=(0, 1)),
        row_risk_account,
        row_session_stats,
        status_panel,
    ]
    parts.extend(event_parts)
    return Group(*parts)


# ============================================================
# SECTION: STARTUP
# ============================================================
print("=" * 60)
print("Starting v6.3.4 (SMC + FVG Mitigation + Fib 5 Level)...")
print(f"   Symbol: {SYMBOL}")
print(f"   Entry TF: {TIMEFRAME_ENTRY}")
print(f"   Auto Trade: {'ON' if CONFIG.get('USE_AUTO_TRADE', True) else 'OFF'}")
print(f"   Model: CONT={CONFIG.get('USE_MODEL_CONTINUATION', True)} "
      f"REV={CONFIG.get('USE_MODEL_REVERSAL', False)} "
      f"SWP={CONFIG.get('USE_MODEL_SWEEP', False)}")
print(f"   SL: {'FIB' if CONFIG.get('USE_FIB_SL') else 'ATR'} x {CONFIG.get('SL_ATR_MULT', 1.5)} "
      f"(max {CONFIG.get('MAX_SL_POINTS', 15.0)} poin)")
print(f"   TP RR: 1:{CONFIG.get('TP_RR_TP1',1.0)} / 1:{CONFIG.get('TP_RR_TP2',2.0)} / 1:{CONFIG.get('TP_RR_TP3',3.0)}")
print(f"   BE: ATR x {CONFIG.get('BE_TRIGGER_ATR',1.5)}")
print(f"   Trailing: ATR x {CONFIG.get('TRAIL_TRIGGER_ATR',2.5)} sec {CONFIG.get('TRAIL_SECURE_PCT',50)}%")
print(f"   Min Confluence: {int(CONFIG.get('MIN_CONFLUENCE',75))}%")
print(f"   Partial: {CONFIG.get('PARTIAL_MODE', 'PERCENT')} "
      f"({CONFIG.get('PARTIAL_PCT_1', 33)}/{CONFIG.get('PARTIAL_PCT_2', 33)})")
print(f"   SMC ATR Period: {CONFIG.get('SMC_ATR_PERIOD', 50)} (dari FluidTrades)")
print(f"   Overlap Filter: ATR x {CONFIG.get('ZONE_OVERLAP_ATR', 1.0)} (dari FluidTrades)")
print(f"   FVG Mitigation: {'ON' if CONFIG.get('USE_FVG_MITIGATION', True) else 'OFF'} (dari LudoGH68)")
print("=" * 60)

time.sleep(float(CONFIG.get("STARTUP_DELAY", 2)))
console.clear()


# ============================================================
# SECTION: MAIN LOOP
# ============================================================

last_analyzed_candle_time = None
last_smc_update = 0.0
last_manual_recovery = 0.0
last_meta_rebuild = 0.0
last_stats_refresh = 0.0

best_model = None
best_risk = None
model_results = []

demand_zones = []
supply_zones = []

trend = "SIDEWAYS"
htf_trend = "SIDEWAYS"
atr_raw = None
atr_val = 0.0
atr_ok = False

session_ok = False
daily_pnl = 0.0
daily_loss_percent = 0.0

refresh_stats(force=True)

with Live(console=console, refresh_per_second=4, screen=True, transient=False,
          vertical_overflow="visible") as live:

    # ----- STARTUP -----
    try:
        df_smc = get_closed_data(TIMEFRAME_SMC, bars=500)
        if df_smc is not None and not df_smc.empty:
            demand_zones = detect_demand_zones(df_smc)
            supply_zones = detect_supply_zones(df_smc)

        if CONFIG.get("USE_MANUAL_RECOVERY", True):
            recover_manual_entries()

        rebuild_position_meta()
        rebuild_partial_plans()
    except Exception as e:
        runtime_message(f"Startup: {e}")

    time.sleep(float(CONFIG.get("STARTUP_DELAY", 2)))

    # ----- MAIN LOOP -----
    while True:
        try:
            current_time = time.time()

            if not mt5.account_info():
                runtime_message("Reconnecting MT5...")
                connected = False
                for attempt in range(int(CONFIG.get("RECONNECT_RETRIES", 5))):
                    try:
                        if mt5.initialize():
                            connected = True
                            runtime_message("MT5 reconnected")
                            break
                    except Exception:
                        pass
                    time.sleep(float(CONFIG.get("RECONNECT_DELAY", 5)))
                if not connected:
                    runtime_message("MT5 reconnect failed")
                    time.sleep(float(CONFIG.get("RECONNECT_DELAY", 5)))
                continue

            df = get_closed_data(TIMEFRAME_ENTRY)
            if df is None or df.empty:
                runtime_message("Waiting data...")
                time.sleep(float(CONFIG.get("MAIN_LOOP_INTERVAL", 1.0)))
                continue

            bid, ask = get_live_price()
            session_ok = in_session()

            smc_interval = float(CONFIG.get("SMC_UPDATE_INTERVAL", 60))
            if current_time - last_smc_update >= smc_interval:
                df_smc = get_closed_data(TIMEFRAME_SMC, bars=500)
                if df_smc is not None and not df_smc.empty:
                    demand_zones = detect_demand_zones(df_smc)
                    supply_zones = detect_supply_zones(df_smc)
                last_smc_update = current_time

            if CONFIG.get("USE_MANUAL_RECOVERY", True):
                interval = float(MANUAL_PROFILE.get("CHECK_INTERVAL", 5))
                if current_time - last_manual_recovery >= interval:
                    recover_manual_entries()
                    rebuild_position_meta()
                    rebuild_partial_plans()
                    last_manual_recovery = current_time

            if current_time - last_meta_rebuild >= float(
                CONFIG.get("META_REBUILD_INTERVAL", 15)
            ):
                rebuild_position_meta()
                rebuild_partial_plans()
                last_meta_rebuild = current_time

            current_positions = mt5.positions_get(symbol=SYMBOL) or []
            active_tickets = {int(p.ticket) for p in current_positions}

            for tk in list(POSITION_META.keys()):
                try:
                    ticket = int(tk)
                except Exception:
                    POSITION_META.pop(tk, None)
                    continue
                if ticket not in active_tickets:
                    POSITION_META.pop(tk, None)

            for tk in list(PARTIAL_STATE.keys()):
                try:
                    ticket = int(tk)
                except Exception:
                    PARTIAL_STATE.pop(tk, None)
                    continue
                if ticket not in active_tickets:
                    PARTIAL_STATE.pop(tk, None)

            daily_pnl, daily_loss_percent = check_daily_loss()

            closed_candle_time = get_last_closed_candle_time(TIMEFRAME_ENTRY)
            new_closed_candle = (
                closed_candle_time is not None
                and closed_candle_time != last_analyzed_candle_time
            )

            if new_closed_candle:
                last_analyzed_candle_time = closed_candle_time

                atr_raw = atr_value(df)
                atr_val = round(atr_raw, 2) if atr_raw is not None else 0.0
                atr_ok = atr_raw is not None and atr_raw >= float(CONFIG.get("MIN_ATR_VALUE", 1.0))

                _fvg_tf = globals().get("FVG_TIMEFRAME") or timeframe_from_name(
                    CONFIG.get("FVG_TIMEFRAME", "M5")
                )
                fvg_df = get_closed_data(_fvg_tf)
                if fvg_df is not None and not fvg_df.empty:
                    update_fvg_state(fvg_df, atr=atr_value(fvg_df))

                trend = trend_m5()
                htf_trend = get_higher_timeframe_trend()
                choch = detect_choch(df, int(CONFIG.get("SWING_STRICTNESS", 1)))
                wick = detect_rejection_wick(df)
                sweep_buy = smart_liquidity_sweep(df, "BUY", atr_raw=atr_raw)
                sweep_sell = smart_liquidity_sweep(df, "SELL", atr_raw=atr_raw)

                DIAG_STATE["swing_buy"] = find_last_swing_for_fib(df, "BUY")[0] is not None
                DIAG_STATE["swing_sell"] = find_last_swing_for_fib(df, "SELL")[0] is not None
                DIAG_STATE["demand_zones"] = len(demand_zones)
                DIAG_STATE["supply_zones"] = len(supply_zones)
                DIAG_STATE["htf_trend"] = htf_trend
                DIAG_STATE["choch"] = choch
                DIAG_STATE["rej_wick"] = wick
                DIAG_STATE["sweep_buy"] = sweep_buy
                DIAG_STATE["sweep_sell"] = sweep_sell

                ctx = {
                    "df_ltf": df,
                    "df_htf": get_closed_data(TIMEFRAME_HTF, bars=100),
                    "htf_trend": htf_trend,
                    "trend_ltf": trend,
                    "demand_zones": demand_zones,
                    "supply_zones": supply_zones,
                    "atr_raw": atr_raw,
                    "atr_now": atr_raw or 3.0,
                    "choch_ltf": choch,
                    "wick_ltf": wick,
                    "sweep_buy": sweep_buy,
                    "sweep_sell": sweep_sell,
                }

                for model_name in ("CONTINUATION", "REVERSAL", "SWEEP"):
                    flag_name = {
                        "CONTINUATION": "USE_MODEL_CONTINUATION",
                        "REVERSAL": "USE_MODEL_REVERSAL",
                        "SWEEP": "USE_MODEL_SWEEP",
                    }[model_name]
                    enabled = bool(CONFIG.get(flag_name, False))
                    MODEL_SCORES[model_name] = {
                        "enabled": enabled, "confluence": 0, "rr": 0.0, "direction": "-",
                        "valid": False, "status": "WAIT" if enabled else "DISABLED",
                        "reason": "Waiting for model evaluation" if enabled else "model off",
                        "met": [], "gate_score": 0, "gate_total": 5, "gates": {},
                    }

                model_results = evaluate_all_models(ctx, session_ok)
                GATE_PROGRESS.clear()
                for mr in model_results:
                    name = mr["model"]
                    gp = mr.get("gate_progress", {})
                    GATE_PROGRESS[name] = {
                        "enabled": True,
                        "score": mr.get("gate_score", 0),
                        "total": mr.get("gate_total", 5),
                        "gates": gp,
                        "direction": mr.get("direction", "-"),
                    }
                    MODEL_SCORES[name].update({
                        "gate_score": mr.get("gate_score", 0),
                        "gate_total": mr.get("gate_total", 5),
                        "gates": gp,
                        "direction": mr.get("direction", "-"),
                        "status": "GATE" if not mr.get("passed") else "WAIT",
                        "reason": mr.get("reason", "Gate incomplete") if not mr.get("passed") else "Gate OK",
                    })

                for model_name in ("CONTINUATION", "REVERSAL", "SWEEP"):
                    if model_name not in GATE_PROGRESS:
                        GATE_PROGRESS[model_name] = {
                            "enabled": False, "score": 0, "total": 5,
                            "gates": {}, "direction": "-",
                        }

                tick = mt5.symbol_info_tick(SYMBOL)
                symbol_info = mt5.symbol_info(SYMBOL)
                risk_candidates = []
                if tick is not None and symbol_info is not None:
                    for mr in model_results:
                        if not mr.get("passed"):
                            continue
                        direction = mr["direction"]
                        entry = tick.ask if direction == "BUY" else tick.bid
                        risk_data = calculate_risk(mr, entry, atr_raw, symbol_info, session_ok)
                        MODEL_SCORES[mr["model"]].update({
                            "confluence": risk_data["confluence"],
                            "rr": risk_data["rr"],
                            "direction": direction,
                            "valid": risk_data["ok"],
                            "status": "RISK_OK" if risk_data["ok"] else "BLOCKED",
                            "reason": risk_data["reason"] if not risk_data["ok"] else "Risk OK",
                            "met": risk_data["confluence_met"],
                        })
                        if risk_data["ok"]:
                            combined = dict(mr)
                            combined.update({
                                "entry": entry, "sl": risk_data["sl"], "lot": risk_data["lot"],
                                "rr": risk_data["rr"], "confluence": risk_data["confluence"],
                                "confluence_met": risk_data["confluence_met"], "risk_data": risk_data,
                            })
                            risk_candidates.append(combined)

                candidate_model = max(risk_candidates, key=lambda x: x["confluence"]) if risk_candidates else None
                best_model = candidate_model
                best_risk = candidate_model.get("risk_data") if candidate_model else None
                signal_reason = "No model passed risk"
                signal_status = "WAIT_RISK"

                if best_model:
                    if CONFIG.get("USE_ATR_FILTER", True) and not atr_ok:
                        signal_reason = f"ATR LOW < {CONFIG.get('MIN_ATR_VALUE', 1.0)}"
                        MODEL_SCORES[best_model["model"]]["status"] = "BLOCKED"
                        MODEL_SCORES[best_model["model"]]["reason"] = signal_reason
                        best_model = None
                        best_risk = None
                        signal_status = "BLOCKED"
                    elif CONFIG.get("USE_SESSION_FILTER", True) and not session_ok:
                        signal_reason = "Outside session"
                        MODEL_SCORES[candidate_model["model"]]["status"] = "BLOCKED"
                        MODEL_SCORES[candidate_model["model"]]["reason"] = signal_reason
                        best_model = None
                        best_risk = None
                        signal_status = "BLOCKED"
                    elif fake_breakout_filter(df) and candidate_model["model"] == "CONTINUATION":
                        signal_reason = "Fake breakout filter"
                        MODEL_SCORES[candidate_model["model"]]["status"] = "BLOCKED"
                        MODEL_SCORES[candidate_model["model"]]["reason"] = signal_reason
                        best_model = None
                        best_risk = None
                        signal_status = "BLOCKED"
                    else:
                        signal_status = "READY"
                        signal_reason = "All risk gates OK"

                if candidate_model and best_model is None:
                    display_model = candidate_model
                else:
                    display_model = best_model

                if display_model:
                    gp = GATE_PROGRESS.get(display_model["model"], {})
                    SIGNAL_STATE.update({
                        "status": signal_status, "model": display_model["model"],
                        "direction": display_model["direction"],
                        "confluence": float(display_model.get("confluence", 0)),
                        "rr": float(display_model.get("rr", 0)),
                        "entry": float(display_model.get("entry")) if display_model.get("entry") is not None else None,
                        "sl": float(display_model.get("sl")) if display_model.get("sl") is not None else None,
                        "lot": float(display_model.get("lot", 0)),
                        "reason": signal_reason,
                        "gate_score": gp.get("score", 0), "gate_total": gp.get("total", 5),
                    })
                else:
                    enabled_gates = [(n, g) for n, g in GATE_PROGRESS.items() if g.get("enabled", False)]
                    top = max(enabled_gates, key=lambda x: x[1].get("score", 0), default=None)
                    if top:
                        n, g = top
                        SIGNAL_STATE.update({
                            "status": "WAIT_GATE", "model": n,
                            "direction": g.get("direction", "-"),
                            "confluence": 0, "rr": 0.0, "entry": None, "sl": None, "lot": 0,
                            "reason": MODEL_SCORES.get(n, {}).get("reason", "Gate incomplete"),
                            "gate_score": g.get("score", 0), "gate_total": g.get("total", 5),
                        })
                    else:
                        SIGNAL_STATE.update({
                            "status": "WAITING", "model": "-", "direction": "-",
                            "confluence": 0, "rr": 0.0, "entry": None, "sl": None, "lot": 0,
                            "reason": "No enabled model", "gate_score": 0, "gate_total": 5,
                        })

                if (best_model and best_risk
                        and not trading_disabled_today
                        and CONFIG.get("USE_AUTO_TRADE", True)
                        and session_ok):
                    atr_now = atr_raw if atr_raw else 3.0
                    can, reason = can_reentry(best_model["model"], best_model["direction"],
                                              best_model["entry"], atr_now)
                    if can:
                        SIGNAL_STATE["status"] = "READY"
                        runtime_message(f"EXEC {best_model['model']} {best_model['direction']} conf={best_risk['confluence']}%")
                        opened = open_trade(best_model, best_risk, symbol_info)
                        if opened:
                            SIGNAL_STATE["status"] = "EXECUTED"
                    else:
                        SIGNAL_STATE["status"] = "WAIT_REENTRY"
                        SIGNAL_STATE["reason"] = reason
                        runtime_message(f"Skip entry — {reason}")
                elif best_model and trading_disabled_today:
                    SIGNAL_STATE["status"] = "BLOCKED"
                    SIGNAL_STATE["reason"] = "Daily loss limit"

            manage_partial_close()
            manage_break_even()
            manage_trailing_sl()

            if current_time - last_stats_refresh >= float(CONFIG.get("STATS_REFRESH_INTERVAL", 10)):
                refresh_stats()
                last_stats_refresh = current_time

            account = mt5.account_info()
            positions = mt5.positions_get(symbol=SYMBOL)
            current_session, _, session_trade_allowed = get_session_status_text()

            live.update(render_rich_dashboard(
                account=account, positions=positions, bid=bid, ask=ask,
                price_direction="=", current_session=current_session,
                session_trade_allowed=session_trade_allowed, trend=trend,
                htf_trend=htf_trend, atr_val=atr_val, atr_ok=atr_ok,
                best_model=best_model, fakeout=fake_breakout_filter(df),
                daily_pnl=daily_pnl, daily_loss_percent=daily_loss_percent,
                trading_disabled_today=trading_disabled_today,
            ))

            time.sleep(float(CONFIG.get("MAIN_LOOP_INTERVAL", 1.0)))

        except KeyboardInterrupt:
            break
        except Exception as e:
            log_error(f"main loop: {traceback.format_exc()}")
            runtime_message(f"ERROR: {e}")
            time.sleep(float(CONFIG.get("MAIN_LOOP_INTERVAL", 1.0)))


# ============================================================
# END OF FILE — v6.3.4
# ============================================================
