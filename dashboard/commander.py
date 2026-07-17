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

from dashboard.daily_pnl import compute_daily_pnl
from dashboard.emailer import send_report
from dashboard.exchange_reader import read_all_bot_balances
from dashboard.fleet_config import FLEET
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
    parser.add_argument("--root", default=None,
                        help="override FLEET_ROOT (dir holding /bot*, /newsradar)")
    parser.add_argument("--email", action="store_true",
                        help="send the report as an HTML email via Resend")
    parser.add_argument("--quiet", action="store_true",
                        help="don't print the terminal report (use with --email in cron)")
    args = parser.parse_args(argv)

    _load_dotenv()

    fleet_root = args.root or os.getenv("FLEET_ROOT", "/root")
    if not os.path.isdir(fleet_root):
        print(f"[warn] FLEET_ROOT not found: {fleet_root} "
              f"(set FLEET_ROOT in .env or pass --root)", file=sys.stderr)

    bot_states = read_all_states(fleet_root)
    guard_status = read_guard_status(fleet_root)

    daily = compute_daily_pnl(bot_states, fleet_root)

    if args.no_exchange:
        bot_balances = {}
    else:
        bot_balances = read_all_bot_balances(FLEET, fleet_root)

    if not args.quiet:
        build_report(bot_states, bot_balances, guard_status, daily)

    if args.email:
        ok, msg = send_report(bot_states, bot_balances, guard_status,
                              daily, fleet_root)
        print(f"[email] {msg}", file=sys.stderr if not ok else sys.stdout)


if __name__ == "__main__":
    main()
