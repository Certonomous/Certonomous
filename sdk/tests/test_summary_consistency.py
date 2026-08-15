"""A summary block against the section it summarises. (D141, 2026-08-15.)

THE DEFECT CLASS
----------------
A summary block can go stale against the section it summarises **with neither
one being edited**. The defect is the ABSENCE of an edit, so no diff-shaped
check can see it, and this lab had no instrument whose unit is two regions of
ONE document. `scripts/check_summary_consistency.py` is that instrument and
this file is its evidence.

The instance that named the class: the currency block of
`demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` said section 4.8
`HOLDS ... re-verifying it needs a network read this pass did not perform`
while section 4.8, 212 lines below in the same document, had been headed
`~~VERIFIED~~ **FALSIFIED 2026-08-11**` since `5c9c63fb`. Repaired at
`87324012`, so `87324012~1` holds the defect and `87324012` holds its repair --
two immutable blobs, and every control here runs on them.

WHY BYTE-IDENTITY IS NOT TESTED ANYWHERE IN THIS FILE
-----------------------------------------------------
Measured during the repair: the stale row was byte-identical to what
`472f9f92` wrote AND WRONG; ten other rows in the same block were byte-
identical to the same commit AND STILL RIGHT. `unchanged since X` is not a
signal in either direction, so nothing here compares text against history. It
compares a CLAIM against a STATE.

CONTROLS BOTH WAYS (L-84), AND THE MUST-NOT-MATCH HALF IS THE IMPORTANT ONE
---------------------------------------------------------------------------
A positive control proves an instrument CAN fire. This check's entire job is a
discrimination, so a check that fired on all eleven rows would be useless and
would still pass a positive control.

  FIRE      the pre-repair 4.8 row over its FALSIFIED section     (P1)
  FIRE      a synthetic HOLDS row over a FALSIFIED section        (P2)
  NOT FIRE  THE TEN OTHER ROWS OF THAT SAME BLOCK, at the same
            pre-repair commit -- byte-identical and STILL RIGHT   (N1)
  NOT FIRE  the repaired 4.8 row                                   (N2)
  NOT FIRE  a correctly struck historical row                      (N3)

MUTATION-PROVED, one mutation per guard site, because an assertion nobody has
seen fail is not evidence. Every `__pycache__` under the tree is purged before
each cell -- stale bytecode has INVERTED mutation results in this lab (clean
control failed, mutated case passed) and `PYTHONDONTWRITEBYTECODE=1` does NOT
fix it, because it stops writing, not reading. Control and mutant are loaded
in ONE invocation.

TWELVE MUTANTS, each aimed at a named test:
  M1   `mask_exempt` bypassed       -> a struck historical row fires (N3 red)
  M2a  the zero-pairs B1 guard      -> SURVIVES, and the cell says so: it is
                                       backstopped by M3, and what is actually
                                       lost is the reason a reader acts on
  M2b  BOTH B1 guards at once       -> an empty set reports PASS. Nothing else
                                       is behind them, which is the point of
                                       running the composite rather than
                                       recording M2a as "killed"
  M3   the zero-GRADED B1 guard     -> "95 pairs, none compared" reports PASS
  M4   the NEUTRAL polarity guard   -> RESOLVED-over-FALSIFIED fires
  M5   the mixed-polarity guard     -> a row holding both polarities fires
  M6   ALL-CAPS verdict matching    -> `the rule holds` in prose is graded
  M7a  the leading cell's 40-char tail -> a cell that MENTIONS a section is
                                       read as a summary OF it
  M7b  the bullet's 60-char opening -> the same, for bullets
  M8   heading neutering            -> the corrected heading reads as nothing,
                                       and the real defect stops being found
  M9   the `_STRUCK_HEAD` status marker -> `### 6.1 Struck` stops counting DENY
  M10  the FAIL exit code           -> a hit exits 0
  M11  the marker read off the RAW heading -> `~~FALSIFIED~~ **VERIFIED**`
                                       reads as withdrawn: one correct pair
                                       loses its grade and one real defect in
                                       the other direction is missed
"""

from __future__ import annotations

import importlib.util
import io
import contextlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SOURCE = REPO / "scripts" / "check_summary_consistency.py"


