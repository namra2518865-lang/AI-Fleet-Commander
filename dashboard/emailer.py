"""Send the fleet report as an HTML email via Resend.

Reuses the same Resend pipeline the news radar uses. Credentials
(RESEND_API_KEY, EMAIL_TO) are read from the dashboard env first, then from
the news radar's own .env under FLEET_ROOT/newsradar/.env — so no new keys
are needed. Uses only the standard library (urllib) to POST to Resend.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from dashboard.daily_pnl import fleet_today_summary

RESEND_URL = "https://api.resend.com/emails"
DEFAULT_FROM = "Aquora Fleet Commander <onboarding@resend.dev>"


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


def _resend_config(fleet_root=None):
    api_key = os.getenv("RESEND_API_KEY")
    email_to = os.getenv("EMAIL_TO")
    email_from = os.getenv("EMAIL_FROM", DEFAULT_FROM)
    if (not api_key or not email_to) and fleet_root:
        env = _parse_env_file(os.path.join(fleet_root, "newsradar", ".env"))
        api_key = api_key or env.get("RESEND_API_KEY")
        email_to = email_to or env.get("EMAIL_TO")
    return api_key, email_to, email_from


def _pnl_html(v):
    if v is None:
        return '<span style="color:#888">-</span>'
    color = "#1a9c4a" if v > 0 else "#d13b3b" if v < 0 else "#888"
    sign = "+" if v >= 0 else "-"
    return f'<span style="color:{color};font-weight:600">{sign}${abs(v):,.2f}</span>'


def _money_html(v):
    return f"${v:,.2f}" if v is not None else '<span style="color:#888">-</span>'


def render_html(bot_states, bot_balances, guard_status, daily):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bot_balances = bot_balances or {}
    daily = daily or {}

    def bal(n):
        return (bot_balances.get(n) or {}).get("usdt")

    def net_for(n):
        return (daily.get(n) or {}).get("net")

    total_bal = sum(v for v in (bal(b["n"]) for b in bot_states if not b.get("paper")) if v)
    total_profit = sum(v for v in (b.get("realized_pnl") for b in bot_states
                                   if not b.get("paper")) if v)
    in_trade = sum(1 for b in bot_states
                   if not b.get("paper") and b["available"] and b["open_positions"])
    n_live = sum(1 for b in bot_states if not b.get("paper"))
    summary = fleet_today_summary(bot_states, daily)

    def guard_badge(v):
        if v is None:
            return '<span style="color:#888">unknown</span>'
        return ('<span style="color:#1a9c4a">ON</span>' if v
                else '<span style="color:#c98a00">OFF</span>')

    ks = guard_status["kill_switch_active"]
    ks_txt = ('<span style="color:#d13b3b">ACTIVE (FROZEN)</span>' if ks
              else '<span style="color:#1a9c4a">armed</span>') \
        if ks is not None else '<span style="color:#888">unknown</span>'

    rows = []
    for bs in bot_states:
        n = bs["n"]
        if not bs["available"]:
            state = f'<span style="color:#888">{bs["note"]}</span>'
        elif bs["open_positions"]:
            syms = ", ".join(p["symbol"] for p in bs["open_positions"])
            state = f'<span style="color:#1a9c4a;font-weight:600">IN TRADE: {syms}</span>'
        else:
            state = '<span style="color:#666">flat</span>'
        name = bs["name"]
        if bs.get("paper"):
            name += ' <span style="background:#eee;color:#777;font-size:10px;' \
                    'padding:1px 5px;border-radius:3px">PAPER</span>'
        d = daily.get(n) or {}
        wl = ""
        if d.get("trades"):
            wl = (f'<div style="font-size:11px;color:#888">{d["trades"]} trades'
                  f', {d.get("wins", 0)}W/{d.get("losses", 0)}L</div>')
        bg = "#faf7ef" if bs.get("paper") else "#fff"
        rows.append(f"""
        <tr style="background:{bg}">
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{n}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{name}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;color:#555">{bs['exchange']}/{bs['market']}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{state}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right">{_money_html(bal(n))}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right">{_pnl_html(net_for(n))}{wl}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right">{_pnl_html(bs.get('realized_pnl'))}</td>
        </tr>""")

    # ---- Today's trades detail (per bot, from trades.csv) ----
    trade_blocks = []
    for bs in bot_states:
        d = daily.get(bs["n"]) or {}
        events = d.get("events")
        if not events:
            continue
        items = []
        for e in events[:12]:
            tag = ' <span style="color:#999">(partial)</span>' if e.get("partial") else ""
            items.append(f"{e['symbol']} {_pnl_html(e.get('pnl'))}{tag}")
        if len(events) > 12:
            items.append(f'<span style="color:#999">+{len(events) - 12} more</span>')
        wl = ""
        if d.get("wins") is not None:
            wl = f" ({d.get('wins', 0)}W/{d.get('losses', 0)}L)"
        extra = f" + {d['partials']} partial" if d.get("partials") else ""
        paper_tag = ' <span style="color:#999">[PAPER]</span>' if bs.get("paper") else ""
        trade_blocks.append(
            f'<div style="padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:12px">'
            f'<b>Bot {bs["n"]} {bs["name"]}{paper_tag}</b>: {", ".join(items)}'
            f'<span style="color:#555"> &rarr; {d.get("trades", 0)} trade(s){wl}{extra}, '
            f'net {_pnl_html(d.get("net"))}</span></div>'
        )
    trades_section = ""
    if trade_blocks:
        trades_section = (
            '<div style="background:#fff;border-left:1px solid #e5e7eb;'
            'border-right:1px solid #e5e7eb;padding:12px 22px">'
            '<div style="font-weight:700;font-size:13px;margin-bottom:6px">'
            "Today's Trades</div>" + "".join(trade_blocks) + "</div>"
        )

    return f"""<!DOCTYPE html>
