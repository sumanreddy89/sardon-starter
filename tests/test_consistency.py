"""Offline checks that agents, schema, Config, setup and README agree.
Run: python3 -m unittest discover tests"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = sorted(p for p in (ROOT / "agents").glob("*.md") if p.name != "README.md")
SCHEMA = (ROOT / "starter" / "HUB_SCHEMA.md").read_text()
PAGE = (ROOT / "starter" / "HUB_PAGE.md").read_text()
SETUP = (ROOT / "starter" / "SETUP_PROMPT.md").read_text()
README = (ROOT / "README.md").read_text()
AGENTS_README = (ROOT / "agents" / "README.md").read_text()


def front(path):
    text = path.read_text()
    fm = text.split("---", 2)[1]
    out = {}
    for line in fm.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out, text.split("---", 2)[2]


def options(table, column):
    """Option names of a SELECT / MULTI_SELECT column in a schema table."""
    block = SCHEMA.split("## " + table, 1)[1].split("```", 2)[1]
    m = re.search(r'"%s" (?:MULTI_)?SELECT\(([^)]*)\)' % re.escape(column), block)
    assert m, (table, column)
    return set(re.findall(r"'((?:[^']|'')*)':", m.group(1)))


def config_keys():
    yaml = PAGE.split("```yaml", 1)[1].split("```", 1)[0]
    keys, stack = set(), []
    for line in yaml.splitlines():
        m = re.match(r"^( *)(\w+):", line)
        if not m:
            continue
        depth = len(m.group(1)) // 2
        stack = stack[:depth] + [m.group(2)]
        keys.add(".".join(stack))
    return keys


def front_list(path, key):
    """A YAML list (one "  - item" per line) or inline [a, b] from the front matter."""
    fm = path.read_text().split("---", 2)[1]
    m = re.search(r"^%s:[ \t]*\[(.*)\][ \t]*$" % key, fm, re.M)
    if m:
        return [x.strip() for x in m.group(1).split(",") if x.strip()]
    m = re.search(r"^%s:\s*\n((?:  - .*\n)+)" % key, fm, re.M)
    return [l.strip()[2:].strip() for l in m.group(1).splitlines()] if m else None


# Every Gmail tool that changes mail, as listed by the Gmail connector on 19 Nov 2026.
GMAIL_WRITES = {
    "send_message", "reply", "forward", "create_draft", "update_draft", "delete_draft",
    "trash_message", "trash_thread", "untrash_message", "untrash_thread",
    "mark_message_spam", "mark_thread_spam", "unmark_message_spam", "unmark_thread_spam",
    "create_label", "update_label", "delete_label", "label_message", "label_thread",
    "unlabel_message", "unlabel_thread", "update_message_labels",
    "apply_sensitive_message_label", "apply_sensitive_thread_label"}
NOTION_DESTRUCTIVE = {"notion-delete-pages", "notion-delete-databases", "notion-move-pages",
                      "notion-update-data-source"}


NAMES = {p: front(p)[0]["name"] for p in AGENTS}


class Agents(unittest.TestCase):
    def test_every_agent_can_log_its_runs(self):
        for name in NAMES.values():
            self.assertIn(name, options("Run log", "Agent"), name)

    def test_every_agent_can_be_credited_with_a_win(self):
        for name in NAMES.values():
            self.assertIn(name, options("Value ledger", "Agent"), name)

    def test_agents_that_propose_are_allowed_to(self):
        for p, name in NAMES.items():
            if "Proposed actions row" in p.read_text():
                self.assertIn(name, options("Proposed actions", "From agent"), name)

    def test_note_recipients_exist(self):
        allowed = options("Heads-up notes", "For")
        for p in AGENTS:
            for m in re.finditer(r'For \[([^\]]*)\]', p.read_text()):
                for r in re.findall(r'"([^"]+)"', m.group(1)):
                    self.assertIn(r, allowed, (p.name, r))

    def test_fact_topics_agents_read_exist(self):
        topics = options("Facts", "Topic")
        for p in AGENTS:
            for t in re.findall(r'Topic "([^"]+)"', p.read_text()):
                self.assertIn(t, topics, (p.name, t))

    def test_placeholders_are_in_config(self):
        keys = config_keys()
        for p in AGENTS:
            _, body = front(p)
            for ph in re.findall(r"\{\{([a-z_]+(?:\.[a-z_]+)+)\}\}", body):
                self.assertIn(ph, keys, (p.name, ph))

    def test_setup_installs_every_agent(self):
        for p in AGENTS:
            self.assertIn("agents/" + p.name, SETUP, p.name)

    def test_readmes_list_every_agent_and_only_those(self):
        rows = set(re.findall(r"^\| \*\*([^*]+)\*\*", README, re.M))
        self.assertEqual(rows, set(NAMES.values()))
        for p in AGENTS:
            self.assertIn("`%s`" % p.name, AGENTS_README)

    def test_no_full_build_recipients_or_agents(self):
        for p in AGENTS:
            body = p.read_text()
            for gone in ("Morning brief", "morning brief", "Week ahead", "Job search agent", "Agent Hub", "on Home"):
                self.assertNotIn(gone, body, (p.name, gone))


class Permissions(unittest.TestCase):
    """Regression for 19 Nov 2026: the allowed list didn't stop a routine creating a Gmail label."""

    def test_every_agent_names_its_connectors(self):
        for p in AGENTS:
            conns = front_list(p, "connectors")
            self.assertTrue(conns, p.name)
            self.assertIn("Notion", conns, p.name)

    def test_gmail_agents_deny_every_gmail_write_they_dont_need(self):
        for p in AGENTS:
            if "Gmail" not in front_list(p, "connectors"):
                continue
            allowed = {t.split("__")[-1] for t in front_list(p, "tools") if t.startswith("mcp__Gmail__")}
            denied = {t.split("__")[-1] for t in front_list(p, "disallowed_tools") or [] if t.startswith("mcp__Gmail__")}
            self.assertEqual(GMAIL_WRITES - allowed, denied - allowed, p.name)

    def test_send_reply_forward_are_denied_everywhere_gmail_is(self):
        for p in AGENTS:
            if "Gmail" in front_list(p, "connectors"):
                denied = front_list(p, "disallowed_tools")
                for tool in ("send_message", "reply", "forward"):
                    self.assertIn("mcp__Gmail__" + tool, denied, p.name)

    def test_inbox_tidy_can_only_read_gmail(self):
        p = ROOT / "agents" / "inbox-tidy.md"
        allowed = {t.split("__")[-1] for t in front_list(p, "tools") if t.startswith("mcp__Gmail__")}
        self.assertFalse(allowed & GMAIL_WRITES)

    def test_notion_destructive_tools_denied(self):
        for p in AGENTS:
            denied = {t.split("__")[-1] for t in front_list(p, "disallowed_tools") or []}
            self.assertLessEqual(NOTION_DESTRUCTIVE, denied, p.name)

    def test_no_tool_is_both_allowed_and_denied(self):
        for p in AGENTS:
            self.assertFalse(set(front_list(p, "tools")) & set(front_list(p, "disallowed_tools") or []), p.name)

    def test_agents_without_gmail_get_no_gmail_tools(self):
        for p in AGENTS:
            if "Gmail" not in front_list(p, "connectors"):
                self.assertFalse([t for t in front_list(p, "tools") if "Gmail" in t], p.name)

    def test_setup_sets_deny_list_and_connectors(self):
        self.assertIn("disallowed_tools", SETUP)
        self.assertIn("mcp_connections", SETUP)
        self.assertIn("api.met.no", SETUP)

    def test_docs_dont_claim_the_allowed_list_is_a_limit(self):
        threat = (ROOT / "THREAT_MODEL.md").read_text()
        for doc, text in (("README", README), ("THREAT_MODEL", threat), ("agents/README", AGENTS_README)):
            for claim in ("Not in any agent's tool list", "search and read only", "read-only Gmail",
                          "can only call the tools it was given", "No agent has a send tool"):
                self.assertNotIn(claim, text, (doc, claim))


