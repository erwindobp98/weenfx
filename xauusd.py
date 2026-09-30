# ============================================================
# Wfx PRO — SMC + FIBONACCI — v6.3.2
# ------------------------------------------------------------
# EA untuk MetaTrader 5 (XAUUSD).
# Strategi: Smart Money Concepts (SMC) + Fibonacci.
# Model: CONTINUATION, REVERSAL, SWEEP.
# PERCENT 33/33 partial + rebuild RR-based
# ============================================================


# ============================================================
# SECTION: STDLIB IMPORTS
# Library bawaan Python
# ============================================================
from pathlib import Path              # Handle path file (config, state, log)
from datetime import datetime, timedelta  # Waktu: daily reset, history deals
import json                           # Baca/tulis file JSON (config, state)
import traceback                      # Stack trace saat error
import time                           # sleep, time.time() untuk interval
import pytz                           # Timezone (WIB)


# ============================================================
# SECTION: THIRD-PARTY IMPORTS
# Library eksternal (install via pip)
# ============================================================
import numpy as np                    # Operasi array (perhitungan ATR)
import pandas as pd                   # DataFrame untuk OHLC dari MT5
from colorama import init             # Init warna terminal (Windows)
from rich.console import Console, Group   # Console + Group panel
from rich.table import Table          # Tabel untuk dashboard
from rich.panel import Panel          # Kotak border
from rich.text import Text            # Text berwarna
from rich.live import Live            # Update dashboard tanpa flicker


# ============================================================
# SECTION: CONFIG BOOTSTRAP
# Path file config, state, log
# ============================================================
BASE_DIR = Path(__file__).resolve().parent   # Folder script ini
CONFIG_FILE = BASE_DIR / "config.json"        # Path config user
STATE_FILE = BASE_DIR / "state.json"          # Path state runtime
ERROR_LOG = BASE_DIR / "error.log"            # Path log error


# ============================================================
# SECTION: DEFAULT_CONFIG
# Nilai default. Kalau config.json tidak ada / kurang key,
# di-merge dari sini.
# ============================================================
DEFAULT_CONFIG = {
    # ----- SYMBOL & TIMEFRAMES -----
    "SYMBOL": "XAUUSD.vxc",       # Symbol trading (sesuaikan broker)
    "TIMEFRAME_ENTRY": "M5",      # TF entry signal (candle 5 menit)
    "TIMEFRAME_SMC": "M15",       # TF deteksi zona SMC
    "TIMEFRAME_HTF": "H1",        # TF trend besar

    # ----- RISK MANAGEMENT -----
    "RISK_PER_TRADE_PCT": 1.0,    # Risiko per trade (% balance) — belum dipakai
    "MAX_DAILY_LOSS_PCT": 20.0,   # Stop entry kalau daily loss ≥ 20%
    "MAX_OPEN_POSITIONS": 6,      # Max posisi global
    "MAX_PER_MODEL": 2,           # Fallback max per model

    # ----- MODEL TOGGLES -----
    "USE_MODEL_CONTINUATION": True,   # Aktifkan model follow trend
    "USE_MODEL_REVERSAL": True,       # Aktifkan model reversal
    "USE_MODEL_SWEEP": True,          # Aktifkan model sweep

    # ----- MAX POSISI PER MODEL -----
    "MAX_POSITIONS_CONTINUATION": 2,  # Max CONTINUATION searah
    "MAX_POSITIONS_REVERSAL": 2,      # Max REVERSAL searah
    "MAX_POSITIONS_SWEEP": 2,         # Max SWEEP searah

    # ----- SL / TP -----
    "SL_ATR_MULT": 1.5,           # SL = ATR × 1.5 (fallback)
    "TP_RR_TP1": 1.0,             # TP1 = entry ± risk × 1.0
    "TP_RR_TP2": 2.0,             # TP2 = entry ± risk × 2.0
    "TP_RR_TP3": 3.0,             # TP3 = entry ± risk × 3.0
    "MIN_RR_TP3": 1.2,            # RR minimal
    "MAX_RR_TP3": 8.0,            # RR soft cap
    "HARD_MAX_RR_TP3": 12.0,      # RR hard cap

    # ----- TRADE MANAGEMENT -----
    "BE_TRIGGER_ATR": 1.0,        # BE aktif saat profit ≥ 1× ATR
    "TRAIL_TRIGGER_ATR": 2.0,     # Trailing aktif saat profit ≥ 2× ATR
    "TRAIL_SECURE_PCT": 50,       # SL = entry + profit × 50%

    # ----- PARTIAL CLOSE (v6.3.2: PERCENT 33/33) -----
    "PARTIAL_MODE": "PERCENT",    # ← UBAH: dari "LOT" ke "PERCENT"
    "PARTIAL_PCT_1": 33,          # ← UBAH: TP1 tutup 33% lot
    "PARTIAL_PCT_2": 33,          # ← UBAH: TP2 tutup 33% lot
    "PARTIAL_LOT_1": 0.01,        # (mode LOT, tidak dipakai)
    "PARTIAL_LOT_2": 0.01,        # (mode LOT, tidak dipakai)
    "PARTIAL_MIN_LOT": 0.03,      # Lot minimal untuk aktifkan partial

    # ----- ENTRY FILTERS -----
    "MIN_CONFLUENCE": 70,         # Skor minimum entry
    "USE_FIB_GATE": False,        # Fib sebagai gate/flag
    "USE_SESSION_FILTER": True,   # Filter session
    "SESSION_TIMEZONE": "Asia/Jakarta",
    "USE_ATR_FILTER": True,       # ATR ≥ MIN_ATR_VALUE
    "MIN_ATR_VALUE": 0.8,         # Minimal ATR
    "USE_CLOSED_CANDLE_LOCK": True,

    # ----- SMC / ZONE -----
    "SMC_ZONE_SENSITIVITY": 0.10, # Body candle > ATR × 0.10 = zona valid
    "SMC_MAX_ZONES": 20,          # Max 20 zona per arah
    "SWEEP_LOOKBACK": 20,         # Lookback 20 candle
    "SWING_STRICTNESS": 1,        # Swing strictness (1=longgar)
    "ZONE_TOLERANCE_ATR": 0.20,   # Toleransi zona
    "MIN_SWING_SIZE": 1.5,        # Swing minimal 1.5 poin
    "SWING_FIB_LOOKBACK": 80,     # Lookback swing fib

    # ----- FILTER TOGGLES -----
    "USE_CHOCH": True,
    "USE_REJECTION_WICK": True,
    "USE_SMART_SWEEP": True,
    "USE_ORDER_BLOCK": True,
    "USE_FVG": True,
    "USE_CONFLUENCE_CHECK": True,

    # ----- FIBONACCI ENTRY ZONES -----
    "FIB_ENTRY_ZONE_CONTINUATION": [0.236, 0.886],
    "FIB_ENTRY_ZONE_REVERSAL": [0.5, 0.886],
    "FIB_ENTRY_ZONE_SWEEP": [0.382, 0.886],

    # ----- ANTI RE-ENTRY -----
    "MIN_REENTRY_ATR": 1.5,       # Jarak minimum re-entry = 1.5× ATR
    "LOSS_REENTRY_ATR": 1.5,      # Trigger averaging
    "RETRACE_MIN_PERCENT": 20.0,  # Retrace setelah TP3

    # ----- LOT SIZING -----
    "LOT_SIZE": 0.01,             # Fallback lot
    "LOT_TIER_1": 0.01,           # Confluence 70-79% → 0.01
    "LOT_TIER_2": 0.03,           # Confluence 80-89% → 0.03
    "LOT_TIER_3": 0.06,           # Confluence 90-100% → 0.06
    "MIN_LOT_SIZE": 0.01,
    "MAX_LOT_SIZE": 0.06,
    "HARD_LOT_CAP": 0.06,

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
    "SHOW_DIAGNOSTIC_PANEL": True,

    # ----- MANUAL RECOVERY -----
    "USE_MANUAL_RECOVERY": True,
    "MANUAL_PROFILE": {
        "SL_TP_MODE": "HYBRID",
        "RR": 1.5,
        "FIB_TP_EXT": 1.618,
        "MIN_SL_PRICE": 3.0,
        "MAX_SL_PRICE": 20.0,
        "CHECK_INTERVAL": 30,
        "OVERRIDE_EXISTING": False,
    },

    # ----- FIB SL -----
    "USE_FIB_SL": True,
    "SL_BUFFER": 1.0,
    "MIN_SL_DISTANCE": 4.0,
}


# ============================================================
# SECTION: CONFIG HELPERS
# ============================================================
def _deep_merge(default, current):
    """Merge nested dict: default di-merge dengan current."""
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
    """Load config dari file atau buat baru."""
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
    """Load state dari file."""
    path = Path(path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state, path=STATE_FILE):
    """Simpan state ke file."""
    path = Path(path)
    try:
        path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError:
        pass


def log_error(exc_text):
    """Log error ke file."""
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
print("WEENfx PRO - v6.3.2")
print("=" * 60)

CONFIG = load_or_create_config()

import MetaTrader5 as mt5

init(autoreset=True)
console = Console()

runtime_message_text = ""


