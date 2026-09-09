#!/usr/bin/env python3
"""grade_drivaer.py -- EXACT-tier grader for Navier-class Case 7 rung R1 (DRIVAER),
the DrivAer notchback (Ford OCDA) external-aero DRAG (and LIFT) coefficient parity
against the DrivAerML scale-resolving CFD reference (Ashton et al. 2024,
arXiv:2408.11969v2, title-page verified 2026-09-09; PDF outside git at
/home/ubuntu/certonomous-runs/reference_pdfs/benchmark_test_cases/).

STATUS: DRAFT / UNFROZEN, and BLOCKED-geometry (a lead, not a terminal verdict): no
DrivAer STL is on disk yet (search of cases/, models/, mission-output/ and the large
stores returned only 'driver' scripts).  This grader stands ready; the RUN it grades
cannot start until a provenance-verified DrivAer notchback STL lands.  The
pre-registration is verification/campaign/DRIVAER_R1_PREREGISTRATION.md.

REFERENCE TIER: CODE-VERIFIED (rank 2).  DrivAerML is a scale-resolving CFD dataset
(hybrid RANS-LES), a CODE reference -- NOT experimental.  A DrivAer result graded here
reproduces a code reference and carries the disavowal 'NOT experiment-validated'.  If
an AutoCFD-workshop EXPERIMENTAL Cd is title-verified later, the tier may be upgraded
to bounded-agreement; that is a completion-time registry action of the verification
team, not this grader's.

WHAT IT GRADES  (both decided ONLY through the Roache triple; CLAUDE.md rule 5)
  * Gate V1 -- vehicle drag coefficient Cd (PRIMARY), from the solver's forceCoeffs
    coefficient.dat, on the REGISTERED magUInf / lRef / Aref / rhoInf (asserted on disk).
  * Gate V2 -- vehicle lift coefficient Cl (SECONDARY), same source; ABSOLUTE band
    because Cl is small and sign-sensitive.
  Triple via the SHARED instrument scripts/roache_triple.py grade_ladder (no P_MIN /
  STAGNANT_FLOOR redefined -- MESH_STANDARD sec.10.5).  Non-CONVERGING -> NOT A RESULT;
  CONVERGING -> PASS inside band else GATE FAIL, GCI at Fs=1.25 printed.

NON-NEGOTIABLES  (identical discipline to grade_suboff.py)
  * RULE 3 planted-zero controls -- the GATE READER has its own: (i) primary, PLANT
    PLANT_COEFF into the last row of a COPY of the finest coefficient.dat for Cd and Cl
    and re-read through read_coeff (the parser the verdict comes from); (ii) secondary,
    PLANT PLANT_KPRESS into ONE body owner-cell of a p-field copy, re-read.  Refuse
    (exit 2) unless each reader sees its plant.
  * RULE 4 strict completion: rc==0 read from an rc sidecar / DONE marker (NOT an 'End'
    line -- setsid parent returns 0); 'End' also required; last==endTime; ExecutionTime
    count == round(endTime/deltaT); incompressible-RANS fields p U k omega nut phi at
    endTime and NEWER than 0/ (age guard).
  * RULE 5 iterative convergence READ from log.simpleFoam, never defaulted.
  * REFUSE-NOT-DEGRADE: exit 2 on bad input / bad control; exit 70 internal defect only;
    exit 0 only when a verdict was produced.  Reads inputs only; sends/commits nothing.

USAGE
  python3 grade_drivaer.py --coarse <dir> --medium <dir> --fine <dir> \
        --reference drivaer_reference_notchback.json [--report out.json]
  python3 grade_drivaer.py --selftest [--smoke <dir>]
"""
import argparse, glob, gzip, json, math, os, re, shutil, sys, tempfile

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "scripts"))
import roache_triple as RT

