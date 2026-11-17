# Sardon Steadfast starter

> Preview. Three scheduled Claude agents that share one Notion hub, propose before they act, and keep a record you can check.

## The three agents

| Agent | When | What it does | What it can change |
|---|---|---|---|
| **Commitments** | Weekdays 07:20 | Finds promises in your email, both ways ("I'll send it Friday", "refund in 5 days"), tracks them and closes them when kept | Only the hub. If someone owes you and is late, it proposes a polite nudge draft; it writes the draft only after you approve, and never sends |
| **Inbox tidy** | Sundays 11:00 | Proposes moving unread newsletters and promotions out of your inbox, in plain English | Nothing yet: propose-only, with read-only Gmail. A separate executor that only your Google login can approve will carry out approved tidy-ups (in progress) |
| **FPL brief** (optional) | Daily check, brief the evening before each deadline | Captain, transfers, bench and mini-league swings for your Fantasy Premier League team | Nothing. Recommendations only |
| **Subscription watch** (optional) | 1st of each month | Lists your subscriptions and renewals from receipts in your email; asks cancel-or-keep about likely waste | Nothing. You cancel; it checks next month and logs the saving |
| **Weather** (optional) | 06:30 and 18:30 daily | Today's and tomorrow's forecast where you are, plus trip destinations, with what to wear. Numbers straight from MET Norway (yr.no); clothing from fixed, tested rules | Nothing. Read-only |

## See it first

`home/demo.html` is the Home page with an invented person's week: approvals, promises, wins to confirm, agent health. Open it in a browser; every button works and nothing is saved. Your real Home reads your own Notion hub.

## What you need

- A Claude plan with Claude Code and scheduled routines.
- Notion and Gmail connected at claude.ai → Settings → Connectors.
- A GitHub fork of this repo, with the Claude GitHub app allowed to read it.
- About 30 minutes.

## Set it up

1. Fork this repo and clone your fork.
2. Open Claude Code in the clone.
3. Paste the prompt from [SETUP_PROMPT.md](starter/SETUP_PROMPT.md). It creates your hub ([HUB_SCHEMA.md](starter/HUB_SCHEMA.md), [HUB_PAGE.md](starter/HUB_PAGE.md)), writes your Config, creates the three routines and test-runs them, asking before each step.
4. Protect your fork's `main` branch so agents can never push to it.

## Safety

- Agents never send email, delete, unsubscribe, pay or log in anywhere. Their tool lists don't include those tools.
- No repo is attached to any agent, so they have no GitHub access: they download their instructions read-only from your public fork.
- Anything that touches your accounts goes to **Proposed actions** first. Silence means no.
- Inbox tidy's limits are enforced in code and covered by tests (`python3 -m unittest discover tests`).
- Kill switch: add a Facts row "Pause inbox tidy" updated by you.
- Your personal values live only in your private Notion Config, never in the repo.

## Measuring it

Each run logs whether it was on time. Each win goes in the Value ledger at a fixed rate (a deadline caught is 15 minutes, a prep page 20, and so on), and counts only when you mark it "Used it". After a month you'll know which agents earn their place.