def timeframe_from_name(value):
    """Konversi nama TF ke konstanta MT5."""
    if isinstance(value, int):
        return value
    mapping = {
        "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    return mapping.get(str(value).upper(), mt5.TIMEFRAME_M5)


def apply_config(c):
    """Terapkan config ke globals."""
    g = globals()
    for key, value in c.items():
        if key in ("SESSION_FILTER", "SESSION_TIMEZONE", "MANUAL_PROFILE"):
            continue
        if key in ("TIMEFRAME_ENTRY", "TIMEFRAME_HTF", "TIMEFRAME_SMC"):
            g[key] = timeframe_from_name(value)
        else:
            g[key] = value


apply_config(CONFIG)

SESSION_CONFIG = CONFIG.get("SESSION_FILTER", DEFAULT_CONFIG["SESSION_FILTER"])
MANUAL_PROFILE = CONFIG.get("MANUAL_PROFILE", DEFAULT_CONFIG["MANUAL_PROFILE"])
WIB = pytz.timezone(CONFIG.get("SESSION_TIMEZONE", "Asia/Jakarta"))
SESSION_STATUS = "OUT OF SESSION"


def runtime_message(message):
    """Set pesan runtime untuk EVENT panel."""
    global runtime_message_text
    try:
        txt = str(message)
        txt = txt.replace("[", "(").replace("]", ")")
        runtime_message_text = txt[:250]
    except Exception:
        runtime_message_text = ""


def connect_mt5():
    """Connect ke MT5 dengan retry."""
    print("[..] Connecting to MT5...")
    retries = 5
    delay = 5
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
    """Ambil OHLC dari MT5."""
    rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, bars)
    if rates is None:
        return pd.DataFrame()
    return pd.DataFrame(rates)


def get_closed_data(tf, bars=300):
    """Ambil data closed only (buang candle current)."""
    df = get_data(tf, bars + 1)
    if df is None or df.empty or len(df) < 3:
        return pd.DataFrame()
    return df.iloc[:-1].copy().reset_index(drop=True)


def get_mt5_candle_time(tf):
    """Waktu candle current."""
    rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, 1)
    if rates is None or len(rates) == 0:
        return None
    return rates[0]['time']


def get_last_closed_candle_time(tf):
    """Waktu candle terakhir yang closed."""
    df = get_closed_data(tf, bars=2)
    if df is None or df.empty:
        return None
    return df['time'].iloc[-1]


def is_new_candle_mt5(tf):
    """Cek apakah candle baru muncul."""
    global last_candle_time
    current_candle_time = get_mt5_candle_time(tf)
    if current_candle_time is None:
        return False
    if last_candle_time is None:
        last_candle_time = current_candle_time
        return True
    if current_candle_time != last_candle_time:
        last_candle_time = current_candle_time
        return True
    return False


def get_live_price():
    """Ambil bid/ask."""
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick:
        return tick.bid, tick.ask
    return None, None


# ============================================================
# SECTION: STATE PERSISTENCE
# ============================================================
POSITION_META = {}    # {ticket: {model, sl_source, orig_volume, max_move}}
PARTIAL_STATE = {}    # {ticket: {tp1, tp2, tp3, tp1_done, vol1, vol2}}

_state = load_state()
_today_wib = datetime.now(WIB).date()
_state_date = _state.get("daily_date")

if _state_date == str(_today_wib):
    daily_start_balance = float(_state.get("daily_start_balance", _account_info.balance))
    trading_disabled_today = bool(_state.get("trading_disabled_today", False))
else:
    daily_start_balance = _account_info.balance
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


def persist_state():
    """Simpan state ke file."""
    try:
        save_state({
            "daily_date": str(daily_date),
            "daily_start_balance": daily_start_balance,
            "trading_disabled_today": trading_disabled_today,
            "position_meta": {str(k): v for k, v in POSITION_META.items()},
            "partial_state": {str(k): v for k, v in PARTIAL_STATE.items()},
        })
    except Exception:
        pass


persist_state()


# ============================================================
# SECTION: TREND DETECTION
# ============================================================
def trend_m5():
    """Trend dari M15 (EMA20 vs EMA50)."""
    df = get_closed_data(mt5.TIMEFRAME_M15)
    if df.empty:
        return "SIDEWAYS"
    df['ema20'] = df['close'].ewm(span=20).mean()
    df['ema50'] = df['close'].ewm(span=50).mean()
    if df['ema20'].iloc[-1] > df['ema50'].iloc[-1]:
        return "BULLISH"
    elif df['ema20'].iloc[-1] < df['ema50'].iloc[-1]:
        return "BEARISH"
    return "SIDEWAYS"


def get_higher_timeframe_trend():
    """Trend dari H1 (EMA20/50/100)."""
    df = get_closed_data(TIMEFRAME_HTF, bars=100)
    if df is None or df.empty:
        return "SIDEWAYS"
    df['ema20'] = df['close'].ewm(span=20).mean()
    df['ema50'] = df['close'].ewm(span=50).mean()
    df['ema100'] = df['close'].ewm(span=100).mean()
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
def atr_value(df):
    """Hitung ATR (14 period)."""
    if df is None or len(df) < 15:
        return None
    prev_close = df['close'].shift(1)
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - prev_close).abs(),
        (df['low'] - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    value = atr.iloc[-1]
    return float(value) if pd.notna(value) else None


def get_atr_current(df=None):
    """ATR saat ini."""
    if df is None:
        df = get_closed_data(TIMEFRAME_ENTRY, bars=100)
    return atr_value(df)


def calculate_atr_series(df, period=14):
    """Tambah kolom ATR ke DataFrame."""
    df['tr'] = np.maximum(df['high'] - df['low'],
                          np.maximum(abs(df['high'] - df['close'].shift(1)),
                                     abs(df['low'] - df['close'].shift(1))))
    df['atr'] = df['tr'].rolling(window=period).mean()
    return df


# ============================================================
# SECTION: SWING & STRUCTURE
# ============================================================
def detect_swing_points(df, lookback=10):
    """Cari swing high/low."""
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
    """Deteksi Change of Character."""
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

    # Fallback 1: window 20
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

    # Fallback 2: window 10
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
    """Candle terakhir."""
    if df is None or len(df) < 1:
        return None
    return df.iloc[-1]


def detect_rejection_wick(df):
    """Deteksi wick rejection."""
    candle = _signal_candle(df)
    if candle is None:
        return None
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    lower_wick = min(candle['open'], candle['close']) - candle['low']
    total_range = candle['high'] - candle['low']
    if total_range <= 0:
        return None
    if lower_wick / total_range >= 0.45 and lower_wick >= upper_wick:
        return "BULL"
    if upper_wick / total_range >= 0.45 and upper_wick >= lower_wick:
        return "BEAR"
    return None


def detect_order_block(df, atr=None):
    """Deteksi order block."""
    if df is None or len(df) < 5:
        return None
    if atr is None:
        atr = atr_value(df)
    if atr is None or atr <= 0:
        return None
    base = df.iloc[-2]
    impulse = df.iloc[-1]
    impulse_body = abs(impulse['close'] - impulse['open'])
    if impulse_body < atr * 0.8:
        return None
    if base['close'] < base['open'] and impulse['close'] > impulse['open'] and impulse['close'] > base['high']:
        return "BULL"
    if base['close'] > base['open'] and impulse['close'] < impulse['open'] and impulse['close'] < base['low']:
        return "BEAR"
    return None


def detect_fvg(df, atr=None):
    """Deteksi Fair Value Gap."""
    if df is None or len(df) < 3:
        return None
    a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    if atr is None:
        atr = atr_value(df)
    min_gap = 0.0 if atr is None else max(0.01, atr * 0.05)
    if c['low'] > a['high'] + min_gap and b['close'] > b['open']:
        return "BULL"
    if c['high'] < a['low'] - min_gap and b['close'] < b['open']:
        return "BEAR"
    return None


def detect_divergence(df, direction, lookback=15):
    """Deteksi divergence sederhana."""
    if df is None or len(df) < lookback + 2:
        return False
    try:
        highs = df['high'].tail(lookback).values
        lows = df['low'].tail(lookback).values
        last_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        if direction == "SELL":
            if highs[-1] > highs[-2] and last_price < prev_price:
                return True
        elif direction == "BUY":
            if lows[-1] < lows[-2] and last_price > prev_price:
                return True
    except (KeyError, IndexError, ValueError):
        return False
    return False


def fake_breakout_filter(df):
    """Deteksi fake breakout."""
    if len(df) < 2:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]
    body = abs(last['close'] - last['open'])
    range_candle = last['high'] - last['low']
    if range_candle == 0:
        return False
    body_ratio = body / range_candle
    if body_ratio < 0.25:
        return True
    if prev['close'] == last['close']:
        return True
    return False


# ============================================================
# SECTION: SMC ZONES
# ============================================================
def detect_demand_zones(df, sensitivity=0.10):
    """Deteksi zona demand."""
    zones = []
    df = calculate_atr_series(df.copy())
    if len(df) < 20:
        return []
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
                        if not any(abs(z[0] - zone_low) < atr_val * 0.5 for z in zones):
                            zones.append((zone_low, zone_high, strength, "DEMAND"))
        except (KeyError, ValueError, TypeError):
            continue
    return zones[-SMC_MAX_ZONES:] if zones else []


def detect_supply_zones(df, sensitivity=0.10):
    """Deteksi zona supply."""
    zones = []
    df = calculate_atr_series(df.copy())
    if len(df) < 20:
        return []
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
                        if not any(abs(z[0] - zone_low) < atr_val * 0.5 for z in zones):
                            zones.append((zone_low, zone_high, strength, "SUPPLY"))
        except (KeyError, ValueError, TypeError):
            continue
    return zones[-SMC_MAX_ZONES:] if zones else []


def price_in_smc_zone(price, zones, zone_type=None, tolerance=0.0):
    """Cek harga di zona SMC."""
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
    """Sweep valid: wick break + close reclaim + displacement."""
    if lookback is None:
        lookback = SWEEP_LOOKBACK
    if df is None or len(df) < lookback + 3:
        return False

    if atr_raw is None:
        atr_raw = atr_value(df)
    if atr_raw is None or atr_raw <= 0:
        return False

    min_displacement = atr_raw * 0.5

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
    """Fib retracement."""
    diff = swing_high - swing_low
    return swing_low + diff * (1 - level)


def fib_extension(swing_low, swing_high, level):
    """Fib extension BUY."""
    diff = swing_high - swing_low
    return swing_low + diff * level


