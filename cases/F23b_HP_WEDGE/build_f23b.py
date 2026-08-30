#!/usr/bin/env python3
"""
F23b -- BUILD ONE LEVEL, AND THE G-WEDGE GUARD (prereg section 4.3, AMENDMENT 1).

Registration: verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md,
              frozen at 57d31dde; AMENDMENT 1 (pre-compute) at 440aca3d.

WHAT F23 DIED ON, AND WHAT REPLACED IT.  `build_f23.py:129-130` refused the built
fine mesh on a FIXED ABSOLUTE 1e-6 tolerance over checkMesh's printed wedge
angle, while `checkMesh` itself printed `Mesh OK.` at all three levels.  Section
4.2 MEASURED why: the printed angle is floating-point summation error inside
`gAverage(faceNormals)` amplified by the ill-conditioning of `acos` near 1, and a
fixed absolute tolerance on a quantity whose floor GROWS WITH THE CELL COUNT was
guaranteed to fail at some level.  Medium already sat at 80 % of the budget.

G-WEDGE, THREE LIMBS (section 4.3):
  LIMB 1  PRIMARY.  From the level's own `constant/polyMesh`, for EVERY face of
          both wedge patches, the angle to the cardinal normal in the
          well-conditioned form `atan2(hypot(n_x, n_y), |n_z|)`; `acos` is never
          called.  Refuses above TOL_REL_WEDGE(level), which is refinement-aware.
  LIMB 2  CROSS-CHECK ON THE MESHER, at its own much blunter resolution:
          checkMesh's OWN printed angle, read from the level's own
          `log.checkMesh`, against TOL_CM(level).  **Limb 2 is ~1,340x blunter
          than limb 1 and is registered as a cross-check, NOT as the sharp
          guard** -- stated here so no record can later present it as the guard
          that did the work.
  LIMB 3  MESH_STANDARD section 3, byte-for-byte F23: `Mesh OK`; max
          non-orthogonality <= 70 deg; max skewness <= 4; aspect ratio recorded
          at the 1000 advisory; cell count == NR x NX; both wedge patches
          present and reported.

THE GUARD MAY NOT GRADE UNTIL IT HAS BEEN BORN (AMENDMENT 1 section A1.4, Sanaa
2026-08-28T17:01Z).  `--level` REFUSES (exit 2) unless
`GWEDGE_CONTROL_RECEIPT.txt` is present, carries this document's freeze sha, and
records a `blockMesh`-path control driven BOTH WAYS at coarse and at fine.  A
points-level plant proves the READER sees a perturbation; it does not prove the
BUILDER can deliver one, and the registration is explicit that the
points-level control is the WEAKER limb and may not substitute.

THE BUILDER REFUSES; IT DOES NOT REPAIR, AND IT DELETES NOTHING.  A destination
holding `0/`, a numeric time directory or `processor*` is REFUSED.  Zero
`assert` (L-332); hard `-O` refusal at entry.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: build_f23b.py must not run under `python3 -O`; G-WEDGE is made of "
                     "checks -O would blind (L-332).\n")
    sys.exit(2)

import os
import re
import json
import math
import time
import shutil
import argparse
import tempfile
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f23b as EX            # noqa: E402
import foam_io_f23b as FIO         # noqa: E402
import numpy as np                 # noqa: E402

CASE_SRC = os.path.join(HERE, "case")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
RECEIPT = os.path.join(HERE, "GWEDGE_CONTROL_RECEIPT.txt")
# AMENDMENT 1 section A1.4 drives the blockMesh-path control at these two levels.
RECEIPT_LEVELS = ("coarse", "fine")
# F23's retained run root, read READ-ONLY as the points-level control's artifact
# (prereg section 4.4; section 9.4: "deleting it would delete the evidence").
F23_RUNS = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                        "verification", "runs", "F23_HP_WEDGE_runs")


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f23b): %s\n" % msg)
    sys.exit(rc)


def refuse(msg):
    sys.stderr.write("REFUSED (build_f23b): %s\n" % msg)
    sys.exit(2)


def foam(cmd, case_dir, log):
    # `set -u` is never in force here (L-339: the bashrc reads unbound variables).
    full = ". %s > /dev/null 2>&1; %s -case %s > %s 2>&1" % (FOAM_BASHRC, cmd, case_dir, log)
    return subprocess.run(["bash", "-c", full]).returncode


def refuse_if_answered(dest):
    if os.path.isdir(dest):
        for d in os.listdir(dest):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?", d) or re.fullmatch(r"processor[0-9]+", d):
                die("%s already holds %s. REFUSED, not deleted (rule 4)." % (dest, d), rc=2)


# ---------------------------------------------------------------------------
# THE BIRTH RECEIPT -- AMENDMENT 1 section A1.4
# ---------------------------------------------------------------------------
def write_receipt(path, prereg_commit, rows):
    with open(path, "w") as f:
        f.write("# F23b G-WEDGE blockMesh-path control receipt (AMENDMENT 1 section A1.4)\n")
        f.write("# The guard does not grade until this control has been driven BOTH WAYS and passed.\n")
        f.write("prereg_commit=%s\n" % prereg_commit)
        f.write("utc=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        for r in rows:
            f.write("row %s\n" % json.dumps(r, sort_keys=True))


def read_receipt(path):
    if not os.path.isfile(path):
        return None, "absent"
    commit, utc, rows = None, None, []
    for line in open(path, errors="replace"):
        if line.startswith("prereg_commit="):
            commit = line.split("=", 1)[1].strip()
        elif line.startswith("utc="):
            utc = line.split("=", 1)[1].strip()
        elif line.startswith("row "):
            try:
                rows.append(json.loads(line[4:]))
            except ValueError as e:
                return None, "unparsable row: %s" % e
    if not commit or not rows:
        return None, "carries no prereg_commit or no rows"
    return dict(prereg_commit=commit, utc=utc, rows=rows), None


def check_receipt(path, prereg_commit):
    """Returns the receipt or REFUSES (exit 2).  Called at entry by `--level`
    here and by grade_f23b.py -- an undriven control certifies blindness, and a
    guard that cannot show it was born does not grade."""
    rec, why = read_receipt(path)
    if rec is None:
        refuse("G-WEDGE's birth control receipt %s is %s. AMENDMENT 1 section A1.4: the guard MAY "
               "NOT GRADE ANYTHING until the blockMesh-path control has been driven, both "
               "directions, and passed. Drive it with `build_f23b.py --gwedge-control "
               "--workdir <scratch> --prereg-commit=<sha>`." % (path, why))
    if rec["prereg_commit"] != prereg_commit:
        refuse("the receipt %s records prereg_commit %r; this invocation runs under %r. A control "
               "driven under a different sha is not this rung's control."
               % (path, rec["prereg_commit"], prereg_commit))
    seen = {}
    for r in rec["rows"]:
        seen.setdefault(r.get("level"), set()).add(r.get("direction"))
        tol = EX.TOL_REL_WEDGE.get(r.get("level"))
        if tol is None:
            refuse("the receipt carries an unregistered level %r" % r.get("level"))
        if r.get("direction") == "MUST_REFUSE":
            ratio = float(r["limb1_max_rel"]) / tol
            lo, hi = EX.GWEDGE_PLANT_RATIO_BAND
            if not (lo <= ratio <= hi):
                refuse("receipt row %s/%s: the planted reading is %.6e = %.4f x TOL_REL_WEDGE, "
                       "outside the registered control band [%.1f, %.1f]. A reading below %.1fx is a "
                       "plant that did not travel; above %.1fx is a plant that travelled differently "
                       "than registered. Both refuse."
                       % (r["level"], r["direction"], r["limb1_max_rel"], ratio, lo, hi, lo, hi))
            if not r.get("refused"):
                refuse("receipt row %s/MUST_REFUSE records that the guard ACCEPTED the perturbed "
                       "mesh; the control did not fire and IT IS MEASURING NOTHING" % r["level"])
        elif r.get("direction") == "MUST_ACCEPT":
            if float(r["limb1_max_rel"]) > EX.GWEDGE_ACCEPT_CEILING:
                refuse("receipt row %s/MUST_ACCEPT: limb 1 read %.6e on an UNPERTURBED mesh, above "
                       "the registered ceiling %.1e. A guard that refuses everything is not a guard."
                       % (r["level"], r["limb1_max_rel"], EX.GWEDGE_ACCEPT_CEILING))
            if r.get("refused"):
                refuse("receipt row %s/MUST_ACCEPT records a REFUSAL on a correctly built mesh"
                       % r["level"])
        else:
            refuse("receipt row carries an unknown direction %r" % r.get("direction"))
    for lvl in RECEIPT_LEVELS:
        if seen.get(lvl) != {"MUST_REFUSE", "MUST_ACCEPT"}:
            refuse("the receipt does not carry BOTH directions at level %r (it carries %s). "
                   "A control shown able to move in only one direction is not a control."
                   % (lvl, sorted(seen.get(lvl, []))))
    return rec


# ---------------------------------------------------------------------------
# G-WEDGE
# ---------------------------------------------------------------------------
def gwedge_limb1(mesh_dir, half_angle_deg, tol_rel):
    """Limb 1 over BOTH wedge patches.  Returns (max_rel, per-patch readings)."""
    out = {}
    worst = 0.0
    for patch in ("wedge1", "wedge2"):
        r = FIO.wedge_limb1(mesh_dir, patch, half_angle_deg)
        out[patch] = r
        worst = max(worst, r["max_rel_dev"])
    return worst, out, worst <= tol_rel


def gwedge_limb2(log_checkmesh, half_angle_deg, tol_cm):
    """Limb 2 from ONE NAMED ARTIFACT: the level's own log.checkMesh."""
    ang = FIO.checkmesh_wedge_angles(log_checkmesh)
    if set(ang) != {"wedge1", "wedge2"}:
        return None, ang, False
    dev = max(abs(v - half_angle_deg) for v in ang.values())
    return dev, ang, dev <= tol_cm


