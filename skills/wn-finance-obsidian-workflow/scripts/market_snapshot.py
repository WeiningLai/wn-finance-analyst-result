#!/usr/bin/env python3
import argparse
import datetime as dt
import math
import os
import subprocess
from pathlib import Path


INDEX_QUOTES = (
    ("000001.SH", "上证指数"),
    ("399001.SZ", "深证成指"),
    ("399006.SZ", "创业板指"),
    ("000688.SH", "科创50"),
    ("000016.SH", "上证50"),
    ("000300.SH", "沪深300"),
)


def find_vault():
    env_vault = os.environ.get("OBSIDIAN_VAULT", "").strip()
    if env_vault and Path(env_vault).is_dir():
        return Path(env_vault)

    obsidian_json = Path.home() / "Library/Application Support/obsidian/obsidian.json"
    if obsidian_json.is_file():
        text = obsidian_json.read_text(encoding="utf-8", errors="ignore")
        marker = '"path":"'
        if marker in text:
            start = text.find(marker) + len(marker)
            end = text.find('"', start)
            if end > start:
                vault = Path(text[start:end])
                if vault.is_dir():
                    return vault

    fallback = Path.home() / "Documents/Obsidian Vault"
    if fallback.is_dir():
        return fallback
    return None


def get_keychain_secret(service):
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_api_key():
    for name in ("WN_TICKFLOW_API_KEY", "TICKFLOW_API_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return get_keychain_secret(os.environ.get("WN_TICKFLOW_KEYCHAIN_SERVICE", "wn-finance-tickflow"))


def safe_float(value):
    if value in (None, "", "-"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ratio_to_percent(value):
    ratio = safe_float(value)
    if ratio is None:
        return None
    return ratio * 100.0


def round_limit_price(prev_close, ratio):
    return math.floor(prev_close * (1 + ratio) * 100 + 0.5) / 100.0


def limit_ratio(symbol, name):
    code = symbol.split(".")[0]
    upper_name = (name or "").upper()
    if code.startswith(("92", "43", "81", "82", "83", "87", "88")) and not code.startswith("900"):
        return 0.30
    if code.startswith(("688", "30")):
        return 0.20
    if "ST" in upper_name:
        return 0.05
    return 0.10


def fetch_quotes(client, symbols):
    quotes = []
    for offset in range(0, len(symbols), 5):
        batch = symbols[offset : offset + 5]
        batch_quotes = client.quotes.get(symbols=batch)
        if batch_quotes:
            quotes.extend(batch_quotes)
    return quotes


def build_indices(client):
    symbols = [symbol for symbol, _ in INDEX_QUOTES]
    quotes = fetch_quotes(client, symbols)
    by_symbol = {str(item.get("symbol", "")).upper(): item for item in quotes if item}
    rows = []
    for symbol, name in INDEX_QUOTES:
        quote = by_symbol.get(symbol)
        if not quote:
            continue
        ext = quote.get("ext") or {}
        current = safe_float(quote.get("last_price"))
        prev_close = safe_float(quote.get("prev_close"))
        change = safe_float(ext.get("change_amount"))
        if change is None and current is not None and prev_close is not None:
            change = current - prev_close
        amplitude = ratio_to_percent(ext.get("amplitude"))
        if amplitude is None and prev_close and prev_close > 0:
            high = safe_float(quote.get("high")) or 0.0
            low = safe_float(quote.get("low")) or 0.0
            amplitude = (high - low) / prev_close * 100
        rows.append(
            {
                "symbol": symbol,
                "name": name,
                "current": current,
                "change": change,
                "change_pct": ratio_to_percent(ext.get("change_pct")),
                "open": safe_float(quote.get("open")),
                "high": safe_float(quote.get("high")),
                "low": safe_float(quote.get("low")),
                "prev_close": prev_close,
                "amount": safe_float(quote.get("amount")),
                "amplitude": amplitude,
            }
        )
    return rows


def is_cn_equity_symbol(symbol):
    upper = (symbol or "").strip().upper()
    code = upper.split(".")[0]
    return len(code) == 6 and code.isdigit() and upper.endswith((".SH", ".SZ", ".BJ"))


def extract_name(quote):
    ext = quote.get("ext") or {}
    return str(ext.get("name") or quote.get("name") or "").strip()


def build_market_stats(client):
    try:
        quotes = client.quotes.get(universes=["CN_Equity_A"])
    except Exception as exc:
        text = str(exc).lower()
        if any(word in text for word in ("permission", "forbidden", "universe", "标的池")):
            return {"status": "permission_denied"}
        return {"status": "failed", "error": "market_stats_fetch_failed"}

    stats = {
        "status": "ok",
        "up_count": 0,
        "down_count": 0,
        "flat_count": 0,
        "limit_up_count": 0,
        "limit_down_count": 0,
        "total_amount": 0.0,
    }
    valid_rows = 0
    for quote in quotes or []:
        symbol = str(quote.get("symbol") or "").strip().upper()
        if not is_cn_equity_symbol(symbol):
            continue
        amount = safe_float(quote.get("amount"))
        if amount and amount > 0:
            stats["total_amount"] += amount / 1e8

        last_price = safe_float(quote.get("last_price"))
        prev_close = safe_float(quote.get("prev_close"))
        if last_price is None or prev_close is None or not amount or amount <= 0:
            continue

        valid_rows += 1
        ratio = limit_ratio(symbol, extract_name(quote))
        limit_up = round_limit_price(prev_close, ratio)
        limit_down = math.floor(prev_close * (1 - ratio) * 100 + 0.5) / 100.0
        if abs(last_price - limit_up) <= round(abs(prev_close * (1 + ratio) - limit_up), 10):
            stats["limit_up_count"] += 1
        if abs(last_price - limit_down) <= round(abs(prev_close * (1 - ratio) - limit_down), 10):
            stats["limit_down_count"] += 1
        if last_price > prev_close:
            stats["up_count"] += 1
        elif last_price < prev_close:
            stats["down_count"] += 1
        else:
            stats["flat_count"] += 1

    if valid_rows == 0:
        return {"status": "empty"}
    return stats


def fmt(value, digits=2, suffix=""):
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}{suffix}"


def render_snapshot(date, fetched_at, indices, stats):
    lines = [
        f"## market_snapshot - {date}",
        "",
        f"fetched_at: {fetched_at}",
        "source: TickFlow",
        "scope: A股大盘核验",
        "",
        "### 主要指数",
        "",
        "| 指数 | 最新 | 涨跌幅 | 开盘 | 最高 | 最低 | 振幅 | 成交额(亿) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in indices:
        amount = item.get("amount")
        amount_yi = amount / 1e8 if amount is not None else None
        lines.append(
            f"| {item['name']} | {fmt(item.get('current'))} | {fmt(item.get('change_pct'), suffix='%')} | "
            f"{fmt(item.get('open'))} | {fmt(item.get('high'))} | {fmt(item.get('low'))} | "
            f"{fmt(item.get('amplitude'), suffix='%')} | {fmt(amount_yi, 0)} |"
        )

    lines.extend(["", "### 市场宽度", ""])
    if stats.get("status") == "ok":
        lines.extend(
            [
                f"up_count: {stats['up_count']}",
                f"down_count: {stats['down_count']}",
                f"flat_count: {stats['flat_count']}",
                f"limit_up_count: {stats['limit_up_count']}",
                f"limit_down_count: {stats['limit_down_count']}",
                f"total_amount_yi: {stats['total_amount']:.0f}",
            ]
        )
    else:
        lines.append(f"status: {stats.get('status', 'unavailable')}")
    lines.extend(
        [
            "",
            "### 使用边界",
            "",
            "该快照只用于验证市场环境、指数承接、成交额和涨跌宽度，不构成买卖建议；当行情数据与文章假设冲突时，应记录冲突并降低假设权重。",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    vault = find_vault()
    if vault is None:
        print("market_snapshot_status=blocked")
        print("reason=vault_not_found")
        return 0

    api_key = get_api_key()
    if not api_key:
        print("market_snapshot_status=skipped")
        print("reason=tickflow_api_key_not_configured")
        return 0

    try:
        from tickflow import TickFlow
    except ImportError:
        print("market_snapshot_status=blocked")
        print("reason=tickflow_package_not_installed")
        return 0

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    date = now.strftime("%Y-%m-%d")
    fetched_at = now.isoformat(timespec="seconds")

    if args.dry_run:
        print("market_snapshot_status=dry_run")
        print(f"date={date}")
        return 0

    client = TickFlow(api_key=api_key, timeout=float(os.environ.get("WN_TICKFLOW_TIMEOUT", "30")))
    try:
        indices = build_indices(client)
        stats = build_market_stats(client)
    finally:
        try:
            client.close()
        except Exception:
            pass

    if not indices:
        print("market_snapshot_status=failed")
        print("reason=indices_unavailable")
        return 0

    content = render_snapshot(date, fetched_at, indices, stats)
    rel = Path("finance-analysis/market-snapshots") / f"{date}.md"
    output = vault / rel
    if not args.no_write:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")

    print("market_snapshot_status=ok")
    print(f"relative_path={rel}")
    print(f"absolute_path={output}")
    print(f"indices={len(indices)}")
    print(f"market_stats_status={stats.get('status', 'unavailable')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
