"""Fleet-wide guard status.

Reports the configured state of the three guards (Market Guard, Event Guard,
Kill-Switch) from environment flags, plus the live kill-switch state if a
state file is provided. This is a read-only summary — it does not arm, reset,
or change any guard.
"""

import json
import os


def _flag(name, default="off"):
    return os.getenv(name, default).strip().lower() in ("1", "true", "on", "yes")


def read_guard_status(state_dir=None):
    status = {
        "market_guard": _flag("MARKET_GUARD"),
        "event_guard": _flag("EVENT_GUARD"),
        "kill_switch_configured": True,
        "kill_switch_active": None,
        "kill_note": "",
    }

    # Optional live kill-switch state file (written by the live fleet).
    ks_path = os.getenv("KILL_SWITCH_STATE")
    if not ks_path and state_dir:
        candidate = os.path.join(state_dir, "kill_switch.json")
        if os.path.exists(candidate):
            ks_path = candidate

    if ks_path and os.path.exists(ks_path):
        try:
            with open(ks_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            status["kill_switch_active"] = bool(
                data.get("active") or data.get("frozen")
            )
        except (json.JSONDecodeError, OSError) as e:
            status["kill_note"] = f"unreadable: {e}"
    else:
        status["kill_note"] = "no live state file"

    return status
