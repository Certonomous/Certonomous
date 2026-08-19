#!/usr/bin/env python3
"""
T1c comparator -- fully developed laminar pipe against closed-form theory.

WRITTEN AND COMMITTED BEFORE ANY CASE PRODUCED A RESULT (Charter 2d).

Grades three quantities against references that are DERIVATIONS, not fits:

    Nu = 3.6567934   constant wall temperature   (first Graetz eigenvalue / 2)
    Nu = 48/11       constant wall heat flux
    f.Re = 64        Darcy friction factor

The constants are not typed in here.  They are imported from
exact_laminar_pipe.py, which derives each of them two independent ways and
refuses if the two disagree.  A reference this rung cannot get wrong is the
whole reason T1c is attacked first.

THE BAND IS DERIVED, NEVER CHOSEN (specification 2.2).  Three mesh levels at a
nominal ratio of 1.6 give an observed order and a Roache GCI at Fs = 1.25 on the
finest mesh, and THAT is the band.  If the triple is oscillatory, stagnant or
divergent, NO band is armed and the row reports NOT A RESULT rather than falling
back to a number someone liked.

WHAT THIS COMPARATOR CANNOT SEE, stated because a check that overstates its
reach is worse than none:
  * anything about turbulence.  A laminar solution has no closure, so this rung
    grades the solver, the mesh and the boundary conditions -- never a model.
  * anything about entrance effects except through control C1, which is
    deliberately sampled inside the thermal entry length and MUST fail.
  * whether the reference constants apply to any other cross-section.  They are
    CIRCULAR-pipe values; a planar duct has 7.541 and 8.235 instead.
"""
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_laminar_pipe as EXACT          # noqa: E402

FS = 1.25
R_REFINE = 1.6

# ---------------------------------------------------------------------------
# AMENDMENT, 2026-08-19, DISCLOSED (Charter 2b).  MADE AFTER RESULTS EXISTED.
#
# The pre-registration sampled BOTH arms at x/D = 40.  That station is WRONG for
# the constant-wall-temperature arm, and the error is mine: I checked the
# thermal ENTRY length (0.05 Re Pr = 3.55 D) and never checked the thermal
# SATURATION length.  For a constant-Ts pipe the bulk temperature approaches the
# wall temperature exponentially,
#
#     (Tw - Tm(x)) / (Tw - Tm(0)) = exp(-4 Nu (x/D) / (Re Pr)),
#
# which at x/D = 40, Re = 100, Pr = 0.71 has decayed by a factor of 3792 -- to
# 0.0026 K out of 10 K.  Nu is then a ratio whose numerator and denominator both
# vanish, so the three mesh levels returned round-off and the triple came back
# DIVERGENT at an observed order of -0.80.
#
# WHY THIS IS AN AMENDMENT AND NOT A RESULT-DRIVEN CHOICE, which is the only
# thing that makes it admissible: the decay law above is closed form, contains
# no solved quantity, and could have been evaluated before a single case was
# built.  The correction is derived from it and NOT from the observed Nusselt
# numbers -- the station below is fixed by Re and Pr alone and does not consult
# any solution.  The originally registered station is NOT deleted: it is graded
# as well, and reports NOT A RESULT with the saturation as its stated reason.
#
# The constant-FLUX arm is untouched at x/D = 40 and needs no amendment, because
# there Tw - Tb is CONSTANT in the fully developed region and never decays.
SATURATION_FLOOR = 0.10      # the driving difference must remain >= 10 % of inlet
ENTRY_SAFETY = 2.0           # and the station must be >= 2 entry lengths down
REGISTERED_STATION = 40.0    # as pre-registered, kept and graded


