#!/usr/bin/env python3
"""Refuse if the copies of `ugrid_to_foam.py` on this box have drifted apart, or if a copy
this checker has never seen appears, or if one that should be there has vanished.

WHY THIS EXISTS, MEASURED NOT SUPPOSED. On 2026-09-03 a cfd lane found FIVE copies of
`ugrid_to_foam.py` on this box in TWO equivalence classes, THREE of them carrying the same
silent byte-order defect byte-for-byte, and ONE of those three living OUTSIDE git where no
repo-only check could ever see it. The directory names actively mislead: the copy under
`hlpw6-memory-probe/` is the OLD lineage while the copy under `dpw5-committee-probe/` is
the DEFECTIVE newer one. Evidence:
`verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/CONVERTER_COPY_MANIFEST.json` (`b78e8858`).

  THE HAZARD IS THE DUPLICATION, NOT THE DEFECT. Repair one copy and the others are
  silently left broken, and no reader can tell which is authoritative.

FOUR DESIGN REQUIREMENTS, each answering a way a checker like this fails open:

 (a) NO BARE `assert` ANYWHERE. `python3 -O` deletes every assert, so a guard written as
     one is a guard the runner switches off without knowing (L-332). Every refusal here
     raises. `ast_self_check()` parses THIS FILE'S OWN SOURCE and refuses if an `Assert`
     node is present, so the rule cannot rot back in.

 (b) IT SWEEPS; IT DOES NOT READ A MANIFEST. A manifest-only checker cannot see a copy
     that appears tomorrow, and "no sixth copy" from a checker that never looked is
     uninterpretable. MEASURED JUSTIFICATION: between the 2026-09-03 audit and the same
     day's re-run, the `.ugrid` population on this box went from 13 files to 17. A
     hard-coded list would already be stale. The sweep states the roots it walked and
     REFUSES if any root is unreadable -- an incomplete sweep is not a clean sweep.

 (c) AN ABSENT COPY IS `NOT A RESULT`, NEVER CLEAN. Two copies live under
     `/home/ubuntu/certonomous-runs/`, outside git, in a tree that can be cleaned at any
     time. A checker reporting "no divergence" because a file vanished is the fail-open
     this lab has hunted repeatedly. A known path that disappears is reported as
     `NOT A RESULT` and exits non-zero.

 (d) IT MUST BE INVOKED -- AND THE INVOCATION PATH IS ENUMERATION, NOT A CALL SITE.
     MEASURED 2026-09-03: `scripts/lab_check.py` does not hold a list of checks to call.
     `enumerate_candidates()` (`lab_check.py:843`) unions `git ls-tree -r HEAD` with an
     `os.walk` over `CHECK_DIRS = ("scripts", "sdk/tests")` (`lab_check.py:437`), then
     classifies whatever it finds. Run on 2026-09-03 it admitted THIS FILE, while still
     untracked, as `gate: main() can exit non-zero (exit(2))`. Under `EXIT_CONTRACT`
     (`lab_check.py:441`) an exit of 2 maps to FAIL. So merely LIVING IN `scripts/` with a
     non-zero-exit `main()` is what wires this checker; no call site is required and none
     exists. `--report-call-site` reports what it can actually see about that, and says
     plainly what it cannot -- see that function's docstring.

EXIT CODES: 0 all copies consistent and accounted for; 2 refusal (divergence, unknown
copy, missing copy, unreadable root, or a self-check failure).
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import tokenize

# Roots swept for copies. Both sides of the repo boundary, because the defect lived on
# both. A root that cannot be walked is a REFUSAL, never an empty result.
ROOTS = [
    "/home/ubuntu/Certonomous",
    "/home/ubuntu/certonomous-runs",
]
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
TARGET = "ugrid_to_foam.py"

# Paths known to this checker. A path here that is MISSING is NOT A RESULT (requirement c);
# a copy found that is NOT here is an unknown copy and is a refusal (requirement b).
#
# `/home/ubuntu/Certonomous/scripts/ugrid_to_foam.py` WAS here and is deliberately gone.
# It was REMOVED 2026-09-03 (cfd-supervisor ruling 3), not lost: it was the older
# five-bare-assert lineage sitting in the one directory that 60+ graders across four teams
# insert at `sys.path` position ZERO (`os.path.join(REPO, "scripts")`), so the next
# `import ugrid_to_foam` written anywhere in the lab would have resolved to the defective
# copy silently and preferentially, ahead of the canonical one. It is not listed below
# because requirement (c) would then report NOT A RESULT forever over a deliberate removal.
KNOWN = [
    "/home/ubuntu/Certonomous/cases/committee-grids/ugrid_to_foam.py",
    "/home/ubuntu/Certonomous/cases/hlpw6/ugrid_to_foam.py",
    "/home/ubuntu/certonomous-runs/dpw5-committee-probe/ugrid_to_foam.py",
    "/home/ubuntu/certonomous-runs/hlpw6-memory-probe/ugrid_to_foam.py",
]

# The canonical repaired converter. Every copy in ITS lineage must match it byte for byte.
CANONICAL = "/home/ubuntu/Certonomous/cases/committee-grids/ugrid_to_foam.py"

# The second, older lineage: no sniff_layout at all. Tracked so a drift inside it is also
# caught, but it is NOT synced to the canonical -- it is a different program.
#
# AFTER the 2026-09-03 removal this lineage has ONE member, and a one-member
# internal-consistency check CANNOT FAIL. That is reported explicitly as VACUOUS rather
# than passed over in silence: a check that cannot fail is a fail-open wearing a pass.
SECOND_LINEAGE = [
    "/home/ubuntu/certonomous-runs/hlpw6-memory-probe/ugrid_to_foam.py",
]


class Refusal(Exception):
    """Explicit refusal. Never an assert (L-332)."""


@dataclasses.dataclass(frozen=True)
class Config:
    """The whole of what this checker looks at, passed in rather than read from globals.

    WHY THIS EXISTS. Until 2026-09-03 `selftest()` could not drive `check()` at all,
    because `check()` read module-level constants pointing at real absolute paths. So the
    plants RE-IMPLEMENTED the comparison inline inside the test -- and a plant that
    re-implements the logic it is testing verifies the test, not the instrument. Deleting
    the shipped `drift` computation left `--selftest` still printing
    `all_plants_fired: true`. Injecting the configuration is what lets every plant run the
    REAL `check()` against a fixture. See `selftest()`.
    """
    roots: tuple[str, ...]
    known: tuple[str, ...]
    canonical: str
    second_lineage: tuple[str, ...]
    target: str = TARGET
    skip_dirs: frozenset = frozenset(SKIP_DIRS)


def default_config() -> Config:
    """The production configuration -- the real paths on this box."""
    return Config(roots=tuple(ROOTS), known=tuple(KNOWN), canonical=CANONICAL,
                  second_lineage=tuple(SECOND_LINEAGE), target=TARGET,
                  skip_dirs=frozenset(SKIP_DIRS))


def ast_self_check(path: str | None = None) -> None:
    """Requirement (a): refuse if THIS FILE has grown a bare `assert`."""
    p = path or os.path.abspath(__file__)
    try:
        tree = ast.parse(open(p, encoding="utf-8").read(), filename=p)
    except (OSError, SyntaxError) as e:
        raise Refusal(f"cannot parse own source {p}: {e}") from e
    bad = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if bad:
        raise Refusal(
            f"{p} contains bare assert(s) at line(s) {bad}. `python3 -O` deletes every "
            f"assert, so a guard written as one is a guard the runner can switch off "
            f"without knowing (L-332). Convert them to explicit raises.")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sweep(cfg: Config):
    """Requirement (b): walk the roots. An unreadable root REFUSES."""
    errors = []
    found = []
    dirs_walked = 0
    for root in cfg.roots:
        if not os.path.isdir(root):
            raise Refusal(f"sweep root is not a directory: {root}. An incomplete sweep is "
                          f"not a clean sweep.")
        for d, subdirs, files in os.walk(root, onerror=errors.append):
            subdirs[:] = [x for x in subdirs if x not in cfg.skip_dirs]
            dirs_walked += 1
            if cfg.target in files:
                found.append(os.path.join(d, cfg.target))
    if errors:
        raise Refusal(
            f"the sweep could not read {len(errors)} director(ies) "
            f"(first: {errors[0]}). An incomplete sweep is NOT A RESULT -- this checker "
            f"will not report 'no unknown copies' over ground it could not walk.")
    return sorted(found), dirs_walked


def check(cfg: Config | None = None, as_json: bool = False, emit: bool = True):
    """Run the whole consistency check. Returns `(exit_code, report)`.

    `emit=False` suppresses printing so a caller -- `selftest()` -- can drive THIS
    function and grade its RETURN VALUE. The plants assert on the code and on
    `report["problems"]`; they do not recompute the comparison.
    """
    cfg = cfg or default_config()
    ast_self_check()
    found, dirs_walked = sweep(cfg)

    report = {
        "instrument": os.path.abspath(__file__),
        "roots_swept": list(cfg.roots),
        "directories_walked": dirs_walked,
        "copies_found": found,
        "n_found": len(found),
        "THIS_IS_NOT_A_GRADED_RUN": True,
        "verdict": "NONE -- a consistency check carries no verdict of the fixed vocabulary",
    }
    problems = []

    # (c) a known path that has vanished is NOT A RESULT, never clean.
    missing = [p for p in cfg.known if not os.path.isfile(p)]
    report["missing_known_copies"] = missing
    if missing:
        problems.append(
            f"NOT A RESULT: {len(missing)} known copy/copies are ABSENT: {missing}. An "
            f"absent copy is not an absent difference -- it is an unmeasured one. Two of "
            f"the known copies live outside git under /home/ubuntu/certonomous-runs/, a "
            f"tree that can be cleaned at any time, so this is the expected way for this "
            f"check to go blind. It reports NOT A RESULT rather than 'no divergence'.")

    # (b) a copy the checker has never seen is a refusal, not a shrug.
    unknown = [p for p in found if p not in cfg.known]
    report["unknown_copies"] = unknown
    if unknown:
        problems.append(
            f"UNKNOWN COPY/COPIES: {unknown}. A new copy is how this defect propagated in "
            f"the first place -- three of five copies were byte-identical clones. Add it "
            f"to KNOWN deliberately, after deciding which lineage it belongs to.")

    # divergence within each lineage
    if os.path.isfile(cfg.canonical):
        canon = sha256(cfg.canonical)
        report["canonical"] = cfg.canonical
        report["canonical_sha256"] = canon
        lineage1 = [p for p in cfg.known
                    if p not in cfg.second_lineage and os.path.isfile(p)]
        h1 = {p: sha256(p) for p in lineage1}
        report["lineage_canonical"] = h1
        drift = [p for p, h in h1.items() if h != canon]
        if drift:
            problems.append(
                f"DIVERGENCE in the canonical lineage: {drift} do not match "
                f"{cfg.canonical}. A repair applied to one copy and not the others is "
                f"exactly the hazard this checker exists for.")
    else:
        problems.append(f"NOT A RESULT: the canonical converter is ABSENT: {cfg.canonical}")

    # SECOND LINEAGE. The consistency statement here is EXPLICITLY QUALIFIED BY ITS OWN
    # POWER. With 0 members present there is nothing to compare; with 1 member the
    # comparison cannot fail. Reporting either as a silent pass would be a check that
    # cannot fail wearing the word that means it did not.
    present2 = [p for p in cfg.second_lineage if os.path.isfile(p)]
    h2 = {p: sha256(p) for p in present2}
    report["lineage_second"] = h2
    report["lineage_second_declared"] = list(cfg.second_lineage)
    report["lineage_second_n_present"] = len(present2)
    if len(present2) == 0:
        report["lineage_second_consistency"] = (
            "NOT A RESULT -- no member of the second lineage is present, so its internal "
            "consistency was not measured at all.")
    elif len(present2) == 1:
        report["lineage_second_consistency"] = (
            "second lineage has 1 member; internal consistency is VACUOUS, not verified. "
            "A one-member set cannot disagree with itself, so this arm of the checker "
            "CANNOT FAIL in the present configuration and its silence carries no "
            "information. The second member, /home/ubuntu/Certonomous/scripts/"
            "ugrid_to_foam.py, was removed 2026-09-03 by cfd-supervisor ruling 3.")
    else:
        if len(set(h2.values())) > 1:
            report["lineage_second_consistency"] = "DIVERGENT"
            problems.append(
                f"DIVERGENCE in the second (older, no-sniff_layout) lineage: {h2}. These "
                f"are deliberately NOT synced to the canonical -- they are a different "
                f"program -- but they must agree with each other.")
        else:
            report["lineage_second_consistency"] = (
                f"VERIFIED over {len(present2)} members present")

    report["problems"] = problems
    report["consistent"] = not problems
    code = 0 if not problems else 2
    report["exit_code"] = code

    if emit:
        if as_json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"swept {dirs_walked} directories under {len(cfg.roots)} roots; "
                  f"found {len(found)} copies of {cfg.target}")
            if os.path.isfile(cfg.canonical):
                print(f"canonical {sha256(cfg.canonical)[:16]}  {cfg.canonical}")
            for p in found:
                mark = "known" if p in cfg.known else "UNKNOWN"
                print(f"  {sha256(p)[:16]}  {mark:7s} {p}")
            print(f"\nsecond lineage: {report['lineage_second_consistency']}")
            for pr in problems:
                print(f"\nREFUSAL: {pr}")
            if not problems:
                print("\nOK: all copies accounted for and consistent within their "
                      "lineages, SUBJECT TO the second-lineage qualification above.")
    return code, report


# ---------------------------------------------------------------------------
# Planted controls
# ---------------------------------------------------------------------------

def _fixture(parent: str):
    """Build a throwaway tree of real `ugrid_to_foam.py` files and a Config over it.

    Three canonical-lineage copies and one second-lineage pair, each in its own
    subdirectory so the sweep finds them by the real filename.

    THE `mkdtemp` ON THE FIRST LINE IS LEDGER-BEARING, NOT STYLE. `lab_check.py`'s
    write predicate (`_write_primitive`, `lab_check.py:714`) exempts a write only when
    the ENCLOSING FUNCTION itself calls a tempmaker -- the exemption is per-function and
    deliberately never module-wide (docket D283), because a blanket once admitted eight
    writers against the live tree. Measured 2026-09-03: when this helper took a path
    from its caller instead of making one, `lab_check --list` reclassified the whole
    module `writes-to-tree: line 306: os.makedirs(...)` and SKIPPED it -- admitted 1
    became admitted 0, and the checker went inert in the runner it exists to be run by.
    Making the temp directory HERE restores admission and is the true statement anyway:
    every write below lands under a directory this function just created.
    """
    tmp = tempfile.mkdtemp(dir=parent)

    def w(rel: str, body: bytes) -> str:
        p = os.path.join(tmp, rel, TARGET)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(body)
        return p

    canon_body = b"# canonical fixture converter\nx = 1\n"
    old_body = b"# older lineage fixture converter, no sniff_layout\ny = 2\n"
    c1 = w("canon_a", canon_body)
    c2 = w("canon_b", canon_body)
    c3 = w("canon_c", canon_body)
    s1 = w("old_a", old_body)
    s2 = w("old_b", old_body)
    cfg = Config(roots=(tmp,), known=(c1, c2, c3, s1, s2), canonical=c1,
                 second_lineage=(s1, s2))
    return cfg, {"c1": c1, "c2": c2, "c3": c3, "s1": s1, "s2": s2}


def _fired(code: int, report: dict, needle: str) -> dict:
    """Grade ONE plant on the SHIPPED `check()`'s own return value."""
    hits = [p for p in report["problems"] if needle in p]
    return {"exit_code": code, "n_problems": len(report["problems"]),
            "matched": len(hits),
            "fired": bool(hits) and code == 2}


