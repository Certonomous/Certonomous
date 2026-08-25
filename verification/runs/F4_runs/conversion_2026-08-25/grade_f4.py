#!/usr/bin/env python3
"""F4 CONVERSION GRADER -- frozen at the pre-registration commit.

Grades the two 2026-07-28 F4 gates (shock standoff vs Billig; windward Cp vs
modified Newtonian) against bands fixed BEFORE the re-run, per
``verification/campaign/F4_CONVERSION_PREREGISTRATION.md``.

WHAT THIS FILE DOES NOT DO, stated first so nobody has to infer it:
  * It does NOT read ``result.json``.  ``result.json`` is written by the runner
    and grading it would grade the runner's arithmetic, not the solver's output.
    Every number below is re-derived from the raw OpenFOAM sample files.
  * It does NOT import ``sdk/workflows/tmr_verification.py``.  Three
    implementations in this repository quote a NEGATIVE GCI (-10.714 %) on a
    divergent triple and that file is one of them.  Every GCI, observed order
    and Richardson value here comes from ``scripts/roache_triple.py`` and from
    nothing else.
  * It does NOT degrade.  Every guard REFUSES (exit 2).  A run that fails any
    completion clause is not graded on partial output.

REFUSAL, not degradation, is the contract (CLAUDE.md rule 4).

Exit codes:  0 = graded (whatever the verdicts say);  2 = REFUSED;  3 = usage.
"""
import sys
import os
import json
import math
import glob
import hashlib
import argparse
import tempfile
import shutil

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "verification", "runs", "F4_runs"))

import roache_triple as RT                                       # noqa: E402
from billig_theory import (billig_delta_over_R,                  # noqa: E402
                           cp_max_rayleigh_pitot,
                           modified_newtonian_cp_of_theta_c)

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS -- every one of these is fixed by the pre-registration and
# derived there.  None was chosen after seeing a re-run number.
# ---------------------------------------------------------------------------
GAMMA = 1.4
R_CYL = 1.0                     # make_cylinder_case.py:46
R_TOP_OVER_R = 1.7              # make_cylinder_case.py:48
THETA_MAX_DEG = 75.0            # make_cylinder_case.py:47
RADIAL_GRADING = 8.0            # make_cylinder_case.py:56
L_RADIAL = (R_TOP_OVER_R - 1.0) * R_CYL          # 0.7
N_SAMPLE_POINTS = 400           # run_cylinder_case.py write_sampledicts, nPoints
ENDTIME = 6.0                   # make_cylinder_case.py end_time_abs
N_SNAPSHOTS = 3                 # last three write times, averaged

MACHS = (6.0, 7.0, 8.0)
LEVELS = ("coarse", "medium", "fine")
CELLS = {"coarse": 1000, "medium": 4000, "fine": 16000}
RES = {"coarse": (50, 20), "medium": (100, 40), "fine": (200, 80)}
DIM = 2                         # 2-D cylinder; h ~ N**(-1/2)
FS = 1.25                       # Roache safety factor -- must equal RT.FS
FORM = "equal"                  # REFUSES an unequal ladder; never "auto"

REQUIRED_FIELDS = ("T", "U", "p", "rho")
STALL_WALL_S = 1200.0           # per-case runaway guard (prereg section 7)
CAP_CORE_MIN = 24.0             # HARD CAP for the nine solver runs (prereg 7)

PLANT_DIST_INDEX = 137          # an interior sample index, far from both ends
PLANT_DIST_INDEX_B = 300        # a SECOND interior index -- two plants, not one
PLANT_RHO_SPIKE = 5.0e+01       # large enough to dominate any physical gradient
PLANT_READBACK_TOL = 1.0e-12


class Refusal(Exception):
    pass


def refuse(msg):
    raise Refusal(msg)


# ---------------------------------------------------------------------------
# THE READ PATH.  The planted-zero controls plant into these files and replay
# EXACTLY these functions, so a value they return is a statement about the file
# on disk rather than about the reader (CLAUDE.md rule 3).
# ---------------------------------------------------------------------------
def read_xy(path):
    """Read one OpenFOAM ``setFormat raw`` line-sample file.

    COLUMN ORDER IS (distance, T, p, rho) AND IT IS NOT ASSUMED.  OpenFOAM
    names the file after the fields it wrote, in the order it wrote them --
    ``r0_T_p_rho.xy`` -- and this function REFUSES any file whose basename does
    not carry that exact field order.  This is the ``coefficient.dat`` trap
    (a positional read of a column-sorted writer) closed by construction.
    """
    if not os.path.isfile(path):
        refuse(f"no sample file at {path}")
    base = os.path.basename(path)
    if not base.endswith("_T_p_rho.xy"):
        refuse(f"{path}: basename does not declare the field order T_p_rho; "
               f"a positional read of this file would be unsafe")
    d = np.loadtxt(path)
    if d.ndim != 2 or d.shape[1] != 4:
        refuse(f"{path}: expected 4 columns (distance T p rho), got shape {d.shape}")
    if len(d) != N_SAMPLE_POINTS:
        refuse(f"{path}: expected {N_SAMPLE_POINTS} sample points, got {len(d)}")
    return d


