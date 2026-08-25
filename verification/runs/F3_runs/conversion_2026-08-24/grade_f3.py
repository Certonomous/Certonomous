#!/usr/bin/env python3
"""
F3 CONVERSION — THE FROZEN GRADING PATH.

This file is the grading path fixed at the pre-registration commit
(`verification/campaign/F3_CONVERSION_PREREGISTRATION.md`, standing rule 2).
It is verified at grade time by hashing this file against the committed blob:
run with `--prereg-commit <sha>` and this script REFUSES (exit 2) if the file
on disk is not byte-identical to the blob committed at that sha.

It grades the five frozen gates G-F3-1 .. G-F3-5 and nothing else. It contains
no tunable threshold: every band is a module-level constant declared in the
pre-registration before any solver in this conversion had started.

REFUSAL DISCIPLINE (standing rule 4): the comparator refuses (exit 2) rather
than degrade. A planted-zero control that cannot see its plant refuses. A run
that fails any clause of the completion rule is NOT graded — it is labelled and
its gate row carries the label, never a number.
"""
import sys
import os
import re
import json
import glob
import math
import hashlib
import argparse
import subprocess
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"
F3_ROOT = os.path.dirname(HERE)                       # .../verification/runs/F3_runs
REL_SELF = os.path.relpath(os.path.abspath(__file__), REPO)

sys.path.insert(0, F3_ROOT)

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS — declared in the pre-registration before any compute.
# ---------------------------------------------------------------------------

# Exact-theory reference values. Computed by F3_runs/exact_theory.py, which
# takes NO CFD input of any kind. Frozen here to full double precision so that
# the reference cannot drift with a later edit of that module.
EXACT = {
    # oblique-shock / theta-beta-M  (wedge)
    "wedge_M2.0_th15.0":   {"beta_deg": 45.343616761855984, "p2_p1": 2.1946531336077966},
    "wedge_M3.0_th15.0":   {"beta_deg": 32.240400182744665, "p2_p1": 2.821562321277495},
    "wedge_M2.5_th10.0":   {"beta_deg": 31.85059223127216,  "p2_p1": 1.8638705181801498},
    # Taylor-Maccoll  (cone)
    "cone_M2.35_thc10.0":  {"beta_deg": 26.73671771893154,  "pc_p1": 1.3739363670377716},
    # shock-expansion  (diamond)
    "diamond_M2.0_eps7.125": {"cd": 0.036331061285517954},
    "diamond_M2.5_eps5.0":   {"cd": 0.01343027834624868},
}

# Frozen bands (percent of the exact value). Derivations are in the
# pre-registration, section 4; none of them was chosen from a measured value
# produced by this conversion.
BAND_SURFACE_PRESSURE_PCT = 0.5    # G-F3-1 (wedge p2/p1), G-F3-3 (cone pc/p1)
BAND_SHOCK_ANGLE_PCT = 2.0         # G-F3-2 (wedge beta),  G-F3-4 (cone beta)
BAND_WAVE_DRAG_PCT = 1.0           # G-F3-5 (diamond cd)

# Roache triple gating (standing rule 5).
GRID_REFINEMENT_RATIO = 2.0        # by construction: every maker doubles both
                                   # mesh directions between levels, so h halves
                                   # exactly. Not inferred from a cell count.
GCI_FS = 1.25

# Planted-zero controls (standing rule 3).
PLANT_P = 1.234e-03                # additive plant into a surface-pressure column
PLANT_SLOPE = 1.000e-02            # planted slope increment for the beta fit
PLANT_FX = 1.234e-05               # additive plant into the force.dat total_x
PLANT_STEP_FRAC = 0.3717           # synthetic shock step location, as a fraction
                                   # of the synthetic sample line's span
PLANT_TOL_ABS = 1.0e-9
PLANT_TOL_DEG = 1.0e-6