# ---------------------------------------------------------------------------
# THE BUILD
# ---------------------------------------------------------------------------
def _write_controlDict(dest, n_iter):
    """Copy the frozen controlDict and set endTime / writeInterval to the count
    section 5.5's branch rule chose.  At the registered N_ITER = 400 the
    destination is BYTE-IDENTICAL to the frozen source; the substitution is
    ASSERTED (each pattern must occur exactly once before and the new value
    exactly once after), never a silent replace (L-221/L-222)."""
    src = open(os.path.join(CASE_SRC, "system", "controlDict")).read()
    wi = EX.write_every(n_iter)
    text = src
    for pat, new, what in ((r"^(\s*endTime\s+)\d+(\s*;)", r"\g<1>%d\g<2>" % n_iter, "endTime"),
                           (r"^(\s*writeInterval\s+)\d+(\s*;)", r"\g<1>%d\g<2>" % wi, "writeInterval")):
        n_before = len(re.findall(pat, text, re.M))
        if n_before != 1:
            die("controlDict carries %d %s lines, expected exactly 1" % (n_before, what))
        text = re.sub(pat, new, text, flags=re.M)
    if len(re.findall(r"^\s*endTime\s+%d\s*;" % n_iter, text, re.M)) != 1:
        die("the endTime substitution did not land")
    if len(re.findall(r"^\s*writeInterval\s+%d\s*;" % wi, text, re.M)) != 1:
        die("the writeInterval substitution did not land")
    open(os.path.join(dest, "system", "controlDict"), "w").write(text)
    return n_iter, wi