def find_shock(path):
    """Peak |d(rho)/d(distance)| locus along a radial sample line.

    Returns (index, distance, rho_at_peak).  This is the frozen reader; the
    ENDPOINT GUARD is applied by the caller, not here, so that the control can
    plant at an endpoint and observe that the reader really does return it.
    """
    d = read_xy(path)
    dist, rho = d[:, 0], d[:, 3]
    grad = np.gradient(rho, dist)
    i = int(np.argmax(np.abs(grad)))
    return i, float(dist[i]), float(rho[i])


def snapshot_times(case_dir):
    """The last N_SNAPSHOTS write times that carry a line sample, ascending."""
    root = os.path.join(case_dir, "postProcessing", "sampleDict")
    if not os.path.isdir(root):
        refuse(f"{case_dir}: no postProcessing/sampleDict")
    times = []
    for name in os.listdir(root):
        try:
            times.append((float(name), name))
        except ValueError:
            continue
    times.sort()
    if len(times) < N_SNAPSHOTS:
        refuse(f"{case_dir}: only {len(times)} sampled times, need {N_SNAPSHOTS}")
    return [n for _, n in times[-N_SNAPSHOTS:]]


# ---------------------------------------------------------------------------
# GATE 0 -- ADMISSIBILITY.  Every clause REFUSES.
# ---------------------------------------------------------------------------
def check_completion(case_dir):
    """CLAUDE.md rule 4, with the ONE declared adaptation named in prereg 6.2.

    Clauses: rc == 0; an ``End`` line; the last logged ``Time =`` equals the
    latest written time directory; that time is >= endTime (the declared
    adaptation -- ``adjustTimeStep yes`` overshoots endTime by O(1e-5) and can
    never land on it exactly); the ``Time =`` count equals the
    ``ExecutionTime`` count; all four fields present at that time; and EVERY
    one of them NEWER than the case's own ``0/T`` (the age guard).
    """
    out = {}
    rc_path = os.path.join(case_dir, "RC.txt")
    if not os.path.isfile(rc_path):
        refuse(f"{case_dir}: no RC.txt -- the return code was never recorded, "
               f"and an inferred rc is not an rc")
    rc = open(rc_path).read().strip()
    if rc != "0":
        refuse(f"{case_dir}: rc = {rc!r}, not 0")
    out["rc"] = 0

    log = os.path.join(case_dir, "log.rhoCentralFoam")
    if not os.path.isfile(log):
        refuse(f"{case_dir}: no log.rhoCentralFoam")
    times, execs, end = [], 0, False
    with open(log, errors="replace") as fh:
        for line in fh:
            if line.startswith("Time = "):
                times.append(line.split()[2])
            elif line.startswith("ExecutionTime"):
                execs += 1
                out["last_exec_s"] = float(line.split()[2])
            elif line.strip() == "End":
                end = True
    if not end:
        refuse(f"{case_dir}: no End line")
    if not times:
        refuse(f"{case_dir}: no 'Time =' blocks")
    if len(times) != execs:
        refuse(f"{case_dir}: {len(times)} Time blocks but {execs} ExecutionTime "
               f"lines -- the log is truncated or interleaved")
    out["n_steps"] = len(times)
    out["last_time_logged"] = float(times[-1])

    tdirs = []
    for name in os.listdir(case_dir):
        if not os.path.isdir(os.path.join(case_dir, name)):
            continue
        try:
            tdirs.append((float(name), name))
        except ValueError:
            continue
    tdirs.sort()
    if not tdirs:
        refuse(f"{case_dir}: no time directories")
    latest_v, latest = tdirs[-1]
    out["latest_time_dir"] = latest
    if abs(latest_v - out["last_time_logged"]) > 1.0e-6:
        refuse(f"{case_dir}: last logged Time {out['last_time_logged']} != "
               f"latest written time dir {latest_v}")
    if latest_v < ENDTIME:
        refuse(f"{case_dir}: latest time {latest_v} < endTime {ENDTIME} -- "
               f"the run did not reach the registered end")
    if latest_v > ENDTIME * 1.001:
        refuse(f"{case_dir}: latest time {latest_v} overshoots endTime "
               f"{ENDTIME} by more than the declared 0.1 % adjustTimeStep "
               f"allowance -- this is a runaway, not a rounding overshoot")

    zero_T = os.path.join(case_dir, "0", "T")
    if not os.path.isfile(zero_T):
        refuse(f"{case_dir}: no 0/T -- the age guard has no reference")
    t0 = os.path.getmtime(zero_T)
    ages = {}
    for f in REQUIRED_FIELDS:
        p = os.path.join(case_dir, latest, f)
        if not os.path.isfile(p):
            refuse(f"{case_dir}: field {f} missing at {latest}")
        age = os.path.getmtime(p) - t0
        ages[f] = age
        if age <= 0:
            refuse(f"{case_dir}: AGE GUARD -- {latest}/{f} is not newer than "
                   f"0/T (delta {age:.3f} s).  This field predates the run "
                   f"that was allowed to produce it.")
    out["field_ages_s"] = ages
    out["core_min"] = out.get("last_exec_s", 0.0) / 60.0
    if out.get("last_exec_s", 0.0) > STALL_WALL_S:
        refuse(f"{case_dir}: ExecutionTime {out['last_exec_s']:.1f} s exceeds "
               f"the registered per-case runaway guard {STALL_WALL_S:.0f} s")
    return out


