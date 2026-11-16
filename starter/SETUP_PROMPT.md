# Setup prompt

Paste everything inside the block below into Claude Code, started in your fork of this repo, with the **Notion** and **Gmail** connectors connected in claude.ai. It builds your hub, writes your Config, creates the starter agents and checks they work. It asks before every step that changes something.

```text
Set up the Sardon Steadfast starter for me from this repo. Work step by step, tell me
what each step will do before doing it, and ask before anything that writes to Notion,
creates a scheduled routine or runs one. Never touch Notion pages outside the hub page
you create, and never change anything in my Gmail during setup.

1. Check prerequisites. Confirm the Notion and Gmail connectors work (a harmless read
   each). Confirm this folder is a git checkout of my fork and tell me its GitHub URL.
   Run `python3 -m unittest discover tests` and stop if anything fails.

2. Ask me, in one message: my first name, email, timezone (IANA, e.g. Europe/Berlin),
   home city and country; senders I read and never want tidied (Inbox tidy will leave
   them alone); and my FPL team ID if I want the FPL brief (skip it otherwise).

3. Create a private Notion page titled "Sardon Steadfast" with the content of
   starter/HUB_PAGE.md, filling in my answers. Leave the table and view addresses
   for step 4.

4. Create the six tables in starter/HUB_SCHEMA.md as databases under that page
   (create-database, schema = each CREATE TABLE with {{owner.name}} replaced). Then add
   the "Feed" view to each with create-view and the configure string from the table
   in that file. Write every collection:// and view:// address into the page's Config
   block, and the view:// strings into the "Reading tables" rule, each in a code span
   so Notion doesn't turn it into a link. Fetch the page and show me the Config.

5. Create the scheduled routines with the RemoteTrigger tool (load it via ToolSearch;
   the /schedule skill explains the body shape). One routine each for
   agents/commitments.md and agents/inbox-tidy.md, plus agents/fpl-daily-check-and-brief.md
   only if I gave an FPL team ID. For each, take name, model, tools (allowed_tools)
   and schedule from the file's front matter, replacing {{owner.timezone}} in the cron.
   Sources: my fork's URL (FPL also gets https://github.com/{{fpl.repo}}). Connectors:
   Notion and Gmail. The prompt is the bootstrap prompt in agents/README.md, filled in
   with the agent's name and file, my hub page id and my Run log address. Show me each
   body before creating it.

6. Test, with my go-ahead for each run:
   - Run Inbox tidy once now. Unless it is Sunday 10:30-13:00 my time, the guard must
     return DRY_RUN and nothing in Gmail may change. Check its Run log row and tell me
     what it would have proposed.
   - Run Commitments once now and check its Run log row.
   - FPL: run it once; on most days it should stop quickly with "no brief due".
   For each run, fetch the run log with RemoteTrigger get_run_log and report any
   errors or permission prompts in plain English.

7. Finish with a short summary: what was created (with links), when each agent next
   runs, how to approve a proposal (set Status to Approved in Proposed actions), and
   the kill switch (add a Facts row "Pause inbox tidy" with Updated by = my name).
   Also tell me to protect my fork's main branch on GitHub (Settings > Branches)
   so agents can never push to it.

Write down anything that was confusing or failed in a file called SETUP_NOTES.md in
this folder, so it can be fixed for the next person.
```

## If something goes wrong

- **A routine can't read the repo:** the Claude GitHub app needs access to your fork (github.com/settings/installations).
- **An agent writes "Failed: can't read Config":** fetch the hub page and check the Config block is a single YAML code block with no `{{…}}` left in it.
- **Notion says a select option doesn't exist:** the agent's name is missing from that table's option list (see the note at the top of `HUB_SCHEMA.md`).
