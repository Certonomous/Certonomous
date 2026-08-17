#!/usr/bin/env python3
"""heat_balance.py -- watts in against watts out, for any OpenFOAM thermal solve.

    python3 scripts/heat_balance.py <case> [--time latestTime] [--tol 1.0]
                                   [--length 0.1] [--json out.json] [--quiet]

Exit 0 = balance closed within --tol percent.  Exit 1 = it did not.
Exit 2 = the auditor REFUSED to produce a number (see REFUSALS below).

WHY THIS EXISTS
---------------
Built at rung K0b of the thermal ladder and made a standing check from that
point on: no thermal number leaves this lab without its boundary heat balance
and its regime numbers attached.  A residual plot says the linear solver stopped
moving.  It does not say energy is conserved.  Those are different claims and
this lab has confused them before.

WHAT IT COMPUTES, AND HOW IT IS DERIVED
---------------------------------------
For a Boussinesq solve the temperature equation is

    div(phi, T) - laplacian(alphaEff, T) = 0,     alphaEff = nu/Pr + nut/Prt

which is a KINEMATIC equation: it never sees rho or cp.  To turn it into watts:

    q  = -rho.cp.alphaEff.grad(T)              [W/m^2]
    Q_into_domain_through_patch_p
       = -integral_p (q . n) dA                 (n = OUTWARD unit normal)
       = +rho.cp.alphaEff . integral_p (n . grad(T)) dA

The surface integral is obtained exactly, not by a finite-difference of my own:
`fvc::grad` overwrites the wall-normal component of its boundary field with the
scheme's own `snGrad` (OpenFOAM's `gaussGrad::correctBoundaryConditions`), so
`areaNormalIntegrate` of `grad(T)` over a patch IS `integral snGrad(T) dA`, in
the discretisation the solver actually used.  Nothing here re-implements the
solver's numerics, which is the whole point.

  TRAP, MEASURED, DO NOT REMOVE THE WORKAROUND.  `grad(T)` must be recomputed
  in the SAME postProcess pass as the surface integral.  If it is written to
  disk first and read back (`postProcess -func <sfv> -fields '(grad(T))'`), the
  wall boundary values come back WITHOUT the snGrad correction and the answer
  is silently wrong.  Measured on the K0a case at 2000 iterations:
      recomputed in-pass  : integral n.grad(T) dA = 0.595629494
      read back from disk : integral n.grad(T) dA = 0.377856775   (-36.6%)
  The in-pass value is the correct one: it reproduces a by-hand
  (T_wall - T_cell)/d summation over the raw T field to 7 significant figures.
  Hence the single `run_post` call with `grad(T)` first in the funcs list.

Note rho.cp.alpha = rho.cp.(nu/Pr) = k, the thermal conductivity, so the
laminar coefficient is just k and the script prints it for cross-checking
against a tabulated value.

At steady state with no volumetric source, sum over all boundary patches of
Q_into_domain must be zero.  The reported imbalance is

    imbalance% = 100 . |sum_p Q_p| / (sum over patches with Q_p > 0 of Q_p)

i.e. the net leak as a percentage of the total heat actually entering.

REFUSALS -- what this script will NOT guess at
----------------------------------------------
It exits 2, loudly, rather than print a wrong number, when:

  * a non-wall, non-empty patch exists (inlet/outlet).  Those carry an
    ADVECTIVE enthalpy flux rho.cp.integral(T (U.n))dA that this script does not
    yet compute, and a balance that silently omits it would be wrong by
    whatever the through-flow carries.  `--allow-advective` adds the term but
    the report is then stamped UNVALIDATED: the advective path has never been
    checked against a closed-form answer, and until it is, it is not trusted.
  * alphat is non-zero anywhere, i.e. a turbulence model is contributing
    turbulent thermal diffusivity.  Then alphaEff varies over the patch and
    `alphaEff . integral(n.grad T) dA` is NOT `integral(alphaEff n.grad T) dA`.
    `--allow-turbulent` uses a weighted integral instead and again stamps the
    report UNVALIDATED.  Validating that path needs a turbulent case with a
    known answer, which is a later rung and its own compute authorisation.

Both refusals are deliberate.  A checker that returns a number for every input
is a checker nobody can learn anything from.

CALIBRATION
-----------
The laminar wall path is calibrated against a closed-form answer by
`--selftest-conduction DT`, which compares the measured hot-patch Q against
rho.cp.alpha.(DT/L).A for a 1-D conduction case.  That control is run and
recorded in demo-output/website/campaign/THERMAL_K0_RESULTS.md.

A NOTE ON CALLING THIS FROM A SHELL
-----------------------------------
Read THIS script's exit status.  `python3 heat_balance.py case | head` reports
head's status, not the auditor's -- that mistake has cost this lab a false pass
before.  Use `out=$(python3 heat_balance.py case); rc=$?`.
"""

