#!/usr/bin/env python3
"""Refuse to go public while personal details remain in tracked files.

Reads every value in config/owner.yaml (plus its optional `private_terms`
list) and searches all git-tracked files for them. Also flags raw Notion
IDs and claude.ai artifact links, which should only ever live in config.

Exit code 0 = clean, 1 = personal details found.
Usage: python3 tools/check_public.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "owner.yaml"

GENERIC_PATTERNS = {
    "Notion ID": re.compile(r"(collection|view)://[0-9a-f-]{20,}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
    "artifact link": re.compile(r"claude\.ai/artifact/[A-Za-z0-9]{10,}"),
    "routine id": re.compile(r"trig_[A-Za-z0-9]{10,}"),
    "email address": re.compile(r"[\w.+-]+@(?!example\.(?:com|org|net)\b)[\w-]+\.[\w.]+"),
}


def config_terms():
    """Every scalar value in owner.yaml, without needing a YAML library."""
    if not CONFIG.exists():
        return []
    terms = set()
    for line in CONFIG.read_text().splitlines():
        line = line.split(" #", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            value = line[2:]
        elif ":" in line:
            value = line.split(":", 1)[1]
        else:
            continue
        value = value.strip().strip('"').strip("'")
        if value in ("", ">-", "|", ">") or value.lower() in ("true", "false", "yes", "no"):
            continue
        # Multi-word values: check each distinctive word as well as the whole.
        terms.add(value)
        for word in re.findall(r"[A-Za-z0-9][\w.@-]{3,}", value):
            # Only split out words that identify on their own (IDs, emails);
            # ordinary words inside a name ("Portfolio") are not personal.
            if any(c.isdigit() for c in word) or "@" in word:
                terms.add(word)
    return sorted(terms, key=len, reverse=True)


def tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.splitlines() if not p.startswith("config/owner.yaml")]


def main():
    terms = config_terms()
    problems = []
    for path in tracked_files():
        if path.name == "check_public.py":
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        rel = path.relative_to(ROOT)
        for n, line in enumerate(text.splitlines(), 1):
            for term in terms:
                if term in line:
                    problems.append(f"{rel}:{n}: personal value '{term}'")
            for label, pattern in GENERIC_PATTERNS.items():
                for m in pattern.finditer(line):
                    if "example" in m.group(0):
                        continue
                    problems.append(f"{rel}:{n}: {label} '{m.group(0)[:40]}'")
    if problems:
        print(f"Not ready to go public: {len(problems)} personal detail(s) found.\n")
        for p in problems:
            print("  " + p)
        return 1
    print("Clean: no personal details in tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
