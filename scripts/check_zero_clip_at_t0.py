#!/usr/bin/env python3
"""check_zero_clip_at_t0.py -- STATIC pre-freeze check for positivity-clip solvers.

WHAT IT ENFORCES (the DMR L5 miscalibration class)
--------------------------------------------------
A positivity-preserving solver that floors internal energy `e` (hence temperature T)
with an element-wise clip `e = min(max(e, eMin_bound), eMax_bound)` MUST carry a
**t=0 zero-clip startup assertion**: on the PHYSICAL initial field, it must count the
cells that would be clipped by the low floor, reduce that count across ranks, and
REFUSE (FatalError / non-zero exit) if it is > 0. A correctly-calibrated positivity
floor is INERT on the physical initial field by construction (it clips 0 cells at
t=0); if it clips any physical cell at t=0 the floor sits ABOVE the physical field and
the run measures the instrument defect, not the model.

This is exactly the DMR-R3 L5 defect: `eMin_bound = -532.410` was derived from a HAND
e-formula `e = Cv*(T-298.15)` (an ASSUMED Tref=298.15/eref=0), but OpenFOAM's ACTUAL
hConst ambient `e ~ -743.589` sat far below it, so the floor clipped 100% of cells
from the first timestep and corrupted the run -> NOT A RESULT
(DMR_R3_L5_BOUNDED_T_RESULTS.md). A t=0 zero-clip assertion would have caught it before
a core-minute was spent -- and would catch ANY future floor miscalibration at runtime,
whatever the derivation. This check turns that repeatedly-payable lesson into an
enforced pre-freeze invariant: it REFUSES (nonzero exit) if a solver defines and USES a
low positivity clip bound but has NO t=0 zero-clip startup assertion.

THE RULE (single decisive comparison, honest and conservative)
--------------------------------------------------------------
For each source file, over the text with C/C++ comments stripped:
  * CLIP PRESENT  := a low clip bound symbol (default `eMin_bound`) is both DEFINED
    and USED in an element-wise floor (`min(max(e, <bound>...` or a `< <bound>.value()`
    comparison).
  * T0 ASSERTION PRESENT := there is a cell-vs-floor comparison `< <bound>.value()`,
    a cross-rank count reduction (`returnReduce(`), AND a `FatalError` -- i.e. a guard
    that counts clipped cells and aborts. (Necessary signals of the assertion; it is
    the author's job, verified by check-1, that this guard runs on the INITIAL field
    before the time loop -- see the honesty section.)
  * FIELD ANCHOR PRESENT (advisory) := the low bound is derived from the ACTUAL field
    via a global reduction over the energy field (`gMin(` / `gMax(` applied to a
    `primitiveField()` / `he()` / `e`), NOT solely from an assumed thermodynamic
    reference. Reported to steer the fix; the DECISIVE refuse is the missing assertion.

The check REFUSES (exit 3) iff CLIP PRESENT and NOT T0 ASSERTION PRESENT. A file with
no positivity clip trivially PASSES (nothing to guard). The t=0 assertion, if present,
catches ANY miscalibration at runtime -- including an assumed-reference floor above the
field (the L5 state) -- so its PRESENCE is the necessary static guarantee.

WHAT A STATIC CHECK CANNOT CATCH (stated honestly)
--------------------------------------------------
  * It does NOT prove the assertion runs on the INITIAL field BEFORE the time loop,
    nor that it reduces the RIGHT count -- it detects the assertion's necessary
    signals (a floor comparison + a rank reduction + a FatalError). Placement and
    correctness are a check-1 human read. This is a NECESSARY, not sufficient, guard:
    it makes "no t=0 assertion at all" impossible to freeze silently.
  * It is text-based (C++ is not Python-AST-parseable). Comments are stripped so a
    comment describing the bug cannot trigger it, but an assertion assembled by macro
    or hidden in an unusual idiom may be missed. Extend the signal regexes if a solver
    uses a different clip/reduce/abort idiom.
  * The FIELD ANCHOR signal is advisory: a solver may calibrate correctly by another
    route as long as the t=0 assertion is present to catch a miscalibration.

PLANTED-CONTROL DISCIPLINE (CLAUDE.md rule 3 family)
----------------------------------------------------
`--selftest` runs the checker against synthetic fixtures held in this file: an
L5-style fixture (clip + hand-formula floor, NO assertion) that the checker MUST
REFUSE, and an L5b-style fixture (clip + field-anchored floor + t=0 assertion) that
it MUST PASS, plus a no-clip fixture (MUST PASS) and a clip-with-assertion-but-
assumed-reference fixture (MUST PASS -- the assertion is what makes it safe). A
checker that cannot be shown to FIRE is not evidence.

EXITS: 0 PASS | 3 REFUSE (clip without t=0 assertion) | 2 usage | 4 read/parse error.
SUBMISSIONS PARKED; nothing leaves the box.
"""
import re
import sys
import argparse

DEFAULT_LOW_BOUND = "eMin_bound"