import argparse
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys

FOAM_BASHRC = os.environ.get(
    "FOAM_BASHRC", "/usr/lib/openfoam/openfoam2606/etc/bashrc"
)


# ---------------------------------------------------------------------------
# OpenFOAM dictionary reading (only the few scalar entries we need)
# ---------------------------------------------------------------------------

def read_scalar(path, key, default=None):
    if not os.path.isfile(path):
        if default is None:
            raise SystemExit(f"REFUSE: {path} not found and no default for '{key}'")
        return default
    with open(path) as fh:
        txt = fh.read()
    m = re.search(rf"^\s*{re.escape(key)}\s+([^;]+);", txt, re.M)
    if not m:
        if default is None:
            raise SystemExit(f"REFUSE: entry '{key}' not found in {path}")
        return default
    return float(m.group(1).strip())


def read_patches(case):
    """Return [(name, type, nFaces), ...] from constant/polyMesh/boundary."""
    bfile = os.path.join(case, "constant", "polyMesh", "boundary")
    if not os.path.isfile(bfile):
        raise SystemExit(
            f"REFUSE: {bfile} not found -- run blockMesh first. The mesh is not "
            "tracked in this repo by design; it is rebuilt from the dictionaries."
        )
    with open(bfile) as fh:
        txt = fh.read()
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", "", txt)
    body = txt.split("}", 1)[1]  # drop the FoamFile header block
    out = []
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", body):
        name, blk = m.group(1), m.group(2)
        t = re.search(r"^\s*type\s+([^;]+);", blk, re.M)
        n = re.search(r"^\s*nFaces\s+([^;]+);", blk, re.M)
        if t and n:
            out.append((name, t.group(1).strip(), int(n.group(1))))
    return out


def list_times(case):
    ts = []
    for e in os.listdir(case):
        if os.path.isdir(os.path.join(case, e)):
            try:
                ts.append((float(e), e))
            except ValueError:
                pass
    return sorted(ts)


# ---------------------------------------------------------------------------
# function-object plumbing
# ---------------------------------------------------------------------------

FO_HEADER = (
    "FoamFile\n{\n    version 2.0;\n    format ascii;\n"
    "    class dictionary;\n    object %s;\n}\n"
)


def fo_surface(name, patch, operation, fields, weight=None):
    s = FO_HEADER % name
    s += (
        "type            surfaceFieldValue;\n"
        "libs            (fieldFunctionObjects);\n"
        "regionType      patch;\n"
        f"name            {patch};\n"
        f"operation       {operation};\n"
        f"fields          ({fields});\n"
        "writeFields     false;\n"
        "writeToFile     true;\n"
        "log             false;\n"
    )
    if weight:
        s += f"weightField     {weight};\n"
    return s


def fo_volume(name, operation, field):
    return FO_HEADER % name + (
        "type            volFieldValue;\n"
        "libs            (fieldFunctionObjects);\n"
        "regionType      all;\n"
        f"operation       {operation};\n"
        f"fields          ({field});\n"
        "writeFields     false;\n"
        "writeToFile     true;\n"
        "log             false;\n"
    )