# ---- pre-registered gate parameters (FROZEN with the pre-registration) -----------------
PLANT_KPRESS    = 5.0        # planted-zero perturbation on the (kinematic) p field
PLANT_COEFF     = 0.05       # planted-zero perturbation on the coefficient.dat Cd/Cl reader
CD_BAND_REL     = 0.10       # Gate V1: |Cd_cfd - Cd_ref| <= 10% of Cd_ref
CL_BAND_ABS     = 0.05       # Gate V2: |Cl_cfd - Cl_ref| <= 0.05 (absolute; Cl is small)
FS_CELIK        = 1.25
PLATEAU_TOL_REL = 0.005
BODY_PATCH      = "body"     # the vehicle wall patch group drag is integrated on
# registered forceCoeffs constants -- DrivAerML setup (arXiv:2408.11969v2, p.5-6)
MAG_U_INF       = 38.889     # m/s  (DrivAerML freestream)
L_REF           = 2.786      # m    (wheelbase; DrivAerML characteristic length)
A_REF           = 2.17       # m2   (DrivAerML reference frontal area)
RHO_INF         = 1.225      # kg/m3 (air; CONFIRM against DrivAerML rho at freeze)
# Re_L = U*L/nu = 7.19e6 (DrivAerML), incompressible (M ~ 0.11)

EXIT_REFUSE, EXIT_DEFECT = 2, 70
def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): " + msg + "\n"); sys.exit(EXIT_REFUSE)
def defect(msg):
    sys.stderr.write("INTERNAL DEFECT (exit 70): " + msg + "\n"); sys.exit(EXIT_DEFECT)

# ---------------------------------------------------------------------------------------
def _read(path):
    if os.path.exists(path):
        return open(path, "r", errors="replace").read()
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt", errors="replace").read()
    return None

def parse_internal_scalar(path):
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

def body_owner_cells(case):
    """Owner cells of every wall face whose patch name contains BODY_PATCH (the DrivAer
    body group may be split into several patches: body, mirrors, wheels, underbody)."""
    bnd = parse_boundary(case); own = parse_owner(case); cells = []
    matched = [p for p in bnd if BODY_PATCH in p.lower()]
    if not matched:
        refuse(f"no patch whose name contains '{BODY_PATCH}' in {case}")
    for p in matched:
        nF, sF = bnd[p]
        if sF + nF > len(own):
            refuse(f"{p} faces exceed owner list in {case}")
        cells.extend(own[sF:sF+nF])
    return cells, matched

# ---------------------------------------------------------------------------------------
FIELDS      = ("p", "U", "k", "omega", "nut", "phi")
RES_TOL     = 1.0e-4                       # registered residualControl target
ITER_FIELDS = ("p", "Ux", "Uy", "Uz", "k", "omega")

def _ctrl_scalar(case, key):
    txt = _read(os.path.join(case, "system/controlDict"))
    if txt is None:
        refuse(f"no controlDict in {case}")
    m = re.search(rf"\b{key}\s+([-\deE.+]+)\s*;", txt)
    if not m:
        refuse(f"no {key} in {case}/system/controlDict")
    return float(m.group(1))

def read_endtime(case):  return _ctrl_scalar(case, "endTime")
def read_deltat(case):   return _ctrl_scalar(case, "deltaT")

def primary_log(case):
    logs = glob.glob(os.path.join(case, "log.simpleFoam*")) + glob.glob(os.path.join(case, "log*simple*"))
    if not logs:
        refuse(f"{case}: no simpleFoam log")
    return sorted(logs)[-1]

def read_rc(case):
    """rc captured INSIDE the detached wrapper (setsid-parent-returns-zero lesson)."""
    for cand in (glob.glob(os.path.join(case, "rc")) + glob.glob(os.path.join(case, "*.rc"))
                 + glob.glob(os.path.join(case, "DONE*"))):
        t = _read(cand) or ""
        m = re.search(r"rc[=:\s]+(-?\d+)", t) or re.fullmatch(r"\s*(-?\d+)\s*", t)
        if m:
            return int(m.group(1)), cand
    return None, None