def strip_comments(src):
    """Remove C/C++ // and /* */ comments so comment prose cannot fire the signals.
    String-literal contents are left intact (clip/abort idioms live in code, and the
    signals we match do not occur meaningfully inside string literals here)."""
    # block comments
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    # line comments
    src = re.sub(r"//[^\n]*", " ", src)
    return src


def analyse(src, low_bound=DEFAULT_LOW_BOUND):
    """Return a report dict of the detected signals for one comment-stripped source."""
    b = re.escape(low_bound)
    code = strip_comments(src)

    bound_defined = re.search(r"\b" + b + r"\b", code) is not None
    # a real cell-vs-floor comparison: a single `<` (NOT the `<<` stream operator)
    # followed by the bound symbol. The negative lookbehind drops `<< eMin_bound`
    # (an Info/Pout stream insertion), which is not a comparison.
    cmp_re = r"(?<!<)<\s*" + b + r"\b"
    # element-wise floor usage: min(max(e, eMin_bound ...  OR  a real `< eMin_bound`
    clip_used = (
        re.search(r"min\s*\(\s*max\s*\([^,]*,\s*" + b, code) is not None
        or re.search(cmp_re, code) is not None
    )
    clip_present = bound_defined and clip_used

    # t=0 assertion necessary signals
    has_floor_cmp = re.search(cmp_re, code) is not None
    has_rank_reduce = re.search(r"\breturnReduce\s*\(", code) is not None
    has_fatal = re.search(r"\bFatalError", code) is not None
    t0_assertion_present = has_floor_cmp and has_rank_reduce and has_fatal

    # advisory: field-anchored derivation (global reduction over the energy field)
    field_anchor_present = (
        re.search(r"\bgMin\s*\([^)]*(primitiveField|\bhe\b|\be\b)", code) is not None
        or re.search(r"\bgMax\s*\([^)]*(primitiveField|\bhe\b|\be\b)", code) is not None
    )
    # advisory: assumed-reference hand formula (a hardcoded Tref literal in the bound)
    assumed_ref_handformula = (
        re.search(r"\bTref\w*\s*=\s*[0-9]", code) is not None
        or re.search(r"\(\s*TMin[^)]*-\s*[0-9]+(\.[0-9]+)?\s*\)", code) is not None
    )

    return {
        "low_bound": low_bound,
        "clip_present": clip_present,
        "t0_assertion_present": t0_assertion_present,
        "field_anchor_present": field_anchor_present,
        "assumed_ref_handformula": assumed_ref_handformula,
        "_signals": {
            "bound_defined": bound_defined,
            "clip_used": clip_used,
            "has_floor_cmp": has_floor_cmp,
            "has_rank_reduce": has_rank_reduce,
            "has_fatal": has_fatal,
        },
    }


def verdict(rep):
    """PASS/REFUSE from a report. REFUSE iff a clip is present with no t=0 assertion."""
    if not rep["clip_present"]:
        return "PASS", "no positivity clip present (nothing to guard)"
    if not rep["t0_assertion_present"]:
        anchor = "field-anchored" if rep["field_anchor_present"] else "NOT field-anchored"
        hand = " assumed-reference hand-formula floor detected;" if rep["assumed_ref_handformula"] else ""
        return "REFUSE", (
            "positivity clip on '%s' is present but there is NO t=0 zero-clip startup "
            "assertion (need a cell<floor comparison + returnReduce count + FatalError)."
            "%s The floor is %s. A correctly-calibrated floor clips 0 cells at t=0; add "
            "the assertion so a miscalibration (the DMR-L5 class) cannot be frozen."
            % (rep["low_bound"], hand, anchor)
        )
    note = "" if rep["field_anchor_present"] else \
        " (advisory: floor is NOT field-anchored; the t=0 assertion is what guarantees safety)"
    return "PASS", ("positivity clip present WITH a t=0 zero-clip startup assertion"
                    " (floor comparison + rank reduction + FatalError)%s" % note)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def check_solver(paths, low_bound=DEFAULT_LOW_BOUND):
    """AGGREGATE across all given files as ONE solver: the clip may live in boundE.H
    while the t=0 assertion lives in createFields.H, so a single verdict is taken over
    the OR of the signals across every file. Pass a solver's whole source (e.g. both
    createFields.H and boundE.H, or a src dir's files) for a correct read."""
    try:
        reps = [analyse(_read(p), low_bound) for p in paths]
    except (OSError, UnicodeDecodeError) as e:
        # FAIL-CLOSED: a target that cannot be read (missing / a directory /
        # permission-denied -> OSError; a non-UTF-8/binary target -> UnicodeDecodeError,
        # which is NOT an OSError and previously escaped as an uncaught traceback) is
        # NEVER silently passed. A check that cannot see its target refuses (exit 4),
        # it does not PASS. (rule 3 family: a zero from a reader that cannot read is
        # not evidence.)
        sys.stderr.write("check_zero_clip_at_t0: cannot read target -- REFUSE (exit 4): %s\n" % e)
        return 4
    agg = {
        "low_bound": low_bound,
        "clip_present": any(r["clip_present"] for r in reps),
        "t0_assertion_present": any(r["t0_assertion_present"] for r in reps),
        "field_anchor_present": any(r["field_anchor_present"] for r in reps),
        "assumed_ref_handformula": any(r["assumed_ref_handformula"] for r in reps),
    }
    v, reason = verdict(agg)
    label = paths[0] if len(paths) == 1 else "%s (+%d file(s))" % (paths[0], len(paths) - 1)
    if v == "REFUSE":
        sys.stderr.write("REFUSE (exit 3): %s -- %s\n" % (label, reason))
        return 3
    sys.stdout.write("PASS: %s -- %s\n" % (label, reason))
    return 0


