"""Render the fleet status as a terminal report.

Uses `rich` for tables/colour when available, and falls back to plain text
if it is not installed, so the report always prints.
"""

from datetime import datetime, timezone

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


def _state_text(bot_state):
    open_pos = bot_state["open_positions"]
    if not bot_state["available"]:
        return f"[dim]{bot_state['note']}[/dim]" if RICH else bot_state["note"]
    if open_pos:
        syms = ", ".join(p["symbol"] for p in open_pos)
        txt = f"IN TRADE: {syms}"
        return f"[green]{txt}[/green]" if RICH else txt
    return "flat"


def build_report(bot_states, bot_balances, guard_status):
    """Return the report as a string (also prints if rich is available)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bot_balances = bot_balances or {}

    def bal_for(n):
        return (bot_balances.get(n) or {}).get("usdt")

    total_balance = sum(v for v in (bal_for(b["n"]) for b in bot_states) if v)
    in_trade = sum(1 for b in bot_states if b["available"] and b["open_positions"])

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
        for col in ["#", "Strategy", "Venue", "State", "Balance", "Realized PnL"]:
            t.add_column(col, no_wrap=(col in ("#", "Venue", "Balance")))
        for bs in bot_states:
            n = bs["n"]
            bal = bal_for(n)
            binfo = bot_balances.get(n) or {}
            bal_txt = _fmt_money(bal)
            if bal is None and binfo.get("note"):
                bal_txt = f"[dim]{binfo['note'][:18]}[/dim]"
            pnl = bs.get("realized_pnl")
            t.add_row(
                str(n), bs["name"], f"{bs['exchange']}/{bs['market']}",
                _state_text(bs), bal_txt,
                _fmt_money(pnl) if pnl is not None else "-",
            )
        console.print(t)

        console.print(
            f"[bold]Bots in trade: {in_trade}/{len(bot_states)}"
            f"   |   Total live USDT: {_fmt_money(total_balance)}[/bold]"
        )
        return console.export_text()

    # ---- plain-text fallback ----
    lines = [f"AQUORA FLEET COMMANDER  |  {now}", "=" * 72]
    g = guard_status
    ks = g["kill_switch_active"]
    lines.append(
        f"Guards  Market:{'ON' if g['market_guard'] else 'OFF'}  "
        f"Event:{'ON' if g['event_guard'] else 'OFF'}  "
        f"Kill:{'ACTIVE' if ks else 'armed' if ks is not None else 'unknown'}"
    )
    lines.append("-" * 72)
    lines.append(f"{'#':<3}{'Strategy':<22}{'Venue':<17}{'State':<22}{'Balance':>10}")
    for bs in bot_states:
        state = _state_text(bs)
        bal = bal_for(bs["n"])
        lines.append(
            f"{bs['n']:<3}{bs['name']:<22}{bs['exchange']+'/'+bs['market']:<17}"
            f"{state:<22}{_fmt_money(bal):>10}"
        )
    lines.append("-" * 72)
    lines.append(
        f"Bots in trade: {in_trade}/{len(bot_states)}   "
        f"Total live USDT: {_fmt_money(total_balance)}"
    )
    text = "\n".join(lines)
    print(text)
    return text
