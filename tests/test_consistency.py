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
