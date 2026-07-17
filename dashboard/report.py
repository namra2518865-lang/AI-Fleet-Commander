"""Render the fleet status as a terminal report.

Uses `rich` for tables/colour when available, and falls back to plain text
if it is not installed, so the report always prints.
"""

from datetime import datetime, timezone

from dashboard.daily_pnl import fleet_today_summary

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    RICH = True
except ImportError:
    RICH = False


def _fmt_money(v):
    if v is None:
        return "-"
    return f"${v:,.2f}"


def _fmt_pnl(v):
    """Signed P&L with colour markup (green up, red down)."""
    if v is None:
        return "-"
    sign = "+" if v >= 0 else "-"
    txt = f"{sign}${abs(v):,.2f}"
    if not RICH:
        return txt
    if v > 0:
        return f"[green]{txt}[/green]"
    if v < 0:
        return f"[red]{txt}[/red]"
    return f"[dim]{txt}[/dim]"


def _state_text(bot_state):
    open_pos = bot_state["open_positions"]
    if not bot_state["available"]:
        return f"[dim]{bot_state['note']}[/dim]" if RICH else bot_state["note"]
    if open_pos:
        syms = ", ".join(p["symbol"] for p in open_pos)
        txt = f"IN TRADE: {syms}"
        return f"[green]{txt}[/green]" if RICH else txt
    return "flat"


def _name_text(bs):
    if bs.get("paper"):
        return f"{bs['name']} [PAPER]"
    return bs["name"]


def _event_str(e):
    tag = " (partial)" if e.get("partial") else ""
    return f"{e['symbol']} {_fmt_pnl(e.get('pnl'))}{tag}"


_MAX_EVENTS_SHOWN = 12


def _bot_trades_line(bs, d):
    """One line listing a bot's today trades, or None if it didn't trade."""
    events = (d or {}).get("events")
    if not events:
        return None
    shown = events[:_MAX_EVENTS_SHOWN]
    parts = ", ".join(_event_str(e) for e in shown)
    if len(events) > _MAX_EVENTS_SHOWN:
        parts += f", +{len(events) - _MAX_EVENTS_SHOWN} more"
    wl = ""
    if d.get("wins") is not None:
        wl = f" ({d.get('wins', 0)}W/{d.get('losses', 0)}L)"
    tail = f"{d.get('trades', 0)} trade(s){wl}"
    if d.get("partials"):
        tail += f" + {d['partials']} partial"
    return f"Bot {bs['n']} {bs['name']}: {parts}  ->  {tail}, net {_fmt_pnl(d.get('net'))}"


