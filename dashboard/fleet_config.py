"""Static definition of the live Aquora fleet.

This mirrors Aquora_Fleet_Reference.docx and the real VPS layout. The
dashboard reads this to know which bots exist, which exchange/market each runs
on, and where to find its state file. Nothing here is a secret — API keys stay
in .env.

VPS layout: each bot lives in its own dir under FLEET_ROOT (default /root):
    /root/bot/position.json     (bot 1 — no number)
    /root/bot2/position.json ... /root/bot11/position.json
So each bot's "state" below is a path RELATIVE to FLEET_ROOT.

State-file shape is auto-detected by the reader (grid vs positions); the
"shape" field here is only a fallback hint.
"""

# n, name, exchange, market, strategy, state (relative to FLEET_ROOT),
# shape hint, never_paused, guard bucket.
FLEET = [
    {"n": 1,  "name": "Grid Range-Scalper",   "exchange": "bitget", "market": "spot",
     "strategy": "Grid (1H)",            "state": "bot/position.json",    "shape": "grid",
     "never_paused": False, "guard": "grid"},
    {"n": 2,  "name": "Trend-Pullback v2",    "exchange": "binance", "market": "spot",
     "strategy": "Trend-Pullback (4H)",  "state": "bot2/position.json",   "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 3,  "name": "EMA-Pullback",         "exchange": "bybit",  "market": "spot",
     "strategy": "EMA-Pullback (15m)",   "state": "bot3/position.json",   "shape": "positions",
     "never_paused": False, "guard": "trend", "retire": True},
    {"n": 4,  "name": "Trend Long+Short",     "exchange": "bybit",  "market": "futures",
     "strategy": "Trend L/S (1H)",       "state": "bot4/position.json",   "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 5,  "name": "RSI Reversion v2",     "exchange": "binance", "market": "futures",
     "strategy": "RSI Reversion (4H)",   "state": "bot5/position.json",   "shape": "positions",
     "never_paused": False, "guard": "meanrev"},
    {"n": 6,  "name": "Donchian Breakout",    "exchange": "bitget", "market": "futures",
     "strategy": "Donchian 1D long",     "state": "bot6/position.json",   "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 7,  "name": "DCA Capitulation",     "exchange": "okx",    "market": "spot",
     "strategy": "DCA Ladder ETH (4H)",  "state": "bot7/position.json",   "shape": "positions",
     "never_paused": True,  "guard": None},
    {"n": 8,  "name": "Darvas Box v2",        "exchange": "bingx",  "market": "futures",
     "strategy": "Darvas Box (4H)",      "state": "bot8/position.json",   "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 9,  "name": "Wyckoff Spring",       "exchange": "kucoin", "market": "spot",
     "strategy": "Wyckoff Spring (4H)",  "state": "bot9/position.json",   "shape": "positions",
     "never_paused": True,  "guard": None},
    {"n": 10, "name": "Supertrend v2",        "exchange": "okx",    "market": "futures",
     "strategy": "Supertrend (1H)",      "state": "bot10/position.json",  "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 11, "name": "Donchian Breakout",    "exchange": "binance", "market": "spot",
     "strategy": "Donchian 1D",          "state": "bot11/position.json",  "shape": "positions",
     "never_paused": False, "guard": "trend"},
]

# Extra fleet-level state files (relative to FLEET_ROOT).
HEALTH_STATE = "bot_healthstate.json"
NEWSRADAR_STATE = "newsradar/state.json"

# Exchanges the fleet spans (used to group balance lookups).
EXCHANGES = ["binance", "bybit", "bitget", "okx", "bingx", "kucoin"]


def bots_on(exchange):
    return [b for b in FLEET if b["exchange"] == exchange]
