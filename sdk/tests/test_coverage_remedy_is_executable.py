"""The printed remedies of `scripts/check_proposal_surface_coverage.py` are RUN.

WHY THIS IS NOT A TEST OF THE CHECK (docket D261)
=================================================
A test that called the check and asserted it exits non-zero would have passed
throughout the entire period the LOST remedy was wrong. The check was never the
broken part. **The failing case is the REMEDY.**

Until 2026-08-16 the LOST class printed *"move it into docket.json via
set_status"*. `set_status` iterates `load_docket()` and returns `None` for an id
it does not find, and LOST means precisely that the docket holds no record of
the id -- so the printed instruction was a silent no-op on EVERY id the class
reports. An operator following it literally got no exception, no message and no
change, then saw the same ids next run and concluded the check was broken.

WHAT THESE TESTS DO INSTEAD OF GREPPING
=======================================
Grepping the remedy string for the word `refresh_docket` would be the
recitation defect: it asserts that a sentence contains a token, which is what
the old sentence did too, with a different token. So each test here:

  1. builds a REAL agenda directory in which the fault genuinely holds, and
     asserts `classify` puts the id in that class -- so the fixture cannot go
     vacuous;
  2. reads the remedy string the check would PRINT, and extracts the call it
     names, without knowing in advance which call that is;
  3. EXECUTES that call against the fixture; and
  4. re-reads the files and re-classifies, asserting the fault has CLEARED.

Step 2 is deliberately generic. If the remedy string is ever changed back to
`set_status`, step 3 executes `set_status`, the id stays absent from the
docket, and step 4 fails. That is the pin.

NOTHING HERE TOUCHES THE REPOSITORY'S OWN AGENDA. Every fixture is a temporary
directory and the module is redirected at it with `CERTONOMOUS_AGENDA_DIR`,
which `agenda._agenda_dir()` reads at CALL time. The real `docket.json` is
never opened for writing, and D219 reserves ratification of the live seven to
the owner in writing.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHECK = REPO / "scripts" / "check_proposal_surface_coverage.py"


def load_check():
    """Load the check by explicit path -- `resolve()` follows symlinks, so a
    harness mirror must be able to substitute the file it is testing."""
    target = Path(os.environ.get("COVERAGE_CHECK_PATH", CHECK))
    spec = importlib.util.spec_from_file_location("_coverage_check", target)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHK = load_check()

sys.path.insert(0, str(REPO / "sdk"))
from chief_engineer import agenda as A  # noqa: E402


#: A name written as a CALL, e.g. "`refresh_docket()`" or "set_status(id, ...)".
_CALLED = re.compile(r"`?(\w+)`?\s*\(")
#: Any bare identifier, for prose that names a function without parentheses.
_WORD = re.compile(r"\w+")


def call_named_by(remedy: str) -> str | None:
    """The function a printed remedy tells the operator to run, or None.

    THIS IS DELIBERATELY GENEROUS ABOUT PROSE, and the reason is the defect
    being pinned. The historical LOST remedy read *"move it into docket.json
    via set_status"* -- no backticks and no parentheses. An extractor that only
    recognised `name(` would fail on that string for the wrong reason: it would
    report "this remedy names no callable" instead of executing `set_status`
    and discovering that the id is still LOST. The pin has to catch the
    HISTORICAL string BEHAVIOURALLY, so a bare mention counts.

    Preference order, and it matters: a name written as a CALL wins over a bare
    mention, because the repaired LOST remedy names `refresh_docket()` as the
    action and `set_status` only to warn against it.

    Returns None when the remedy names no function at all -- BLOCKED, SHADOWED
    and ORPHANED are human instructions and are out of scope here.
    """
    for match in _CALLED.finditer(remedy):
        if hasattr(A, match.group(1)):
            return match.group(1)
    for match in _WORD.finditer(remedy):
        if match.group(0).islower() and "_" in match.group(0) \
                and callable(getattr(A, match.group(0), None)):
            return match.group(0)
    return None


class AgendaFixture:
    """A real agenda directory the module can be pointed at."""

    def __init__(self, docket_records, inbox_records):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        (self.path / "proposals").mkdir()
        (self.path / "docket.json").write_text(
            json.dumps({"generated_at": "2026-01-01T00:00:00Z",
                        "proposals": docket_records}, indent=1))
        for record in inbox_records:
            (self.path / "proposals" / f"{record['id']}.json").write_text(
                json.dumps(record, indent=1))
        self._prev = os.environ.get("CERTONOMOUS_AGENDA_DIR")
        os.environ["CERTONOMOUS_AGENDA_DIR"] = str(self.path)

    def classify_now(self) -> dict:
        """Re-read both surfaces from disk and classify. No caching."""
        docket = CHK.load_docket(self.path / "docket.json")
        inbox = CHK.load_inbox(self.path / "proposals")
        return CHK.classify(inbox, docket, set(), {})

    def class_of(self, item_id: str) -> str | None:
        for row in self.classify_now()["rows"]:
            if row["id"] == item_id:
                return row["class"]
        return None

    def close(self):
        if self._prev is None:
            os.environ.pop("CERTONOMOUS_AGENDA_DIR", None)
        else:
            os.environ["CERTONOMOUS_AGENDA_DIR"] = self._prev
        self.tmp.cleanup()


def a_file(item_id, status, **extra):
    record = {
        "id": item_id,
        "objective": f"an objective for {item_id} long enough to be accepted "
                     f"by the style rails of the inbox reader",
        "rationale": "a rationale",
        "est_core_min": 1.0,
        "expected_knowledge_gain": "something",
        "source_kind": "measurement",
        "status": status,
        "created_at": "2026-01-01T00:00:00Z",
    }
    record.update(extra)
    return record


class TheLostRemedyActuallyWorks(unittest.TestCase):
    """Follow the LOST remedy literally; the fault must clear."""

    def setUp(self):
        self.item = "a-decided-file-the-docket-never-heard-of"
        self.fx = AgendaFixture(
            docket_records=[],
            inbox_records=[a_file(self.item, "done", outcome="what it found")],
        )
        self.addCleanup(self.fx.close)

    def test_the_fixture_is_genuinely_lost(self):
        """If this stops holding, every assertion below is vacuous."""
        self.assertEqual(self.fx.class_of(self.item), "LOST")

    def test_following_the_printed_remedy_clears_the_fault(self):
        """THE PIN. The remedy is executed, not read."""
        remedy = CHK.FAULTS["LOST"]
        name = call_named_by(remedy)
        self.assertIsNotNone(
            name, f"the LOST remedy names no runnable call at all: {remedy!r}")
        func = getattr(A, name, None)
        self.assertIsNotNone(func, f"the remedy names {name!r}, which "
                                   f"chief_engineer.agenda does not define")

        required = [p for p in inspect.signature(func).parameters.values()
                    if p.default is inspect.Parameter.empty
                    and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        if required:
            func(self.item, "done", outcome="what it found")
        else:
            func()

        self.assertNotEqual(
            self.fx.class_of(self.item), "LOST",
            f"the printed LOST remedy names {name}(), it was executed, and the "
            f"id is STILL LOST -- the remedy is a no-op on the class it is "
            f"printed for")

    def test_set_status_specifically_is_a_no_op_on_a_lost_id(self):
        """The defect itself, pinned so it cannot be reintroduced quietly."""
        before = (self.fx.path / "docket.json").read_bytes()
        self.assertIsNone(A.set_status(self.item, "done", outcome="x"))
        self.assertEqual((self.fx.path / "docket.json").read_bytes(), before)
        self.assertEqual(self.fx.class_of(self.item), "LOST")

    def test_the_lost_remedy_does_not_name_set_status(self):
        """Cheap and redundant on purpose: it names the defect in the report."""
        self.assertNotEqual(call_named_by(CHK.FAULTS["LOST"]), "set_status")


class TheUnabsorbedRemedyActuallyWorks(unittest.TestCase):
    """The opposite call. UNABSORBED ids ARE on the docket."""

    def setUp(self):
        self.item = "an-item-whose-evidence-is-only-in-an-artifact"
        record = a_file(self.item, "approved")
        self.fx = AgendaFixture(docket_records=[dict(record)],
                                inbox_records=[dict(record)])
        self.addCleanup(self.fx.close)

    def _unabsorbed_ids(self):
        docket = CHK.load_docket(self.fx.path / "docket.json")
        inbox = CHK.load_inbox(self.fx.path / "proposals")
        named = {self.item: ["demo-output/somewhere/result.json"]}
        return {u["id"] for u in
                CHK.classify(inbox, docket, set(), named)["unabsorbed"]}

    def test_the_fixture_is_genuinely_unabsorbed(self):
        self.assertIn(self.item, self._unabsorbed_ids())

    def test_following_the_printed_remedy_clears_the_fault(self):
        name = call_named_by(CHK.FAULTS["UNABSORBED"])
        self.assertIsNotNone(name, "the UNABSORBED remedy names no call")
        func = getattr(A, name, None)
        self.assertIsNotNone(func)
        func(self.item, "done", outcome="what the artifact showed")
        self.assertNotIn(
            self.item, self._unabsorbed_ids(),
            f"the printed UNABSORBED remedy names {name}(), it was executed, "
            f"and the id is STILL unabsorbed")

    def test_a_refresh_cannot_clear_this_class(self):
        """Why the two classes take different calls, asserted not assumed."""
        A.refresh_docket()
        self.assertIn(self.item, self._unabsorbed_ids())


class EveryPrintedRemedyNamesSomethingReal(unittest.TestCase):
    """A remedy naming a callable must name one that exists."""

    def test_every_named_call_resolves_on_the_agenda_module(self):
        """Scanned RAW, not through `call_named_by`.

        `call_named_by` filters candidates by `hasattr(A, ...)`, so a remedy
        naming a function that does NOT exist comes back as None and reads as
        prose. Routing this assertion through it made it unable to fail --
        measured: mutant M2 plants `merge_inbox_into_docket()` and this test
        stayed green. A test that cannot fail is worse than no test, so the
        scan here is deliberately unfiltered.
        """
        for klass, remedy in CHK.FAULTS.items():
            for match in re.finditer(r"`?([a-z_]{4,})`?\s*\(", remedy):
                name = match.group(1)
                self.assertTrue(
                    callable(getattr(A, name, None)),
                    f"{klass}'s remedy tells the operator to run {name}(), "
                    f"which chief_engineer.agenda does not define")


if __name__ == "__main__":
    unittest.main()