def selftest():
    """PLANTED CONTROL. An OK from a checker never shown able to refuse is not evidence.

    EVERY PLANT DRIVES THE SHIPPED `check()`. Before 2026-09-03 plants 1, 2 and 3
    re-implemented the comparison inline in the test -- deleting the shipped `drift`
    computation entirely left this printing `all_plants_fired: true`. That is the lab's
    "the reader answered a different question" fail-open, inside a file written to prevent
    fail-opens. Each plant now builds a fixture, calls `check(cfg, emit=False)`, and grades
    the RETURNED exit code and `problems` list.

    P0 is the NEGATIVE control and is not optional: a checker that refuses everything
    would fire every positive plant. P0 requires exit 0 and an EMPTY problems list on a
    clean fixture, so the positives are only evidence against a background of silence.
    """
    rep = {}
    with tempfile.TemporaryDirectory() as t:

        # P0 -- NEGATIVE CONTROL. A clean fixture must be silent.
        cfg, f = _fixture(t)
        code, report = check(cfg, emit=False)
        rep["P0_clean_fixture_is_silent"] = {
            "exit_code": code, "n_problems": len(report["problems"]),
            "problems": report["problems"],
            "fired": code == 0 and report["problems"] == [],
            "note": "negative control -- without this, a checker that refuses "
                    "unconditionally would pass every positive plant below"}

        # P1 -- ONE BYTE differs inside the canonical lineage.
        cfg, f = _fixture(t)
        with open(f["c2"], "r+b") as fh:
            fh.seek(2)
            fh.write(b"X")
        code, report = check(cfg, emit=False)
        rep["P1_one_byte_flip_in_canonical_lineage"] = _fired(
            code, report, "DIVERGENCE in the canonical lineage")
        rep["P1_one_byte_flip_in_canonical_lineage"]["drifted_paths"] = [
            os.path.relpath(p, t) for p in report.get("lineage_canonical", {})
            if report["lineage_canonical"][p] != report.get("canonical_sha256")]

        # P2 -- an UNKNOWN copy appears on disk.
        cfg, f = _fixture(t)
        # INSIDE the fixture's own sweep root (cfg.roots[0]), or the sweep never sees it
        # and P2 stops firing for a reason that has nothing to do with the instrument.
        stray = os.path.join(cfg.roots[0], "stray", TARGET)
        os.makedirs(os.path.dirname(stray), exist_ok=True)
        shutil.copyfile(f["c1"], stray)
        code, report = check(cfg, emit=False)
        rep["P2_unknown_copy_detected"] = _fired(code, report, "UNKNOWN COPY")
        rep["P2_unknown_copy_detected"]["unknown"] = [
            os.path.relpath(p, t) for p in report["unknown_copies"]]

        # P3 -- a KNOWN copy vanishes. NOT A RESULT, never "no divergence".
        cfg, f = _fixture(t)
        os.remove(f["c3"])
        code, report = check(cfg, emit=False)
        rep["P3_absent_copy_is_NOT_A_RESULT"] = _fired(code, report, "NOT A RESULT")
        rep["P3_absent_copy_is_NOT_A_RESULT"]["missing"] = [
            os.path.relpath(p, t) for p in report["missing_known_copies"]]
        rep["P3_absent_copy_is_NOT_A_RESULT"]["note"] = (
            "an absent copy is an UNMEASURED difference, never an absent one")

        # P4 -- the ast self-check rejects a file carrying a bare assert.
        bad = os.path.join(t, "has_assert.py")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("def g(x):\n    assert x > 0\n    return x\n")
        try:
            ast_self_check(bad)
            fired4 = False
        except Refusal:
            fired4 = True
        rep["P4_ast_self_check_rejects_bare_assert"] = {"fired": fired4}

        # P5 -- DRIFT INSIDE THE SECOND LINEAGE, which is never synced to the canonical.
        cfg, f = _fixture(t)
        with open(f["s2"], "ab") as fh:
            fh.write(b"# drifted\n")
        code, report = check(cfg, emit=False)
        rep["P5_second_lineage_drift"] = _fired(
            code, report, "DIVERGENCE in the second")
        rep["P5_second_lineage_drift"]["consistency"] = report[
            "lineage_second_consistency"]

        # P6 -- A ONE-MEMBER SECOND LINEAGE MUST DECLARE ITSELF VACUOUS, NOT PASS.
        # This is the production configuration after the 2026-09-03 removal. The plant
        # requires the word VACUOUS in the report, because a silent pass over a set that
        # cannot disagree with itself is a fail-open wearing a pass.
        cfg, f = _fixture(t)
        cfg1 = dataclasses.replace(
            cfg, second_lineage=(f["s1"],),
            known=tuple(p for p in cfg.known if p != f["s2"]))
        os.remove(f["s2"])
        code, report = check(cfg1, emit=False)
        rep["P6_single_member_lineage_declares_VACUOUS"] = {
            "exit_code": code,
            "n_present": report["lineage_second_n_present"],
            "consistency": report["lineage_second_consistency"],
            "fired": (report["lineage_second_n_present"] == 1
                      and "VACUOUS" in report["lineage_second_consistency"]
                      and code == 0),
            "note": "not a refusal -- a true statement about a check that cannot fail"}

    ok = all(v["fired"] for v in rep.values())
    print(json.dumps({"selftest": rep, "all_plants_fired": ok,
                      "plants_driving_shipped_check": ["P0", "P1", "P2", "P3", "P5", "P6"],
                      "plants_driving_helper_only": ["P4"]},
                     indent=2, sort_keys=True))
    return 0 if ok else 2