def fib_extension_sell(swing_low, swing_high, level):
    """Fib extension SELL."""
    diff = swing_high - swing_low
    return swing_high - diff * level


def find_last_swing_for_fib(df, direction, lookback=None):
    """Cari swing low/high terakhir."""
    if lookback is None:
        lookback = SWING_FIB_LOOKBACK
    if df is None or len(df) < 30:
        return None, None

    highs, lows = detect_swing_points(df, SWING_STRICTNESS)

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
    """Cek harga di zona fib."""
    if None in (price, swing_low, swing_high):
        return False
    level_a = fib_retracement(swing_low, swing_high, zone_low)
    level_b = fib_retracement(swing_low, swing_high, zone_high)
    lo, hi = min(level_a, level_b), max(level_a, level_b)
    return lo <= price <= hi


def resolve_fib_sl(swing_low, swing_high, direction, entry):
    """Hitung SL dari fib 0.786 ± buffer."""
    if not USE_FIB_SL:
        return None
    if None in (swing_low, swing_high):
        return None
    if swing_high <= swing_low:
        return None

    min_sl_dist = float(CONFIG.get("MIN_SL_DISTANCE", 1.0))
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
    """Deteksi session aktif."""
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
    """True kalau ada session aktif yang enabled."""
    active = detect_sessions()
    if not USE_SESSION_FILTER or not SESSION_CONFIG.get("ENABLED", True):
        return True
    for name in active:
        if SESSION_CONFIG.get(name, {}).get("ENABLED", False):
            return True
    return False


def get_session_status_text():
    """Status session untuk display."""
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
    """Cek daily loss & disable trading."""
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
    if daily_loss_percent >= MAX_DAILY_LOSS_PCT:
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
    ZONE_TOLERANCE_ATR = 0.15
    NEEDS_SWEEP = False
    NEEDS_CHOCH_OR_WICK = True
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
        }

    def _diag(self, reason):
        self.result["reason"] = reason

    def gate_htf(self):
        if not self.HTF_REQUIRED:
            return True
        htf = self.ctx.get("htf_trend", "SIDEWAYS")
        if htf not in ("BULLISH", "BEARISH"):
            self._diag(f"HTF={htf}")
            return False
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

        if self.NAME == "SWEEP":
            if has_sweep and wick_ok:
                return True
            self._diag(f"no-confirm(sweep={has_sweep},wick={wick_ok})")
            return False

        if self.NAME == "REVERSAL":
            confirmations = sum([has_sweep, choch_ok, wick_ok])
            if confirmations >= 3:
                return True
            self._diag(f"REVERSAL confirm={confirmations}/3 (need 3)")
            return False

        confirmations = sum([has_sweep, choch_ok, wick_ok])
        if confirmations >= 2:
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
        if size < MIN_SWING_SIZE:
            self._diag(f"swing-small({size:.1f})")
            return False
        self.result["swing_low"] = swing_low
        self.result["swing_high"] = swing_high
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
        return True

    def evaluate(self):
        raise NotImplementedError


# ============================================================
# SECTION: CONTINUATION MODEL (v5.4 logic)
# ============================================================
class ContinuationModel(BaseModel):
    NAME = "CONTINUATION"
    FIB_ZONE = CONFIG.get("FIB_ZONE_CONTINUATION", [0.382, 0.786])
    ZONE_TOLERANCE_ATR = 0.10
    HTF_REQUIRED = True

    def evaluate(self):
        """CONTINUATION: 1 dari 4 konfirmasi (LTF atau HTF)."""
        if not self.gate_htf():
            return self.result

        htf = self.ctx.get("htf_trend", "SIDEWAYS")
        direction = "BUY" if htf == "BULLISH" else "SELL"
        self.result["direction"] = direction

        if not self.gate_zone(direction):
            return self.result

        df_ltf = self.ctx["df_ltf"]
        df_htf = self.ctx.get("df_htf", df_ltf)
        ltf_choch = self.ctx.get("choch_ltf")
        ltf_rej = self.ctx.get("wick_ltf")
        htf_choch = detect_choch(df_htf, SWING_STRICTNESS)
        htf_rej = detect_rejection_wick(df_htf)

        confirmed = (
            (direction == "BUY" and (
                ltf_choch == "BULL_CHoCH" or ltf_rej == "BULL" or
                htf_choch == "BULL_CHoCH" or htf_rej == "BULL"
            )) or
            (direction == "SELL" and (
                ltf_choch == "BEAR_CHoCH" or ltf_rej == "BEAR" or
                htf_choch == "BEAR_CHoCH" or htf_rej == "BEAR"
            ))
        )
        if not confirmed:
            self._diag(f"no-Confirm(choch={ltf_choch},wick={ltf_rej})")
            return self.result

        self.result["choch"] = ltf_choch
        self.result["wick"] = ltf_rej
        self.result["sweep"] = False

        if not self.gate_swing(direction):
            return self.result

        if not self.gate_fib(direction):
            return self.result

        self.result["passed"] = True
        return self.result


# ============================================================
# SECTION: REVERSAL MODEL (v5.4 logic)
# ============================================================
class ReversalModel(BaseModel):
    NAME = "REVERSAL"
    FIB_ZONE = CONFIG.get("FIB_ZONE_REVERSAL", [0.786, 0.886])
    ZONE_TOLERANCE_ATR = 0.15
    HTF_REQUIRED = False

    def evaluate(self):
        """REVERSAL: 4 jalur masuk."""
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
            return self.result

        self.result["direction"] = direction

        has_sweep = False
        if direction == "BUY" and sweep_buy:
            has_sweep = True
        elif direction == "SELL" and sweep_sell:
            has_sweep = True

        choch_ok = (
            (direction == "BUY" and mss == "BULL_CHoCH") or
            (direction == "SELL" and mss == "BEAR_CHoCH")
        )
        wick_ok = (
            (direction == "BUY" and rej == "BULL") or
            (direction == "SELL" and rej == "BEAR")
        )

        # 4 jalur masuk
        if has_sweep and (choch_ok or wick_ok):
            pass
        elif choch_ok and wick_ok:
            pass
        elif choch_ok and not has_sweep and not wick_ok:
            self._diag(f"choch-only({mss})")
        elif wick_ok and not has_sweep and not choch_ok:
            self._diag(f"wick-only({rej})")
        else:
            self._diag(f"no-confirm(sweep={has_sweep},choch={mss},wick={rej})")
            return self.result

        if not self.gate_zone(direction):
            return self.result

        self.result["choch"] = mss
        self.result["wick"] = rej
        self.result["sweep"] = has_sweep

        if not self.gate_swing(direction):
            return self.result

        if not self.gate_fib(direction):
            return self.result

        self.result["passed"] = True
        return self.result


# ============================================================
# SECTION: SWEEP MODEL (v5.4 logic)
# ============================================================
class SweepModel(BaseModel):
    NAME = "SWEEP"
    FIB_ZONE = CONFIG.get("FIB_ZONE_SWEEP", [0.382, 0.786])
    ZONE_TOLERANCE_ATR = 0.10
    HTF_REQUIRED = False

    def evaluate(self):
        """SWEEP: hanya sweep + wick."""
        sweep_buy = self.ctx.get("sweep_buy", False)
        sweep_sell = self.ctx.get("sweep_sell", False)

        direction = None
        if sweep_buy:
            direction = "BUY"
        elif sweep_sell:
            direction = "SELL"

        if direction is None:
            self._diag("no-Sweep")
            return self.result

        self.result["direction"] = direction

        wick = self.ctx.get("wick_ltf")
        if direction == "BUY" and wick != "BULL":
            self._diag(f"no-Wick({wick})")
            return self.result
        if direction == "SELL" and wick != "BEAR":
            self._diag(f"no-Wick({wick})")
            return self.result

        if not self.gate_zone(direction):
            return self.result

        self.result["wick"] = wick
        self.result["sweep"] = True

        if not self.gate_swing(direction):
            return self.result

        if not self.gate_fib(direction):
            return self.result

        self.result["passed"] = True
        return self.result


# ============================================================
# SECTION: CONFLUENCE SCORE
# ============================================================
def calculate_confluence(model_result, ctx, session_ok):
    """Skor 0-100 untuk model yang lolos gate."""
    if not model_result or not model_result.get("passed"):
        return 0, []

    score = 0
    met = []
    direction = model_result["direction"]

    htf = ctx.get("htf_trend", "SIDEWAYS")
    want_htf = "BULLISH" if direction == "BUY" else "BEARISH"
    if htf == want_htf:
        score += 20
        met.append("HTF")

    if model_result.get("poi_zone"):
        score += 20
        met.append("POI")

    if model_result.get("choch"):
        score += 15
        met.append("CHoCH")

    if model_result.get("wick"):
        score += 10
        met.append("WICK")

    if model_result.get("fib_ok"):
        score += 15
        met.append("FIB")

    if session_ok:
        score += 10
        met.append("SESSION")

    met.append("RR_PENDING")
    return score, met


def add_rr_score(score, met, rr):
    """Tambah 10 poin kalau RR ≥ 2.0."""
    if "RR_PENDING" in met:
        met.remove("RR_PENDING")
    if rr >= 2.0:
        score += 10
        met.append("RR")
    return score, met


def evaluate_all_models(ctx, session_ok):
    """Evaluasi 3 model, return yang lolos."""
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
    """Fib SL dulu, fallback ATR."""
    if atr_raw is None or atr_raw <= 0:
        return None, "no-atr"

    if USE_FIB_SL and swing_low is not None and swing_high is not None:
        fib_sl = resolve_fib_sl(swing_low, swing_high, direction, entry)
        if fib_sl is not None:
            return fib_sl, "FIB"

    sl_distance = atr_raw * float(SL_ATR_MULT)
    if direction == "BUY":
        sl = entry - sl_distance
    else:
        sl = entry + sl_distance
    return sl, "ATR"


