#!/usr/bin/env python3
"""
SUBOFF_A1 -- GATE M-b-1 INSTRUMENT.  Counts cells across each named geometric
feature of a BUILT mesh, and carries the rule-3 PLANTED-ZERO CONTROL.

WHY A PLANT (CLAUDE.md rule 3).  The dangerous answer here is ZERO -- "zero cells
across the trailing-edge base" is what a resolved cusp looks like AND what a probe
box in the wrong units, the wrong coordinate, or the wrong half of a half-model
looks like.  A zero from a reader not shown able to see a non-zero is not evidence.
So PLANT_N synthetic cell centres of KNOWN count are pushed through the SAME
counting function on EVERY invocation, before any mesh is read, and the probe
REFUSES (exit 2) if the function does not return exactly PLANT_N.

HALF MODEL.  The symmetry plane z = 0 is the sail MID-plane, so only z >= 0 exists.
Both the raw half count and the full-base-equivalent (2x) are reported: a reader
given only one cannot tell a factor-of-two convention error from a result.

NEVER RUNS IN THE GRADED TREE.  It writes constant/C, which would make the rule-4
age guard unreadable (commit 0bdf38639).  It copies to a scratch dir and refuses if
--scratch is inside the case.

ZERO `assert` (L-332).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)
import os, re, json, shutil, argparse, subprocess
import numpy as np

PLANT_N = 13            # rule-3 plant: a KNOWN, ODD, non-round count
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def count_along_z(centres, x0, x1, y0, y1, zmax, tol_bins):
    """Cells across a feature in z: the number of DISTINCT z-levels of cell centres
    inside the window.  Distinct means separated by more than tol_bins."""
    m = ((centres[:, 0] >= x0) & (centres[:, 0] <= x1) &
         (centres[:, 1] >= y0) & (centres[:, 1] <= y1) &
         (centres[:, 2] >= 0.0) & (centres[:, 2] <= zmax))
    z = np.sort(centres[m, 2])
    if z.size == 0:
        return 0
    keep = 1 + int(np.sum(np.diff(z) > tol_bins))
    return keep


def plant_control():
    """Rule 3.  Build PLANT_N synthetic centres on a known segment and push them
    through count_along_z.  REFUSE unless it returns exactly PLANT_N."""
    zs = np.linspace(1.0e-4, 1.0e-3, PLANT_N)
    fake = np.column_stack([np.full(PLANT_N, 0.5), np.full(PLANT_N, 0.25), zs])
    got = count_along_z(fake, 0.4, 0.6, 0.2, 0.3, 2.0e-3, 1.0e-6)
    if got != PLANT_N:
        sys.stderr.write(f"REFUSED (rule 3): planted {PLANT_N} cell centres and the "
                         f"counting function returned {got}. The reader cannot see a "
                         f"non-zero; no zero it reports is evidence.\n")
        sys.exit(2)
    # and the converse: a window that excludes the plant must return 0, so a
    # function that returns PLANT_N unconditionally also fails.
    got0 = count_along_z(fake, 10.0, 11.0, 0.2, 0.3, 2.0e-3, 1.0e-6)
    if got0 != 0:
        sys.stderr.write(f"REFUSED (rule 3): a window EXCLUDING the plant returned "
                         f"{got0}, not 0. The counter is not reading its window.\n")
        sys.exit(2)
    return {"PLANT_N": PLANT_N, "returned": got, "excluded_window_returned": got0,
            "verdict": "ARMED"}


def read_cell_centres(case, scratch):
    if os.path.abspath(scratch).startswith(os.path.abspath(case)):
        sys.stderr.write("REFUSED: --scratch is inside the case. This probe writes "
                         "constant/C and must never touch a graded tree.\n"); sys.exit(2)
    work = os.path.join(scratch, "probe_case")
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(os.path.join(work, "constant"))
    shutil.copytree(os.path.join(case, "constant", "polyMesh"),
                    os.path.join(work, "constant", "polyMesh"))
    shutil.copytree(os.path.join(case, "system"), os.path.join(work, "system"))
    cmd = (f"set +u; source {FOAM_BASHRC} '' >/dev/null 2>&1; cd {work} && "
           f"postProcess -func writeCellCentres -constant > log.writeCellCentres 2>&1")
    subprocess.run(["bash", "-lc", cmd], check=False)
    cpath = os.path.join(work, "constant", "C")
    if not os.path.isfile(cpath):
        sys.stderr.write("REFUSED: writeCellCentres produced no constant/C. "
                         f"See {work}/log.writeCellCentres.\n"); sys.exit(2)
    txt = open(cpath).read()
    # PARSE ONLY internalField.  Measured defect, 2026-09-11: slicing from
    # "internalField" to EOF also swallows boundaryField, and the probe then read
    # 3,495,646 "cells" against checkMesh's 3,268,613 -- 227,033 BOUNDARY FACE
    # centres counted as cells.  The rule-3 plant does NOT catch this: it validates
    # the COUNTER, not the PARSER.  So the parsed count is now CROSS-CHECKED against
    # the header count that OpenFOAM itself writes, and the probe REFUSES on a
    # mismatch.
    i = txt.index("internalField")
    j = txt.find("boundaryField", i)
    body = txt[i:j if j > 0 else len(txt)]
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)", body)
    vals = re.findall(r"\(([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\)", body)
    if not vals:
        sys.stderr.write("REFUSED: constant/C parsed to zero cell centres.\n"); sys.exit(2)
    if m is None:
        sys.stderr.write("REFUSED: constant/C has no internalField element count to "
                         "cross-check the parse against.\n"); sys.exit(2)
    declared = int(m.group(1))
    if len(vals) != declared:
        sys.stderr.write(f"REFUSED: parsed {len(vals)} cell centres but constant/C "
                         f"declares {declared}. The parser is reading something that "
                         f"is not a cell centre.\n")
        sys.exit(2)
    return np.array(vals, dtype=float), work


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    plant = plant_control()                       # rule 3: BEFORE any mesh is read
    print(f"rule-3 plant: {plant}")

    man = json.load(open(os.path.join(a.case, "BUILD_MANIFEST.json")))
    (tx0, ty0, tz0), (tx1, ty1, tz1) = man["te_box_m"]
    d_te = man["finest_cell_m"]
    C, work = read_cell_centres(a.case, a.scratch)

    x_te = 0.5 * (tx0 + tx1)
    z_base_half = 0.5 * 1.310895e-3
    # sample 10 equally spaced spanwise stations over the sail span at the base
    stations = np.linspace(ty0 + 0.02 * (ty1 - ty0), ty0 + 0.98 * (ty1 - ty0), 10)
    dy = 0.5 * (stations[1] - stations[0])
    rows = []
    for ys in stations:
        n_half = count_along_z(C, x_te - 0.6 * d_te, x_te + 0.6 * d_te,
                               ys - dy, ys + dy, z_base_half, 0.25 * d_te)
        rows.append({"y_m": float(ys), "half_model_count": int(n_half),
                     "full_base_equivalent": int(2 * n_half)})
    counts = [r["full_base_equivalent"] for r in rows]

    out = {
        "case": os.path.abspath(a.case),
        "level": man["level"],
        "rule3_plant": plant,
        "finest_cell_m": d_te,
        "truncated_base_full_thickness_mm": 1.310895,
        "te_base_stations": rows,
        "te_base_full_equivalent_min": int(min(counts)),
        "te_base_full_equivalent_median": float(np.median(counts)),
        "GATE_M_b_1_TE_FLOOR": 8,
        "n_cells_total": int(C.shape[0]),
        "NOTE": "counts are MEASURED from constant/C of a SCRATCH COPY; the graded "
                "tree was not written to. The gate verdict is the cfd-supervisor's.",
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"cells total {C.shape[0]}   TE base full-equivalent counts {counts}")
    print(f"min {min(counts)}  median {np.median(counts)}  floor 8")


if __name__ == "__main__":
    main()
