"""Every check in `scripts/self_audit.py` PRINTS what it cannot see.

THE DEFECT THIS PINS, and it is the audit's own. `BASIS` has carried a blind
spot for every check since it was written, and `check_every_check_states_its_
basis` has enforced that the entry is non-empty. Both were true on 2026-08-15
and thirty of the thirty-four blind spots had still never been read by anybody,
because the terminal printer emitted the `BLIND TO:` line only for a
`GENERATOR`/`TRANSCRIBED` verdict or one naming a shared symbol. Four printed.
Thirty sat in a dict.

**A guard that checks the declaration EXISTS is not a guard that the
declaration is DISCLOSED**, and this file is the second one. Measured two ways
before the repair and both gave thirty: by the printer gate (4 of 34 emitted a
line), and by scanning what each `Result` itself said (3 of 34 under D34's own
ruling, which threw out `check_record_writers_name_their_drops` because there
the subject of "cannot see" is the audited function and not the instrument --
D34 published "3 of 34, 31 silent" and that measurement reproduces).

WHY THE REPORT IS RENDERED WITH STUBS. A real run of all thirty-four checks
takes 1m47s on this box, which is not a unit test. The contract under test is
the PRINTER's -- given the checks that exist, does every one of them reach the
reader with a blind spot -- so the checks are replaced by stubs that carry the
REAL check names and the real `BASIS` is left alone. A check added to `CHECKS`
without a `BASIS` entry therefore fails this suite whether or not it is slow,
which is the property that has to survive the next person adding a check.

THE MUTATION THAT PROVES IT. `test_a_check_with_no_declaration_is_caught`
appends a stub named after no `BASIS` entry and asserts the render omits its
line -- the same predicate the guard uses, exercised in the failing direction.
Run against the printer as it stood before 2026-08-15, thirty checks are
missing their line and `test_the_report_prints_a_blind_spot_for_every_check`
fails naming all thirty.

DERIVED, NOT TYPED. The measured half of a blind spot is a figure, and L-79
watched typed figures in this same file go stale inside a week. So the tests
below do not assert any count: they assert that the printed number MOVES when
the state it is derived from moves, which is the only property that
distinguishes a measurement from a well-chosen constant.
"""
from __future__ import annotations

import importlib.util
import io
import re
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "self_audit_blind_spots", REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)

_BLIND_LINE = re.compile(r"^\s*BLIND TO:", re.M)


def _stub(name: str, status: str = "PASS"):
    """A check that costs nothing and answers to a real check's name.

    The name is what the printer looks `BASIS` up by, so a stub is a faithful
    stand-in for the one question this suite asks.
    """
    def check() -> "sa.Result":
        return sa.Result(name.replace("check_", "").replace("_", " "), status,
                         "stub verdict", [])
    check.__name__ = name
    return check


def _render(names, argv=("self_audit",), status="PASS") -> str:
    """The human report, as `main()` writes it, for the given check names."""
    original_checks, original_argv = sa.CHECKS, sys.argv
    sa.CHECKS = tuple(_stub(n, status) for n in names)
    sys.argv = list(argv)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            sa.main()
    finally:
        sa.CHECKS = original_checks
        sys.argv = original_argv
    return buffer.getvalue()


def _blind_lines(report: str) -> list[str]:
    return [ln for ln in report.splitlines() if ln.strip().startswith("BLIND TO:")]


class EveryCheckDisclosesWhatItCannotSee(unittest.TestCase):
    """The guard proper: no check ships without a PRINTED blind spot."""

    def test_the_report_prints_a_blind_spot_for_every_check(self):
        """THIS IS THE GUARD. One printed `BLIND TO:` line per check.

        Not "most checks", and not "the ones that cannot fail". Before
        2026-08-15 this assertion failed with thirty names in the message.
        """
        names = [c.__name__ for c in sa.CHECKS]
        report = _render(names)
        silent = [n for n in names
                  if not _BLIND_LINE.search(_section(report, n))]
        self.assertEqual(
            [], silent,
            f"{len(silent)} of {len(names)} check(s) reach the reader with no "
            f"statement of what they cannot see: {', '.join(silent)}")
        self.assertEqual(
            len(names), len(_blind_lines(report)),
            "the number of printed blind spots must equal the number of "
            "checks; a shared or duplicated line is not a per-check "
            "disclosure")

    def test_a_check_with_no_declaration_is_caught(self):
        """THE MUTATION, in-suite: a declaration-less check must go silent.

        This is the failing direction of the assertion above. If this test
        ever passes trivially -- because the printer grew a fallback that
        prints something for an undeclared check -- the guard above has
        stopped discriminating and both tests must be reread together.
        """
        invented = "check_a_name_that_no_BASIS_entry_will_ever_hold"
        self.assertNotIn(invented, sa.BASIS)
        names = [c.__name__ for c in sa.CHECKS] + [invented]
        report = _render(names)
        self.assertFalse(
            _BLIND_LINE.search(_section(report, invented)),
            "an undeclared check printed a blind spot, so the guard above "
            "cannot tell a declared check from an undeclared one")
        self.assertEqual(
            len(names) - 1, len(_blind_lines(report)),
            "exactly the declared checks should print; the mutant must be "
            "the only silent one")

    def test_the_quiet_report_also_discloses(self):
        """`--quiet` hides passes, not blind spots, for what it does show.

        A reader who runs `--quiet` is reading a shorter report, not a less
        honest one. Every check it PRINTS must still say what it cannot see.
        """
        names = [c.__name__ for c in sa.CHECKS]
        report = _render(names, argv=("self_audit", "--quiet"), status=sa.WARN)
        shown = [n for n in names if _section(report, n).strip()]
        self.assertTrue(shown, "the quiet report showed no check at all")
        for name in shown:
            self.assertTrue(
                _BLIND_LINE.search(_section(report, name)),
                f"{name} is shown by --quiet with no blind spot")

    def test_the_json_surface_carries_the_same_disclosure(self):
        """A hook reading `--json` must not see a different set of blind spots.

        Until 2026-08-15 the JSON was the ONLY consumer that saw all
        thirty-four, which is how thirty stayed unread: the machine surface was
        complete and the human one was not. They must not now diverge in the
        other direction.
        """
        import json
        names = [c.__name__ for c in sa.CHECKS]
        rows = json.loads(_render(names, argv=("self_audit", "--json")))
        self.assertEqual(len(names), len(rows))
        for row in rows:
            self.assertTrue(
                (row.get("blind_to") or "").strip(),
                f"{row.get('name')} carries no blind_to in the JSON")


