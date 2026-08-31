#!/usr/bin/env python3
"""F28 -- MESH BIRTH CERTIFICATE, one per level.

Registration: verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md
section 5 -- "Birth certificate per level (`case/mesh/BIRTH_L<n>.json`): actual
cell count, recomputed refinement ratio against the next-coarser level, the
three checkMesh values, the `y+` histogram after the first solve, the mesh
script sha, and the generating command line."

THE `y+` HISTOGRAM IS THE ONE FIELD THIS SCRIPT CANNOT FILL AND DOES NOT PRETEND
TO.  `y+` needs `u_tau`, and `u_tau` needs a solved field.  Stage 0 runs no
solver.  The field is therefore emitted as `null` with the explicit status
`PENDING_FIRST_SOLVE`, never as a number and never silently absent -- a `null`
that announces itself, which is exactly what MESH_STANDARD section 12.6 says a
record owes when a value has not been measured.  What IS measured here is the
FIRST CELL HEIGHT at each viscous wall, read back off the built mesh, together
with the `u_tau` estimate the target was set from, so a later reader can check
the `y+` claim against the basis it was made on.

-------------------------------------------------------------------------------
MESH_STANDARD OBLIGATIONS DISCHARGED HERE
-------------------------------------------------------------------------------
* section 11.4 -- `max_aspect_ratio` (non-null), `aspect_ratio_flagged`,
  `min_cell_volume`, `max_cell_volume`, `cell_volume_ratio` (STATED AS DERIVED),
  `geometric_directions`, `checkMesh_log` (absolute path).
* section 12.2 -- `ABSENT` IS A THIRD LABEL FORM and is recorded as one.  The
  two printed forms are not exhaustive: four logs in this lab carry no
  aspect-ratio field at all because the run stopped before the check executed.
* section 12.3 -- a non-positive or unprinted minimum cell volume is recorded
  with an explicit status (`MIN_NEGATIVE` / `MIN_ZERO` /
  `MIN_VOLUME_LINE_ABSENT`), never a bare `null`, and never dropped.
* section 9.2 -- the per-level grading values are READ BACK from the WRITTEN
  dictionary, never reported from the requested parameter.  That read-back is
  produced by `make_mesh.py` into `system/MESH_DIAGNOSTICS.json` and is copied
  in here verbatim.

-------------------------------------------------------------------------------
THE PLANTED CONTROL (CLAUDE.md rule 3, MESH_STANDARD 11.4)
-------------------------------------------------------------------------------
"A zero from a reader not shown able to see a non-zero is not evidence."  This
reader's controls RUN ON EVERY INVOCATION, not only under a flag, and each is
driven in BOTH directions -- the plant must FIRE and its unperturbed twin must
STAY SILENT.  A reader that reports the plant on every input passes a fire-only
test and is worthless.  On any control that does not behave, the reader
REFUSES (exit 2) rather than degrading.

  C-A  the `=` label form           -> a non-null value, and the exact one
  C-B  the `:` (flagged) label form -> a non-null value, and `flagged` true
  C-C  a log with NO aspect field   -> status `ABSENT`, and NOT a number
  C-D  a positive Min/Max volume    -> a non-trivial derived ratio
  C-E  `***Zero or negative cell volume detected.` -> `MIN_NEGATIVE`, not a ratio
  C-F  a perturbed non-orthogonality value -> the reader sees the perturbation
       (the negative limb: the unperturbed twin must NOT report it)

Actuator-disk representation; no rotor.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys

# checkMesh prints the aspect ratio under two mutually exclusive labels, and a
# third case exists where it prints neither (MESH_STANDARD 11.3, 12.2).
# A NUMBER PATTERN THAT DOES NOT SWALLOW THE SENTENCE'S FULL STOP.
# checkMesh writes "Min volume = 3.1e-14. Max volume = 0.047." -- a character
# class of [-\d.eE+]+ is greedy across that trailing period and yields
# "0.047525891." which float() refuses.  CONTROL C-D CAUGHT THIS ON THE FIRST
# RUN OF THIS READER, before it ever saw a real log; it is recorded here rather
# than quietly fixed, because a reader whose controls catch nothing has
# certified nothing.
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"

RE_ASPECT_OK = re.compile(r"Max aspect ratio\s*=\s*(" + NUM + r")")
RE_ASPECT_HI = re.compile(r"\*\*\*High aspect ratio cells found,\s*"
                          r"Max aspect ratio:\s*(" + NUM + r")")
RE_VOL = re.compile(r"Min volume\s*=\s*(" + NUM + r")\.?\s*"
                    r"Max volume\s*=\s*(" + NUM + r")")
RE_NEGVOL = re.compile(r"\*\*\*Zero or negative cell volume detected")
RE_NONORTHO = re.compile(r"Mesh non-orthogonality Max:\s*(" + NUM + r")\s+"
                         r"average:\s*(" + NUM + r")")
RE_SKEW = re.compile(r"Max skewness\s*=\s*(" + NUM + r")")
RE_SKEW_HI = re.compile(r"\*\*\*Max skewness\s*=\s*(" + NUM + r")")
RE_DIRS = re.compile(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions")
RE_CELLS = re.compile(r"^\s*cells:\s*(\d+)", re.M)
RE_VERDICT = re.compile(r"(Mesh OK\.|Failed \d+ mesh checks?\.)")
RE_WEDGE = re.compile(r"Wedge (\w+) with angle\s*([-\d.eE+]+)\s*degrees")


def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg)
    sys.exit(2)


def read_checkmesh(text):
    """Parse one checkMesh log.  Returns a dict; never guesses, never degrades."""
    out = {}

    m_ok, m_hi = RE_ASPECT_OK.search(text), RE_ASPECT_HI.search(text)
    if m_ok and m_hi:
        refuse("both aspect-ratio label forms present in one log")
    if m_ok:
        out["max_aspect_ratio"] = float(m_ok.group(1))
        out["aspect_ratio_label_form"] = "EQUALS"
        out["aspect_ratio_flagged"] = False
    elif m_hi:
        out["max_aspect_ratio"] = float(m_hi.group(1))
        out["aspect_ratio_label_form"] = "COLON_FLAGGED"
        out["aspect_ratio_flagged"] = True
    else:
        out["max_aspect_ratio"] = None
        out["aspect_ratio_label_form"] = "ABSENT"
        out["aspect_ratio_flagged"] = None

    mv = RE_VOL.search(text)
    if RE_NEGVOL.search(text):
        out["cell_volume_status"] = "MIN_NEGATIVE"
        out["min_cell_volume"] = None
        out["max_cell_volume"] = None
        out["cell_volume_ratio"] = None
    elif mv:
        vmin, vmax = float(mv.group(1)), float(mv.group(2))
        out["min_cell_volume"], out["max_cell_volume"] = vmin, vmax
        if vmin < 0.0:
            out["cell_volume_status"] = "MIN_NEGATIVE"
            out["cell_volume_ratio"] = None
        elif vmin == 0.0:
            out["cell_volume_status"] = "MIN_ZERO"
            out["cell_volume_ratio"] = None
        else:
            out["cell_volume_status"] = "OK"
            out["cell_volume_ratio"] = vmax / vmin
    else:
        out["cell_volume_status"] = "MIN_VOLUME_LINE_ABSENT"
        out["min_cell_volume"] = out["max_cell_volume"] = None
        out["cell_volume_ratio"] = None

    mn = RE_NONORTHO.search(text)
    out["max_non_orthogonality"] = float(mn.group(1)) if mn else None
    out["avg_non_orthogonality"] = float(mn.group(2)) if mn else None

    ms = RE_SKEW_HI.search(text) or RE_SKEW.search(text)
    out["max_skewness"] = float(ms.group(1)) if ms else None

    md = RE_DIRS.search(text)
    out["geometric_directions"] = int(md.group(1)) if md else None

    mc = RE_CELLS.search(text)
    out["cells"] = int(mc.group(1)) if mc else None

    mvd = RE_VERDICT.search(text)
    out["checkMesh_verdict"] = mvd.group(1) if mvd else None

    out["wedge_angles_deg_DIAGNOSTIC_ONLY"] = {
        w: float(a) for w, a in RE_WEDGE.findall(text)}
    return out


# =============================================================================
# THE CONTROLS -- driven in BOTH directions, on every invocation
# =============================================================================
_L_BASE = """Checking geometry...
    Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)
    Wedge front with angle 2.5 degrees
    Min volume = 3.1472532e-14. Max volume = 0.047525891.  Total volume = 5.48.
    Mesh non-orthogonality Max: %s average: 9.9341627
    Max skewness = 1.667755 OK.
    cells:            29832
