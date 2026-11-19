# Hub page template

The setup prompt creates a private Notion page called **Sardon Steadfast** with this content, replacing every `{{…}}`. Agents fetch this page at the start of every run: the Rules section is their contract, and the Config section fills the `{{placeholders}}` in their instruction files.

---

Where my scheduled Claude agents log their runs, leave notes for each other, propose actions and get measured. Nothing outside this hub changes without my approval.

## Rules

- **Allowed without asking:** reading my email and the web; writing to this hub; publishing their own report page; sending push notifications.
- **No agent creates, changes or runs scheduled tasks.** Agents share information only through this hub.
- **Needs my approval:** anything else that touches my accounts, such as an email draft or a label. Agents add these to Proposed actions and stop.
- **Never, even with approval:** sending emails or messages, payments, fantasy-football transfers, bookings, unsubscribing, or deleting anything outside this hub.
- **Reading tables:** read with query-data-sources in mode "view", passing these exact strings as view_url: {{view list, each in a code span, e.g. Run log `view://…` · Proposed actions `view://…` · Proposed actions (All) `view://…` · …}}. The Proposed actions Feed shows only rows still Proposed; to find Approved, Declined or Expired rows, read Proposed actions (All). Filter rows yourself; page with next_cursor. SQL and "rows" mode share a small hourly allowance, so use them at most once per run.
- **Value ledger:** when a run creates real value, add one row: Win (one short line), Kind, Agent, Date today, Minutes saved from this rate card (Deadline caught 15 · Conflict caught 10 · Promise kept 10 · Prep done 20 · Time saved 5). These minutes are an estimate from a fixed rate card, not measured time, Link. Leave "Used?" empty; only I fill it. Never log routine runs or the same win twice.
- **Privacy:** one short line per entry. No amounts, balances, account numbers, email contents, or other people's details.
- **Facts** hold the current answer to things agents might flag; read Facts before raising anything, and my rows always win.
- **Proposed actions** left untouched for 7 days are Expired.

## Config

```yaml
owner:
  name: {{owner.name}}
  email: {{owner.email}}
  timezone: {{owner.timezone}}
  home_city: {{owner.home_city}}
  home_country: {{owner.home_country}}
kit:
  fork: {{owner/repo of the fork}}
  ref: {{commit the routines are pinned to}}
inbox_tidy:
  keep_senders: "{{senders the owner reads and never wants tidied, comma-separated}}"
weather:
  user_agent: ""
hub:
  page_id: {{this page's id}}
  tables:
    run_log: collection://…
    proposed_actions: collection://…
    facts: collection://…
    notes: collection://…
    commitments: collection://…
    value_ledger: collection://…
    weather: collection://… (only if Weather was chosen)
  views:
    run_log: view://…
    proposed_actions: view://…
    proposed_actions_all: view://…
    facts: view://…
    notes: view://…
    commitments: view://…
    value_ledger: view://…
    weather: view://… (only if Weather was chosen)
```