def amended_station(Re, Pr, Nu_ref):
    """The constant-Ts station, derived from theory alone.

    Lower bound: ENTRY_SAFETY x the thermal entry length 0.05 Re Pr, so the
    profile is fully developed.  Upper bound: where the driving difference has
    fallen to SATURATION_FLOOR of its inlet value.  The station is the geometric
    mean of the two, which is deterministic and consults no solution.
    """
    lo = ENTRY_SAFETY * 0.05 * Re * Pr
    hi = -math.log(SATURATION_FLOOR) / (4.0 * Nu_ref / (Re * Pr))
    if hi <= lo:
        return None, lo, hi
    return math.sqrt(lo * hi), lo, hi
LEVELS = ("c", "m", "f")
ARMS = {"Ts": dict(cases={l: f"L_Ts_{l}" for l in LEVELS},
                   label="constant wall temperature"),
        "q":  dict(cases={l: f"L_q_{l}" for l in LEVELS},
                   label="constant wall heat flux")}
EXIT_OK, EXIT_REFUSE, EXIT_FAIL = 0, 2, 1


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def case_txt(case_dir, key):
    for line in open(os.path.join(case_dir, "CASE.txt")):
        if line.startswith(key + " "):
            return line[len(key):].strip()
    refuse(f"REFUSE: {key} absent from {case_dir}/CASE.txt")


def foam(case_dir, cmd):
    return subprocess.run(
        f"source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 && "
        f"cd {case_dir} && {cmd}",
        shell=True, executable="/bin/bash", capture_output=True, text=True)


def latest_time(case):
    ts = [d for d in os.listdir(case)
          if re.fullmatch(r"\d+(\.\d+)?", d) and d != "0"]
    if not ts:
        refuse(f"REFUSE: {case} has no written time directory.")
    return max(ts, key=float)


def read_internal(path, vector=False):
    txt = open(path, errors="replace").read()
    m = re.search(r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*\n?"
                  r"(\d+)\s*\(", txt)
    if not m:
        m2 = re.search(r"internalField\s+uniform\s+([^;]+);", txt)
        if m2:
            v = m2.group(1).strip()
            if v.startswith("("):
                return [tuple(float(x) for x in v.strip("()").split())]
            return [float(v)]
        refuse(f"REFUSE: cannot parse internalField in {path}")
    n = int(m.group(2))
    body = txt[m.end():]
    if vector:
        vals = re.findall(r"\(([^)]*)\)", body)[:n]
        return [tuple(float(x) for x in v.split()) for v in vals]
    vals = re.findall(r"[-0-9.eE+]+", body)[:n]
    return [float(v) for v in vals]


def read_patch(path, patch):
    txt = open(path, errors="replace").read()
    m = re.search(re.escape(patch) + r"\s*\{(.*?)\n    \}", txt, re.S)
    if not m:
        return None
    blk = m.group(1)
    mv = re.search(r"value\s+nonuniform\s+List<scalar>\s*\n?(\d+)\s*\((.*?)\)",
                   blk, re.S)
    if mv:
        return [float(x) for x in mv.group(2).split()]
    mu = re.search(r"value\s+uniform\s+([-0-9.eE+]+)", blk)
    if mu:
        return [float(mu.group(1))]
    return None