# ============================================================
# SECTION: TP RESOLVER (RR-based)
# ============================================================
def resolve_tp(entry, sl, direction):
    """Hitung TP1, TP2, TP3 dari RR × risk."""
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

    return {
        "tp1": tp1, "tp2": tp2, "tp3": tp3,
        "mode": "RR", "risk": risk,
        "rr1": rr1, "rr2": rr2, "rr3": rr3,
    }


def validate_tp(tp_plan, entry, sl, direction):
    """Validasi RR TP3."""
    if tp_plan is None:
        return False, 0.0, None

    min_rr = float(CONFIG.get("MIN_RR_TP3", 1.2))
    max_rr = float(CONFIG.get("MAX_RR_TP3", 8.0))
    hard_max_rr = float(CONFIG.get("HARD_MAX_RR_TP3", 12.0))

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
    """Clamp lot ke batas broker & hard cap."""
    if symbol_info is None:
        symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        return float(LOT_SIZE)
    broker_min = float(symbol_info.volume_min or 0.01)
    broker_max = float(symbol_info.volume_max or 100.0)
    broker_step = float(symbol_info.volume_step or 0.01)
    hard_cap = float(CONFIG.get("HARD_LOT_CAP", 0.06))
    eff_max = min(float(MAX_LOT_SIZE), hard_cap, broker_max)
    eff_min = max(float(MIN_LOT_SIZE), broker_min)
    lot = max(eff_min, min(eff_max, float(raw_lot)))
    if broker_step > 0:
        lot = round(lot / broker_step) * broker_step
    return round(lot, 8)


def calculate_lot_by_confluence(confluence_score, symbol_info=None):
    """Lot tier dari confluence score."""
    if confluence_score >= 90:
        lot = float(CONFIG.get("LOT_TIER_3", 0.06))
    elif confluence_score >= 80:
        lot = float(CONFIG.get("LOT_TIER_2", 0.03))
    elif confluence_score >= 70:
        lot = float(CONFIG.get("LOT_TIER_1", 0.01))
    else:
        lot = float(LOT_SIZE)
    return _clamp_lot(lot, symbol_info)


# ============================================================
# SECTION: GUARDS
# ============================================================
def check_margin_guard(lot, symbol_info=None):
    """Cek margin."""
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
        safety_pct = 30.0
        if usage_pct > safety_pct:
            return False, f"margin {usage_pct:.1f}% > {safety_pct:.0f}%"
        return True, f"margin {usage_pct:.1f}%"
    except Exception:
        return True, "skip err"


# ============================================================
# SECTION: RISK CALCULATOR
# ============================================================
def calculate_risk(model_result, entry, atr_raw, symbol_info, session_ok):
    """Hitung semua parameter risk."""
    result = {
        "ok": False, "reason": "", "sl": None, "sl_source": "",
        "tp_plan": None, "rr": 0.0, "lot": 0.0,
        "confluence": model_result.get("confluence", 0),
        "confluence_met": model_result.get("confluence_met", []),
    }

    direction = model_result["direction"]

    # 1. SL
    sl, sl_source = resolve_sl(
        entry, direction, atr_raw,
        swing_low=model_result.get("swing_low"),
        swing_high=model_result.get("swing_high"),
    )
    if sl is None:
        result["reason"] = "SL=0 skip"
        return result
    result["sl"] = sl
    result["sl_source"] = sl_source

    # 2. TP plan
    tp_plan = resolve_tp(entry, sl, direction)
    if tp_plan is None:
        result["reason"] = "TP=None skip"
        return result

    # 3. Validate RR
    tp_valid, rr, tp_plan = validate_tp(tp_plan, entry, sl, direction)
    if not tp_valid:
        if rr > float(CONFIG.get("HARD_MAX_RR_TP3", 12.0)):
            result["reason"] = f"RR too high 1:{rr:.1f}"
        else:
            result["reason"] = f"RR < min (actual {rr:.2f})"
        return result
    result["tp_plan"] = tp_plan
    result["rr"] = rr

    # 4. Update confluence dengan RR
    conf_score = result["confluence"]
    conf_met = result["confluence_met"]
    conf_score, conf_met = add_rr_score(conf_score, conf_met, rr)
    result["confluence"] = conf_score
    result["confluence_met"] = conf_met

    # 5. Cek threshold
    min_conf = float(CONFIG.get("MIN_CONFLUENCE", 70))
    if conf_score < min_conf:
        result["reason"] = f"conf {conf_score}% < {int(min_conf)}%"
        return result

    # 6. Lot
    lot = calculate_lot_by_confluence(conf_score, symbol_info)
    result["lot"] = lot

    # 7. Margin
    margin_ok, margin_reason = check_margin_guard(lot, symbol_info)
    if not margin_ok:
        result["reason"] = margin_reason
        return result

    result["ok"] = True
    return result


# ============================================================
# SECTION: PARTIAL CLOSE PLAN
# v6.3.2: PERCENT 33/33/34
# ============================================================
def _round_to_step(vol, step):
    """Bulatkan volume ke step broker (pakai round(), bukan floor)."""
    if step <= 0:
        return vol
    return round(vol / step) * step


def register_partial_plan(ticket, tp_plan, orig_volume, model_name, entry_price, direction):
    """
    Daftarkan rencana partial close.
    Mode PERCENT: 33% TP1, 33% TP2, sisa broker TP3.
    Mode LOT: TP1=tetap, TP2=tetap.
    """
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        return

    vol_min = float(symbol_info.volume_min or 0.01)
    vol_step = float(symbol_info.volume_step or 0.01)
    lot = float(orig_volume)

    # Cek lot minimal
    min_lot_for_partial = float(CONFIG.get("PARTIAL_MIN_LOT", 0.03))
    if lot < min_lot_for_partial:
        runtime_message(f"Partial #{ticket}: lot {lot} < min {min_lot_for_partial}, skip")
        return

    mode = str(CONFIG.get("PARTIAL_MODE", "PERCENT")).upper()

    # Hitung volume per TP
    if mode == "LOT":
        raw1 = float(CONFIG.get("PARTIAL_LOT_1", 0.01))
        raw2 = float(CONFIG.get("PARTIAL_LOT_2", 0.01))
    else:  # PERCENT
        pct1 = float(CONFIG.get("PARTIAL_PCT_1", 33))
        pct2 = float(CONFIG.get("PARTIAL_PCT_2", 33))
        raw1 = lot * (pct1 / 100.0)   # Contoh: 0.03 × 0.33 = 0.0099
        raw2 = lot * (pct2 / 100.0)   # Contoh: 0.06 × 0.33 = 0.0198

    v1 = _round_to_step(raw1, vol_step)   # 0.0099 → 0.01
    v2 = _round_to_step(raw2, vol_step)   # 0.0198 → 0.02

    tp1_en = v1 >= vol_min and v1 < lot
    tp2_en = v2 >= vol_min and v2 < lot

    # Pastikan total tidak melebihi lot
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
        "tp1": tp_plan["tp1"],
        "tp2": tp_plan["tp2"],
        "tp3": tp_plan["tp3"],
        "tp1_done": False,
        "tp2_done": False,
        "tp3_done": False,
        "tp1_enabled": tp1_en,
        "tp2_enabled": tp2_en,
        "vol1": v1,
        "vol2": v2,
        "orig_volume": lot,
        "model": model_name,
        "entry": entry_price,
        "direction": direction,
        "mode": mode,
    }
    persist_state()

    marks = []
    if tp1_en: marks.append(f"TP1({v1:g})")
    if tp2_en: marks.append(f"TP2({v2:g})")
    runtime_message(f"Partial #{ticket} lot {lot} [{mode}]: {'/'.join(marks)} (TP3=broker)")


# ============================================================
# SECTION: REBUILD (v6.3.2)
# Pulihkan POSITION_META & PARTIAL_STATE setelah restart
# ============================================================
def rebuild_position_meta():
    """Rebuild POSITION_META dari posisi terbuka (setelah restart)."""
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions:
            return
        for pos in positions:
            if pos.ticket in POSITION_META:
                continue

            # Parse model dari comment order
            comment = pos.comment or ""
            model_name = "UNKNOWN"
            c = comment.upper()
            if "CONTINUATION" in c:
                model_name = "CONTINUATION"
            elif "REVERSAL" in c:
                model_name = "REVERSAL"
            elif "SWEEP" in c:
                model_name = "SWEEP"
            elif pos.magic != int(CONFIG.get("MAGIC", 777777)):
                model_name = "MANUAL"
            else:
                model_name = "RECOVERED"

            # Perkiraan max_move dari SL
            max_move = 0.0
            if pos.sl and pos.sl > 0:
                if pos.type == 0 and pos.sl > pos.price_open:
                    max_move = pos.sl - pos.price_open
                elif pos.type == 1 and pos.sl < pos.price_open:
                    max_move = pos.price_open - pos.sl

            POSITION_META[pos.ticket] = {
                "model": model_name,
                "sl_source": "RECOVERED",
                "orig_volume": float(pos.volume),
                "max_move": max_move,
                "source": "position_meta_rebuild",
            }
            runtime_message(f"Recovered meta #{pos.ticket} ({model_name})")
        persist_state()
    except Exception:
        log_error(f"rebuild_position_meta: {traceback.format_exc()}")


