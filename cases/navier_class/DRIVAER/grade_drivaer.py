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
# The VEHICLE is defined by EXCLUDING the registered domain patches, never by a
# substring of the vehicle's own names.  BODY_PATCH = "body" was measured on the built
# fine mesh to match 18 of 47 vehicle patches and 21.98 m2 of 34.67 m2 -- it MISSED
# every wheel, tyre, mirror, the entire exhaust system, the powertrain and all the
# Notchback roof/trunk/window surfaces (29 patches, 12.70 m2, 37% of the wetted area).
# Its own docstring claimed it covered "body, mirrors, wheels, underbody"; "body" is
# not a substring of "Mirrors1" or "Tiresfront", so the code never did what the comment
# said.  A control that silently covers 63% of the surface looks like coverage.
DOMAIN_PATCHES  = ("inlet", "outlet", "floorslip", "floornoslip",
                   "top", "sideminus", "sideplus")

# ---- THERE ARE NO REGISTERED CONSTANTS IN THIS FILE, DELIBERATELY --------------------
# magUInf / lRef / Aref / rhoInf / Cd / Cl used to be literals here (38.889 / 2.786 /
# 2.17 / 1.225 / 0.28 / None).  They drifted out of step with the registration the
# moment the registration settled on run_466's PER-GEOMETRY reference convention
# (Aref 2.298, lRef 2.79, rhoInf 1.0), and a grader holding the other convention
# would have REFUSED a correctly-configured case -- the assertion working exactly as
# designed, against the wrong target.  Two places holding one number is one place too
# many.  Every one of them is now READ from the pinned reference file and every one is
# MANDATORY: see resolve_reference().
REQUIRED_REF_KEYS = {
    "magUInf": "magUInf_m_s",
    "lRef":    "L_ref_m",
    "Aref":    "Aref_m2",
    "rhoInf":  "rho_kg_m3",
}
REQUIRED_GATE_KEYS = ("Cd", "Cl")   # BOTH gates are armed.  Neither may be absent.

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
    """Owner cells of every wall face on the VEHICLE -- i.e. every patch that is not
    one of the registered DOMAIN_PATCHES.  Defined by exclusion on purpose: see the
    measurement beside DOMAIN_PATCHES."""
    bnd = parse_boundary(case); own = parse_owner(case); cells = []
    matched = [p for p in bnd if p.lower() not in DOMAIN_PATCHES]
    if not matched:
        refuse(f"no vehicle patch in {case}: every patch is a registered domain "
               f"patch {DOMAIN_PATCHES}")
    unknown = [p for p in bnd if p.lower() in DOMAIN_PATCHES]
    if len(unknown) != len(DOMAIN_PATCHES):
        refuse(f"{case}: expected all {len(DOMAIN_PATCHES)} registered domain patches "
               f"{DOMAIN_PATCHES} on the mesh, found {sorted(unknown)}. A missing or "
               f"renamed domain patch would silently be counted as vehicle surface.")
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
def resolve_reference(path):
    """Read every gate parameter from the pinned reference file.  REFUSE on any absent
    one.  A GATE THAT DATA CAN DISARM IS NOT A GATE.

    The predecessor of this function did not exist: the caller wrote
        cd_ref, cl_ref = ref["Cd"], ref.get("Cl")
    and then guarded the whole V2 gate and its planted control with
        if cl_ref is not None:
    so a reference file carrying "Cl": null -- which the shipped one did, with the note
    "Leave null to skip gate V2 until pinned" -- SILENTLY DROPPED gate V2 and its
    control, and the grader still exited 0 with a verdict.  A limb that disarms itself
    on missing data and says nothing about it is the failure this refuses.
    """
    try:
        doc = json.load(open(path))
    except Exception as e:
        refuse(f"reference {path}: unreadable ({e})")
    if "reference" not in doc:
        refuse(f"reference {path}: no 'reference' object")
    ref = doc["reference"]
    out = {}
    for name, key in REQUIRED_REF_KEYS.items():
        v = ref.get(key)
        if v is None:
            refuse(f"reference {path}: '{key}' is absent or null.  It sets the "
                   f"forceCoeffs constant {name!r} that the on-disk assertion compares "
                   f"against; without it the assertion cannot be evaluated, and an "
                   f"unevaluated assertion is not a passed one.")
        out[name] = float(v)
    for key in REQUIRED_GATE_KEYS:
        v = ref.get(key)
        if v is None:
            refuse(f"reference {path}: gate reference '{key}' is absent or null.  "
                   f"Gate V{'1' if key == 'Cd' else '2'} cannot be evaluated.  This is a "
                   f"REFUSAL and not a skip: the gate does not disarm because its "
                   f"reference is missing.")
        out[key] = float(v)
    return out


