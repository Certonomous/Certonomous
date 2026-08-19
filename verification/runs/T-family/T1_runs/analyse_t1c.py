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

    D = float(case_txt(case_dir, "D").split()[0])
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

    # wall temperature and wall-normal gradient at this station
    Tw_patch = read_patch(os.path.join(case_dir, t, "T"), "wall")
    if Tw_patch is None:
        refuse(f"REFUSE: no wall patch values for T in {case_dir}")
    # the near-wall cell at this station
    iw = max(idx, key=lambda i: Cy[i])
    r_near = Cy[iw]
    h = (D / 2.0) - r_near
    if wall_kind == "fixedFlux":
        grad = float(case_txt(case_dir, "dTdn_wall").split()[0])
        Tw = T[iw] + grad * h
    else:
        Tw = float(case_txt(case_dir, "T_wall").split()[0])
        grad = (Tw - T[iw]) / h
    Nu = D * abs(grad) / abs(Tw - T_bulk)

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
        m = {l: measure(os.path.join(HERE, a["cases"][l]), 40.0) for l in LEVELS}
        out["arms"][arm] = {l: m[l] for l in LEVELS}
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