def _write_fvSolution(dest, a0_dictionary):
    """Copy the frozen fvSolution.  With `a0_dictionary` the DESTINATION COPY is
    rewritten to F23's alpha_U = 0.7 settings -- AMENDMENT 1 item A0 only.

    WHY A0 RUNS UNDER THE OLD DICTIONARY, WHICH IS THE POINT OF IT (A1.5): the
    arm-acceptance reader's ACCEPT side must not depend on the very thing ARM-P
    is testing.  Were A0 run under section 5.3's SIMPLEC settings and SIMPLEC
    failed, no accepting artifact could ever exist and the reader could never be
    born -- a control defined in terms of the thing it controls.  F23 section 7
    records that exact 16 x 64 configuration converging (Ux 2.3e-16 by iteration
    4,000), so it is the one configuration on this box already KNOWN to deliver a
    converged artifact.  Only the relaxation differs; the producer, the file
    schema and the reader path are identical.  NO FILE IS ADDED to section 12's
    frozen list: the frozen fvSolution is never edited, only its destination copy.
    """
    text = open(os.path.join(CASE_SRC, "system", "fvSolution")).read()
    note = "section 5.3 SIMPLEC dictionary (consistent yes, alpha_U = 1.0)"
    if a0_dictionary:
        subs = ((r"consistent\s+yes\s*;", "consistent      no;", "consistent"),
                (r"fields\s*\{\s*p\s+1\.0;\s*\}", "fields    { p 0.3; }", "fields p"),
                (r"equations\s*\{\s*U\s+1\.0;\s*\}", "equations { U 0.7; }", "equations U"))
        for pat, new, what in subs:
            if len(re.findall(pat, text)) != 1:
                die("A0 dictionary: %s does not occur exactly once in the frozen fvSolution" % what)
            text = re.sub(pat, new, text)
        for want in ("consistent      no;", "{ p 0.3; }", "{ U 0.7; }"):
            if text.count(want) != 1:
                die("A0 dictionary: the substitution %r did not land exactly once" % want)
        note = "AMENDMENT 1 item A0: F23's alpha_U = 0.7 dictionary (consistent no, p 0.3, U 0.7)"
    open(os.path.join(dest, "system", "fvSolution"), "w").write(text)
    return note