def report_call_site():
    """Report what the caller's SOURCE says about this checker -- and what that cannot prove.

    THIS FUNCTION MAKES NO CLAIM ABOUT INVOCATION, and it used to. Until 2026-09-03 it was
    called `--prove-invocation` and the module docstring promised it "demonstrates that the
    CALLER actually runs it, by showing that a planted divergence goes UNDETECTED when the
    call site is removed and IS detected when it is restored." The implementation was
    `"check_converter_copies" in src` -- a substring test that a mention in a comment, a
    docstring or dead code satisfies. That is not hypothetical: `scripts/lab_check.py:573`
    already names `ugrid_to_foam.py` inside a docstring. A frozen file asserting a
    protection it does not provide is the SECOND instance of that shape in this converter's
    story; the first was the converter's own docstring claiming "the caller's own
    byte-budget assertion below is what actually proves the choice right" while that
    assertion sat only inside the `if fortran:` branch, leaving raw C streams unguarded.

    So the claim was withdrawn rather than the check strengthened, on the principle that AN
    HONEST WEAK CHECK BEATS A DISHONEST STRONG-SOUNDING ONE. What is reported is a
    tokenised mention count, split by whether the name appears as code, inside a string
    literal, or inside a comment -- because those three are not equally good evidence and
    the old test could not tell them apart. NONE OF THEM IS PROOF THAT ANYTHING RAN.

    AND THE MENTION IS THE WRONG QUESTION ANYWAY. Measured 2026-09-03: `lab_check.py` holds
    no list of checks. `enumerate_candidates()` unions `git ls-tree -r HEAD` with an
    `os.walk` over `CHECK_DIRS = ("scripts", "sdk/tests")`, so this file is admitted BECAUSE
    IT LIVES IN `scripts/` AND ITS `main()` CAN EXIT NON-ZERO -- with no call site at all.
    `python3 scripts/lab_check.py --list --only check_converter_copies` reported exactly
    that on 2026-09-03, while this file was still untracked. Only observing a run proves a
    run; that is what that command is for.
    """
    caller = "/home/ubuntu/Certonomous/scripts/lab_check.py"
    me = "check_converter_copies"
    out = {
        "caller": caller,
        "this_reports": "mentions of the checker's name in the caller's source, by "
                        "token kind",
        "this_does_NOT_prove": "that the caller ever runs this checker. A mention is not "
                               "an invocation. Only observing a run proves a run.",
        "actual_invocation_path": (
            "lab_check.py enumerates scripts/ and sdk/tests/ by os.walk (CHECK_DIRS, "
            "lab_check.py:437) unioned with git ls-tree -r HEAD, and admits any file whose "
            "main() can exit non-zero. No call site is required. Verify with: "
            "python3 scripts/lab_check.py --list --only check_converter_copies"),
        "mentions_in_code": 0,
        "mentions_in_string_literals": 0,
        "mentions_in_comments": 0,
        "mentions_total": 0,
    }
    if not os.path.isfile(caller):
        out["evidence"] = f"caller ABSENT: {caller} -- NOT A RESULT, not 'unmentioned'"
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    src = open(caller, encoding="utf-8", errors="replace").read()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError) as e:
        out["evidence"] = (f"NOT A RESULT: the caller could not be tokenised ({e}), so this "
                           f"report cannot distinguish a code mention from a comment.")
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    for tok in toks:
        if me not in tok.string:
            continue
        n = tok.string.count(me)
        if tok.type == tokenize.COMMENT:
            out["mentions_in_comments"] += n
        elif tok.type == tokenize.STRING:
            out["mentions_in_string_literals"] += n
        elif tok.type == tokenize.NAME:
            out["mentions_in_code"] += n
    out["mentions_total"] = (out["mentions_in_code"]
                             + out["mentions_in_string_literals"]
                             + out["mentions_in_comments"])

    if out["mentions_total"] == 0:
        out["evidence"] = (
            "the caller's source does not mention this checker anywhere. It is NOT wired "
            "by a call site -- but see actual_invocation_path: on this box it is admitted "
            "by enumeration regardless, so 'no mention' does NOT mean 'never runs'.")
    elif out["mentions_in_code"] == 0:
        out["evidence"] = (
            f"the name appears {out['mentions_total']} time(s) but NEVER as code -- only "
            f"in string literals and/or comments. This is exactly what the withdrawn "
            f"--prove-invocation would have reported as 'wired'.")
    else:
        out["evidence"] = (
            f"the name appears as code {out['mentions_in_code']} time(s). That is "
            f"consistent with an invocation and does not establish one; read the call.")
    print(json.dumps(out, indent=2, sort_keys=True))
    # Exit 0: this is a REPORT, not a gate. It carries no finding about the lab, so it
    # must not hand lab_check a FAIL (EXIT_CONTRACT maps 2 -> FAIL) for a question it
    # was never able to answer.
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted controls and exit")
    ap.add_argument("--report-call-site", action="store_true",
                    help="report mentions of this checker in scripts/lab_check.py, by "
                         "token kind. Reports; does NOT prove invocation.")
    a = ap.parse_args()
    try:
        if a.selftest:
            sys.exit(selftest())
        if a.report_call_site:
            sys.exit(report_call_site())
        sys.exit(check(as_json=a.json)[0])
    except Refusal as e:
        print(f"REFUSAL: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