<html><body style="margin:0;background:#f4f5f7;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif">
<div style="max-width:720px;margin:0 auto;padding:24px">
  <div style="background:#0f1720;color:#fff;border-radius:10px 10px 0 0;padding:18px 22px">
    <div style="font-size:18px;font-weight:700;letter-spacing:.5px">AQUORA FLEET COMMANDER</div>
    <div style="font-size:12px;color:#9fb0c0;margin-top:2px">{now}</div>
  </div>
  <div style="background:#fff;padding:14px 22px;border-left:1px solid #e5e7eb;border-right:1px solid #e5e7eb">
    <div style="font-size:13px;color:#333">
      Guards &nbsp; Market: {guard_badge(guard_status['market_guard'])} &nbsp;·&nbsp;
      Event: {guard_badge(guard_status['event_guard'])} &nbsp;·&nbsp;
      Kill-Switch: {ks_txt}
    </div>
  </div>
  <table style="width:100%;border-collapse:collapse;background:#fff;font-size:13px;
                border-left:1px solid #e5e7eb;border-right:1px solid #e5e7eb">
    <thead>
      <tr style="background:#f0f2f5;color:#444;text-align:left">
        <th style="padding:8px 10px">#</th>
        <th style="padding:8px 10px">Strategy</th>
        <th style="padding:8px 10px">Venue</th>
        <th style="padding:8px 10px">State</th>
        <th style="padding:8px 10px;text-align:right">Balance</th>
        <th style="padding:8px 10px;text-align:right">Day P&amp;L</th>
        <th style="padding:8px 10px;text-align:right">Total P&amp;L</th>
      </tr>
    </thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  {trades_section}
  <div style="background:#fff;border-left:1px solid #e5e7eb;border-right:1px solid #e5e7eb;
              padding:12px 22px;font-size:13px;color:#333">
    <b>Today (live fleet):</b>&nbsp; Trades {summary['trades']} &nbsp;·&nbsp;
    <span style="color:#1a9c4a">Wins {summary['wins']}</span> &nbsp;
    <span style="color:#d13b3b">Losses {summary['losses']}</span> &nbsp;·&nbsp;
    Profit {_pnl_html(summary['profit'])} &nbsp; Loss {_pnl_html(summary['loss'])}
    &nbsp;·&nbsp; <b>Net</b> {_pnl_html(summary['net'])}
  </div>
  <div style="background:#0f1720;color:#fff;border-radius:0 0 10px 10px;padding:14px 22px;font-size:13px">
    <b>Bots in trade:</b> {in_trade}/{n_live} &nbsp;·&nbsp;
    <b>Total live USDT:</b> ${total_bal:,.2f} &nbsp;·&nbsp;
    <b>Total profit (all-time):</b> {_pnl_html(total_profit)}
  </div>
  <div style="color:#9aa4af;font-size:11px;text-align:center;padding:12px">
    Bot 3 (EMA-Pullback) is PAPER — shown but excluded from live totals.<br>
    Read-only fleet monitor · not financial advice
  </div>
</div>
</body></html>"""


def send_report(bot_states, bot_balances, guard_status, daily, fleet_root=None):
    """Render + send the report. Returns (ok, message)."""
    api_key, email_to, email_from = _resend_config(fleet_root)
    if not api_key or not email_to:
        return False, "no RESEND_API_KEY / EMAIL_TO found"

    summary = fleet_today_summary(bot_states, daily or {})
    net = summary["net"]
    day_txt = f"{'+' if net >= 0 else '-'}${abs(net):,.2f}"
    in_trade = sum(1 for b in bot_states
                   if not b.get("paper") and b["available"] and b["open_positions"])
    subject = (f"Aquora Fleet — {in_trade} in trade, "
               f"{summary['trades']} trades today, net {day_txt}")

    html = render_html(bot_states, bot_balances, guard_status, daily)
    payload = json.dumps({
        "from": email_from,
        "to": [email_to],
        "subject": subject,
        "html": html,
    }).encode("utf-8")

    req = urllib.request.Request(
        RESEND_URL, data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Resend sits behind Cloudflare, which blocks the default
            # Python-urllib User-Agent (error 1010). Send a normal UA.
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if 200 <= resp.status < 300:
                return True, f"email sent to {email_to}"
            return False, f"resend HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "ignore")[:300]
        except Exception:
            pass
        return False, f"HTTP {e.code} (from={email_from}, to={email_to}): {body}"
    except Exception as e:
        return False, f"send failed: {str(e)[:80]}"
