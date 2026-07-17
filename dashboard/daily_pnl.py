"""Per-bot daily P&L.

Bots expose a cumulative `stats.realizedPnl`, but only the grid bot tracks
its own `dayPnl`. To get a daily figure for every bot uniformly, the
dashboard snapshots each bot's cumulative realized P&L at the first run of
each (UTC) day and reports:  daily = current_cumulative - start_of_day.

If a bot reports its own `day_pnl` (grid), that authoritative value is used
directly instead of the snapshot diff.

The snapshot is a small JSON file; nothing here is a secret. For the daily
number to capture a full day, the dashboard should run regularly (cron) so
the baseline is taken near the day boundary.
"""

import json
import os
from datetime import datetime, timezone

SNAPSHOT_NAME = "dashboard_daily_snapshot.json"


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


def compute_daily_pnl(bot_states, fleet_root=None, snapshot_path=None):
    """Return {bot_n: daily_pnl_or_None}. Updates the snapshot file."""
    if snapshot_path is None:
        base_dir = fleet_root or "."
        snapshot_path = os.path.join(base_dir, SNAPSHOT_NAME)

    today = _today_utc()
    # current cumulative realized P&L per bot (only where known)
    current = {
        str(bs["n"]): bs["realized_pnl"]
        for bs in bot_states
        if bs.get("realized_pnl") is not None
    }

    snap = _load(snapshot_path)
    if not snap or snap.get("date") != today:
        # first run of the day (or no snapshot yet): reset the baseline
        snap = {"date": today, "baseline": current}
        _save(snapshot_path, snap)
    else:
        # new bots that appeared mid-day get a baseline now
        changed = False
        for k, v in current.items():
            if k not in snap["baseline"]:
                snap["baseline"][k] = v
                changed = True
        if changed:
            _save(snapshot_path, snap)

    baseline = snap.get("baseline", {})
    daily = {}
    for bs in bot_states:
        n = bs["n"]
        key = str(n)
        if bs.get("day_pnl") is not None:
            # bot tracks its own daily figure (authoritative)
            daily[n] = round(bs["day_pnl"], 4)
        elif key in current and key in baseline and baseline[key] is not None:
            daily[n] = round(current[key] - baseline[key], 4)
        else:
            daily[n] = None
    return daily