def build(dest, level, nr, nx, n_iter, half_angle_deg, tol_rel, tol_cm, enforce_geometry=True,
          a0_dictionary=False):
    """Template, mesh, gate, write 0/C, 0/V, 0/p and 0/U LAST OF ALL."""
    if os.path.realpath(dest).startswith(os.path.realpath(CASE_SRC)):
        die("destination %s lies inside the tracked case tree; refused" % dest, rc=2)
    refuse_if_answered(dest)
    for sub in ("system", "constant"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for f in ("fvSchemes", "decomposeParDict"):
        shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
    for f in ("transportProperties", "turbulenceProperties", "fvOptions"):
        shutil.copy(os.path.join(CASE_SRC, "constant", f), os.path.join(dest, "constant", f))
    solver_note = _write_fvSolution(dest, a0_dictionary)
    end_time, write_interval = _write_controlDict(dest, n_iter)
    a = math.radians(half_angle_deg)
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "blockMeshDict.template"),
                            os.path.join(dest, "system", "blockMeshDict"),
                            {"__NX__": str(nx), "__NR__": str(nr), "__L__": repr(EX.L),
                             "__YW__": repr(EX.R * math.cos(a)), "__ZW__": repr(EX.R * math.sin(a)),
                             "__HALF_ANGLE_DEG__": repr(half_angle_deg)})
    # --- the dictionaries on disk must be the registered ones -----------------
    tp = open(os.path.join(dest, "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        die("transportProperties nu is not exact_f23b.NU")
    fo = open(os.path.join(dest, "constant", "fvOptions")).read()
    m = re.search(r"U\s+\(\(\s*([0-9eE+\-.]+)\s+0\s+0\s*\)\s+0\s*\)\s*;", fo)
    if not m or abs(float(m.group(1)) - EX.G) > 1e-15:
        die("fvOptions momentum source is not exact_f23b.G = %.17g" % EX.G)
    fs = open(os.path.join(dest, "system", "fvSolution")).read()
    if not a0_dictionary and not re.search(r"consistent\s+yes\s*;", fs):
        die("fvSolution does not carry `consistent yes` (SIMPLEC); section 5.3 registers it")
    if a0_dictionary and not re.search(r"equations\s*\{\s*U\s+0\.7;\s*\}", fs):
        die("the A0 dictionary was requested but the destination fvSolution does not carry "
            "alpha_U = 0.7; A0's independence from what it certifies rests on that")
    if re.search(r"^\s*residualControl", fs, re.M):
        die("fvSolution carries residualControl; the run must go to endTime")
    dp = open(os.path.join(dest, "system", "decomposeParDict")).read()
    m = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
    if not m or int(m.group(1)) != EX.RANKS:
        die("decomposeParDict numberOfSubdomains is not the registered %d" % EX.RANKS)

    # --- mesh -----------------------------------------------------------------
    if foam("blockMesh", dest, os.path.join(dest, "log.blockMesh")) != 0:
        die("blockMesh failed; see %s/log.blockMesh" % dest)
    if foam("checkMesh", dest, os.path.join(dest, "log.checkMesh")) != 0:
        die("checkMesh failed; see %s/log.checkMesh" % dest)
    cm = open(os.path.join(dest, "log.checkMesh"), errors="replace").read()

    # --- LIMB 3: MESH_STANDARD section 3, byte-for-byte F23 -------------------
    if "Mesh OK" not in cm:
        die("checkMesh did not report `Mesh OK`")
    m_cells = re.search(r"^\s*cells:\s+(\d+)", cm, re.M)
    m_no = re.search(r"non-orthogonality Max: ([0-9.eE+-]+)", cm)
    m_sk = re.search(r"Max skewness = ([0-9.eE+-]+)", cm)
    m_ar = re.search(r"Max aspect ratio = ([0-9.eE+-]+)", cm)
    if not (m_cells and m_no and m_sk and m_ar):
        die("could not read cells / non-orthogonality / skewness / aspect ratio from log.checkMesh")
    cells = int(m_cells.group(1))
    if cells != nr * nx:
        die("built mesh has %d cells, level %s registers %d" % (cells, level, nr * nx))
    if float(m_no.group(1)) > EX.MAX_NON_ORTHO:
        die("max non-orthogonality %s exceeds the %g deg gate" % (m_no.group(1), EX.MAX_NON_ORTHO))
    if float(m_sk.group(1)) > EX.MAX_SKEW:
        die("max skewness %s exceeds the gate %g" % (m_sk.group(1), EX.MAX_SKEW))

    # --- LIMB 1 (PRIMARY) and LIMB 2 (cross-check on the mesher) --------------
    mesh_dir = os.path.join(dest, "constant", "polyMesh")
    l1, l1_detail, l1_ok = gwedge_limb1(mesh_dir, half_angle_deg, tol_rel)
    l2, l2_ang, l2_ok = gwedge_limb2(os.path.join(dest, "log.checkMesh"), half_angle_deg, tol_cm)
    if l2 is None:
        die("checkMesh did not report both wedge patches' angles: %s" % l2_ang)
    if not l1_ok:
        die("G-WEDGE LIMB 1 REFUSES level %s: max over %d faces of |angle/%g - 1| = %.6e exceeds "
            "TOL_REL_WEDGE = %.6e (occupancy %.4f). The builder refuses; it does not repair and it "
            "deletes nothing." % (level, 2 * nr * nx, half_angle_deg, l1, tol_rel, l1 / tol_rel), rc=2)
    if not l2_ok:
        die("G-WEDGE LIMB 2 REFUSES level %s: checkMesh printed %s, deviation %.6e deg exceeds "
            "TOL_CM = %.6e deg. Limb 2 is the BLUNT cross-check on the mesher; a limb-2 refusal with "
            "limb 1 at %.6e means the mesher, not the reader." % (level, l2_ang, l2, tol_cm, l1), rc=2)
    aspect_note = "advisory" if float(m_ar.group(1)) > EX.ASPECT_ADVISORY else "under_advisory"
    with open(os.path.join(dest, "MESH_LINE.txt"), "w") as f:
        f.write("level=%s nr=%d nx=%d cells=%d max_non_orthogonality_deg=%s max_skewness=%s "
                "max_aspect_ratio=%s aspect_%s=%g wedge_angles_deg=%s gate_non_ortho=%g gate_skew=%g "
                "GWEDGE_limb1_max_rel=%.9e limb1_tol=%.9e limb1_occupancy=%.6e "
                "GWEDGE_limb2_dev_deg=%.9e limb2_tol_deg=%.9e limb2_occupancy=%.6e "
                "half_angle_deg=%.12g endTime=%d writeInterval=%d source=log.checkMesh+constant/polyMesh\n"
                % (level, nr, nx, cells, m_no.group(1), m_sk.group(1), m_ar.group(1), aspect_note,
                   EX.ASPECT_ADVISORY, "/".join("%s:%.13g" % kv for kv in sorted(l2_ang.items())),
                   EX.MAX_NON_ORTHO, EX.MAX_SKEW, l1, tol_rel, l1 / tol_rel, l2, tol_cm, l2 / tol_cm,
                   half_angle_deg, end_time, write_interval))

    # --- 0/ : p, C, V, then U LAST OF ALL (the age guard's datum) -------------
    os.makedirs(os.path.join(dest, "0"))
    shutil.copy(os.path.join(CASE_SRC, "0", "p"), os.path.join(dest, "0", "p"))
    if foam("postProcess -func writeCellCentres -time 0", dest, os.path.join(dest, "log.writeCellCentres")) != 0:
        die("postProcess writeCellCentres failed")
    if foam("postProcess -func writeCellVolumes -time 0", dest, os.path.join(dest, "log.writeCellVolumes")) != 0:
        die("postProcess writeCellVolumes failed")
    C = FIO.read_field(os.path.join(dest, "0", "C"))
    if C["kind"] != "vector" or C["internal"] is None or len(C["internal"]) != cells:
        die("0/C does not carry %d cell centres" % cells)
    V = FIO.read_field(os.path.join(dest, "0", "V"))
    if V["kind"] != "scalar" or V["internal"] is None or len(V["internal"]) != cells:
        die("0/V does not carry %d cell volumes" % cells)
    if enforce_geometry:
        # the cell centres and volumes must be the MODEL's, because the band rests on it
        g = EX.wedge_geometry(nr, half_angle_deg)
        yc = C["internal"][:, 1]
        dx = EX.L / nx
        j = np.rint((yc / (EX.R * g["ca"])) * nr - 0.5).astype(int)
        j = np.clip(j, 0, nr - 1)
        if np.max(np.abs(yc - g["yc"][j])) > 1e-9 or np.max(np.abs(V["internal"] - g["vol"][j] * dx)) > 1e-9 * dx:
            die("mesh geometry disagrees with exact_f23b.wedge_geometry (centres or volumes); the "
                "model would not describe this mesh")
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "U.template"), os.path.join(dest, "0", "U"),
                            {"__INTERNALFIELD__": FIO.fmt_list(np.zeros((cells, 3)), "vector")})
    return dict(level=level, dest=dest, cells=cells, nr=nr, nx=nx, n_iter=end_time,
                write_interval=write_interval, half_angle_deg=half_angle_deg, solver=solver_note,
                limb1_max_rel=l1, limb1_tol=tol_rel, limb1_occupancy=l1 / tol_rel,
                limb2_dev_deg=l2, limb2_tol_deg=tol_cm, limb2_occupancy=l2 / tol_cm,
                checkmesh_angles=l2_ang, non_ortho=float(m_no.group(1)), skew=float(m_sk.group(1)),
                aspect=float(m_ar.group(1)))


