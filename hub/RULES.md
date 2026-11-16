# Hub rules

Every agent reads this file and the Rules section of the Notion hub page at the start of each run. The hub page's copy is the live one; if they differ, the hub page wins.

- **Allowed without asking:** reading my email and the web; writing to this hub; publishing their own report page; sending push notifications.
- **No agent creates, changes or runs scheduled tasks.** Agents share information only through this hub.
- **Needs my approval:** anything else that touches my accounts, such as an email draft or a label. Agents add these to Proposed actions and stop.
- **Never, even with approval:** sending emails or messages, payments, fantasy-football transfers, bookings, unsubscribing, or deleting anything outside this hub.
- **Reading tables:** read with query-data-sources in mode "view", passing these exact strings as view_url: {{view list, each in a code span, e.g. Run log `view://…` · Proposed actions `view://…` · …}}. Filter rows yourself; page with next_cursor. SQL and "rows" mode share a small hourly allowance, so use them at most once per run.
- **Value ledger:** when a run creates real value, add one row: Win (one short line), Kind, Agent, Date today, Minutes saved from this rate card (Deadline caught 15 · Conflict caught 10 · Promise kept 10 · Prep done 20 · Time saved 5 · Money saved 0), Link. Leave "Used?" empty; only I fill it. Never log routine runs or the same win twice.
- **Privacy:** one short line per entry. No amounts, balances, account numbers, email contents, or other people's details.
- **Facts** hold the current answer to things agents might flag; read Facts before raising anything, and my rows always win.
- **Proposed actions** left untouched for 7 days are Expired.
