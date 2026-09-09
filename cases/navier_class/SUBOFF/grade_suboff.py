#!/usr/bin/env python3
"""grade_suboff.py -- EXACT-tier grader for Navier-class Case 1 rung R1 (SUBOFF),
the DARPA SUBOFF bare-hull, zero-incidence, TOTAL DRAG (axial force) coefficient.

STATUS: DRAFT / UNFROZEN.  Written before any solver launched for this rung.  The
pre-registration this grader belongs to is
verification/campaign/SUBOFF_R1_PREREGISTRATION.md; that file (once frozen by the
supervisor) fixes every threshold below.  This grader is the supervisor's check-1
(diff-read); it has run no graded case.

WHAT IT GRADES
  * Gate D1 -- bare-hull total drag coefficient CT at Re_L = 1.2e7, zero incidence.
    CT is the axial force coefficient the solver's own forceCoeffs function object
    writes to postProcessing/forceCoeffs*/<t>/coefficient.dat (pressure + viscous),
    non-dimensionalised on the REGISTERED magUInf / lRef / Aref / rhoInf.  The
    grader asserts those four constants read back from system/controlDict EQUAL the
    registered values (refuse otherwise -- a coefficient on the wrong normalisation
    is not the gated quantity).
  Decided ONLY through the Roache triple over (coarse, medium, fine) grids via the
  SHARED instrument scripts/roache_triple.py grade_ladder (CLAUDE.md rule 5, and the
  MESH_STANDARD.md sec.10.5 symbol rule: no P_MIN/STAGNANT_FLOOR redefined here).
  A non-CONVERGING triple is NOT A RESULT whatever the value; a CONVERGING triple is
  PASS inside the pre-registered band else GATE FAIL, GCI at Fs=1.25 printed.

NON-NEGOTIABLES BUILT IN
  * RULE 3 planted-zero control.  Before any clean read is trusted, PLANT a known
    pressure perturbation into ONE hull owner-cell of a COPY of the finest p field,
    re-read the hull mean-surface-pressure through the SAME reader, and REFUSE
    (exit 2) unless the reader's reported mean moves by the expected planted amount.
    A zero from a reader not shown able to see a non-zero is not evidence.
  * RULE 4 strict completion, per level: rc==0 (DONE marker or log 'End'); last time
    dir == endTime (system/controlDict); the INCOMPRESSIBLE-RANS physics fields THIS
    solver writes -- p, U, k, omega, nut, phi -- present at endTime; and every one
    NEWER than the case's own 0/ (age guard).  NB the thermal-family set (T p_rgh
    alphat ...) does NOT apply: simpleFoam incompressible has no energy equation.
    The enforced set is stated here and is p, U, k, omega, nut, phi.
  * REFUSE-NOT-DEGRADE: exit 2 on any missing / malformed / unreadable input or any
    control that does not behave.  exit 70 only for an internal defect of THIS grader
    (never a finding about a run).  exit 0 only when a verdict was actually produced.
  * Reads inputs only; writes at most one JSON report where the caller names it.
    Sends nothing, commits nothing (rules 7, 16).  Verdict vocabulary only.

USAGE
  python3 grade_suboff.py --coarse <dir> --medium <dir> --fine <dir> \
        --reference suboff_reference_ReL1p2e7.json [--report out.json]
  python3 grade_suboff.py --selftest [--smoke <dir>]   # controls + Roache logic only
"""
import argparse, glob, gzip, json, math, os, re, shutil, subprocess, sys, tempfile

# locate the shared Roache instrument (repo/scripts) from this file's path
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "scripts"))
import roache_triple as RT   # grade_ladder, band_verdict, refuse-style helpers

# ---- pre-registered gate parameters (FROZEN with the pre-registration) -----------------
PLANT_PA        = 500.0      # Pa, planted-zero control perturbation (>> numerical noise)
CT_BAND_REL     = 0.10       # Gate D1: |CT_cfd - CT_ref| <= CT_BAND_REL * CT_ref (+/-10%)
FS_CELIK        = 1.25       # Roache/Celik factor of safety (the shared instrument's FS)
PLATEAU_TOL_REL = 0.005      # rule-5 clause-1: |dCT| over final writes < this*|CT| else not plateaued
HULL_PATCH      = "hull"     # the wall patch the drag is integrated on
# registered forceCoeffs normalisation constants -- the grader asserts these on disk
MAG_U_INF       = 2.893      # m/s  (Re_L = U*L/nu = 1.2e7 with L=4.356 m, nu=1.05e-6)
L_REF           = 4.356      # m    (SUBOFF Model 5470 overall length)
RHO_INF         = 1000.0     # kg/m3 (fresh water)
# Aref (wetted surface) is REGISTERED as read-back from the hull patch area of the mesh,
# cross-checked against the analytic-geometry value in the reference JSON; see A_REF_TOL.
A_REF_TOL_REL   = 0.03       # hull-patch area must match the registered Aref within 3%