# Completion rule (standing rule 4), adapted for a TRANSIENT adjustable-timestep
# solver. The adaptation is declared in the pre-registration, section 5.
REQUIRED_FIELDS = ("T", "U", "p", "rho")

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# 1. Grading-path freeze check (standing rule 2)
# ---------------------------------------------------------------------------

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen_against_commit(prereg_commit):
    """Hash this file against the blob committed at the pre-registration sha."""
    on_disk = sha256_file(os.path.abspath(__file__))
    try:
        blob = subprocess.run(
            ["git", "-C", REPO, "cat-file", "blob", "%s:%s" % (prereg_commit, REL_SELF)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
    except subprocess.CalledProcessError as e:
        refuse("grading path %s is not in commit %s (%s)"
               % (REL_SELF, prereg_commit, e.stderr.decode().strip()))
    committed = hashlib.sha256(blob).hexdigest()
    if committed != on_disk:
        refuse("grading path CHANGED since the pre-registration commit.\n"
               "  committed %s @ %s = %s\n  on disk               = %s"
               % (REL_SELF, prereg_commit, committed, on_disk))
    return dict(grading_path=REL_SELF, prereg_commit=prereg_commit,
                sha256=on_disk, frozen_match=True)


# ---------------------------------------------------------------------------
# 2. Strict completion rule (standing rule 4)
# ---------------------------------------------------------------------------

def _read_control(case_dir):
    txt = open(os.path.join(case_dir, "system", "controlDict")).read()

    def g(key):
        m = re.search(r"^\s*%s\s+([^\s;]+)\s*;" % key, txt, re.M)
        return m.group(1) if m else None
    return dict(endTime=float(g("endTime")), maxDeltaT=float(g("maxDeltaT")),
                adjustTimeStep=g("adjustTimeStep"))


def _time_dirs(case_dir):
    out = []
    for d in os.listdir(case_dir):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?", d) \
           and os.path.isdir(os.path.join(case_dir, d)):
            out.append(d)
    return sorted(out, key=float)


def completion_check(case_dir):
    """All-or-nothing. Returns (ok, clauses dict)."""
    c = {}
    log = os.path.join(case_dir, "log.rhoCentralFoam")

    # C1 -- rc == 0, recorded on disk by the launcher.
    rc_path = os.path.join(case_dir, "run_rc.txt")
    c["C1_rc_zero"] = (os.path.exists(rc_path)
                       and open(rc_path).read().strip() == "0")

    if not os.path.exists(log):
        c["C2_end_line"] = c["C3_last_time_is_endTime"] = False
        c["C4_fields_present"] = c["C5_log_step_integrity"] = False
        c["C6_age_guard"] = False
        c["ran_before_found"] = "log absent -- check could not run"
        return False, c

    txt = open(log, "r", errors="replace").read()

    # C2 -- an End line.
    c["C2_end_line"] = bool(re.search(r"^End\s*$", txt, re.M))

    # C5 (adapted) -- log step integrity. The literal rule's
    # "ExecutionTime count == endTime" is a STEADY-iteration clause; this is a
    # transient adjustable-timestep solver, where the step count is not endTime.
    # The equivalent invariant is that the log is not truncated mid-step:
    # one ExecutionTime line per Time line.
    n_time = len(re.findall(r"^Time = ", txt, re.M))
    n_exec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    c["C5_log_step_integrity"] = (n_time == n_exec and n_time > 0)
    c["_n_time_lines"] = n_time
    c["_n_exec_lines"] = n_exec

    # C3 -- last written time == endTime (within one maxDeltaT, because
    # adjustTimeStep is on and the last step lands inside one dt of endTime).
    ctrl = _read_control(case_dir)
    tds = [d for d in _time_dirs(case_dir) if float(d) > 0.0]
    if not tds:
        c["C3_last_time_is_endTime"] = False
        c["_last_time"] = None
    else:
        last = tds[-1]
        c["_last_time"] = float(last)
        c["_endTime"] = ctrl["endTime"]
        c["C3_last_time_is_endTime"] = abs(float(last) - ctrl["endTime"]) <= ctrl["maxDeltaT"]
        m = re.findall(r"^Time = ([0-9.eE+-]+)", txt, re.M)
        c["_log_final_time"] = float(m[-1]) if m else None
        if c["_log_final_time"] is None or abs(c["_log_final_time"] - float(last)) > 1e-9:
            c["C3_last_time_is_endTime"] = False

    # C4 -- fields present at the last written time.
    if tds:
        d = os.path.join(case_dir, tds[-1])
        missing = [f for f in REQUIRED_FIELDS if not os.path.exists(os.path.join(d, f))]
        c["C4_fields_present"] = not missing
        c["_missing_fields"] = missing
    else:
        c["C4_fields_present"] = False

    # C6 -- THE AGE GUARD. Every field at the last time must be NEWER than the
    # case's own 0/ directory. Reference taken as the LATEST mtime anywhere in
    # 0/ (stricter than the rule's 0/T, declared in the pre-registration).
    zero = os.path.join(case_dir, "0")
    if tds and os.path.isdir(zero):
        zmt = max(os.path.getmtime(os.path.join(zero, f)) for f in os.listdir(zero))
        d = os.path.join(case_dir, tds[-1])
        ages = {}
        ok = True
        for f in REQUIRED_FIELDS:
            p = os.path.join(d, f)
            if not os.path.exists(p):
                ok = False
                continue
            ages[f] = os.path.getmtime(p) - zmt
            if ages[f] <= 0:
                ok = False
        c["C6_age_guard"] = ok
        c["_age_margin_s"] = {k: round(v, 3) for k, v in ages.items()}
    else:
        c["C6_age_guard"] = False

    c["ran_before_found"] = "checked"
    ok = all(c[k] for k in c if k.startswith("C"))
    return ok, c


# ---------------------------------------------------------------------------
# 3. Planted-zero controls (standing rule 3)
# ---------------------------------------------------------------------------

def _linfit_beta(pts):
    """Byte-for-byte the fit the frozen 2026-07-28 runners use."""
    xk, yk = pts[:, 0], pts[:, 1]
    A = np.vstack([xk, np.ones_like(xk)]).T
    m_slope, c0 = np.linalg.lstsq(A, yk, rcond=None)[0]
    return math.degrees(math.atan(m_slope)), float(m_slope)


def pz_surface_pressure(raw_path):
    """PZ-1. Plant a KNOWN additive offset into the surface-pressure column of a
    COPY of the case's own artifact, read it back with the same reader, and
    REFUSE if the reader cannot see it."""
    arr = np.loadtxt(raw_path, comments="#")
    base = float(np.mean(arr[:, 3]))
    planted = arr.copy()
    planted[:, 3] += PLANT_P
    with tempfile.NamedTemporaryFile("w", suffix=".raw", delete=False) as fh:
        np.savetxt(fh, planted)
        tmp = fh.name
    back = np.loadtxt(tmp, comments="#")
    os.unlink(tmp)
    seen = float(np.mean(back[:, 3])) - base
    if abs(seen - PLANT_P) > PLANT_TOL_ABS:
        refuse("PZ-1 surface-pressure reader could not see its planted %.6e "
               "(saw %.6e) in %s" % (PLANT_P, seen, raw_path))
    return dict(control="PZ-1_surface_pressure_reader", plant=PLANT_P,
                seen=seen, artifact=raw_path, passed=True)


def pz_shock_detector(find_fn, name):
    """PZ-2. Hand the frozen shock detector a SYNTHETIC sample line carrying a
    density step at a KNOWN location, and REFUSE if it cannot find it. This is
    the control that shows the detector can see a non-zero at all."""
    n = 800
    y = np.linspace(0.0, 1.0, n)
    y_plant = PLANT_STEP_FRAC
    rho = np.where(y < y_plant, 2.5, 1.0)          # density DROP going outward,
    rho = rho + 0.0 * y                            # which is what both detectors
    T = 1.0 + 0.3 * (rho - 1.0)                    # look for
    p = 1.0 + 0.9 * (rho - 1.0)
    dat = np.column_stack([y, T, p, rho])
    with tempfile.NamedTemporaryFile("w", suffix=".xy", delete=False) as fh:
        np.savetxt(fh, dat)
        tmp = fh.name
    got = find_fn(tmp)
    os.unlink(tmp)
    if isinstance(got, tuple):
        got = got[0]
    if got is None:
        refuse("PZ-2 (%s) shock detector returned None on a planted step" % name)
    spacing = 1.0 / (n - 1)
    if abs(float(got) - y_plant) > 2.0 * spacing:
        refuse("PZ-2 (%s) shock detector could not see a planted step at "
               "y=%.6f (returned %.6f, spacing %.6f)"
               % (name, y_plant, float(got), spacing))
    return dict(control="PZ-2_shock_detector_%s" % name, plant_y=y_plant,
                seen_y=float(got), sample_spacing=spacing, passed=True)


def pz_beta_fit(shock_pts, beta_stored_deg):
    """PZ-3. Re-derive beta INDEPENDENTLY from the stored shock locus, assert it
    reproduces the runner's stored value, then plant a KNOWN slope increment and
    assert the fit moves by exactly the amount trigonometry demands."""
    pts = np.asarray(shock_pts, dtype=float)
    if len(pts) <= 3:
        refuse("PZ-3 shock locus has %d points; the frozen fit needs >3" % len(pts))
    fit_pts = pts[1:]                              # excl-first fit, as frozen
    beta_re, m = _linfit_beta(fit_pts)
    if abs(beta_re - beta_stored_deg) > 1e-6:
        refuse("PZ-3 independent re-derivation of beta (%.9f) does not reproduce "
               "the runner's stored value (%.9f)" % (beta_re, beta_stored_deg))
    planted = fit_pts.copy()
    planted[:, 1] = planted[:, 1] + PLANT_SLOPE * planted[:, 0]
    beta_planted, _ = _linfit_beta(planted)
    expect = math.degrees(math.atan(m + PLANT_SLOPE))
    if abs(beta_planted - expect) > PLANT_TOL_DEG:
        refuse("PZ-3 beta fit could not see its planted slope %.6e "
               "(expected %.9f deg, got %.9f deg)"
               % (PLANT_SLOPE, expect, beta_planted))
    return dict(control="PZ-3_beta_fit", plant_slope=PLANT_SLOPE,
                beta_rederived_deg=beta_re, beta_planted_deg=beta_planted,
                beta_planted_expected_deg=expect, passed=True)


def pz_force_reader(force_path, z_thickness, q1, chord, cd_stored):
    """PZ-4. Re-derive cd INDEPENDENTLY from the primary force.dat, assert it
    reproduces the runner's stored value, then plant a KNOWN force increment and
    assert cd moves by exactly the amount the definition demands."""
    def read_fx(path):
        lines = [l for l in open(path) if not l.startswith("#") and l.strip()]
        return float(lines[-1].split()[1])

    fx = read_fx(force_path)
    cd_re = 2.0 * (fx / z_thickness) / (q1 * chord)
    if abs(cd_re - cd_stored) > 1e-12 * max(1.0, abs(cd_stored)):
        refuse("PZ-4 independent re-derivation of cd (%.12e) does not reproduce "
               "the runner's stored value (%.12e)" % (cd_re, cd_stored))
    lines = open(force_path).read().rstrip("\n").split("\n")
    body = [l for l in lines if not l.startswith("#") and l.strip()]
    parts = body[-1].split()
    parts[1] = repr(float(parts[1]) + PLANT_FX)
    with tempfile.NamedTemporaryFile("w", suffix=".dat", delete=False) as fh:
        fh.write("\n".join(body[:-1] + [" ".join(parts)]) + "\n")
        tmp = fh.name
    fx_p = read_fx(tmp)
    os.unlink(tmp)
    cd_p = 2.0 * (fx_p / z_thickness) / (q1 * chord)
    expect = cd_re + 2.0 * (PLANT_FX / z_thickness) / (q1 * chord)
    if abs(cd_p - expect) > 1e-12 * max(1.0, abs(expect)):
        refuse("PZ-4 force reader could not see its planted %.6e "
               "(expected cd %.12e, got %.12e)" % (PLANT_FX, expect, cd_p))
    return dict(control="PZ-4_force_reader", plant_Fx=PLANT_FX,
                cd_rederived=cd_re, cd_planted=cd_p, cd_planted_expected=expect,
                artifact=force_path, passed=True)


# ---------------------------------------------------------------------------
# 4. Roache triple gating (standing rule 5)
# ---------------------------------------------------------------------------

def roache(f_coarse, f_medium, f_fine, r=GRID_REFINEMENT_RATIO):
    """Classify a grid triple. f1 = fine, f2 = medium, f3 = coarse.

    Returns the convergence ratio R = (f2-f1)/(f3-f2), the class, the observed
    order at dim=2 and at dim=3 (which differ by exactly 1.5, VERIFICATION
    charter 3.1), and the GCI -- which is None unless the triple CONVERGES.
    """
    f1, f2, f3 = float(f_fine), float(f_medium), float(f_coarse)
    d_fine = f2 - f1       # medium -> fine increment
    d_coarse = f3 - f2     # coarse -> medium increment
    out = dict(triple_coarse_medium_fine=[f3, f2, f1],
               increment_coarse_to_medium=d_coarse,
               increment_medium_to_fine=d_fine,
               refinement_ratio_h=r)
    if d_coarse == 0.0 and d_fine == 0.0:
        out.update(R=None, klass="EXACT", p_dim2=None, p_dim3=None, gci_fine_pct=None)
        return out
    if d_coarse == 0.0:
        out.update(R=None, klass="STAGNANT", p_dim2=None, p_dim3=None, gci_fine_pct=None)
        return out
    R = d_fine / d_coarse
    out["R"] = R
    if R == 0.0:
        out.update(klass="STAGNANT", p_dim2=None, p_dim3=None, gci_fine_pct=None)
        return out
    if R < 0.0:
        klass = "OSCILLATORY"
    elif R >= 1.0:
        klass = "DIVERGENT"
    else:
        klass = "CONVERGING"
    out["klass"] = klass
    if klass == "CONVERGING":
        p2 = math.log(1.0 / R) / math.log(r)
        out["p_dim2"] = p2
        out["p_dim3"] = p2 * 1.5
        out["gci_fine_pct"] = 100.0 * GCI_FS * abs(d_fine / f1) / (r ** p2 - 1.0)
    else:
        # Never quote a GCI on a non-monotone triple (standing rule 5).
        out["p_dim2"] = None
        out["p_dim3"] = None
        out["gci_fine_pct"] = None
        # The order the naive fit WOULD have produced, printed beside the class
        # so a reader can see what was refused, per rule 5's "both orders".
        if R > 0:
            out["p_dim2_refused"] = math.log(1.0 / R) / math.log(r)
            out["p_dim3_refused"] = out["p_dim2_refused"] * 1.5
    return out


def apply_gate(dev_pct, band_pct, triple):
    """Standing rule 5 order of operations. The triple can only turn a PASS or a
    GATE FAIL INTO NOT A RESULT, never the reverse."""
    band_verdict = "PASS" if abs(dev_pct) <= band_pct else "GATE FAIL"
    if triple is None:
        return band_verdict, "no grid triple -- band only, no discretization-error estimate"
    if triple["klass"] != "CONVERGING":
        return "NOT A RESULT", "grid triple is %s (R=%s)" % (
            triple["klass"], "n/a" if triple["R"] is None else "%.4f" % triple["R"])
    return band_verdict, "grid triple CONVERGING, p(dim=2)=%.3f, GCI(fine)=%.3f%%" % (
        triple["p_dim2"], triple["gci_fine_pct"])


# ---------------------------------------------------------------------------
# 5. Case loading
# ---------------------------------------------------------------------------

def load_case(case_dir):
    rj = os.path.join(case_dir, "result.json")
    if not os.path.exists(rj):
        return None
    d = json.load(open(rj))
    mj = os.path.join(case_dir, "meta.json")
    d["_meta"] = json.load(open(mj)) if os.path.exists(mj) else {}
    d["_dir"] = case_dir
    return d


def latest_sub(path_glob):
    hits = sorted(glob.glob(path_glob))
    return hits[-1] if hits else None


# ---------------------------------------------------------------------------
# 6. Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg-commit", required=True,
                    help="sha of the commit that froze this grading path")
    ap.add_argument("--root", default=os.path.join(HERE, "runs"))
    ap.add_argument("--out", default=os.path.join(HERE, "F3_CONVERSION_GRADED.json"))
    a = ap.parse_args()

    freeze = verify_frozen_against_commit(a.prereg_commit)

    from run_wedge_case import find_shock_y
    from run_cone_case import find_shock_r

    controls = [pz_shock_detector(find_shock_y, "wedge_find_shock_y"),
                pz_shock_detector(find_shock_r, "cone_find_shock_r")]

    report = dict(family="F3", conversion="F3_CONVERSION_PREREGISTRATION.md",
                  grading_path_freeze=freeze, planted_zero_controls=controls,
                  bands=dict(surface_pressure_pct=BAND_SURFACE_PRESSURE_PCT,
                             shock_angle_pct=BAND_SHOCK_ANGLE_PCT,
                             wave_drag_pct=BAND_WAVE_DRAG_PCT),
                  runs={}, gates={})

    # ---- collect every run -------------------------------------------------
    spec = [
        ("wedge", "M2.0_th15",     ("coarse", "medium", "fine")),
        ("wedge", "M3.0_th15",     ("fine",)),
        ("wedge", "M2.5_th10",     ("fine",)),
        ("cone",  "M2.35_th10",    ("coarse", "medium", "fine")),
        ("diamond", "M2.0_eps7p125", ("coarse", "medium", "fine")),
        ("diamond", "M2.5_eps5",     ("fine",)),
    ]
    # ------------------------------------------------------------------
    # AMENDMENT 2 REPAIR (2026-08-25), under VERIFICATION_CHARTER 2d.1.
    # ONE CONSTRUCTOR, ONE SCHEMA.  Previously report["runs"][key] was built at two
    # sites with DIFFERENT key sets -- the PENDING branch (run directory absent) wrote
    # no ``core_s`` -- and the summary read ``core_s`` across every entry, so the
    # grader raised KeyError on the one state section 7 GUARANTEES: a wave the
    # pre-wave budget check refuses to launch.  The cap fired exactly as registered
    # and the grader crashed on it having fired (L-322).
    #
    # Adding ``core_s`` to the short branch would patch the symptom and leave the next
    # divergent key waiting.  The defect is TWO SITES THAT CAN DRIFT APART, so there is
    # now exactly one factory and every entry carries every key.  An unlaunched run has
    # NO COST -- that is a fact to REPRESENT (core_s=None), not an error to avoid.
    # No gate, threshold, cap or label is altered by this change.
    # ------------------------------------------------------------------
    def run_entry(status, completion=None, core_s=None, note=None):
        """The ONLY constructor for a report["runs"] entry.  Single schema."""
        return dict(status=status, completion=completion, core_s=core_s, note=note)

    cases = {}
    for fam, pair, levels in spec:
        for lvl in levels:
            cd = os.path.join(a.root, fam, pair, lvl)
            key = "%s/%s/%s" % (fam, pair, lvl)
            if not os.path.isdir(cd):
                report["runs"][key] = run_entry(
                    "PENDING",
                    note="run directory does not exist -- not launched")
                continue
            ok, clauses = completion_check(cd)
            d = load_case(cd)
            report["runs"][key] = run_entry(
                "COMPLETE" if ok else "INCOMPLETE",
                completion=clauses,
                core_s=None if d is None else round(
                    d.get("t_mesh_s", 0) + d.get("t_run_s", 0)
                    + d.get("t_sample_s", 0), 2))
            if ok and d is not None:
                cases[key] = d

    def get(key):
        return cases.get(key)

    def triple_of(fam, pair, extract):
        c, m, f = [get("%s/%s/%s" % (fam, pair, l)) for l in ("coarse", "medium", "fine")]
        if None in (c, m, f):
            return None
        return roache(extract(c), extract(m), extract(f))

    # ---- G-F3-1 / G-F3-2 : wedge ------------------------------------------
    g1, g2 = {}, {}
    wedge_pairs = [("M2.0_th15", "wedge_M2.0_th15.0", True),
                   ("M3.0_th15", "wedge_M3.0_th15.0", False),
                   ("M2.5_th10", "wedge_M2.5_th10.0", False)]
    for pair, ex, has_triple in wedge_pairs:
        fine = get("wedge/%s/fine" % pair)
        if fine is None:
            g1[pair] = dict(verdict="PENDING", note="fine run absent or incomplete")
            g2[pair] = dict(verdict="PENDING", note="fine run absent or incomplete")
            continue
        raw = latest_sub(os.path.join(fine["_dir"], "postProcessing",
                                      "surfaceSampleDict", "*", "*p*.raw"))
        if raw is None:
            refuse("wedge %s fine: surface-pressure artifact missing" % pair)
        controls.append(pz_surface_pressure(raw))
        controls.append(pz_beta_fit(fine["shock_pts"], fine["beta_computed_deg"]))

        p_ex = EXACT[ex]["p2_p1"]
        dev_p = 100.0 * (fine["p_wall_mean"] - p_ex) / p_ex
        tri_p = triple_of("wedge", pair, lambda d: d["p_wall_mean"]) if has_triple else None
        v, why = apply_gate(dev_p, BAND_SURFACE_PRESSURE_PCT, tri_p)
        g1[pair] = dict(verdict=v, measured=fine["p_wall_mean"], exact=p_ex,
                        deviation_pct=dev_p, band_pct=BAND_SURFACE_PRESSURE_PCT,
                        triple=tri_p, basis=why)

        b_ex = EXACT[ex]["beta_deg"]
        dev_b = 100.0 * (fine["beta_computed_deg"] - b_ex) / b_ex
        tri_b = triple_of("wedge", pair, lambda d: d["beta_computed_deg"]) if has_triple else None
        v, why = apply_gate(dev_b, BAND_SHOCK_ANGLE_PCT, tri_b)
        g2[pair] = dict(verdict=v, measured=fine["beta_computed_deg"], exact=b_ex,
                        deviation_pct=dev_b, band_pct=BAND_SHOCK_ANGLE_PCT,
                        triple=tri_b, basis=why,
                        secondary_all_station_fit_deg=fine["beta_all_stations_deg"],
                        secondary_all_station_dev_pct=100.0 * (
                            fine["beta_all_stations_deg"] - b_ex) / b_ex,
                        detector_quantization_1sigma_pct=beta_quantization_pct(fine))
    report["gates"]["G-F3-1_wedge_surface_pressure"] = g1
    report["gates"]["G-F3-2_wedge_shock_angle"] = g2

    # ---- G-F3-3 / G-F3-4 : cone -------------------------------------------
    fine = get("cone/M2.35_th10/fine")
    ex = EXACT["cone_M2.35_thc10.0"]
    if fine is None:
        report["gates"]["G-F3-3_cone_surface_pressure"] = dict(verdict="PENDING")
        report["gates"]["G-F3-4_cone_shock_angle"] = dict(verdict="PENDING")
    else:
        raw = latest_sub(os.path.join(fine["_dir"], "postProcessing",
                                      "surfaceSampleDict", "*", "*p*.raw"))
        if raw is None:
            refuse("cone fine: surface-pressure artifact missing")
        controls.append(pz_surface_pressure(raw))
        controls.append(pz_beta_fit(fine["shock_pts"], fine["beta_computed_deg"]))

        dev_p = 100.0 * (fine["p_wall_mean"] - ex["pc_p1"]) / ex["pc_p1"]
        tri_p = triple_of("cone", "M2.35_th10", lambda d: d["p_wall_mean"])
        v, why = apply_gate(dev_p, BAND_SURFACE_PRESSURE_PCT, tri_p)
        report["gates"]["G-F3-3_cone_surface_pressure"] = dict(
            verdict=v, measured=fine["p_wall_mean"], exact=ex["pc_p1"],
            deviation_pct=dev_p, band_pct=BAND_SURFACE_PRESSURE_PCT,
            triple=tri_p, basis=why)

        dev_b = 100.0 * (fine["beta_computed_deg"] - ex["beta_deg"]) / ex["beta_deg"]
        tri_b = triple_of("cone", "M2.35_th10", lambda d: d["beta_computed_deg"])
        v, why = apply_gate(dev_b, BAND_SHOCK_ANGLE_PCT, tri_b)
        report["gates"]["G-F3-4_cone_shock_angle"] = dict(
            verdict=v, measured=fine["beta_computed_deg"], exact=ex["beta_deg"],
            deviation_pct=dev_b, band_pct=BAND_SHOCK_ANGLE_PCT,
            triple=tri_b, basis=why,
            secondary_all_station_fit_deg=fine["beta_all_stations_deg"],
            secondary_all_station_dev_pct=100.0 * (
                fine["beta_all_stations_deg"] - ex["beta_deg"]) / ex["beta_deg"],
            detector_quantization_1sigma_pct=beta_quantization_pct(fine))

    # ---- G-F3-5 : diamond --------------------------------------------------
    g5 = {}
    for pair, exk, has_triple in [("M2.0_eps7p125", "diamond_M2.0_eps7.125", True),
                                  ("M2.5_eps5", "diamond_M2.5_eps5.0", False)]:
        fine = get("diamond/%s/fine" % pair)
        if fine is None:
            g5[pair] = dict(verdict="PENDING", note="fine run absent or incomplete")
            continue
        fdat = latest_sub(os.path.join(fine["_dir"], "postProcessing",
                                       "forces1", "*", "force.dat"))
        if fdat is None:
            refuse("diamond %s fine: force.dat missing" % pair)
        q1 = 0.5 * 1.4 * 1.0 * fine["M"] ** 2
        controls.append(pz_force_reader(fdat, 0.01, q1, fine["_meta"]["c"],
                                        fine["cd_computed"]))
        cd_ex = EXACT[exk]["cd"]
        dev = 100.0 * (fine["cd_computed"] - cd_ex) / cd_ex
        tri = triple_of("diamond", pair, lambda d: d["cd_computed"]) if has_triple else None
        v, why = apply_gate(dev, BAND_WAVE_DRAG_PCT, tri)
        g5[pair] = dict(verdict=v, measured=fine["cd_computed"], exact=cd_ex,
                        deviation_pct=dev, band_pct=BAND_WAVE_DRAG_PCT,
                        triple=tri, basis=why)
    report["gates"]["G-F3-5_diamond_wave_drag"] = g5

    # AMENDMENT 2: an unlaunched run has no cost.  .get() rather than [] so a future
    # entry missing the key is ALSO tolerated -- the summary must never be the thing
    # that decides whether a registered outcome can be represented.
    total_core_s = sum((v.get("core_s") or 0.0) for v in report["runs"].values())
    report["actual_core_minutes"] = round(total_core_s / 60.0, 4)
    report["planted_zero_controls"] = controls

    with open(a.out, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({k: v for k, v in report.items()
                      if k in ("gates", "actual_core_minutes")}, indent=2))
    print("\nwritten: %s" % a.out)


def beta_quantization_pct(case):
    """The detector's own 1-sigma quantization floor on beta, from MESH GEOMETRY
    ONLY (no CFD value enters). Reported as a diagnostic beside every beta row;
    it is NOT a band and never moves a verdict."""
    m = case.get("_meta", {})
    try:
        if "H" in m and "Lramp" in m:
            span, ny, L = m["H"], m["ny"], m["Lramp"]
        elif "R" in m and "x_max" in m:
            span, ny, L = m["R"], m["nr"], m["x_max"] - m.get("x_min", 0.0)
        else:
            return None
        dy = span / float(ny)
        xs = np.linspace(0.12, 0.88, 6) * L
        xf = xs[1:]
        sigma = dy / math.sqrt(12.0)
        sig_slope = sigma / (math.sqrt(len(xf)) * float(np.std(xf)))
        beta = case["beta_computed_deg"]
        mm = math.tan(math.radians(beta))
        return 100.0 * math.degrees(sig_slope / (1.0 + mm * mm)) / beta
    except Exception:
        return None


if __name__ == "__main__":
    main()
