# Sardon Steadfast starter

> **What a personal AI team looks like when the person actually owns it.**

It runs for you, never instead of you. Specialized agents watch your world, draft your work and keep a shared memory. They share one hub and one set of rules, written as plain instructions you can read. They read your email and write to your hub on their own; anything else that would touch your accounts is proposed first, and a win counts only when you confirm it.

It's not a product or a chatbot. It's a template: fork it and you run your own team, for yourself. Where funded agents go deep on one domain for many users, this goes deep on one person's life: your conventions, your history, and a kill list of what didn't work.

Preview. This kit is a small, tested part of a fuller system one person runs every day (the "full build"). Where the two differ, this README says so.

**Status: release [`v0.4`](https://github.com/sumanreddy89/sardon-starter/releases/tag/v0.4). The first outside test hasn't happened yet; it starts on 1 Dec 2026** ([criteria, written before it runs](FRIEND_TEST.md)). The numbers so far: [what it costs](COSTS.md), measured, and the [kill log](KILL_LOG.md) of every agent retired, merged or cut back.

## Start here

Not sure yet? Download `home/demo.html` and open it in a browser. It's the full build's Home page with an invented person's week: approvals, promises, wins to confirm, agent health. Every button works except Ask the hub, which needs the full build, and nothing is saved. **The kit doesn't install a Home page:** you use your Notion hub directly.

### What you need

- A paid Claude plan that includes scheduled tasks (see [What it costs](#what-it-costs)), with Claude Code.
- Notion and Gmail connected at claude.ai → Settings → Connectors.
- A GitHub fork of this repo, with the Claude GitHub app allowed to read it.
- Python 3 and git on your computer (setup runs the kit's tests).
- About 30 minutes, if nothing goes wrong. No one outside has timed it yet; the [friend test](FRIEND_TEST.md) will.

### Set it up

1. Fork this repo and clone your fork. If you were asked to test a release, check that the commit setup reports in its first step is the commit of that release's tag (on the repo's Tags page). A fork copies `main`, not a tag.
2. Open Claude Code in the clone.
3. Paste the prompt from [SETUP_PROMPT.md](starter/SETUP_PROMPT.md). It creates your hub ([HUB_SCHEMA.md](starter/HUB_SCHEMA.md), [HUB_PAGE.md](starter/HUB_PAGE.md)), writes your Config, creates the routines and test-runs them, asking before each step.
4. Protect your fork's `main` branch: Settings > Branches > add a classic branch protection rule for `main`. Tick "Require a pull request before merging", untick "Require approvals" (you're the only reviewer), and tick "Do not allow bypassing the above settings". This stops direct pushes; see [Safety](#safety) for what it doesn't stop.

## Owned, gated, measured

- **Owned.** The agents run on your own Claude plan, from your own fork, and write to your own Notion hub. Your data stays in accounts you own and can export. You can read every instruction the agents follow, and the kit's author receives nothing. Switch off any agent and the rest keep running.
- **Gated.** Agents read your email and write to your hub without asking. Anything else is proposed first, and no agent sends, books, spends or logs in anywhere.
- **Measured.** Most agent projects count what their agents do; this counts what you used. Every run is logged, and a win counts only when you mark it "Used it". The full build also subtracts your supervision time, so the measure can come out negative, and retires agents that stop earning their place ([kill log](KILL_LOG.md)). A number that can't go down proves nothing.

## What's in this kit, and what isn't yet

| Part | In this kit | In the full build |
|---|---|---|
| Agents propose changes outside the hub; you approve | Yes | Yes |
| Home page (approve, mark wins, ask the hub) | No; use Notion directly. [Demo](home/demo.html) | Yes |
| A win counts only when you mark it "Used it" | Yes | Yes |
| Weekly review: supervision time subtracted, net time per agent | Not yet | Yes |
| Retirement proposals for agents nobody uses (4 weeks, no confirmed wins) | Not yet | Yes |
| [Kill log](KILL_LOG.md): every agent retired, merged or cut back, with the evidence | Yes | Yes |

## The agents

All three are scheduled: they run while you're away and leave proposals and reports in your hub. None of them works websites for you, logs in, books or pays. That's deliberate.

| Agent | When | What it does | What it can change |
|---|---|---|---|
| **Commitments** | Weekdays 07:20 | Finds promises in your email, both ways ("I'll send it Friday", "refund in 5 days"), tracks them, and closes them when the thread shows they were kept (with the evidence; you can reopen) | The hub. If someone owes you and is late, it proposes a polite nudge; after you approve, it writes a Gmail draft and never sends it |
| **Inbox tidy** | Sundays 11:00 | Proposes clearing unread newsletters and promotions out of your inbox, in plain English, with the Gmail search to do it yourself | Nothing in Gmail: every Gmail tool that changes mail is removed from its routine. Nothing in the kit carries out a tidy-up for you yet |
| **Weather** (optional) | 06:30 daily | Today's and tomorrow's forecast where you are, plus trip destinations, with what to wear. Numbers straight from MET Norway (yr.no); clothing from fixed, tested rules | Nothing outside the hub. Its routine has your fork attached; see [Safety](#safety) |

FPL brief, Subscription watch and the full build's other agents aren't in the kit.

## What it costs

- **A paid Claude plan that includes scheduled tasks (routines).** Free plans don't run scheduled agents.
- **Agent runs count against the same usage limits as your own chats.** The full build hit its weekly limit once while being developed, and runs that hit the limit fail. The kit is designed to be much lighter.
- **Measured run time and confirmed wins, per agent: [COSTS.md](COSTS.md)**, from one week of the full build, bad numbers included. The kit's three agents (all Sonnet) made 11 runs and used about 6 minutes in that week. There's no euro figure yet: plan usage is reported as a share of a weekly limit, and that share wasn't captured. The friend test will measure the kit on someone else's account.

## Safety

What's enforced and what's only an instruction is spelled out in [THREAT_MODEL.md](THREAT_MODEL.md). In short:

- **Automatic, without asking:** reading your email, writing to your hub, push notifications.
- **Proposed first:** anything outside the hub. Commitments' Gmail drafts wait for your approval, but that rule is an instruction to the model, not a technical block.
- **Removed from every routine (its deny list):** sending, replying, forwarding, trashing, labelling and marking spam in Gmail, plus deleting or moving Notion pages. Commitments keeps create-draft for nudges you approve; Inbox tidy can only search and read. A routine's *allowed* tool list doesn't limit anything: in a 19 Nov test, a routine allowed only three Gmail reading tools still created a Gmail label. The deny list is what stopped it. Setup shows you each routine's deny list and connectors after creating it.
- **Only the connectors each agent needs:** Notion and Gmail for Commitments and Inbox tidy, Notion only for Weather. Setup names them; a routine created without a list gets every connector you have.
- **GitHub:** Commitments and Inbox tidy have no repo attached and download instructions pinned to one commit, so changes to your fork don't reach them until you update. Weather has your fork attached, which gives it GitHub access as you; protecting `main` stops direct pushes but not a pull request it opens and merges itself. Its instructions forbid that; nothing else does.
- **Notion:** the connector reaches your whole workspace. Agents are told to stay inside the hub; nothing enforces it. Connect a workspace with nothing sensitive in it if that matters to you.
- Pause Inbox tidy with a Facts row "Pause inbox tidy" updated by you. Switch off any agent by asking Claude Code to disable its routine; nothing is deleted, and no agent depends on another.
- Your personal values live only in your private Notion Config, never in the repo.

### What the gate does not stop

The approval gate covers actions outside the hub. It does not stop:

- **An agent reading your email.** Reading is allowed without asking; that's how the agents work.
- **Wrong or misleading rows in your hub.** Agents write to the hub on their own. A malicious email could steer what they write.
- **An agent reaching other Notion pages.** The connector can reach your whole workspace; staying inside the hub is an instruction, not a block.
- **Commitments creating a Gmail draft you didn't approve.** It's never sent, but *when* a draft is created is an instruction.
- **Weather merging a pull request in your fork.** Its routine has GitHub access as you, and GitHub's review rules don't stop the account they act as.
- **Usage.** Runs count against your Claude plan's limits like your own chats; nothing caps an agent's run time.

Details and tests: [THREAT_MODEL.md](THREAT_MODEL.md).

## Measuring it

Each run logs whether it was on time. Each win goes in the Value ledger and counts only when you mark it "Used it". The ledger also gives each win an **estimated** number of minutes from a fixed rate card (a deadline caught is 15, a prep page 20); that's a rough score, not measured time. The confirmed wins are the number to trust.

Tests: `python3 -m unittest discover tests` covers the Weather script, the tidy guard (written for a future executor; no agent uses it yet), and a consistency check that agents, schema, Config and setup agree. Nothing tests a live routine or Notion end to end; the friend test is that check.

## Before you trust it

- [THREAT_MODEL.md](THREAT_MODEL.md): what's enforced by code, what's only an instruction, where your data goes, and what a malicious email could and couldn't do.
- [FRIEND_TEST.md](FRIEND_TEST.md): the pass/fail criteria for the first outside test, written before it ran.

## Licence

[MIT](LICENSE).

## What we won't build

Ideas that don't strengthen governance, measurement or operability go on the [someday list](SOMEDAY.md), not into the kit.
