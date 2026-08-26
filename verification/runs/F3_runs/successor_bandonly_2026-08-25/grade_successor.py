#!/usr/bin/env python3
"""
**RETIRED FROM THE GRADED PATH — 2026-08-26, by cfd-supervisor's check-1 refusal.**

This file graded BAND-ONLY rows. The successor now runs FULL GRID TRIPLES, and this
grader's in-scope guard (see `main()`, "came back WITH a grid triple") refuses any row
that carries one — it would have refused EVERY row the rung produces. It is retired
rather than inverted: inverting it would keep a band-only instrument inside a
triple-scoped rung.

It also routed grading to `grade_f3.py`, which reimplements the Roache triple at
:377-395 and supplies no iterative or plateau states, so rule 5 limb (1) was never
asked -- the `ABSENT` defect ruled on at 887ddfaf.

THE LIVE GRADING PATH IS:
    verification/runs/F3_runs/successor_triple_2026-08-26/grade_f3s.py
which calls scripts/roache_triple.py::grade_ladder directly with both state sets.

Kept on disk as the record of the superseded design. NOT part of any live rung.

F3 SUCCESSOR (band-only rows) — THE GRADING PATH, frozen with its pre-registration.

WHAT THIS IS, AND WHAT IT DELIBERATELY IS NOT
---------------------------------------------
This script does NOT grade. It does not own a band, a reference value or a verdict
rule, and it cannot move one. **The grading is done by F3's OWN frozen comparator,
`conversion_2026-08-24/grade_f3.py`, invoked BYTE-UNCHANGED as a subprocess**, with
its own freeze check (`--prereg-commit`) live. Every band and every reference value
therefore carries over from F3 unchanged and NOTHING is re-derived, which is the
point: no band is chosen at all, so no band can have been chosen to fit an answer.

What this script adds is ONE thing, and it is a requirement of the cfd supervisor's
ruling of 2026-08-25 (`BAND_ONLY_RULING_2026-08-25.md`, condition 1):

    EVERY BAND-ONLY ROW CARRIES ITS LIMIT ON ITS OWN FACE, EMITTED BY THE GRADER.

A row whose limitation lives only in a companion document is a row that will be
cited without it. So the limitation is attached HERE, mechanically, DATA-DRIVEN off
`triple is None` -- never off a hardcoded list of row names, which could be wrong
about which rows are band-only and would then annotate the wrong thing.

REFUSAL DISCIPLINE (standing rule 4): this script REFUSES (exit 2) rather than
degrade. If the frozen comparator refuses, THAT IS THE RESULT and it is reported as
such -- it is never worked around, and no verdict is synthesised in its place.
"""
import os
import sys
import json
import re
import hashlib
import argparse
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"
F3_ROOT = os.path.dirname(HERE)
CONV = os.path.join(F3_ROOT, "conversion_2026-08-24")
FROZEN_GRADER = os.path.join(CONV, "grade_f3.py")
# The ruling that requires the limitation wording. It is the EXTERNAL REFERENT
# the wording is checked against -- see selftest_annotator(). A wording check
# that compares a constant against itself cannot fail (VERIFICATION_CHARTER 6b,
# L-74), and a mutation test of this file caught exactly that defect here.
RULING = os.path.join(CONV, "BAND_ONLY_RULING_2026-08-25.md")

# ---------------------------------------------------------------------------
# FROZEN ARTIFACTS -- used BYTE-UNCHANGED, asserted by hash before anything runs.
# Exactly as F3 itself did with the 2026-07-28 generators and runners.
# ---------------------------------------------------------------------------
FROZEN_SHA256 = {
    "conversion_2026-08-24/grade_f3.py":
        "e7602996cb75fd61e95a51a85910b24cf0a675b6eee05e8b7c3d2e5ae0b88570",
    "exact_theory.py":
        "1e1879a3034c4eaabf092a4a05bd76ef01f216473e366c32cd4f7b0ecc4ca8d6",
    "make_wedge_case.py":
        "5741fd6229157287291edc94a36b9fa072bf98126ce57e857ddba3f19d891e3a",
    "make_diamond_case.py":
        "c2a5a70dd7d9f1d981cc98c4c02a76768c43956c7317abb57a7727bd46a5ad68",
    "run_wedge_case.py":
        "edbfc6b06a29ac8dea269f9025f9267061b5d3f221e2a7f8d28ee4337e44f2e1",
    "run_diamond_case.py":
        "607c7de45ba25afc770ce145811865e9ea564bf95e78e22458245861bc37bee5",
    "foam_io.py":
        "a2e73ab08f20b91e096f916322711ad904c12cf5ce0b46b442b3aeb5b48eee8e",
}

