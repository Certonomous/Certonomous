#!/usr/bin/env python3
"""Grader for MRF_R1 -- Rushton-turbine power number Np via whole-tank MRF.

STATUS: DRAFT / UNFROZEN.  No compute has run; this grader is written before the
graded triple exists, so it can be diff-read (the cfd-supervisor's check-1) and
plant-driven before a single core-minute is spent.  The pre-registration it
serves is  verification/campaign/MRF_R1_PREREGISTRATION.md .

WHAT IT GRADES.  The power number of a 6-blade Rushton disc turbine in a
fully-baffled stirred tank, computed from the STEADY MRF impeller torque:

    P  = omega * Q = 2*pi*N * Q            (power drawn by the impeller)
    Np = P / (rho * N**3 * D**5) = 2*pi*Q / (rho * N**2 * D**5)

rho, N (rev/s) and D (m) are fixed inputs; Q is the impeller torque about the
shaft axis, read from the forces function object's moment.dat.  Np is graded
against the pre-registered band by the SHARED Roache instrument.

WHAT THIS FILE DOES NOT REINVENT.  Roache rule-5 gating (a non-CONVERGING triple
is NOT A RESULT whatever the value), the one-way gate, the GCI at Fs = 1.25, the
fixed verdict vocabulary and refuse-not-degrade all come from the already-
selftested shared instrument  scripts/roache_triple.py  -- this file IMPORTS it
and grades through  grade_ladder .  What this file adds is the MRF-specific read
path (rule-4 completion + torque -> Np) and a LIVE planted-zero control on THAT
read path (rule 3).

THE FIVE REFUSALS (each a CLAUDE.md rule):
  * rule 4 -- a level that is not DONE (rc, End, last==endTime, fields, age
    guard) is refused, never graded on a partial run.
  * rule 3 -- no clean Np is emitted until a PLANT injected into the actual
    moment.dat read path is read back; a blind reader refuses (exit 2).
  * rule 5 -- inherited from roache_triple: non-CONVERGING triple -> NOT A
    RESULT; no GCI on a non-monotone triple.
  * refuse-not-degrade -- every missing/malformed input exits 2 with the reason.
  * fixed vocabulary -- PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
    BLOCKED / PENDING, and nothing else.

Exit codes (match roache_triple): 0 = PASS, 1 = GATE FAIL, 2 = REFUSE,
3 = NOT A RESULT.  A guard that could be stripped is not a guard: main refuses
to run under `python3 -O` (L-332), exactly as the shared instrument does.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

# --- import the shared, selftested Roache instrument by path ----------------
_HERE = os.path.dirname(os.path.abspath(__file__))          # cases/navier_class/MRF
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))  # repo root
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import roache_triple as rt  # noqa: E402

# incompressible-RAS field set for THIS case (see prereg section 5; the rule-4
# canonical T U p_rgh alphat nut k omega phi list is the THERMAL family's; this
# case is isothermal incompressible, so its analogous complete set is:)
REQUIRED_FIELDS = ("U", "p", "phi", "k", "omega", "nut")

# the shared planted perturbation (rule 3), same value as roache_triple.PLANT
PLANT = rt.PLANT                       # 1.234e-03
PLANT_TOL = rt.PLANT_READBACK_TOL      # 1e-12

EXIT_OK, EXIT_FAIL, EXIT_REFUSE, EXIT_NOT_A_RESULT = 0, 1, 2, 3


class Refusal(rt.Refusal):
    pass


def refuse(msg):
    raise Refusal(msg)


# ---------------------------------------------------------------------------
# Np arithmetic
# ---------------------------------------------------------------------------
def power_number(torque_Nm, rho, N_rev_s, D_m):
    """Np = 2*pi*Q / (rho * N**2 * D**5).  Torque is |Q| about the axis; a Rushton
    impeller DRAWS power, so a physical torque magnitude gives Np > 0."""
    if rho <= 0 or N_rev_s <= 0 or D_m <= 0:
        refuse(f"rho, N, D must be positive; got rho={rho}, N={N_rev_s}, D={D_m}")
    Q = abs(float(torque_Nm))
    return 2.0 * math.pi * Q / (rho * N_rev_s ** 2 * D_m ** 5)


# ---------------------------------------------------------------------------
# THE READ PATH -- moment.dat  (this is what the planted control plants into)
#
# FINDING 2 (cfd-supervisor check-1 diff-read, 2026-09-09): the total-moment
# column position and the shaft axis are OpenFOAM-version-dependent and are the
# single highest-risk SILENT-wrong-number path -- a wrong column gives a wrong Np
# with no refusal, and the planted control cannot catch it because it plants into
# whatever column the reader reads.  This reader therefore FAILS CLOSED: it
# resolves the total-moment axial column FROM THE moment.dat HEADER (never from an
# assumed position) and REFUSES if the header does not name it.  The layout MUST
# STILL be confirmed first-hand against a REAL moment.dat at the A3FL1 exercise
# smoke, for the exact solver version, and pinned here -- see the prereg section 7.
# ---------------------------------------------------------------------------
def _norm_tokens(s):
    """Strip a leading '#', turn '(a b c)' bracketing into plain tokens, split."""
    s = s.lstrip("#").replace("(", " ").replace(")", " ")
    return s.split()


def _resolve_total_axial_col(comment_lines, axis):
    """Locate, FROM THE HEADER, the data-token index of the TOTAL moment's axial
    component.  OpenFOAM forces/functionObject moment.dat labels its columns in a
    '#' header, e.g. '# Time (total_x total_y total_z) (pressure_x ...) ...'.
    Because both the header and each data row lead with the time column, the
    header token index equals the data token index.  Refuses if no header names
    'total_<axis>' -- fail-closed, so a wrong column becomes a REFUSAL not a
    silent number (FINDING 2)."""
    want = f"total_{axis}"
    for cl in comment_lines:
        toks = _norm_tokens(cl)
        if want in toks:
            return toks.index(want)
    refuse(f"moment.dat header does not name {want!r}; the total-moment column "
           "cannot be resolved from the header, so the axial torque is NOT read "
           "from an assumed position (FINDING 2, fail-closed). Pin the verified "
           "column layout against a real moment.dat at the exercise smoke.")


def _read_moment_file(moment_dat_path):
    """Return (comment_lines, last_data_line). Refuses if there is no data row."""
    if not os.path.isfile(moment_dat_path):
        refuse(f"no moment.dat at {moment_dat_path}")
    comments, last = [], None
    with open(moment_dat_path) as fh:
        for line in fh:
            s = line.rstrip("\n")
            st = s.strip()
            if not st:
                continue
            if st.startswith("#"):
                comments.append(st)
            else:
                last = st
    if last is None:
        refuse(f"{moment_dat_path}: no data rows (only comments/blank)")
    return comments, last


def read_axial_torque(moment_dat_path, axis="z"):
    """Read the impeller torque about the shaft axis from an OpenFOAM forces/
    functionObject moment.dat, returning the axial component of the TOTAL moment
    at the last time row.  Column resolved FROM THE HEADER (FINDING 2, fail-
    closed); refuses on anything it cannot read -- never a silent zero (rule 3)."""
    if axis not in ("x", "y", "z"):
        refuse(f"axis must be x/y/z, got {axis!r}")
    comments, last = _read_moment_file(moment_dat_path)
    col = _resolve_total_axial_col(comments, axis)
    nums = [float(t) for t in _norm_tokens(last)]
    if col >= len(nums):
        refuse(f"{moment_dat_path}: total_{axis} header column {col} beyond the "
               f"{len(nums)} numeric fields of the data row: {last!r}")
    return nums[col]


# ---------------------------------------------------------------------------
# LIVE planted-zero control on the moment.dat read path (rule 3)
# ---------------------------------------------------------------------------
def _plant_into_moment_dat(src_path, dst_path, axis="z", plant=PLANT):
    """Copy moment.dat to dst and add `plant` to the SAME header-resolved
    total-moment axial column of the LAST data row.  Plants into the exact field
    the reader reads (FINDING 2).  Returns the pre-plant axial torque."""
    with open(src_path) as fh:
        lines = fh.readlines()
    before = read_axial_torque(src_path, axis=axis)          # header-resolved
    comments = [ln.strip() for ln in lines if ln.strip().startswith("#")]
    col = _resolve_total_axial_col(comments, axis)
    # find the last data line index
    last_i = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s and not s.startswith("#"):
            last_i = i
    if last_i is None:
        refuse(f"{src_path}: no data row to plant into")
    # rewrite the last data row: bump the header-resolved column by `plant`,
    # preserving column order so the header still resolves the same index.
    nums = [float(t) for t in _norm_tokens(lines[last_i])]
    if col >= len(nums):
        refuse(f"{src_path}: resolved column {col} beyond data row width")
    nums[col] += plant
    lines[last_i] = "\t".join(f"{v:.12g}" for v in nums) + "\n"
    with open(dst_path, "w") as fh:
        fh.writelines(lines)
    return before


def planted_zero_control(moment_dat_path, axis="z", plant=PLANT):
    """Plant PLANT into a TEMP COPY of the real moment.dat, read it back through
    read_axial_torque -- the SAME parser the grade uses -- and report whether the
    reader saw it.  Returns a control dict compatible with
    roache_triple.assert_plant_control.  Never disturbs the graded file."""
    tmp = tempfile.mkdtemp(prefix="mrf_np_plant_")
    try:
        work = os.path.join(tmp, os.path.basename(moment_dat_path))
        before = _plant_into_moment_dat(moment_dat_path, work, axis=axis, plant=plant)
        after = read_axial_torque(work, axis=axis)
        return rt.external_plant_control(
            "read_axial_torque", before, after, plant=plant,
            artifact=os.path.abspath(moment_dat_path), level=None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# rule 4 -- strict completion (see prereg section 5)
# ---------------------------------------------------------------------------
def _time_dirs(case_dir):
    out = []
    for name in os.listdir(case_dir):
        try:
            t = float(name)
        except ValueError:
            continue
        if os.path.isdir(os.path.join(case_dir, name)):
            out.append((t, name))
    return sorted(out)


def strict_completion(case_dir, end_time, log_path, fields=REQUIRED_FIELDS,
                      delta_t=1.0):
    """Rule 4, all clauses.  Returns a dict of the evidence; refuses (exit 2) on
    any failure -- a run failing any clause is NOT done and is not graded.

    ``delta_t`` is the SIMPLE time step (iteration step); for a steady simpleFoam
    run it is 1.0 and the ExecutionTime-count clause reduces to n_exec ==
    endTime (CLAUDE.md rule 4 clause-5, Sanaa 2026-09-09).  The prereg (section 5)
    pins endTime as a HARD stop with NO residualControl early-exit, so
    last==endTime AND n_exec==round(endTime/deltaT) are both reachable."""
    ev = {"case_dir": os.path.abspath(case_dir), "endTime": end_time,
          "deltaT": delta_t}
    if not os.path.isdir(case_dir):
        refuse(f"no case dir {case_dir}")
    if not os.path.isfile(log_path):
        refuse(f"no solver log at {log_path}")
    log = open(log_path, encoding="utf-8", errors="replace").read()

    # clause: rc == 0.  We accept an explicit rc sidecar the launcher writes; if
    # absent we refuse rather than assume success (an assumed rc is not a check).
    rc_path = os.path.join(case_dir, "rc")
    if not os.path.isfile(rc_path):
        refuse(f"{case_dir}: no rc sidecar; rc==0 cannot be verified, so the run "
               "is not shown DONE (rule 4 clause 1). The launcher must capture rc "
               "INSIDE the detached wrapper (setsid parent returns 0 for every "
               "outcome -- memory: setsid-parent-returns-zero).")
    rc = open(rc_path).read().strip()
    if rc != "0":
        refuse(f"{case_dir}: rc = {rc!r} != 0 (rule 4 clause 1)")
    ev["rc"] = 0

    # clause: an End line
    if not re.search(r"^End\b", log, re.M):
        refuse(f"{log_path}: no 'End' line (rule 4 clause 2)")
    ev["end_line"] = True

    # clause: ExecutionTime count == round(endTime / deltaT)  (rule 4 clause-5,
    # Sanaa 2026-09-09; == endTime for the unit-step steady case, deltaT=1).
    # simpleFoam prints one 'ExecutionTime = <x> s' line per SIMPLE iteration.
    if float(delta_t) <= 0.0:
        refuse(f"deltaT must be positive, got {delta_t}")
    n_exec = len(re.findall(r"^ExecutionTime = ", log, re.M))
    expected = round(float(end_time) / float(delta_t))
    if n_exec != expected:
        refuse(f"{log_path}: ExecutionTime count {n_exec} != round(endTime/deltaT)"
               f" = round({end_time}/{delta_t}) = {expected} (rule 4 clause-5). "
               "A steady run must reach the pinned hard endTime; an early "
               "residualControl exit fails this AND the last==endTime clause -- "
               "the prereg section 5 pins endTime as a hard stop for this reason.")
    ev["exec_count"] = n_exec

    # clause: last written time == endTime
    tds = _time_dirs(case_dir)
    if not tds:
        refuse(f"{case_dir}: no time directories (rule 4 clause 3)")
    last_t, last_name = tds[-1]
    if abs(last_t - float(end_time)) > 1e-9:
        refuse(f"{case_dir}: last time {last_t} != endTime {end_time} "
               "(rule 4 clause 3)")
    ev["last_time"] = last_t
    end_dir = os.path.join(case_dir, last_name)

    # clause: fields present at endTime
    missing = [f for f in fields if not os.path.exists(os.path.join(end_dir, f))]
    if missing:
        refuse(f"{end_dir}: missing fields {missing} (rule 4 clause 4; "
               f"incompressible set {list(fields)})")
    ev["fields"] = list(fields)

    # clause: age guard -- every endTime field NEWER than the case's own 0/
    zero_dir = os.path.join(case_dir, "0")
    if not os.path.isdir(zero_dir):
        refuse(f"{case_dir}: no 0/ directory; the age guard has no datum "
               "(rule 4 clause 5)")
    # the age datum: mtime of 0/ (touched last at launch).  We use the newest
    # entry inside 0/ as the launch datum, matching mark_done_t3 practice.
    zero_mtime = max(os.path.getmtime(os.path.join(zero_dir, f))
                     for f in os.listdir(zero_dir)) if os.listdir(zero_dir) \
        else os.path.getmtime(zero_dir)
    stale = []
    for f in fields:
        fp = os.path.join(end_dir, f)
        if os.path.getmtime(fp) <= zero_mtime:
            stale.append(f)
    if stale:
        refuse(f"{end_dir}: fields {stale} are NOT newer than 0/ "
               f"(age guard, rule 4 clause 5) -- they may be from a prior run")
    ev["age_guard"] = "PASS"
    return ev


# ---------------------------------------------------------------------------
# assemble the level series and grade through the shared instrument
# ---------------------------------------------------------------------------
def build_level(name, case_dir, cells, end_time, rho, N, D, axis,
                iterative_state, plateau_state, moment_subdir="impellerForces",
                delta_t=1.0):
    """Complete-check ONE level and return its Np, cells, and states."""
    log_path = os.path.join(case_dir, "log.simpleFoam")
    ev = strict_completion(case_dir, end_time, log_path, delta_t=delta_t)
    # locate the newest moment.dat under postProcessing/<moment_subdir>/<t>/
    pp = os.path.join(case_dir, "postProcessing", moment_subdir)
    if not os.path.isdir(pp):
        refuse(f"{pp}: no forces postProcessing dir")
    cand = []
    for t in os.listdir(pp):
        m = os.path.join(pp, t, "moment.dat")
        if os.path.isfile(m):
            try:
                cand.append((float(t), m))
            except ValueError:
                pass
    if not cand:
        refuse(f"{pp}: no moment.dat under any time dir")
    _, moment_dat = sorted(cand)[-1]
    # rule 3: LIVE planted-zero control on THIS moment.dat, THIS parser
    pc = planted_zero_control(moment_dat, axis=axis)
    rt.assert_plant_control(pc)                     # refuses (exit 2) if blind
    Q = read_axial_torque(moment_dat, axis=axis)
    Np = power_number(Q, rho, N, D)
    return dict(name=name, cells=int(cells), value=Np,
                torque=Q, moment_dat=os.path.abspath(moment_dat),
                completion=ev, plant_control=pc,
                iterative_state=iterative_state, plateau_state=plateau_state)


def grade(levels_cfg, band, rho, N, D, axis="z"):
    """levels_cfg: list of dicts (name, case_dir, cells, end_time,
    iterative_state, plateau_state), coarse first.  Grades Np through
    roache_triple.grade_ladder at dim = 3."""
    if len(levels_cfg) < 3:
        refuse("a Roache triple needs at least three levels (rule 5)")
    built = [build_level(c["name"], c["case_dir"], c["cells"], c["end_time"],
                         rho, N, D, axis, c["iterative_state"], c["plateau_state"],
                         delta_t=c.get("delta_t", 1.0))
             for c in levels_cfg]
    levels = [dict(name=b["name"], cells=b["cells"], value=b["value"]) for b in built]
    iterative = {b["name"]: b["iterative_state"] for b in built}
    plateau = {b["name"]: b["plateau_state"] for b in built}
    # ONE control for the ladder: reuse the finest level's live control (each
    # level already had its own asserted above; grade_ladder needs one passed).
    row = rt.grade_ladder("Rushton Np (MRF)", levels, 3, band, built[-1]["plant_control"],
                          iterative_states=iterative, plateau_states=plateau,
                          reference=5.0)
    row["levels_detail"] = built
    return row


# ---------------------------------------------------------------------------
# selftest -- drive the moment.dat planted control BOTH directions (rule 3)
# ---------------------------------------------------------------------------
def _write_moment(path, mz):
    with open(path, "w") as fh:
        fh.write("# Forces\n# Time (total_x total_y total_z) ...\n")
        fh.write(f"3000\t(0.0 0.0 {mz:.12g})\t(0 0 0)\t(0 0 0)\n")


def selftest():
    print("grade_mrf_np.py --selftest  (rule 3: a zero from a blind reader is not evidence)")
    ok = True
    tmp = tempfile.mkdtemp(prefix="mrf_np_selftest_")
    try:
        # a physical Rushton torque at N=5, D=0.1, rho=998 that gives Np ~ 5:
        # Q = Np*rho*N^2*D^5/(2pi) = 5*998*25*1e-5/(2pi) ~ 0.01985 N*m
        rho, N, D = 998.0, 5.0, 0.1
        Q_true = 5.0 * rho * N ** 2 * D ** 5 / (2 * math.pi)
        m = os.path.join(tmp, "moment.dat")
        _write_moment(m, -Q_true)      # axial moment opposes +z omega (drawing power)

        # (1) the reader SEES the true torque and Np arithmetic round-trips
        Q_read = read_axial_torque(m, axis="z")
        Np = power_number(Q_read, rho, N, D)
        c1 = abs(Np - 5.0) < 1e-9
        ok &= c1
        print(f"  [{'ok ' if c1 else 'FAIL'}] reader sees torque {Q_read:.6g} -> Np {Np:.6f} (want 5.0)")

        # (2) GREEN: a working reader SEES the planted perturbation
        pc = planted_zero_control(m, axis="z")
        c2 = pc["passed"] and abs(pc["reader_delta"] - PLANT) < PLANT_TOL
        ok &= c2
        print(f"  [{'ok ' if c2 else 'FAIL'}] working reader SEES planted {PLANT} "
              f"(saw {pc['reader_delta']:.6e})")

        # (3) RED: a blind reader (hand it a stale before/after) FAILS the control
        blind = rt.external_plant_control("blind", 1.0, 1.0)
        try:
            rt.assert_plant_control(blind)
            c3 = False
            print("  [FAIL] a blind control was accepted -- the gate is blind")
        except rt.Refusal:
            c3 = True
            print("  [ok ] a blind reader FAILS the control (grade refuses, exit 2)")
        ok &= c3

        # (4) the plant does not disturb the graded file: it reads back identical
        #     to before the control ran (compared through the same parser).
        Q_after = read_axial_torque(m, axis="z")
        c4 = Q_after == Q_read
        ok &= c4
        print(f"  [{'ok ' if c4 else 'FAIL'}] control planted into a temp copy only "
              "(graded moment.dat untouched)")

        # (5) refuse-not-degrade: a moment.dat with no data row refuses
        empty = os.path.join(tmp, "empty.dat")
        with open(empty, "w") as fh:
            fh.write("# only a comment\n")
        try:
            read_axial_torque(empty)
            c5 = False
            print("  [FAIL] read a zero from an empty moment.dat")
        except rt.Refusal:
            c5 = True
            print("  [ok ] refuses an empty moment.dat rather than returning 0")
        ok &= c5

        # (6) band mutation: same Np, band flipped -> PASS vs GATE FAIL through
        #     the shared instrument (proves the band is load-bearing)
        levels = [dict(name=n, cells=c, value=v) for n, c, v in
                  zip(("c", "m", "f"), (250000, 850000, 2900000),
                      # a CONVERGING synthetic Np triple approaching ~4.6
                      (4.30, 4.52, 4.58))]
        okstate = {"c": "CONVERGED", "m": "CONVERGED", "f": "CONVERGED"}
        plst = {"c": "PLATEAUED", "m": "PLATEAUED", "f": "PLATEAUED"}
        row_pass = rt.grade_ladder("np", levels, 3, (4.0, 6.0), pc,
                                   iterative_states=okstate, plateau_states=plst)
        row_fail = rt.grade_ladder("np", levels, 3, (5.9, 6.0), pc,
                                   iterative_states=okstate, plateau_states=plst)
        c6 = (row_pass["verdict"] == "PASS" and row_fail["verdict"] == "GATE FAIL"
              and "GCI_pct" in row_pass)
        ok &= c6
        print(f"  [{'ok ' if c6 else 'FAIL'}] band load-bearing via shared instrument: "
              f"[4,6]->{row_pass['verdict']}, [5.9,6]->{row_fail['verdict']}")

        # (7) FINDING 2 fail-closed: a header that does not NAME total_<axis> is
        #     refused, never read from an assumed position.
        noheader = os.path.join(tmp, "noheader.dat")
        with open(noheader, "w") as fh:
            fh.write("# Time Mx My Mz\n")            # no 'total_' label
            fh.write("3000\t(0 0 -0.2)\n")
        try:
            read_axial_torque(noheader, axis="z")
            c7 = False
            print("  [FAIL] read from a header without total_z (silent-wrong-column path OPEN)")
        except rt.Refusal:
            c7 = True
            print("  [ok ] FINDING 2 fail-closed: refuses when header does not name total_z")
        ok &= c7

        # (8) FINDING 1: the ExecutionTime-count clause (rule 4 clause-5).
        import time
        casedir = os.path.join(tmp, "case")
        os.makedirs(os.path.join(casedir, "0"))
        os.makedirs(os.path.join(casedir, "50"))
        past = time.time() - 100
        for f in REQUIRED_FIELDS:
            open(os.path.join(casedir, "0", f), "w").close()
            os.utime(os.path.join(casedir, "0", f), (past, past))
            open(os.path.join(casedir, "50", f), "w").close()  # newer -> age guard OK
        with open(os.path.join(casedir, "rc"), "w") as fh:
            fh.write("0")
        logp = os.path.join(casedir, "log.simpleFoam")
        with open(logp, "w") as fh:
            for i in range(1, 51):                    # 50 iterations, deltaT=1
                fh.write(f"Time = {i}\n")
                fh.write(f"ExecutionTime = {i} s  ClockTime = {i} s\n")
            fh.write("End\n")
        try:
            ev = strict_completion(casedir, 50, logp, delta_t=1.0)
            c8a = ev.get("exec_count") == 50 and ev.get("last_time") == 50.0
        except rt.Refusal as exc:
            c8a = False
            print(f"       (unexpected refusal on the good case: {exc})")
        print(f"  [{'ok ' if c8a else 'FAIL'}] good run: n_exec 50 == endTime 50, "
              "last==endTime, age guard PASS")
        ok &= c8a
        try:                                          # count mismatch -> refuse
            strict_completion(casedir, 4000, logp, delta_t=1.0)
            c8b = False
            print("  [FAIL] a 50-iter log passed as endTime 4000 (count clause not enforced)")
        except rt.Refusal as exc:
            c8b = "ExecutionTime count" in str(exc)
            print(f"  [{'ok ' if c8b else 'FAIL'}] count mismatch (50 != 4000) refuses via clause-5")
        ok &= c8b

        print(f"\nSELFTEST: {'PASS' if ok else 'FAIL'} -- every arm hit its expectation."
              if ok else "\nSELFTEST: FAIL")
        return EXIT_OK if ok else EXIT_FAIL
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--levels", help="JSON file: [{name,case_dir,cells,end_time,"
                    "iterative_state,plateau_state}, ...] coarse first")
    ap.add_argument("--band", help="lo,hi -- the PRE-REGISTERED band (default from prereg)",
                    default="4.0,6.0")
    ap.add_argument("--rho", type=float, default=998.0)
    ap.add_argument("--N", type=float, default=5.0, help="impeller speed, rev/s")
    ap.add_argument("--D", type=float, default=0.10, help="impeller diameter, m")
    ap.add_argument("--axis", default="z")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    if sys.flags.optimize:
        print("REFUSE: this grader does not run under python -O (rule 4/L-332)")
        return EXIT_REFUSE
    if args.selftest:
        return selftest()
    if not args.levels:
        ap.error("--levels is required (or --selftest)")
    try:
        with open(args.levels) as fh:
            cfg = json.load(fh)
        lo, hi = (float(x) for x in args.band.split(","))
        row = grade(cfg, (lo, hi), args.rho, args.N, args.D, axis=args.axis)
    except rt.Refusal as exc:
        print(f"REFUSE: {exc}")
        return EXIT_REFUSE
    print(rt.format_row(row))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(row, fh, indent=2, sort_keys=True, default=str)
        print(f"    written: {os.path.abspath(args.json_out)}")
    return rt.exit_code_for(row["verdict"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
