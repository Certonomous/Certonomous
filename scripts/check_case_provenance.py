#!/usr/bin/env python3
"""SOLVER-NAMESPACE CONTAMINATION: does this case carry entries its solver cannot read?

WHY THIS EXISTS
---------------
T4 failed at launch three times in one night.  Two of the three were ONE defect
wearing two faces, and it is a PROVENANCE defect rather than a typo:

  * `0/alphat` carried `compressible::alphatWallFunction` while the case is run by
    `buoyantBoussinesqSimpleFoam`, which is INCOMPRESSIBLE;
  * `system/fvSchemes` carried the COMPRESSIBLE spelling
    `div(((rho*nuEff)*dev2(T(grad(U)))))`.

Both survived into a FROZEN rung, and the reason they survived is the finding:

    THE T4 CASE TEMPLATE WAS DERIVED FROM A COMPRESSIBLE CASE, AND THE
    COMPRESSIBLE ARTIFACTS SURVIVED BECAUSE NOTHING IN THE REGISTRATION HAD AN
    OPINION ABOUT THEM.  A registration that fixes the SOLVER but not the WALL
    TREATMENT has left the physics that produces its graded number unregistered.

`scripts/check_launcher_can_launch.py` catches this at LAUNCH, by driving the real
solver for one iteration.  That is the right last line of defence and it is not
replaced here.  THIS check runs EARLIER and answers a different question: not
"does it start?" but "WHERE DID THIS TEMPLATE COME FROM, and is it internally
consistent with the solver it names?"  A case can be contaminated in a file the
one-iteration arm never reaches -- a `fvSolution` block for a field this solver
does not solve, a `thermophysicalProperties` left beside a Boussinesq case -- and
those cost a re-freeze rather than a crash.

    RUN THIS BEFORE THE FREEZE.  A crash is cheap; a frozen rung carrying a
    silent inconsistency is not.

WHAT IT DOES
------------
Reads the solver from `system/controlDict` (`application`), classifies it, and
sweeps `0/`, `0.orig/`, `constant/` and `system/` for tokens belonging to the
OTHER family.  Findings are reported with file, line number and the line.

It REFUSES (`sys.exit(2)`) when contamination is found.  It carries ZERO `assert`
statements -- `python3 -O` deletes those (L-332) -- and every refusal is a real
exception or exit.

THE PLANTED CONTROL, and it is not optional (standing rule 3)
-------------------------------------------------------------
`--selftest` writes a sacrificial case carrying a known contaminant, sweeps it,
and REFUSES if the sweep cannot see it.  A clean report from this tool is
evidence only because the tool is shown able to produce a dirty one.  The
selftest also drives itself under `python3 -O` and requires the refusal to fire
identically.

WHAT IT DOES NOT DO
-------------------
It does not judge PHYSICS.  A `compressible::` entry in a genuinely compressible
case is correct and is reported as clean.  It does not know whether a wall
function suits a mesh -- that is a y+ measurement and a case-selection call, and
this tool deliberately has no opinion on it.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

# Tokens that belong to the COMPRESSIBLE family.  A case whose `application` is an
# incompressible solver must not carry these.
COMPRESSIBLE_TOKENS = [
    (r"compressible::", "a compressible-namespace boundary condition"),
    (r"\brho\s*\*", "a density-weighted scheme spelling"),
    (r"\balphaEff\b", "the compressible effective thermal diffusivity"),
    (r"\bthermoType\b", "a thermophysical model block"),
    (r"\bthermophysicalProperties\b", "a thermophysical properties reference"),
    (r"\bhePsiThermo\b|\bheRhoThermo\b", "a compressible thermo package"),
]
# Tokens that belong to the INCOMPRESSIBLE/Boussinesq family.
INCOMPRESSIBLE_TOKENS = [
    (r"\bp_rgh\b", "the Boussinesq buoyant pressure field"),
    (r"\bTRef\b", "the Boussinesq reference temperature"),
    (r"\bbeta\b\s*\[", "the Boussinesq expansion coefficient"),
]
INCOMPRESSIBLE_SOLVERS = (
    "buoyantBoussinesqSimpleFoam", "buoyantBoussinesqPimpleFoam",
    "simpleFoam", "pimpleFoam", "pisoFoam", "icoFoam", "scalarTransportFoam",
)
COMPRESSIBLE_SOLVERS = (
    "buoyantSimpleFoam", "buoyantPimpleFoam", "rhoSimpleFoam", "rhoPimpleFoam",
    "sonicFoam", "chtMultiRegionSimpleFoam", "chtMultiRegionFoam",
)
SWEPT_DIRS = ("0", "0.orig", "constant", "system")
LARGE_FILE_BYTES = 1 << 20        # 1 MB: above this, head+tail only (see sweep())
SCAN_EDGE_BYTES = 512 << 10       # 512 KB scanned at each end


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def read_application(case):
    cd = os.path.join(case, "system", "controlDict")
    if not os.path.isfile(cd):
        # a .template is the pre-build form and is swept just as happily
        for alt in ("controlDict.template",):
            p = os.path.join(case, "system", alt)
            if os.path.isfile(p):
                cd = p
                break
        else:
            refuse("no system/controlDict in %s -- cannot determine the solver, "
                   "and a provenance sweep without a solver is guesswork" % case)
    with open(cd, errors="replace") as fh:
        txt = fh.read()
    m = re.search(r"^\s*application\s+([A-Za-z0-9_]+)\s*;", txt, re.M)
    if not m:
        refuse("no `application` entry in %s" % cd)
    return m.group(1)


def classify(app):
    if app in INCOMPRESSIBLE_SOLVERS:
        return "incompressible"
    if app in COMPRESSIBLE_SOLVERS:
        return "compressible"
    return "unknown"


def sweep(case, family):
    """Return findings as (path, lineno, line, why)."""
    if family == "incompressible":
        tokens, label = COMPRESSIBLE_TOKENS, "compressible"
    elif family == "compressible":
        tokens, label = INCOMPRESSIBLE_TOKENS, "incompressible/Boussinesq"
    else:
        return None, None, []
    pats = [(re.compile(p), why) for p, why in tokens]
    out = []
    partial = []
    for d in SWEPT_DIRS:
        root = os.path.join(case, d)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # constant/polyMesh holds the mesh itself -- `points`, `faces`,
            # `owner`, `neighbour` -- which run to hundreds of MB and CANNOT
            # contain a wall-function or scheme token.  Reading them made a
            # territory sweep time out at 170 s on first live use; skipping them
            # is a correctness-preserving speedup, not a narrowing of scope.
            dirnames[:] = [d for d in dirnames if d != "polyMesh"]
            for fn in sorted(filenames):
                p = os.path.join(dirpath, fn)
                # a file with a NUL byte in its first block is binary (a
                # compressed or binary-format field); it carries no readable
                # dictionary entry and is skipped rather than scanned.
                try:
                    with open(p, "rb") as bh:
                        if b"\x00" in bh.read(8192):
                            continue
                except OSError:
                    continue
                # LARGE FILES ARE SCANNED HEAD+TAIL ONLY, AND THIS IS A STATED
                # NARROWING OF SCOPE -- not a correctness-preserving speedup like
                # the polyMesh prune above.  `constant/` holds BULK NUMERICAL DATA
                # as well as dictionaries: T10aR_runs/R_x carries a 6.1 GB
                # `constant/F` view-factor matrix and a 1.5 GB
                # `globalFaceFaces`, neither under polyMesh, and reading them
                # line-by-line stalled a territory sweep indefinitely.
                # In an OpenFOAM field file the `FoamFile` header is at the START
                # and the `boundaryField` block -- where every wall-function type
                # lives -- is at the END; the bulk between them is numeric data
                # that cannot carry a namespace token.  So head+tail is sound in
                # practice.  IT IS NOT SOUND IN PRINCIPLE, and the count of
                # partially scanned files is REPORTED rather than buried, so a
                # reader can see exactly how much of the corpus was skimmed.
                try:
                    size = os.path.getsize(p)
                    if size > LARGE_FILE_BYTES:
                        with open(p, errors="replace") as fh:
                            headtxt = fh.read(SCAN_EDGE_BYTES)
                        with open(p, "rb") as bh:
                            bh.seek(max(0, size - SCAN_EDGE_BYTES))
                            tailtxt = bh.read().decode("utf-8", "replace")
                        lines = (headtxt + "\n" + tailtxt).splitlines()
                        partial.append(os.path.relpath(p, case))
                    else:
                        with open(p, errors="replace") as fh:
                            lines = fh.read().splitlines()
                except OSError:
                    continue
                for i, line in enumerate(lines, 1):
                    stripped = line.split("//")[0]
                    for pat, why in pats:
                        if pat.search(stripped):
                            out.append((os.path.relpath(p, case), i,
                                        line.strip()[:160], why))
                            break
    return out, label, partial


def check_case(case, quiet=False):
    case = case.rstrip(os.sep) or case
    app = read_application(case)
    family = classify(app)
    findings, label, partial = sweep(case, family)
    if family == "unknown":
        print("%s: application `%s` -- UNCLASSIFIED solver, no sweep performed. "
              "Add it to the tables in this script rather than assuming it is "
              "clean." % (os.path.basename(case), app))
        return None
    if findings:
        print("%s: application `%s` (%s)" % (os.path.basename(case), app, family))
        for rel, ln, line, why in findings:
            print("  %s:%d  %s" % (rel, ln, line))
            print("      ^ %s, in a %s case" % (why, family))
        return findings
    if not quiet:
        note = ""
        if partial:
            note = ("  [%d file(s) over %d MB scanned HEAD+TAIL only: %s]"
                    % (len(partial), LARGE_FILE_BYTES >> 20,
                       ", ".join(sorted(partial)[:3])))
        print("%s: application `%s` (%s) -- no %s-family tokens found in %s%s"
              % (os.path.basename(case), app, family, label,
                 "/".join(SWEPT_DIRS), note))
    return []


CONTAMINANT = "        plate { type compressible::alphatWallFunction; Prt 0.85; }\n"


def write_fixture(root, contaminated):
    os.makedirs(os.path.join(root, "system"))
    os.makedirs(os.path.join(root, "0"))
    with open(os.path.join(root, "system", "controlDict"), "w") as fh:
        fh.write("application     buoyantBoussinesqSimpleFoam;\n"
                 "endTime         10;\n")
    with open(os.path.join(root, "0", "alphat"), "w") as fh:
        fh.write("boundaryField\n{\n")
        if contaminated:
            fh.write(CONTAMINANT)
        else:
            fh.write("        plate { type calculated; value uniform 0; }\n")
        fh.write("}\n")


def selftest():
    failures = []
    tmp = tempfile.mkdtemp(prefix="case_provenance_")
    dirty = os.path.join(tmp, "dirty_case")
    clean = os.path.join(tmp, "clean_case")
    write_fixture(dirty, True)
    write_fixture(clean, False)

    # (1) PLANTED CONTROL FIRST -- rule 3.  If the sweep cannot see a planted
    #     contaminant, nothing it says about a clean case is worth anything.
    found = check_case(dirty, quiet=True)
    if found and len(found) == 1 and found[0][0] == os.path.join("0", "alphat"):
        print("PLANT SEEN: the planted `compressible::alphatWallFunction` in "
              "0/alphat was detected at line %d." % found[0][1])
    else:
        failures.append("PLANTED CONTROL FAILED: sweep did not see the planted "
                        "contaminant; got %r" % (found,))

    # (2) the clean fixture must come back clean
    found_clean = check_case(clean, quiet=True)
    if found_clean == []:
        print("CLEAN FIXTURE CLEAN: an incompressible case with a `calculated` "
              "wall type reports no findings.")
    else:
        failures.append("clean fixture reported %r" % (found_clean,))

    # (3) a comment-only occurrence must NOT be reported -- T4's build_t4.py:312
    #     carries the contaminant inside a `//` comment recording its own repair,
    #     and flagging that would train readers to ignore this tool.
    commented = os.path.join(tmp, "commented_case")
    write_fixture(commented, False)
    with open(os.path.join(commented, "0", "alphat"), "a") as fh:
        fh.write("    //     plate { type compressible::alphatWallFunction; }\n")
    if check_case(commented, quiet=True) == []:
        print("COMMENT NOT FLAGGED: a `//`-commented contaminant is correctly "
              "ignored, so a repair record does not read as a defect.")
    else:
        failures.append("a commented contaminant was flagged")

    # (4) THE ARM THAT BITES -- driven under `python3 -O`, refusal must FIRE.
    me = os.path.abspath(__file__)
    rcs = {}
    for tag, argv in (("python3", [sys.executable, me]),
                      ("python3 -O", [sys.executable, "-O", me])):
        p = subprocess.run(argv + ["--case", dirty], capture_output=True, text=True)
        rcs[tag] = p.returncode
    if rcs["python3"] == 2 and rcs["python3 -O"] == 2:
        print("REFUSAL FIRES UNDER `-O`: the contaminated fixture returned rc 2 "
              "under BOTH `python3` and `python3 -O`.")
    else:
        failures.append("refusal did not fire identically: %r" % (rcs,))

    for root, _d, files in os.walk(tmp, topdown=False):
        for f in files:
            os.unlink(os.path.join(root, f))
        os.rmdir(root)

    if failures:
        for f in failures:
            print("FAILED: " + f)
        return 1
    print("SELFTEST PASS: 4 arms, 0 FAILED.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", default=[],
                    help="a case directory (holding system/controlDict)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.case:
        ap.print_help()
        return 0
    dirty_total = 0
    for c in a.case:
        f = check_case(c)
        if f:
            dirty_total += len(f)
    if dirty_total:
        refuse("%d solver-namespace inconsistency(ies) found. The case template's "
               "PROVENANCE is the question: a contaminated template survives a "
               "freeze because the registration has no opinion about it." % dirty_total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