def check_no_preexisting(case_dir):
    """Rule 4's launch-side guard: refuse a case where 0/ or a time dir already
    exists.  Called by the LAUNCHER before a case is built; exposed here so the
    selftest can exercise it and so the grader can state it was available."""
    if os.path.isdir(os.path.join(case_dir, "0")):
        refuse(f"{case_dir}: 0/ already exists -- refusing to overwrite")
    for name in os.listdir(case_dir) if os.path.isdir(case_dir) else []:
        if name in ("0",):
            continue
        try:
            float(name)
        except ValueError:
            continue
        refuse(f"{case_dir}: time directory {name} already exists -- refusing")
    return True


# ---------------------------------------------------------------------------
# GATE S -- LADDER SIMILARITY, MEASURED FROM THE WRITTEN blockMeshDicts.
# MESH_STANDARD 9.2: "the requested value is the thing that lied."  Nothing
# here reads RES; everything reads the dict the mesher was actually handed.
# ---------------------------------------------------------------------------
def read_written_mesh(case_dir):
    """Parse the ``hex ... (nTheta nR 1) simpleGrading (1 G 1)`` line out of the
    blockMeshDict that was actually written into the case."""
    path = os.path.join(case_dir, "system", "blockMeshDict")
    if not os.path.isfile(path):
        refuse(f"{case_dir}: no system/blockMeshDict to measure similarity from")
    hexline = None
    for line in open(path, errors="replace"):
        if line.lstrip().startswith("hex "):
            if hexline is not None:
                refuse(f"{path}: more than one hex block; the similarity "
                       f"measurement assumes the single polar O-grid block")
            hexline = line.strip()
    if hexline is None:
        refuse(f"{path}: no hex line")
    nums = hexline.replace("(", " ").replace(")", " ").split()
    try:
        k = nums.index("simpleGrading")
    except ValueError:
        refuse(f"{path}: hex line carries no simpleGrading: {hexline!r}")
    counts = [int(x) for x in nums[k - 3:k]]
    grading = [float(x) for x in nums[k + 1:k + 4]]
    n_theta, n_r, n_z = counts
    if n_z != 1:
        refuse(f"{path}: n_z = {n_z}, not 1 -- this is not the 2-D ladder")
    return dict(path=path, n_theta=n_theta, n_r=n_r,
                cells=n_theta * n_r, grading=grading, hexline=hexline)


def first_cell_height(n_r, L=L_RADIAL, E=RADIAL_GRADING):
    """First (wall-adjacent) radial cell of a simpleGrading block, closed form."""
    k = E ** (1.0 / (n_r - 1))
    return L * (k - 1.0) / (k ** n_r - 1.0)


def cell_at_distance(n_r, d, L=L_RADIAL, E=RADIAL_GRADING):
    """Radial cell height at radial distance ``d`` from the wall."""
    k = E ** (1.0 / (n_r - 1))
    h1 = L * (k - 1.0) / (k ** n_r - 1.0)
    edge = 0.0
    for i in range(n_r):
        h = h1 * k ** i
        edge += h
        if edge >= d:
            return h
    refuse(f"distance {d} lies outside the radial span {L}")


