#!/usr/bin/env python3
"""Gatekeeper for Inbox tidy: decides, in code, whether one approved tidy-up may touch Gmail.

The agent must run this for every approved row and obey the verdict. The rules
live here, not only in the prompt, so they hold even if the agent misreads its
instructions or an email tries to talk it into something.

Verdicts (printed as JSON, also the exit code):
  ACT      (0) - all checks pass; use the returned "search" and "label" exactly,
                 and move at most "max_threads" threads.
  SKIP     (1) - the row breaks a rule; change nothing, leave it Approved, log "reasons".
  DRY_RUN  (2) - the row is fine but this isn't a real run (wrong day or time);
                 report what would happen, change nothing.
  PAUSED   (3) - the owner's kill switch is on; change nothing at all this run.

Usage:
  python3 tools/tidy_guard.py --tz Europe/London --status Approved \
      --from-agent "Inbox tidy" --type Other --proposed-on 2026-11-08 \
      --action "Clear X out of your inbox: 11 emails ..." \
      --details "label Tidy/X; archive; search: in:inbox from:news@example.com newer_than:30d" \
      --count 12 --moved-so-far 0 --paused no
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, time, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

# Limits
SLACK_OVER_APPROVED = 5        # count may exceed the approved number by this much
MAX_PER_TIDY = 50              # threads in one tidy-up
MAX_PER_RUN = 150              # threads in one run, across all tidy-ups
APPROVAL_MAX_AGE_DAYS = 14     # proposals older than this are stale
WINDOW_DAY = 6                 # Sunday (Monday is 0)
WINDOW_START = time(10, 30)
WINDOW_END = time(13, 0)

# Always excluded from any search, whatever Details says
SAFETY_EXCLUSIONS = "-is:starred -is:important -from:me"

FORBIDDEN_IN_SEARCH = [
    (re.compile(r"\bOR\b"), "uses OR"),
    (re.compile(r"[{}|()]"), "uses grouping characters"),
    (re.compile(r"\*"), "uses a wildcard"),
    (re.compile(r"\bcategory:", re.I), "uses category:"),
    (re.compile(r"\blabel:", re.I), "uses label:"),
    (re.compile(r"\bin:(anywhere|all|sent|spam|trash|drafts?)\b", re.I), "searches outside the inbox"),
    (re.compile(r"-in:", re.I), "uses -in:"),
    (re.compile(r"\bis:(starred|important)\b", re.I), "targets starred or important mail"),
    (re.compile(r"(?<![\w-])(to|cc|bcc|deliveredto):", re.I), "uses a recipient operator"),
]
FROM_OPERATOR = re.compile(r"(?<![\w-])from:(\S+)", re.I)
NEGATED_FROM = re.compile(r"-from:", re.I)
LABEL_NAME = re.compile(r"^Tidy/[A-Za-z0-9 .&'_-]{1,40}$")
APPROVED_COUNT = re.compile(r"(\d+)\s+(?:e-?mails?|threads?|messages?)\b", re.I)


NOTION_MAILTO = re.compile(r"\[([^\[\]\s]+@[^\[\]\s]+)\]\(mailto:([^()\s]+)\)")


def undo_notion_formatting(text):
    """Notion returns 'a@example.com' as '[a@example.com](mailto:a@example.com)' and '_' as '\\_'.

    Only a link whose text and address are identical is unwrapped; anything
    else stays as it is, and the search checks then reject it.
    """
    text = NOTION_MAILTO.sub(lambda m: m.group(1) if m.group(1) == m.group(2) else m.group(0), text)
    return text.replace("\\_", "_")


def parse_details(details):
    """Split 'label Tidy/X; archive; search: ...' into its parts."""
    details = undo_notion_formatting(details)
    parts = [p.strip() for p in details.split(";") if p.strip()]
    label, archive, search = None, False, None
    for p in parts:
        low = p.lower()
        if low.startswith("label "):
            label = p[6:].strip()
        elif low == "archive":
            archive = True
        elif low.startswith("search:"):
            search = p[7:].strip()
        elif low.startswith(("moved ", "undo:")):
            continue  # notes appended by earlier runs
        else:
            return None, None, None, f"Details has an unrecognised part: {p[:40]!r}"
    return label, archive, search, None


def check_search(search):
    reasons = []
    if not re.search(r"(?<![\w-])in:inbox\b", search, re.I):
        reasons.append("search doesn't contain in:inbox")
    senders = FROM_OPERATOR.findall(search)
    if len(senders) != 1:
        reasons.append(f"search must name exactly one sender (found {len(senders)})")
    elif "@" not in senders[0] or "," in senders[0]:
        reasons.append("sender must be a single full email address")
    if NEGATED_FROM.search(search):
        reasons.append("search uses -from:")
    for pattern, why in FORBIDDEN_IN_SEARCH:
        if pattern.search(search):
            reasons.append(f"search {why}")
    return reasons


def decide(args, now):
    reasons = []

    if args.paused:
        return {"verdict": "PAUSED", "reasons": ["Owner's kill switch (Pause inbox tidy) is on"]}

    # Row must be exactly an approved Inbox tidy proposal
    if args.status != "Approved":
        reasons.append(f"Status is {args.status!r}, not 'Approved'")
    if args.from_agent != "Inbox tidy":
        reasons.append(f"From agent is {args.from_agent!r}, not 'Inbox tidy'")
    if args.type != "Other":
        reasons.append(f"Type is {args.type!r}, not 'Other'")

    today = now.date()
    try:
        proposed = date.fromisoformat(args.proposed_on[:10])
        age = (today - proposed).days
        if age < 0:
            reasons.append("Proposed on is in the future")
        elif age > APPROVAL_MAX_AGE_DAYS:
            reasons.append(f"approval is stale: proposed {age} days ago (limit {APPROVAL_MAX_AGE_DAYS})")
    except ValueError:
        reasons.append("Proposed on isn't a date")

    # The number the owner actually approved, from the plain-English Action
    m = APPROVED_COUNT.search(args.action or "")
    approved = int(m.group(1)) if m else None
    if approved is None:
        reasons.append("Action doesn't say how many emails were approved")

    label, archive, search, err = parse_details(args.details or "")
    if err:
        reasons.append(err)
    else:
        if not label or not LABEL_NAME.match(label):
            reasons.append("label must be 'Tidy/<name>' (letters, numbers, spaces, . & ' _ -)")
        if not search:
            reasons.append("Details has no search")
        else:
            reasons.extend(check_search(search))

    # Counts
    if args.count < 0:
        reasons.append("count can't be negative")
    if approved is not None and args.count > approved + SLACK_OVER_APPROVED:
        reasons.append(f"found {args.count} threads but only {approved} were approved (+{SLACK_OVER_APPROVED} allowed)")
    if args.count > MAX_PER_TIDY:
        reasons.append(f"found {args.count} threads; one tidy-up may move at most {MAX_PER_TIDY}")
    if args.moved_so_far + args.count > MAX_PER_RUN:
        reasons.append(f"would take this run to {args.moved_so_far + args.count} threads; limit {MAX_PER_RUN}")

    if reasons:
        return {"verdict": "SKIP", "reasons": reasons}

    result = {
        "label": label,
        "archive": archive,
        "search": f"{search} {SAFETY_EXCLUSIONS}",
        "max_threads": min(args.count, MAX_PER_TIDY),
    }

    in_window = (
        now.weekday() == WINDOW_DAY
        and WINDOW_START <= now.time() <= WINDOW_END
    )
    if not in_window:
        result.update(verdict="DRY_RUN", reasons=[
            f"not a real run: real changes only on Sunday {WINDOW_START:%H:%M}-{WINDOW_END:%H:%M} "
            f"local time (now {now:%a %H:%M})"
        ])
        return result

    result.update(verdict="ACT", reasons=[])
    return result


EXIT_CODES = {"ACT": 0, "SKIP": 1, "DRY_RUN": 2, "PAUSED": 3}


def yes_no(value):
    v = value.strip().lower()
    if v in ("yes", "true", "1"):
        return True
    if v in ("no", "false", "0"):
        return False
    raise argparse.ArgumentTypeError("use yes or no")


def build_parser():
    p = argparse.ArgumentParser(description="Decide whether an approved tidy-up may touch Gmail.")
    p.add_argument("--tz", required=True, help="owner's timezone, e.g. Europe/London")
    p.add_argument("--status", required=True)
    p.add_argument("--from-agent", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--proposed-on", required=True, help="YYYY-MM-DD")
    p.add_argument("--action", required=True, help="the row's plain-English Action")
    p.add_argument("--details", required=True, help="the row's Details")
    p.add_argument("--count", type=int, required=True, help="threads the search matches now")
    p.add_argument("--moved-so-far", type=int, default=0, help="threads already moved this run")
    p.add_argument("--paused", type=yes_no, required=True, help="yes if the owner paused Inbox tidy")
    return p


def main(argv=None, _now=None):
    """Command-line entry point. The clock always comes from the system;
    `_now` exists only for tests calling this function from Python and can't
    be set from the command line."""
    args = build_parser().parse_args(argv)
    if ZoneInfo is None:
        out = {"verdict": "SKIP", "reasons": ["Python lacks zoneinfo; can't check the time window"]}
    else:
        tz = ZoneInfo(args.tz)
        now = datetime.fromisoformat(_now).replace(tzinfo=tz) if _now else datetime.now(tz)
        out = decide(args, now)
    print(json.dumps(out, ensure_ascii=False))
    return EXIT_CODES[out["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