def _purge_pycache() -> int:
    """Stale bytecode has inverted mutation results here. Purge, and count."""
    n = 0
    for p in REPO.rglob("__pycache__"):
        if ".git" in p.parts:
            continue
        shutil.rmtree(p, ignore_errors=True)
        n += 1
    return n


_purge_pycache()
_SPEC = importlib.util.spec_from_file_location("summary_consistency_ut", _SOURCE)
sc = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sc
_SPEC.loader.exec_module(sc)


def _mutant(name: str, old: str, new: str):
    """The check with ONE substitution, loaded as its own module.

    The copy sits in a temporary tree so no mutant can be read by accident,
    and its `REPO` is pointed back at the live repository afterwards: the
    controls read two git blobs by commit, and a mutant whose controls simply
    fail to read anything would report UNKNOWN for the wrong reason and look
    killed when it was not.
    """
    _purge_pycache()
    text = _SOURCE.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError(
            f"mutation {name!r} does not identify one site: "
            f"{text.count(old)} occurrence(s). The code moved; fix the "
            f"mutation rather than deleting this test.")
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "scripts").mkdir()
    target = root / "scripts" / "check_summary_consistency.py"
    target.write_text(text.replace(old, new), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"sc_{name}", target)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.__keepalive = tmp          # noqa: SLF001 - hold the tempdir open
    return module


def _mutant_of(module, name: str, old: str, new: str):
    """A second substitution on top of an already-mutated module.

    Needed for the composite cell: two guards that overlap must be proved to
    have nothing behind them, and that takes both removed at once.
    """
    _purge_pycache()
    src = Path(module.__file__)
    text = src.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError(f"mutation {name!r} does not identify one site")
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "scripts").mkdir()
    target = root / "scripts" / "check_summary_consistency.py"
    target.write_text(text.replace(old, new), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"sc_{name}", target)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.REPO = REPO
    mod.__keepalive = tmp             # noqa: SLF001
    return mod


def _blob(commit: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{commit}:{sc.CONTROL_PATH}"],
        capture_output=True, text=True)
    if p.returncode != 0:                       # pragma: no cover - env fault
        raise unittest.SkipTest(f"git show {commit} failed: {p.stderr}")
    return p.stdout


PRE = _blob(sc.CONTROL_COMMIT + "~1")
POST = _blob(sc.CONTROL_COMMIT)


def hits(module, text, path="doc.md"):
    return [p for p in module.grade_document(text, path)[0]
            if p.grade == "DISAGREE"]


def pairs_of(module, text, path="doc.md"):
    return module.grade_document(text, path)[0]


def currency_block(module, text):
    """The contiguous table holding the 4.8 row -- grown, never enumerated."""
    ps = pairs_of(module, text)
    seed = next((p.sum_line for p in ps if p.ident == "4.8"), None)
    if seed is None:
        return []
    lines = text.split("\n")
    lo = hi = seed
    while lo > 0 and module._ROW_RE.match(lines[lo - 1]):
        lo -= 1
    while hi + 1 < len(lines) and module._ROW_RE.match(lines[hi + 1]):
        hi += 1
    return [p for p in ps if lo <= p.sum_line <= hi]


# ---------------------------------------------------------------------------
# The real instance, both sides of its repair
# ---------------------------------------------------------------------------

class TestTheRealDefect(unittest.TestCase):
    """P1 and N2: the row that named the class, before and after."""

    def test_P1_the_pre_repair_4_8_row_fires(self):
        h = [p for p in hits(sc, PRE, sc.CONTROL_PATH) if p.ident == "4.8"]
        self.assertEqual(len(h), 1, "the D141 defect must be found")
        self.assertIn("HOLDS", h[0].sum_verdicts)
        self.assertIn("FALSIFIED", h[0].sec_verdicts)

    def test_P1_names_both_regions_by_line_so_a_reader_can_check_it(self):
        h = [p for p in hits(sc, PRE, sc.CONTROL_PATH) if p.ident == "4.8"][0]
        self.assertGreater(h.sec_line - h.sum_line, 200,
                           "the two regions are 212 lines apart; a hit that "
                           "does not carry both line numbers is unactionable")

    def test_N2_the_repaired_row_does_not_fire_and_is_graded_AGREE(self):
        block = currency_block(sc, POST)
        row = [p for p in block if p.ident == "4.8"]
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0].grade, "AGREE")


