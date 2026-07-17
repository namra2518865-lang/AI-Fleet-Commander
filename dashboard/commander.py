"""Aquora Fleet Commander — read-only terminal dashboard.

Combines two data sources into one fleet report:
  1. Bot state files  (STATE_DIR)   -> per-bot status, open positions
  2. Exchange read-only API (ccxt)  -> live USDT balance, open positions

Run:
    py -m dashboard.commander
    py -m dashboard.commander --no-exchange   # state files only (offline)

Config via environment / .env (see .env.example). This tool never places,
modifies, or cancels any order — it only reads.
"""

import argparse
import os
import sys

from dashboard.exchange_reader import read_all_exchanges
from dashboard.fleet_config import EXCHANGES
from dashboard.guard_status import read_guard_status
from dashboard.report import build_report
from dashboard.state_reader import read_all_states


def _load_dotenv():
    """Load .env from repo root if python-dotenv is present (optional)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


def main(argv=None):
    parser = argparse.ArgumentParser(description="Aquora Fleet Commander (read-only)")
    parser.add_argument("--no-exchange", action="store_true",
                        help="skip live exchange lookups; use state files only")
    parser.add_argument("--state-dir", default=None,
                        help="override STATE_DIR (where bot *.json state files live)")
    args = parser.parse_args(argv)

    _load_dotenv()

    state_dir = args.state_dir or os.getenv("STATE_DIR", ".")
    if not os.path.isdir(state_dir):
        print(f"[warn] STATE_DIR not found: {state_dir} "
              f"(set STATE_DIR in .env or pass --state-dir)", file=sys.stderr)

    bot_states = read_all_states(state_dir)
    guard_status = read_guard_status(state_dir)

    if args.no_exchange:
        exchange_data = {ex: {"exchange": ex, "available": False,
                              "note": "skipped (--no-exchange)", "usdt": None,
                              "open_positions": []} for ex in EXCHANGES}
    else:
        exchange_data = read_all_exchanges(EXCHANGES)

    build_report(bot_states, exchange_data, guard_status)


if __name__ == "__main__":
    main()
