# Aquora Fleet Commander — Dashboard

A **read-only** terminal dashboard for the live Aquora trading fleet. It does
**not** trade, place, modify, or cancel any order — it only reads state and
reports it.

## What it shows

- Every bot's live status: flat / in-trade (with symbols) / state-file missing
- Realized PnL per bot (from state files)
- Live USDT balance + open positions per exchange (read-only API)
- Guard status: Market Guard, Event Guard, Kill-Switch

## Data sources (both combined)

1. **Bot state files** — the `position.json` each bot writes under
   `FLEET_ROOT/<bot-dir>/` (VPS: `/root/bot/`, `/root/bot2/` … `/root/bot11/`).
   Works offline. The grid-vs-positions shape is auto-detected.
2. **Exchange read-only API** (via `ccxt`) — live balances/positions for the
   6 venues (Binance, Bybit, BitGet, OKX, BingX, KuCoin).

Either source degrading (missing file, missing keys, ccxt absent) never breaks
the report — that row just shows a note.

## Setup

```bash
pip install -r requirements.txt      # ccxt, rich, python-dotenv
cp .env.example .env                 # then edit .env
```

In `.env` set:
- `FLEET_ROOT` — dir holding each bot's folder + `/newsradar` (VPS: `/root`)
- **read-only** exchange API keys (leave blank to skip a venue)

> Use keys with **read-only / view** permission only. The tool never trades,
> but read-only keys mean a leaked key still can't move funds.

## Run

```bash
py -m dashboard.commander                 # full report (state files + exchanges)
py -m dashboard.commander --no-exchange    # offline: state files only
py -m dashboard.commander --root /root     # override FLEET_ROOT
```

On the VPS use `python3` instead of `py`.

## Files

| File | Role |
|---|---|
| `fleet_config.py`  | Static 11-bot fleet map (bot -> exchange/market/strategy/state file) |
| `state_reader.py`  | Reads bot `position.json` (auto-detects grid/positions shape), degrades gracefully |
| `exchange_reader.py` | ccxt read-only balance + positions per exchange |
| `guard_status.py`  | Market/Event/Kill-Switch status |
| `report.py`        | Renders the terminal report (rich, plain-text fallback) |
| `commander.py`     | Entry point (`py -m dashboard.commander`) |