def build_report(bot_states, bot_balances, guard_status, daily=None):
    """Return the report as a string (also prints if rich is available)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bot_balances = bot_balances or {}
    daily = daily or {}

    def bal_for(n):
        return (bot_balances.get(n) or {}).get("usdt")

    def net_for(n):
        return (daily.get(n) or {}).get("net")

    # Live totals EXCLUDE paper bots (bot 3)
    total_balance = sum(
        v for v in (bal_for(b["n"]) for b in bot_states if not b.get("paper")) if v
    )
    total_profit_alltime = sum(
        v for v in (b.get("realized_pnl") for b in bot_states if not b.get("paper")) if v
    )
    in_trade = sum(1 for b in bot_states
                   if not b.get("paper") and b["available"] and b["open_positions"])
    summary = fleet_today_summary(bot_states, daily)

    if RICH:
        console = Console(record=True)
        console.rule(f"[bold]AQUORA FLEET COMMANDER[/bold]  |  {now}")

        def onoff(v):
            if v is None:
                return "[dim]unknown[/dim]"
            return "[green]ON[/green]" if v else "[yellow]OFF[/yellow]"

        ks = guard_status["kill_switch_active"]
        ks_txt = ("[red]ACTIVE (FROZEN)[/red]" if ks else "[green]armed[/green]") \
            if ks is not None else "[dim]unknown[/dim]"
        console.print(
            f"Guards   Market: {onoff(guard_status['market_guard'])}   "
            f"Event: {onoff(guard_status['event_guard'])}   "
            f"Kill-Switch: {ks_txt}"
        )

        t = Table(box=box.SIMPLE_HEAVY, expand=False, title="Bots")
        for col in ["#", "Strategy", "Venue", "State", "Balance",
                    "Day P&L", "Total P&L"]:
            t.add_column(col, no_wrap=(col in ("#", "Venue", "Balance",
                                               "Day P&L", "Total P&L")))
        for bs in bot_states:
            n = bs["n"]
            bal = bal_for(n)
            binfo = bot_balances.get(n) or {}
            bal_txt = _fmt_money(bal)
            if bal is None and binfo.get("note"):
                bal_txt = f"[dim]{binfo['note'][:18]}[/dim]"
            t.add_row(
                str(n), _name_text(bs), f"{bs['exchange']}/{bs['market']}",
                _state_text(bs), bal_txt,
                _fmt_pnl(net_for(n)), _fmt_pnl(bs.get("realized_pnl")),
            )
        console.print(t)

        # ---- Today's trades (per bot, from trades.csv) ----
        trade_lines = [ln for ln in
                       (_bot_trades_line(bs, daily.get(bs["n"])) for bs in bot_states)
                       if ln]
        if trade_lines:
            console.print("\n[bold]Today's Trades[/bold]")
            for ln in trade_lines:
                console.print(f"  {ln}")

        # ---- Today's activity (live fleet) ----
        console.print(
            f"\n[bold]Today (live):[/bold]  "
            f"Trades {summary['trades']}  |  "
            f"[green]Wins {summary['wins']}[/green]  "
            f"[red]Losses {summary['losses']}[/red]  |  "
            f"Profit {_fmt_pnl(summary['profit'])}  "
            f"Loss {_fmt_pnl(summary['loss'])}  |  "
            f"Net {_fmt_pnl(summary['net'])}"
        )
        console.print(
            f"[bold]Bots in trade: {in_trade}/{len(bot_states) - _paper_count(bot_states)}"
            f"   |   Total live USDT: {_fmt_money(total_balance)}"
            f"   |   Total profit (all-time): {_fmt_pnl(total_profit_alltime)}[/bold]"
        )

        # paper bots shown separately (not in live totals)
        for bs in bot_states:
            if bs.get("paper"):
                d = daily.get(bs["n"]) or {}
                console.print(
                    f"[dim]PAPER — {bs['name']} (Bot {bs['n']}): "
                    f"today {_fmt_pnl(d.get('net'))}, "
                    f"total {_fmt_pnl(bs.get('realized_pnl'))} "
                    f"(not counted in live totals)[/dim]"
                )
        return console.export_text()

    # ---- plain-text fallback ----
    lines = [f"AQUORA FLEET COMMANDER  |  {now}", "=" * 84]
    g = guard_status
    ks = g["kill_switch_active"]
    lines.append(
        f"Guards  Market:{'ON' if g['market_guard'] else 'OFF'}  "
        f"Event:{'ON' if g['event_guard'] else 'OFF'}  "
        f"Kill:{'ACTIVE' if ks else 'armed' if ks is not None else 'unknown'}"
    )
    lines.append("-" * 84)
    lines.append(f"{'#':<3}{'Strategy':<22}{'Venue':<16}{'State':<20}"
                 f"{'Balance':>10}{'Day':>10}")
    for bs in bot_states:
        lines.append(
            f"{bs['n']:<3}{_name_text(bs):<22}{bs['exchange']+'/'+bs['market']:<16}"
            f"{_state_text(bs):<20}{_fmt_money(bal_for(bs['n'])):>10}"
            f"{_fmt_pnl(net_for(bs['n'])):>10}"
        )
    lines.append("-" * 84)
    trade_lines = [ln for ln in
                   (_bot_trades_line(bs, daily.get(bs["n"])) for bs in bot_states)
                   if ln]
    if trade_lines:
        lines.append("Today's Trades:")
        for ln in trade_lines:
            lines.append(f"  {ln}")
        lines.append("-" * 84)
    lines.append(
        f"Today (live): Trades {summary['trades']}  Wins {summary['wins']}  "
        f"Losses {summary['losses']}  Profit {_fmt_pnl(summary['profit'])}  "
        f"Loss {_fmt_pnl(summary['loss'])}  Net {_fmt_pnl(summary['net'])}"
    )
    lines.append(
        f"Bots in trade: {in_trade}/{len(bot_states) - _paper_count(bot_states)}   "
        f"Total live USDT: {_fmt_money(total_balance)}   "
        f"Total profit (all-time): {_fmt_pnl(total_profit_alltime)}"
    )
    for bs in bot_states:
        if bs.get("paper"):
            d = daily.get(bs["n"]) or {}
            lines.append(
                f"PAPER - {bs['name']} (Bot {bs['n']}): today "
                f"{_fmt_pnl(d.get('net'))}, total {_fmt_pnl(bs.get('realized_pnl'))} "
                f"(not in live totals)"
            )
    text = "\n".join(lines)
    print(text)
    return text


def _paper_count(bot_states):
    return sum(1 for b in bot_states if b.get("paper"))
