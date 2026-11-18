# Sardon Steadfast starter

> **A personal AI team with a strict manager.** Agents propose, you approve. A win counts only when you confirm it. The time you spend supervising is subtracted. Agents that stop earning their place get retired, and the retirements are published.

Preview. This kit is the first part of a system one person runs every day: scheduled Claude agents that share one Notion hub and keep a record you can check.

## How this differs

Most personal-agent projects measure what their agents do: messages handled, tasks completed, hours of activity. This one measures what the owner gets back, after the time it costs to supervise them. An agent's output counts as a win only when the owner marks it "used". Supervision (reading reports, approving proposals, correcting mistakes) is counted as a cost. And an agent that produces nothing the owner uses for four weeks is proposed for retirement. The measure is allowed to come out negative, because a number that can't go down proves nothing.

## Owned, gated, measured

- **Owned.** The agents run on your own Claude plan, from your own fork, and write to your own Notion hub. You can read every instruction they follow, and the kit's author receives nothing. Switch off any agent and the rest keep running.
- **Gated.** Agents watch and propose; nothing touches your accounts until you approve it. No agent logs in, books or pays anywhere.
- **Measured.** Every run is logged. A win counts only when you mark it used. Agents that stop earning their place are retired, and the retirements are published in the [kill log](KILL_LOG.md).

## What's in this kit, and what isn't yet

| Part | In this kit | In the full build |
|---|---|---|
| Agents propose; nothing touches your accounts until you approve | Yes | Yes |
| A win counts only when you mark it "Used it" | Yes | Yes |
| Weekly review: supervision time subtracted, net time per agent | Not yet | Yes |
| Retirement proposals for agents nobody uses (4 weeks, no confirmed wins) | Not yet | Yes |
| [Kill log](KILL_LOG.md): every agent retired, merged or cut back, with the evidence | Yes | Yes |

## The agents

There are two kinds of agent:

- **Live:** "Ask the hub" on your Home page. It answers when you ask, from your hub, and anything it suggests saving waits for your tap.
- **Proactive:** the scheduled agents below. They run while you're away, watching your email, deadlines and forecasts, and leave proposals and reports in your hub.

There is no third kind that works websites for you, logging in, booking or paying. That's deliberate: every action that touches your accounts waits for your approval.

| Agent | Kind | When | What it does | What it can change |
|---|---|---|---|---|
| **Commitments** | Proactive | Weekdays 07:20 | Finds promises in your email, both ways ("I'll send it Friday", "refund in 5 days"), tracks them and closes them when kept | Only the hub. If someone owes you and is late, it proposes a polite nudge draft. It writes the draft only after you approve, and never sends |
| **Inbox tidy** | Proactive | Sundays 11:00 | Proposes moving unread newsletters and promotions out of your inbox, in plain English | Nothing: propose-only, with read-only Gmail. A separate executor that only your Google login can approve will carry out approved tidy-ups (in progress) |
| **FPL brief** (optional) | Proactive | Daily check; a brief the evening before each deadline | Captain, transfers, bench and mini-league swings for your Fantasy Premier League team | Nothing. Recommendations only |
| **Subscription watch** (optional) | Proactive | 1st of each month | Lists your subscriptions and renewals from receipts in your email; asks cancel-or-keep about likely waste | Nothing. You cancel; it checks next month and logs the saving |
| **Weather** (optional) | Proactive | 06:30 daily | Today's and tomorrow's forecast where you are, plus trip destinations, with what to wear. Numbers straight from MET Norway (yr.no); clothing from fixed, tested rules | Nothing. Read-only |

## See it first

`home/demo.html` is the Home page with an invented person's week: approvals, promises, wins to confirm, agent health. Open it in a browser; every button works and nothing is saved. Your real Home reads your own Notion hub.

## What it costs

- **A paid Claude plan that includes scheduled tasks (routines).** Free plans don't run scheduled agents.
- **Agent runs count against the same usage limits as your own chats.** The full build hit its weekly limit once while being developed, and runs that hit the limit fail. The kit is designed to be much lighter.
- **Estimated draw for this kit: about 3 to 6 million tokens a month, mostly Sonnet** (roughly a sixth of the full build). This is an estimate from run lengths, not a measurement; Anthropic doesn't publish plan limits in tokens. It will be replaced with measured numbers after the first outside test.
- Biggest costs, in order: Commitments (weekdays), Weather (daily), then the weekly and monthly agents.

## What you need

- The Claude plan above, with Claude Code.
- Notion and Gmail connected at claude.ai → Settings → Connectors.
- A GitHub fork of this repo, with the Claude GitHub app allowed to read it.
- About 30 minutes.

## Set it up

1. Fork this repo and clone your fork.
2. Open Claude Code in the clone.
3. Paste the prompt from [SETUP_PROMPT.md](starter/SETUP_PROMPT.md). It creates your hub ([HUB_SCHEMA.md](starter/HUB_SCHEMA.md), [HUB_PAGE.md](starter/HUB_PAGE.md)), writes your Config, creates the routines and test-runs them, asking before each step.
4. Protect your fork's `main` branch so agents can never push to it.

## Safety

- Agents never send email, delete, unsubscribe, pay or log in anywhere. Their tool lists don't include those tools.
- Agents that only follow instructions (Commitments, Inbox tidy, Subscription watch) have no repo attached, so they have no GitHub access: they download their instructions read-only from your public fork. Agents that run code (Weather, FPL) have the repo attached, because Claude's safety checks block running code downloaded from the web; with `main` protected, the most they could do is open a branch or pull request you'd see and decline.
- Anything that touches your accounts goes to **Proposed actions** first. Silence means no.
- Inbox tidy's limits are enforced in code and covered by tests (`python3 -m unittest discover tests`).
- Kill switch: add a Facts row "Pause inbox tidy" updated by you.
- Switch off any agent by asking Claude Code to disable its routine. Nothing is deleted, and no agent depends on another.
- Your personal values live only in your private Notion Config, never in the repo.

## Measuring it

Each run logs whether it was on time. Each win goes in the Value ledger at a fixed rate (a deadline caught is 15 minutes, a prep page 20, and so on), and counts only when you mark it "Used it". After a month you'll know which agents earn their place.

## Before you trust it

- [THREAT_MODEL.md](THREAT_MODEL.md): what's enforced by code, what's only an instruction, where your data goes, and what a malicious email could and couldn't do.
- [FRIEND_TEST.md](FRIEND_TEST.md): the pass/fail criteria for the first outside test, written before it ran.

## What we won't build

Ideas that don't strengthen governance, measurement or operability go on the [someday list](SOMEDAY.md), not into the kit.
