#!/usr/bin/env python3
"""Live crypto price ticker with terminal sparkline. Uses Crypto.com public API."""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import deque

API = "https://api.crypto.com/exchange/v1/public/get-tickers?instrument_name={symbol}"
SPARK = "▁▂▃▄▅▆▇█"
GREEN = "\033[32m"
RED = "\033[31m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def fetch_price(symbol: str) -> tuple[float, float]:
    url = API.format(symbol=symbol)
    with urllib.request.urlopen(url, timeout=5) as r:
        data = json.load(r)
    rows = data.get("result", {}).get("data", [])
    if not rows:
        raise RuntimeError(f"no data for {symbol}")
    t = rows[0]
    return float(t["a"]), float(t["c"])


def sparkline(values: list[float]) -> str:
    if len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    if hi == lo:
        return SPARK[0] * len(values)
    return "".join(SPARK[min(len(SPARK) - 1, int((v - lo) / (hi - lo) * (len(SPARK) - 1)))] for v in values)


def fmt_change(pct: float) -> str:
    color = GREEN if pct >= 0 else RED
    arrow = "▲" if pct >= 0 else "▼"
    return f"{color}{arrow} {pct:+.2f}%{RESET}"


def run(symbols: list[str], interval: float, history: int) -> None:
    series: dict[str, deque[float]] = {s: deque(maxlen=history) for s in symbols}
    sys.stdout.write("\033[?25l")
    try:
        while True:
            sys.stdout.write("\033[H\033[J")
            print(f"{BOLD}crypto ticker{RESET}  {DIM}refresh {interval}s · history {history}{RESET}\n")
            print(f"  {'symbol':<14}{'price':>14}{'24h':>16}  spark")
            print(f"  {DIM}{'─' * 60}{RESET}")
            for sym in symbols:
                try:
                    pct, price = fetch_price(sym)
                    series[sym].append(price)
                    spark = sparkline(list(series[sym]))
                    print(f"  {sym:<14}{price:>14,.4f}{fmt_change(pct):>26}  {spark}")
                except (urllib.error.URLError, RuntimeError, KeyError, ValueError) as e:
                    print(f"  {sym:<14}  {DIM}error: {e}{RESET}")
            sys.stdout.flush()
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\n")


def main() -> None:
    p = argparse.ArgumentParser(description="Live crypto ticker")
    p.add_argument("symbols", nargs="*", default=["BTC_USDT", "ETH_USDT", "SOL_USDT"],
                   help="instrument names like BTC_USDT")
    p.add_argument("--interval", type=float, default=5.0)
    p.add_argument("--history", type=int, default=40)
    args = p.parse_args()
    run(args.symbols, args.interval, args.history)


if __name__ == "__main__":
    main()