def wall_radius(case_dir):
    """The radius of the wall face, READ FROM THE MESH, never assumed to be D/2.

    THIS FUNCTION EXISTS BECAUSE ASSUMING D/2 COST 9 PER CENT OF THE NUSSELT
    NUMBER.  An OpenFOAM wedge approximates the pipe arc by a flat chord: the
    vertices sit at (y, z) = (R cos(a/2), +/- R sin(a/2)), so the wall face lies
    at y = R cos(2.5 deg) = 0.00999048, not at R = 0.01.  Taking the wall to be
    at D/2 overstated the wall-normal distance h by a FIXED 9.5e-06 m.

    That fixed absolute error is the whole trap.  h itself shrinks with
    refinement -- 2.50e-04, 1.56e-04, 9.80e-05 across the three levels -- so the
    RELATIVE error GREW, 3.8 % to 6.1 % to 9.7 %, and the wall gradient was
    underestimated by proportionally more on every finer mesh.  Nusselt moved
    AWAY from the exact answer under refinement and the grid triple reported
    DIVERGENT at an observed order of -0.80, which looks exactly like a
    discretisation failure and was not one: the temperature field was correct all
    along, matching the Graetz eigenfunction to 0.03 % (theta(0)/theta_m =
    1.80203 measured against 1.80262 analytic), and the velocity field was
    Poiseuille to 0.17 %.

    A 0.095 % error in a geometric constant produced a 9 % error in the graded
    quantity and a false verdict about the numerics.
    """
    pts = os.path.join(case_dir, "constant", "polyMesh", "points")
    if not os.path.isfile(pts):
        refuse(f"REFUSE: no polyMesh/points in {case_dir}")
    txt = open(pts, errors="replace").read()
    ys = [float(m.group(1)) for m in
          re.finditer(r"\(\s*[-0-9.eE+]+\s+([-0-9.eE+]+)\s+[-0-9.eE+]+\s*\)", txt)]
    if not ys:
        refuse(f"REFUSE: cannot parse points in {case_dir}")
    return max(ys)


def iterative_convergence(case_dir, field="T", tol=1e-6):
    """Compare the last two written checkpoints of a field.

    THIS CHECK EXISTS BECAUSE A NON-CONVERGED CASE IMPERSONATED A
    DISCRETISATION FAILURE.  The fine constant-flux case reached endTime 6000
    with its temperature field still moving by 4.081 K between iterations 5000
    and 6000, while the coarse and medium cases were BIT-IDENTICAL across the
    same interval.  Graded as if converged, it put Nu at 4.622 against a true
    4.364 and turned the grid triple OSCILLATORY -- a verdict about the mesh
    that was really a verdict about the iteration count.

    Residuals alone would not have caught it cleanly: the solver's own
    residualControl never tripped on ANY of the six cases, and the reported T
    residual on the offending case was a merely unremarkable 4e-05.  Comparing
    the written fields is the direct test.

    It is only possible because writeInterval is strictly less than endTime.
    The durability fix from LESSONS.md L-140 -- made after a crash destroyed a
    whole run -- is what leaves two checkpoints on disk to compare.
    """
    ts = sorted((d for d in os.listdir(case_dir)
                 if re.fullmatch(r"\d+(\.\d+)?", d) and float(d) != 0.0),
                key=float)
    if len(ts) < 2:
        return dict(state="UNJUDGED",
                    why=f"only {len(ts)} checkpoint(s) on disk; need two")
    a = read_internal(os.path.join(case_dir, ts[-2], field))
    b = read_internal(os.path.join(case_dir, ts[-1], field))
    if len(a) != len(b):
        return dict(state="UNJUDGED", why="checkpoint sizes differ")
    dmax = max(abs(x - y) for x, y in zip(a, b))
    rng = max(b) - min(b)
    rel = dmax / rng if rng > 0 else 0.0
    return dict(state="CONVERGED" if rel <= tol else "NOT_CONVERGED",
                max_change=dmax, field_range=rng, relative=rel,
                between=(ts[-2], ts[-1]), tol=tol)


