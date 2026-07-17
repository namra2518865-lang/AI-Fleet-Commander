"""Read-only exchange balance + open-position lookups via ccxt.

Uses ONLY read endpoints (fetch_balance / fetch_positions). No orders are
ever placed here. Keys come from environment variables and must be
read-only keys. If ccxt is not installed or an exchange has no keys
configured, that exchange is skipped and the dashboard falls back to
state-file data only.

Env var names per exchange (set the read-only key/secret):
    BINANCE_API_KEY / BINANCE_SECRET_KEY
    BYBIT_API_KEY   / BYBIT_SECRET_KEY
    BITGET_API_KEY  / BITGET_SECRET_KEY / BITGET_PASSPHRASE
    OKX_API_KEY     / OKX_SECRET_KEY    / OKX_PASSPHRASE
    BINGX_API_KEY   / BINGX_SECRET_KEY
    KUCOIN_API_KEY  / KUCOIN_SECRET_KEY / KUCOIN_PASSPHRASE
"""

import os

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

# exchange id -> (ccxt class name, extra credential env suffixes)
_EXCHANGE_MAP = {
    "binance": ("binance", []),
    "bybit":   ("bybit", []),
    "bitget":  ("bitget", ["PASSPHRASE"]),
    "okx":     ("okx", ["PASSPHRASE"]),
    "bingx":   ("bingx", []),
    "kucoin":  ("kucoin", ["PASSPHRASE"]),
}


def _creds(exchange):
    up = exchange.upper()
    key = os.getenv(f"{up}_API_KEY")
    secret = os.getenv(f"{up}_SECRET_KEY")
    if not key or not secret:
        return None
    creds = {"apiKey": key, "secret": secret, "enableRateLimit": True}
    _, extras = _EXCHANGE_MAP[exchange]
    for extra in extras:
        val = os.getenv(f"{up}_{extra}")
        if val:
            creds["password"] = val  # ccxt uses "password" for passphrase
    return creds


def read_exchange(exchange):
    """Return {available, note, usdt, open_positions} for one exchange."""
    out = {"exchange": exchange, "available": False, "note": "",
           "usdt": None, "open_positions": []}

    if not CCXT_AVAILABLE:
        out["note"] = "ccxt not installed"
        return out
    if exchange not in _EXCHANGE_MAP:
        out["note"] = "unsupported exchange"
        return out

    creds = _creds(exchange)
    if creds is None:
        out["note"] = "no read-only keys set"
        return out

    cls_name, _ = _EXCHANGE_MAP[exchange]
    try:
        client = getattr(ccxt, cls_name)(creds)
        balance = client.fetch_balance()
        usdt = balance.get("total", {}).get("USDT")
        out["usdt"] = round(usdt, 2) if usdt is not None else None

        # positions only exist on derivatives-capable accounts
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
            except Exception as e:  # positions optional; balance already got
                out["note"] = f"positions n/a: {str(e)[:40]}"

        out["available"] = True
    except Exception as e:
        out["note"] = f"error: {str(e)[:60]}"

    return out


def read_all_exchanges(exchanges):
    return {ex: read_exchange(ex) for ex in exchanges}