class TestTheTenCorrectRows(unittest.TestCase):
    """N1, the important half.

    These ten rows sat in the same block as the stale one, at the same commit,
    byte-identical to what `472f9f92` wrote -- and every one of them was still
    RIGHT. An instrument that cannot tell them from the eleventh is measuring
    byte-identity, which decides nothing in either direction.
    """

    def setUp(self):
        self.block = currency_block(sc, PRE)

    def test_the_block_is_eleven_rows_and_the_control_is_not_empty(self):
        self.assertEqual(len(self.block), 11,
                         "a must-not-match control over an empty set clears "
                         "nothing (defect class B1)")

    def test_none_of_the_other_ten_fires(self):
        fired = [p.ident for p in self.block
                 if p.ident != "4.8" and p.grade == "DISAGREE"]
        self.assertEqual(fired, [])

    def test_and_they_are_reported_UNDECIDABLE_with_a_reason_not_as_clean(self):
        for p in self.block:
            if p.ident == "4.8":
                continue
            self.assertEqual(p.grade, "UNDECIDABLE")
            self.assertTrue(p.reason.strip(),
                            "an ungradeable pair must say why")


# ---------------------------------------------------------------------------
# Synthetic controls, both halves
# ---------------------------------------------------------------------------

SEC_FALSIFIED = ("\n### 9.2 The widget is current — ~~VERIFIED~~ "
                 "**FALSIFIED 2026-08-11**\n\nThe widget moved.\n")
TABLE = "| § | claim | verdict |\n|---|---|---|\n"


def doc(row: str, section: str = SEC_FALSIFIED) -> str:
    return "# A document\n\n" + TABLE + row + "\n" + section


class TestSyntheticControls(unittest.TestCase):
    def test_P2_HOLDS_over_FALSIFIED_fires(self):
        d = doc("| **9.2** | the widget | **HOLDS** |\n")
        self.assertEqual(len(hits(sc, d)), 1)

    def test_N3_a_correctly_struck_row_does_not_fire_and_is_EXEMPT(self):
        d = doc("| **9.2** | the widget | ~~**HOLDS**~~ *(struck)* |\n")
        self.assertEqual(hits(sc, d), [])
        self.assertEqual([p.grade for p in pairs_of(sc, d)], ["EXEMPT"])

    def test_the_other_direction_fires_too(self):
        """A section left VERIFIED under a row that says FALSIFIED is the
        same class with the staleness on the other side."""
        d = doc("| **9.2** | the widget | **FALSIFIED 2026-08-11** |\n",
                "\n### 9.2 The widget is current — **VERIFIED**\n\nok\n")
        self.assertEqual(len(hits(sc, d)), 1)

    def test_a_section_heading_that_declares_itself_STRUCK_counts_DENY(self):
        d = doc("| **6.1** | the deviation was halved | **HOLDS** |\n",
                "\n### 6.1 STRUCK, 2026-08-14 — the deviation claim\n\nx\n")
        self.assertEqual(len(hits(sc, d)), 1)


# ---------------------------------------------------------------------------
# The three-valued contract, and B1
# ---------------------------------------------------------------------------

def run_cli(module, *argv):
    out = io.StringIO()
    old = sys.argv
    sys.argv = ["check_summary_consistency", *argv]
    try:
        with contextlib.redirect_stdout(out):
            rc = module.main()
    finally:
        sys.argv = old
    return rc, out.getvalue()


class TestEmptySetIsNotPass(unittest.TestCase):
    def test_a_document_with_no_pairs_yields_no_pairs(self):
        self.assertEqual(pairs_of(sc, "# Title\n\nProse only.\n"), [])

    def test_the_runner_reports_UNKNOWN_when_it_finds_no_pairs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "-C", td, "init", "-q"], check=True)
            (root / "a.md").write_text("# Title\n\nProse only.\n")
            subprocess.run(["git", "-C", td, "add", "a.md"], check=True)
            rc, text = run_cli(sc, "--root", td)
        self.assertIn("VERDICT: UNKNOWN", text)
        self.assertEqual(rc, sc.EXIT[sc.UNKNOWN])
        self.assertIn("defect class B1", text)
        self.assertNotIn("VERDICT: PASS", text)

    def test_the_verdict_words_are_three_and_the_codes_are_pinned(self):
        self.assertEqual(sc.EXIT, {"PASS": 0, "FAIL": 1, "UNKNOWN": 3})


