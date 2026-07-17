"""Read-only exchange balance + open-position lookups via ccxt.

Uses ONLY read endpoints (fetch_balance / fetch_positions). No orders are
ever placed, modified, or cancelled here.

Credential sources, in priority order:
  1. Dashboard's own env vars  ({EX}_API_KEY / {EX}_SECRET_KEY / ...)
     -> use these if you set dedicated READ-ONLY keys in the dashboard .env.
  2. The live bots' own .env files under FLEET_ROOT/<bot-dir>/.env
     -> zero extra setup; reuses keys already on the VPS. Enabled unless
        REUSE_BOT_KEYS=off. NOTE: these are the bots' trade-enabled keys, but
        this tool only ever calls read endpoints.

Per-exchange var names differ (BingX/KuCoin use *_API_SECRET, others
*_SECRET_KEY), so the mapping is explicit below.
"""

import os

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

# exchange id -> ccxt class name
_CCXT_CLASS = {
    "binance": "binance",
    "bybit":   "bybit",
    "bitget":  "bitget",
    "okx":     "okx",
    "bingx":   "bingx",
    "kucoin":  "kucoin",
}

# Which bot's .env holds usable keys for each exchange, and the exact var
# names in that file. "password" = passphrase (ccxt's field name).
_BOT_KEY_SOURCE = {
    "binance": {"dir": "bot2", "key": "BINANCE_API_KEY", "secret": "BINANCE_SECRET_KEY"},
    "bybit":   {"dir": "bot3", "key": "BYBIT_API_KEY",   "secret": "BYBIT_SECRET_KEY"},
    "bitget":  {"dir": "bot6", "key": "BITGET_API_KEY",  "secret": "BITGET_SECRET_KEY",
                "password": "BITGET_PASSPHRASE"},
    "okx":     {"dir": "bot7", "key": "OKX_API_KEY",     "secret": "OKX_SECRET_KEY",
                "password": "OKX_PASSPHRASE"},
    "bingx":   {"dir": "bot8", "key": "BINGX_API_KEY",   "secret": "BINGX_API_SECRET"},
    "kucoin":  {"dir": "bot9", "key": "KUCOIN_API_KEY",  "secret": "KUCOIN_API_SECRET",
                "password": "KUCOIN_PASSPHRASE"},
}


def _reuse_enabled():
    return os.getenv("REUSE_BOT_KEYS", "on").strip().lower() in ("1", "true", "on", "yes")


def _parse_env_file(path):
    """Minimal KEY=VALUE parser for a bot .env file."""
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def _creds_from_dashboard_env(exchange):
    up = exchange.upper()
    key = os.getenv(f"{up}_API_KEY")
    secret = os.getenv(f"{up}_SECRET_KEY")
    if not key or not secret:
        return None
    creds = {"apiKey": key, "secret": secret, "enableRateLimit": True}
    passphrase = os.getenv(f"{up}_PASSPHRASE")
    if passphrase:
        creds["password"] = passphrase
    return creds


def _creds_from_bot_env(exchange, fleet_root):
    src = _BOT_KEY_SOURCE.get(exchange)
    if not src or not fleet_root:
        return None
    env_path = os.path.join(fleet_root, src["dir"], ".env")
    env = _parse_env_file(env_path)
    key = env.get(src["key"])
    secret = env.get(src["secret"])
    if not key or not secret:
        return None
    creds = {"apiKey": key, "secret": secret, "enableRateLimit": True}
    if "password" in src and env.get(src["password"]):
        creds["password"] = env[src["password"]]
    return creds


def _creds(exchange, fleet_root):
    creds = _creds_from_dashboard_env(exchange)
    if creds:
        return creds, "dashboard .env"
    if _reuse_enabled():
        creds = _creds_from_bot_env(exchange, fleet_root)
        if creds:
            return creds, "bot .env"
    return None, None


def read_exchange(exchange, fleet_root=None):
    """Return {available, note, usdt, open_positions, source} for one exchange."""
    out = {"exchange": exchange, "available": False, "note": "",
           "usdt": None, "open_positions": [], "source": None}

    if not CCXT_AVAILABLE:
        out["note"] = "ccxt not installed"
        return out
    if exchange not in _CCXT_CLASS:
        out["note"] = "unsupported exchange"
        return out

    creds, source = _creds(exchange, fleet_root)
    if creds is None:
        out["note"] = "no keys found"
        return out
    out["source"] = source

    try:
        client = getattr(ccxt, _CCXT_CLASS[exchange])(creds)
        balance = client.fetch_balance()
        usdt = balance.get("total", {}).get("USDT")
        out["usdt"] = round(usdt, 2) if usdt is not None else None

        if client.has.get("fetchPositions"):
            try:
                for p in client.fetch_positions() or []:
                    contracts = p.get("contracts") or 0
                    if contracts and float(contracts) != 0:
                        out["open_positions"].append({
                            "symbol": p.get("symbol"),
                            "side": p.get("side"),
                            "contracts": contracts,
                            "entry": p.get("entryPrice"),
                            "upnl": p.get("unrealizedPnl"),
                        })
            except Exception as e:
                out["note"] = f"positions n/a: {str(e)[:40]}"

        out["available"] = True
    except Exception as e:
        out["note"] = f"error: {str(e)[:60]}"

    return out


def read_all_exchanges(exchanges, fleet_root=None):
    return {ex: read_exchange(ex, fleet_root) for ex in exchanges}
