# Agents

One file per scheduled agent. The YAML front matter is metadata (schedule, model, tools); the body is the agent's instructions, with `{{placeholders}}` for personal values.

## How a routine runs an agent

Commitments and Inbox tidy have no repo attached. A routine with a repo attached gets GitHub access that acts as you (it can push branches, open pull requests, and GitHub won't stop it merging one), so these two download their instruction files read-only instead. Weather runs a script, and Claude's safety checks block running code downloaded from the web, so its routine has your fork attached. Its instructions forbid touching the repo; nothing else stops it.

Each routine's prompt is this bootstrap, filled in once at setup. `{REF}` is the commit of your fork at setup time, so the instructions an agent follows can't change unless you change the routine.

```
You are the {AGENT NAME} agent of Sardon Steadfast. Download your instructions read-only:
  curl -fsSL https://raw.githubusercontent.com/{OWNER}/{REPO}/{REF}/agents/{file}.md -o /tmp/agent.md
  curl -fsSL https://raw.githubusercontent.com/{OWNER}/{REPO}/{REF}/hub/RULES.md -o /tmp/rules.md
Read both files (ignore the YAML front matter). Then fetch the Notion hub page {hub page id}
and read its "Config" section: it gives the value of every {{placeholder}} in your
instructions. Substitute them, then follow the instructions exactly. The hub page's Rules
override hub/RULES.md where they differ. If either download fails or the Config section is
missing, don't improvise: add a Run log row ({run log data source}) with Agent "{AGENT NAME}",
Result "Failed" and the reason, send a push saying so, and stop.
```

`{OWNER}/{REPO}` is your fork. Keep your fork public (it holds no personal values).

## Agents

| File | Schedule | Changes anything outside the hub? |
|---|---|---|
| `commitments.md` | Weekdays 07:20 | Creates a reply draft only for a nudge you approved (an instruction, not enforced); never sends |
| `inbox-tidy.md` | Sundays 11:00 | No. Propose-only, with read-only Gmail. You carry out approved tidy-ups yourself in Gmail |
| `weather.md` (optional) | 06:30 daily | No. Read-only forecast from MET Norway (yr.no) |

FPL brief and Subscription watch run in the full build only.