# ---------------------------------------------------------------------------
# THE blockMesh-PATH CONTROL -- items A4-A7, GATING under AMENDMENT 1
# ---------------------------------------------------------------------------
def drive_gwedge_control(workdir, prereg_commit, levels=RECEIPT_LEVELS, receipt=RECEIPT):
    """Both directions, at coarse and at fine, through the REAL producer.

    The perturbation is written into `__HALF_ANGLE_DEG__` and flows through the
    builder's math.cos / math.sin into `__YW__` / `__ZW__` and then through
    blockMesh's own vertex arithmetic -- which may round, snap or renormalise
    where a direct z-scale does not.  That is why the points-level plant of
    section 4.4 is the WEAKER limb and may not substitute for this one.
    """
    if os.path.realpath(workdir).startswith(os.path.realpath(HERE)):
        refuse("the control workdir %s lies inside the tracked case tree" % workdir)
    rows = []
    for lvl in levels:
        nr, nx = dict((n, (a, b)) for n, a, b in EX.LEVELS)[lvl]
        tol = EX.TOL_REL_WEDGE[lvl]
        for direction, ang in (("MUST_ACCEPT", EX.HALF_ANGLE_DEG),
                               ("MUST_REFUSE", EX.HALF_ANGLE_DEG * (1.0 + EX.GWEDGE_PLANT_RATIO * tol))):
            dest = os.path.join(workdir, "%s_%s" % (lvl, direction))
            os.makedirs(dest, exist_ok=True)
            a = math.radians(ang)
            FIO.write_from_template(
                os.path.join(CASE_SRC, "system", "blockMeshDict.template"),
                os.path.join(dest, "blockMeshDict.staged"),
                {"__NX__": str(nx), "__NR__": str(nr), "__L__": repr(EX.L),
                 "__YW__": repr(EX.R * math.cos(a)), "__ZW__": repr(EX.R * math.sin(a)),
                 "__HALF_ANGLE_DEG__": repr(ang)})
            os.makedirs(os.path.join(dest, "system"), exist_ok=True)
            shutil.move(os.path.join(dest, "blockMeshDict.staged"),
                        os.path.join(dest, "system", "blockMeshDict"))
            for f in ("controlDict", "fvSchemes", "fvSolution", "decomposeParDict"):
                shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
            os.makedirs(os.path.join(dest, "constant"), exist_ok=True)
            for f in ("transportProperties", "turbulenceProperties", "fvOptions"):
                shutil.copy(os.path.join(CASE_SRC, "constant", f), os.path.join(dest, "constant", f))
            t0 = time.time()
            if foam("blockMesh", dest, os.path.join(dest, "log.blockMesh")) != 0:
                refuse("the control build at %s/%s failed in blockMesh; see %s/log.blockMesh"
                       % (lvl, direction, dest))
            if foam("checkMesh", dest, os.path.join(dest, "log.checkMesh")) != 0:
                refuse("the control build at %s/%s failed in checkMesh" % (lvl, direction))
            mesh_dir = os.path.join(dest, "constant", "polyMesh")
            # limb 1 is ALWAYS evaluated against the REGISTERED half angle, never
            # against the perturbed one -- a guard evaluated against the thing it
            # is testing is not a guard.
            l1, _d, ok = gwedge_limb1(mesh_dir, EX.HALF_ANGLE_DEG, tol)
            rows.append(dict(level=lvl, direction=direction, half_angle_written=ang,
                             plant_relative=(ang / EX.HALF_ANGLE_DEG - 1.0),
                             limb1_max_rel=l1, limb1_tol=tol, ratio_to_tol=l1 / tol,
                             refused=(not ok), accepted=ok,
                             log_blockMesh=os.path.join(dest, "log.blockMesh"),
                             log_checkMesh=os.path.join(dest, "log.checkMesh"),
                             checkmesh_angles=FIO.checkmesh_wedge_angles(
                                 os.path.join(dest, "log.checkMesh")),
                             wall_s=round(time.time() - t0, 3)))
            print("  %-6s %-12s half_angle_written=%.12g  limb1=%.6e  ratio=%.4f  -> %s  (%.1f s)"
                  % (lvl, direction, ang, l1, l1 / tol, "REFUSE" if not ok else "ACCEPT",
                     rows[-1]["wall_s"]))
    write_receipt(receipt, prereg_commit, rows)
    check_receipt(receipt, prereg_commit)      # the receipt must pass its OWN gate
    print("G-WEDGE BORN: receipt written and re-read through its own gate -> %s" % receipt)
    return rows