class TestTheFramePrintsItsOwnReach(unittest.TestCase):
    def test_every_run_prints_pairs_found_graded_and_why_not(self):
        rc, text = run_cli(sc)
        for phrase in ("documents considered", "documents opened",
                       "pairs FOUND", "pairs GRADED", "pairs UNDECIDABLE",
                       "pairs EXEMPT", "CONTROLS", "BLIND TO",
                       "NOT GRADED"):
            self.assertIn(phrase, text, f"the frame must state {phrase!r}")
        self.assertIn(rc, (0, 1, 3))


class TestUndecidableIsUsedRatherThanForced(unittest.TestCase):
    def test_a_neutral_verdict_word_is_UNDECIDABLE_not_a_hit(self):
        d = doc("| **9.2** | the widget | **RESOLVED** |\n")
        self.assertEqual([p.grade for p in pairs_of(sc, d)], ["UNDECIDABLE"])

    def test_a_row_carrying_both_polarities_is_UNDECIDABLE_not_a_hit(self):
        d = doc("| **9.2** | the widget | **HOLDS** where it was **MOOT** |\n")
        self.assertEqual([p.grade for p in pairs_of(sc, d)], ["UNDECIDABLE"])

    def test_a_section_with_no_verdict_word_is_UNDECIDABLE_not_clean(self):
        d = doc("| **9.2** | the widget | **HOLDS** |\n",
                "\n### 9.2 The widget is current\n\nprose\n")
        p = pairs_of(sc, d)[0]
        self.assertEqual(p.grade, "UNDECIDABLE")
        self.assertIn("no verdict word", p.reason)


class TestPairsAreDerivedNotListed(unittest.TestCase):
    def test_a_citation_inside_a_body_cell_is_not_a_summary(self):
        d = doc("| **1.1** | see §9.2 for why this **HOLDS** | notes |\n")
        self.assertEqual([p.ident for p in pairs_of(sc, d)], [])

    def test_a_heading_string_in_the_leading_cell_pairs(self):
        d = ("# Doc\n\n" + TABLE
             + "| The widget is current | x | **HOLDS** |\n"
             + SEC_FALSIFIED)
        self.assertEqual(len(hits(sc, d)), 1)

    def test_the_real_document_yields_pairs_from_three_structural_rules(self):
        ps = pairs_of(sc, POST, sc.CONTROL_PATH)
        kinds = {p.kind for p in ps}
        self.assertIn("table-row", kinds)
        self.assertGreater(len(ps), 20)


# ---------------------------------------------------------------------------
# MUTATION PROOF -- ten mutants, control and mutant in one invocation
# ---------------------------------------------------------------------------

