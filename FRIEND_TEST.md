# First outside test: success criteria

Written on 17 Nov 2026, **before** the test, so the result can't be argued either way afterwards. Revised on 18 Nov 2026, still before the test, so that the criteria check the kit's three claims: owned, gated, measured. Revised again on 18 Nov 2026 after an outside review, still before the test: logging, retention and cost criteria fixed so a correctly working kit can pass them. Revised on 19 Nov 2026, still before the test: the release moves to `v0.3`, because a test showed a routine's allowed tool list doesn't limit Gmail; v0.3 adds deny lists and explicit connectors, and the criteria are unchanged. The tester uses the tagged release `v0.3` and their own Claude, Notion and Gmail accounts. The commit their routines are pinned to is recorded with the results.

## Pass or fail

| # | Claim | Criterion | How it's checked | Pass |
|---|---|---|---|---|
| 1 | Owned | Setup takes under an hour, with no help from the author | The tester times it from fork to first test run. Any question to the author counts as help (it's logged, not hidden) | Under 60 minutes, zero help |
| 2 | Owned | The first test run of every chosen agent passes | Each agent's first Run log row | Result "Done" for every agent |
| 3 | Owned | The tester can switch off an agent without breaking the rest | On day 7 the tester switches off one agent of their choice, using only the README | The other agents' next scheduled runs are "Done", and nothing else had to change |
| 4 | Gated | Nothing outside the hub changed without the tester's approval | On day 7, the tester checks their Gmail drafts and labels against Proposed actions | Every change matches a row they approved; zero exceptions |
| 5 | Gated | The tester can explain what has access to what | Asked on day 1, without notes: what can each agent read, what can it change, what needs their approval | Correct for every agent they set up |
| 6 | Measured | The tester knows what it costs them and what it returned | Asked on day 7, without notes: that agent runs share their plan's usage limits with their own chats, roughly how many runs a week they've switched on, and how many wins they confirmed | All three correct against the README, their routines and the Value ledger |
| 7 | Measured | The agents are still running on day 7 | Run log | Every scheduled run on days 1 to 7 has a Run log row; every failure's summary says why |
| 8 | All three | "I'd keep this" on day 7 | Asked on day 7: keep it running, or switch it off? | "Keep it", unprompted |

All eight must pass. Anything else the tester hits is recorded as a finding, not as a pass or a fail.

## Also recorded (not pass/fail)

- Did agent runs push the tester's plan to its limit?
- Supervision minutes in the first week.
- Every question the tester asked, every point where they got stuck, and every bug, with the release it was found in.

## Retention (recorded, not pass/fail)

A **retained runner** on day N is a tester who, on that day:

1. still has at least one agent switched on,
2. the most recent scheduled run of at least one switched-on agent, before that day, is "Done" in their Run log (for Inbox tidy, last Sunday's run; for the others, the last weekday or day), and
3. says, when asked, that they're still running it on purpose.

All three, checked from the tester's self-report and a screenshot or export of their Run log. Measured on **day 7** (the same day as criterion 8) and again on **day 30**, and recorded here for every tester.

## Afterwards

Results go in this file, unedited, next to these criteria. A failed criterion becomes an issue and, where it's a bug, a regression test.
