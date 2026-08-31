#!/usr/bin/env python3
"""F28 BC PROBE -- MACHINE CHECK OF THE SINGLE-VARIATION CLAIM.

PRECOMMITTED_READINGS.md section 2 asserts that the probe case is byte-identical
to its parent arm EXCEPT that the `farfield` entry becomes `slip` on U, p, k,
omega and nut.  That assertion is the whole evidentiary content of the probe: a
probe that silently changed two things isolates no mechanism.

This script makes the claim a MACHINE-CHECKED PRECONDITION OF THE LAUNCH rather
than a lane's word for it.  It exits 0 only if:

  * every system/ and constant/ input (polyMesh included) is byte-identical;
  * each of the five 0/ fields, with its `farfield` entry EXCISED, is
    byte-identical to the parent's with ITS `farfield` entry excised; and
  * every excised probe entry is exactly `type slip;` and no parent entry is.

Anchored to the ENTRY LINE (`^\\s*farfield\\b`) and brace-balanced, never
matched on value text -- run_f28_feasibility.sh records the measured defect
where a substitution matched a dictionary's own self-documenting prose.

Standing rule 3: run with --selftest to drive it to a REFUSAL on a planted
perturbation.  A checker not shown able to fail is not a control.

Usage:  assert_bcprobe_single_variation.py <parent_dir> <probe_dir>
        assert_bcprobe_single_variation.py --selftest <parent_dir> <probe_dir>
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

FIELDS = ["U", "p", "k", "omega", "nut"]
SYSTEM = ["controlDict", "decomposeParDict", "fvSchemes", "fvSolution"]
CONSTANT = ["fvOptions", "transportProperties", "turbulenceProperties"]
# ANCHORED TO THE ENTRY LINE *AND SCOPED TO boundaryField*.  Both halves were
# paid for.  The first anchor tried here was `^\s*farfield\b`, and it matched
# `0/U` line 6 -- a HEADER COMMENT that describes the boundary treatment in
# prose, indented two spaces.  That is the FOURTH instance in this case of one
# defect shape already recorded three times in run_f28_feasibility.sh (the bare
# `__` placeholder sweep matching `__PLACEHOLDERS__` in controlDict.template's
# own header; the div-scheme substitution matching fvSchemes' quoted section 8;
# the same again at a different count): IN THIS REPOSITORY THE DICTIONARIES
# DOCUMENT THEMSELVES BY QUOTING THEIR OWN CONTENT, so a match on a name alone
# hits the documentation.  Requiring the opening brace AND confining the search
# to the boundaryField block removes both routes.  The header comment still
# lands in the REMAINDER, where it must stay byte-identical -- so prose is
# still compared, just never mistaken for an entry.
ENTRY = re.compile(r"^\s*farfield\s*\{")
BFIELD = re.compile(r"^\s*boundaryField\b")


def excise_farfield(path):
    """Return (remainder_text, entry_text). Brace-balanced from the entry line."""
    lines = open(path).read().splitlines(keepends=True)
    bstarts = [i for i, ln in enumerate(lines) if BFIELD.match(ln)]
    if len(bstarts) != 1:
        raise SystemExit("REFUSE: %s has %d boundaryField lines, expected 1"
                         % (path, len(bstarts)))
    lo = bstarts[0]
    starts = [i for i, ln in enumerate(lines) if i > lo and ENTRY.match(ln)]
    if len(starts) != 1:
        raise SystemExit("REFUSE: %s has %d farfield entry lines, expected 1"
                         % (path, len(starts)))
    i = starts[0]
    depth = 0
    j = i
    while j < len(lines):
        depth += lines[j].count("{") - lines[j].count("}")
        if depth == 0 and j >= i and "{" in "".join(lines[i:j + 1]):
            break
        j += 1
    else:
        raise SystemExit("REFUSE: unbalanced farfield entry in %s" % path)
    return "".join(lines[:i] + lines[j + 1:]), "".join(lines[i:j + 1])


def check(parent, probe, verbose=True):
    """Return list of failure strings. Empty list means the claim holds."""
    fails = []

    def say(m):
        if verbose:
            print(m)

    for rel in (["system/" + f for f in SYSTEM]
                + ["constant/" + f for f in CONSTANT]):
        a, b = os.path.join(parent, rel), os.path.join(probe, rel)
        if not (os.path.isfile(a) and os.path.isfile(b)):
            fails.append("MISSING input %s" % rel)
            continue
        if open(a, "rb").read() != open(b, "rb").read():
            fails.append("DIFFERS (must be identical): %s" % rel)
        else:
            say("  identical: %s" % rel)

    # polyMesh: the mesh is the experiment's control surface.
    a, b = os.path.join(parent, "constant/polyMesh"), os.path.join(probe, "constant/polyMesh")
    rc = subprocess.run(["diff", "-r", "-q", a, b],
                        capture_output=True, text=True)
    if rc.returncode != 0:
        fails.append("constant/polyMesh DIFFERS: %s" % (rc.stdout + rc.stderr).strip()[:400])
    else:
        say("  identical: constant/polyMesh (recursive)")

    for f in FIELDS:
        a, b = os.path.join(parent, "0", f), os.path.join(probe, "0", f)
        if not (os.path.isfile(a) and os.path.isfile(b)):
            fails.append("MISSING field 0/%s" % f)
            continue
        try:
            arem, aent = excise_farfield(a)
            brem, bent = excise_farfield(b)
        except SystemExit as e:
            fails.append(str(e))
            continue
        if arem != brem:
            fails.append("0/%s DIFFERS OUTSIDE its farfield entry -- the probe "
                         "changed more than one thing" % f)
        else:
            say("  0/%s: identical outside the farfield entry" % f)
        if not re.match(r"^\s*farfield\s*\{\s*type\s+slip;\s*\}\s*$", bent.strip()):
            fails.append("0/%s probe farfield entry is not `type slip;`: %r"
                         % (f, bent.strip()))
        if "slip" in aent:
            fails.append("0/%s PARENT farfield already reads slip -- there is "
                         "no variation to test" % f)
    return fails


def selftest(parent, probe):
    """Drive the checker to a REFUSAL on planted perturbations (rule 3)."""
    print("SELFTEST -- a checker not shown able to fail is not a control.")
    live = check(parent, probe, verbose=False)
    print("  control (unperturbed real pair): %d failures -- %s"
          % (len(live), "PASS as expected" if not live else "UNEXPECTED: %s" % live))
    ok = not live
    tmp = tempfile.mkdtemp(prefix="f28bcprobe_selftest_")
    try:
        # PLANT 1: a second change outside the farfield entry.
        p1 = os.path.join(tmp, "plant1")
        shutil.copytree(probe, p1, symlinks=True)
        t = open(os.path.join(p1, "system/fvSolution")).read()
        open(os.path.join(p1, "system/fvSolution"), "w").write(
            t.replace("U 0.7", "U 0.5", 1))
        f1 = check(parent, p1, verbose=False)
        print("  PLANT 1 (relaxation also changed): %d failures -- %s"
              % (len(f1), "REFUSED as required" if f1 else "*** MISSED ***"))
        ok = ok and bool(f1)

        # PLANT 2: farfield reverted to the parent form on one field.
        p2 = os.path.join(tmp, "plant2")
        shutil.copytree(probe, p2, symlinks=True)
        prem, pent = excise_farfield(os.path.join(parent, "0", "k"))
        brem, bent = excise_farfield(os.path.join(p2, "0", "k"))
        open(os.path.join(p2, "0", "k"), "w").write(
            open(os.path.join(p2, "0", "k")).read().replace(bent, pent, 1))
        f2 = check(parent, p2, verbose=False)
        print("  PLANT 2 (0/k farfield not slip): %d failures -- %s"
              % (len(f2), "REFUSED as required" if f2 else "*** MISSED ***"))
        ok = ok and bool(f2)

        # PLANT 3: a perturbed mesh.
        p3 = os.path.join(tmp, "plant3")
        shutil.copytree(probe, p3, symlinks=True)
        with open(os.path.join(p3, "constant/polyMesh/boundary"), "a") as fh:
            fh.write("\n// planted\n")
        f3 = check(parent, p3, verbose=False)
        print("  PLANT 3 (polyMesh perturbed): %d failures -- %s"
              % (len(f3), "REFUSED as required" if f3 else "*** MISSED ***"))
        ok = ok and bool(f3)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST %s" % ("rc 0 -- all three plants seen" if ok else "FAILED"))
    return 0 if ok else 2


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        sys.exit(selftest(args[1], args[2]))
    if len(args) != 2:
        raise SystemExit(__doc__)
    fails = check(args[0], args[1])
    if fails:
        print("REFUSE -- the single-variation claim does NOT hold:")
        for f in fails:
            print("  * " + f)
        sys.exit(2)
    print("SINGLE VARIATION CONFIRMED: farfield -> slip on U p k omega nut, "
          "and nothing else differs.")
    sys.exit(0)
