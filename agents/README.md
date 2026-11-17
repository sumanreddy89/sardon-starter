# Agents

One file per scheduled agent. The YAML front matter is metadata (schedule, model, tools); the body is the agent's instructions, with `{{placeholders}}` for personal values.

## How a routine runs an agent

Agents that only follow instructions (Commitments, Inbox tidy, Subscription watch) have no repo attached: a routine with a repo attached gets a GitHub key that acts as you and can push branches and open pull requests, so they download their instruction files read-only instead. Agents that run code (Weather, FPL) do need their repo attached, because Claude's safety checks block running code downloaded from the web. Their repos are public with `main` protected, so the most they could do is open a branch or pull request you'd see and decline.

Each routine's prompt is this bootstrap, filled in once at setup:

```
You are the {AGENT NAME} agent of Sardon Steadfast. Download your instructions read-only:
  curl -fsSL https://raw.githubusercontent.com/{OWNER}/{REPO}/main/agents/{file}.md -o /tmp/agent.md
  curl -fsSL https://raw.githubusercontent.com/{OWNER}/{REPO}/main/hub/RULES.md -o /tmp/rules.md
Read both files (ignore the YAML front matter). Then fetch the Notion hub page {hub page id}
and read its "Config" section: it gives the value of every {{placeholder}} in your
instructions. Substitute them, then follow the instructions exactly. The hub page's Rules
override hub/RULES.md where they differ. If either download fails or the Config section is
missing, don't improvise: add a Run log row ({run log data source}) with Agent "{AGENT NAME}",
Result "Failed" and the reason, send a push saying so, and stop.
```

`{OWNER}/{REPO}` is your fork. Keep your fork public (it holds no personal values) and protect its `main` branch.

## Agents

| File | Schedule | Changes anything outside the hub? |
|---|---|---|
| `commitments.md` | Weekdays 07:20 | Creates a reply draft only for a nudge you approved; never sends |
| `inbox-tidy.md` | Sundays 11:00 | No. Propose-only: read-only Gmail. Approved tidy-ups are carried out by a separate executor |
| `fpl-daily-check-and-brief.md` | Daily 19:00 UTC | No. Recommendations only |
| `subscription-and-renewal-watch.md` (optional) | 1st of the month 11:00 | No. Asks cancel-or-keep; you cancel |
| `weather.md` (optional) | 06:30 and 18:30 daily | No. Read-only forecast from MET Norway (yr.no) |
