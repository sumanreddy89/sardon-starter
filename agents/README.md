# Agents

One file per scheduled agent. The YAML front matter is metadata (schedule, model, connectors, tools, deny list); the body is the agent's instructions, with `{{placeholders}}` for personal values.

## What limits a routine

Three settings, and only two of them are limits. Tested on 19 Nov 2026.

- **`connectors`**: the only connectors the routine gets. Setup must list them explicitly; a routine created without a connector list gets every connector you've connected.
- **`disallowed_tools`** (the deny list): these tools are removed from the routine entirely. The agent can't load or call them. Every Gmail tool that sends, replies, forwards, drafts, trashes, labels or marks spam is on it, except `create_draft` for Commitments.
- **`tools`** (the allowed list) is **not** a limit. It only pre-approves tools. In the test, a routine whose allowed list had three Gmail reading tools could still load all 31 Gmail tools and created a Gmail label. Don't rely on it.

When you change a routine, send its whole configuration (environment, model, tools, deny list and prompt). A partial update replaces the session settings and erases the prompt.

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
| `commitments.md` | Weekdays 07:20 | Creates a reply draft only for a nudge you approved (an instruction, not enforced). Sending, replying and every other Gmail change are on its deny list |
| `inbox-tidy.md` | Sundays 11:00 | No. Propose-only; every Gmail tool that changes mail is on its deny list. You carry out approved tidy-ups yourself in Gmail |
| `weather.md` (optional) | 06:30 daily | No. Read-only forecast from MET Norway (yr.no) |

FPL brief and Subscription watch run in the full build only.