def measure_similarity(case_dirs, tol_ratio=1.0e-9, tol_h1=0.05):
    """case_dirs: {level: path}.  REFUSES unless the WRITTEN dicts form the
    registered ladder."""
    meshes = {lv: read_written_mesh(case_dirs[lv]) for lv in LEVELS}
    for lv in LEVELS:
        if meshes[lv]["cells"] != CELLS[lv]:
            refuse(f"{lv}: written mesh has {meshes[lv]['cells']} cells, "
                   f"registered {CELLS[lv]}")
        if (meshes[lv]["n_theta"], meshes[lv]["n_r"]) != RES[lv]:
            refuse(f"{lv}: written (nTheta,nR) = "
                   f"({meshes[lv]['n_theta']},{meshes[lv]['n_r']}), "
                   f"registered {RES[lv]}")
        if abs(meshes[lv]["grading"][1] - RADIAL_GRADING) > 1e-12:
            refuse(f"{lv}: written radial grading {meshes[lv]['grading'][1]} "
                   f"!= registered {RADIAL_GRADING}")
    r21 = RT.refinement_ratio(meshes["medium"]["cells"], meshes["fine"]["cells"], DIM)
    r32 = RT.refinement_ratio(meshes["coarse"]["cells"], meshes["medium"]["cells"], DIM)
    if abs(r21 - r32) > tol_ratio:
        refuse(f"written ladder is UNEQUAL: r21 = {r21!r}, r32 = {r32!r}")
    h1 = {lv: first_cell_height(meshes[lv]["n_r"]) for lv in LEVELS}
    ratios = (h1["coarse"] / h1["medium"], h1["medium"] / h1["fine"])
    for r in ratios:
        if abs(r - 2.0) / 2.0 > tol_h1:
            refuse(f"near-wall spacing is NOT similar: h1 ratio {r:.6f} "
                   f"departs from 2 by more than {100*tol_h1:.0f} %.  The "
                   f"cell COUNTS refine by 2 but the WALL SPACING does not, so "
                   f"this is not one ladder.")
    return dict(meshes={lv: meshes[lv] for lv in LEVELS}, r21=r21, r32=r32,
                h1=h1, h1_ratios=ratios)


# ---------------------------------------------------------------------------
# THE TWO MEASURED QUANTITIES
# ---------------------------------------------------------------------------
def standoff(case_dir):
    """Gate-1 quantity: mean detected standoff at theta = 0 over the last three
    write times, with the ENDPOINT-CENSORING GUARD applied to every snapshot.

    THE GUARD IS THE POINT.  ``find_shock`` returns ``argmax`` over a fixed
    400-point line, so its output is CONFINED to [0, 0.7] whatever the flow
    does.  F4_hypersonic_blunt_body.md section 3 records this detector actually
    pinning at 0.70 (the domain edge, index 399) at theta ~ 60 deg at EVERY
    resolution.  A value at either endpoint is the instrument's range limit,
    not a measurement, and grading one would be grading a censored quantity.
    """
    snaps, per = [], []
    for st in snapshot_times(case_dir):
        p = os.path.join(case_dir, "postProcessing", "sampleDict", st,
                         "r0_T_p_rho.xy")
        i, dist, rho = find_shock(p)
        if i == 0 or i == N_SAMPLE_POINTS - 1:
            refuse(f"{case_dir} @ {st}: CENSORED READ -- the peak-gradient "
                   f"locus is at sample index {i}, an ENDPOINT of the sample "
                   f"line.  The detector has pinned at its range limit "
                   f"(distance {dist}); this is not a standoff measurement.")
        snaps.append(dist)
        per.append(dict(time=st, index=i, standoff=dist, rho_at_peak=rho))
    a = np.array(snaps)
    return dict(mean=float(a.mean()), std=float(a.std()), snapshots=per)


def cp_rms(case_dir, M):
    """Gate-2 quantity: RMS(Cp_cfd - Cp_modified_newtonian) over the sampled
    windward face, as a percentage of Cp_max.  Averaged over the same three
    snapshots.  Reads ``p_cylSurface.raw`` BY EXACT NAME -- not by a glob, which
    would silently pick a different field if the writer's naming changed."""
    q1 = 0.5 * GAMMA * 1.0 * M * M            # p_inf = 1 in this non-dim gas
    cpmax = float(cp_max_rayleigh_pitot(M))
    per_snap, theta = [], None
    for st in snapshot_times(case_dir):
        p = os.path.join(case_dir, "postProcessing", "surfaceSampleDict", st,
                         "p_cylSurface.raw")
        if not os.path.isfile(p):
            refuse(f"{case_dir} @ {st}: no p_cylSurface.raw")
        arr = np.loadtxt(p, comments="#")
        if arr.ndim != 2 or arr.shape[1] != 4:
            refuse(f"{p}: expected 4 columns (x y z p), got {arr.shape}")
        x, y, pw = arr[:, 0], arr[:, 1], arr[:, 3]
        th = np.degrees(np.arctan2(y, -x))
        o = np.argsort(th)
        th, pw = th[o], pw[o]
        if theta is None:
            theta = th
        elif not np.allclose(theta, th):
            refuse(f"{case_dir} @ {st}: the sampled wall stations moved "
                   f"between snapshots; they cannot be averaged")
        per_snap.append((pw - 1.0) / q1)
    cp = np.array(per_snap).mean(axis=0)
    newton = np.array([modified_newtonian_cp_of_theta_c(math.radians(t), M)
                       for t in theta])
    rms = float(np.sqrt(np.mean((cp - newton) ** 2)))
    return dict(rms=rms, cp_max=cpmax, rms_pct_of_cpmax=100.0 * rms / cpmax,
                n_stations=int(len(theta)))


