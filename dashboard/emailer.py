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


def render_html(bot_states, bot_balances, guard_status, daily_pnl):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bot_balances = bot_balances or {}
    daily_pnl = daily_pnl or {}

    def bal(n):
        return (bot_balances.get(n) or {}).get("usdt")

    total_bal = sum(v for v in (bal(b["n"]) for b in bot_states) if v)
    total_day = sum(v for v in (daily_pnl.get(b["n"]) for b in bot_states) if v)
    in_trade = sum(1 for b in bot_states if b["available"] and b["open_positions"])

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
        rows.append(f"""
        <tr>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{n}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{bs['name']}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;color:#555">{bs['exchange']}/{bs['market']}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee">{state}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right">{_money_html(bal(n))}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right">{_pnl_html(daily_pnl.get(n))}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #eee;text-align:right">{_pnl_html(bs.get('realized_pnl'))}</td>
        </tr>""")

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
  <div style="background:#0f1720;color:#fff;border-radius:0 0 10px 10px;padding:14px 22px;font-size:13px">
    <b>Bots in trade:</b> {in_trade}/{len(bot_states)} &nbsp;·&nbsp;
    <b>Total live USDT:</b> ${total_bal:,.2f} &nbsp;·&nbsp;
    <b>Today:</b> {_pnl_html(total_day)}
  </div>
  <div style="color:#9aa4af;font-size:11px;text-align:center;padding:12px">
    Read-only fleet monitor · not financial advice
  </div>
</div>
</body></html>"""


def send_report(bot_states, bot_balances, guard_status, daily_pnl, fleet_root=None):
    """Render + send the report. Returns (ok, message)."""
    api_key, email_to, email_from = _resend_config(fleet_root)
    if not api_key or not email_to:
        return False, "no RESEND_API_KEY / EMAIL_TO found"

    total_day = sum(v for v in (daily_pnl or {}).values() if v)
    day_txt = f"{'+' if total_day >= 0 else '-'}${abs(total_day):,.2f}"
    in_trade = sum(1 for b in bot_states if b["available"] and b["open_positions"])
    subject = f"Aquora Fleet — {in_trade} in trade, today {day_txt}"

    html = render_html(bot_states, bot_balances, guard_status, daily_pnl)
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
