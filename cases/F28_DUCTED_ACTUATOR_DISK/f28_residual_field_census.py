#!/usr/bin/env python3
"""F28 sibling-run spatial-residual census.

Answers the question left OPEN at
verification/campaign/F28G_L1_RESIDUAL_RECONCILIATION.md Addendum 1 sec A1.5:

    "I established `writeResidualFields false` for THIS run only; the other seven
     `F28_runs` logs were not checked for the same switch, so whether any sibling
     run carries spatial residuals is OPEN, and it is the first thing the item-2
     registration should check -- if a sibling has them, item 2 may be cheaper
     than a re-run."

Standing rule 3: this reader plants a KNOWN `writeResidualFields true` and a
KNOWN spatial residual field into a scratch tree and REFUSES unless it reads
both back.  A zero from a reader not shown able to see a non-zero is not
evidence.

Zero solver compute.  Reads only.
"""

import os
import re
import shutil
import sys
import tempfile

ROOT = "/home/ubuntu/Certonomous/verification/runs/F28_runs"

# A spatial residual field written by the `solverInfo` FO is named
# `<field>Residual` (v2606: solverInfo.C writes `residualFieldName = fieldName +
# "Residual"`).  Anything matching this in a time directory is a spatial field.
RESIDUAL_FIELD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.]*Residual$")

SWITCH_RE = re.compile(r"writeResidualFields\s+(\w+)\s*;")


def read_switch(case):
    """Return (state, path) for writeResidualFields in this case's controlDict."""
    cd = os.path.join(case, "system", "controlDict")
    if not os.path.isfile(cd):
        return ("NO_CONTROLDICT", cd)
    with open(cd, "r", errors="replace") as fh:
        text = fh.read()
    hits = SWITCH_RE.findall(text)
    if not hits:
        return ("SWITCH_ABSENT", cd)
    if len(set(hits)) > 1:
        return ("SWITCH_AMBIGUOUS:" + ",".join(hits), cd)
    return (hits[0], cd)


def time_dirs(case):
    out = []
    if not os.path.isdir(case):
        return out
    for name in os.listdir(case):
        p = os.path.join(case, name)
        if not os.path.isdir(p):
            continue
        try:
            float(name)
        except ValueError:
            continue
        out.append((float(name), name, p))
    out.sort()
    return out


def spatial_residual_fields(case):
    """Every file in any time directory (serial or processor*) whose name is a
    spatial residual field."""
    found = []
    roots = [case]
    for name in sorted(os.listdir(case)) if os.path.isdir(case) else []:
        if name.startswith("processor"):
            roots.append(os.path.join(case, name))
    for r in roots:
        for _, tname, tpath in time_dirs(r):
            for f in sorted(os.listdir(tpath)):
                if RESIDUAL_FIELD_RE.match(f):
                    found.append(os.path.join(os.path.relpath(tpath, case), f))
    return found


def residuals_fo_dir_contents(case):
    base = os.path.join(case, "postProcessing", "residuals")
    if not os.path.isdir(base):
        return None
    out = []
    for dirpath, _dirnames, filenames in os.walk(base):
        for f in sorted(filenames):
            out.append(os.path.relpath(os.path.join(dirpath, f), base))
    return sorted(out)


def is_run_root(p):
    return os.path.isdir(os.path.join(p, "system")) or os.path.isfile(
        os.path.join(p, "log.simpleFoam")
    )


# ---------------------------------------------------------------- planted control
def planted_control():
    """Build a scratch case the reader MUST see as (true, one spatial field).
    Then build its negative limb: same tree with the plant removed."""
    tmp = tempfile.mkdtemp(prefix="f28_plant_")
    try:
        case = os.path.join(tmp, "PLANTED")
        os.makedirs(os.path.join(case, "system"))
        os.makedirs(os.path.join(case, "15000"))
        cd = os.path.join(case, "system", "controlDict")
        with open(cd, "w") as fh:
            fh.write(
                "functions\n{\n  residuals\n  {\n    type solverInfo;\n"
                "    fields (p U k omega);\n    writeResidualFields true;\n  }\n}\n"
            )
        # the plant: a spatial residual field, and a decoy that must NOT match
        open(os.path.join(case, "15000", "pResidual"), "w").write("planted\n")
        open(os.path.join(case, "15000", "p"), "w").write("not a residual field\n")

        sw, _ = read_switch(case)
        fields = spatial_residual_fields(case)
        pos_ok = (sw == "true") and (len(fields) == 1) and fields[0].endswith("pResidual")

        # negative limb: flip the switch and remove the field
        with open(cd, "w") as fh:
            fh.write(
                "functions\n{\n  residuals\n  {\n    type solverInfo;\n"
                "    fields (p U k omega);\n    writeResidualFields false;\n  }\n}\n"
            )
        os.remove(os.path.join(case, "15000", "pResidual"))
        sw2, _ = read_switch(case)
        fields2 = spatial_residual_fields(case)
        neg_ok = (sw2 == "false") and (fields2 == [])

        return pos_ok, neg_ok, sw, fields, sw2, fields2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    pos_ok, neg_ok, sw, fields, sw2, fields2 = planted_control()
    print("=== PLANTED CONTROL (standing rule 3) ===")
    print("  positive limb: switch read back = %r, spatial fields = %r -> %s"
          % (sw, fields, "SEEN" if pos_ok else "NOT SEEN"))
    print("  negative limb: switch read back = %r, spatial fields = %r -> %s"
          % (sw2, fields2, "CLEAN" if neg_ok else "DIRTY"))
    if not (pos_ok and neg_ok):
        print("REFUSE (exit 2): the reader was not shown able to see a non-zero.")
        return 2
    print("  reader is LIVE.  A zero below is a reading.\n")

    cases = []
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p) and is_run_root(p):
            cases.append(p)

    print("=== CENSUS: every F28 run root under %s ===" % ROOT)
    print("%-46s %-22s %-8s %s" % ("run root", "writeResidualFields", "nTimes", "spatial residual fields"))
    any_spatial = 0
    any_true = 0
    for c in cases:
        sw, _cd = read_switch(c)
        f = spatial_residual_fields(c)
        nt = len(time_dirs(c))
        if f:
            any_spatial += 1
        if sw == "true":
            any_true += 1
        print("%-46s %-22s %-8d %s" % (os.path.basename(c), sw, nt, f if f else "NONE"))

    print("\nrun roots examined              : %d" % len(cases))
    print("with writeResidualFields true   : %d" % any_true)
    print("carrying ANY spatial residual   : %d" % any_spatial)

    # the FO directory contents for the graded rung specifically
    graded = os.path.join(ROOT, "F28G_L1_dp1000_U20")
    print("\n=== postProcessing/residuals/ contents, graded rung ===")
    print(residuals_fo_dir_contents(graded))
    return 0


if __name__ == "__main__":
    sys.exit(main())