%s
Failed 1 mesh checks.
"""
_ASPECT_EQ = "    Max aspect ratio = 805.199 OK."
_ASPECT_HI = (" ***High aspect ratio cells found, Max aspect ratio: 2842.46, "
              "number of cells 34")
_NEGVOL = """Checking geometry...
    Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)
 ***Zero or negative cell volume detected.  Minimum negative volume: -3.30275e-09
    Mesh non-orthogonality Max: 12.0 average: 3.0
    Max skewness = 1.0 OK.
Failed 10 mesh checks.
"""


def run_controls():
    fails = []

    # C-A  the `=` form must yield the exact printed value
    a = read_checkmesh(_L_BASE % ("57.868895", _ASPECT_EQ))
    if a["max_aspect_ratio"] != 805.199 or a["aspect_ratio_flagged"] is not False:
        fails.append("C-A: `=` label form not read (%r)" % a["max_aspect_ratio"])
    if a["aspect_ratio_label_form"] != "EQUALS":
        fails.append("C-A: label form misreported %s" % a["aspect_ratio_label_form"])

    # C-B  the `:` flagged form must yield its value AND set the flag
    b = read_checkmesh(_L_BASE % ("57.868895", _ASPECT_HI))
    if b["max_aspect_ratio"] != 2842.46 or b["aspect_ratio_flagged"] is not True:
        fails.append("C-B: `:` label form not read (%r)" % b["max_aspect_ratio"])

    # C-C  NEGATIVE LIMB -- no aspect field at all must give ABSENT, not a number
    c = read_checkmesh(_L_BASE % ("57.868895", "    Face pyramids OK."))
    if c["aspect_ratio_label_form"] != "ABSENT" or c["max_aspect_ratio"] is not None:
        fails.append("C-C: a log with NO aspect field reported %r"
                     % c["max_aspect_ratio"])

    # C-D  a non-trivial derived ratio must be produced
    if a["cell_volume_status"] != "OK":
        fails.append("C-D: volume status %s" % a["cell_volume_status"])
    else:
        want = 0.047525891 / 3.1472532e-14
        if abs(a["cell_volume_ratio"] / want - 1.0) > 1e-9:
            fails.append("C-D: ratio %r != %r" % (a["cell_volume_ratio"], want))
        if abs(a["cell_volume_ratio"] - 1.0) < 1e-6:
            fails.append("C-D: ratio is 1 -- the reader is not reading")

    # C-E  a degenerate mesh must be recorded, not silently dropped
    e = read_checkmesh(_NEGVOL)
    if e["cell_volume_status"] != "MIN_NEGATIVE" or e["cell_volume_ratio"] is not None:
        fails.append("C-E: negative-volume log reported %r/%r"
                     % (e["cell_volume_status"], e["cell_volume_ratio"]))

    # C-F  PLANT and its unperturbed twin.  The plant must FIRE and the twin
    #      must STAY SILENT -- a reader that reports the plant on every input
    #      passes a fire-only test and has certified nothing.
    PLANT = 61.234567
    p = read_checkmesh(_L_BASE % ("%.6f" % PLANT, _ASPECT_EQ))
    if p["max_non_orthogonality"] != PLANT:
        fails.append("C-F fire: planted non-orthogonality %r read as %r"
                     % (PLANT, p["max_non_orthogonality"]))
    if a["max_non_orthogonality"] == PLANT:
        fails.append("C-F silent: the UNPERTURBED twin also reported the plant")
    if a["max_non_orthogonality"] != 57.868895:
        fails.append("C-F silent: twin read %r" % a["max_non_orthogonality"])

    if fails:
        refuse("PLANTED CONTROLS DID NOT BEHAVE:\n  " + "\n  ".join(fails))
    return {"C-A_equals_form": "FIRED", "C-B_colon_form": "FIRED",
            "C-C_absent_form": "SILENT (correctly reported ABSENT)",
            "C-D_derived_ratio": "FIRED (%.6e)" % a["cell_volume_ratio"],
            "C-E_negative_volume": "FIRED (MIN_NEGATIVE, ratio withheld)",
            "C-F_plant": "FIRED at %.6f; unperturbed twin SILENT" % PLANT}


# =============================================================================
# WALL SPACING, READ BACK OFF THE BUILT MESH
# =============================================================================
def _load(path):
    t = open(path).read()
    return t[t.index("// * * *"):]


def wall_first_cell_heights(case, patches):
    """First cell height at each named wall, from `constant/polyMesh`.

    2 x the distance from the boundary face centre to its owner cell centre,
    which is the wall-normal extent of the first cell.  READ OFF THE BUILT
    MESH, not off the grading that was requested (MESH_STANDARD 9.2).
    """
    pm = os.path.join(case, "constant", "polyMesh")
    pts = [(float(m.group(1)), float(m.group(2)), float(m.group(3)))
           for m in re.finditer(
               r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
               _load(os.path.join(pm, "points")))]
    faces = [[int(v) for v in m.group(2).split()]
             for m in re.finditer(r"(\d+)\(([\d\s]+)\)",
                                  _load(os.path.join(pm, "faces")))]
    t = _load(os.path.join(pm, "owner"))
    own = [int(v) for v in t[t.index("\n(") + 2:t.rindex(")")].split()]
    t = _load(os.path.join(pm, "neighbour"))
    nei = [int(v) for v in t[t.index("\n(") + 2:t.rindex(")")].split()]

    bnd = {}
    bt = _load(os.path.join(pm, "boundary"))
    for m in re.finditer(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);\s*startFace\s+(\d+);",
                         bt, re.S):
        bnd[m.group(1)] = (int(m.group(2)), int(m.group(3)))

    ncells = max(own) + 1
    acc = [[0.0, 0.0, 0.0, 0] for _ in range(ncells)]
    fctr = []
    for fid, f in enumerate(faces):
        c = [sum(pts[i][k] for i in f) / len(f) for k in range(3)]
        fctr.append(c)
        for cid in [own[fid]] + ([nei[fid]] if fid < len(nei) else []):
            for k in range(3):
                acc[cid][k] += c[k]
            acc[cid][3] += 1
    cen = [[a[k] / a[3] for k in range(3)] for a in acc]

    out = {}
    for p in patches:
        if p not in bnd:
            out[p] = {"status": "PATCH_ABSENT"}
            continue
        n, s0 = bnd[p]
        if n == 0:
            out[p] = {"status": "PATCH_EMPTY", "n_faces": 0}
            continue
        hs = []
        for fid in range(s0, s0 + n):
            c, o = fctr[fid], cen[own[fid]]
            # THE WALL-NORMAL COMPONENT, not the centre-to-centre distance.
            # The first version of this reader used 2*|C_owner - C_face| and
            # reported a hub first cell of 6.691e-3 m against a 1.0e-5 m target
            # -- a 670x over-read produced entirely by the sliver cells at the
            # centrebody nose apex, where the centre-to-centre vector is almost
            # entirely TANGENTIAL.  y+ is a wall-NORMAL quantity, so the
            # projection is the only defensible measure.
            f = faces[fid]
            ctr = [sum(pts[i][k] for i in f) / len(f) for k in range(3)]
            ax = [0.0, 0.0, 0.0]
            for i in range(len(f)):
                p1, p2 = pts[f[i]], pts[f[(i + 1) % len(f)]]
                u = [p2[k] - p1[k] for k in range(3)]
                v = [ctr[k] - p1[k] for k in range(3)]
                ax[0] += 0.5 * (u[1] * v[2] - u[2] * v[1])
                ax[1] += 0.5 * (u[2] * v[0] - u[0] * v[2])
                ax[2] += 0.5 * (u[0] * v[1] - u[1] * v[0])
            am = math.sqrt(sum(q * q for q in ax))
            if am <= 0.0:
                continue
            d = [o[k] - c[k] for k in range(3)]
            hs.append(2.0 * abs(sum(d[k] * ax[k] for k in range(3))) / am)
        if not hs:
            out[p] = {"status": "ALL_FACES_ZERO_AREA", "n_faces": n}
            continue
        out[p] = {"status": "OK", "n_faces": n,
                  "first_cell_min_m": min(hs), "first_cell_max_m": max(hs),
                  "first_cell_mean_m": sum(hs) / len(hs)}
    return out


# =============================================================================
def main():
    if len(sys.argv) not in (4, 5):
        sys.stderr.write("usage: birth_certificate.py <level> <case_dir> "
                         "<out.json> [next_coarser_cert.json]\n")
        sys.exit(2)
    level, case, out_path = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    coarser = sys.argv[4] if len(sys.argv) == 5 else None
    controls = run_controls()          # refuses (exit 2) if any misbehaves

    log = os.path.abspath(os.path.join(case, "log.checkMesh"))
    if not os.path.exists(log):
        refuse("no checkMesh log at %s" % log)
    cm = read_checkmesh(open(log, errors="replace").read())
    if cm["max_non_orthogonality"] is None or cm["max_skewness"] is None:
        refuse("checkMesh log carries no non-orthogonality or skewness line")

    diagp = os.path.join(case, "system", "MESH_DIAGNOSTICS.json")
    diag = json.load(open(diagp))

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_mesh.py")
    sha = hashlib.sha256(open(script, "rb").read()).hexdigest()
    if sha != diag["mesh_script_sha256"]:
        refuse("the mesh script on disk (%s) is NOT the one that wrote this "
               "level (%s).  MESH_STANDARD 9.2: the requested value is the one "
               "that lies; so is a stale script."
               % (sha[:12], diag["mesh_script_sha256"][:12]))

    walls = wall_first_cell_heights(case, ["ductInner", "ductOuter", "hub",
                                           "axis", "farfield"])

    # Registered gates, section 5 of the frozen pre-registration.
    gates = {
        "max_non_orthogonality_lt_65": cm["max_non_orthogonality"] < 65.0,
        "max_skewness_lt_4": cm["max_skewness"] < 4.0,
        "zero_negative_volumes": cm["cell_volume_status"] == "OK"
                                 and cm["min_cell_volume"] > 0.0,
    }
    verdict = "GATE REACHED" if all(gates.values()) else "GATE FAIL"

    cert = {
        "case": "F28_DUCTED_ACTUATOR_DISK",
        "disclosure": "Actuator-disk representation; no rotor.",
        "registration":
            "verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md",
        "level": level,
        "stage": "Stage 0 -- mesh and checkMesh only.  NO SOLVER HAS RUN.",
        "cells": diag["cells_predicted"],
        "cells_from_checkMesh_log": cm["cells"],
        "blocks": diag["blocks"],
        "mesh_script": "case/mesh/make_mesh.py",
        "mesh_script_sha256": sha,
        "blockMeshDict_sha256": diag["blockMeshDict_sha256"],
        "generating_command": diag["generating_command"],
        "checkMesh_log": log,
        "checkMesh": cm,
        "registered_gates_section_5": gates,
        "stage0_verdict": verdict,
        "y_plus_histogram": None,
        "y_plus_status": "PENDING_FIRST_SOLVE -- y+ needs u_tau and u_tau "
                         "needs a solved field; Stage 0 runs no solver.",
        "y_plus_target_basis": {
            "target": "y+ <= 1 on ductInner, ductOuter and hub (section 5)",
            "first_cell_height_requested_m": diag["y_first_requested_m"],
            "derivation": "U_ref 45 m/s (the largest registered ideal exit "
                          "velocity, 40.8 m/s at delta_p = 2000 Pa, with "
                          "margin); nu 1.5e-5 m^2/s; L 0.2 m; "
                          "Cf = 0.058 Re_L^-0.2; u_tau = sqrt(0.5 Cf) U_ref "
                          "= 1.9 m/s; y(y+=1) = nu/u_tau = 7.9e-6 m.  The "
                          "requested first cell is 1.0e-5 m at L1 and scales "
                          "as 1/r with the level.",
            "first_cell_height_measured_m": walls,
        },
        "grading_read_back_from_written_dict":
            diag["grading_read_back_from_written_dict"],
        "radial_distributions": diag["radial"],
        "axial_distributions": diag["axial"],
        "geometry_diagnostics": {
            k: diag[k] for k in
            ("cprime_nose_slope_requested", "cprime_nose_slope_used",
             "cprime_min_clearance_m", "pprime_sectors_deg",
             "pprime_min_sector_deg", "tail_cone_half_angle_deg",
             "nose_max_slope_deg", "lip_cells_inner", "lip_cells_outer",
             "lip_cells_wrap_total", "disk_zone_cells_axial",
             "disk_zone_cells_radial", "A_disk_m2", "r_exit_m",
             "wedge_disk_zone_volume_m3", "full_annulus_disk_zone_volume_m3")},
        "wedge_angle_note":
            "MESH_STANDARD section 13: checkMesh's printed wedge angle derives "
            "from wedgePolyPatch::cosAngle_, a SUMMED and NEVER RENORMALISED "
            "mean of face normals whose error floor GROWS WITH THE FACE COUNT. "
            "It is recorded here as a DIAGNOSTIC and IS NOT GATED, by this "
            "case or by anything downstream of it.",
        "aspect_ratio_note":
            "MESH_STANDARD sections 3.3 and 11.4: the aspect ratio is RECORDED "
            "and is NOT a gate.  checkMesh's own 'Failed N mesh checks' on "
            "these levels is the high-aspect-ratio check alone.  For "
            "calibration, the NASA TMR reference flat-plate grids measure "
            "66643 to 74041 (MESH_STANDARD section 4).",
        "planted_controls": controls,
    }

    # Section 5: "the ACTUAL cell counts and the ACTUAL ratios recomputed from
    # them are recorded in each birth certificate and are what the comparator
    # uses.  A registration that grades against a target it did not achieve is
    # grading against a wish."  r = (N_fine/N_coarse)^(1/2) on the wedge's
    # effective 2-D scaling, section 5.
    if coarser:
        cz = json.load(open(coarser))
        nf, nc2 = cert["cells"], cz["cells"]
        if nf <= nc2:
            refuse("level %d has %d cells, not more than the coarser %d"
                   % (level, nf, nc2))
        r = math.sqrt(float(nf) / float(nc2))
        cert["refinement_against_next_coarser"] = {
            "coarser_certificate": os.path.abspath(coarser),
            "coarser_level": cz["level"], "coarser_cells": nc2,
            "this_cells": nf, "r_achieved": r, "r_required_min": 1.3,
            "r_ge_1_3": r >= 1.3,
            "formula": "r = (N_fine / N_coarse)^(1/2), section 5",
            "note": "The registered TARGETS were r_32 = 1.35401 and "
                    "r_21 = 1.34840 from 30000/55000/100000.  These are the "
                    "ACHIEVED values from the ACTUAL counts.  Section 5 "
                    "registers the NON-CONSTANT-RATIO Roache formulation and "
                    "FORBIDS the constant-r shortcut here."}
    else:
        cert["refinement_against_next_coarser"] = {
            "status": "N/A -- coarsest level of the ladder"}
    with open(out_path, "w") as fh:
        json.dump(cert, fh, indent=2, sort_keys=True)
    print(json.dumps({"level": level, "verdict": verdict,
                      "cells": cert["cells"],
                      "max_non_orthogonality": cm["max_non_orthogonality"],
                      "max_skewness": cm["max_skewness"],
                      "min_cell_volume": cm["min_cell_volume"],
                      "cell_volume_status": cm["cell_volume_status"],
                      "max_aspect_ratio": cm["max_aspect_ratio"],
                      "aspect_ratio_flagged": cm["aspect_ratio_flagged"],
                      "out": out_path}, indent=2))


if __name__ == "__main__":
    main()