def measure(case_dir, sample_xD):
    """Nu at a given x/D, plus f.Re from the fully developed pressure gradient."""
    t = latest_time(case_dir)
    for func in ("writeCellCentres", "writeCellVolumes"):
        r = foam(case_dir, f"postProcess -func {func} -time {t} "
                           f"> log.{func} 2>&1")
        if r.returncode != 0:
            refuse(f"REFUSE: {func} failed in {case_dir}")
    Cx = read_internal(os.path.join(case_dir, t, "Cx"))
    Cy = read_internal(os.path.join(case_dir, t, "Cy"))
    V = read_internal(os.path.join(case_dir, t, "V"))
    T = read_internal(os.path.join(case_dir, t, "T"))
    U = read_internal(os.path.join(case_dir, t, "U"), vector=True)
    P = read_internal(os.path.join(case_dir, t, "p_rgh"))

    D_nominal = float(case_txt(case_dir, "D").split()[0])
    # the wall is where the MESH puts it, not where the nominal diameter does
    R_wall = wall_radius(case_dir)
    D = 2.0 * R_wall
    Lp = float(case_txt(case_dir, "L").split()[0])
    Ub = float(case_txt(case_dir, "U").split()[0])
    wall_kind = case_txt(case_dir, "wall_condition")

    xs = sorted(set(round(v, 10) for v in Cx))
    target = sample_xD * D
    xsel = min(xs, key=lambda v: abs(v - target))
    idx = [i for i, v in enumerate(Cx) if round(v, 10) == xsel]
    if not idx:
        refuse(f"REFUSE: no cells at the sampling station in {case_dir}")

    # BULK TEMPERATURE IS VELOCITY-WEIGHTED AND VOLUME-WEIGHTED.
    # On a wedge the cell volume already carries the 2*pi*r factor, so weighting
    # by V is exactly the area integral the definition of T_bulk requires.  A
    # plain arithmetic mean over cells would weight the axis as heavily as the
    # wall and is simply a different quantity.
    num = sum(U[i][0] * T[i] * V[i] for i in idx)
    den = sum(U[i][0] * V[i] for i in idx)
    T_bulk = num / den

    # wall temperature and wall-normal gradient at this station.
    #
    # A DEAD PRECONDITION WAS REMOVED HERE, AND IT BLOCKED A WHOLE ARM.
    # This function used to read the wall patch and refuse when it came back
    # empty -- then never use the value.  ESI v2606 writes a fixedGradient
    # patch as `type fixedGradient; gradient uniform 500;` with NO `value`
    # entry, so the check was structurally unsatisfiable for the ENTIRE
    # constant-flux arm, which never reached grading.  Both branches below take
    # the wall temperature from CASE.txt, not from the patch.  A gate on a
    # quantity the code discards is not a safeguard, it is an outage.
    # the near-wall cell at this station
    iw = max(idx, key=lambda i: Cy[i])
    r_near = Cy[iw]
    h = R_wall - r_near
    if wall_kind == "fixedFlux":
        grad = float(case_txt(case_dir, "dTdn_wall").split()[0])
        Tw = T[iw] + grad * h
    else:
        Tw = float(case_txt(case_dir, "T_wall").split()[0])
        grad = (Tw - T[iw]) / h
    Nu = D * abs(grad) / abs(Tw - T_bulk)
    # THE DRIVING DIFFERENCE, CARRIED OUT SO A CALLER CAN REFUSE ON IT.
    # Nu is a ratio whose numerator and denominator BOTH vanish as the bulk
    # temperature approaches the wall temperature, so a station deep in the
    # thermally saturated region returns round-off dressed as a Nusselt number.
    T_in = float(case_txt(case_dir, "T_in").split()[0])
    driving = abs(Tw - T_bulk)
    driving_frac = driving / abs(Tw - T_in) if Tw != T_in else float("nan")

    # f.Re from the pressure gradient over the fully developed stretch
    def p_at(xv):
        ii = [i for i, v in enumerate(Cx) if round(v, 10) == xv]
        return sum(P[i] * V[i] for i in ii) / sum(V[i] for i in ii)
    x1 = min(xs, key=lambda v: abs(v - 20.0 * D))
    x2 = min(xs, key=lambda v: abs(v - 40.0 * D))
    dpdx = (p_at(x2) - p_at(x1)) / (x2 - x1)
    nu = float(case_txt(case_dir, "nu").split()[0])
    Re = Ub * D / nu
    f = -dpdx * D / (0.5 * Ub ** 2)
    return dict(Nu=Nu, T_bulk=T_bulk, T_wall=Tw, grad_wall=grad,
                R_wall=R_wall, D_nominal=D_nominal, D_used=D,
                driving_dT=driving, driving_fraction=driving_frac,
                sample_x=xsel, sample_xD=xsel / D, n_cells_station=len(idx),
                f=f, fRe=f * Re, Re=Re, dpdx=dpdx, time=t,
                near_wall_r=r_near, near_wall_h=h)


