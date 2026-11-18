# First outside test: success criteria

Written on 17 Nov 2026, **before** the test, so the result can't be argued either way afterwards. Revised on 18 Nov 2026, still before the test, so that the criteria check the kit's three claims: owned, gated, measured. The tester uses the tagged release `v0.1` and their own Claude, Notion and Gmail accounts.

## Pass or fail

| # | Claim | Criterion | How it's checked | Pass |
|---|---|---|---|---|
| 1 | Owned | Setup takes under an hour, with no help from the author | The tester times it from fork to first test run. Any question to the author counts as help (it's logged, not hidden) | Under 60 minutes, zero help |
| 2 | Owned | The first test run of every chosen agent passes | Each agent's first Run log row | Result "Done" for every agent |
| 3 | Owned | The tester can switch off an agent without breaking the rest | On day 7 the tester switches off one agent of their choice, using only the README | The other agents' next scheduled runs are "Done", and nothing else had to change |
| 4 | Gated | Nothing outside the hub changed without the tester's approval | On day 7, the tester checks their Gmail drafts and labels against Proposed actions | Every change matches a row they approved; zero exceptions |
| 5 | Gated | The tester can explain what has access to what | Asked on day 1, without notes: what can each agent read, what can it change, what needs their approval | Correct for every agent they set up |
| 6 | Measured | The tester knows what it cost and what it returned | Asked on day 7, without notes: roughly what share of their plan's usage the agents took, and how many wins they confirmed | Both answers match claude.ai Settings → Usage and the Value ledger |
| 7 | Measured | The agents are still running on day 7 | Run log | Every scheduled run on days 1 to 7 logged; every failure has a summary that says why |
| 8 | All three | "I'd keep this" on day 7 | Asked on day 7: keep it running, or switch it off? | "Keep it", unprompted |

All eight must pass. Anything else the tester hits is recorded as a finding, not as a pass or a fail.

## Also recorded (not pass/fail)

- Did agent runs push the tester's plan to its limit?
- Supervision minutes in the first week.
- Every question the tester asked, every point where they got stuck, and every bug, with the release it was found in.

## Afterwards

Results go in this file, unedited, next to these criteria. A failed criterion becomes an issue and, where it's a bug, a regression test.