def assert_forcecoeffs_constants(case, want):
    txt = _read(os.path.join(case, "system/controlDict"))
    blob = (txt or "") + (_read(os.path.join(case, "system", "forceCoeffs")) or "")
    if not blob:
        refuse(f"no controlDict/forceCoeffs in {case}")
    def _get(key):
        m = re.search(rf"\b{key}\s+([-\deE.+]+)\s*;", blob)
        return float(m.group(1)) if m else None
    got = {k: _get(k) for k in REQUIRED_REF_KEYS}
    for k in REQUIRED_REF_KEYS:
        v = want[k]
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
                n_vehicle_patches=len(patches),
                artifact=os.path.join(case, str(time), "p"), patches=patches,
                base_mean_p=base, seen_mean_p=seen, reader_delta=delta,
                expected_delta=expected, n_body_cells=n)

# ---------------------------------------------------------------------------------------
def grade_case(case, want):
    endT, last = check_completion(case)
    fc = assert_forcecoeffs_constants(case, want)
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
    want = resolve_reference(args.reference)      # REFUSES on any absent parameter
    cd_ref, cl_ref = want["Cd"], want["Cl"]
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
    ctrl_cl = coefficient_plant_control(args.fine, "Cl")   # unconditional: V2 is armed
    if not ctrl_cl["passed"]:
        refuse(f"coefficient.dat Cl (gate-reader) planted-zero control did not behave: {ctrl_cl}")
    ctrl = ctrl_cd   # gate-reader control is the primary passed to grade_ladder
    per = {n: grade_case(d, want) for n, d in levels_in.items()}
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
    if True:   # V2 is unconditional; the reference cannot disarm it (resolve_reference)
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



# =======================================================================================
# DECLARED NON-CONFORMANCE -- THE CAP TRAVELS WITH THE NUMBER, IN THE JSON.
#
# A mesh failing a hard MESH_STANDARD gate MAY be solved, provided the exceedance is
# registered with its MEASURED values and the result's claim is capped.  What is NOT
# permitted is the number later being cited without the cap.  Prose in a registration
# does not travel with a JSON value into somebody's table -- so the cap is emitted
# here, attached to the number, and it CANNOT be emitted without the measurements
# because both are parsed from the level's own checkMesh artifact or the grader
# refuses.
# =======================================================================================
MESH_STANDARD_SOURCE = "docs/standards/MESH_STANDARD.md"
MESH_STANDARD_LIMITS = {"max_skewness": 4.0, "max_non_ortho": 70.0}
CLAIM_CAP = ("CLAIM CAP -- THIS RESULT IS NOT A CREDENTIAL. The mesh does not meet "
             f"{MESH_STANDARD_SOURCE}. This number MUST NOT be recorded as a "
             "credential, MUST NOT be entered in a matrix as HOLDS or GATE REACHED, "
             "and may appear only as a STATED-LIMITATION row carrying the measured "
             "exceedance below. Citing it without this cap is the failure the "
             "non-conformance ruling exists to prevent.")