def time_dirs(case):
    ts = [d for d in os.listdir(case)
          if re.fullmatch(r"\d+(\.\d+)?", d) and os.path.isdir(os.path.join(case, d)) and d != "0"]
    return sorted(ts, key=float)

def read_iterative_state(case):
    """rule-5 clause-1: per-level iterative convergence READ from log.simpleFoam, never
    defaulted.  CONVERGED iff 'SIMPLE solution converged' OR every monitored field's FINAL
    Initial residual is below RES_TOL (Initial, not Final -- the W3 gate-(b) test)."""
    logtxt = _read(primary_log(case)) or ""
    if re.search(r"SIMPLE solution converged", logtxt):
        return "CONVERGED", dict(via="SIMPLE solution converged line")
    finals = {}
    for f in ITER_FIELDS:
        hits = re.findall(rf"Solving for {f},\s*Initial residual\s*=\s*([-\d.eE+]+)", logtxt)
        if hits:
            finals[f] = float(hits[-1])
    if not finals:
        return "NOT_CONVERGED", dict(why="no Initial-residual lines parsed from the log")
    worst = max(finals.values())
    return ("CONVERGED" if worst < RES_TOL else "NOT_CONVERGED"), \
           dict(final_initial_residuals=finals, res_tol=RES_TOL, worst=worst)

def check_completion(case):
    endT = read_endtime(case); dt = read_deltat(case)
    logtxt = _read(primary_log(case)) or ""
    rc, rc_src = read_rc(case)
    if rc is None:
        refuse(f"{case}: no rc sidecar/DONE marker carrying rc -- rc must be captured "
               "inside the detached wrapper, not inferred from an 'End' line")
    if rc != 0:
        refuse(f"{case}: rc={rc} (from {rc_src}) -- not a clean exit")
    if not (logtxt.rstrip().endswith("End") or "\nEnd\n" in logtxt):
        refuse(f"{case}: no 'End' line in the simpleFoam log")
    ts = time_dirs(case)
    if not ts:
        refuse(f"{case}: no time directories after 0")
    last = ts[-1]
    if abs(float(last) - endT) > 1e-9 * max(1.0, abs(endT)):
        refuse(f"{case}: last time {last} != endTime {endT}")
    n_exec = len(re.findall(r"ExecutionTime\s*=", logtxt))
    want = round(endT / dt)
    if n_exec != want:
        refuse(f"{case}: ExecutionTime count {n_exec} != round(endTime/deltaT)={want}")
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
def assert_forcecoeffs_constants(case):
    txt = _read(os.path.join(case, "system/controlDict"))
    blob = (txt or "") + (_read(os.path.join(case, "system", "forceCoeffs")) or "")
    if not blob:
        refuse(f"no controlDict/forceCoeffs in {case}")
    def _get(key):
        m = re.search(rf"\b{key}\s+([-\deE.+]+)\s*;", blob)
        return float(m.group(1)) if m else None
    got = {k: _get(k) for k in ("magUInf", "lRef", "Aref", "rhoInf")}
    want = {"magUInf": MAG_U_INF, "lRef": L_REF, "Aref": A_REF, "rhoInf": RHO_INF}
    for k, v in want.items():
        if got[k] is None:
            refuse(f"{case}: forceCoeffs constant {k} not found on disk")
        if abs(got[k] - v) > 1e-4 * max(1.0, abs(v)):
            refuse(f"{case}: forceCoeffs {k}={got[k]} != registered {v} -- wrong normalisation")
    return got

def _dat_and_ci(dat, name):
    lines = open(dat).read().splitlines()
    cols = None
    for h in reversed([l for l in lines if l.startswith("#")]):
        toks = h.lstrip("#").split()
        if name in toks:
            cols = toks; break
    if cols is None:
        refuse(f"{dat}: no '{name}' column in header")
    return lines, cols.index(name)

