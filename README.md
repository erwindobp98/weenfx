# xauusd only windows
# Wfx PRO — SMC + Fibonacci EA v6.3.1

Expert Advisor untuk MetaTrader 5 (XAUUSD) dengan strategi **Smart Money Concepts (SMC)** + **Fibonacci**. Menggunakan 3 model entry:
- **CONTINUATION** — follow trend
- **REVERSAL** — tangkap pembalikan
- **SWEEP** — tangkap sweep likuiditas

## Fitur

- ✅ 3 model entry (CONTINUATION, REVERSAL, SWEEP)
- ✅ Deteksi SMC: Demand/Supply zone, CHoCH, Order Block, FVG
- ✅ Fibonacci entry zone (OTE) + Fib SL
- ✅ Partial close (TP1/TP2) + broker TP3
- ✅ Break Even ATR-based
- ✅ Trailing SL (max_move historis, tidak mundur)
- ✅ Anti re-entry 3 lapis (max positions, jarak, retrace after TP3)
- ✅ Manual recovery (posisi manual otomatis di-SL/TP)
- ✅ Dashboard rich (live, multi-panel)
- ✅ Stats 30 hari (winrate, PF, per model)

## Requirements

- Python 3.8+
- MetaTrader 5 (Windows)
- Library:
  ```bash
  pip install MetaTrader5 pandas numpy pytz colorama rich
  ```

## Instalasi

1. Clone repo:
   ```bash
   git clone https://github.com/erwindobp98/xauusd.git
   cd xauusd
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `config.example.json` → `config.json`:
   ```bash
   cp config.example.json config.json
   ```

4. Edit `config.json`:
   - `SYMBOL` → sesuaikan broker (contoh: `XAUUSD.vxc`, `XAUUSD`, `GOLD`)
   - `MAX_LOT_SIZE` → sesuaikan balance
   - `MIN_CONFLUENCE` → 70 (default)

5. Jalankan:
   ```bash
   python xauusd.py
   ```

## Struktur File

```
weenfx-v631/
├── xauusd.py          # Script utama
├── config.example.json     # Contoh config
├── requirements.txt        # Dependencies
├── README.md               # Dokumentasi ini
├── .gitignore              # Exclude state, log
└── LICENSE                 # MIT (opsional)
```

Runtime files (tidak di-commit):
- `config.json` — config user
- `state.json` — state runtime (POSITION_META, PARTIAL_STATE)
- `error.log` — log error

## Cara Kerja

### Alur Utama

```
START
  ↓
Load config + state
  ↓
Connect MT5
  ↓
Rebuild POSITION_META & PARTIAL_STATE (posisi lama)
  ↓
LOOP setiap 1 detik:
  ├─ Analisis: trend, ATR, CHoCH, wick, sweep
  ├─ Evaluasi 3 model (CONT, REV, SWP)
  ├─ Hitung confluence score (0-100%)
  ├─ Pilih best model (confluence ≥ 70%)
  ├─ Cek can_reentry (max pos, jarak, TP3 retrace)
  ├─ Execute trade (kalau lolos filter)
  ├─ Manage partial/BE/trailing
  └─ Render dashboard
```

### 5 Gate Model

Setiap model harus lolos 5 gate:

1. **Gate HTF** — trend H1 harus BULLISH/BEARISH (CONT) atau opsional (REV/SWP)
2. **Gate Zone** — harga harus di zona SMC (demand/supply)
3. **Gate Confirmation** — sinyal konfirmasi (CHoCH/wick/sweep)
4. **Gate Swing** — swing valid ≥ MIN_SWING_SIZE
5. **Gate Fib** — harga di zona fib (flag atau gate)

### Confluence Score

Skor 0-100% dari:
- HTF align: 20
- POI zone: 20
- CHoCH: 15
- Wick: 10
- Fib OTE: 15
- Session: 10
- RR ≥ 2.0: 10

Model harus punya skor ≥ `MIN_CONFLUENCE` (default 70%) untuk entry.

### TP & Partial

- **TP1** = entry ± risk × 1.0 → partial close `PARTIAL_LOT_1`
- **TP2** = entry ± risk × 2.0 → partial close `PARTIAL_LOT_2`
- **TP3** = entry ± risk × 3.0 → broker TP tutup sisa

Partial aktif hanya kalau lot ≥ `PARTIAL_MIN_LOT` (default 0.03).

## Konfigurasi Penting

| Key | Default | Penjelasan |
|-----|---------|-----------|
| `SYMBOL` | `XAUUSD.vxc` | Symbol trading |
| `TIMEFRAME_ENTRY` | `M5` | TF entry |
| `TIMEFRAME_HTF` | `H1` | TF trend besar |
| `MAX_OPEN_POSITIONS` | 6 | Max posisi global |
| `MAX_POSITIONS_CONTINUATION` | 2 | Max per model |
| `MIN_CONFLUENCE` | 70 | Skor minimal entry |
| `TP_RR_TP1/2/3` | 1.0/2.0/3.0 | RR TP1/2/3 |
| `MIN_REENTRY_ATR` | 1.5 | Jarak minimum re-entry |
| `USE_AUTO_TRADE` | true | Auto execute |
| `PARTIAL_MODE` | `LOT` | LOT / PERCENT |

Lihat `config.example.json` untuk semua key.

## Peringatan

- ⚠️ **Gunakan demo dulu** minimal 2 minggu sebelum live.
- ⚠️ **Backtest** tidak menjamin hasil live.
- ⚠️ **Spread XAUUSD** bisa melebar saat news — sesuaikan `MAX_SPREAD_POINTS` kalau perlu.
- ⚠️ **Tidak ada jaminan profit** — trading berisiko.

## Changelog

### v6.3.1
- Fix: rebuild POSITION_META untuk posisi lama saat restart
- Fix: rebuild partial plans jangan skip kalau model kosong
- Fix: startup urutan (meta → partial → manual recovery)

### v6.3
- Gabungkan arsitektur v6.2 + model entry v5.4
- Model entry: CONTINUATION (1/4), REVERSAL (4 jalur), SWEEP (sweep+wick)
- TP RR-based (bukan Fib extension)

### v6.2
- Class-based model
- 5 gate seragam
- Confluence score
- Fix gate_confirmation
- MAX_POSITIONS per model

## Lisensi

MIT — bebas dipakai, modifikasi, distribusi.

## Kontribusi

Pull request welcome. Untuk bug report, buat issue dengan:
- Log error (dari `error.log`)
- Screenshot dashboard
- Versi Python & MT5

## Disclaimer

Software ini disediakan "as is", tanpa jaminan apapun. Penggunaan sepenuhnya risiko Anda sendiri. Penulis tidak bertanggung jawab atas kerugian trading.