def read_mesh_conformance(case):
    """Parse the level's OWN full-flag checkMesh artifact and measure the exceedances.

    REFUSES if the artifact is absent or if a metric cannot be read.  That refusal is
    the point: the non-conformance block cannot be produced without the measured
    values attached to it, so there is no way to emit a capped number whose cap is
    not backed by a measurement, and no way to emit an uncapped number by losing the
    artifact.
    """
    path = os.path.join(case, "log.checkMeshFull")
    txt = _read(path)
    if not txt:
        refuse(f"{case}: no log.checkMeshFull. The full-flag checkMesh artifact is "
               f"required: mesh conformance against {MESH_STANDARD_SOURCE} is measured "
               f"from it, and without it neither conformance nor non-conformance can "
               f"be stated. An unmeasured mesh is not a conforming one.")
    m = re.search(r"Max skewness = ([\d.eE+-]+)", txt)
    if not m:
        refuse(f"{path}: no 'Max skewness' line -- the metric "
               f"{MESH_STANDARD_SOURCE} gates on cannot be read")
    skew = float(m.group(1))
    m = re.search(r"Mesh non-orthogonality Max: ([\d.eE+-]+)", txt)
    if not m:
        refuse(f"{path}: no 'Mesh non-orthogonality Max' line")
    nonortho = float(m.group(1))
    fm = re.search(r"^Failed (\d+) mesh checks\.", txt, re.M)
    failed = int(fm.group(1)) if fm else 0
    nf = re.search(r"([\d]+) highly skew faces detected", txt)
    measured = {"max_skewness": skew, "max_non_ortho": nonortho}
    breaches = []
    for k, limit in MESH_STANDARD_LIMITS.items():
        if measured[k] > limit:
            breaches.append(dict(metric=k, measured=measured[k], threshold=limit,
                                 standard=MESH_STANDARD_SOURCE,
                                 exceedance_factor=measured[k] / limit,
                                 n_faces_affected=int(nf.group(1)) if (
                                     k == "max_skewness" and nf) else None))
    return dict(case=case, artifact=path, measured=measured,
                failed_mesh_checks_full_flags=failed,
                conforms=not breaches, breaches=breaches)


# =======================================================================================
# STAGE A -- the gate this setup can actually support, and NOTHING MORE.
#
# Stage A has NO WALL LAYERS (snappyHexMesh layer addition is defective on this
# geometry) and therefore y+ ~ 2342 / 1171 / 585.  Standard wall functions are
# calibrated for the log layer, y+ ~ 30-300.  On a bluff body whose drag is set by
# boundary-layer separation and base pressure, a Cd from a first cell centre sitting
# out in the wake is NOT A MEASUREMENT OF Cd.
#
# So Stage A DOES NOT ROUTE THROUGH grade_ladder AT ALL:
#   * no Roache triple, no GCI, no observed order -- a y+ varying 4x across levels
#     would measure the wall model changing, not the grid;
#   * two levels, not three, because only two pass the geometry limb -- and
#     grade_ladder refuses fewer than three levels, which is the correct refusal and
#     is why this path is separate rather than a weakened call into it.
# What it CAN check is real: rule-4 completion, the on-disk constants, every planted
# control firing, plateau, and a DELIBERATELY WIDE gross-error band on Cd.
#
# THE Cd BAND IS A DIAGNOSTIC BAND, NOT A VALIDATION GATE.  Its bounds are set from
# what is physically possible for a road car, NOT from the DrivAerML reference: no
# passenger car has Cd below ~0.15 or above ~0.60.  It catches a wrong sign, a wrong
# order of magnitude, a gross Aref blunder and a bluff-body 1.5.  It CANNOT and DOES
# NOT establish agreement with Cd_ref = 0.2758368, and every record it emits says so
# in a field a later reader cannot miss.
# =======================================================================================
CD_DIAG_BAND = (0.15, 0.60)     # physical bounds for a road car; NOT a reference band
CL_DIAG_BAND = (-0.50, 0.50)    # a notchback DrivAer cannot be outside this
NOT_VALIDATION = ("DIAGNOSTIC BAND, NOT A VALIDATION GATE. An in-band value is NOT "
                  "agreement with the DrivAerML reference Cd_ref=0.2758368 and MUST "
                  "NOT be cited as agreement. Stage A has no wall layers, y+ is "
                  "roughly an order of magnitude above the wall-function range, and "
                  "no grid gate (Gate G) is registered for it.")


def _band_verdict(value, band, name):
    lo, hi = band
    ok = (lo <= value <= hi)
    return dict(gate=name, value=value, band=[lo, hi],
                verdict="PASS" if ok else "GATE FAIL",
                interpretation=NOT_VALIDATION)