# The exact string the ruling requires on the face of every band-only row.
LIMITATION = ("band only — no grid triple — no discretization-error "
              "estimate — NOT a credential")

# The THREE gate rows this successor is registered to produce, and no others.
# Anything else the frozen comparator emits is OUT OF SCOPE and is labelled so.
IN_SCOPE = [
    ("G-F3-1_wedge_surface_pressure", "M2.5_th10"),
    ("G-F3-2_wedge_shock_angle",      "M2.5_th10"),
    ("G-F3-5_diamond_wave_drag",      "M2.5_eps5"),
]

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# The control census, REGISTERED as a number so that a missing control is a
# COUNT MISMATCH and not a silently shorter list. selftest_annotator() emits one
# row per planted annotator case (5), one for the ruling-search discrimination
# control, and one for the wording match against the ruling on disk.
EXPECTED_CONTROLS = 7
EXPECTED_FROZEN_ARTIFACTS = 7


def controls_all_passed(controls, frozen):
    """The success PREDICATE. Separate from any print, so the claim can only be
    made by evaluating it. Returns (ok, why)."""
    if not isinstance(controls, list) or len(controls) != EXPECTED_CONTROLS:
        return False, ("expected %d controls, got %r -- a control that did not "
                       "run cannot have passed"
                       % (EXPECTED_CONTROLS, len(controls) if isinstance(controls, list)
                          else type(controls).__name__))
    for c in controls:
        if not isinstance(c, dict) or c.get("passed") is not True:
            return False, "control %r did not report passed=True" % (c,)
    if not isinstance(frozen, dict) or len(frozen) != EXPECTED_FROZEN_ARTIFACTS:
        return False, ("expected %d frozen artifacts asserted, got %r"
                       % (EXPECTED_FROZEN_ARTIFACTS,
                          len(frozen) if isinstance(frozen, dict) else frozen))
    return True, "%d controls passed; %d frozen artifacts byte-asserted" % (
        len(controls), len(frozen))


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_frozen_bytes():
    """Every borrowed artifact is byte-unchanged. Refuse on ANY drift."""
    seen = {}
    for rel, want in sorted(FROZEN_SHA256.items()):
        p = os.path.join(F3_ROOT, rel)
        if not os.path.exists(p):
            refuse("frozen artifact missing: %s" % p)
        got = sha256_file(p)
        if got != want:
            refuse("frozen artifact CHANGED: %s\n  expected %s\n  on disk  %s"
                   % (rel, want, got))
        seen[rel] = got
    return seen


# ---------------------------------------------------------------------------
# THE ANNOTATOR -- and the planted control that proves it DISCRIMINATES.
# ---------------------------------------------------------------------------

def is_band_only(row):
    """A graded row with NO grid triple. Data-driven, never a name list.

    Three states are distinguished on purpose:
      * a graded row carrying a triple            -> NOT band-only
      * a graded row whose triple is None         -> band-only
      * a row that was never graded (PENDING etc.) -> NOT band-only, because
        there is no number on its face to qualify.
    """
    if not isinstance(row, dict):
        return False
    if "triple" not in row:
        return False
    if row.get("verdict") not in ("PASS", "GATE FAIL", "NOT A RESULT"):
        return False
    return row["triple"] is None


def annotate(row):
    """Attach the limitation to a band-only row. Returns a NEW dict."""
    out = dict(row)
    if is_band_only(row):
        out["limitation"] = LIMITATION
        out["is_credential"] = False
    return out