def rebuild_partial_plans():
    """
    Rebuild PARTIAL_STATE dari posisi terbuka.
    v6.3.2: pakai RR (bukan 0.5/0.75) supaya konsisten dengan posisi baru.
    """
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions:
            return
        for pos in positions:
            if pos.ticket in PARTIAL_STATE:
                continue

            meta = POSITION_META.get(pos.ticket, {})
            model_name = meta.get("model", "")

            # Kalau model kosong, pakai RECOVERED
            if not model_name:
                model_name = "RECOVERED"
                POSITION_META[pos.ticket] = {
                    "model": model_name,
                    "sl_source": "RECOVERED",
                    "orig_volume": float(pos.volume),
                    "max_move": 0.0,
                }

            tp3 = pos.tp
            if not tp3 or tp3 <= 0:
                continue

            entry = float(pos.price_open)
            direction = "BUY" if pos.type == 0 else "SELL"
            sl = pos.sl if pos.sl and pos.sl > 0 else entry
            risk = abs(entry - sl)
            if risk <= 0:
                continue

            # v6.3.2 FIX: pakai RR, bukan dist × 0.5 / 0.75
            rr1 = float(CONFIG.get("TP_RR_TP1", 1.0))
            rr2 = float(CONFIG.get("TP_RR_TP2", 2.0))

            if direction == "BUY":
                tp1 = entry + risk * rr1
                tp2 = entry + risk * rr2
            else:
                tp1 = entry - risk * rr1
                tp2 = entry - risk * rr2

            register_partial_plan(
                pos.ticket,
                {"tp1": tp1, "tp2": tp2, "tp3": tp3},
                pos.volume, model_name,
                entry_price=entry, direction=direction
            )

            # Deteksi TP1/TP2 yang sudah done dari lot ratio
            orig_volume = float(meta.get("orig_volume", 0.0))
            current_volume = float(pos.volume)
            if orig_volume > 0 and current_volume < orig_volume:
                ratio = current_volume / orig_volume
                plan = PARTIAL_STATE.get(pos.ticket, {})
                if plan:
                    if ratio < 0.99:
                        plan["tp1_done"] = True
                    if ratio < 0.60:
                        plan["tp2_done"] = True
                    plan["orig_volume"] = orig_volume
                    persist_state()

            runtime_message(f"Rebuild #{pos.ticket} lot={pos.volume}")
    except Exception:
        log_error(f"rebuild_partial_plans: {traceback.format_exc()}")


# ============================================================
# SECTION: ORDER EXECUTION HELPERS
# ============================================================
def _get_supported_filling(symbol_info):
    """Filling mode yang didukung broker."""
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
    """Tutup sebagian posisi."""
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
                "deviation": 20,
                "magic": MAGIC,
                "comment": "PARTIAL_V6",
                "type_filling": filling,
                "type_time": mt5.ORDER_TIME_GTC,
            }
            res = mt5.order_send(req)
            if res is None:
                last_rc = "None"
                log_error(f"_close_partial #{position.ticket}: order_send None err={mt5.last_error()}")
                continue
            if res.retcode == mt5.TRADE_RETCODE_DONE:
                return True
            last_rc = res.retcode
            if res.retcode not in (mt5.TRADE_RETCODE_INVALID_FILL,):
                log_error(f"_close_partial #{position.ticket}: filling={filling} rc={res.retcode}")
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
    """Kelola partial close TP1/TP2."""
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions:
            PARTIAL_STATE.clear()
            persist_state()
            return
        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            return

        # Bersihkan plan untuk posisi closed
        active_tickets = {p.ticket for p in positions}
        for tk in list(PARTIAL_STATE.keys()):
            if tk not in active_tickets:
                PARTIAL_STATE.pop(tk, None)
        persist_state()
        if not PARTIAL_STATE:
            return

        for pos in positions:
            plan = PARTIAL_STATE.get(pos.ticket)
            if not plan:
                continue

            tick = mt5.symbol_info_tick(SYMBOL)
            if tick is None:
                continue
            current = tick.bid if pos.type == 0 else tick.ask

            # TP1
            if plan.get("tp1_enabled") and not plan.get("tp1_done"):
                hit = (pos.type == 0 and current >= plan["tp1"]) or \
                      (pos.type == 1 and current <= plan["tp1"])
                if hit:
                    vol = float(plan["vol1"])
                    if vol > 0 and _close_partial(pos, vol, symbol_info):
                        plan["tp1_done"] = True
                        persist_state()
                        runtime_message(f"TP1 hit #{pos.ticket} @ {plan['tp1']:.2f} vol {vol:g}")
                    continue

            # TP2
            if plan.get("tp1_done") and plan.get("tp2_enabled") and not plan.get("tp2_done"):
                hit = (pos.type == 0 and current >= plan["tp2"]) or \
                      (pos.type == 1 and current <= plan["tp2"])
                if hit:
                    vol = float(plan["vol2"])
                    if vol > 0 and _close_partial(pos, vol, symbol_info):
                        plan["tp2_done"] = True
                        persist_state()
                        runtime_message(f"TP2 hit #{pos.ticket} @ {plan['tp2']:.2f} vol {vol:g}")
                    continue

            # TP3: hanya set flag (broker tutup sisa)
            if plan.get("tp2_done") and not plan.get("tp3_done"):
                hit = (pos.type == 0 and current >= plan["tp3"]) or \
                      (pos.type == 1 and current <= plan["tp3"])
                if hit:
                    plan["tp3_done"] = True
                    persist_state()
                    runtime_message(f"TP3 hit #{pos.ticket} @ {plan['tp3']:.2f} (broker close)")

    except Exception:
        log_error(f"manage_partial_close: {traceback.format_exc()}")


# ============================================================
# SECTION: BREAK EVEN
# ============================================================
def manage_break_even():
    """BE aktif saat profit ≥ BE_TRIGGER_ATR × ATR."""
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        return
    symbol_info = mt5.symbol_info(SYMBOL)
    digits = symbol_info.digits if symbol_info else 2

    atr_now = get_atr_current()
    if atr_now is None or atr_now <= 0:
        return

    be_trigger = atr_now * float(CONFIG.get("BE_TRIGGER_ATR", 1.0))

    for pos in positions:
        meta = POSITION_META.get(pos.ticket, {})
        model_name = meta.get("model", "")
        if not model_name:
            continue

        # Skip kalau SL sudah di BE atau lebih
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
            new_sl = round(pos.price_open + 0.1, digits)
            old_sl = pos.sl if pos.sl and pos.sl > 0 else -1e9
            if new_sl > old_sl and new_sl < price:
                result = mt5.order_send({
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "sl": new_sl,
                    "tp": pos.tp,
                })
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    runtime_message(f"BE {model_name} BUY #{pos.ticket} SL→{new_sl}")
        else:
            new_sl = round(pos.price_open - 0.1, digits)
            old_sl = pos.sl if pos.sl and pos.sl > 0 else 1e9
            if new_sl < old_sl and new_sl > price:
                result = mt5.order_send({
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "sl": new_sl,
                    "tp": pos.tp,
                })
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    runtime_message(f"BE {model_name} SELL #{pos.ticket} SL→{new_sl}")