# --------------------------------------------------------------------------
# PLANTED CONTROL (rule 3 family): the checker must be shown able to FIRE
# --------------------------------------------------------------------------
_FX_L5BUG = r'''
    // L5 defect: hand-formula floor, NO t=0 assertion
    const scalar Cv_bound = 2.5 - 8314.47/11640.3;
    const scalar Tref_bound = 298.15;
    const dimensionedScalar eMin_bound("eMin_bound", dimEnergy/dimMass,
        Cv_bound*(TMin.value() - Tref_bound));
    // ... in the time loop:
    e = min(max(e, eMin_bound), eMax_bound);
'''

_FX_L5B = r'''
    // L5b fix: field-anchored floor + t=0 zero-clip startup assertion
    const scalar eMinInit = gMin(e.primitiveField());
    const dimensionedScalar eMin_bound("eMin_bound", dimEnergy/dimMass,
        eMinInit - Cv_bound*(TMinInit - TMin.value()));
    {
        const scalarField& e0 = e.primitiveField();
        label nClip0Local = 0;
        forAll(e0, celli) { if (e0[celli] < eMin_bound.value()) ++nClip0Local; }
        const label nClip0 = returnReduce(nClip0Local, sumOp<label>());
        if (nClip0 > 0) { FatalErrorInFunction << "REFUSE: clip fires at t=0" << exit(FatalError); }
    }
    e = min(max(e, eMin_bound), eMax_bound);
'''

_FX_NOCLIP = r'''
    // no positivity clip at all
    e = rhoE/rho - 0.5*magSqr(U);
    thermo.correct();
'''

_FX_HANDFORMULA_WITH_ASSERT = r'''
    // assumed-reference floor BUT with a t=0 assertion -> safe (assertion catches it)
    const scalar Tref_bound = 298.15;
    const dimensionedScalar eMin_bound("eMin_bound", dimEnergy/dimMass,
        Cv_bound*(TMin.value() - Tref_bound));
    {
        const scalarField& e0 = e.primitiveField();
        label n = 0;
        forAll(e0, celli) { if (e0[celli] < eMin_bound.value()) ++n; }
        if (returnReduce(n, sumOp<label>()) > 0) { FatalErrorInFunction << "abort" << exit(FatalError); }
    }
    e = min(max(e, eMin_bound), eMax_bound);
'''


def _refuses(src):
    rep = analyse(src)
    v, _ = verdict(rep)
    return v == "REFUSE"


def selftest():
    checks = [
        ("L5 bug: clip + hand-formula floor, NO assertion -> must REFUSE", _FX_L5BUG, True),
        ("L5b: clip + field-anchored floor + t=0 assertion -> must PASS", _FX_L5B, False),
        ("no clip present -> must PASS", _FX_NOCLIP, False),
        ("assumed-ref floor WITH t=0 assertion -> must PASS", _FX_HANDFORMULA_WITH_ASSERT, False),
    ]
    all_ok = True
    for label, src, must_fire in checks:
        fired = _refuses(src)
        ok = (fired == must_fire)
        all_ok = all_ok and ok
        print("  [%s] %s  (refused=%s, expected_refuse=%s)"
              % ("OK" if ok else "FAIL", label, fired, must_fire))
    # advisory signal spot-check: L5b must read as field-anchored; L5 bug must not
    if analyse(_FX_L5B)["field_anchor_present"] is not True:
        print("  [FAIL] L5b fixture should read as field-anchored"); all_ok = False
    if analyse(_FX_L5BUG)["field_anchor_present"] is not False:
        print("  [FAIL] L5 bug fixture should read as NOT field-anchored"); all_ok = False
    if all_ok:
        print("SELFTEST OK -- the checker FIRES on a clip with no t=0 assertion and "
              "PASSES on a clip that carries one.")
        return 0
    print("SELFTEST FAILED -- the checker did not behave as a planted control requires.")
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Static pre-freeze check: a positivity-clip solver must carry a "
                    "t=0 zero-clip startup assertion (DMR-L5 miscalibration class).")
    p.add_argument("files", nargs="*",
                   help="a solver's source files, read together as ONE solver "
                        "(e.g. createFields.H boundE.H)")
    p.add_argument("--low-bound", default=DEFAULT_LOW_BOUND,
                   help="low clip bound symbol to look for (default: eMin_bound)")
    p.add_argument("--selftest", action="store_true", help="run the planted-control selftest and exit")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.files:
        sys.stderr.write("usage: check_zero_clip_at_t0.py <file> [<file> ...]  |  --selftest\n")
        return 2
    return check_solver(args.files, args.low_bound)


if __name__ == "__main__":
    sys.exit(main())