class TestMutants(unittest.TestCase):
    """Each cell reintroduces one defect and asserts the aimed test reddens."""

    def test_M1_bypassing_mask_exempt_makes_a_struck_row_fire(self):
        m = _mutant("m1", "masked, mcounts = cdf.mask_exempt(raw)",
                    "masked, mcounts = raw, {}")
        d = doc("| **9.2** | the widget | ~~**HOLDS**~~ *(struck)* |\n")
        self.assertEqual(hits(sc, d), [], "control: struck row is silent")
        self.assertEqual(len(hits(m, d)), 1, "mutant must fire on struck text")

    def test_M2a_the_zero_pairs_guard_alone_is_BACKSTOPPED_and_that_is_stated(
            self):
        """Recorded rather than hidden: this mutant SURVIVES, by design.

        `not pairs` is a strict subset of `not graded` -- zero pairs cannot
        produce a graded pair -- so removing the first guard leaves the second
        holding the same case. What is lost is the REASON a reader acts on,
        and that is what this cell asserts. The composite is M2b.
        """
        m = _mutant("m2a", "    elif not pairs:", "    elif False:")
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "-C", td, "init", "-q"], check=True)
            (Path(td) / "a.md").write_text("# Title\n\nProse only.\n")
            subprocess.run(["git", "-C", td, "add", "a.md"], check=True)
            rc_c, t_c = run_cli(sc, "--root", td)
            rc_m, t_m = run_cli(m, "--root", td)
        self.assertIn("VERDICT: UNKNOWN", t_c)
        self.assertIn("zero summary/section pairs found", t_c)
        self.assertIn("VERDICT: UNKNOWN", t_m)
        self.assertNotIn("zero summary/section pairs found", t_m)

    def test_M2b_removing_BOTH_B1_guards_lets_an_empty_set_report_PASS(self):
        m = _mutant("m2b", "    elif not pairs:", "    elif False:")
        m = _mutant_of(m, "m2b2", "    elif not graded:", "    elif False:")
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "-C", td, "init", "-q"], check=True)
            (Path(td) / "a.md").write_text("# Title\n\nProse only.\n")
            subprocess.run(["git", "-C", td, "add", "a.md"], check=True)
            rc_c, t_c = run_cli(sc, "--root", td)
            rc_m, t_m = run_cli(m, "--root", td)
        self.assertIn("VERDICT: UNKNOWN", t_c)
        self.assertEqual(rc_c, sc.EXIT[sc.UNKNOWN])
        self.assertIn("VERDICT: PASS", t_m)
        self.assertEqual(rc_m, 0, "nothing else backstops the empty set")

    def test_M3_deleting_the_zero_graded_guard_lets_nothing_compared_PASS(self):
        m = _mutant("m3", "    elif not graded:", "    elif False:")
        text = ("# Doc\n\n" + TABLE
                + "| **9.2** | the widget | no verdict here |\n"
                + "\n### 9.2 The widget is current\n\nprose\n")
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "-C", td, "init", "-q"], check=True)
            (Path(td) / "a.md").write_text(text)
            subprocess.run(["git", "-C", td, "add", "a.md"], check=True)
            rc_c, t_c = run_cli(sc, "--root", td)
            rc_m, t_m = run_cli(m, "--root", td)
        self.assertIn("VERDICT: UNKNOWN", t_c)
        self.assertIn("VERDICT: PASS", t_m)

    def test_M4_deleting_the_NEUTRAL_guard_makes_RESOLVED_fire(self):
        m = _mutant("m4", 'if "NEUTRAL" in sp or "NEUTRAL" in cp:',
                    "if False:")
        d = doc("| **9.2** | the widget | **RESOLVED** |\n")
        self.assertEqual(hits(sc, d), [])
        self.assertEqual(len(hits(m, d)), 1)

    def test_M5_deleting_the_mixed_polarity_guard_makes_a_mixed_row_fire(self):
        m = _mutant("m5", "if len(sp) > 1 or len(cp) > 1:", "if False:")
        d = doc("| **9.2** | the widget | **HOLDS** where it was **MOOT** |\n")
        self.assertEqual(hits(sc, d), [])
        self.assertEqual(len(hits(m, d)), 1)

    def test_M6_case_insensitive_verdicts_grade_a_verb_in_prose(self):
        m = _mutant("m6",
                    '_VERDICT_RE = re.compile(r"\\b(" + "|".join(VERDICTS) + r")\\b")',
                    '_VERDICT_RE = re.compile(r"\\b(" + "|".join(VERDICTS) + r")\\b", re.I)')
        d = doc("| **9.2** | the widget | the rule holds, as before |\n")
        self.assertEqual(hits(sc, d), [], "control: `holds` is a verb")
        self.assertEqual(len(hits(m, d)), 1)

    def test_M7a_a_loose_leading_cell_pairs_a_citation_as_a_summary(self):
        """The 40-character tail on `_CELL_NUM` is what keeps a leading cell
        that MENTIONS a section from being read as a summary OF it."""
        m = _mutant("m7a", r'r"(?:[\s*_~`(\[][^|]{0,40})?$")',
                    r'r"(?:[\s*_~`(\[][^|]*)?$")')
        d = doc("| 9.2 is cited here as background only, and the verdict in "
                "this row is about something else | x | **HOLDS** |\n")
        self.assertEqual(pairs_of(sc, d), [])
        self.assertEqual(len(hits(m, d)), 1)

    def test_M7b_a_bullet_scanned_past_its_opening_pairs_a_citation(self):
        m = _mutant("m7b", "BULLET_HEAD_CHARS = 60", "BULLET_HEAD_CHARS = 4000")
        d = ("# Doc\n\n- This bullet is about the round-5 duct route and the "
             "decline gate, and only later does it mention §9.2, where the "
             "claim **HOLDS**.\n" + SEC_FALSIFIED)
        self.assertEqual(pairs_of(sc, d), [])
        self.assertEqual(len(hits(m, d)), 1)

    def test_M8_not_neutering_the_heading_loses_the_real_defect(self):
        m = _mutant("m8", 'return re.sub(r"[#>]", " ", line)', "return line")
        self.assertEqual(
            len([p for p in hits(sc, PRE, sc.CONTROL_PATH)
                 if p.ident == "4.8"]), 1)
        self.assertEqual(
            [p for p in hits(m, PRE, sc.CONTROL_PATH) if p.ident == "4.8"], [],
            "the corrected heading must read FALSIFIED, not nothing")

    def test_M9_dropping_the_struck_head_marker_loses_a_withdrawn_section(self):
        """The marker earns its place on the headings the VOCABULARY misses:
        `Struck` capitalised is a withdrawal to `_STRUCK_HEAD` and not a
        verdict word to this check."""
        m = _mutant("m9",
                    'if live_struck and "DENY" not in polarities(cv or ()):',
                    "if False:")
        d = doc("| **6.1** | the deviation | **HOLDS** |\n",
                "\n### 6.1 Struck, 2026-08-14 — the deviation claim\n\nx\n")
        self.assertEqual(len(hits(sc, d)), 1)
        self.assertEqual(hits(m, d), [])

    def test_M11_reading_the_status_marker_off_the_RAW_heading_over_fires(self):
        """A correction the other way -- `~~FALSIFIED~~ **VERIFIED**` -- makes
        `_STRUCK_HEAD` match a section that is not withdrawn. Reading the
        marker off the raw line flags every correct summary of it."""
        m = _mutant("m11", 'cdf._STRUCK_HEAD.match("#" + head_live)',
                    "cdf._STRUCK_HEAD.match(rlines[sec.line])")
        sec = ("\n### 9.2 The widget — ~~FALSIFIED~~ **VERIFIED 2026-08-12**"
               "\n\nre-checked\n")
        agreeing = doc("| **9.2** | the widget | **VERIFIED 2026-08-12** |\n",
                       sec)
        self.assertEqual([p.grade for p in pairs_of(sc, agreeing)], ["AGREE"])
        self.assertEqual([p.grade for p in pairs_of(m, agreeing)],
                         ["UNDECIDABLE"],
                         "the mutant reads a standing section as withdrawn "
                         "and loses the grade")
        stale = doc("| **9.2** | the widget | **FALSIFIED 2026-08-11** |\n",
                    sec)
        self.assertEqual(len(hits(sc, stale)), 1,
                         "control: a summary still saying FALSIFIED over a "
                         "section since re-VERIFIED is the same class")
        self.assertEqual(hits(m, stale), [], "the mutant misses it")

    def test_M10_a_hit_that_exits_zero_is_a_printer_not_a_gate(self):
        m = _mutant("m10", 'EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}',
                    'EXIT = {PASS: 0, FAIL: 0, UNKNOWN: 3}')
        text = doc("| **9.2** | the widget | **HOLDS** |\n")
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "-C", td, "init", "-q"], check=True)
            (Path(td) / "a.md").write_text(text)
            subprocess.run(["git", "-C", td, "add", "a.md"], check=True)
            rc_c, t_c = run_cli(sc, "--root", td)
            rc_m, t_m = run_cli(m, "--root", td)
        self.assertIn("VERDICT: FAIL", t_c)
        self.assertEqual(rc_c, 1)
        self.assertIn("VERDICT: FAIL", t_m)
        self.assertEqual(rc_m, 0, "mutant must be the defect, not a crash")


class TestTheRunnerAdmitsIt(unittest.TestCase):
    """`lab_check.py` admits by AST. If it stops admitting, nothing runs it."""

    def setUp(self):
        _purge_pycache()
        spec = importlib.util.spec_from_file_location(
            "lab_check_ut", REPO / "scripts" / "lab_check.py")
        self.lc = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.lc
        spec.loader.exec_module(self.lc)

    def test_it_is_admitted_as_a_script_gate(self):
        cands, _frame = self.lc.enumerate_candidates(REPO, allow_writers=False)
        mine = [c for c in cands
                if c.path.endswith("check_summary_consistency.py")]
        self.assertEqual(len(mine), 1, "the runner must see exactly one")
        self.assertTrue(mine[0].admitted,
                        f"not admitted: {mine[0].reason}")


if __name__ == "__main__":
    unittest.main()