class TheMeasuredHalfIsMeasured(unittest.TestCase):
    """A blind spot that states a reach states a figure, and figures rot."""

    def test_the_corpus_reach_moves_when_the_corpus_moves(self):
        """The derived text must be a function of state, not a constant.

        The assertion is deliberately not "it says 50 PDFs". A test that pins
        the number is a second copy of the number, and this lab has been
        burned by exactly that. What is pinned is that the number MOVES.
        """
        sa._corpus_reach.cache_clear()
        try:
            real = sa._blind_corpus()
            fake = dict(sa._corpus_reach())
            fake["pdf"] += 1000
            fake["act_transcripts"] += 7
            original = sa._corpus_reach
            sa._corpus_reach = lambda: fake
            try:
                moved = sa._blind_corpus()
            finally:
                sa._corpus_reach = original
        finally:
            sa._corpus_reach.cache_clear()
        self.assertNotEqual(
            real, moved,
            "the corpus blind spot did not move when the corpus did, so it is "
            "typed rather than measured")
        self.assertIn(f"{fake['pdf']} PDF(s)", moved)
        self.assertIn(f"{fake['act_transcripts']} act transcript(s)", moved)

    def test_the_corpus_reach_names_the_cap_it_actually_enforces(self):
        """The stated cap is the constant the sweeps use, not a second copy."""
        self.assertIn(f"{sa._RANK_MAX_BYTES:,}", sa._blind_corpus())

    def test_the_placement_binding_derives_who_it_cannot_fault(self):
        """Whom rule A cannot reach is read off the two boards, not listed.

        D89's finding, disclosed by the instrument itself: the identity
        binding comes from the frozen scoring pin, the standing comes from the
        live record, and anybody in the second and not the first is
        unfaultable. That set is computed, so it empties itself the day the
        pin is repointed.
        """
        text = sa._blind_placement_binding()
        board, _ = sa._published_board()
        ranking = sa._ranking_board()
        live = dict(ranking[0]) if isinstance(ranking, tuple) else dict(ranking or {})
        for who in live:
            if who not in board:
                self.assertIn(who, text,
                              f"{who} is on the live board, outside the "
                              f"identity binding, and unnamed in the blind "
                              f"spot that exists to say so")
        self.assertIn("NO ARITHMETIC predicate", text)

    def test_a_deriver_that_raises_does_not_take_the_report_down(self):
        """An instrument that cannot state its reach says so, and continues.

        The failure mode this forbids is the one that matters: a blind-spot
        line that vanishes on error reads, to every consumer, exactly like a
        check with nothing to disclose.
        """
        def explode():
            raise RuntimeError("no reach")
        name = sa.CHECKS[0].__name__
        original = sa.BLIND_DERIVED.get(name)
        sa.BLIND_DERIVED[name] = explode
        try:
            measured = sa._derived_blind_spot(name)
        finally:
            if original is None:
                sa.BLIND_DERIVED.pop(name, None)
            else:
                sa.BLIND_DERIVED[name] = original
        self.assertIsNotNone(measured)
        self.assertIn("could not be measured", measured)
        self.assertIn("it is not thereby smaller", measured)

    def test_every_derived_entry_names_a_live_check(self):
        """A deriver for a check that no longer exists is a stale disclosure."""
        names = {c.__name__ for c in sa.CHECKS}
        stale = sorted(set(sa.BLIND_DERIVED) - names)
        self.assertEqual([], stale,
                         f"BLIND_DERIVED names checks that are gone: {stale}")


class TheDeclarationsSayWhatIsInvisible(unittest.TestCase):
    """A blind spot names a class of defect, not merely a frame."""

    def test_every_check_declares_a_non_empty_blind_spot(self):
        names = {c.__name__ for c in sa.CHECKS}
        missing = sorted(n for n in names
                         if not (sa.BASIS.get(n) or (None, None, "", None))[2])
        self.assertEqual([], missing,
                         f"check(s) with no declared blind spot: {missing}")


def _section(report: str, name: str) -> str:
    """The report lines belonging to one check, by its verdict line.

    The printer writes the check's Result name rather than the function name,
    so the section is located by the derived display name and bounded by the
    next verdict line.
    """
    display = name.replace("check_", "").replace("_", " ")
    lines = report.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^\[[A-Z]+\s*\]\s+" + re.escape(display) + r"\s", line):
            start = index
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^\[[A-Z]+\s*\]", lines[index]) or \
                lines[index].startswith("="):
            end = index
            break
    return "\n".join(lines[start:end])


if __name__ == "__main__":
    unittest.main()