def selftest_annotator():
    """PLANTED CONTROL (standing rule 3 / MONITOR_STANDARD S17 step 3).

    An annotator that annotates EVERYTHING, and one that annotates NOTHING, both
    produce an output that looks plausible on the row we care about. Only a
    control that plants BOTH directions can tell them apart, so both are planted
    and both are required to come back right.
    """
    cases = [
        # (name, row, must_be_annotated)
        ("band_only_PASS",      dict(verdict="PASS", triple=None), True),
        ("band_only_GATE_FAIL", dict(verdict="GATE FAIL", triple=None), True),
        ("triple_PASS",         dict(verdict="PASS", triple=dict(klass="CONVERGING")), False),
        ("triple_NOT_A_RESULT", dict(verdict="NOT A RESULT",
                                     triple=dict(klass="OSCILLATORY")), False),
        ("ungraded_PENDING",    dict(verdict="PENDING", note="absent"), False),
    ]
    results = []
    for name, row, want in cases:
        got = "limitation" in annotate(row)
        if got != want:
            refuse("ANNOTATOR CONTROL FAILED on %s: annotated=%s, required=%s. "
                   "The annotator has not been shown to discriminate, so its "
                   "output is not evidence." % (name, got, want))
        results.append(dict(control="PZ-A_annotator_%s" % name,
                            annotated=got, required=want, passed=True))
    # ---- the wording, checked against an EXTERNAL REFERENT -------------
    # Comparing the emitted string to this file's own LIMITATION constant is a
    # check that CANNOT FAIL: mutate the constant and both sides move together.
    # A mutation test of this script proved that concretely. So the wording is
    # checked against the SUPERVISOR'S RULING ON DISK, which this script does
    # not author and cannot silently move.
    emitted = annotate(dict(verdict="PASS", triple=None))["limitation"]
    if not os.path.exists(RULING):
        refuse("the ruling that fixes the limitation wording is missing: %s" % RULING)
    ruling_norm = re.sub(r"\s+", " ", open(RULING, encoding="utf-8").read())

    # PLANTED CONTROL on the SEARCH ITSELF (standing rule 3): a searcher that
    # returns True for everything, or False for everything, would make the check
    # above meaningless. Prove it can tell present from absent BEFORE trusting it.
    present_probe = "EVERY ROW CARRIES ITS LIMIT ON ITS OWN FACE"
    absent_probe = "band only — no grid triple — THIS PHRASE IS NOT IN THE RULING"
    if present_probe not in ruling_norm:
        refuse("the ruling-search control could not find a phrase KNOWN to be in "
               "the ruling; the searcher is not shown able to see a hit and its "
               "negative results are not evidence")
    if absent_probe in ruling_norm:
        refuse("the ruling-search control found a phrase known to be ABSENT; the "
               "searcher does not discriminate")
    results.append(dict(control="PZ-A_ruling_search_discriminates",
                        found_known_present=True, found_known_absent=False,
                        passed=True))

    if re.sub(r"\s+", " ", emitted) not in ruling_norm:
        refuse("the annotator's wording is NOT the wording the ruling fixes.\n"
               "  emitted: %r\n  ruling:  %s\n"
               "This is a paraphrase, and a paraphrased limit is how a limit gets "
               "dropped." % (emitted, RULING))
    results.append(dict(control="PZ-A_annotator_wording_matches_ruling",
                        emitted=emitted, referent=os.path.relpath(RULING, REPO),
                        passed=True))
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def walk_gates(gates, fn):
    """Apply fn to every leaf gate row, preserving the two shapes the frozen
    comparator emits: a bare row, or a dict of pair -> row."""
    out = {}
    for gid, node in gates.items():
        if isinstance(node, dict) and "verdict" in node:
            out[gid] = fn(node)
        elif isinstance(node, dict):
            out[gid] = {pair: fn(row) for pair, row in node.items()}
        else:
            out[gid] = node
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg-commit", help="sha of the successor's freeze commit")
    ap.add_argument("--root", default=os.path.join(HERE, "runs"))
    ap.add_argument("--out", default=os.path.join(HERE, "SUCCESSOR_GRADED.json"))
    ap.add_argument("--selftest", action="store_true",
                    help="run the frozen-bytes assertion and the annotator "
                         "planted control, then exit")
    a = ap.parse_args()

    frozen = assert_frozen_bytes()
    controls = selftest_annotator()

    if a.selftest:
        # THE CLAIM IS MADE INSIDE THE PASSING BRANCH, AND NOWHERE ELSE.
        # Measured defect, 2026-08-26: this block previously printed
        # "SELFTEST GREEN" at rc=0 in sequence after the controls ran, without
        # inspecting them. A mutation replacing `controls = selftest_annotator()`
        # with `controls = []` -- the whole planted-zero control deleted -- still
        # printed SELFTEST GREEN and still exited 0 under `python3 -O`. That is
        # the manufactured-certification shape: a certificate issued by a run in
        # which nothing was checked. The rule that fixes the CLASS, not the
        # instance: PRINT INSIDE THE PASSING BRANCH, SO REMOVING THE CHECK
        # REMOVES THE CLAIM.
        ok, why = controls_all_passed(controls, frozen)
        print(json.dumps(dict(frozen_bytes_asserted=frozen,
                              annotator_controls=controls,
                              limitation_string=LIMITATION,
                              control_census=dict(expected=EXPECTED_CONTROLS,
                                                  seen=len(controls) if
                                                  isinstance(controls, list) else None),
                              selftest_predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade")

    # ---- run F3's OWN frozen comparator, byte-unchanged, freeze check live ----
    raw_out = os.path.join(HERE, "FROZEN_COMPARATOR_RAW.json")
    cmd = [sys.executable, FROZEN_GRADER,
           "--prereg-commit", a.prereg_commit,
           "--root", a.root, "--out", raw_out]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode())
        refuse("THE FROZEN COMPARATOR REFUSED (rc=%d). That refusal IS the result "
               "and is not worked around." % proc.returncode)
    if not os.path.exists(raw_out):
        refuse("frozen comparator returned 0 but wrote no output")
    raw = json.load(open(raw_out))

    # ---- annotate, data-driven -------------------------------------------
    report = dict(
        rung="F3-SUCCESSOR-BANDONLY",
        prereg="verification/campaign/F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md",
        prereg_commit=a.prereg_commit,
        frozen_bytes_asserted=frozen,
        grading_is_done_by="conversion_2026-08-24/grade_f3.py (BYTE-UNCHANGED, "
                           "invoked as a subprocess with its own freeze check live)",
        frozen_comparator_freeze=raw.get("grading_path_freeze"),
        annotator_controls=controls,
        planted_zero_controls=raw.get("planted_zero_controls"),
        bands=raw.get("bands"),
        limitation_string=LIMITATION,
        does_not_alter_F3=("F3's tally, rows and verdicts are NOT altered by this "
                           "rung. F3's three rows stay BLOCKED as a launch request "
                           "and PENDING as graded cells."),
        runs=raw.get("runs"),
        gates=walk_gates(raw.get("gates", {}), annotate),
    )

    # ---- scope, and the REFUSAL that makes condition 1 enforceable --------
    in_scope_rows = {}
    for gid, pair in IN_SCOPE:
        node = report["gates"].get(gid)
        if not isinstance(node, dict) or pair not in node:
            refuse("in-scope row %s / %s absent from the comparator's output" % (gid, pair))
        row = node[pair]
        v = row.get("verdict")
        if v not in VERDICTS:
            refuse("in-scope row %s / %s carries a verdict outside the fixed "
                   "vocabulary: %r" % (gid, pair, v))
        if v in ("PASS", "GATE FAIL", "NOT A RESULT"):
            if row.get("triple") is not None:
                refuse("in-scope row %s / %s came back WITH a grid triple. This "
                       "rung is registered for band-only rows; a triple here "
                       "means the run matrix is not what was frozen." % (gid, pair))
            if row.get("limitation") != LIMITATION:
                refuse("in-scope row %s / %s is graded but carries NO limitation "
                       "on its face. Condition 1 of the ruling is not met and this "
                       "grader refuses rather than emit a row that will be cited "
                       "without its limit." % (gid, pair))
        in_scope_rows["%s / %s" % (gid, pair)] = row

    report["in_scope"] = in_scope_rows
    report["out_of_scope_note"] = (
        "Every other row the frozen comparator emits belongs to F3 and is NOT "
        "produced, altered or regraded by this rung. Rows reading PENDING here "
        "are F3 runs absent from THIS rung's run root by design.")

    with open(a.out, "w") as f:
        json.dump(report, f, indent=2)

    # ---- the tally, and EVERY row carries its limit -----------------------
    print("F3 SUCCESSOR (band-only) -- TALLY")
    print("=" * 78)
    for key, row in in_scope_rows.items():
        v = row.get("verdict")
        if v in ("PASS", "GATE FAIL", "NOT A RESULT"):
            print("%-46s %s" % (key, v))
            print("    measured %.12g  exact %.12g  dev %+.6f%%  band +-%.2f%%"
                  % (row["measured"], row["exact"], row["deviation_pct"],
                     row["band_pct"]))
            print("    %s" % row["limitation"])
        else:
            print("%-46s %s  (%s)" % (key, v, row.get("note", "")))
    print("=" * 78)
    print("Every row above carries its limitation as emitted by this grader.")
    print("F3 is NOT altered by this rung.")
    print("\nwritten: %s" % a.out)


if __name__ == "__main__":
    main()
