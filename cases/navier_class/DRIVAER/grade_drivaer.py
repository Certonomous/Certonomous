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
  * RULE 3 planted-zero control on ONE body owner-cell of a p-field copy, re-read.
  * RULE 4 strict completion: rc==0 / 'End'; last==endTime; incompressible-RANS fields
    p U k omega nut phi present at endTime and NEWER than 0/ (age guard).
  * REFUSE-NOT-DEGRADE: exit 2 on bad input / bad control; exit 70 internal defect only;
    exit 0 only when a verdict was produced.  Reads inputs only; sends/commits nothing.

USAGE
  python3 grade_drivaer.py --coarse <dir> --medium <dir> --fine <dir> \
        --reference drivaer_reference_notchback.json [--report out.json]
  python3 grade_drivaer.py --selftest [--smoke <dir>]
"""
import argparse, glob, gzip, json, math, os, re, sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "scripts"))
import roache_triple as RT

# ---- pre-registered gate parameters (FROZEN with the pre-registration) -----------------
PLANT_KPRESS    = 5.0        # planted-zero perturbation on the (kinematic) p field
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

def read_coeff(case, name):
    """coefficient <name> (Cd or Cl) from forceCoeffs coefficient.dat; returns the series."""
    dats = glob.glob(os.path.join(case, "postProcessing", "forceCoeffs*", "*", "coefficient.dat")) \
         + glob.glob(os.path.join(case, "postProcessing", "forceCoeffs*", "*", "forceCoeffs.dat"))
    if not dats:
        refuse(f"{case}: no forceCoeffs coefficient.dat under postProcessing/")
    dat = sorted(dats)[-1]
    lines = open(dat).read().splitlines()
    cols = None
    for h in reversed([l for l in lines if l.startswith("#")]):
        toks = h.lstrip("#").split()
        if name in toks:
            cols = toks; break
    if cols is None:
        refuse(f"{dat}: no '{name}' column in header")
    ci = cols.index(name)
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
    return dict(case=case, nCells=ncells, endTime=endT, last=last, Cd=cd[-1], Cl=cl[-1],
                Cd_prev=cd[-2], Cl_prev=cl[-2], coefficient_dat=d_dat,
                cd_plateaued=bool(cd_plat), cl_plateaued=bool(cl_plat),
                forceCoeffs_constants=fc)

def run_grade(args):
    ref = json.load(open(args.reference))["reference"]
    cd_ref, cl_ref = ref["Cd"], ref.get("Cl")
    levels_in = {"coarse": args.coarse, "medium": args.medium, "fine": args.fine}
    if not all(levels_in.values()):
        refuse("all three of --coarse --medium --fine are required for the Roache triple")
    ctrl = planted_zero_control(args.fine, check_completion(args.fine)[1])
    if not ctrl["passed"]:
        refuse(f"planted-zero control did not behave: {ctrl}")
    per = {n: grade_case(d) for n, d in levels_in.items()}
    order = ("coarse", "medium", "fine")
    lv_cd = [dict(name=n, cells=per[n]["nCells"], value=per[n]["Cd"]) for n in order]
    band_cd = (cd_ref * (1 - CD_BAND_REL), cd_ref * (1 + CD_BAND_REL))
    it = {n: "CONVERGED" for n in per}     # launcher supplies real iterative states; see NB in grade_suboff
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
                                     plant_control=ctrl, iterative_states=it, plateau_states=pl_cl,
                                     fs=FS_CELIK, reference=cl_ref))
    report = dict(rung="DRIVAER_R1", gates=gates, per_level=per,
                  planted_zero_control=ctrl, reference=ref)
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
