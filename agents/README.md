# Agents

One file per scheduled agent. The YAML front matter is metadata (schedule, model, tools, routine id); the body is the agent's instructions.

## Running an agent from this repo

Agents with `runs_from: repo` in their front matter don't keep their instructions inside the routine. Their routine has this repo attached as a source and a short bootstrap prompt:

1. Read `agents/<name>.md` (skip the front matter) and `hub/RULES.md`.
2. Fetch the private Notion hub page and read its **Config** section.
3. Replace every `{{placeholder}}` in the instructions with the matching Config value.
4. Follow the instructions. Never edit or commit to the repo.

So merging a change to `main` changes the agent's behaviour from its next run. Personal values never enter the repo; they live in the hub page's Config section (and in your local `config/owner.yaml`).

Agents without `runs_from: repo` still use the copy of their instructions stored in the routine. Their file here is a snapshot.

## Bootstrap prompt

```
You are the {AGENT NAME} agent of Sardon Steadfast. Your instructions live in the attached
sardon-steadfast repo. Read agents/{file}.md (ignore its YAML front matter) and hub/RULES.md.
Then fetch the Notion hub page {hub page id} and read its "Config" section: it gives the value
of every {{placeholder}} in your instructions. Substitute them, then follow the instructions
exactly. If you can't read the repo file or the Config section, don't improvise: add a Run log
row ({run log data source}) with Agent "{AGENT NAME}", Result "Failed" and the reason, send a
push saying so, and stop. Never edit, commit to or push to the repo.
```
