#!/usr/bin/env python3
"""PRD-E1 §2ba DETACHED AUTOGRADER -- Porous Radiator Duct, Navier-spine Case 3.

The detached collector/grader specified by the pre-registration §8 (§2ba spec) and
ruling §4 condition 4.  It ORCHESTRATES the FROZEN comparator `analyse_prd.py`; it
does NOT reimplement any gate, reader, control or triple logic.  Everything graded
here goes through `analyse_prd` (which itself delegates rule-4 completion to
`mark_done_prd.py` and the rule-5 triple/GCI to `scripts/roache_triple.py`).

WHAT IT DOES  (prereg §8 §2ba, verbatim scope)
----------------------------------------------
Launched DETACHED (PPID=1, survives fleet death; the setsid re-exec pattern of
run_prd.sh, rc captured in the foreground child).  Then, per U_s and per level:
  * watches the monitored Delta-p to PLATEAU (not rc=0 alone; L-15/L-89);
  * applies the rule-4 completion clauses + age guard via analyse_prd.require_done
    (-> mark_done_prd.py, the {U,p,k,omega,nut,phi} field set);
  * reads Delta-p via the planted-zero-controlled reader (analyse_prd.read_dp_pa +
    control_dp_reader plant read-back + visibility_pair INERT/ACTIVE, §6 / rule 3);
  * assembles the 3-level triple per U_s and grades it with analyse_prd.grade_us
    (rule-5 hierarchy -> G-ERGUN band + G-ASYMP + GCI at Fs=1.25; pre-asymptotic /
    order-band guards flag L4);
  * applies the y+ gate (analyse_prd.yplus_from_log + control_yplus_log, max<=200)
    and the checkMesh gate (non-ortho<70/mean<20, skew<4) from the launcher logs;
  * writes a durable gate_prd_e1.json.

WHAT IT WILL NOT DO
-------------------
  * It will NOT grade while the comparator is UNFROZEN: it calls
    analyse_prd.verify_self() first, which REFUSES (exit 2) while
    GRADING_PATH_FREEZE_COMMIT == 'PIN-AT-FREEZE' (rule 2).  So this file may be
    committed BEFORE freeze and simply refuses to grade until the pin is set.
  * It LAUNCHES NO graded solve.  When grade_us flags a U_s PRE-ASYMPTOTIC it
    RECORDS 'L4-REQUIRED' in the JSON for that U_s; launching L4 is the supervisor's
    call (the ladder launch harness), never this watcher's.
  * It writes ONLY under --root (the run tree) and its own gate_prd_e1.json; never
    the case-input dir, never a scratch handoff (L-186).

L-332: no module-level assert; --selftest drives the checks on synthetic case trees.
L-41/scratchpad: discovers cases by reading each case's OWN inlet U_s and cell count
(not by a fragile name contract), so the launch harness may name dirs freely.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"
sys.path.insert(0, HERE)
import analyse_prd as A                                              # noqa: E402

EXIT_OK, EXIT_REFUSE = 0, 2

# --- plateau + iterative-convergence watch parameters (NOT gate inputs) -----
# The gated Delta-p must PLATEAU (change < tol over the last WINDOW writes), the
# convergence criterion (L-15/L-89), never rc=0 alone.  These are watch controls,
# not gate thresholds; the gate bands live frozen in analyse_prd.
PLATEAU_REL_TOL = 1.0e-4     # |dp_n - dp_{n-WINDOW}| / |dp_n| < this  -> PLATEAUED
PLATEAU_WINDOW  = 3          # consecutive surfaceFieldValue writes compared
IT_RESID_TOL    = 1.0e-5     # final Ux & p initial residual below this -> CONVERGED
DEFAULT_INTERVAL = 30.0      # s between watch polls
DEFAULT_MAX_WAIT = 6.0 * 3600  # s; a watch that never plateaus is reported, not hung


# ==========================================================================
# CASE DISCOVERY -- read each case's OWN U_s, level and active/inert from disk
# ==========================================================================
def _read_us(case_dir: str):
    """Inlet superficial U_s from 0/U (or 0.orig/U): the x-component of the inlet
    fixedValue.  Returns float or None."""
    for cand in ("0/U", "0.orig/U"):
        p = os.path.join(case_dir, cand)
        if not os.path.isfile(p):
            continue
        txt = open(p, errors="replace").read()
        m = re.search(r"inlet\s*\{[^}]*?uniform\s*\(\s*([-\d.eE+]+)", txt, re.S)
        if m:
            return float(m.group(1))
    return None


def _read_cells(case_dir: str):
    """Cell count from checkMesh log ('cells:  N') or polyMesh/owner header."""
    lg = os.path.join(case_dir, "log.checkMesh")
    if os.path.isfile(lg):
        m = re.search(r"cells:\s*(\d+)", open(lg, errors="replace").read())
        if m:
            return int(m.group(1))
    owner = os.path.join(case_dir, "constant/polyMesh/owner")
    if os.path.isfile(owner):
        m = re.search(r"note\s*\".*nCells:\s*(\d+)", open(owner, errors="replace").read())
        if m:
            return int(m.group(1))
    return None


def _level_of(cells):
    """Map a cell count to the frozen level name (exact match to CELLS)."""
    if cells is None:
        return None
    for lv, n in A.CELLS.items():
        if cells == n:
            return lv
    return None


def _read_active(case_dir: str):
    """True if fvOptions carries a NONZERO streamwise Darcy d (ACTIVE sink),
    False if d=f=0 (INERT visibility control)."""
    p = os.path.join(case_dir, "system/fvOptions")
    if not os.path.isfile(p):
        return None
    txt = open(p, errors="replace").read()
    m = re.search(r"\bd\s+\(\s*([-\d.eE+]+)", txt)
    if not m:
        return None
    return abs(float(m.group(1))) > 0.0


def discover_cases(root: str):
    """Every immediate subdir of root that looks like a PRD case -> a descriptor
    dict {case, dir, u_s, level, cells, active}.  Skips dirs we cannot classify."""
    out = []
    for d in sorted(glob.glob(os.path.join(root, "*"))):
        if not os.path.isdir(d):
            continue
        if not os.path.isdir(os.path.join(d, "system")):
            continue
        us = _read_us(d)
        cells = _read_cells(d)
        lv = _level_of(cells)
        act = _read_active(d)
        if us is None or lv is None or act is None:
            continue
        out.append(dict(case=os.path.basename(d), dir=d, u_s=us, level=lv,
                        cells=cells, active=act))
    return out


# ==========================================================================
# PLATEAU + ITERATIVE-CONVERGENCE WATCH (the convergence criterion, not rc=0)
# ==========================================================================
def _dp_series(case_dir: str):
    """The monitored core Delta-p series in Pa (×rho), one value per
    surfaceFieldValue write.  Uses analyse_prd's plane reader on the WHOLE series
    (not just the last row).  Returns [] if the read path is not there yet."""
    try:
        inl = A._plane_dat(case_dir, "dp_inlet_plane")
        out = A._plane_dat(case_dir, "dp_outlet_plane")
    except SystemExit:
        return []
    def _rows(path):
        rows = []
        for line in open(path, errors="replace"):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            c = s.split()
            try:
                rows.append((float(c[0]), float(c[-1])))
            except (ValueError, IndexError):
                continue
        return rows
    ri, ro = _rows(inl), _rows(out)
    n = min(len(ri), len(ro))
    return [A.dp_pa(ri[i][1], ro[i][1]) for i in range(n)]


def plateau_state(case_dir: str) -> str:
    """'PLATEAUED' if the last PLATEAU_WINDOW+1 monitored Delta-p writes agree to
    PLATEAU_REL_TOL, else 'NOT_PLATEAUED'.  The state string is what analyse_prd
    (-> roache) requires; anything but 'PLATEAUED' fails the triple (rule 5 step a)."""
    s = _dp_series(case_dir)
    if len(s) < PLATEAU_WINDOW + 1:
        return "NOT_PLATEAUED"
    last = s[-1]
    if last == 0.0:
        return "NOT_PLATEAUED"
    window = s[-(PLATEAU_WINDOW + 1):]
    if max(abs(v - last) for v in window) / abs(last) < PLATEAU_REL_TOL:
        return "PLATEAUED"
    return "NOT_PLATEAUED"


def iterative_state(case_dir: str) -> str:
    """'CONVERGED' if the final Ux AND p initial residuals are below IT_RESID_TOL,
    else 'NOT_CONVERGED'.  Read from log.simpleFoam (the launcher's solver log)."""
    lg = os.path.join(case_dir, "log.simpleFoam")
    if not os.path.isfile(lg):
        return "NOT_CONVERGED"
    txt = open(lg, errors="replace").read()
    def _last(field):
        ms = re.findall(r"Solving for %s, Initial residual = ([-\d.eE+]+)" % field, txt)
        return float(ms[-1]) if ms else None
    ux, p = _last("Ux"), _last("p")
    if ux is None or p is None:
        return "NOT_CONVERGED"
    return "CONVERGED" if (ux < IT_RESID_TOL and p < IT_RESID_TOL) else "NOT_CONVERGED"


def all_ready(cases, root):
    """A case is READY when its run is rule-4 DONE (mark_done) AND its monitored
    Delta-p has PLATEAUED.  Returns (ready:bool, per_case_status:list)."""
    st = []
    ready = True
    for c in cases:
        done = _mark_done_ok(root, c["case"])
        plat = plateau_state(c["dir"])
        r = done and plat == "PLATEAUED"
        ready = ready and r
        st.append(dict(case=c["case"], done=done, plateau=plat, ready=r))
    return ready, st


def _mark_done_ok(root: str, case: str) -> bool:
    md = os.path.join(HERE, "mark_done_prd.py")
    if not os.path.isfile(md):
        return False
    r = subprocess.run([sys.executable, md, "--root", root, "--case", case],
                       capture_output=True, text=True)
    return r.returncode == 0


# ==========================================================================
# THE Y+ AND checkMesh GATES (read the launcher's logs; produce y+ if absent)
# ==========================================================================
def yplus_gate(case_dir: str, foam_bashrc: str):
    """Run `simpleFoam -postProcess -func yPlus -latestTime` if no y+ log exists,
    then grade max y+ <= YPLUS_MAX via analyse_prd's reader + planted control."""
    ylog = os.path.join(case_dir, "log.yPlus")
    if not os.path.isfile(ylog) and foam_bashrc and foam_bashrc != "none" \
            and os.path.isfile(foam_bashrc):
        cmd = (". %s >/dev/null 2>&1; simpleFoam -case %s -postProcess -func yPlus "
               "-latestTime > %s 2>&1" % (foam_bashrc, case_dir, ylog))
        subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    if not os.path.isfile(ylog):
        return dict(passed=False, why="no y+ log and could not produce one")
    try:
        yr = A.yplus_from_log(ylog)              # REFUSES an all-zero reading (rule 3)
        ctl = A.control_yplus_log(ylog)          # plant read-back or refuse (rule 3)
    except SystemExit:
        return dict(passed=False, why="y+ reader/control REFUSED (rule 3)")
    worst = max(v["max"] for v in yr.values())
    ok = ctl.get("passed") and worst <= A.YPLUS_MAX
    return dict(passed=bool(ok), max_yplus=worst, limit=A.YPLUS_MAX,
                control_passed=bool(ctl.get("passed")), per_patch=yr, artifact=ylog)


def checkmesh_gate(case_dir: str):
    """Parse log.checkMesh: non-ortho max<70 & mean<20, skewness<4 (§5 gate)."""
    lg = os.path.join(case_dir, "log.checkMesh")
    if not os.path.isfile(lg):
        return dict(passed=False, why="no log.checkMesh")
    txt = open(lg, errors="replace").read()
    nom = re.search(r"non-orthogonality.*?Max:\s*([-\d.eE+]+).*?average:\s*([-\d.eE+]+)",
                    txt, re.S | re.I)
    skm = re.search(r"[Mm]ax skewness\s*=\s*([-\d.eE+]+)", txt)
    if not nom or not skm:
        return dict(passed=False, why="could not parse non-ortho / skewness")
    no_max, no_avg, skew = float(nom.group(1)), float(nom.group(2)), float(skm.group(1))
    ok = no_max < 70.0 and no_avg < 20.0 and skew < 4.0
    return dict(passed=bool(ok), nonortho_max=no_max, nonortho_mean=no_avg,
                skewness=skew, artifact=lg)


# ==========================================================================
# THE GRADE -- orchestrate analyse_prd.grade_us per U_s; write gate_prd_e1.json
# ==========================================================================
def grade_all(root: str, foam_bashrc: str = "none"):
    """Grade the full ladder.  REFUSES (exit 2) if the comparator is unfrozen
    (analyse_prd.verify_self) or a case is not rule-4 DONE.  Returns the result
    dict (also written to gate_prd_e1.json under root)."""
    A.verify_self()                              # rule 2: refuses while unpinned
    cases = discover_cases(root)
    if not cases:
        A.refuse("no classifiable PRD cases under %s -- nothing to grade" % root)

    # rule-4 completion for EVERY case (active + inert), via mark_done_prd
    A.require_done([c["case"] for c in cases])

    by_us = {}
    for c in cases:
        by_us.setdefault(round(c["u_s"], 6), []).append(c)

    results = {}
    any_l4 = []
    for us in sorted(by_us):
        group = by_us[us]
        active = {c["level"]: c for c in group if c["active"]}
        inert = [c for c in group if not c["active"]]
        needed = ("L1", "L2", "L3")
        if not all(lv in active for lv in needed):
            results["%.2f" % us] = dict(verdict="PENDING",
                why="missing ACTIVE levels %s (have %s)"
                    % ([lv for lv in needed if lv not in active], sorted(active)))
            continue

        dp_by_level = {lv: A.read_dp_pa(active[lv]["dir"])[0] for lv in needed}
        # add L4 if an ACTIVE L4 case exists (pre-asymptotic re-form)
        have_l4 = "L4" in active
        if have_l4:
            dp_by_level["L4"] = A.read_dp_pa(active["L4"]["dir"])[0]

        # planted-zero controls (rule 3), on the FINEST active level's plane dats
        fine = active["L3"]["dir"]
        plant_control = A.control_dp_reader(
            A._plane_dat(fine, "dp_inlet_plane"),
            A._plane_dat(fine, "dp_outlet_plane"))
        vis = None
        if inert:
            vis = A.visibility_pair(A.read_dp_pa(inert[0]["dir"])[0], dp_by_level["L3"])

        st_it = {lv: iterative_state(active[lv]["dir"]) for lv in needed}
        st_pl = {lv: plateau_state(active[lv]["dir"]) for lv in needed}
        if have_l4:
            st_it["L4"] = iterative_state(active["L4"]["dir"])
            st_pl["L4"] = plateau_state(active["L4"]["dir"])

        verdict, detail = A.grade_us(us, dp_by_level, plant_control, st_it, st_pl,
                                     have_l4=have_l4)
        if detail.get("flag_L4") and not have_l4:
            any_l4.append("%.2f" % us)

        yg = yplus_gate(active["L3"]["dir"], foam_bashrc)
        cm = checkmesh_gate(active["L3"]["dir"])
        # a gate can only turn a PASS/GATE FAIL INTO NOT A RESULT, never the reverse
        final = verdict
        gate_notes = []
        if verdict in ("PASS", "GATE FAIL"):
            if not cm.get("passed"):
                final = "NOT A RESULT"; gate_notes.append("checkMesh gate failed")
            if not yg.get("passed"):
                final = "NOT A RESULT"; gate_notes.append("y+ gate failed")

        results["%.2f" % us] = dict(
            verdict=final, gate_us_verdict=verdict, ergun_pa=detail.get("ergun"),
            dp_by_level=dp_by_level, order=detail.get("order"),
            gci_pct=detail.get("gci_pct"), richardson=detail.get("richardson"),
            asymp_rel=detail.get("asymp_rel"), why=detail.get("why"),
            plant_control_passed=plant_control.get("passed"),
            visibility_pair=vis, yplus_gate=yg, checkmesh_gate=cm,
            iterative_states=st_it, plateau_states=st_pl,
            l4_required=bool(detail.get("flag_L4") and not have_l4),
            gate_notes=gate_notes)

    passed = [u for u, r in results.items() if r["verdict"] == "PASS"]
    credential = len(passed) == len(A.U_S_SET) and len(results) == len(A.U_S_SET)
    summary = dict(
        ladder="PRD-E1", fs=A.FS, band_rel=A.ERGUN_BAND_REL,
        asymp_band_rel=A.ASYMP_BAND_REL, freeze_pin=A.GRADING_PATH_FREEZE_COMMIT,
        per_us=results, n_pass=len(passed), n_us=len(A.U_S_SET),
        l4_required_for=any_l4, credential=bool(credential),
        graded_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    outp = os.path.join(root, "gate_prd_e1.json")
    with open(outp, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    A.note("gate_prd_e1.json written -> %s" % outp)
    A.note("PRD-E1: %d/%d U_s PASS; credential=%s%s"
           % (len(passed), len(A.U_S_SET), credential,
              ("; L4 required for U_s " + ", ".join(any_l4)) if any_l4 else ""))
    return summary


# ==========================================================================
# DETACH + WATCH LOOP
# ==========================================================================
def detach_once(argv_extra):
    """Re-exec DETACHED via setsid (PPID=1), survives fleet death; rc lives in the
    detached child.  Guard env var prevents a re-detach loop."""
    if os.environ.get("PRD_AG_DETACHED") == "1":
        return False
    os.environ["PRD_AG_DETACHED"] = "1"
    log = argv_extra.get("log")
    cmd = ["setsid", sys.executable, os.path.abspath(__file__)] + argv_extra["args"] \
        + ["--no-detach"]
    with open(log, "a") as lf:
        subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=lf, stderr=lf,
                         start_new_session=True, env=os.environ.copy())
    print("autograder launched DETACHED; watch log -> %s" % log)
    return True


def watch_and_grade(root, interval, max_wait, foam_bashrc):
    t0 = time.time()
    while True:
        cases = discover_cases(root)
        ready, st = all_ready(cases, root) if cases else (False, [])
        A.note("[%s] cases=%d ready=%s"
                % (time.strftime("%H:%M:%S"), len(cases), ready))
        for s in st:
            A.note("   %-24s done=%s plateau=%s" % (s["case"], s["done"], s["plateau"]))
        if ready and cases:
            return grade_all(root, foam_bashrc=foam_bashrc)
        if time.time() - t0 > max_wait:
            A.note("MAX_WAIT (%gs) exceeded; not all cases ready -- reporting, not "
                   "grading (a watch that never plateaus is a finding, not a pass)"
                   % max_wait)
            return dict(status="TIMEOUT_NOT_READY", per_case=st)
        time.sleep(interval)


# ==========================================================================
# --selftest -- synthetic case trees; drive discovery, plateau, grade path
# ==========================================================================
_CHECKS = []


def _ck(name, ok, detail=""):
    _CHECKS.append(bool(ok))
    print("  [%s] %s%s" % ("ok " if ok else "FAIL", name, ("   " + detail) if detail else ""))


def _mk_case(root, name, u_s, cells, active, dp_series_pa, converged=True):
    """Write a synthetic case tree just rich enough for discovery + plateau +
    the plane reader (NOT a real solve)."""
    d = os.path.join(root, name)
    for sub in ("system", "constant/polyMesh", "0",
                "postProcessing/dp_inlet_plane/0", "postProcessing/dp_outlet_plane/0"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    open(os.path.join(d, "0/U"), "w").write(
        "boundaryField{ inlet { type fixedValue; value uniform (%r 0 0); } }\n" % u_s)
    dval = A.__dict__.get("D_STREAM", 9.375e7) if active else 0.0
    # build_prd emits fvOptions with 'd (dx dy dz);' -- mimic for _read_active
    open(os.path.join(d, "system/fvOptions"), "w").write(
        "porosity1{ DarcyForchheimerCoeffs{ d (%r 0 0); f (0 0 0); } }\n"
        % (9.375e7 if active else 0.0))
    open(os.path.join(d, "log.checkMesh"), "w").write(
        "    cells:  %d\n   ...non-orthogonality Max: 0.0 average: 0.0\n"
        "Max skewness = 0.0\n" % cells)
    open(os.path.join(d, "log.simpleFoam"), "w").write(
        ("Solving for Ux, Initial residual = %s\n"
         "Solving for p, Initial residual = %s\nEnd\n")
        % ("1e-7" if converged else "1e-2", "1e-7" if converged else "1e-2"))
    open(os.path.join(d, "log.yPlus"), "w").write(
        "patch walls y+ : min = 12.3, max = 55.0, average = 30.1\n")
    # plane series: outlet fixed ~0, inlet = dp/RHO so ×rho gives dp
    for t, dp in enumerate(dp_series_pa):
        pass
    def _wr(name2, vals):
        p = os.path.join(d, "postProcessing", name2, "0", "surfaceFieldValue.dat")
        with open(p, "w") as f:
            f.write("# Time areaAverage(p)\n")
            for i, v in enumerate(vals):
                f.write("%d %r\n" % (50 * (i + 1), v))
    _wr("dp_inlet_plane", [dp / A.RHO for dp in dp_series_pa])
    _wr("dp_outlet_plane", [0.0 for _ in dp_series_pa])
    return d


def selftest():
    import shutil
    import tempfile
    print("autograde_prd.py --selftest  (discovery + plateau + grade orchestration)")
    tmp = tempfile.mkdtemp(prefix="prd_autograde_")
    try:
        # a plateaued vs a still-moving Delta-p series
        flat = [825.20, 825.203, 825.201, 825.202, 825.2015]
        moving = [700.0, 760.0, 800.0, 815.0, 825.2]
        _mk_case(tmp, "c_l1", 1.0, A.CELLS["L1"], True, flat)
        _ck("discover_cases finds a classified case",
            len(discover_cases(tmp)) == 1)
        c = discover_cases(tmp)[0]
        _ck("case classified: U_s=1.0 L1 ACTIVE",
            abs(c["u_s"] - 1.0) < 1e-9 and c["level"] == "L1" and c["active"] is True)
        _ck("plateau_state PLATEAUED on a flat series",
            plateau_state(c["dir"]) == "PLATEAUED")
        _ck("iterative_state CONVERGED on low residuals",
            iterative_state(c["dir"]) == "CONVERGED")

        _mk_case(tmp, "c_move", 1.0, A.CELLS["L2"], True, moving)
        cm = [x for x in discover_cases(tmp) if x["case"] == "c_move"][0]
        _ck("plateau_state NOT_PLATEAUED on a still-moving series",
            plateau_state(cm["dir"]) == "NOT_PLATEAUED")

        # INERT classification
        _mk_case(tmp, "c_inert", 1.0, A.CELLS["L1"], False, [0.02, 0.02, 0.02, 0.02, 0.02])
        ci = [x for x in discover_cases(tmp) if x["case"] == "c_inert"][0]
        _ck("INERT case classified active=False", ci["active"] is False)

        # checkMesh + y+ gates on the synthetic logs
        _ck("checkMesh gate PASSES a clean all-hex log",
            checkmesh_gate(c["dir"])["passed"])
        yg = yplus_gate(c["dir"], "none")
        _ck("y+ gate PASSES (max 55 <= 200) with a live plant control",
            yg["passed"] and abs(yg["max_yplus"] - 55.0) < 1e-9)

        # grade_all must REFUSE while the comparator is UNFROZEN (rule 2)
        rc = subprocess.run([sys.executable, os.path.abspath(__file__),
                             "--grade", "--root", tmp, "--no-detach"],
                            capture_output=True, text=True)
        _ck("grade_all REFUSES while comparator UNFROZEN (verify_self, rule 2)",
            rc.returncode == EXIT_REFUSE and "PIN-AT-FREEZE" in (rc.stdout + rc.stderr))

        # no module-level assert (L-332)
        import ast
        src = open(os.path.abspath(__file__)).read()
        n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
        _ck("no assert in module body (L-332)", n0 == 0, "%d asserts" % n0)

        n_ok = sum(1 for x in _CHECKS if x)
        print("\n%d/%d checks passed" % (n_ok, len(_CHECKS)))
        return 0 if n_ok == len(_CHECKS) else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None, help="the PRD run tree (RUNS)")
    ap.add_argument("--grade", action="store_true", help="grade once, now (no watch)")
    ap.add_argument("--watch", action="store_true", help="watch to plateau, then grade")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    ap.add_argument("--max-wait", type=float, default=DEFAULT_MAX_WAIT)
    ap.add_argument("--foam-bashrc",
                    default="/usr/lib/openfoam/openfoam2606/etc/bashrc")
    ap.add_argument("--no-detach", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.root:
        ap.error("--root is required (or --selftest)")

    if args.watch and not args.no_detach:
        log = os.path.join(args.root, "autograde_prd.watch.log")
        detach_once(dict(args=[a for a in argv if a != "--no-detach"], log=log))
        return EXIT_OK

    if args.grade:
        grade_all(args.root, foam_bashrc=args.foam_bashrc)
        return EXIT_OK
    if args.watch:
        watch_and_grade(args.root, args.interval, args.max_wait, args.foam_bashrc)
        return EXIT_OK
    ap.error("give --grade, --watch or --selftest")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
