"""Reads bot state files written by the live Aquora bots.

Handles the two on-disk shapes ("grid" and "positions") and always degrades
gracefully: a missing or unreadable file returns a status object with
available=False instead of raising, so one dead bot never breaks the report.
"""

import json
import os

from dashboard.fleet_config import FLEET


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "no state file"
    except (json.JSONDecodeError, OSError) as e:
        return None, f"unreadable: {e}"


def _open_positions_from_positions_shape(data):
    """positions shape -> list of open positions."""
    open_pos = []
    for symbol, p in (data.get("positions") or {}).items():
        if p.get("open"):
            open_pos.append({
                "symbol": symbol,
                "side": p.get("side", "?"),
                "entry": p.get("entryPrice", 0),
                "qty": p.get("qty", 0),
                "stop": p.get("stopPrice", 0),
                "booked_pnl": p.get("bookedPnl", 0),
            })
    return open_pos


def _open_positions_from_grid_shape(data):
    """grid shape -> each coin with inventory rungs is an 'open' holding."""
    open_pos = []
    for coin, c in (data.get("coins") or {}).items():
        inv = c.get("inv") or []
        if inv:
            qty = sum(u.get("qty", 0) for u in inv)
            avg = (
                sum(u.get("buy", 0) * u.get("qty", 0) for u in inv) / qty
                if qty else 0
            )
            open_pos.append({
                "symbol": coin,
                "side": "long",
                "entry": round(avg, 6),
                "qty": round(qty, 6),
                "stop": 0,
                "booked_pnl": 0,
                "rungs": len(inv),
            })
    return open_pos


def _detect_shape(data, hint):
    """Auto-detect the state-file shape from its keys; hint is a fallback."""
    if isinstance(data, dict):
        if "coins" in data:
            return "grid"
        if "positions" in data:
            return "positions"
    return hint


def read_bot_state(bot, fleet_root):
    """Return a status dict for one bot from its state file."""
    status = {
        "n": bot["n"],
        "name": bot["name"],
        "exchange": bot["exchange"],
        "market": bot["market"],
        "strategy": bot["strategy"],
        "paper": bot.get("paper", False),
        "available": False,
        "note": "",
        "open_positions": [],
        "last_run": None,
        "day_pnl": None,
        "realized_pnl": None,
        "wins": None,
        "losses": None,
        "total_closed": None,
    }

    if not bot.get("state"):
        status["note"] = "no state file (exchange-only)"
        return status

    path = os.path.join(fleet_root, bot["state"])
    data, err = _read_json(path)
    if err:
        status["note"] = err
        return status

    status["available"] = True
    shape = _detect_shape(data, bot.get("shape"))

    if shape == "grid":
        status["open_positions"] = _open_positions_from_grid_shape(data)
    elif shape == "positions":
        status["open_positions"] = _open_positions_from_positions_shape(data)
    else:
        status["note"] = "unknown state shape"

    # Both shapes carry a top-level "stats" block with cumulative figures;
    # grid additionally tracks its own dayPnl.
    stats = data.get("stats") or {}
    status["realized_pnl"] = stats.get("realizedPnl")
    status["day_pnl"] = stats.get("dayPnl")  # None for bots that don't track it
    status["wins"] = stats.get("wins")
    status["losses"] = stats.get("losses")
    # full closed round-trips (partials are handled within a trade, not counted
    # here); grid bots track sells instead of totalClosed.
    status["total_closed"] = stats.get("totalClosed")
    if status["total_closed"] is None:
        status["total_closed"] = stats.get("sells")
    status["last_run"] = data.get("lastRun")

    return status


def read_all_states(fleet_root):
    return [read_bot_state(bot, fleet_root) for bot in FLEET]
