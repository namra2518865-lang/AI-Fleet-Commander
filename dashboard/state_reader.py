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


def read_bot_state(bot, state_dir):
    """Return a status dict for one bot from its state file."""
    status = {
        "n": bot["n"],
        "name": bot["name"],
        "exchange": bot["exchange"],
        "market": bot["market"],
        "strategy": bot["strategy"],
        "available": False,
        "note": "",
        "open_positions": [],
        "last_run": None,
        "day_pnl": None,
        "realized_pnl": None,
    }

    if not bot.get("state"):
        status["note"] = "no state file (exchange-only)"
        return status

    path = os.path.join(state_dir, bot["state"])
    data, err = _read_json(path)
    if err:
        status["note"] = err
        return status

    status["available"] = True

    if bot["shape"] == "grid":
        status["open_positions"] = _open_positions_from_grid_shape(data)
        stats = data.get("stats") or {}
        status["day_pnl"] = stats.get("dayPnl")
        status["realized_pnl"] = stats.get("realizedPnl")
        status["last_run"] = data.get("lastRun")
    elif bot["shape"] == "positions":
        status["open_positions"] = _open_positions_from_positions_shape(data)
        # sum booked pnl across symbols as a rough realized figure
        total = 0
        for p in (data.get("positions") or {}).values():
            total += p.get("bookedPnl", 0) or 0
        status["realized_pnl"] = round(total, 4)
        status["last_run"] = data.get("lastRun")

    return status


def read_all_states(state_dir):
    return [read_bot_state(bot, state_dir) for bot in FLEET]
