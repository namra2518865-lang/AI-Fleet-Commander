"""Parse each bot's trades.csv to list today's realized trades with P&L.

Two on-disk formats exist across the fleet; rows are detected individually
(a file may even mix them after a bot upgrade):

STANDARD (Node bot.js fleet):
    Date,Time (UTC),Exchange,Symbol,Side,Quantity,Price,Total USD,Fee,
    Net Amount,Order ID,Mode,Notes
  - col0 = YYYY-MM-DD (no 'T')
  - full close: Side=SELL/BUY and Notes contain "P&L ... ($X)"
  - partial:    Side=PARTIAL or Notes contain "booked $X"

COMPACT (grid + newer bots: bot1/5/8/10):
    time,action,symbol,side,price,qty,notional,pnl,reason
  - col0 = ISO timestamp (has 'T')
  - full close: action=SELL/BUY/CLOSE with a non-empty pnl column
  - partial:    action=PARTIAL
  - entries (BUY with empty pnl) are skipped

Rows without a realized P&L (HOLD / entry / unrealized) are skipped.
"""

import csv
import os
import re
from datetime import datetime, timezone

_PNL_RE = re.compile(r"P&L[^(]*\(\$?(-?[\d,]+\.?\d*)\)", re.I)
_BOOKED_RE = re.compile(r"booked\s*\$?(-?[\d,]+\.?\d*)", re.I)
_DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _today_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _num(s):
    if s is None:
        return None
    s = str(s).replace(",", "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_standard_row(row):
    """Return {symbol, side, pnl, partial} or None."""
    if len(row) < 5:
        return None
    side = (row[4] or "").strip().upper()
    notes = row[-1] or ""
    symbol = row[3] if len(row) > 3 else ""
    netcol = _num(row[9]) if len(row) > 9 else None
    m_pnl = _PNL_RE.search(notes)
    if m_pnl:
        pnl = _num(m_pnl.group(1))
        return {"symbol": symbol, "side": side,
                "pnl": pnl if pnl is not None else netcol, "partial": False}
    if side == "PARTIAL" or _BOOKED_RE.search(notes):
        m_b = _BOOKED_RE.search(notes)
        return {"symbol": symbol, "side": side,
                "pnl": _num(m_b.group(1)) if m_b else netcol, "partial": True}
    return None


def _parse_compact_row(row):
    """time,action,symbol,side,price,qty,notional,pnl,reason -> event or None."""
    if len(row) < 8:
        return None
    action = (row[1] or "").strip().upper()
    symbol = row[2] if len(row) > 2 else ""
    pnl = _num(row[7])
    if action == "PARTIAL":
        return {"symbol": symbol, "side": action, "pnl": pnl, "partial": True}
    if pnl is not None:  # SELL/BUY/CLOSE with a realized pnl
        return {"symbol": symbol, "side": action, "pnl": pnl, "partial": False}
    return None  # entry (empty pnl) / noise


def parse_today_trades(bot, fleet_root, today=None):
    """Return today's realized events for one bot, or None if no trades.csv."""
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
            for row in csv.reader(f):
                if not row:
                    continue
                col0 = row[0].strip()
                if not col0.startswith(today):
                    continue
                # per-row format detection
                if "T" in col0:                       # ISO timestamp -> compact
                    ev = _parse_compact_row(row)
                elif _DATE_ONLY_RE.match(col0):        # YYYY-MM-DD -> standard
                    ev = _parse_standard_row(row)
                else:
                    ev = None
                if ev is not None:
                    events.append(ev)
    except OSError:
        return None
    return events


def summarize_trades(events, partials_as_trades=False):
    """Reduce today's events to per-bot figures.

    partials_as_trades=True (grid bot): partial closes count as trades and
    toward win/loss. Otherwise partials are shown/added to net but not counted.
    """
    def is_counted(e):
        return e["pnl"] is not None and (not e["partial"] or partials_as_trades)

    counted = [e for e in events if is_counted(e)]
    uncounted_partials = [
        e for e in events
        if e["partial"] and e["pnl"] is not None and not partials_as_trades
    ]
    wins = sum(1 for e in counted if e["pnl"] > 0)
    losses = sum(1 for e in counted if e["pnl"] <= 0)
    net = round(sum(e["pnl"] for e in events if e["pnl"] is not None), 4)
    return {
        "trades": len(counted),
        "wins": wins,
        "losses": losses,
        "partials": len(uncounted_partials),
        "net": net,
        "events": events,
    }