# ---------------------------------------------------------------------------
# THE BANDS.  Derived, never fitted.  See prereg section 5 for the derivation;
# the arithmetic is repeated here so the number is produced, not transcribed.
# ---------------------------------------------------------------------------
def standoff_band_pct(M, level):
    """+/- one LOCAL RADIAL CELL at the shock, as a percentage of the Billig
    standoff.  Rationale (prereg 5.1): the sample line is interpolated
    ``cellPoint`` from cells of local radial height dr, so two shock positions
    closer together than dr produce the SAME detected locus.  A deviation
    smaller than dr/delta is therefore below the instrument's resolution and is
    not a resolved disagreement.  Purely geometric -- no CFD value enters."""
    d = float(billig_delta_over_R(M))
    dr = cell_at_distance(RES[level][1], d)
    return 100.0 * dr / d


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (CLAUDE.md rule 3).  Three of them, and the grader
# REFUSES if any fails.  A zero -- or any number -- from a reader not shown able
# to see a plant is not evidence.
# ---------------------------------------------------------------------------
def _plant_spike(src, dst, index, spike=PLANT_RHO_SPIKE):
    """Copy an .xy file and add ``spike`` to rho at ONE sample index, then read
    the file back FROM DISK and prove the perturbation landed."""
    if os.path.abspath(src) == os.path.abspath(dst):
        refuse("plant destination must differ from the donor; planting in "
               "place would destroy the unperturbed reference")
    d = np.loadtxt(src)
    d[index, 3] += spike
    with open(dst, "w") as fh:
        for row in d:
            fh.write("\t".join(f"{v:.10g}" for v in row) + "\n")
    back = np.loadtxt(dst)
    got = back[index, 3] - np.loadtxt(src)[index, 3]
    if abs(got - spike) > PLANT_READBACK_TOL * max(1.0, abs(spike)):
        refuse(f"PLANT DID NOT LAND: wrote {spike} at index {index}, read back "
               f"{got}")
    return dst


def control_p1(donor_xy, tmp):
    """P1 -- CAN THE READER SEE A PLANT AT ALL?  Plant a dominating rho spike at
    a known interior index and require ``find_shock`` to return THAT index.
    Two plant locations, not one, so a reader that happens to peak near the
    first cannot pass by luck."""
    results = {}
    for tag, idx in (("A", PLANT_DIST_INDEX), ("B", PLANT_DIST_INDEX_B)):
        sub = os.path.join(tmp, f"p1_{tag}")
        os.makedirs(sub, exist_ok=True)
        dst = os.path.join(sub, "r0_T_p_rho.xy")
        _plant_spike(donor_xy, dst, idx)
        i, dist, _ = find_shock(dst)
        # a single-point spike makes |grad| peak at the two flanking points;
        # the located index must be within one sample of the plant.
        if abs(i - idx) > 1:
            refuse(f"P1{tag} FAILED: planted a rho spike at index {idx}; the "
                   f"reader located the peak gradient at index {i}.  THE "
                   f"READER CANNOT SEE A PLANT AND ITS OUTPUT IS NOT EVIDENCE.")
        results[tag] = dict(planted_index=idx, located_index=i, distance=dist)
        shutil.rmtree(sub, ignore_errors=True)
    return results


def control_p2(case_dir, tmp):
    """P2 -- THE NEGATIVE CONTROL.  Plant into a station the theta = 0 gate does
    NOT select (r3, i.e. theta ~ 36 deg) and require the gate value to be
    BIT-IDENTICAL.  A selector that moves when a file it does not read is
    perturbed is reading something it did not declare."""
    before = standoff(case_dir)["mean"]
    st = snapshot_times(case_dir)[-1]
    victim = os.path.join(case_dir, "postProcessing", "sampleDict", st,
                          "r3_T_p_rho.xy")
    if not os.path.isfile(victim):
        refuse(f"P2 cannot run: no r3_T_p_rho.xy at {st} to plant into")
    backup = os.path.join(tmp, "r3_backup.xy")
    shutil.copy(victim, backup)
    try:
        _plant_spike(backup, victim, PLANT_DIST_INDEX)
        after = standoff(case_dir)["mean"]
    finally:
        shutil.copy(backup, victim)
    if after != before:
        refuse(f"P2 FAILED: planting into the theta ~ 36 deg station moved the "
               f"theta = 0 gate value from {before!r} to {after!r}.  The gate "
               f"selector reads files it does not declare.")
    restored = standoff(case_dir)["mean"]
    if restored != before:
        refuse(f"P2 FAILED TO RESTORE: {restored!r} != {before!r}")
    return dict(before=before, after=after, restored=restored,
                victim=os.path.relpath(victim, case_dir))


