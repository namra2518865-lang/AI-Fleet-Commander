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


def _bot_row(bot_state, guard_status):
    n = bot_state["n"]
    name = bot_state["name"]
    venue = f"{bot_state['exchange']}/{bot_state['market']}"
    open_pos = bot_state["open_positions"]

    if not bot_state["available"]:
        state = f"[dim]{bot_state['note']}[/dim]" if RICH else bot_state["note"]
    elif open_pos:
        syms = ", ".join(p["symbol"] for p in open_pos)
        state = f"IN TRADE: {syms}"
        if RICH:
            state = f"[green]{state}[/green]"
    else:
        state = "flat"

    pnl = bot_state.get("realized_pnl")
    return [str(n), name, venue, state, _fmt_money(pnl) if pnl is not None else "-"]


def build_report(bot_states, exchange_data, guard_status):
    """Return the report as a string (also prints if rich is available)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if RICH:
        console = Console(record=True)
        console.rule(f"[bold]AQUORA FLEET COMMANDER[/bold]  |  {now}")

        # --- Guards line ---
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

        # --- Fleet table ---
        t = Table(box=box.SIMPLE_HEAVY, expand=False, title="Bots")
        for col in ["#", "Strategy", "Venue", "State", "Realized PnL"]:
            t.add_column(col, no_wrap=(col in ("#", "Venue")))
        in_trade = 0
        for bs in bot_states:
            if bs["available"] and bs["open_positions"]:
                in_trade += 1
            t.add_row(*_bot_row(bs, guard_status))
        console.print(t)

        # --- Exchange balances table ---
        et = Table(box=box.SIMPLE_HEAVY, expand=False, title="Exchange balances (read-only)")
        for col in ["Exchange", "USDT", "Open positions", "Note"]:
            et.add_column(col)
        total = 0.0
        have_any = False
        for ex, d in exchange_data.items():
            usdt = d.get("usdt")
            if usdt is not None:
                total += usdt
                have_any = True
            pos = d.get("open_positions") or []
            pos_txt = ", ".join(
                f"{p['symbol']}({p['side']})" for p in pos
            ) or ("-" if d["available"] else "")
            note = d.get("note", "")
            if not note and d.get("source"):
                note = f"via {d['source']}"
            et.add_row(ex, _fmt_money(usdt), pos_txt,
                       f"[dim]{note}[/dim]" if note else "")
        console.print(et)

        summary = f"Bots in trade: {in_trade}/{len(bot_states)}"
        if have_any:
            summary += f"   ·   Live USDT across venues: {_fmt_money(total)}"
        console.print(f"[bold]{summary}[/bold]")

        return console.export_text()

    # ---- plain-text fallback ----
    lines = [f"AQUORA FLEET COMMANDER  |  {now}", "=" * 60]
    g = guard_status
    lines.append(
        f"Guards  Market:{'ON' if g['market_guard'] else 'OFF'}  "
        f"Event:{'ON' if g['event_guard'] else 'OFF'}  "
        f"Kill:{'ACTIVE' if g['kill_switch_active'] else 'armed' if g['kill_switch_active'] is not None else 'unknown'}"
    )
    lines.append("-" * 60)
    lines.append(f"{'#':<3}{'Strategy':<22}{'Venue':<18}{'State':<22}{'PnL':>10}")
    in_trade = 0
    for bs in bot_states:
        if bs["available"] and bs["open_positions"]:
            in_trade += 1
        r = _bot_row(bs, g)
        # strip rich markup for plain output
        state = r[3].replace("[green]", "").replace("[/green]", "").replace("[dim]", "").replace("[/dim]", "")
        lines.append(f"{r[0]:<3}{r[1]:<22}{r[2]:<18}{state:<22}{r[4]:>10}")
    lines.append("-" * 60)
    total, have_any = 0.0, False
    for ex, d in exchange_data.items():
        usdt = d.get("usdt")
        if usdt is not None:
            total += usdt
            have_any = True
        note = d.get("note", "")
        lines.append(f"{ex:<10}{_fmt_money(usdt):>12}   {note}")
    summ = f"Bots in trade: {in_trade}/{len(bot_states)}"
    if have_any:
        summ += f"   Live USDT: {_fmt_money(total)}"
    lines.append("=" * 60)
    lines.append(summ)
    text = "\n".join(lines)
    print(text)
    return text
