#!/usr/bin/env python3
"""The Act C admissibility source: what T25R4 ACTUALLY GRADED, and nothing else.

WHY THIS FILE EXISTS, AND WHY IT IS NOT A WIDER THRESHOLD.  Act C's withholding
guard (`check_actC_gate_screen.py`) refuses every kelvin magnitude at or above
0.1 K and every decimal in the absolute-temperature band [200, 500].  Sanaa
approved (commit `0fe482c4`, 2026-09-01) an Act C that reports T25R4's
temperatures once they are graded, which means that refusal has to open.

THE OBVIOUS IMPLEMENTATION IS THE WRONG ONE.  Raising `KELVIN_MAX` from 0.1 to
some larger number admits EVERY value in the widened band -- including a number
nobody graded, a number typed by hand into a sheet, and the adiabatic bounds
this act has been withholding since it was written.  A band cannot tell a
graded value from a plausible one.  So the guard does not get a wider band.  It
gets an ALLOWLIST, and the allowlist is DERIVED FROM THE GRADED ARTEFACT rather
than maintained by a person.  A hand-maintained allowlist is a hole with a
comment on it.

THE PROPERTY THAT MAKES THIS SELF-ENFORCING, AND IT IS THE POINT OF THE FILE:

    IF T25R4 HAS NOT GRADED, THE DERIVED SET IS EMPTY, AND A GUARD CONSULTING
    AN EMPTY SET BEHAVES BIT-IDENTICALLY TO THE GUARD BEFORE THIS FILE EXISTED.

Every branch below fails CLOSED.  No artefact, an uncommitted artefact, an
unparseable artefact, a wrong rung, an absent declaration, a run whose verdict
is not one this lab reports -- each of those yields the EMPTY set, not a
partial one and not an error the caller might swallow.  The fallback ending
Sanaa registered ("the team tells the user their convergence study is on its
way") is therefore enforced by the instrument, not by anyone remembering it.
The fallback is the DEFAULT; the reporting act is the exception that a graded
artefact has to earn.

THE ARTEFACT IS READ OUT OF GIT, NOT OFF THE DISK.  `verification/runs/` is a
shared working tree and an uncommitted file there is somebody's unfinished
work.  A grading that has not been committed has not been boarded, and a screen
must not depend on a file that `git checkout` would remove.  So the reader is
`git cat-file blob HEAD:<path>`; a working-tree copy is invisible to it.

TWO CROSS-CHECKS THAT SEPARATE THIS FROM A CURATED LIST.  The graded artefact
carries an explicit `screen_admissible_K` declaration -- the comparator saying
which quantities are reportable.  A declaration alone would be exactly the
hand-written list this file exists to avoid, so:

  1. each declared entry names a RUN, and that run's verdict in the same
     artefact must be one this lab reports (`PASS` or `GATE REACHED`); and
  2. each declared VALUE must actually occur as a number inside that run's own
     graded subtree.

A value declared but not present in the graded body is not "unbacked and
dropped" -- it is a REFUSAL (`AdmissionRefused`), because a number that appears
in the declaration and nowhere in the grading is a number someone typed.
Dropping it silently would make the tampering invisible; refusing makes it a
stop.

THE BARRED SET IS CHECKED FIRST AND NO ALLOWLIST REACHES IT.  The adiabatic
bounds are analytic consequences of the energy input, not solver outputs; they
disclose the scale of the answer by the back door, which is why the guard has
withheld them from the start.  They stay refused unconditionally.

WHAT THIS FILE DOES NOT DECIDE.  It says which NUMERIC TOKENS may be rendered.
It does not relax the banned claim phrases, the Celsius ban, the language
rules, or the barred figures.  Those are separate policy and are not re-scoped
by Sanaa's 2026-09-01 approval, which was put to her in terms of T25R4's
numbers.

    python3 actC_graded_admission.py --selftest     # both directions, offline
    python3 actC_graded_admission.py                # report the live state
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

#: The graded artefact, by repository-relative path.  The name follows the
#: family's existing convention -- Act A reads `T23_runs/T23_GRADE.json` -- so
#: this is the T-family's own naming carried forward, not a new one invented
#: for this guard.
GRADE_RELPATH = ("verification/runs/T-family/T25R4_MODULE_runs/"
                 "T25R4_GRADE.json")

#: The rung this admission source will accept and no other.  A graded artefact
#: from a different rung is a different registration with a different threshold
#: and does not admit anything here.
RUNG = "T25R4"

#: The verdicts whose values this lab reports.  `NOT A RESULT`, `GATE FAIL`,
#: `BLOCKED` and `PENDING` are absent deliberately: rule 5 makes a row whose
#: triple is not CONVERGING NOT A RESULT whatever its value says, and a value
#: this lab will not report in a record is not a value it puts on a screen.
REPORTABLE_VERDICTS = frozenset({"PASS", "GATE REACHED"})

#: Refused unconditionally, whatever any allowlist says.  These are ANALYTIC
#: BOUNDS on the temperature rise, computed from the registered volumetric heat
#: input, not outputs of any solve -- `T25R4_PREREGISTRATION.md` section 3.1
#: registers the integral 2.698750e+07 J/m3 and the bound 10.7950 K, and the
#: Act C gate sheet has withheld 2.400 / 10.800 K since it was written on the
#: same reasoning: they tell a viewer the scale of the answer without any run
#: having earned it.  A graded artefact cannot make an analytic bound a
#: measurement, so no derived set reaches these.
BARRED_K = (2.400, 10.800, 10.7950)

#: The five figures of the 0.4 K run Sanaa barred.  The content specification
#: (section 0) records that nothing mechanical stopped them reaching a screen --
#: only a written rule did.  Named here so the guard can refuse the FILE rather
#: than hoping to catch its numbers, because a barred run's figure is barred by
#: provenance and no numeric test recovers that.
BARRED_FIGURE_BASENAMES = (
    "actc_cell_histories.pdf",
    "actc_field_snapshots.pdf",
    "actc_pack_uniformity.pdf",
    "actc_per_cell_table.pdf",
    "actc_step_independence.pdf",
)


class AdmissionRefused(Exception):
    """The graded artefact declares a value its own grading does not contain."""


# --------------------------------------------------------------------------
# THE MATCH RULE, stated rather than implied
# --------------------------------------------------------------------------

def _decimals(token):
    """How many digits the rendered token carries after its point, or None."""
    m = re.match(r"^-?\d[\d,]*\.(\d+)$", token.strip())
    return len(m.group(1)) if m else None


def _as_float(token):
    try:
        return float(token.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def matches_at_token_precision(token, value):
    """Is `token` the rendering of `value` at the token's OWN precision?

    THE TOLERANCE IS THE TOKEN'S, NOT A CONSTANT.  A sheet prints 298.87312 as
    "298.9" or "298.873" depending on its own format, and a fixed relative
    tolerance either refuses the first or admits a neighbour of the second.
    So the test is the exact statement of "this token is that value, printed":
    half a unit in the token's last place, symmetric, plus one part in 1e12 for
    binary representation.

    A token with NO decimal point is never matched.  An integer kelvin token
    ("300 K") carries so little precision that admitting it would admit a whole
    unit-wide band, and no graded quantity on these screens is reported to zero
    decimals.
    """
    d = _decimals(token)
    if d is None or d < 1:
        return False
    t = _as_float(token)
    if t is None:
        return False
    tol = 0.5 * (10.0 ** -d) * (1.0 + 1e-12)
    return abs(float(value) - t) <= tol


def token_is_barred(token, barred=BARRED_K):
    """Checked BEFORE any allowlist.  No derived set reaches these."""
    return any(matches_at_token_precision(token, b) for b in barred)


def token_admissible(token, admissible, barred=BARRED_K):
    """The whole of the loosening, in one function.

    With `admissible` empty this returns False for every token, which is what
    makes the guard's behaviour bit-identical to its behaviour before this file
    existed.  That is not an accident of the loop; it is the reason the
    allowlist is a set and not a band.
    """
    if token_is_barred(token, barred):
        return False
    return any(matches_at_token_precision(token, v) for v in admissible)


# --------------------------------------------------------------------------
# THE DERIVATION
# --------------------------------------------------------------------------

def _numeric_leaves(node, out):
    if isinstance(node, dict):
        for v in node.values():
            _numeric_leaves(v, out)
    elif isinstance(node, (list, tuple)):
        for v in node:
            _numeric_leaves(v, out)
    elif isinstance(node, bool):
        return
    elif isinstance(node, (int, float)):
        out.append(float(node))


def derive_from_text(text):
    """Derive the admissible set from the graded artefact's BYTES.

    Returns `(values, provenance)`.  `values` is a tuple of floats, empty
    whenever anything at all is missing or malformed; `provenance` is one
    sentence naming why the set is what it is, and the guard prints it, so a
    reader always knows which regime the sweep ran in rather than inferring it
    from a hit count.

    Raises `AdmissionRefused` for the one case that is not a default-deny: a
    declared value with no backing anywhere in its run's grading.
    """
    if not text:
        return (), "no graded artefact: nothing is admitted"
    try:
        doc = json.loads(text)
    except (ValueError, TypeError) as exc:
        return (), ("the graded artefact does not parse (%s): nothing is "
                    "admitted" % exc)
    if not isinstance(doc, dict):
        return (), "the graded artefact is not an object: nothing is admitted"
    if doc.get("rung") != RUNG:
        return (), ("the graded artefact is rung %r, not %r: nothing is "
                    "admitted" % (doc.get("rung"), RUNG))

    results = doc.get("results")
    if not isinstance(results, dict) or not results:
        return (), ("the graded artefact carries no per-run results: nothing "
                    "is admitted")

    declared = doc.get("screen_admissible_K")
    if not isinstance(declared, list) or not declared:
        return (), ("the graded artefact declares no reportable quantity: "
                    "nothing is admitted")

    values = []
    unbacked = []
    skipped = 0
    for entry in declared:
        if not isinstance(entry, dict):
            skipped += 1
            continue
        run = entry.get("run")
        value = entry.get("value")
        if not isinstance(run, str) or not isinstance(value, (int, float)) \
                or isinstance(value, bool):
            skipped += 1
            continue
        graded = results.get(run)
        if not isinstance(graded, dict):
            skipped += 1
            continue
        if graded.get("verdict") not in REPORTABLE_VERDICTS:
            skipped += 1
            continue
        leaves = []
        _numeric_leaves(graded, leaves)
        # The declared value must OCCUR in the grading.  Exact equality on the
        # float is right here: both sides come from the same JSON document, so
        # a declaration that quotes its own grading matches bit for bit, and
        # one that does not was typed.
        if not any(leaf == float(value) for leaf in leaves):
            unbacked.append((run, float(value), entry.get("quantity")))
            continue
        values.append(float(value))

    if unbacked:
        raise AdmissionRefused(
            "the graded artefact DECLARES %d value(s) that its own grading "
            "does not contain: %s. A number in the declaration and nowhere in "
            "the grading was typed, not measured, and this refuses rather "
            "than dropping it -- a dropped entry would make the tampering "
            "invisible." % (len(unbacked), unbacked))

    if not values:
        return (), ("no declared quantity survived the run-verdict and "
                    "backing checks: nothing is admitted")
    note = ("%d value(s) derived from the committed grading of %s"
            % (len(values), RUNG))
    if skipped:
        note += (" (%d declared entr(y/ies) skipped: malformed, or naming a "
                 "run this lab does not report)" % skipped)
    return tuple(values), note


def _git_blob(repo, relpath):
    """The COMMITTED bytes of `relpath`, or None. A working-tree copy is
    invisible here on purpose: an uncommitted grading has not been boarded."""
    try:
        out = subprocess.run(["git", "-C", repo, "cat-file", "blob",
                              "HEAD:" + relpath],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             check=False)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace")


def derive(repo=REPO, relpath=GRADE_RELPATH):
    """The live derivation. Empty whenever T25R4 has not graded and committed."""
    text = _git_blob(repo, relpath)
    if text is None:
        return (), ("%s is not committed at HEAD: nothing is admitted, and "
                    "every temperature is refused exactly as before this "
                    "allowlist existed" % os.path.basename(relpath))
    return derive_from_text(text)


# --------------------------------------------------------------------------
# CONTROLS -- BOTH DIRECTIONS.  A loosening not shown to still refuse is not
# a guard.
# --------------------------------------------------------------------------

_PLANTED_GRADED = {
    "rung": "T25R4",
    "frozen_document": "docs/campaigns/T-family/T25R4_PREREGISTRATION.md",
    "results": {
        "S2": {"verdict": "PASS",
               "Q2_peak_module_K": 298.873120,
               "Q1_outlet_area_mean_K": 295.114000,
               "roache": {"classification": "CONVERGING", "p": 1.04}},
        "S1": {"verdict": "NOT A RESULT",
               "Q2_peak_module_K": 297.500000},
    },
    "screen_admissible_K": [
        {"run": "S2", "quantity": "peak module temperature",
         "value": 298.873120},
        {"run": "S2", "quantity": "coolant outlet area-mean temperature",
         "value": 295.114000},
    ],
}


def _chk(fails, label, ok):
    print("  %-4s %s" % ("ok" if ok else "FAIL", label))
    if not ok:
        fails.append(label)


def selftest():
    fails = []

    print("DIRECTION 1 -- EMPTY GRADED SET.  The guard must refuse every "
          "temperature, identically to its behaviour before this file.")
    empty, why = derive_from_text("")
    _chk(fails, "no artefact derives the EMPTY set", empty == ())
    print("       provenance: %s" % why)
    for token in ("298.873", "293.0", "295.114", "2.384", "10.8", "0.42",
                  "376.757834772", "298.9"):
        _chk(fails, "with an empty set %r is REFUSED" % token,
             not token_admissible(token, empty))
    for bad, label in ((json.dumps({"rung": "T25R2"}), "a different rung"),
                       ("{not json", "an unparseable artefact"),
                       (json.dumps({"rung": "T25R4"}), "no results block"),
                       (json.dumps({"rung": "T25R4", "results": {"S2": {
                           "verdict": "PASS", "x": 1.0}}}),
                        "no declaration")):
        vals, note = derive_from_text(bad)
        _chk(fails, "%s derives the EMPTY set" % label, vals == ())
    vals, _ = derive_from_text(json.dumps({
        "rung": "T25R4",
        "results": {"S1": {"verdict": "NOT A RESULT",
                           "Q2_peak_module_K": 297.5}},
        "screen_admissible_K": [{"run": "S1", "quantity": "peak",
                                 "value": 297.5}]}))
    _chk(fails, "a value graded NOT A RESULT is NOT admitted", vals == ())

    print("\nDIRECTION 2 -- PLANTED GRADED SET.  The guard must admit exactly "
          "the planted values and still refuse a neighbour.")
    planted, why = derive_from_text(json.dumps(_PLANTED_GRADED))
    print("       provenance: %s" % why)
    _chk(fails, "the planted grading derives exactly 2 values",
         sorted(planted) == sorted([298.873120, 295.114000]))
    _chk(fails, "the planted value 298.873120 is ADMITTED",
         token_admissible("298.873120", planted))
    _chk(fails, "the same value printed to 3 decimals is ADMITTED",
         token_admissible("298.873", planted))
    _chk(fails, "the same value printed to 1 decimal is ADMITTED",
         token_admissible("298.9", planted))
    _chk(fails, "the second planted value 295.114 is ADMITTED",
         token_admissible("295.114", planted))
    # THE NEGATIVE ARM.  A loosening that admits its own plant proves nothing
    # about what it still refuses.
    for token in ("299.873", "298.773", "298.8", "297.500000", "293.0",
                  "376.757834772", "0.42", "5.873"):
        _chk(fails, "a NON-graded neighbour %r is still REFUSED" % token,
             not token_admissible(token, planted))
    _chk(fails, "a value graded on a run whose verdict is NOT A RESULT "
                "(297.500000, present in the artefact) is REFUSED",
         not token_admissible("297.500000", planted))

    print("\nTHE BARRED SET -- refused even when an allowlist names them.")
    forged = dict(_PLANTED_GRADED)
    forged = json.loads(json.dumps(_PLANTED_GRADED))
    forged["results"]["S2"]["adiabatic_bound_K"] = 10.800
    forged["screen_admissible_K"].append(
        {"run": "S2", "quantity": "adiabatic bound", "value": 10.800})
    vals, _ = derive_from_text(json.dumps(forged))
    _chk(fails, "an artefact CAN declare the adiabatic bound (the derivation "
                "does not special-case it)", 10.800 in vals)
    for token in ("10.800", "10.8", "2.400", "2.4", "10.7950", "10.795"):
        _chk(fails, "and the token %r is STILL refused, by the barred set "
                    "checked first" % token,
             not token_admissible(token, vals))

    print("\nTAMPERING -- a declared value its own grading does not contain.")
    tampered = json.loads(json.dumps(_PLANTED_GRADED))
    tampered["screen_admissible_K"].append(
        {"run": "S2", "quantity": "invented", "value": 311.000001})
    try:
        derive_from_text(json.dumps(tampered))
        _chk(fails, "an unbacked declared value REFUSES", False)
    except AdmissionRefused as exc:
        _chk(fails, "an unbacked declared value REFUSES", "311.000001" in str(exc))

    print("\nINTEGER TOKENS -- never admitted, whatever is graded.")
    _chk(fails, "'299' carries no decimals and is REFUSED",
         not token_admissible("299", (298.873120, 299.0)))
    _chk(fails, "'299.0' with 299.0 graded IS admitted",
         token_admissible("299.0", (299.0,)))

    print("\nTHE GIT READER -- planted control, in a scratch repository.")
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="actC_admission_")
    try:
        env = {"GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "s@x",
               "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "s@x",
               "PATH": os.environ.get("PATH", ""), "HOME": tmp}
        subprocess.run(["git", "-C", tmp, "init", "-q"], check=True, env=env)
        rel = GRADE_RELPATH
        os.makedirs(os.path.join(tmp, os.path.dirname(rel)), exist_ok=True)
        # NEGATIVE ARM FIRST: written to the working tree, NOT committed.
        with open(os.path.join(tmp, rel), "w") as fh:
            json.dump(_PLANTED_GRADED, fh)
        vals, why = derive(tmp)
        _chk(fails, "an UNCOMMITTED grading derives the EMPTY set -- the "
                    "reader looks at HEAD, not at the working tree", vals == ())
        subprocess.run(["git", "-C", tmp, "add", "--", rel], check=True, env=env)
        subprocess.run(["git", "-C", tmp, "commit", "-q", "-m", "planted"],
                       check=True, env=env)
        vals, why = derive(tmp)
        _chk(fails, "once COMMITTED the same grading derives 2 values -- the "
                    "reader is not blind", len(vals) == 2)
        print("       provenance: %s" % why)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL",
                                         len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    values, note = derive()
    print("Act C admissibility source, live state")
    print("  artefact : %s" % GRADE_RELPATH)
    print("  derived  : %s" % note)
    print("  values   : %s" % (list(values) if values else "NONE"))
    print("  barred   : %s K, refused unconditionally" % list(BARRED_K))
    if not values:
        print("\nEvery temperature is refused. The guard's behaviour is "
              "bit-identical to its behaviour before this file existed, and "
              "the act's fallback ending is what plays.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
