"""Per-bot daily activity: today's net P&L, trades, wins, losses.

Bots expose cumulative counters in stats (realizedPnl, totalClosed, wins,
losses). To get today's figures the dashboard snapshots those counters at the
first UTC-day run and reports the delta since. Only fully-closed trades move
these counters (partial exits are handled within a trade), so wins/losses are
counted only when a trade completes.

If a bot reports its own dayPnl (grid), that value is used for net directly.

The snapshot is a small JSON file (gitignored). For the figures to cover a
full day, the dashboard should run regularly (cron) so the baseline is taken
near the day boundary.
"""

import json
import os
from datetime import datetime, timezone

SNAPSHOT_NAME = "dashboard_daily_snapshot.json"

# cumulative metrics tracked per bot for daily deltas
_METRICS = ("realized_pnl", "total_closed", "wins", "losses")


def _today_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _save(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
    except OSError:
        pass


def _metrics_now(bot_states):
    """Current cumulative metrics per bot, keyed by str(n)."""
    out = {}
    for bs in bot_states:
        m = {k: bs.get(k) for k in _METRICS if bs.get(k) is not None}
        if m:
            out[str(bs["n"])] = m
    return out


def compute_daily(bot_states, fleet_root=None, snapshot_path=None):
    """Return {bot_n: {net, trades, wins, losses}} for today.

    Any figure that can't be derived is None.
    """
    if snapshot_path is None:
        snapshot_path = os.path.join(fleet_root or ".", SNAPSHOT_NAME)

    today = _today_utc()
    current = _metrics_now(bot_states)

    snap = _load(snapshot_path)
    # valid = today's snapshot in the new per-metric dict format
    valid = (
        isinstance(snap, dict)
        and snap.get("date") == today
        and isinstance(snap.get("baseline"), dict)
        and all(isinstance(v, dict) for v in snap["baseline"].values())
    )
    if not valid:
        # no/stale/old-format snapshot -> start today's baseline fresh
        snap = {"date": today, "baseline": current}
        _save(snapshot_path, snap)
    else:
        changed = False
        for k, v in current.items():
            if k not in snap["baseline"]:
                snap["baseline"][k] = v
                changed = True
        if changed:
            _save(snapshot_path, snap)

    baseline = snap.get("baseline", {})

    def delta(key, metric):
        base = baseline.get(key)
        if not isinstance(base, dict):
            return None
        cur = current.get(key, {}).get(metric)
        bv = base.get(metric)
        if cur is None or bv is None:
            return None
        return round(cur - bv, 4) if metric == "realized_pnl" else int(cur - bv)

    result = {}
    for bs in bot_states:
        n = bs["n"]
        key = str(n)
        # net: prefer the bot's own dayPnl (grid), else realizedPnl delta
        if bs.get("day_pnl") is not None:
            net = round(bs["day_pnl"], 4)
        else:
            net = delta(key, "realized_pnl")
        result[n] = {
            "net": net,
            "trades": delta(key, "total_closed"),
            "wins": delta(key, "wins"),
            "losses": delta(key, "losses"),
        }
    return result


def compute_today(bot_states, fleet, fleet_root=None, snapshot_path=None):
    """Per-bot today figures, preferring trades.csv detail over stats deltas.

    Returns {bot_n: {net, trades, wins, losses, partials, events}}. `events`
    is the per-trade list from trades.csv (None if only stats were available).
    """
    from dashboard.trades_log import parse_today_trades, summarize_trades

    stats_daily = compute_daily(bot_states, fleet_root, snapshot_path)
    by_n = {b["n"]: b for b in fleet}

    result = {}
    for bs in bot_states:
        n = bs["n"]
        base = dict(stats_daily.get(n) or {})
        base.setdefault("partials", None)
        base.setdefault("events", None)
        events = parse_today_trades(by_n.get(n, {}), fleet_root)
        if events is not None:
            base.update(summarize_trades(events))  # trades.csv wins over stats
        result[n] = base
    return result


def fleet_today_summary(bot_states, daily, exclude_paper=True):
    """Aggregate today's activity across the LIVE fleet (paper bots excluded).

    Returns trades, wins, losses, gross profit (sum of winning bots' net),
    gross loss (sum of losing bots' net), and net.
    """
    trades = wins = losses = 0
    profit = loss = 0.0
    for bs in bot_states:
        if exclude_paper and bs.get("paper"):
            continue
        d = daily.get(bs["n"]) or {}
        if d.get("trades"):
            trades += d["trades"]
        if d.get("wins"):
            wins += d["wins"]
        if d.get("losses"):
            losses += d["losses"]
        net = d.get("net")
        if net:
            if net > 0:
                profit += net
            else:
                loss += net
    return {
        "trades": trades, "wins": wins, "losses": losses,
        "profit": round(profit, 2), "loss": round(loss, 2),
        "net": round(profit + loss, 2),
    }