def control_p3(case_dirs, tmp):
    """P3 -- THE SIMILARITY CONTROL.  Perturb ONE level's WRITTEN blockMeshDict
    cell count and require ``measure_similarity`` to STOP calling the ladder
    similar.  Without this, a similarity check that always says yes is
    indistinguishable from no check at all."""
    ok = measure_similarity(case_dirs)
    staged = {}
    for lv in LEVELS:
        staged[lv] = os.path.join(tmp, f"case_{lv}")
        os.makedirs(os.path.join(staged[lv], "system"), exist_ok=True)
        shutil.copy(os.path.join(case_dirs[lv], "system", "blockMeshDict"),
                    os.path.join(staged[lv], "system", "blockMeshDict"))
    p = os.path.join(staged["medium"], "system", "blockMeshDict")
    txt = open(p).read().replace("(100 40 1)", "(100 41 1)")
    open(p, "w").write(txt)
    try:
        measure_similarity(staged)
    except Refusal as exc:
        return dict(clean_r21=ok["r21"], clean_r32=ok["r32"],
                    perturbed_refusal=str(exc)[:200])
    refuse("P3 FAILED: the similarity check accepted a ladder whose medium "
           "level was perturbed from 100x40 to 100x41.  IT IS NOT MEASURING "
           "SIMILARITY.")


# ---------------------------------------------------------------------------
# GRADING
# ---------------------------------------------------------------------------
def grade_triple(values, quantity, M):
    """Rule 5, in the registered order.  The gate can only turn a PASS or a
    GATE FAIL INTO a NOT A RESULT, never the reverse."""
    tr = RT.triple_from_cells(values["coarse"], values["medium"], values["fine"],
                              CELLS["coarse"], CELLS["medium"], CELLS["fine"],
                              dim=DIM, fs=FS, form=FORM)
    out = dict(quantity=quantity, M=M, state=tr["state"],
               values={lv: values[lv] for lv in LEVELS},
               cells=[CELLS[lv] for lv in LEVELS],
               r21=tr.get("r21"), r32=tr.get("r32"),
               ratio_gap=tr.get("ratio_gap"), order=tr.get("order"),
               monotone=RT.monotone(tr))
    if tr["state"] == "CONVERGING" and out["monotone"]:
        out["GCI_pct"] = tr.get("GCI_pct")
        out["richardson"] = tr.get("richardson")
        out["triple_verdict"] = "CONVERGING"
    else:
        out["GCI_pct"] = None          # never quote a GCI off a non-monotone triple
        out["richardson"] = None
        out["triple_verdict"] = "NOT A RESULT"
        out["why"] = (f"triple state {tr['state']}, monotone={out['monotone']} "
                      f"-- standing rule 5 clause 2")
    return out