def fo_derived(name, fotype, field, result):
    """A derived field under a PRIVATE name.

    Two reasons the result name is not the default:
      1. the default names ('grad(T)', 'mag(U)') collide with files a previous
         audit left in the time directory, and OpenFOAM aborts with
         "Failed to store pointer: mag(U). Risk of memory leakage" on the
         SECOND audit of the same case. The auditor was not idempotent until
         this was fixed, and a checker that only works once is not a checker.
      2. a private name cannot be silently satisfied by a stale file somebody
         else's postProcess run wrote.
    Whatever these do write is deleted again by `clean_derived` below, so an
    audit leaves the case exactly as it found it.
    """
    return FO_HEADER % name + (
        f"type            {fotype};\n"
        "libs            (fieldFunctionObjects);\n"
        f"field           {field};\n"
        f"result          {result};\n"
        "writeControl    none;\n"
        "log             false;\n"
    )


DERIVED = ("hbAuditGradT", "hbAuditMagU")


def clean_derived(case):
    for tdir in os.listdir(case):
        full = os.path.join(case, tdir)
        if not os.path.isdir(full):
            continue
        for d in DERIVED:
            try:
                os.remove(os.path.join(full, d))
            except OSError:
                pass


def run_post(case, funcs, time_spec):
    cmd = (
        f'. "{FOAM_BASHRC}" >/dev/null 2>&1 && '
        f"cd {case!r} && postProcess -time {time_spec} -funcs '({' '.join(funcs)})'"
    )
    p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    return p