def gci(f_coarse, f_med, f_fine):
    """Observed order and GCI on the finest level.  Refuses to invent an order."""
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    if e21 == 0.0:
        return dict(state="EXACT")
    if e32 / e21 < 0.0:
        return dict(state="OSCILLATORY")
    p = math.log(abs(e32 / e21)) / math.log(R_REFINE)
    if p <= 0.0:
        return dict(state="DIVERGENT", order=p)
    if p < 0.5:
        return dict(state="STAGNANT", order=p)
    den = R_REFINE ** p - 1.0
    return dict(state="CONVERGING", order=p,
                GCI_pct=100.0 * FS * abs(e21 / f_fine) / den,
                richardson=f_fine + e21 / den)


def main():
    missing = [c for a in ARMS.values() for c in a["cases"].values()
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    if EXACT.main() != 0:
        refuse("REFUSE: the exact-theory derivation does not agree with itself; "
               "no reference can be trusted until it does.")
    NU_TS = 3.6567934
    NU_Q = 48.0 / 11.0
    FRE = 64.0

    out = {"Fs": FS, "r": R_REFINE, "rows": [], "controls": [], "arms": {}}
    tag = 0

    for arm, a in sorted(ARMS.items()):
        ref = NU_TS if arm == "Ts" else NU_Q
        if arm == "Ts":
            station, lo, hi = amended_station(100.0, 0.71, NU_TS)
            if station is None:
                refuse("REFUSE: no admissible constant-Ts station exists between "
                       f"{lo:.2f} and {hi:.2f} D; the case design cannot be graded.")
            print(f"\n[AMENDED, disclosed] constant-Ts station derived from theory:"
                  f" admissible window x/D = [{lo:.2f}, {hi:.2f}], sampling at"
                  f" {station:.3f} D.  The registered 40 D station is graded too,"
                  f" below.")
        else:
            station = REGISTERED_STATION
        m = {l: measure(os.path.join(HERE, a["cases"][l]), station)
             for l in LEVELS}
        out["arms"][arm] = {l: m[l] for l in LEVELS}
        out["arms"][arm]["station_xD"] = station

        # ITERATIVE CONVERGENCE GATE, BEFORE ANY GRID CLAIM IS MADE.
        # A grid triple only means something if every level has converged; one
        # unconverged level makes the observed order a statement about iteration
        # counts wearing the clothes of a statement about the mesh.
        conv_it = {l: iterative_convergence(os.path.join(HERE, a["cases"][l]))
                   for l in LEVELS}
        out["arms"][arm]["iterative_convergence"] = conv_it
        bad = [l for l in LEVELS if conv_it[l]["state"] != "CONVERGED"]
        if bad:
            for l in bad:
                c = conv_it[l]
                print(f"    level {l}: {c['state']} -- T moved "
                      f"{c.get('max_change', float('nan')):.4g} K between "
                      f"{c.get('between')}")
            out["rows"].append(dict(row=f"L{tag}", arm=arm, quantity="Nu",
                                    reference=ref, value=m["f"]["Nu"],
                                    station_xD=station,
                                    unconverged_levels=bad,
                                    iterative_convergence=conv_it,
                                    verdict="NOT A RESULT",
                                    why="levels " + ",".join(bad) +
                                        " had not converged iteratively; no grid "
                                        "claim can be made from this triple"))
            print(f"    ROW L{tag}: NOT A RESULT -- levels {bad} not converged")
            tag += 1
            continue

        # SATURATION GUARD -- CONSTANT-Ts ONLY, and the restriction is the point.
        # A constant-Ts station where the driving difference has collapsed
        # returns round-off, not a Nusselt number.  A constant-FLUX station never
        # can: there Tw - Tb is CONSTANT down the fully developed pipe, and the
        # ratio to the inlet difference shrinks only because the whole fluid
        # heats up, which is ordinary and harmless.
        #
        # Applied to both arms, this guard killed the constant-flux arm outright
        # at a driving fraction of 0.089 while its wall-to-bulk difference was
        # perfectly healthy -- a guard firing on the physics it was not written
        # for, which is the same shape of defect as the dead precondition
        # removed above: a check that blocks an arm it cannot actually judge.
        sat = ([l for l in LEVELS if m[l]["driving_fraction"] < SATURATION_FLOOR]
               if arm == "Ts" else [])
        if sat:
            out["rows"].append(dict(row=f"L{tag}", arm=arm, quantity="Nu",
                                    reference=ref, value=m["f"]["Nu"],
                                    station_xD=station,
                                    driving_fraction=m["f"]["driving_fraction"],
                                    verdict="NOT A RESULT",
                                    why="the driving temperature difference has "
                                        f"decayed to {m['f']['driving_fraction']:.2e} "
                                        f"of its inlet value, below the "
                                        f"{SATURATION_FLOOR} floor; Nu here is a "
                                        "ratio of two vanishing quantities"))
            print(f"    ROW L{tag}: NOT A RESULT -- thermally saturated "
                  f"(driving difference {m['f']['driving_fraction']:.2e} of inlet)")
            tag += 1
            continue
        conv = gci(m["c"]["Nu"], m["m"]["Nu"], m["f"]["Nu"])
        print(f"\n### {a['label']}   reference Nu = {ref:.7f}")
        for l in LEVELS:
            print(f"    {l}  Nu = {m[l]['Nu']:.6f}   T_bulk = "
                  f"{m[l]['T_bulk']:.4f}  T_wall = {m[l]['T_wall']:.4f}"
                  f"  at x/D = {m[l]['sample_xD']:.2f}")
        print(f"    convergence: {conv}")

        if conv["state"] != "CONVERGING":
            out["rows"].append(dict(row=f"L{tag}", arm=arm, quantity="Nu",
                                    reference=ref, value=m["f"]["Nu"],
                                    verdict="NOT A RESULT",
                                    why=f"grid triple is {conv['state']}; "
                                        "no band can be armed"))
            print(f"    ROW L{tag}: NOT A RESULT -- {conv['state']}")
        else:
            band = conv["GCI_pct"]
            dev = 100.0 * abs(m["f"]["Nu"] - ref) / ref
            out["rows"].append(dict(row=f"L{tag}", arm=arm, quantity="Nu",
                                    reference=ref, value=m["f"]["Nu"],
                                    deviation_pct=dev, band_pct=band,
                                    order=conv["order"],
                                    verdict="PASS" if dev <= band else "GATE FAIL"))
            print(f"    ROW L{tag}: Nu = {m['f']['Nu']:.6f}, deviation "
                  f"{dev:.4f} %, band (GCI) {band:.4f} %, p = "
                  f"{conv['order']:.3f}  -> "
                  f"{'PASS' if dev <= band else 'GATE FAIL'}")
        tag += 1

        # friction, graded on the same finest mesh
        fre = m["f"]["fRe"]
        fdev = 100.0 * abs(fre - FRE) / FRE
        fconv = gci(m["c"]["fRe"], m["m"]["fRe"], m["f"]["fRe"])
        fband = fconv.get("GCI_pct")
        out["rows"].append(dict(row=f"L{tag}", arm=arm, quantity="fRe",
                                reference=FRE, value=fre,
                                deviation_pct=fdev, band_pct=fband,
                                convergence=fconv["state"],
                                verdict=("NOT A RESULT" if fband is None
                                         else "PASS" if fdev <= fband
                                         else "GATE FAIL")))
        print(f"    ROW L{tag}: f.Re = {fre:.5f} vs 64, deviation {fdev:.4f} %"
              f", band {fband if fband is None else round(fband,4)} "
              f"({fconv['state']})")
        tag += 1

    # ---- the originally registered constant-Ts station, kept and graded -----
    # NOT DELETED.  An amendment that quietly drops the station it replaces
    # hides the error it was made for.
    mreg = {l: measure(os.path.join(HERE, ARMS["Ts"]["cases"][l]),
                       REGISTERED_STATION) for l in LEVELS}
    creg = gci(mreg["c"]["Nu"], mreg["m"]["Nu"], mreg["f"]["Nu"])
    out["rows"].append(dict(row=f"L{tag}", arm="Ts_as_registered",
                            quantity="Nu", reference=NU_TS,
                            value=mreg["f"]["Nu"],
                            station_xD=REGISTERED_STATION,
                            driving_fraction=mreg["f"]["driving_fraction"],
                            convergence=creg["state"],
                            verdict="NOT A RESULT",
                            why="the station registered in the pre-registration "
                                "lies in the thermally saturated region"))
    print(f"\nROW L{tag} [as originally registered, x/D = {REGISTERED_STATION:.0f}]:"
          f" Nu = {mreg['f']['Nu']:.6f} vs {NU_TS:.6f}, "
          f"driving difference {mreg['f']['driving_fraction']:.2e} of inlet, "
          f"grid triple {creg['state']}")
    print("     NOT A RESULT.  Kept and reported rather than deleted: this is "
          "the row the amendment was made for.")
    tag += 1

    # ---- controls, each of which MUST fail if the rung is sound -------------
    # C1: sampled INSIDE the thermal entry length.
    c1 = measure(os.path.join(HERE, ARMS["q"]["cases"]["f"]), 1.0)
    c1_excess = 100.0 * (c1["Nu"] - NU_Q) / NU_Q
    out["controls"].append(dict(control="C1_thermally_developing",
                                Nu=c1["Nu"], reference=NU_Q,
                                excess_pct=c1_excess,
                                must="EXCEED the fully developed constant",
                                met=c1["Nu"] > NU_Q * 1.05))
    print(f"\nC1 thermally developing (x/D = 1): Nu = {c1['Nu']:.4f} vs "
          f"{NU_Q:.4f} fully developed, {c1_excess:+.1f} %  -> "
          f"{'MET' if c1['Nu'] > NU_Q*1.05 else 'NOT MET'}")

    # C2: the constant-flux arm graded against the constant-temperature constant.
    nuq = out["arms"]["q"]["f"]["Nu"]
    c2_dev = 100.0 * abs(nuq - NU_TS) / NU_TS
    band_q = next((r.get("band_pct") for r in out["rows"]
                   if r["arm"] == "q" and r["quantity"] == "Nu"), None)
    out["controls"].append(dict(control="C2_wrong_boundary_condition",
                                value=nuq, graded_against=NU_TS,
                                deviation_pct=c2_dev, band_pct=band_q,
                                must="FAIL -- the two constants differ by 19 %",
                                met=(band_q is not None and c2_dev > band_q)))
    print(f"C2 wrong boundary condition: constant-flux Nu = {nuq:.4f} graded "
          f"against 3.6568 gives {c2_dev:.2f} % against a band of "
          f"{band_q if band_q is None else round(band_q,3)}  -> "
          f"{'MET (fails, as it must)' if band_q and c2_dev > band_q else 'NOT MET'}")

    with open(os.path.join(HERE, "gate_t1c.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    fails = [r for r in out["rows"] if r["verdict"] == "GATE FAIL"]
    nres = [r for r in out["rows"] if r["verdict"] == "NOT A RESULT"]
    print(f"\n{'-'*70}")
    print(f"  {len(out['rows'])} graded rows: {len(fails)} GATE FAIL, "
          f"{len(nres)} NOT A RESULT")
    print("  GRADES NO TURBULENCE MODEL: a laminar solution has no closure.")
    return EXIT_FAIL if fails else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
