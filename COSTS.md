# What it costs

Measured, not estimated, including the bad numbers. These are real numbers from the full build (the system this kit comes from), measured over one week, 2026-11-19 to 2026-11-25. Run minutes are how long each agent ran; a win counts only when the owner marked it "Used it".

| Agent | Model | Runs | Failed | Timed runs | Run minutes | Confirmed wins | Minutes saved |
|---|---|---|---|---|---|---|---|
| Morning brief | Opus | 5 | 0 | 5 of 5 | 18 | 1 | 20 |
| Week ahead | Opus | 1 | 0 | 1 of 1 | 5 | 0 | 0 |
| Portfolio review | Opus | 1 | 0 | 1 of 1 | 5 | 0 | 0 |
| Inbox tidy | Sonnet | 1 | 0 | 1 of 1 | 2 | 0 | 0 |
| Transaction watch | Sonnet | 2 | 0 | 2 of 2 | 2 | 0 | 0 |
| Weather | Sonnet | 6 | 0 | 6 of 6 | 2 | 0 | 0 |
| Commitments | Sonnet | 4 | 0 | 3 of 4 | 2 | 0 | 0 |
| Travel watch | Sonnet | 1 | 0 | 1 of 1 | 1 | 0 | 0 |
| Post ideas | Opus | 1 | 0 | 1 of 1 | 1 | 0 | 0 |
| Job search | Opus | 1 | 0 | 1 of 1 | 1 | 0 | 0 |
| FPL brief | Opus | 1 | 0 | 0 of 1 | 0 | 0 | 0 |
| Health check | Sonnet | 3 | 0 | 0 of 3 | 0 | 0 | 0 |
| **Total** | | 27 | 0 | 22 of 27 | 39 | 1 | 20 |

- Opus minutes per confirmed win: 30.
- Timing source: 0 of 22 timed runs from the routine's own run log; the rest are the agent's self-report, which misses start-up time and reads low.
- 1 run stalled (over 60 minutes, e.g. waiting on a hung Notion call) and is left out of the minutes: FPL brief (1).
- 5 runs finished partial: Morning brief (1), Portfolio review (1), Inbox tidy (1), Transaction watch (1), Travel watch (1).
- 4 of 27 runs weren't timed; their minutes are missing from the totals, not estimated.
- Plan usage: Not measured. The weekly usage figure for 19–25 Nov reset before it was read (the 12% read on 25 Nov covers only that day, mostly the owner's own coding). Ran on a Claude Pro plan.
- The starter kit runs three of these: Commitments, Inbox tidy and Weather, all on Sonnet. This week they made 11 runs and about 6 self-reported minutes in total.
- Minutes are the agents' own reports, which have read about half of real run time when checked; no per-run session timings this week.
- Health check and FPL daily check fire every day but write a Run log row only when they have work, so their quiet runs aren't counted.
- Morning brief changed mid-week (distilled-state pilot).
- Morning brief and Portfolio review run as desktop scheduled tasks on Opus; the rest are cloud routines.

## What this doesn't tell you yet

- **A money figure.** Agents run on a Claude plan, which reports usage as a share of a weekly limit, not in tokens or euros. That share wasn't captured for this week, so there's no honest euro figure here.
- **What the kit costs you.** The kit runs only Commitments, Inbox tidy and Weather, all on Sonnet. The friend test (from 1 Dec 2026) will measure it on someone else's account.
- **How long runs really take.** Most minutes are the agents' own reports, which have read about half the real time when checked.

One confirmed win in a week is the honest number. The full build's retirement rule ([kill log](KILL_LOG.md)) exists for exactly this: agents with no confirmed wins in four weeks are proposed for retirement.