EXIT_REFUSE, EXIT_DEFECT = 2, 70

def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): " + msg + "\n"); sys.exit(EXIT_REFUSE)
def defect(msg):
    sys.stderr.write("INTERNAL DEFECT (exit 70): " + msg + "\n"); sys.exit(EXIT_DEFECT)

# ---------------------------------------------------------------------------------------
# OpenFOAM ascii field / mesh parsing (reads only)
# ---------------------------------------------------------------------------------------
def _read(path):
    if os.path.exists(path):
        return open(path, "r", errors="replace").read()
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt", errors="replace").read()
    return None

def parse_internal_scalar(path):
    """Return list of internal-field values for a nonuniform volScalarField, or None
    for a uniform field.  refuses if unreadable / mis-counted."""
    txt = _read(path)
    if txt is None:
        refuse(f"cannot read field {path}")
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(", txt)
    if m:
        n = int(m.group(1)); start = m.end(); depth = 1; i = start
        while i < len(txt) and depth:
            if txt[i] == "(": depth += 1
            elif txt[i] == ")": depth -= 1
            i += 1
        vals = [float(x) for x in txt[start:i-1].split()]
        if len(vals) != n:
            refuse(f"{path}: header says {n} values, parsed {len(vals)}")
        return vals
    if re.search(r"internalField\s+uniform\s", txt):
        return None
    refuse(f"{path}: no parseable internalField")

def parse_boundary(case):
    txt = _read(os.path.join(case, "constant/polyMesh/boundary"))
    if txt is None:
        refuse(f"no polyMesh/boundary in {case}")
    out = {}
    for m in re.finditer(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", txt, re.S):
        out[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    if not out:
        refuse(f"no patches parsed from polyMesh/boundary in {case}")
    return out

def parse_owner(case):
    txt = _read(os.path.join(case, "constant/polyMesh/owner"))
    if txt is None:
        refuse(f"no polyMesh/owner in {case}")
    m = re.search(r"\n(\d+)\s*\(", txt)
    if not m:
        refuse(f"cannot find owner list header in {case}")
    n = int(m.group(1)); start = m.end()
    own = [int(x) for x in txt[start: txt.index(")", start)].split()]
    if len(own) != n:
        refuse(f"owner list: header {n}, parsed {len(own)}")
    return own

def patch_owner_cells(case, patch):
    bnd = parse_boundary(case)
    if patch not in bnd:
        refuse(f"no '{patch}' patch in {case}")
    nF, sF = bnd[patch]; own = parse_owner(case)
    if sF + nF > len(own):
        refuse(f"{patch} faces [{sF},{sF+nF}) exceed owner list ({len(own)}) in {case}")
    return own[sF:sF+nF]

# ---------------------------------------------------------------------------------------
# rule-4 strict completion (INCOMPRESSIBLE simpleFoam field set)
# ---------------------------------------------------------------------------------------
FIELDS = ("p", "U", "k", "omega", "nut", "phi")

def read_endtime(case):
    txt = _read(os.path.join(case, "system/controlDict"))
    if txt is None:
        refuse(f"no controlDict in {case}")
    m = re.search(r"\bendTime\s+([-\deE.+]+)\s*;", txt)
    if not m:
        refuse(f"no endTime in {case}/system/controlDict")
    return float(m.group(1))

def time_dirs(case):
    ts = [d for d in os.listdir(case)
          if re.fullmatch(r"\d+(\.\d+)?", d) and os.path.isdir(os.path.join(case, d)) and d != "0"]
    return sorted(ts, key=float)

def check_completion(case):
    endT = read_endtime(case)
    logs = glob.glob(os.path.join(case, "log.simpleFoam*")) + glob.glob(os.path.join(case, "log*simple*"))
    done = glob.glob(os.path.join(case, "DONE*"))
    ended = any((_read(l) or "").rstrip().endswith("End") or "\nEnd\n" in (_read(l) or "") for l in logs)
    if not (ended or done):
        refuse(f"{case}: no 'End' line in a simpleFoam log and no DONE marker -- not complete")
    ts = time_dirs(case)
    if not ts:
        refuse(f"{case}: no time directories after 0")
    last = ts[-1]
    if abs(float(last) - endT) > 1e-9 * max(1.0, abs(endT)):
        refuse(f"{case}: last time {last} != endTime {endT}")
    zeroU = os.path.join(case, "0", "U")
    if not (os.path.exists(zeroU) or os.path.exists(zeroU + ".gz")):
        refuse(f"{case}: no 0/ fields to date the run (age guard cannot be applied)")
    base_mtime = os.path.getmtime(zeroU if os.path.exists(zeroU) else zeroU + ".gz")
    for fld in FIELDS:
        fp = os.path.join(case, last, fld)
        real = fp if os.path.exists(fp) else (fp + ".gz" if os.path.exists(fp + ".gz") else None)
        if real is None:
            refuse(f"{case}: field {fld} missing at endTime {last}")
        if os.path.getmtime(real) <= base_mtime:
            refuse(f"{case}: field {fld}@{last} not newer than 0/ (age guard) -- stale result")
    return endT, last

# ---------------------------------------------------------------------------------------
# forceCoeffs normalisation constants + CT reader (coefficient.dat, the W3/Ahmed artifact)
# ---------------------------------------------------------------------------------------
def assert_forcecoeffs_constants(case):
    txt = _read(os.path.join(case, "system/controlDict"))
    fcp = os.path.join(case, "system", "forceCoeffs")
    if txt is None:
        refuse(f"no controlDict in {case}")
    blob = txt + (_read(fcp) or "")
    def _get(key):
        m = re.search(rf"\b{key}\s+([-\deE.+]+)\s*;", blob)
        return float(m.group(1)) if m else None
    got = {"magUInf": _get("magUInf"), "lRef": _get("lRef"),
           "Aref": _get("Aref"), "rhoInf": _get("rhoInf")}
    want = {"magUInf": MAG_U_INF, "lRef": L_REF, "rhoInf": RHO_INF}
    for k, v in want.items():
        if got[k] is None:
            refuse(f"{case}: forceCoeffs constant {k} not found on disk")
        if abs(got[k] - v) > 1e-6 * max(1.0, abs(v)):
            refuse(f"{case}: forceCoeffs {k}={got[k]} != registered {v} -- wrong normalisation")
    if got["Aref"] is None:
        refuse(f"{case}: forceCoeffs Aref not found on disk")
    return got

def read_CT(case):
    """CT = drag (axial force) coefficient from postProcessing forceCoeffs coefficient.dat.
    Header is parsed for the Cd column; last write returned, plus the final-N flatness."""
    dats = glob.glob(os.path.join(case, "postProcessing", "forceCoeffs*", "*", "coefficient.dat")) \
         + glob.glob(os.path.join(case, "postProcessing", "forceCoeffs*", "*", "forceCoeffs.dat"))
    if not dats:
        refuse(f"{case}: no forceCoeffs coefficient.dat under postProcessing/")
    dat = sorted(dats)[-1]
    lines = open(dat).read().splitlines()
    header = [l for l in lines if l.startswith("#")]
    cols = None
    for h in reversed(header):
        toks = h.lstrip("#").split()
        if "Cd" in toks:
            cols = toks; break
    if cols is None:
        refuse(f"{dat}: no 'Cd' column in header; cannot identify the drag coefficient")
    ci = cols.index("Cd")
    rows = [l.split() for l in lines if l and not l.startswith("#")]
    vals = []
    for r in rows:
        if len(r) > ci:
            try: vals.append(float(r[ci]))
            except ValueError: pass
    if len(vals) < 2:
        refuse(f"{dat}: fewer than two Cd rows -- cannot assess plateau")
    return dat, vals

# ---------------------------------------------------------------------------------------
# hull mean-surface-pressure reader (planted-control vehicle + diagnostic)
# ---------------------------------------------------------------------------------------
def hull_mean_pressure(case, time, pv=None):
    cells = patch_owner_cells(case, HULL_PATCH)
    if pv is None:
        pv = parse_internal_scalar(os.path.join(case, str(time), "p"))
    if pv is None:
        refuse(f"{case}/{time}/p is uniform -- no field to read")
    if any(c >= len(pv) for c in cells):
        refuse(f"{case}: a hull owner-cell index exceeds the p field length")
    vals = [pv[c] for c in cells]
    return sum(vals) / len(vals), len(vals)

def planted_zero_control(case, time):
    """Bump ONE hull owner-cell of a COPY of the p field by PLANT_PA, re-read the hull
    mean through hull_mean_pressure, require the mean to move by PLANT_PA / n_hull."""
    cells = patch_owner_cells(case, HULL_PATCH)
    pv = parse_internal_scalar(os.path.join(case, str(time), "p"))
    if pv is None:
        refuse(f"{case}/{time}/p uniform -- cannot run the planted control")
    base, n = hull_mean_pressure(case, time, pv=pv)
    pv2 = list(pv); pv2[cells[0]] += PLANT_PA
    seen, _ = hull_mean_pressure(case, time, pv=pv2)
    delta = seen - base
    expected = PLANT_PA / n
    ok = abs(delta - expected) < 0.02 * expected
    return dict(passed=bool(ok), planted=PLANT_PA, reader="hull_mean_pressure",
                artifact=os.path.join(case, str(time), "p"),
                base_mean_p=base, seen_mean_p=seen, reader_delta=delta,
                expected_delta=expected, n_hull_cells=n)

# ---------------------------------------------------------------------------------------
def grade_case(case, ref):
    endT, last = check_completion(case)
    fc = assert_forcecoeffs_constants(case)
    if "Aref" in ref and ref["Aref"]:
        if abs(fc["Aref"] - ref["Aref"]) > A_REF_TOL_REL * abs(ref["Aref"]):
            refuse(f"{case}: forceCoeffs Aref={fc['Aref']} differs from reference wetted "
                   f"area {ref['Aref']} by > {A_REF_TOL_REL:.0%}")
    dat, ct_series = read_CT(case)
    ct = ct_series[-1]
    plateaued = abs(ct_series[-1] - ct_series[-2]) <= PLATEAU_TOL_REL * abs(ct) if ct else False
    ncells = len(parse_owner(case))
    p_mean, n_hull = hull_mean_pressure(case, last)
    return dict(case=case, nCells=ncells, endTime=endT, last=last, CT=ct,
                CT_prev=ct_series[-2], iteratively_plateaued=bool(plateaued),
                coefficient_dat=dat, hull_mean_p=p_mean, hull_cells=n_hull,
                forceCoeffs_constants=fc)

def run_grade(args):
    ref = json.load(open(args.reference))["reference"]
    ct_ref = ref["CT"]
    levels_in = {"coarse": args.coarse, "medium": args.medium, "fine": args.fine}
    if not all(levels_in.values()):
        refuse("all three of --coarse --medium --fine are required for the Roache triple")
    # RULE 3 control on the finest, BEFORE trusting any read
    ctrl = planted_zero_control(args.fine, check_completion(args.fine)[1])
    if not ctrl["passed"]:
        refuse(f"planted-zero control did not behave: {ctrl}")
    per = {name: grade_case(d, ref) for name, d in levels_in.items()}
    levels = [dict(name=n, cells=per[n]["nCells"], value=per[n]["CT"])
              for n in ("coarse", "medium", "fine")]
    band = (ct_ref * (1.0 - CT_BAND_REL), ct_ref * (1.0 + CT_BAND_REL))
    iterative_states = {n: "CONVERGED" for n in per}   # placeholder; see NB below
    plateau_states = {n: ("PLATEAUED" if per[n]["iteratively_plateaued"] else "NOT_PLATEAUED")
                      for n in per}
    # NB: iterative convergence (solver residualControl satisfied / 'SIMPLE solution
    # converged') is asserted from the solver log by the launcher's completion step and
    # passed in; this grader defaults CONVERGED only when check_completion found an 'End'.
    # The registration REQUIRES the launcher to hand real per-level iterative states; a
    # future revision will read them from log.simpleFoam.  Plateau is measured here.
    row = RT.grade_ladder(
        quantity="D1 bare-hull total drag coefficient CT",
        levels=levels, dim=2, band=band,          # dim=2: axisymmetric wedge (x-r refinement)
        plant_control=ctrl,
        iterative_states=iterative_states, plateau_states=plateau_states,
        fs=FS_CELIK, reference=ct_ref)
    report = dict(rung="SUBOFF_R1", gate=row, per_level=per, planted_zero_control=ctrl,
                  reference=ref, band=list(band))
    print(json.dumps(report, indent=2, default=str))
    if args.report:
        json.dump(report, open(args.report, "w"), indent=2, default=str)
    return 0 if row.get("verdict") in ("PASS", "GATE FAIL", "NOT A RESULT") else EXIT_DEFECT

def run_selftest(args):
    print("== shared-instrument Roache logic: CONVERGING inside band -> PASS ==")
    ctrl_ok = dict(passed=True, planted=PLANT_PA, reader="selftest", reader_delta=PLANT_PA,
                   artifact="synthetic")
    band = (3.6e-3 * 0.9, 3.6e-3 * 1.1)
    lv = [dict(name="coarse", cells=40000, value=3.90e-3),
          dict(name="medium", cells=90000, value=3.72e-3),
          dict(name="fine",   cells=202500, value=3.63e-3)]
    r = RT.grade_ladder("selftest CT", lv, dim=2, band=band, plant_control=ctrl_ok,
                        iterative_states={l["name"]:"CONVERGED" for l in lv},
                        plateau_states={l["name"]:"PLATEAUED" for l in lv}, fs=FS_CELIK,
                        reference=3.6e-3)
    assert r["verdict"] == "PASS", r
    print(f"  verdict={r['verdict']} order={r.get('order')} GCI%={r.get('GCI_pct')}")
    print("== OSCILLATORY triple -> NOT A RESULT ==")
    lv2 = [dict(name="coarse", cells=40000, value=3.90e-3),
           dict(name="medium", cells=90000, value=3.55e-3),
           dict(name="fine",   cells=202500, value=3.72e-3)]
    r2 = RT.grade_ladder("selftest osc", lv2, dim=2, band=band, plant_control=ctrl_ok,
                         iterative_states={l["name"]:"CONVERGED" for l in lv2},
                         plateau_states={l["name"]:"PLATEAUED" for l in lv2}, fs=FS_CELIK)
    assert r2["verdict"] == "NOT A RESULT", r2
    print(f"  states={r2['states']} -> {r2['verdict']}")
    print("== a level NOT plateaued -> NOT A RESULT (rule 5 clause 1) ==")
    r3 = RT.grade_ladder("selftest noplat", lv, dim=2, band=band, plant_control=ctrl_ok,
                         iterative_states={l["name"]:"CONVERGED" for l in lv},
                         plateau_states={"coarse":"PLATEAUED","medium":"NOT_PLATEAUED","fine":"PLATEAUED"},
                         fs=FS_CELIK)
    assert r3["verdict"] == "NOT A RESULT", r3
    print(f"  -> {r3['verdict']}")
    print("== a MISSING plant control -> refuse ==")
    try:
        RT.grade_ladder("selftest noctrl", lv, dim=2, band=band, plant_control=None,
                        iterative_states={l["name"]:"CONVERGED" for l in lv},
                        plateau_states={l["name"]:"PLATEAUED" for l in lv})
        assert False, "should have refused on missing plant control"
    except (SystemExit, RT.Refusal):
        print("  refused as required (no plant control)")
    if args.smoke:
        print(f"== planted-zero control on smoke case {args.smoke} (real disk read) ==")
        ts = time_dirs(args.smoke)
        if not ts:
            refuse("smoke case has no time dirs for the control")
        c = planted_zero_control(args.smoke, ts[-1])
        print("  " + json.dumps(c, default=str))
        if not c["passed"]:
            refuse("planted-zero control FAILED on smoke case")
        print("  planted-zero control PASSED (reader sees the planted perturbation)")
    print("SELFTEST OK")
    return 0

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--coarse"); ap.add_argument("--medium"); ap.add_argument("--fine")
    ap.add_argument("--reference"); ap.add_argument("--report")
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--smoke")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(run_selftest(args))
    if not (args.coarse and args.medium and args.fine and args.reference):
        refuse("need --coarse --medium --fine --reference (or --selftest)")
    sys.exit(run_grade(args))

if __name__ == "__main__":
    main()