def grade_all(root):
    """root: the run root holding cyl/M<M>/<level>/ .

    HARD GUARD, FIRST.  Control P2 plants into a case directory and restores it.
    Pointed at the 2026-07-28 production tree
    (``verification/runs/F4_runs/cyl/``) it would touch the mtimes of a GRADED
    artifact and could break that tree's own age guard.  The grader therefore
    REFUSES any root not under a ``conversion_*`` directory.  A grader that can
    be aimed at the record it exists to re-grade is a hazard, not an instrument.
    """
    ap = os.path.abspath(root)
    if not any(part.startswith("conversion_") for part in ap.split(os.sep)):
        refuse(f"root {ap} is not under a conversion_* directory.  This grader "
               f"MUTATES case files during control P2 and must never be aimed "
               f"at the 2026-07-28 production tree.")
    report = dict(root=root, gates=[], cases={}, controls={}, cost={})
    case_path = {}
    for M in MACHS:
        for lv in LEVELS:
            case_path[(M, lv)] = os.path.join(root, "cyl", f"M{M}", lv)

    total_core_min = 0.0
    for key, cd in case_path.items():
        comp = check_completion(cd)
        report["cases"][f"M{key[0]}/{key[1]}"] = comp
        total_core_min += comp["core_min"]
    report["cost"]["solver_core_min"] = total_core_min
    report["cost"]["cap_core_min"] = CAP_CORE_MIN
    report["cost"]["cap_crossed"] = total_core_min > CAP_CORE_MIN

    # controls FIRST: nothing is graded by a reader not shown able to see
    tmp = tempfile.mkdtemp(prefix="f4grade_")
    try:
        donor = os.path.join(case_path[(6.0, "fine")], "postProcessing",
                             "sampleDict", snapshot_times(case_path[(6.0, "fine")])[-1],
                             "r0_T_p_rho.xy")
        report["controls"]["P1"] = control_p1(donor, tmp)
        report["controls"]["P2"] = control_p2(case_path[(6.0, "fine")], tmp)
        report["controls"]["P3"] = control_p3(
            {lv: case_path[(6.0, lv)] for lv in LEVELS}, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for M in MACHS:
        sim = measure_similarity({lv: case_path[(M, lv)] for lv in LEVELS})
        report.setdefault("similarity", {})[f"M{M}"] = dict(
            r21=sim["r21"], r32=sim["r32"], h1_ratios=sim["h1_ratios"])

        so = {lv: standoff(case_path[(M, lv)]) for lv in LEVELS}
        cp = {lv: cp_rms(case_path[(M, lv)], M) for lv in LEVELS}

        # --- G-F4-1: Roache triple on standoff
        t1 = grade_triple({lv: so[lv]["mean"] for lv in LEVELS},
                          "standoff delta/R", M)
        report["gates"].append(dict(gate=f"G-F4-1-M{M}", **t1))

        # --- G-F4-2: standoff deviation vs Billig at fine, band = one local cell
        d_ref = float(billig_delta_over_R(M))
        dev = 100.0 * (so["fine"]["mean"] - d_ref) / d_ref
        band = standoff_band_pct(M, "fine")
        g2 = dict(gate=f"G-F4-2-M{M}", quantity="standoff dev vs Billig (fine)",
                  reference=d_ref, measured=so["fine"]["mean"],
                  deviation_pct=dev, band_pct=band,
                  snapshot_std=so["fine"]["std"])
        if t1["triple_verdict"] != "CONVERGING":
            g2["verdict"] = "NOT A RESULT"
            g2["why"] = (f"G-F4-1-M{M} is NOT A RESULT; rule 5 forbids a band "
                         f"verdict on a non-converging triple")
        else:
            g2["verdict"] = "PASS" if abs(dev) <= band else "GATE FAIL"
        report["gates"].append(g2)

        # --- G-F4-3: Roache triple on Cp RMS
        t3 = grade_triple({lv: cp[lv]["rms_pct_of_cpmax"] for lv in LEVELS},
                          "RMS(Cp - Cp_Newton) as % of Cp_max", M)
        t3["cp_max"] = cp["fine"]["cp_max"]
        report["gates"].append(dict(gate=f"G-F4-3-M{M}", **t3))
    return report


# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", help="run root holding cyl/M<M>/<level>/")
    ap.add_argument("--out", help="write the JSON report here")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.root:
        print("usage: grade_f4.py --root <run root> [--out report.json]",
              file=sys.stderr)
        return 3
    try:
        rep = grade_all(a.root)
    except (Refusal, RT.Refusal) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    txt = json.dumps(rep, indent=2, default=str)
    if a.out:
        open(a.out, "w").write(txt)
    print(txt)
    return 0


# ---------------------------------------------------------------------------
# SELFTEST -- VALUE-CHECKING, and every control has a MUTATION that must make it
# fail.  A control that has never been seen to fail is not a control.
# ---------------------------------------------------------------------------
def selftest():
    fails = []

    def ck(name, cond, detail=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    print("F4 conversion grader selftest")
    print("-- frozen constants against their source lines")
    ck("FS matches roache_triple", FS == RT.FS, f"{FS} == {RT.FS}")
    ck("form is 'equal', never 'auto'", FORM == "equal")
    ck("L_radial", abs(L_RADIAL - 0.7) < 1e-15, f"{L_RADIAL}")

    print("-- Billig reference values, full double precision")
    exp = {6.0: 0.4394656652111482, 7.0: 0.4245982772504153,
           8.0: 0.4152190114522218}
    for M, v in exp.items():
        got = float(billig_delta_over_R(M))
        ck(f"Billig M={M}", abs(got - v) < 1e-15, f"{got!r}")

    print("-- the registered bands, recomputed")
    expb = {6.0: 3.1747, 7.0: 3.2005, 8.0: 3.2728}
    for M, v in expb.items():
        got = standoff_band_pct(M, "fine")
        ck(f"band M={M} fine", abs(got - v) < 5e-4, f"{got:.6f} %")
    ck("band tightens with refinement",
       standoff_band_pct(6.0, "coarse") > standoff_band_pct(6.0, "medium")
       > standoff_band_pct(6.0, "fine"),
       f"{standoff_band_pct(6.0,'coarse'):.4f} > "
       f"{standoff_band_pct(6.0,'medium'):.4f} > "
       f"{standoff_band_pct(6.0,'fine'):.4f}")

    print("-- the ladder is equal-ratio and form='equal' accepts it")
    r21 = RT.refinement_ratio(CELLS["medium"], CELLS["fine"], DIM)
    r32 = RT.refinement_ratio(CELLS["coarse"], CELLS["medium"], DIM)
    ck("r21 == r32 == 2", r21 == 2.0 and r32 == 2.0, f"{r21}, {r32}")

    print("-- GATE NON-DEGENERACY: each gate can PASS and can FAIL")
    t_pass = grade_triple({"coarse": 1.10, "medium": 1.04, "fine": 1.01},
                          "synthetic", 6.0)
    ck("a monotone triple grades CONVERGING",
       t_pass["triple_verdict"] == "CONVERGING", f"order {t_pass['order']:.3f}")
    t_fail = grade_triple({"coarse": 1.00, "medium": 1.10, "fine": 1.02},
                          "synthetic", 6.0)
    ck("a non-monotone triple grades NOT A RESULT",
       t_fail["triple_verdict"] == "NOT A RESULT", t_fail["state"])
    ck("no GCI is quoted off the non-monotone triple",
       t_fail["GCI_pct"] is None)
    d6 = float(billig_delta_over_R(6.0))
    b6 = standoff_band_pct(6.0, "fine")
    inside = d6 * (1 + 0.5 * b6 / 100.0)
    outside = d6 * (1 + 2.0 * b6 / 100.0)
    ck("a standoff inside the band is representable on the sample line",
       0.0 < inside < L_RADIAL, f"{inside:.6f} in (0, {L_RADIAL})")
    ck("a standoff outside the band is ALSO representable (the gate is not "
       "censored into passing)", 0.0 < outside < L_RADIAL,
       f"{outside:.6f} in (0, {L_RADIAL})")

    print("-- READER + CONTROLS on synthetic on-disk files")
    tmp = tempfile.mkdtemp(prefix="f4selftest_")
    try:
        src = os.path.join(tmp, "r0_T_p_rho.xy")
        dist = np.linspace(0.0, L_RADIAL, N_SAMPLE_POINTS)
        rho = 1.0 + 5.0 * (dist > 0.44)          # a clean step at 0.44
        arr = np.column_stack([dist, np.ones_like(dist), np.ones_like(dist), rho])
        np.savetxt(src, arr, delimiter="\t")
        i, d, _ = find_shock(src)
        ck("reader finds a synthetic step", abs(d - 0.44) < 2 * L_RADIAL / 399,
           f"index {i}, distance {d:.6f}")

        p1 = control_p1(src, tmp)
        ck("P1 sees a plant at index 137",
           abs(p1["A"]["located_index"] - PLANT_DIST_INDEX) <= 1, str(p1["A"]))
        ck("P1 sees a plant at index 300",
           abs(p1["B"]["located_index"] - PLANT_DIST_INDEX_B) <= 1, str(p1["B"]))

        # MUTATION: a reader that ignores the file must FAIL P1
        real = globals()["find_shock"]
        try:
            globals()["find_shock"] = lambda p: (7, 0.0123, 1.0)
            try:
                control_p1(src, tmp)
                ck("P1 FAILS a blind reader (mutation)", False,
                   "the control accepted a reader that ignores the file")
            except Refusal:
                ck("P1 FAILS a blind reader (mutation)", True)
        finally:
            globals()["find_shock"] = real

        # the endpoint guard: a plant at index 399 must be REFUSED by standoff()
        endp = os.path.join(tmp, "endpoint_T_p_rho.xy")
        arr2 = arr.copy()
        arr2[N_SAMPLE_POINTS - 1, 3] += PLANT_RHO_SPIKE
        np.savetxt(endp, arr2, delimiter="\t")
        ie, de, _ = find_shock(endp)
        ck("the reader really does return the endpoint when the peak is there",
           ie >= N_SAMPLE_POINTS - 2, f"index {ie}")

        # the filename guard
        bad = os.path.join(tmp, "r0_p_rho_T.xy")
        shutil.copy(src, bad)
        try:
            read_xy(bad)
            ck("read_xy refuses a file whose name declares a different column "
               "order", False)
        except Refusal:
            ck("read_xy refuses a file whose name declares a different column "
               "order", True)

        # similarity + P3, on synthetic written dicts
        cds = {}
        for lv in LEVELS:
            cds[lv] = os.path.join(tmp, f"sim_{lv}")
            os.makedirs(os.path.join(cds[lv], "system"), exist_ok=True)
            nt, nr = RES[lv]
            open(os.path.join(cds[lv], "system", "blockMeshDict"), "w").write(
                f"blocks\n(\n    hex (0 1 2 3 4 5 6 7) ({nt} {nr} 1) "
                f"simpleGrading (1 {RADIAL_GRADING} 1)\n);\n")
        sim = measure_similarity(cds)
        ck("similarity accepts the registered ladder",
           sim["r21"] == 2.0 and sim["r32"] == 2.0,
           f"h1 ratios {sim['h1_ratios'][0]:.6f}, {sim['h1_ratios'][1]:.6f}")
        p3 = control_p3(cds, tmp)
        ck("P3 refuses a perturbed ladder (100x40 -> 100x41)",
           "perturbed_refusal" in p3, p3.get("perturbed_refusal", "")[:70])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("-- the production-tree guard")
    try:
        grade_all(os.path.join(REPO, "verification", "runs", "F4_runs"))
        ck("grade_all refuses the 2026-07-28 production tree", False,
           "IT DID NOT REFUSE")
    except Refusal as exc:
        ck("grade_all refuses the 2026-07-28 production tree",
           "conversion_" in str(exc), str(exc)[:80])
    except Exception as exc:                                   # noqa: BLE001
        ck("grade_all refuses the 2026-07-28 production tree", False,
           f"raised {type(exc).__name__} instead of Refusal: {exc}")

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s): {fails}")
        return 1
    print("SELFTEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
