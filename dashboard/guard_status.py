"""Fleet-wide guard status.

Reports the configured state of the three guards (Market Guard, Event Guard,
Kill-Switch). Guard flags are read from the dashboard's own env first, then
fall back to a representative bot's .env under FLEET_ROOT — so the status
reflects the live fleet without any extra setup. Read-only: it never arms,
resets, or changes any guard.
"""

import json
import os

# Bot whose .env is read as the representative fleet guard config.
_GUARD_SOURCE_DIR = "bot2"


def _truthy(v):
    return str(v).strip().lower() in ("1", "true", "on", "yes")


def _parse_env_file(path):
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


def _flag(name, bot_env, default=False):
    val = os.getenv(name)
    if val is not None:
        return _truthy(val)
    if name in bot_env:
        return _truthy(bot_env[name])
    return default


def read_guard_status(fleet_root=None):
    bot_env = {}
    if fleet_root:
        bot_env = _parse_env_file(
            os.path.join(fleet_root, _GUARD_SOURCE_DIR, ".env")
        )

    status = {
        "market_guard": _flag("MARKET_GUARD", bot_env),
        "event_guard": _flag("EVENT_GUARD", bot_env),
        "kill_switch_configured": True,
        "kill_switch_active": None,
        "kill_note": "",
    }

    # Optional live kill-switch state file (written by the live fleet).
    ks_path = os.getenv("KILL_SWITCH_STATE")
    if not ks_path and fleet_root:
        for candidate in ("kill_switch.json", "bot_healthstate.json"):
            p = os.path.join(fleet_root, candidate)
            if os.path.exists(p):
                ks_path = p
                break

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
