# First outside test: success criteria

Written on 17 Nov 2026, **before** the test, so the result can't be argued either way afterwards. The tester uses the tagged release `v0.1` and their own Claude, Notion and Gmail accounts.

## Pass or fail

| # | Criterion | How it's checked | Pass |
|---|---|---|---|
| 1 | Setup takes under an hour, with no help from the author | The tester times it from fork to first test run. Any question to the author counts as help (it's logged, not hidden) | Under 60 minutes, zero help |
| 2 | The first test run of every chosen agent passes | Each agent's first Run log row | Result "Done" for every agent |
| 3 | The tester can explain what has access to what | Asked on day 1, without notes: what can each agent read, what can it change, what needs their approval | Correct for every agent they set up |
| 4 | The agents are still running on day 7 | Run log | Every scheduled run on days 1 to 7 logged; failures explained in the health check or a report |
| 5 | "I'd keep this" on day 7 | Asked on day 7: keep it running, or switch it off? | "Keep it", unprompted |

All five must pass. Anything else the tester hits is recorded as a finding, not as a pass or a fail.

## Also recorded (not pass/fail)

- Usage: did agent runs push the tester's plan to its limit? (Checked in claude.ai Settings → Usage.)
- Confirmed wins and supervision minutes in the first week.
- Every question the tester asked, every point where they got stuck, and every bug, with the release it was found in.

## Afterwards

Results go in this file, unedited, next to these criteria. A failed criterion becomes an issue and, where it's a bug, a regression test.
