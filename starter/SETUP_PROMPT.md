# Setup prompt

Paste everything inside the block below into Claude Code, started in your fork of this repo, with the **Notion** and **Gmail** connectors connected in claude.ai. It builds your hub, writes your Config, creates the starter agents and checks they work. It asks before every step that changes something. If it stops partway, paste it again: it picks up where it left off.

```text
Set up the Sardon Steadfast starter for me from this repo. Work step by step, tell me
what each step will do before doing it, and ask before anything that writes to Notion,
creates a scheduled routine or runs one. Never touch Notion pages outside the hub page
you create, and never change anything in my Gmail during setup.

0. Resume, don't duplicate. Search Notion for a page titled "Sardon Steadfast" and list
   my routines (RemoteTrigger list) for ones named Commitments, Inbox tidy or Weather.
   If any exist, show me what's there and continue from the first missing piece instead
   of creating a second copy. Never delete anything to start over unless I ask.

1. Check prerequisites. Confirm the Notion and Gmail connectors work (a harmless read
   each). Confirm this folder is a git checkout of my fork, tell me its GitHub URL, and
   note the current commit (git rev-parse HEAD): the routines will be pinned to it.
   Run `python3 -m unittest discover tests` and stop if anything fails.

2. Ask me, in one message: my first name, email, timezone (IANA, e.g. Europe/Berlin),
   home city and country; senders I read and never want tidied (Inbox tidy will leave
   them alone); and whether I want the optional Weather agent.

3. Create a private Notion page titled "Sardon Steadfast" with the content of
   starter/HUB_PAGE.md, filling in my answers, my fork (owner/repo) and the commit
   from step 1. Leave the table and view addresses for step 4.

4. Create the tables in starter/HUB_SCHEMA.md as databases under that page: the six
   always, plus Weather only if I chose it (create-database, schema = each CREATE TABLE
   with {{owner.name}} replaced). Then add the "Feed" view to each with create-view and
   the configure string from the table in that file, plus the second "All" view on
   Proposed actions. Write every collection:// and
   view:// address into the page's Config block (remove the weather lines if I didn't
   choose it), and the view:// strings into the "Reading tables" rule, each in a code
   span so Notion doesn't turn it into a link. Fetch the page and show me the Config.

5. Create the scheduled routines with the RemoteTrigger tool (load it via ToolSearch;
   the /schedule skill explains the body shape). One routine each for
   agents/commitments.md and agents/inbox-tidy.md, plus agents/weather.md only if I
   chose it. For each, take name, model, tools (allowed_tools), disallowed_tools and
   schedule from the file's front matter, replacing {{owner.timezone}} in the cron. Put
   disallowed_tools in job_config.ccr.session_context next to allowed_tools: it is the
   deny list that removes Gmail and Notion tools that change things. The allowed list
   does not limit anything on its own. Repositories: attach NO repository to Commitments
   or Inbox tidy (they download their instructions read-only). Attach my fork to Weather
   only, because it runs tools/weather.py. Connectors: set mcp_connections to exactly the
   front matter's `connectors` (Notion and Gmail for Commitments and Inbox tidy; Notion
   only for Weather). Never leave mcp_connections out: a routine without it gets every
   connector I have. The prompt is the bootstrap prompt in agents/README.md, filled in
   with the agent's name and file, my fork's owner/name, the commit from step 1 as
   {REF}, my hub page id and my Run log address. Make sure my fork is public, since the
   agents download from it. Show me each body before creating it, and afterwards show
   me what the created routine actually has (RemoteTrigger get): its connectors and its
   disallowed_tools. Stop and tell me if either is missing.

5b. Weather only, if I chose it: routines run with limited internet access, and MET
   Norway (api.met.no) isn't allowed by default. Tell me to open the Weather routine on
   claude.ai, open its cloud environment's network settings and add api.met.no to the
   allowed domains. If my home city isn't in tools/places.json, also add
   geocoding-api.open-meteo.com. Wait for me to confirm before step 6.

6. Test, with my go-ahead for each run:
   - Run Inbox tidy once now. Check its Run log row and tell me what it proposed.
     Confirm nothing changed in Gmail.
   - Run Commitments once now and check its Run log row.
   - Weather (if chosen): run it once and check the Weather table has today's and
     tomorrow's rows.
   For each run, fetch the run log with RemoteTrigger get_run_log and report any
   errors or permission prompts in plain English.

7. Finish with a short summary: what was created (with links), when each agent next
   runs, how to approve a proposal (set Status to Approved in Proposed actions), how to
   pause Inbox tidy (a Facts row "Pause inbox tidy" with Updated by = my name), and how
   to switch off any agent (ask Claude Code to disable its routine). Also tell me to
   protect my fork's main branch on GitHub (Settings > Branches, classic rule for main:
   tick "Require a pull request before merging", untick "Require approvals", tick "Do
   not allow bypassing the above settings"). Say plainly what that does and doesn't do:
   it stops direct pushes to main, but agents act with my GitHub identity, so it can't
   stop the Weather routine merging a pull request of its own. That's why the other
   agents' instructions are pinned to a commit.

Write down anything that was confusing or failed in a file called SETUP_NOTES.md in
this folder, so it can be fixed for the next person.
```

## Updating the kit later

The routines follow the commit they were pinned to at setup, so changes to your fork (including any an agent makes) don't reach them until you choose. To update: pull the changes you want into your fork, then ask Claude Code to "update my Sardon routines to the current commit". It changes {REF} in each routine's prompt and the `kit.ref` line in your Config. An update must send each routine's whole job configuration (environment, model, allowed tools, deny list and prompt): a partial update replaces the session settings, which erases the prompt and the deny list.

## If something goes wrong

- **A routine can't read the repo:** the Claude GitHub app needs access to your fork (github.com/settings/installations).
- **Weather writes "Blocked: api.met.no":** the domain isn't in the routine environment's allowed domains (step 5b), or MET Norway refused the request. Add the domain, or set `weather.user_agent` in Config to something with your contact details.
- **An agent writes "Failed: can't read Config":** fetch the hub page and check the Config block is a single YAML code block with no `{{…}}` left in it.
- **Notion says a select option doesn't exist:** the agent's name is missing from that table's option list (see the note at the top of `HUB_SCHEMA.md`).
