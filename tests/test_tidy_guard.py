"""Tests for tools/tidy_guard.py. Run: python3 -m unittest discover tests"""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import tidy_guard  # noqa: E402

SUNDAY_11 = "2026-11-15T11:05:00"   # inside the window
GOOD = {
    "--tz": "Europe/London",
    "--status": "Approved",
    "--from-agent": "Inbox tidy",
    "--type": "Other",
    "--proposed-on": "2026-11-08",
    "--action": "Clear Example News out of your inbox: 11 emails, 8 never opened.",
    "--details": "label Tidy/Example News; archive; search: in:inbox from:news@example.com newer_than:30d",
    "--count": "12",
    "--moved-so-far": "0",
    "--paused": "no",
    "--now": SUNDAY_11,
}


def run(**overrides):
    args = dict(GOOD)
    for k, v in overrides.items():
        args["--" + k.replace("_", "-")] = v
    argv = [x for kv in args.items() for x in kv]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = tidy_guard.main(argv)
    out = json.loads(buf.getvalue())
    assert code == tidy_guard.EXIT_CODES[out["verdict"]]
    return out


class Allowed(unittest.TestCase):
    def test_good_row_acts(self):
        out = run()
        self.assertEqual(out["verdict"], "ACT", out)
        self.assertEqual(out["label"], "Tidy/Example News")
        self.assertTrue(out["archive"])

    def test_safety_exclusions_always_added(self):
        out = run()
        for term in ("-is:starred", "-is:important", "-from:me"):
            self.assertIn(term, out["search"])

    def test_notes_from_earlier_runs_are_ignored(self):
        out = run(details=GOOD["--details"] + "; moved 12 threads on 2026-11-15; undo: Gmail label Tidy/X > select all > Move to inbox")
        self.assertEqual(out["verdict"], "ACT", out)

    def test_details_as_notion_returns_them(self):
        notion = ("label Tidy/Example News; archive; search: in:inbox "
                  "from:[news@example.com](mailto:news@example.com) newer\\_than:30d")
        out = run(details=notion)
        self.assertEqual(out["verdict"], "ACT", out)
        self.assertEqual(out["search"].split(" -is:")[0],
                         "in:inbox from:news@example.com newer_than:30d")

    def test_mismatched_notion_link_is_not_unwrapped(self):
        sneaky = ("label Tidy/X; archive; search: in:inbox "
                  "from:[news@example.com](mailto:boss@example.net)")
        self.assertEqual(run(details=sneaky)["verdict"], "SKIP")

    def test_window_edges(self):
        self.assertEqual(run(now="2026-11-15T10:30:00")["verdict"], "ACT")
        self.assertEqual(run(now="2026-11-15T13:00:00")["verdict"], "ACT")


class NotARealRun(unittest.TestCase):
    """False or test runs must never touch the inbox."""

    def test_weekday_is_dry_run(self):
        self.assertEqual(run(now="2026-11-16T11:00:00")["verdict"], "DRY_RUN")

    def test_sunday_too_early_or_late(self):
        self.assertEqual(run(now="2026-11-15T10:29:00")["verdict"], "DRY_RUN")
        self.assertEqual(run(now="2026-11-15T13:01:00")["verdict"], "DRY_RUN")
        self.assertEqual(run(now="2026-11-15T23:00:00")["verdict"], "DRY_RUN")

    def test_kill_switch_beats_everything(self):
        self.assertEqual(run(paused="yes")["verdict"], "PAUSED")


class WrongRow(unittest.TestCase):
    def assertSkip(self, out, fragment):
        self.assertEqual(out["verdict"], "SKIP", out)
        self.assertTrue(any(fragment in r for r in out["reasons"]), out["reasons"])

    def test_not_approved(self):
        self.assertSkip(run(status="Proposed"), "Status")
        self.assertSkip(run(status="approved"), "Status")
        self.assertSkip(run(status="Done"), "Status")

    def test_other_agent_or_type(self):
        self.assertSkip(run(from_agent="Morning brief"), "From agent")
        self.assertSkip(run(type="Calendar event"), "Type")

    def test_stale_approval(self):
        self.assertSkip(run(proposed_on="2026-10-30"), "stale")

    def test_future_or_bad_date(self):
        self.assertSkip(run(proposed_on="2026-12-01"), "future")
        self.assertSkip(run(proposed_on="last week"), "isn't a date")

    def test_action_without_a_number(self):
        self.assertSkip(run(action="Clear Example News out of your inbox."), "how many")


