# Starter hub schema

The Notion tables the starter agents (Commitments, Inbox tidy, Weather) need: six always, plus Weather if you choose it. The setup prompt creates them with Notion's `create-database` tool, passing each `CREATE TABLE` below as `schema`, with the hub page as parent. Replace `{{owner.name}}` with the owner's first name before creating.

Every agent name an agent writes must already exist as a select option, so adding a new agent later means adding its name to each `Agent` / `From agent` / `Updated by` list.

## Run log
One row per agent run.

```sql
CREATE TABLE (
  "Summary" TITLE,
  "Agent" SELECT('Commitments':red, 'Inbox tidy':gray, 'Weather':blue, 'Setup':default),
  "Result" SELECT('Done':green, 'Partial':yellow, 'Failed':red),
  "Date" DATE,
  "Report link" URL,
  "Published at" DATE COMMENT 'Real time the report or push went out, owner timezone',
  "On time" CHECKBOX COMMENT 'Ticked if it went out by the agent''s target time',
  "Minutes late" NUMBER COMMENT '0 if on time',
  "Useful?" SELECT('Yes':green, 'Partly':yellow, 'No':red) COMMENT 'Owner''s rating; agents never fill this'
)
```

## Proposed actions
Actions an agent wants approved. Nothing happens until the owner sets Status to Approved.

```sql
CREATE TABLE (
  "Action" TITLE COMMENT 'One plain-English sentence the owner understands at a glance',
  "Type" SELECT('Gmail draft':purple, 'Gmail label':gray, 'Calendar event':blue, 'Agent change':pink, 'Other':red),
  "From agent" SELECT('Commitments':red, 'Inbox tidy':gray, 'Setup':default),
  "Status" SELECT('Proposed':yellow, 'Approved':blue, 'Declined':gray, 'Done':green, 'Expired':brown),
  "Proposed on" DATE,
  "Done on" DATE,
  "Details" RICH_TEXT COMMENT 'How to carry it out. For Inbox tidy: the Gmail search, and how to undo'
)
```

## Facts
The current answer to anything agents might flag. One row per fact, updated in place. Rows updated by the owner always win.

```sql
CREATE TABLE (
  "Fact" TITLE,
  "Value" RICH_TEXT COMMENT 'Current answer, one short line',
  "Topic" SELECT('Trip':orange, 'Work':blue, 'Personal':gray, 'Admin':red),
  "Updated by" SELECT('{{owner.name}}':default, 'Commitments':red, 'Inbox tidy':gray, 'Weather':blue),
  "Updated" DATE,
  "Valid until" DATE COMMENT 'After this date the fact no longer matters'
)
```

## Heads-up notes
Short notes one agent leaves for the others (or the owner leaves for all of them).

```sql
CREATE TABLE (
  "Note" TITLE,
  "From agent" SELECT('{{owner.name}}':default, 'Commitments':red, 'Inbox tidy':gray, 'Weather':blue, 'Setup':default),
  "For" MULTI_SELECT('All':gray, 'Commitments':red, 'Inbox tidy':gray, 'Weather':blue),
  "Status" SELECT('Open':yellow, 'Resolved':green),
  "Resolved by" RICH_TEXT,
  "Date" DATE,
  "Expires" DATE
)
```

## Commitments
Promises found in email, both directions.

```sql
CREATE TABLE (
  "Commitment" TITLE COMMENT 'One short line starting with a verb',
  "Direction" SELECT('I owe':blue, 'They owe':orange),
  "Who" RICH_TEXT COMMENT 'First name or organisation only',
  "Due" DATE,
  "Status" SELECT('Open':yellow, 'Done':green, 'Dropped':gray),
  "Found on" DATE,
  "Last checked" DATE,
  "Thread" URL COMMENT 'Gmail thread link',
  "Closed by" RICH_TEXT
)
```

## Value ledger
One row per real win. Only wins the owner marks "Used it" count.

```sql
CREATE TABLE (
  "Win" TITLE,
  "Kind" SELECT('Deadline caught':red, 'Conflict caught':orange, 'Promise kept':blue, 'Prep done':purple, 'Time saved':gray),
  "Agent" SELECT('Commitments':red, 'Inbox tidy':gray, 'Weather':blue),
  "Date" DATE,
  "Minutes saved" NUMBER COMMENT 'From the rate card in the hub Rules',
  "Link" URL,
  "Used?" SELECT('Used it':green, 'Didn''t need it':gray) COMMENT 'Owner only, from Home'
)
```

## Weather (optional)
Forecast and what to wear, one row per place and day, written by the Weather agent from MET Norway (yr.no).

```sql
CREATE TABLE ("Day" TITLE, "Place" RICH_TEXT, "Date" DATE, "Kind" SELECT('Today':blue, 'Tomorrow':gray, 'Trip':orange), "Summary" RICH_TEXT, "Outfit" RICH_TEXT, "Flags" MULTI_SELECT('Ice risk':red, 'Heavy rain':blue, 'Heavy snow':purple, 'Storm':red, 'Windy':yellow, 'Snow':gray), "Low" NUMBER, "High" NUMBER, "Feels" NUMBER, "Rain chance" NUMBER, "Rain mm" NUMBER, "Rain from" RICH_TEXT, "Gust" NUMBER, "Sun" RICH_TEXT, "Periods" RICH_TEXT, "Yr" URL, "Updated" DATE)
```

Create it only if you chose Weather. The other tables already list Weather as an option, so nothing else changes.

## Feed views

After creating each table, add one table view named **Feed** with `create-view` (`database_id` = the new database). Agents and Home read these views, which don't count against Notion's hourly query allowance.

| Table | `configure` |
|---|---|
| Run log | `SORT BY "Date" DESC` |
| Proposed actions | `FILTER "Status" = "Proposed"; SORT BY "Proposed on" DESC` |
| Facts | `SORT BY "Updated" DESC` |
| Heads-up notes | `FILTER "Status" = "Open"; SORT BY "Date" DESC` |
| Commitments | `FILTER "Status" = "Open"; SORT BY "Due" ASC` |
| Value ledger | `SORT BY "Date" DESC` |
| Weather | `SORT BY "Date" ASC` |

Each `create-view` result gives a `view://…` address. Record it in Config under `hub.views`, and record each table's `collection://…` address under `hub.tables`.