# Config key of each Proposed actions view -> its row label in the schema's Feed views table.
PROPOSAL_VIEWS = {"proposed_actions": "Proposed actions",
                  "proposed_actions_all": "Proposed actions (second view, named **All**)"}
# Statuses an agent can act on, and how its instructions refer to them.
STATUS_WORDS = {"Approved": r"\bApproved\b", "Declined": r"\b[Dd]eclined\b",
                "Expired": r"\b[Ee]xpire"}
ALL_STATUSES = {"Proposed", "Approved", "Declined", "Expired", "Done"}


def view_statuses(label):
    """Statuses a Feed-views-table row shows: its FILTER values, or every status if unfiltered."""
    m = re.search(r"^\| %s \| `([^`]*)` \|$" % re.escape(label), SCHEMA, re.M)
    assert m, label
    shown = set(re.findall(r'"Status" = "(\w+)"', m.group(1)))
    return shown or set(ALL_STATUSES)


class Visibility(unittest.TestCase):
    """Regression for 19 Nov 2026: the Proposed actions Feed shows only Proposed rows, so an
    agent reading it never saw the owner's approvals, and nothing reported an error."""

    def test_agents_read_a_view_that_shows_every_proposal_status_they_act_on(self):
        for p in AGENTS:
            _, body = front(p)
            if "Proposed actions" not in body:
                continue
            needed = {s for s, pat in STATUS_WORDS.items() if re.search(pat, body)}
            visible = set()
            for key, label in PROPOSAL_VIEWS.items():
                if "{{hub.views.%s}}" % key in body:
                    visible |= view_statuses(label)
            self.assertLessEqual(needed, visible, (p.name, needed - visible))

    def test_proposal_views_are_in_config_and_setup(self):
        keys = config_keys()
        for key in PROPOSAL_VIEWS:
            self.assertIn("hub.views." + key, keys)
        self.assertIn('"All" view on\n   Proposed actions', SETUP)

    def test_feed_still_shows_only_waiting_proposals(self):
        # The owner's approval queue stays short; agents use the All view for the rest.
        self.assertEqual(view_statuses(PROPOSAL_VIEWS["proposed_actions"]), {"Proposed"})


class Schedules(unittest.TestCase):
    def test_readme_times_match_crons(self):
        for p, name in NAMES.items():
            cron = front(p)[0]["schedule"].split()[-5:]
            minute, hours = cron[0], cron[1].split(",")
            times = ["%02d:%02d" % (int(h), int(minute)) for h in hours]
            row = next(l for l in README.splitlines() if l.startswith("| **%s**" % name))
            for t in times:
                self.assertIn(t, row, (name, t))
            self.assertEqual(len(times), len(re.findall(r"\b\d\d:\d\d\b", row.split("|")[2])), name)


if __name__ == "__main__":
    unittest.main()