def read_coeff(case, name, dat_path=None):
    """coefficient <name> (Cd or Cl) from forceCoeffs coefficient.dat; returns (dat, series).
    dat_path overrides the glob (used by the coefficient-parser planted control)."""
    if dat_path:
        dat = dat_path
    else:
        dats = glob.glob(os.path.join(case, "postProcessing", "forceCoeffs*", "*", "coefficient.dat")) \
             + glob.glob(os.path.join(case, "postProcessing", "forceCoeffs*", "*", "forceCoeffs.dat"))
        if not dats:
            refuse(f"{case}: no forceCoeffs coefficient.dat under postProcessing/")
        dat = sorted(dats)[-1]
    lines, ci = _dat_and_ci(dat, name)
    vals = []
    for l in lines:
        if l and not l.startswith("#"):
            r = l.split()
            if len(r) > ci:
                try: vals.append(float(r[ci]))
                except ValueError: pass
    if len(vals) < 2:
        refuse(f"{dat}: fewer than two {name} rows")
    return dat, vals

def coefficient_plant_control(case, name):
    """RULE 3 on the ACTUAL GATE READER.  Perturb the last-row <name> of a COPY of the
    finest coefficient.dat by PLANT_COEFF, re-read through read_coeff (the parser the
    verdict comes from), require the returned last value to move by PLANT_COEFF."""
    dat, series = read_coeff(case, name)
    before = series[-1]
    lines, ci = _dat_and_ci(dat, name)
    di = max(i for i, l in enumerate(lines) if l and not l.startswith("#") and len(l.split()) > ci)
    toks = lines[di].split(); toks[ci] = repr(float(toks[ci]) + PLANT_COEFF)
    lines2 = list(lines); lines2[di] = " ".join(toks)
    tmp = tempfile.mkdtemp(prefix="drivaer_plant_")
    try:
        p = os.path.join(tmp, "coefficient.dat")
        open(p, "w").write("\n".join(lines2) + "\n")
        after = read_coeff(case, name, dat_path=p)[1][-1]
        delta = after - before
        return dict(passed=bool(abs(delta - PLANT_COEFF) <= 1e-9 + 1e-6 * abs(PLANT_COEFF)),
                    planted=PLANT_COEFF, reader=f"read_coeff({name},coefficient.dat)",
                    artifact=dat, coefficient=name, before=before, after=after, reader_delta=delta)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ---------------------------------------------------------------------------------------
def body_mean_pressure(case, time, pv=None):
    cells, _ = body_owner_cells(case)
    if pv is None:
        pv = parse_internal_scalar(os.path.join(case, str(time), "p"))
    if pv is None:
        refuse(f"{case}/{time}/p uniform -- no field to read")
    if any(c >= len(pv) for c in cells):
        refuse(f"{case}: a body owner-cell index exceeds the p field length")
    vals = [pv[c] for c in cells]
    return sum(vals) / len(vals), len(vals)

def planted_zero_control(case, time):
    cells, patches = body_owner_cells(case)
    pv = parse_internal_scalar(os.path.join(case, str(time), "p"))
    if pv is None:
        refuse(f"{case}/{time}/p uniform -- cannot run the planted control")
    base, n = body_mean_pressure(case, time, pv=pv)
    pv2 = list(pv); pv2[cells[0]] += PLANT_KPRESS
    seen, _ = body_mean_pressure(case, time, pv=pv2)
    delta = seen - base; expected = PLANT_KPRESS / n
    ok = abs(delta - expected) < 0.02 * expected
    return dict(passed=bool(ok), planted=PLANT_KPRESS, reader="body_mean_pressure",
                artifact=os.path.join(case, str(time), "p"), patches=patches,
                base_mean_p=base, seen_mean_p=seen, reader_delta=delta,
                expected_delta=expected, n_body_cells=n)