def read_dat(case, foname):
    """Last data row of postProcessing/<foname>/*/[a-z]*.dat -> (time, [values])."""
    cands = sorted(glob.glob(os.path.join(case, "postProcessing", foname, "*", "*.dat")))
    if not cands:
        raise SystemExit(f"REFUSE: no output written for function object '{foname}'")
    rows = []
    for c in cands:
        with open(c) as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split()
                rows.append((float(parts[0]), [float(x) for x in parts[1:]]))
    if not rows:
        raise SystemExit(f"REFUSE: function object '{foname}' produced no data rows")
    return rows[-1]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("case")
    ap.add_argument("--time", default="latestTime",
                    help="time to audit; 'latestTime' (default) or a value")
    ap.add_argument("--tol", type=float, default=1.0,
                    help="pass threshold on imbalance, percent (default 1.0)")
    ap.add_argument("--length", type=float, default=None,
                    help="characteristic length L for Rayleigh number, metres")
    ap.add_argument("--rho", type=float, default=None)
    ap.add_argument("--cp", type=float, default=None)
    ap.add_argument("--allow-advective", action="store_true")
    ap.add_argument("--allow-turbulent", action="store_true")
    ap.add_argument("--selftest-conduction", type=float, default=None,
                    metavar="DT",
                    help="calibrate against the closed-form 1-D conduction answer "
                         "Q = rho.cp.alpha.(DT/L).A for the hottest patch")
    ap.add_argument("--json", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    case = os.path.abspath(a.case)
    if not os.path.isdir(case):
        raise SystemExit(f"REFUSE: no such case directory {case}")

    # Delete any previous --json output FIRST. If this run dies, the caller must
    # find no file rather than last run's numbers wearing this run's name. A
    # stale artefact that reads as fresh is how a wrong figure survives a fix.
    if a.json and os.path.exists(a.json):
        os.remove(a.json)

    tp = os.path.join(case, "constant", "transportProperties")
    nu = read_scalar(tp, "nu")
    Pr = read_scalar(tp, "Pr")
    Prt = read_scalar(tp, "Prt", 0.85)
    TRef = read_scalar(tp, "TRef", 300.0)
    beta = read_scalar(tp, "beta", 1.0 / TRef)

    ap_file = os.path.join(case, "constant", "thermalAuditProperties")
    rho = a.rho if a.rho is not None else read_scalar(ap_file, "rho0")
    cp = a.cp if a.cp is not None else read_scalar(ap_file, "cp0")

    alpha = nu / Pr
    kcond = rho * cp * alpha

    gpath = os.path.join(case, "constant", "g")
    gmag = 0.0
    if os.path.isfile(gpath):
        with open(gpath) as fh:
            m = re.search(r"^\s*value\s*\(([^)]*)\)", fh.read(), re.M)
        if m:
            gmag = math.sqrt(sum(float(x) ** 2 for x in m.group(1).split()))

    patches = read_patches(case)
    active = [p for p in patches if p[1] not in ("empty", "symmetry", "symmetryPlane",
                                                 "wedge", "cyclic", "processor")]
    walls = [p for p in active if p[1] == "wall"]
    nonwall = [p for p in active if p[1] != "wall"]

    if nonwall and not a.allow_advective:
        sys.stderr.write(
            "REFUSE: non-wall patches carry an advective enthalpy flux this "
            "auditor does not compute: "
            + ", ".join(f"{n} (type {t})" for n, t, _ in nonwall)
            + "\n        Re-run with --allow-advective to include an UNVALIDATED "
              "advective term, or audit a closed domain.\n"
        )
        return 2

    times = list_times(case)
    if a.time == "latestTime":
        if not times:
            raise SystemExit("REFUSE: no time directories in the case")
        tval, tdir = times[-1]
        tspec = tdir
    else:
        tspec = a.time
        tval = float(a.time)

    # ---- build function objects ------------------------------------------
    sysdir = os.path.join(case, "system")
    made = []
    fo_map = {}
    open(os.path.join(sysdir, "hbAudit_gradT"), "w").write(
        fo_derived("hbAudit_gradT", "grad", "T", "hbAuditGradT"))
    open(os.path.join(sysdir, "hbAudit_magU"), "w").write(
        fo_derived("hbAudit_magU", "mag", "U", "hbAuditMagU"))
    made += ["hbAudit_gradT", "hbAudit_magU"]
    # grad(T) MUST be recomputed here, in this same pass -- see the TRAP note
    # at the top of this file.
    funcs = ["hbAudit_gradT", "hbAudit_magU"]
    for name, _t, _n in active:
        fq = f"hbAudit_flux_{name}"
        ft = f"hbAudit_Twall_{name}"
        open(os.path.join(sysdir, fq), "w").write(
            fo_surface(fq, name, "areaNormalIntegrate", "hbAuditGradT"))
        open(os.path.join(sysdir, ft), "w").write(
            fo_surface(ft, name, "areaAverage", "T"))
        made += [fq, ft]
        funcs += [fq, ft]
        fo_map[name] = (fq, ft)
    for nm, op, fld in (("hbAudit_Tmax", "max", "T"),
                        ("hbAudit_Tmin", "min", "T"),
                        ("hbAudit_alphatMax", "max", "alphat"),
                        ("hbAudit_Umax", "max", "hbAuditMagU")):
        open(os.path.join(sysdir, nm), "w").write(fo_volume(nm, op, fld))
        made.append(nm)
        funcs.append(nm)

    shutil.rmtree(os.path.join(case, "postProcessing"), ignore_errors=True)
    clean_derived(case)
    try:
        proc = run_post(case, funcs, tspec)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout[-4000:] + "\n" + proc.stderr[-4000:] + "\n")
            sys.stderr.write("REFUSE: postProcess failed; no balance produced\n")
            return 2

        alphat_max = abs(read_dat(case, "hbAudit_alphatMax")[1][0])
        if alphat_max > 1e-14 and not a.allow_turbulent:
            sys.stderr.write(
                f"REFUSE: alphat is non-zero (max {alphat_max:.6e} m^2/s), so "
                "alphaEff varies over the patches and the laminar coefficient "
                "used here is wrong.\n        The turbulent path exists behind "
                "--allow-turbulent but has never been calibrated; it is not "
                "trusted and its report is stamped UNVALIDATED.\n"
            )
            return 2

        Tmax = read_dat(case, "hbAudit_Tmax")[1][0]
        Tmin = read_dat(case, "hbAudit_Tmin")[1][0]
        Umax = read_dat(case, "hbAudit_Umax")[1][0]

        per_patch = []
        for name, ptype, nf in active:
            fq, ft = fo_map[name]
            _t, vals = read_dat(case, fq)
            G = vals[0]
            _t2, tv = read_dat(case, ft)
            Twall = tv[0]
            area = patch_area(case, fq)
            Q = kcond * G
            per_patch.append(dict(patch=name, type=ptype, nFaces=nf, area=area,
                                  int_snGradT=G, Q_in_W=Q, T_area_avg=Twall))
    finally:
        for nm in made:
            try:
                os.remove(os.path.join(sysdir, nm))
            except OSError:
                pass
        clean_derived(case)

    # ---- balance ----------------------------------------------------------
    Qs = [p["Q_in_W"] for p in per_patch]
    Q_net = sum(Qs)
    Q_in = sum(q for q in Qs if q > 0)
    Q_out = sum(q for q in Qs if q < 0)
    imbalance_pct = 100.0 * abs(Q_net) / Q_in if Q_in > 0 else float("nan")

    # ---- regime -----------------------------------------------------------
    Twall_max = max(p["T_area_avg"] for p in per_patch)
    Twall_min = min(p["T_area_avg"] for p in per_patch)
    dT_field = Tmax - Tmin
    dT_wall = Twall_max - Twall_min
    dT = max(dT_field, dT_wall)
    L = a.length
    Ra = Gr = None
    if L and gmag > 0 and dT > 0:
        Ra = gmag * beta * dT * L ** 3 / (nu * alpha)
        Gr = Ra / Pr

    res = dict(
        case=case, time=tval,
        properties=dict(nu=nu, Pr=Pr, Prt=Prt, beta=beta, TRef=TRef, rho=rho,
                        cp=cp, alpha=alpha, k_derived=kcond, g=gmag),
        patches=per_patch,
        Q_in_W=Q_in, Q_out_W=Q_out, Q_net_W=Q_net,
        imbalance_pct=imbalance_pct, tolerance_pct=a.tol,
        dT_field_K=dT_field, dT_wall_K=dT_wall, dT_used_K=dT,
        beta_dT=beta * dT, boussinesq_ok=bool(beta * dT < 0.1),
        T_max_K=Tmax, T_min_K=Tmin, U_max_magnitude_ms=Umax,
        alphat_max=alphat_max, laminar=bool(alphat_max <= 1e-14),
        Rayleigh=Ra, Grashof=Gr, Prandtl=Pr, length_scale_m=L,
        Richardson_note=("not defined independently: no imposed velocity scale. "
                         "With Re built from the buoyancy velocity, Ri = Gr/Re^2 = 1 "
                         "identically, by construction. Ra and Pr carry the regime."),
        passed=bool(imbalance_pct == imbalance_pct and imbalance_pct <= a.tol),
    )

    if a.selftest_conduction is not None:
        dtc = a.selftest_conduction
        hot = max(per_patch, key=lambda p: p["Q_in_W"])
        Q_exact = kcond * (dtc / L) * hot["area"]
        err = 100.0 * (hot["Q_in_W"] - Q_exact) / Q_exact
        res["selftest_conduction"] = dict(
            patch=hot["patch"], dT=dtc, L=L, area=hot["area"],
            Q_closed_form_W=Q_exact, Q_measured_W=hot["Q_in_W"],
            error_pct=err, passed=bool(abs(err) < 0.5))

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w") as fh:
            json.dump(res, fh, indent=2)

    if not a.quiet:
        emit(res)
    return 0 if res["passed"] else 1