# ---------------------------------------------------------------------------
# THE POINTS-LEVEL CONTROL (section 4.4) -- the WEAKER limb, zero compute
# ---------------------------------------------------------------------------
def points_level_control(levels=("coarse", "fine"), f23_runs=F23_RUNS):
    """C-1 / C-2 / C-3 / C-4, driven through the REAL reader on REAL F23 meshes.

    Read-only on F23's run root; the plant is written to a COPY in a scratch
    directory and read back with the same reader.  This exercises the real READER
    but NOT the real PRODUCER, so it is explicitly the weaker of the two controls
    and may not substitute for the blockMesh-path control (AMENDMENT 1 A1.4).
    """
    rows, fails = [], []
    tmp = tempfile.mkdtemp(prefix="f23b_wedge_control_")
    try:
        for lvl in levels:
            src = os.path.join(f23_runs, lvl, "constant", "polyMesh")
            if not os.path.isdir(src):
                refuse("the points-level control's artifact is absent: %s. Section 9.4 registers "
                       "F23's run root as RETAINED because it is this control's evidence." % src)
            tol = EX.TOL_REL_WEDGE[lvl]
            for tag, p, want in (("unplanted_real", 0.0, "ACCEPT"),
                                 ("plant_3xTOL", EX.GWEDGE_PLANT_RATIO * tol, "REFUSE"),
                                 ("plant_0.10", 0.10, "REFUSE")):
                if p == 0.0:
                    mesh, rt = src, 0.0
                else:
                    mesh = os.path.join(tmp, "%s_%s" % (lvl, tag))
                    rt = FIO.plant_points_z_into_copy(src, mesh, p)
                    if rt > EX.GWEDGE_ROUNDTRIP_TOL:
                        fails.append("C-4 %s/%s: the plant's round trip through the file format is "
                                     "%.3e, above %.1e; a plant that cannot survive its own file "
                                     "format is not a plant" % (lvl, tag, rt, EX.GWEDGE_ROUNDTRIP_TOL))
                l1, _d, ok = gwedge_limb1(mesh, EX.HALF_ANGLE_DEG, tol)
                got = "ACCEPT" if ok else "REFUSE"
                rows.append(dict(level=lvl, construction=tag, plant_relative=p,
                                 roundtrip_max_dz=rt, limb1_max_rel=l1, ratio_to_tol=l1 / tol,
                                 required=want, got=got, artifact=mesh))
                if got != want:
                    fails.append("%s/%s: limb 1 read %.6e (%.4f x tol) and %s where the registration "
                                 "requires %s" % (lvl, tag, l1, l1 / tol, got, want))
                if tag == "plant_3xTOL" and not (EX.GWEDGE_PLANT_RATIO_BAND[0] <= l1 / tol
                                                 <= EX.GWEDGE_PLANT_RATIO_BAND[1]):
                    fails.append("%s/plant_3xTOL: ratio %.4f outside the registered [%.1f, %.1f]"
                                 % (lvl, l1 / tol, *EX.GWEDGE_PLANT_RATIO_BAND))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return rows, fails