# ---------------------------------------------------------------------------------------
def grade_case(case):
    endT, last = check_completion(case)
    fc = assert_forcecoeffs_constants(case)
    d_dat, cd = read_coeff(case, "Cd")
    _, cl = read_coeff(case, "Cl")
    cd_plat = abs(cd[-1] - cd[-2]) <= PLATEAU_TOL_REL * abs(cd[-1]) if cd[-1] else False
    cl_plat = abs(cl[-1] - cl[-2]) <= max(PLATEAU_TOL_REL * abs(cl[-1]), 1e-4)
    ncells = len(parse_owner(case))
    it_state, it_detail = read_iterative_state(case)   # rule-5 clause-1, READ not defaulted
    return dict(case=case, nCells=ncells, endTime=endT, last=last, Cd=cd[-1], Cl=cl[-1],
                Cd_prev=cd[-2], Cl_prev=cl[-2], coefficient_dat=d_dat,
                cd_plateaued=bool(cd_plat), cl_plateaued=bool(cl_plat),
                iterative_state=it_state, iterative_detail=it_detail,
                forceCoeffs_constants=fc)

def run_grade(args):
    ref = json.load(open(args.reference))["reference"]
    cd_ref, cl_ref = ref["Cd"], ref.get("Cl")
    levels_in = {"coarse": args.coarse, "medium": args.medium, "fine": args.fine}
    if not all(levels_in.values()):
        refuse("all three of --coarse --medium --fine are required for the Roache triple")
    # RULE 3 controls on the finest, BEFORE trusting any read: the p-field reader AND
    # read_coeff (the parser the VERDICT comes from), on Cd and, if graded, Cl.
    last_fine = check_completion(args.fine)[1]
    ctrl_field = planted_zero_control(args.fine, last_fine)
    if not ctrl_field["passed"]:
        refuse(f"p-field planted-zero control did not behave: {ctrl_field}")
    ctrl_cd = coefficient_plant_control(args.fine, "Cd")
    if not ctrl_cd["passed"]:
        refuse(f"coefficient.dat Cd (gate-reader) planted-zero control did not behave: {ctrl_cd}")
    ctrl_cl = coefficient_plant_control(args.fine, "Cl") if cl_ref is not None else None
    if ctrl_cl is not None and not ctrl_cl["passed"]:
        refuse(f"coefficient.dat Cl (gate-reader) planted-zero control did not behave: {ctrl_cl}")
    ctrl = ctrl_cd   # gate-reader control is the primary passed to grade_ladder
    per = {n: grade_case(d) for n, d in levels_in.items()}
    order = ("coarse", "medium", "fine")
    lv_cd = [dict(name=n, cells=per[n]["nCells"], value=per[n]["Cd"]) for n in order]
    band_cd = (cd_ref * (1 - CD_BAND_REL), cd_ref * (1 + CD_BAND_REL))
    # rule-5 clause-1: iterative-convergence state READ from each level's log, never defaulted
    it = {n: per[n]["iterative_state"] for n in per}
    pl_cd = {n: ("PLATEAUED" if per[n]["cd_plateaued"] else "NOT_PLATEAUED") for n in per}
    gate_cd = RT.grade_ladder("V1 vehicle drag coefficient Cd", lv_cd, dim=3, band=band_cd,
                              plant_control=ctrl, iterative_states=it, plateau_states=pl_cd,
                              fs=FS_CELIK, reference=cd_ref)
    gates = [gate_cd]
    if cl_ref is not None:
        lv_cl = [dict(name=n, cells=per[n]["nCells"], value=per[n]["Cl"]) for n in order]
        band_cl = (cl_ref - CL_BAND_ABS, cl_ref + CL_BAND_ABS)
        pl_cl = {n: ("PLATEAUED" if per[n]["cl_plateaued"] else "NOT_PLATEAUED") for n in per}
        gates.append(RT.grade_ladder("V2 vehicle lift coefficient Cl", lv_cl, dim=3, band=band_cl,
                                     plant_control=ctrl_cl, iterative_states=it, plateau_states=pl_cl,
                                     fs=FS_CELIK, reference=cl_ref))
    report = dict(rung="DRIVAER_R1", gates=gates, per_level=per,
                  planted_zero_control_Cd=ctrl_cd, planted_zero_control_Cl=ctrl_cl,
                  planted_zero_control_field=ctrl_field, reference=ref)
    print(json.dumps(report, indent=2, default=str))
    if args.report:
        json.dump(report, open(args.report, "w"), indent=2, default=str)
    return 0 if all(g.get("verdict") in ("PASS", "GATE FAIL", "NOT A RESULT") for g in gates) else EXIT_DEFECT

