"""Parse each bot's trades.csv to list today's realized trades with P&L.

Standard format (used by the Node bot.js fleet, incl. the grid bot):
    Date,Time (UTC),Exchange,Symbol,Side,Quantity,Price,Total USD,Fee,
    Net Amount,Order ID,Mode,Notes

Row types:
  - Full close: Side = SELL/BUY, Notes contain "P&L ... ($X)"  -> realized P&L
  - Partial:    Side = PARTIAL,  Notes contain "booked $X"     -> partial book
  - HOLD / BUY-entry: skipped (no realized P&L)

Bots whose trades.csv is missing or in a different schema (e.g. bot5) return
None, and the caller falls back to the stats-snapshot daily figures.
"""

import csv
import os
import re
from datetime import datetime, timezone

_STANDARD_HEADER = "Date,Time"
_PNL_RE = re.compile(r"P&L[^(]*\(\$?(-?[\d,]+\.?\d*)\)", re.I)
_BOOKED_RE = re.compile(r"booked\s*\$?(-?[\d,]+\.?\d*)", re.I)


def _today_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _num(s):
    try:
        return float(str(s).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def parse_today_trades(bot, fleet_root, today=None):
    """Return today's realized events for one bot, or None if unparseable.

    Each event: {symbol, side, pnl, partial}.
    """
    state = bot.get("state") or ""
    bdir = os.path.dirname(state)
    if not bdir or not fleet_root:
        return None
    path = os.path.join(fleet_root, bdir, "trades.csv")
    if not os.path.exists(path):
        return None

    today = today or _today_utc()
    events = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            first = f.readline()
            if not first.startswith(_STANDARD_HEADER):
                return None  # non-standard schema -> caller falls back
            for row in csv.reader(f):
                if not row or not row[0].startswith(today):
                    continue
                if len(row) < 5:
                    continue
                side = (row[4] or "").strip().upper()
                notes = row[-1] or ""
                symbol = row[3] if len(row) > 3 else ""
                netcol = _num(row[9]) if len(row) > 9 else None

                m_pnl = _PNL_RE.search(notes)
                if m_pnl:  # full realized close
                    pnl = _num(m_pnl.group(1))
                    events.append({"symbol": symbol, "side": side,
                                   "pnl": pnl if pnl is not None else netcol,
                                   "partial": False})
                elif side == "PARTIAL" or _BOOKED_RE.search(notes):
                    m_b = _BOOKED_RE.search(notes)
                    pnl = _num(m_b.group(1)) if m_b else netcol
                    events.append({"symbol": symbol, "side": side,
                                   "pnl": pnl, "partial": True})
                # else: HOLD / entry / unrealized -> skip
    except OSError:
        return None
    return events


def summarize_trades(events):
    """Reduce a list of today's events to per-bot figures."""
    full = [e for e in events if not e["partial"] and e["pnl"] is not None]
    partials = [e for e in events if e["partial"] and e["pnl"] is not None]
    wins = sum(1 for e in full if e["pnl"] > 0)
    losses = sum(1 for e in full if e["pnl"] <= 0)
    net = round(sum(e["pnl"] for e in (full + partials)), 4)
    return {
        "trades": len(full),
        "wins": wins,
        "losses": losses,
        "partials": len(partials),
        "net": net,
        "events": events,
    }