# ============================================================
# SECTION: TRAILING SL (max_move historis)
# ============================================================
def manage_trailing_sl():
    """Trailing aktif setelah profit ≥ TRAIL_TRIGGER_ATR × ATR."""
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

    trail_trigger = atr_now * float(CONFIG.get("TRAIL_TRIGGER_ATR", 2.0))
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

        # Track max_move historis
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
                result = mt5.order_send({
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
                result = mt5.order_send({
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
    """Hitung SL dari ATR."""
    if atr is None:
        atr = get_atr_current()
    if atr is None or atr <= 0:
        return 4.0
    sl = atr * float(SL_ATR_MULT)
    return max(4.0, min(20.0, sl))


def _recover_manual_position(pos, symbol_info, atr_raw, digits):
    """Hitung SL/TP untuk posisi manual."""
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
                        valid = (
                            (direction == "BUY" and fib_sl < entry and tp_price > entry) or
                            (direction == "SELL" and fib_sl > entry and tp_price < entry)
                        )
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
    """Pasang SL/TP untuk posisi manual."""
    if not CONFIG.get("USE_MANUAL_RECOVERY", True):
        return
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if not positions:
            return
        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            return
        digits = symbol_info.digits
        df_entry = get_closed_data(TIMEFRAME_ENTRY, bars=100)
        atr_raw = atr_value(df_entry)
        override = bool(MANUAL_PROFILE.get("OVERRIDE_EXISTING", False))

        for pos in positions:
            if pos.magic == int(CONFIG.get("MAGIC", 777777)):
                continue
            if pos.ticket in POSITION_META:
                continue
            if not override and (pos.sl != 0 or pos.tp != 0):
                continue

            ok, method, sl_price, tp_price = _recover_manual_position(
                pos, symbol_info, atr_raw, digits
            )
            if not ok:
                continue

            new_sl = sl_price if (override or pos.sl == 0) else pos.sl
            new_tp = tp_price if (override or pos.tp == 0) else pos.tp

            result = mt5.order_send({
                "action": mt5.TRADE_ACTION_SLTP,
                "position": pos.ticket,
                "sl": new_sl,
                "tp": new_tp,
            })
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                runtime_message(f"Manual #{pos.ticket} SL:{new_sl} TP:{new_tp} [{method}]")
                POSITION_META[pos.ticket] = {
                    "model": "MANUAL",
                    "sl_source": method,
                    "source": "manual_recovery",
                    "orig_volume": float(pos.volume),
                    "max_move": 0.0,
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
        return detect_choch(df_smc, SWING_STRICTNESS)
    except Exception:
        return None


def check_reentry_after_tp3(direction, current_price):
    """Cek re-entry setelah TP3 hit (retrace + CHoCH M15)."""
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
    """Return posisi aktif untuk model & arah tertentu."""
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
    """Cek apakah boleh re-entry."""
    positions = mt5.positions_get(symbol=SYMBOL)
    all_positions = positions if positions else []

    # Aturan 1: Max global
    max_global = int(CONFIG.get("MAX_OPEN_POSITIONS", 3))
    if max_global > 0 and len(all_positions) >= max_global:
        return False, f"max global ({max_global})"

    # Aturan 2: Max per model
    max_model_map = {
        "CONTINUATION": int(CONFIG.get("MAX_POSITIONS_CONTINUATION", 2)),
        "REVERSAL": int(CONFIG.get("MAX_POSITIONS_REVERSAL", 1)),
        "SWEEP": int(CONFIG.get("MAX_POSITIONS_SWEEP", 1)),
    }
    max_model = max_model_map.get(model_name, int(CONFIG.get("MAX_PER_MODEL", 2)))

    same_model = get_positions_by_model(model_name, direction)
    if len(same_model) >= max_model:
        return False, f"max {model_name} ({max_model})"

    if not same_model:
        return True, "ok (no same-direction)"

    # Aturan 3: Retrace setelah TP3
    tp3_hit_exists = any(
        PARTIAL_STATE.get(p.ticket, {}).get("tp3_done")
        for p in same_model
    )
    if tp3_hit_exists:
        ok, reason = check_reentry_after_tp3(direction, entry_price)
        if not ok:
            return False, reason

    # Aturan 4: Jarak minimum
    min_dist = atr_now * float(CONFIG.get("MIN_REENTRY_ATR", 2.0))
    avg_trigger_poin = atr_now * float(CONFIG.get("LOSS_REENTRY_ATR", 1.5))

    if direction == "SELL":
        highest_entry = max(float(p.price_open) for p in same_model)
        threshold = highest_entry + min_dist

        if entry_price <= threshold:
            price_move = entry_price - highest_entry
            if price_move < avg_trigger_poin:
                return False, f"SELL too close (need >= {threshold:.2f}, got {entry_price:.2f})"
            return True, f"ok (SELL averaging: move {price_move:+.2f})"
        return True, f"ok (SELL dist {entry_price - highest_entry:+.2f} >= {min_dist:.2f})"
    else:
        lowest_entry = min(float(p.price_open) for p in same_model)
        threshold = lowest_entry - min_dist

        if entry_price >= threshold:
            price_move = lowest_entry - entry_price
            if price_move < avg_trigger_poin:
                return False, f"BUY too close (need <= {threshold:.2f}, got {entry_price:.2f})"
            return True, f"ok (BUY averaging: move {price_move:+.2f})"
        return True, f"ok (BUY dist {lowest_entry - entry_price:+.2f} >= {min_dist:.2f})"


# ============================================================
# SECTION: OPEN TRADE
# ============================================================
def open_trade(model_result, risk_data, symbol_info=None):
    """Eksekusi order."""
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

        sl, sl_source = resolve_sl(
            entry, direction, atr_now,
            swing_low=model_result.get("swing_low"),
            swing_high=model_result.get("swing_high"),
        )
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

        lot = risk_data.get("lot", float(LOT_SIZE))

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
                "deviation": 20, "magic": MAGIC,
                "type_filling": filling, "type_time": mt5.ORDER_TIME_GTC,
                "comment": f"Wfx_{model_name}",
            }
            result = mt5.order_send(req)
            if result is None:
                last_rc = "None"
                continue
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                runtime_message(f"OK {model_name} {direction} @{entry} SL:{sl} TP:{tp3} Lot:{lot} RR1:{rr_est:.1f}")

                time.sleep(0.5)
                poss = mt5.positions_get(symbol=SYMBOL)
                if poss:
                    latest = max(poss, key=lambda p: p.time)
                    POSITION_META[latest.ticket] = {
                        "model": model_name,
                        "sl_source": sl_source,
                        "orig_volume": float(lot),
                        "max_move": 0.0,
                    }
                    register_partial_plan(
                        latest.ticket, tp_plan, lot, model_name,
                        entry_price=latest.price_open, direction=direction
                    )
                    persist_state()
                return True
            last_rc = result.retcode

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
    """Ambil history trade dari MT5."""
    if lookback_days is None:
        lookback_days = int(CONFIG.get("STATS_LOOKBACK_DAYS", 7))
    if magic is None:
        magic = int(MAGIC)
    try:
        date_from = datetime.now() - timedelta(days=lookback_days)
        date_to = datetime.now() + timedelta(days=1)
        deals = mt5.history_deals_get(date_from, date_to)
        if deals is None or len(deals) == 0:
            return []
        positions_map = {}
        for d in deals:
            if d.magic != magic:
                continue
            if d.symbol != SYMBOL:
                continue
            pid = d.position_id
            if pid not in positions_map:
                positions_map[pid] = {"profit": 0.0, "volume": 0.0,
                                      "time_open": d.time, "time_close": d.time,
                                      "comment": "", "direction": None}
            positions_map[pid]["profit"] += float(d.profit) + float(d.swap) + float(d.commission)
            if d.entry == 0:
                positions_map[pid]["volume"] = float(d.volume)
                positions_map[pid]["time_open"] = d.time
                positions_map[pid]["comment"] = d.comment
                positions_map[pid]["direction"] = "BUY" if d.type == 0 else "SELL"
            if d.entry == 1:
                positions_map[pid]["time_close"] = d.time
        result = []
        for pid, info in positions_map.items():
            if info["direction"] is None or info["volume"] == 0:
                continue
            model = _parse_model_from_comment(info["comment"])
            result.append({
                "ticket": pid, "model": model, "direction": info["direction"],
                "profit": info["profit"], "volume": info["volume"],
                "time_open": info["time_open"], "time_close": info["time_close"],
            })
        return result
    except Exception:
        log_error(f"fetch_history: {traceback.format_exc()}")
        return []


def compute_stats(trades):
    """Hitung statistik dari list trades."""
    stats = {"total": len(trades), "wins": 0, "losses": 0, "be": 0,
             "profit_total": 0.0, "profit_wins": 0.0, "profit_losses": 0.0,
             "winrate": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "profit_factor": 0.0}
    for t in trades:
        p = t["profit"]
        stats["profit_total"] += p
        if p > 0.01:
            stats["wins"] += 1            stats["profit_wins"] += p
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
    """Group stats by model."""
    by_model = {}
    for t in trades:
        m = t["model"]
        by_model.setdefault(m, []).append(t)
    return {m: compute_stats(ts) for m, ts in by_model.items()}


STATS_CACHE = {"trades": [], "global": {}, "per_model": {}, "last_refresh": 0}
STATS_REFRESH_INTERVAL = 30


def refresh_stats(force=False):
    """Refresh stats cache."""
    now = time.time()
    if not force and (now - STATS_CACHE["last_refresh"]) < STATS_REFRESH_INTERVAL:
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


best_model_global = {}


def render_stats_panel():
    """Panel STATS."""
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
    tbl.add_row("WinRate", Text(f"{g['winrate']:.1f}%  ({g['wins']}W / {g['losses']}L / {g['be']}BE)", style=wr_style))
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
    """Panel DIAGNOSTIC."""
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
    tbl.add_row("", Text("-" * 20, style="dim"))
    notes_txt = " | ".join(DIAG_STATE["notes"][-6:]) if DIAG_STATE["notes"] else "(all OK)"
    tbl.add_row("Notes", Text(notes_txt, style="yellow", overflow="fold"))
    for _ in range(2):
        tbl.add_row("", Text(""))
    return tbl


def render_model_scores_panel():
    """Panel MODEL SCORES."""
    tbl = Table.grid(expand=True, padding=(0, 1))
    tbl.add_column(style="cyan", no_wrap=True)
    tbl.add_column(ratio=1, justify="center")
    tbl.add_column(ratio=1, justify="center")
    tbl.add_column(ratio=1, justify="center")

    def _header_col(m):
        is_active = best_model_global.get("model") == m
        t = Text()
        t.append(m[:4], style="bold yellow" if is_active else "bold cyan")
        if is_active:
            t.append(" <", style="bold yellow")
        return t

    tbl.add_row("", _header_col("CONTINUATION"), _header_col("REVERSAL"), _header_col("SWEEP"))

    row_conf = [Text("Conf", style="dim")]
    row_rr = [Text("RR", style="dim")]
    row_dir = [Text("Dir", style="dim")]
    row_valid = [Text("Valid", style="dim")]
    row_reason = [Text("Reason", style="dim")]

    for m in ("CONTINUATION", "REVERSAL", "SWEEP"):
        s = MODEL_SCORES.get(m, {})

        conf = s.get("confluence", 0)
        if conf >= 90:
            conf_style = "bold green"
        elif conf >= 70:
            conf_style = "green"
        elif conf >= 50:
            conf_style = "yellow"
        else:
            conf_style = "dim"
        row_conf.append(Text(f"{conf}%", style=conf_style))

        rr = s.get("rr", 0.0)
        if rr > float(CONFIG.get("HARD_MAX_RR_TP3", 12.0)):
            rr_style = "red"
        elif rr >= 2.0:
            rr_style = "green"
        elif rr >= 1.2:
            rr_style = "cyan"
        else:
            rr_style = "dim"
        row_rr.append(Text(f"1:{rr:.1f}", style=rr_style))

        d = s.get("direction", "-") or "-"
        d_style = "green" if d == "BUY" else ("red" if d == "SELL" else "dim")
        row_dir.append(Text(d, style=d_style))

        valid = s.get("valid", False)
        row_valid.append(Text("Y" if valid else "N", style="green" if valid else "red"))

        reason = s.get("reason", "")[:25]
        row_reason.append(Text(reason, style="white", overflow="fold"))

    tbl.add_row(*row_conf)
    tbl.add_row(*row_rr)
    tbl.add_row(*row_dir)
    tbl.add_row(*row_valid)
    tbl.add_row(*row_reason)

    for m in ("CONTINUATION", "REVERSAL", "SWEEP"):
        s = MODEL_SCORES.get(m, {})
        if s.get("met"):
            tags = ", ".join(s["met"][:5])
            is_active = best_model_global.get("model") == m
            tbl.add_row(
                Text(f"{m[:4]} met", style="bold yellow" if is_active else "dim"),
                Text(tags, style="green", overflow="fold"), "", ""
            )
        else:
            tbl.add_row(Text(f"{m[:4]} met", style="dim"), Text("-", style="dim"), "", "")

    for _ in range(2):
        tbl.add_row(Text(""), Text(""), Text(""), Text(""))
    return tbl


def _hstack_panels(panels, ratios=None, spacing=0):
    """Gabungkan panel horizontal."""
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
    """Render dashboard."""
    global best_model_global
    best_model_global = best_model or {}

    now = datetime.now(WIB).strftime("%H:%M:%S WIB")
    trade_txt = Text("ON", style="bold green") if CONFIG.get("USE_AUTO_TRADE", True) else Text("OFF", style="bold red")
    session_txt = Text(current_session, style="bold green" if session_trade_allowed else "bold yellow")

    # ----- HEADER -----
    header = Table.grid(expand=True)
    header.add_column(ratio=1)
    header.add_column(justify="center", ratio=1)
    header.add_column(justify="right", ratio=1)
    title = Text("WEENfx PRO - v6.3.2", style="bold cyan")
    symbol = Text(SYMBOL, style="bold white")
    right = Text()
    right.append(now, style="white")
    right.append("  TRADE ", style="dim")
    right.append(trade_txt)
    header.add_row(title, symbol, right)
    header_panel = Panel(header, border_style="cyan", padding=(0, 1))

    # ----- PRICE BAR -----
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

    # ----- MARKET PANEL -----
    market = Table.grid(expand=True, padding=(0, 1))
    market.add_column(style="cyan", no_wrap=True, width=12)
    market.add_column(ratio=1)
    market.add_row("Bias", rich_direction(trend))
    market.add_row("HTF", rich_direction(htf_trend))
    market.add_row("ATR", Text(f"{atr_val:.2f}  {'OK' if atr_ok else 'LOW'}",
                               style="green" if atr_ok else "red"))
    market.add_row("Confluence", Text(f"Min {int(CONFIG.get('MIN_CONFLUENCE', 70))}%", style="cyan"))
    market.add_row("Session", session_txt)
    market.add_row("", Text(""))

    # ----- SIGNAL PANEL -----
    signal = Table.grid(expand=True, padding=(0, 1))
    signal.add_column(style="cyan", no_wrap=True, width=10)
    signal.add_column(ratio=1)

    if best_model:
        bm = best_model
        signal.add_row("BEST", Text(f"{bm['model']} {bm['direction']}", style="bold green"))
        signal.add_row("Conf", Text(f"{bm.get('confluence', 0)}%", style="bold green"))
        signal.add_row("Met", Text(", ".join(bm.get("confluence_met", [])[:4]),
                                    style="green", overflow="fold"))
        signal.add_row("RR", Text(f"1:{bm.get('rr', 0):.1f}", style="cyan"))
        signal.add_row("Entry", Text(f"{bm.get('entry', 0):.2f}", style="white"))
        signal.add_row("SL", Text(f"{bm.get('sl', 0):.2f}", style="red"))
        signal.add_row("Lot", Text(f"{bm.get('lot', 0):g}", style="white"))
    else:
        best_candidate = None
        best_conf = 0
        for name, s in MODEL_SCORES.items():
            if s.get("confluence", 0) > best_conf:
                best_conf = s.get("confluence", 0)
                best_candidate = (name, s)

        if best_candidate and best_conf > 0:
            name, s = best_candidate
            signal.add_row("NEAR", Text(f"{name[:4]} {s.get('direction','-')}", style="yellow"))
            signal.add_row("Conf", Text(f"{s.get('confluence',0)}% (need {int(CONFIG.get('MIN_CONFLUENCE',70))}%)",
                                        style="yellow"))
            signal.add_row("Reason", Text(s.get("reason", "")[:30],
                                          style="dim", overflow="fold"))
            signal.add_row("RR", Text(f"1:{s.get('rr', 0):.1f}", style="cyan"))
            signal.add_row("", Text(""))
            signal.add_row("", Text(""))
            signal.add_row("", Text(""))
        else:
            signal.add_row("STATUS", Text("WAITING MODEL", style="yellow"))
            for _ in range(6):
                signal.add_row("", Text(""))

    # ----- DIAGNOSTIC + SCORES -----
    try:
        diag_panel = Panel(render_diagnostic_panel(), title="DIAGNOSTIC",
                           border_style="yellow", expand=True)
    except Exception as e:
        diag_panel = Panel(Text(f"diag err: {e}", style="red"), border_style="red")

    try:
        scores_panel = Panel(render_model_scores_panel(),
                             title=f"MODEL SCORES  [Min Conf {int(CONFIG.get('MIN_CONFLUENCE',70))}%]",
                             border_style="cyan", expand=True)
    except Exception:
        scores_panel = Panel(Text("scores err", style="red"), border_style="red")

    # ----- POSITIONS TABLE -----
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
            if pos.magic != MAGIC and model_tag == "?":
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

    # ----- RISK PANEL -----
    risk = Table.grid(expand=True, padding=(0, 1))
    risk.add_column(style="cyan", no_wrap=True, width=14)
    risk.add_column(ratio=1)
    risk.add_row("AutoTrade", rich_status(CONFIG.get("USE_AUTO_TRADE", True)))
    risk.add_row("Sizing", Text("Confluence", style="cyan"))
    risk.add_row("SL", Text(f"Fib / ATR×{CONFIG.get('SL_ATR_MULT', 1.5)}", style="cyan"))
    risk.add_row("TP RR", Text(f"1:{CONFIG.get('TP_RR_TP1',1.0)}/1:{CONFIG.get('TP_RR_TP2',2.0)}/1:{CONFIG.get('TP_RR_TP3',3.0)}"))
    risk.add_row("BE", Text(f"ATR×{CONFIG.get('BE_TRIGGER_ATR',1.0)}", style="cyan"))
    risk.add_row("Trail", Text(f"ATR×{CONFIG.get('TRAIL_TRIGGER_ATR',2.0)} s{CONFIG.get('TRAIL_SECURE_PCT',50)}%"))
    risk.add_row("Partial", Text(f"{CONFIG.get('PARTIAL_MODE', 'PERCENT')} "
                                  f"{CONFIG.get('PARTIAL_PCT_1', 33)}/{CONFIG.get('PARTIAL_PCT_2', 33)}",
                                  style="magenta"))
    risk.add_row("Daily", Text(f"${daily_pnl:.2f} / {daily_loss_percent:.2f}%"))
    risk.add_row("Manual Rec", Text("ON" if CONFIG.get("USE_MANUAL_RECOVERY", True) else "OFF",
                                    style="green" if CONFIG.get("USE_MANUAL_RECOVERY", True) else "dim"))
    risk.add_row("FakeBrk", Text("FAKE!" if fakeout else "clear",
                                  style="red" if fakeout else "green"))

    # ----- ACCOUNT PANEL -----
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

    # ----- SESSION PANEL -----
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

    # ----- SUSUN LAYOUT -----
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
        Panel(pos_group, title=f"POSITIONS  {len(positions) if positions else 0}/{maxpos}",
              border_style="white", padding=(0, 1)),
        row_risk_account,
        row_session_stats,
        status_panel,
    ]
    parts.extend(event_parts)
    return Group(*parts)


# ============================================================
# SECTION: DIAGNOSTIC STATE
# ============================================================
DIAG_STATE = {
    "swing_buy": False, "swing_sell": False,
    "demand_zones": 0, "supply_zones": 0,
    "htf_trend": "SIDEWAYS", "choch": None, "rej_wick": None,
    "sweep_buy": False, "sweep_sell": False,
    "notes": [],
}

MODEL_SCORES = {
    "CONTINUATION": {"confluence": 0, "rr": 0.0, "direction": "-", "valid": False, "reason": "", "met": []},
    "REVERSAL": {"confluence": 0, "rr": 0.0, "direction": "-", "valid": False, "reason": "", "met": []},
    "SWEEP": {"confluence": 0, "rr": 0.0, "direction": "-", "valid": False, "reason": "", "met": []},
}


# ============================================================
# SECTION: STARTUP
# ============================================================
print("=" * 60)
print("Starting v6.3.2 ...")
print(f"   Symbol: {SYMBOL}")
print(f"   Entry TF: {TIMEFRAME_ENTRY}")
print(f"   Auto Trade: {'ON' if CONFIG.get('USE_AUTO_TRADE', True) else 'OFF'}")
print(f"   Model: CONT={CONFIG.get('USE_MODEL_CONTINUATION', True)} "
      f"REV={CONFIG.get('USE_MODEL_REVERSAL', False)} "
      f"SWP={CONFIG.get('USE_MODEL_SWEEP', False)}")
print(f"   Max: Global={CONFIG.get('MAX_OPEN_POSITIONS', 2)} "
      f"CONT={CONFIG.get('MAX_POSITIONS_CONTINUATION', 2)} "
      f"REV={CONFIG.get('MAX_POSITIONS_REVERSAL', 1)} "
      f"SWP={CONFIG.get('MAX_POSITIONS_SWEEP', 1)}")
print(f"   SL: Fib / ATR x {CONFIG.get('SL_ATR_MULT', 1.5)}")
print(f"   TP RR: 1:{CONFIG.get('TP_RR_TP1',1.0)} / 1:{CONFIG.get('TP_RR_TP2',2.0)} / 1:{CONFIG.get('TP_RR_TP3',3.0)}")
print(f"   BE: ATR x {CONFIG.get('BE_TRIGGER_ATR',1.0)}")
print(f"   Trailing: ATR x {CONFIG.get('TRAIL_TRIGGER_ATR',2.0)} sec {CONFIG.get('TRAIL_SECURE_PCT',50)}%")
print(f"   Min Confluence: {int(CONFIG.get('MIN_CONFLUENCE',70))}%")
print(f"   Partial: {CONFIG.get('PARTIAL_MODE', 'PERCENT')} "
      f"({CONFIG.get('PARTIAL_PCT_1', 33)}/{CONFIG.get('PARTIAL_PCT_2', 33)}), "
      f"min lot {CONFIG.get('PARTIAL_MIN_LOT', 0.03)}")
print(f"   Manual Recovery: {'ON' if CONFIG.get('USE_MANUAL_RECOVERY', True) else 'OFF'}")
print(f"   Retrace After TP3: {CONFIG.get('RETRACE_MIN_PERCENT', 20.0)}% + CHoCH M15")
print("=" * 60)

time.sleep(2)
console.clear()


# ============================================================
# SECTION: MAIN LOOP
# ============================================================
last_candle_time = get_last_closed_candle_time(TIMEFRAME_ENTRY)
active_model = "-"
best_model = None
last_smc_update = time.time()
last_manual_recovery = time.time()
demand_zones = []
supply_zones = []

refresh_stats(force=True)

with Live(console=console, refresh_per_second=4, screen=True, transient=False,
          vertical_overflow="visible") as live:

    # ----- STARTUP: rebuild meta → partial → manual recovery -----
    try:
        df_smc = get_closed_data(TIMEFRAME_SMC, bars=500)
        if df_smc is not None and not df_smc.empty:
            demand_zones = detect_demand_zones(df_smc, CONFIG.get("SMC_ZONE_SENSITIVITY", 0.10))
            supply_zones = detect_supply_zones(df_smc, CONFIG.get("SMC_ZONE_SENSITIVITY", 0.10))

        # 1. Rebuild POSITION_META dulu
        try:
            rebuild_position_meta()
        except Exception as e:
            runtime_message(f"Rebuild meta: {e}")

        # 2. Rebuild PARTIAL_STATE (butuh POSITION_META)
        try:
            rebuild_partial_plans()
        except Exception as e:
            runtime_message(f"Rebuild partial: {e}")

        # 3. Manual recovery
        if CONFIG.get("USE_MANUAL_RECOVERY", True):
            try:
                recover_manual_entries()
            except Exception as e:
                runtime_message(f"Startup manual recovery: {e}")
    except Exception as e:
        runtime_message(f"Startup: {e}")

    # ----- MAIN LOOP -----
    while True:
        try:
            current_time = time.time()

            if not mt5.account_info():
                runtime_message("Reconnecting MT5...")
                mt5.initialize()
                time.sleep(3)
                continue

            df = get_closed_data(TIMEFRAME_ENTRY)
            if df is None or df.empty:
                runtime_message("Waiting data...")
                time.sleep(2)
                continue

            bid, ask = get_live_price()

            new_candle = is_new_candle_mt5(TIMEFRAME_ENTRY)
            session_ok = in_session()

            # Update SMC zones tiap 60 detik
            if (current_time - last_smc_update > 60):
                df_smc = get_closed_data(TIMEFRAME_SMC, bars=500)
                if df_smc is not None and not df_smc.empty:
                    demand_zones = detect_demand_zones(df_smc, CONFIG.get("SMC_ZONE_SENSITIVITY", 0.10))
                    supply_zones = detect_supply_zones(df_smc, CONFIG.get("SMC_ZONE_SENSITIVITY", 0.10))
                last_smc_update = current_time

            refresh_stats()

            # Manual recovery tiap 30 detik
            if CONFIG.get("USE_MANUAL_RECOVERY", True):
                interval = float(MANUAL_PROFILE.get("CHECK_INTERVAL", 30))
                if current_time - last_manual_recovery > interval:
                    recover_manual_entries()
                    last_manual_recovery = current_time

            # Bersihkan POSITION_META untuk posisi closed
            current_positions = mt5.positions_get(symbol=SYMBOL)
            active_tickets = {p.ticket for p in current_positions} if current_positions else set()
            for tk in list(POSITION_META.keys()):
                if tk not in active_tickets:
                    POSITION_META.pop(tk, None)
            persist_state()

            # ----- ANALISIS -----
            trend = trend_m5()
            htf_trend = get_higher_timeframe_trend()

            atr_raw = atr_value(df)
            atr_val = round(atr_raw, 2) if atr_raw is not None else 0.0
            atr_ok = atr_raw is not None and atr_raw >= float(CONFIG.get("MIN_ATR_VALUE", 0.8))

            choch = detect_choch(df, CONFIG.get("SWING_STRICTNESS", 1))
            wick = detect_rejection_wick(df)
            sweep_buy = smart_liquidity_sweep(df, "BUY", atr_raw=atr_raw)
            sweep_sell = smart_liquidity_sweep(df, "SELL", atr_raw=atr_raw)

            daily_pnl, daily_loss_percent = check_daily_loss()

            DIAG_STATE["swing_buy"] = find_last_swing_for_fib(df, "BUY")[0] is not None
            DIAG_STATE["swing_sell"] = find_last_swing_for_fib(df, "SELL")[0] is not None
            DIAG_STATE["demand_zones"] = len(demand_zones)
            DIAG_STATE["supply_zones"] = len(supply_zones)
            DIAG_STATE["htf_trend"] = htf_trend
            DIAG_STATE["choch"] = choch
            DIAG_STATE["rej_wick"] = wick
            DIAG_STATE["sweep_buy"] = sweep_buy
            DIAG_STATE["sweep_sell"] = sweep_sell
            DIAG_STATE["notes"] = []

            # ----- MODEL EVALUATION -----
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

            for k in MODEL_SCORES:
                MODEL_SCORES[k] = {"confluence": 0, "rr": 0.0, "direction": "-",
                                   "valid": False, "reason": "", "met": []}

            model_results = evaluate_all_models(ctx, session_ok)

            # Catat reason untuk model yang gagal
            if CONFIG.get("USE_MODEL_CONTINUATION", True):
                r = ContinuationModel(ctx).evaluate()
                if not r["passed"]:
                    DIAG_STATE["notes"].append(f"C={r['reason']}")
            if CONFIG.get("USE_MODEL_REVERSAL", False):
                r = ReversalModel(ctx).evaluate()
                if not r["passed"]:
                    DIAG_STATE["notes"].append(f"R={r['reason']}")
            if CONFIG.get("USE_MODEL_SWEEP", False):
                r = SweepModel(ctx).evaluate()
                if not r["passed"]:
                    DIAG_STATE["notes"].append(f"S={r['reason']}")

            # ----- RISK CALCULATION -----
            tick = mt5.symbol_info_tick(SYMBOL)
            symbol_info = mt5.symbol_info(SYMBOL)
            entry_preview = tick.ask if tick else 0

            risk_candidates = []
            for mr in model_results:
                direction = mr["direction"]
                entry = tick.ask if direction == "BUY" else tick.bid if tick else 0
                risk_data = calculate_risk(mr, entry, atr_raw, symbol_info, session_ok)

                MODEL_SCORES[mr["model"]] = {
                    "confluence": risk_data["confluence"],
                    "rr": risk_data["rr"],
                    "direction": direction,
                    "valid": risk_data["ok"],
                    "reason": risk_data["reason"] if not risk_data["ok"] else "OK",
                    "met": risk_data["confluence_met"],
                }

                if risk_data["ok"]:
                    combined = dict(mr)
                    combined["entry"] = entry
                    combined["sl"] = risk_data["sl"]
                    combined["lot"] = risk_data["lot"]
                    combined["rr"] = risk_data["rr"]
                    combined["confluence"] = risk_data["confluence"]
                    combined["confluence_met"] = risk_data["confluence_met"]
                    combined["risk_data"] = risk_data
                    risk_candidates.append(combined)

            # ----- PILIH BEST MODEL -----
            best_model = None
            best_risk = None
            if risk_candidates:
                best_model = max(risk_candidates, key=lambda x: x["confluence"])
                best_risk = best_model.get("risk_data")

            # ----- FILTER -----
            if best_model:
                if CONFIG.get("USE_ATR_FILTER", True) and not atr_ok:
                    best_model = None
                    best_risk = None
                elif CONFIG.get("USE_SESSION_FILTER", True) and not session_ok:
                    best_model = None
                    best_risk = None
                elif fake_breakout_filter(df) and best_model["model"] == "CONTINUATION":
                    best_model = None
                    best_risk = None

            # ----- EXECUTE TRADE -----
            if best_model and best_risk:
                if not trading_disabled_today and CONFIG.get("USE_AUTO_TRADE", True) and session_ok:
                    atr_now = atr_raw if atr_raw else 3.0
                    can, reason = can_reentry(best_model["model"], best_model["direction"], entry_preview, atr_now)
                    if can:
                        runtime_message(f"EXEC {best_model['model']} {best_model['direction']} conf={best_risk['confluence']}%")
                        open_trade(best_model, best_risk, symbol_info)
                    else:
                        runtime_message(f"Skip entry — {reason}")

            # ----- TRADE MANAGEMENT -----
            manage_partial_close()
            manage_break_even()
            manage_trailing_sl()

            # ----- RENDER DASHBOARD -----
            account = mt5.account_info()
            positions = mt5.positions_get(symbol=SYMBOL)
            current_session, _, session_trade_allowed = get_session_status_text()

            live.update(render_rich_dashboard(
                account=account, positions=positions, bid=bid, ask=ask,
                price_direction="=",
                current_session=current_session,
                session_trade_allowed=session_trade_allowed,
                trend=trend, htf_trend=htf_trend,
                atr_val=atr_val, atr_ok=atr_ok,
                best_model=best_model,
                fakeout=fake_breakout_filter(df),
                daily_pnl=daily_pnl,
                daily_loss_percent=daily_loss_percent,
                trading_disabled_today=trading_disabled_today,
            ))

            time.sleep(1)

        except KeyboardInterrupt:
            break
        except Exception as e:
            log_error(f"main loop: {traceback.format_exc()}")
            runtime_message(f"ERROR: {e}")
            time.sleep(3)


# ============================================================
# END OF FILE — v6.3.2
# ============================================================