def run_stage_a(args):
    """Stage A: completion + instrument, plus a gross-error diagnostic band."""
    want = resolve_reference(args.reference)      # REFUSES on any absent parameter
    levels = []
    for spec in args.levels:
        if "=" not in spec:
            refuse(f"--levels takes name=path, got {spec!r}")
        levels.append(tuple(spec.split("=", 1)))
    # STAGE A IS REGISTERED FOR EXACTLY ONE LEVEL, and the count is enforced.
    # One level is coherent here precisely BECAUSE Gate G is not registered: there is
    # no triple to form and no grid verdict on offer, so a second level would buy a
    # grid sensitivity that nothing grades.  The count fell from two to one because
    # the registered geometry-limb floor B2=0.70 was HELD and not moved to admit the
    # level in hand -- medium reads 0.5989 against it.
    if len(levels) != 1:
        refuse(f"Stage A is registered for EXACTLY ONE level (fine); got "
               f"{len(levels)}: {[n for n, _ in levels]}. Two levels would be a grid "
               f"sensitivity pair and three a Roache triple; neither is registered "
               f"for Stage A, and a triple must go through grade_ladder with a "
               f"registered Gate G -- which Stage A deliberately does not have. "
               f"Refusing rather than silently grading extra levels under a "
               f"diagnostic band.")
    finest = levels[-1][1]

    # ---- RULE 3, before anything is trusted; all three controls UNCONDITIONAL --------
    last_fine = check_completion(finest)[1]
    ctrl_field = planted_zero_control(finest, last_fine)
    if not ctrl_field["passed"]:
        refuse(f"p-field planted-zero control did not behave: {ctrl_field}")
    ctrl_cd = coefficient_plant_control(finest, "Cd")
    if not ctrl_cd["passed"]:
        refuse(f"coefficient.dat Cd gate-reader control did not behave: {ctrl_cd}")
    ctrl_cl = coefficient_plant_control(finest, "Cl")
    if not ctrl_cl["passed"]:
        refuse(f"coefficient.dat Cl gate-reader control did not behave: {ctrl_cl}")

    per, conf = {}, {}
    for name, path in levels:
        per[name] = grade_case(path, want)        # rule-4 completion + on-disk constants
        conf[name] = read_mesh_conformance(path)  # REFUSES if the artifact is absent

    # ---- Gate A1: completion and instrument.  This one is a REAL gate. --------------
    bad = []
    for name in per:
        if per[name]["iterative_state"] != "CONVERGED":
            bad.append(f"{name}: iterative state {per[name]['iterative_state']}")
        if not per[name]["cd_plateaued"]:
            bad.append(f"{name}: Cd not plateaued")
        if not per[name]["cl_plateaued"]:
            bad.append(f"{name}: Cl not plateaued")
    gate_a1 = dict(gate="A1 completion and instrument",
                   verdict="PASS" if not bad else "GATE FAIL",
                   failures=bad,
                   checked=["rule-4 completion on every level (rc sidecar, End line, "
                            "last==endTime, field set, ExecutionTime count, age guard)",
                            "forceCoeffs magUInf/lRef/Aref/rhoInf asserted on disk "
                            "against the pinned reference",
                            "planted control on the p-field reader",
                            "planted control on the Cd gate reader",
                            "planted control on the Cl gate reader",
                            "iterative convergence READ from each log",
                            "Cd and Cl plateau"],
                   planted_controls=dict(field=ctrl_field, Cd=ctrl_cd, Cl=ctrl_cl))

    # ---- Gate A2/A3: gross-error diagnostic bands.  NOT validation. -----------------
    cd_fine, cl_fine = per[levels[-1][0]]["Cd"], per[levels[-1][0]]["Cl"]
    gate_a2 = _band_verdict(cd_fine, CD_DIAG_BAND, "A2 Cd gross-error diagnostic band")
    gate_a3 = _band_verdict(cl_fine, CL_DIAG_BAND, "A3 Cl gross-error diagnostic band")

    nonconf = {n: c for n, c in conf.items() if not c["conforms"]}
    cap = None
    if nonconf:
        cap = dict(
            claim_cap=CLAIM_CAP,
            credential_eligible=False,
            matrix_status=("STATED LIMITATION -- not HOLDS, not GATE REACHED, "
                           "not a credential"),
            standard=MESH_STANDARD_SOURCE,
            non_conforming_levels=sorted(nonconf),
            breaches={n: c["breaches"] for n, c in nonconf.items()},
            measured={n: c["measured"] for n, c in nonconf.items()})

    report = dict(rung="DRIVAER_R1_STAGE_A",
                  mesh_conformance=conf,
                  declared_non_conformance=cap,
                  credential_eligible=(cap is None),
                  stage_a_scope=NOT_VALIDATION,
                  gate_G_registered=False,
                  gate_G_absent_because=("y+ ~ 2342/1171/585 without wall layers and "
                                         "varying 4x across levels; a Roache order "
                                         "from that measures the wall model changing, "
                                         "not the grid"),
                  levels=[n for n, _ in levels],
                  gates=[gate_a1, gate_a2, gate_a3],
                  per_level=per, reference=want,
                  reference_Cd_NOT_GATED_AGAINST=want["Cd"],
                  reference_Cl_NOT_GATED_AGAINST=want["Cl"])
    print(json.dumps(report, indent=2, default=str))
    if args.report:
        json.dump(report, open(args.report, "w"), indent=2, default=str)
    return 0


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
    # ===================================================================================
    # ARMING PROOFS.  A gate that has not been SHOWN ABLE TO REFUSE is not armed.
    # The three tests above prove the ladder can READ.  These prove the Cl gate and the
    # on-disk assertion can FIRE and can REFUSE -- which is the property that was
    # actually missing: "Cl": null used to disarm gate V2 in silence.
    # ===================================================================================
    print("== ARMING PROOF 1: an absent Cl reference REFUSES (it must not skip) ==")
    tmp2 = tempfile.mkdtemp(prefix="drivaer_arming_")
    try:
        full = {"reference": {"magUInf_m_s": 38.889, "L_ref_m": 2.79, "Aref_m2": 2.298,
                              "rho_kg_m3": 1.0, "Cd": 0.2758368, "Cl": -0.05357145}}
        good = os.path.join(tmp2, "ref_full.json")
        json.dump(full, open(good, "w"))
        got = resolve_reference(good)
        assert got["Cl"] == -0.05357145 and got["Aref"] == 2.298, got
        print(f"  complete reference resolves: Aref={got['Aref']} lRef={got['lRef']} "
              f"rhoInf={got['rhoInf']} Cd={got['Cd']} Cl={got['Cl']}")
        for drop in ("Cl", "Cd", "Aref_m2", "rho_kg_m3", "L_ref_m", "magUInf_m_s"):
            import copy
            bad = copy.deepcopy(full); bad["reference"][drop] = None
            bpath = os.path.join(tmp2, f"ref_no_{drop}.json")
            json.dump(bad, open(bpath, "w"))
            try:
                resolve_reference(bpath)
                raise AssertionError(f"NOT ARMED: a null {drop} was accepted")
            except SystemExit as e:
                assert e.code == EXIT_REFUSE, (drop, e.code)
                print(f"  null {drop:12s} -> REFUSED (exit {e.code}), not skipped")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    print("== ARMING PROOF 2: the Cl gate FIRES on a planted wrong value ==")
    cl_ref = -0.05357145
    band_cl = (cl_ref - CL_BAND_ABS, cl_ref + CL_BAND_ABS)
    lv_ok = [dict(name="coarse", cells=128_230, value=-0.070),
             dict(name="medium", cells=748_658, value=-0.062),
             dict(name="fine",   cells=5_025_587, value=-0.058)]
    st = dict(iterative_states={l["name"]: "CONVERGED" for l in lv_ok},
              plateau_states={l["name"]: "PLATEAUED" for l in lv_ok})
    r_ok = RT.grade_ladder("arming Cl in band", lv_ok, dim=3, band=band_cl,
                           plant_control=ctrl_ok, fs=FS_CELIK, reference=cl_ref,
                           form="unequal", **st)
    assert r_ok["verdict"] == "PASS", r_ok
    print(f"  in-band  Cl={lv_ok[-1]['value']} -> {r_ok['verdict']}")
    # plant the wrong value into the SAME ladder: only the finest value moves
    lv_bad = [dict(l) for l in lv_ok]
    lv_bad[-1]["value"] = cl_ref + 3.0 * CL_BAND_ABS      # the plant
    r_bad = RT.grade_ladder("arming Cl planted wrong", lv_bad, dim=3, band=band_cl,
                            plant_control=ctrl_ok, fs=FS_CELIK, reference=cl_ref,
                            form="unequal",
                            iterative_states={l["name"]: "CONVERGED" for l in lv_bad},
                            plateau_states={l["name"]: "PLATEAUED" for l in lv_bad})
    assert r_bad["band_verdict"] == "GATE FAIL", r_bad
    print(f"  planted  Cl={lv_bad[-1]['value']:.6f} -> band_verdict={r_bad['band_verdict']} "
          f"(band {r_bad['band']}); the gate moved when the value moved")

    print("== ARMING PROOF 3: the CLAIM CAP is emitted, and cannot be emitted "
          "without the measured values ==")
    tmp3 = tempfile.mkdtemp(prefix="drivaer_cap_")
    try:
        def _mk(name, body):
            d = os.path.join(tmp3, name); os.makedirs(d)
            if body is not None:
                open(os.path.join(d, "log.checkMeshFull"), "w").write(body)
            return d
        good = _mk("conforming",
                   "    Mesh non-orthogonality Max: 41.2 average: 6.1\n"
                   "    Max skewness = 3.5 OK.\n")
        c = read_mesh_conformance(good)
        assert c["conforms"] and not c["breaches"], c
        print(f"  conforming mesh (skew 3.5)  -> conforms=True, no cap")

        bad = _mk("nonconforming",
                  "    Mesh non-orthogonality Max: 64.940718 average: 5.4484841\n"
                  " ***Max skewness = 10.315144, 16 highly skew faces detected\n"
                  "Failed 3 mesh checks.\n")
        c = read_mesh_conformance(bad)
        assert not c["conforms"], c
        b = c["breaches"][0]
        assert b["metric"] == "max_skewness", b
        assert abs(b["measured"] - 10.315144) < 1e-9, b
        assert b["threshold"] == 4.0 and b["n_faces_affected"] == 16, b
        print(f"  non-conforming (skew {b['measured']}) -> breach carries measured="
              f"{b['measured']}, threshold={b['threshold']}, "
              f"faces={b['n_faces_affected']}, factor={b['exceedance_factor']:.3f}")
        for tok in ("NOT A CREDENTIAL", "HOLDS", "GATE REACHED", "STATED-LIMITATION"):
            assert tok in CLAIM_CAP, tok
        print(f"  CLAIM_CAP names all of: NOT A CREDENTIAL / HOLDS / GATE REACHED / "
              f"STATED-LIMITATION")

        # the cap CANNOT be produced without the measurements
        for name, body, why in (
                ("no_artifact", None, "checkMesh artifact absent"),
                ("no_skew", "    Mesh non-orthogonality Max: 41.2 average: 6.1\n",
                 "no Max skewness line"),
                ("no_nonortho", "    Max skewness = 3.5 OK.\n", "no non-orthogonality line")):
            d = _mk(name, body)
            try:
                read_mesh_conformance(d)
                raise AssertionError(f"NOT ARMED: conformance claimed with {why}")
            except SystemExit as e:
                assert e.code == EXIT_REFUSE, (name, e.code)
                print(f"  {why:34s} -> REFUSED (exit {e.code}); "
                      f"no cap and no pass can be emitted unmeasured")
    finally:
        shutil.rmtree(tmp3, ignore_errors=True)

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
    ap.add_argument("--stage-a", action="store_true")
    ap.add_argument("--levels", nargs="+", default=[])
    args = ap.parse_args()
    if args.selftest:
        sys.exit(run_selftest(args))
    if args.stage_a:
        if not (args.levels and args.reference):
            refuse("Stage A needs --levels name=path name=path and --reference")
        sys.exit(run_stage_a(args))
    if not (args.coarse and args.medium and args.fine and args.reference):
        refuse("need --coarse --medium --fine --reference (or --selftest)")
    sys.exit(run_grade(args))

if __name__ == "__main__":
    main()
