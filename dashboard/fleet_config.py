"""Static definition of the live Aquora fleet.

This mirrors Aquora_Fleet_Reference.docx. The dashboard reads this to know
which bots exist, which exchange/market each runs on, and where to find its
state file. Nothing here is a secret — API keys stay in .env.
"""

# Each bot: number, name, exchange, market, strategy, timeframe,
# state file key (basename under STATE_DIR, or None if no state file),
# and the "state shape" the reader should expect.
#   shape "grid"      -> {coins: {SYM: {inv, nextBuy}}, stats: {...}}
#   shape "positions" -> {positions: {SYMBOL: {open, side, entryPrice, ...}}}
#   shape None        -> no local state file (read from exchange only)
FLEET = [
    {"n": 1,  "name": "Grid Range-Scalper",   "exchange": "bitget", "market": "spot",
     "strategy": "Grid (1H)",            "state": "bot1_grid_state.json", "shape": "grid",
     "never_paused": False, "guard": "grid"},
    {"n": 2,  "name": "Trend-Pullback v2",    "exchange": "binance", "market": "spot",
     "strategy": "Trend-Pullback (4H)",  "state": "bot2_position.json",  "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 3,  "name": "EMA-Pullback",         "exchange": "bybit",  "market": "spot",
     "strategy": "EMA-Pullback (15m)",   "state": "bot3_position.json",  "shape": "positions",
     "never_paused": False, "guard": "trend", "retire": True},
    {"n": 4,  "name": "Trend Long+Short",     "exchange": "bybit",  "market": "futures",
     "strategy": "Trend L/S (1H)",       "state": "bot4_live_pos.json",  "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 5,  "name": "RSI Reversion v2",     "exchange": "binance", "market": "futures",
     "strategy": "RSI Reversion (4H)",   "state": "bot5_position.json",  "shape": "positions",
     "never_paused": False, "guard": "meanrev"},
    {"n": 6,  "name": "Donchian Breakout",    "exchange": "bitget", "market": "futures",
     "strategy": "Donchian 1D long",     "state": "bot6_position.json",  "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 7,  "name": "DCA Capitulation",     "exchange": "okx",    "market": "spot",
     "strategy": "DCA Ladder ETH (4H)",  "state": "bot7_position.json",  "shape": "positions",
     "never_paused": True,  "guard": None},
    {"n": 8,  "name": "Darvas Box v2",        "exchange": "bingx",  "market": "futures",
     "strategy": "Darvas Box (4H)",      "state": "bot8_position.json",  "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 9,  "name": "Wyckoff Spring",       "exchange": "kucoin", "market": "spot",
     "strategy": "Wyckoff Spring (4H)",  "state": "bot9_position.json",  "shape": "positions",
     "never_paused": True,  "guard": None},
    {"n": 10, "name": "Supertrend v2",        "exchange": "okx",    "market": "futures",
     "strategy": "Supertrend (1H)",      "state": "bot10_position.json", "shape": "positions",
     "never_paused": False, "guard": "trend"},
    {"n": 11, "name": "Donchian Breakout",    "exchange": "binance", "market": "spot",
     "strategy": "Donchian 1D",          "state": "bot11_position.json", "shape": "positions",
     "never_paused": False, "guard": "trend"},
]

# Exchanges the fleet spans (used to group balance lookups).
EXCHANGES = ["binance", "bybit", "bitget", "okx", "bingx", "kucoin"]


def bots_on(exchange):
    return [b for b in FLEET if b["exchange"] == exchange]