def provenance_control(level="coarse", f23_runs=F23_RUNS):
    """The reader is reading the SAME GEOMETRY THE MESHER WROTE: the
    reimplementation of `wedgePolyPatch::calcGeometry` must reproduce the angle
    `checkMesh` PRINTED into that level's own log, to the digits the log carries.
    NEGATIVE LIMB: the fsum substitution -- the same points, the same faces,
    nothing else changed -- must move the reading, or the mechanism section 4.2
    measured is not what this reader is seeing."""
    mesh = os.path.join(f23_runs, level, "constant", "polyMesh")
    log = os.path.join(f23_runs, level, "log.checkMesh")
    printed = FIO.checkmesh_wedge_angles(log)
    rows = []
    for patch in ("wedge1", "wedge2"):
        r = FIO.checkmesh_cos_angle(mesh, patch)
        want = printed[patch]
        agree = abs(r["angle_deg"] - want) <= 5e-13
        rows.append(dict(patch=patch, reimplemented=r["angle_deg"], checkmesh_printed=want,
                         one_minus_mag_n_bar=r["one_minus_mag_n_bar"], agrees=agree))
    return rows


# ---------------------------------------------------------------------------
def selftest(deep=True):
    print("build_f23b.py --selftest  (ZERO SOLVER COMPUTE; blockMesh is NOT run)")
    t0 = time.time()
    fails = []
    prov = provenance_control("coarse")
    for r in prov:
        print("  PROVENANCE %-7s reimplemented %.14f vs checkMesh's printed %.13g -> %s"
              % (r["patch"], r["reimplemented"], r["checkmesh_printed"],
                 "agree" if r["agrees"] else "DISAGREE"))
        if not r["agrees"]:
            fails.append("provenance %s: the reader does not reproduce checkMesh's own printed angle"
                         % r["patch"])
    if prov and prov[0]["one_minus_mag_n_bar"] <= 0.0:
        fails.append("provenance: 1 - |n_bar| is not positive, so the section 4.2 mechanism is not "
                     "present in what this reader sees and the control is measuring nothing")
    lv = ("coarse", "fine") if deep else ("coarse",)
    rows, f2 = points_level_control(lv)
    fails += f2
    for r in rows:
        print("  POINTS-PLANT %-6s %-14s p=%.6e  roundtrip_max_dz=%.3e  limb1=%.6e  ratio=%.4f  "
              "required %s  got %s" % (r["level"], r["construction"], r["plant_relative"],
                                       r["roundtrip_max_dz"], r["limb1_max_rel"], r["ratio_to_tol"],
                                       r["required"], r["got"]))
    # the receipt gate, driven BOTH ways on a scratch receipt -- no build, no compute
    tmp = tempfile.mkdtemp(prefix="f23b_receipt_")
    try:
        good = []
        for lvl in RECEIPT_LEVELS:
            tol = EX.TOL_REL_WEDGE[lvl]
            good.append(dict(level=lvl, direction="MUST_ACCEPT", limb1_max_rel=1e-10, refused=False))
            good.append(dict(level=lvl, direction="MUST_REFUSE", limb1_max_rel=3.0 * tol, refused=True))
        rp = os.path.join(tmp, "R.txt")
        write_receipt(rp, "deadbeef", good)
        pos = _fires(check_receipt, rp, "deadbeef")[0] is False
        neg = []
        neg.append(("absent", _fires(check_receipt, os.path.join(tmp, "nope.txt"), "deadbeef")[0]))
        neg.append(("wrong sha", _fires(check_receipt, rp, "cafe1234")[0]))
        bad = [dict(r) for r in good]
        bad[1]["limb1_max_rel"] = 1.0e-12          # a plant that did not travel
        write_receipt(os.path.join(tmp, "B1.txt"), "deadbeef", bad)
        neg.append(("plant did not travel", _fires(check_receipt, os.path.join(tmp, "B1.txt"), "deadbeef")[0]))
        bad2 = [dict(r) for r in good]
        bad2[1]["refused"] = False                  # the control did not fire
        write_receipt(os.path.join(tmp, "B2.txt"), "deadbeef", bad2)
        neg.append(("control did not fire", _fires(check_receipt, os.path.join(tmp, "B2.txt"), "deadbeef")[0]))
        write_receipt(os.path.join(tmp, "B3.txt"), "deadbeef", good[:2])   # fine missing
        neg.append(("one level only", _fires(check_receipt, os.path.join(tmp, "B3.txt"), "deadbeef")[0]))
        bad4 = [dict(r) for r in good]
        bad4[0]["limb1_max_rel"] = 1.0e-6           # accept limb above the ceiling
        write_receipt(os.path.join(tmp, "B4.txt"), "deadbeef", bad4)
        neg.append(("refuses a correct mesh", _fires(check_receipt, os.path.join(tmp, "B4.txt"), "deadbeef")[0]))
        print("  RECEIPT GATE  positive limb (a well-formed receipt is accepted): %s" % ("ok" if pos else "FAIL"))
        for nm, fired in neg:
            print("  RECEIPT GATE  negative limb %-24s %s" % (nm, "FIRED" if fired else "DID NOT FIRE"))
        if not pos:
            fails.append("receipt gate: a well-formed receipt was refused")
        for nm, fired in neg:
            if not fired:
                fails.append("receipt gate negative limb %r DID NOT FIRE -- IT IS MEASURING NOTHING" % nm)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    wall = time.time() - t0
    if fails:
        print("SELFTEST FAILED after %.1f s:" % wall)
        for f in fails:
            print("  %s" % f)
        return 1
    print("SELFTEST GREEN in %.1f s -- the reader reproduces checkMesh's OWN printed wedge angle to "
          "the last digit it prints; limb 1 ACCEPTS the real unplanted mesh at coarse%s and REFUSES a "
          "planted mis-built wedge at 3x tolerance and at 10 %%, with the plant surviving its own file "
          "format; and the AMENDMENT 1 receipt gate accepts a well-formed receipt and FIRES on every "
          "one of %d malformations." % (wall, " and at FINE" if deep else "", 6))
    return 0