def run_selftest(args):
    ctrl_ok = dict(passed=True, planted=PLANT_KPRESS, reader="selftest",
                   reader_delta=PLANT_KPRESS, artifact="synthetic")
    print("== CONVERGING inside band -> PASS ==")
    lv = [dict(name="coarse", cells=3_000_000, value=0.305),
          dict(name="medium", cells=6_000_000, value=0.292),
          dict(name="fine",   cells=12_000_000, value=0.285)]
    r = RT.grade_ladder("selftest Cd", lv, dim=3, band=(0.28*0.9, 0.28*1.1), plant_control=ctrl_ok,
                        iterative_states={l["name"]:"CONVERGED" for l in lv},
                        plateau_states={l["name"]:"PLATEAUED" for l in lv}, fs=FS_CELIK, reference=0.28)
    assert r["verdict"] == "PASS", r
    print(f"  verdict={r['verdict']} order={r.get('order')} GCI%={r.get('GCI_pct')}")
    print("== CONVERGING outside band -> GATE FAIL ==")
    lv2 = [dict(name="coarse", cells=3_000_000, value=0.365),
           dict(name="medium", cells=6_000_000, value=0.352),
           dict(name="fine",   cells=12_000_000, value=0.345)]
    r2 = RT.grade_ladder("selftest Cd hi", lv2, dim=3, band=(0.28*0.9, 0.28*1.1), plant_control=ctrl_ok,
                         iterative_states={l["name"]:"CONVERGED" for l in lv2},
                         plateau_states={l["name"]:"PLATEAUED" for l in lv2}, fs=FS_CELIK, reference=0.28)
    assert r2["verdict"] == "GATE FAIL", r2
    print(f"  verdict={r2['verdict']} (value {r2['value']} outside band {r2['band']})")
    print("== missing plant control -> refuse ==")
    try:
        RT.grade_ladder("noctrl", lv, dim=3, band=(0.252,0.308), plant_control=None,
                        iterative_states={l["name"]:"CONVERGED" for l in lv},
                        plateau_states={l["name"]:"PLATEAUED" for l in lv})
        assert False
    except (SystemExit, RT.Refusal):
        print("  refused as required (no plant control)")
    print("== coefficient.dat (gate-reader) planted control on a synthetic file (Cd & Cl) ==")
    tmp = tempfile.mkdtemp(prefix="drivaer_selftest_")
    try:
        pp = os.path.join(tmp, "postProcessing", "forceCoeffs1", "0"); os.makedirs(pp)
        open(os.path.join(pp, "coefficient.dat"), "w").write(
            "# Force coefficients\n# Time Cd Cs Cl\n"
            "1000 0.285 0.0 -0.050\n2000 0.286 0.0 -0.051\n")
        for nm in ("Cd", "Cl"):
            c = coefficient_plant_control(tmp, nm)
            assert c["passed"], c
            print(f"  {nm}: reader saw planted {c['planted']} ({c['before']} -> {c['after']})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if args.smoke:
        ts = time_dirs(args.smoke)
        if not ts:
            refuse("smoke case has no time dirs for the control")
        c = planted_zero_control(args.smoke, ts[-1])
        print("  " + json.dumps(c, default=str))
        if not c["passed"]:
            refuse("planted-zero control FAILED on smoke case")
        print("  planted-zero control PASSED")
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