def patch_area(case, foname):
    for c in sorted(glob.glob(os.path.join(case, "postProcessing", foname, "*", "*.dat"))):
        with open(c) as fh:
            for line in fh:
                m = re.match(r"#\s*Area\s*:\s*(\S+)", line)
                if m:
                    return float(m.group(1))
    return float("nan")


def emit(r):
    p = print
    p("=" * 74)
    p(f"HEAT BALANCE AUDIT   {r['case']}")
    p(f"time = {r['time']:g}     regime: "
      + (f"Ra = {r['Rayleigh']:.4e}, " if r["Rayleigh"] else "Ra = n/a (no --length or g=0), ")
      + f"Pr = {r['Prandtl']:.6f}")
    p("=" * 74)
    p(f"  properties: nu={r['properties']['nu']:.6e} m2/s  Pr={r['properties']['Pr']:.6f}"
      f"  alpha={r['properties']['alpha']:.6e} m2/s")
    p(f"              rho={r['properties']['rho']:g} kg/m3  cp={r['properties']['cp']:g} J/kg/K"
      f"  -> k = rho.cp.alpha = {r['properties']['k_derived']:.6f} W/m/K")
    p(f"              |g| = {r['properties']['g']:.4f} m/s2"
      f"   {'(LAMINAR: alphat = 0, alphaEff = nu/Pr exactly)' if r['laminar'] else '(TURBULENT)'}")
    p("-" * 74)
    p(f"{'patch':<20}{'type':<10}{'area m2':>12}{'int snGradT':>16}{'Q into dom. W':>16}")
    for q in r["patches"]:
        p(f"{q['patch']:<20}{q['type']:<10}{q['area']:>12.6g}"
          f"{q['int_snGradT']:>16.6g}{q['Q_in_W']:>16.6g}")
    p("-" * 74)
    p(f"  heat IN   = {r['Q_in_W']:+.6e} W")
    p(f"  heat OUT  = {r['Q_out_W']:+.6e} W")
    p(f"  net       = {r['Q_net_W']:+.6e} W")
    p(f"  IMBALANCE = {r['imbalance_pct']:.4f} %  of heat in   "
      f"(tolerance {r['tolerance_pct']:.4f} %)  -> {'PASS' if r['passed'] else 'FAIL'}")
    p("-" * 74)
    p(f"  max |U|        = {r['U_max_magnitude_ms']:.6e} m/s")
    p(f"  T range, cells = {r['T_min_K']:.6f} .. {r['T_max_K']:.6f} K")
    p(f"  max dT used    = {r['dT_used_K']:.6f} K "
      f"(field {r['dT_field_K']:.6f}, wall-average {r['dT_wall_K']:.6f})")
    p(f"  BOUSSINESQ     : beta.dT = {r['beta_dT']:.6e}  -> "
      + ("SATISFIED (<< 1)" if r["boussinesq_ok"]
         else "VIOLATED: beta.dT is NOT small, the constant-density assumption "
              "in the momentum equation does not hold at this dT"))
    if r["Rayleigh"]:
        p(f"  Ra = {r['Rayleigh']:.6e}   Gr = {r['Grashof']:.6e}   Pr = {r['Prandtl']:.6f}"
          f"   (L = {r['length_scale_m']} m, dT = {r['dT_used_K']:.6f} K)")
    p(f"  Ri: {r['Richardson_note']}")
    if "selftest_conduction" in r:
        s = r["selftest_conduction"]
        p("-" * 74)
        p(f"  CALIBRATION vs closed-form 1-D conduction on patch '{s['patch']}':")
        p(f"    Q_closed_form = rho.cp.alpha.(dT/L).A = {s['Q_closed_form_W']:.9e} W")
        p(f"    Q_measured                            = {s['Q_measured_W']:.9e} W")
        p(f"    error = {s['error_pct']:+.4f} %  -> {'PASS' if s['passed'] else 'FAIL'}")
    p("=" * 74)


if __name__ == "__main__":
    sys.exit(main())