def _fires(fn, *a, **k):
    err, sys.stderr = sys.stderr, open(os.devnull, "w")
    try:
        fn(*a, **k)
        return False, None
    except SystemExit as e:
        return True, e.code
    finally:
        sys.stderr.close()
        sys.stderr = err


def main(argv):
    ap = argparse.ArgumentParser(description="F23b level builder and G-WEDGE guard")
    ap.add_argument("dest", nargs="?")
    ap.add_argument("--level")
    ap.add_argument("--scratch", nargs=2, type=int, metavar=("NR", "NX"))
    ap.add_argument("--n-iter", type=int, default=EX.N_ITER)
    ap.add_argument("--half-angle-deg", type=float, default=EX.HALF_ANGLE_DEG)
    ap.add_argument("--prereg-commit", default=None)
    ap.add_argument("--gwedge-control", action="store_true")
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--receipt", default=RECEIPT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--shallow", action="store_true",
                    help="selftest: drive the points-level control at coarse only")
    ap.add_argument("--a0-dictionary", action="store_true",
                    help="AMENDMENT 1 item A0 ONLY: build under F23's alpha_U = 0.7 dictionary")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest(deep=not a.shallow)

    if a.gwedge_control:
        if not a.workdir or not a.prereg_commit:
            die("--gwedge-control needs --workdir and --prereg-commit")
        drive_gwedge_control(a.workdir, a.prereg_commit, receipt=a.receipt)
        return 0

    if not a.dest:
        die("a destination directory is required")
    dest = os.path.abspath(a.dest)

    if a.level:
        lv = dict((nm, (nr, nx)) for nm, nr, nx in EX.LEVELS)
        if a.level not in lv:
            die("unknown level %r" % a.level)
        if not a.prereg_commit:
            die("--prereg-commit is required to build a LADDER LEVEL (rule 2, and AMENDMENT 1's "
                "receipt is checked against it)", rc=2)
        if a.a0_dictionary:
            die("--a0-dictionary is registered for the A0 CONTROL only (AMENDMENT 1 section A1.5); "
                "a ladder level runs under section 5.3's dictionary and nothing else", rc=2)
        check_receipt(a.receipt, a.prereg_commit)
        nr, nx = lv[a.level]
        r = build(dest, a.level, nr, nx, a.n_iter, EX.HALF_ANGLE_DEG,
                  EX.TOL_REL_WEDGE[a.level], EX.TOL_CM_DEG[a.level])
    elif a.scratch:
        nr, nx = a.scratch
        if (nr, nx) in [(x, y) for _n, x, y in EX.LEVELS]:
            die("--scratch may not build a registered ladder level")
        # a scratch level is not on the ladder, so it has no registered tolerance;
        # the coarse tolerance is used and SAID SO, and the geometry cross-check
        # is kept because the model must still describe the mesh.
        r = build(dest, "SCRATCH(not_a_ladder_level)", nr, nx, a.n_iter, a.half_angle_deg,
                  EX.TOL_REL_WEDGE["coarse"], EX.TOL_CM_DEG["coarse"],
                  enforce_geometry=(abs(a.half_angle_deg - EX.HALF_ANGLE_DEG) < 1e-15),
                  a0_dictionary=a.a0_dictionary)
    else:
        die("one of --level, --scratch, --gwedge-control or --selftest is required")

    print("solver dictionary: %s" % r["solver"])
    print("built %s at %s: %d cells, endTime %d, writeInterval %d, non-ortho %g, skew %g, "
          "aspect %g; G-WEDGE limb 1 %.6e (occupancy %.4f of %.6e), limb 2 %.6e deg (occupancy "
          "%.4f of %.6e deg); geometry == model; 0/U written LAST"
          % (r["level"], r["dest"], r["cells"], r["n_iter"], r["write_interval"], r["non_ortho"],
             r["skew"], r["aspect"], r["limb1_max_rel"], r["limb1_occupancy"], r["limb1_tol"],
             r["limb2_dev_deg"], r["limb2_occupancy"], r["limb2_tol_deg"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