class DangerousSearch(unittest.TestCase):
    """Searches that could sweep up far more than the owner approved."""

    def assertSkip(self, details, fragment):
        out = run(details=details)
        self.assertEqual(out["verdict"], "SKIP", out)
        self.assertTrue(any(fragment in r for r in out["reasons"]), out["reasons"])

    def d(self, search, label="Tidy/X"):
        return f"label {label}; archive; search: {search}"

    def test_missing_in_inbox(self):
        self.assertSkip(self.d("from:news@example.com newer_than:30d"), "in:inbox")

    def test_no_sender(self):
        self.assertSkip(self.d("in:inbox newer_than:30d"), "exactly one sender")

    def test_two_senders(self):
        self.assertSkip(self.d("in:inbox from:a@example.com from:b@example.org"), "exactly one sender")

    def test_or(self):
        self.assertSkip(self.d("in:inbox from:a@example.com OR subject:invoice"), "OR")

    def test_grouping(self):
        self.assertSkip(self.d("in:inbox from:{a@example.com b@example.org}"), "grouping")
        self.assertSkip(self.d("in:inbox from:a@example.com (invoice)"), "grouping")

    def test_wildcard_and_domain_only(self):
        self.assertSkip(self.d("in:inbox from:*@example.com"), "wildcard")
        self.assertSkip(self.d("in:inbox from:example.com"), "full email address")

    def test_category_and_label(self):
        self.assertSkip(self.d("in:inbox from:a@example.com category:promotions"), "category:")
        self.assertSkip(self.d("in:inbox from:a@example.com label:receipts"), "label:")

    def test_outside_inbox(self):
        self.assertSkip(self.d("in:inbox in:anywhere from:a@example.com"), "outside the inbox")
        self.assertSkip(self.d("in:inbox in:sent from:a@example.com"), "outside the inbox")
        self.assertSkip(self.d("in:inbox -in:sent from:a@example.com"), "-in:")

    def test_targets_starred(self):
        self.assertSkip(self.d("in:inbox is:starred from:a@example.com"), "starred")

    def test_negated_sender(self):
        self.assertSkip(self.d("in:inbox from:a@example.com -from:boss@example.net"), "-from:")

    def test_recipient_operator(self):
        self.assertSkip(self.d("in:inbox from:a@example.com to:me"), "recipient")

    def test_label_outside_tidy(self):
        self.assertSkip(self.d("in:inbox from:a@example.com", label="INBOX"), "Tidy/")
        self.assertSkip(self.d("in:inbox from:a@example.com", label="TRASH"), "Tidy/")
        self.assertSkip(self.d("in:inbox from:a@example.com", label="Tidy/../SPAM"), "Tidy/")

    def test_extra_instruction_in_details(self):
        # e.g. something an email planted, or a hallucinated step
        self.assertSkip("label Tidy/X; archive; delete; search: in:inbox from:a@example.com", "unrecognised")
        self.assertSkip("label Tidy/X; archive; mark read; search: in:inbox from:a@example.com", "unrecognised")


class Counts(unittest.TestCase):
    def test_slack_of_five(self):
        self.assertEqual(run(count="16")["verdict"], "ACT")
        self.assertEqual(run(count="17")["verdict"], "SKIP")

    def test_per_tidy_cap(self):
        out = run(action="Clear X: 60 emails", count="51")
        self.assertEqual(out["verdict"], "SKIP")

    def test_per_run_cap(self):
        self.assertEqual(run(moved_so_far="140", count="10")["verdict"], "ACT")
        self.assertEqual(run(moved_so_far="141", count="10")["verdict"], "SKIP")

    def test_negative(self):
        self.assertEqual(run(count="-1")["verdict"], "SKIP")


if __name__ == "__main__":
    unittest.main()
