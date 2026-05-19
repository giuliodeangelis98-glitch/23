#!/usr/bin/env python3
"""Multi-turn terminal chat with Claude. Streaming output, prompt caching, slash commands."""
from __future__ import annotations

import argparse
import os
import sys

try:
    import anthropic
except ImportError:
    sys.exit("error: anthropic SDK not installed. run: pip install anthropic")

MODEL = "claude-opus-4-7"
DEFAULT_SYSTEM = "You are a helpful assistant running in a terminal. Keep replies concise unless asked for detail."

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

HELP = """\
slash commands:
  /help           show this help
  /clear          clear conversation history
  /system <text>  set a new system prompt (clears history)
  /tokens         show usage from last response
  /quit, /exit    exit
"""


def stream_reply(client: anthropic.Anthropic, system: str, messages: list[dict], think: bool) -> tuple[str, object]:
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": 16000,
        "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        "messages": messages,
    }
    if think:
        kwargs["thinking"] = {"type": "adaptive"}

    print(f"{GREEN}claude{RESET} ", end="", flush=True)
    chunks: list[str] = []
    with client.messages.stream(**kwargs) as stream:
        for text in stream.text_stream:
            sys.stdout.write(text)
            sys.stdout.flush()
            chunks.append(text)
        final = stream.get_final_message()
    print()
    return "".join(chunks), final.usage


def fmt_usage(usage) -> str:
    parts = [f"in={usage.input_tokens}", f"out={usage.output_tokens}"]
    if getattr(usage, "cache_read_input_tokens", 0):
        parts.append(f"{CYAN}cache_read={usage.cache_read_input_tokens}{RESET}")
    if getattr(usage, "cache_creation_input_tokens", 0):
        parts.append(f"cache_write={usage.cache_creation_input_tokens}")
    return " ".join(parts)


def read_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return "/quit"


def repl(system: str, think: bool) -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("error: ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic()
    messages: list[dict] = []
    last_usage = None

    print(f"{BOLD}claude chat{RESET} {DIM}· {MODEL} · /help for commands{RESET}")
    if think:
        print(f"{DIM}adaptive thinking enabled{RESET}")

    while True:
        line = read_input(f"\n{YELLOW}you{RESET} ").strip()
        if not line:
            continue

        if line in ("/quit", "/exit"):
            break
        if line == "/help":
            print(HELP)
            continue
        if line == "/clear":
            messages = []
            print(f"{DIM}history cleared{RESET}")
            continue
        if line.startswith("/system "):
            system = line[len("/system "):].strip() or DEFAULT_SYSTEM
            messages = []
            print(f"{DIM}system updated, history cleared{RESET}")
            continue
        if line == "/tokens":
            print(fmt_usage(last_usage) if last_usage else f"{DIM}no usage yet{RESET}")
            continue
        if line.startswith("/"):
            print(f"{DIM}unknown command. /help for list{RESET}")
            continue

        messages.append({"role": "user", "content": line})
        try:
            reply, last_usage = stream_reply(client, system, messages, think)
        except anthropic.APIError as e:
            messages.pop()
            print(f"{DIM}api error: {e}{RESET}")
            continue
        except KeyboardInterrupt:
            messages.pop()
            print(f"\n{DIM}interrupted{RESET}")
            continue

        messages.append({"role": "assistant", "content": reply})
        print(f"{DIM}{fmt_usage(last_usage)}{RESET}")


def main() -> None:
    p = argparse.ArgumentParser(description="Terminal chat with Claude")
    p.add_argument("--system", default=DEFAULT_SYSTEM, help="initial system prompt")
    p.add_argument("--think", action="store_true", help="enable adaptive thinking")
    args = p.parse_args()
    repl(args.system, args.think)


if __name__ == "__main__":
    main()
