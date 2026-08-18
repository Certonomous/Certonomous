#!/usr/bin/env python3
"""analyse_k0cs.py -- grade the F14 K0cS square-cavity rung against its spec.

    python3 analyse_k0cs.py       # writes gate_k0cs.json and GATE_TABLE.md

Exit 0 = every graded row passed.  Exit 1 = at least one graded row failed.
Exit 2 = refused to grade (a case did not converge, the specification could not
be read, or a measurement could not be made honestly).

REFERENCE VALUES AND BANDS ARE PARSED FROM THE SPECIFICATION, NOT TYPED HERE
----------------------------------------------------------------------------
Every one comes out of Section 3.2 of

    docs/campaigns/F14-cooling-ladder/K0cS_SQUARE_CAVITY_GATE.md

resolved by SEARCHING UPWARD for the repository root rather than by an
assembled relative literal.  The K0cT rung's analyser was BROKEN AT HEAD by
exactly that mistake when a reorganisation moved its run tree; see
K0cT_NUSSELT_REGRADE.md Section 6.1.  A comparator holding its own copy of the
reference is this lab's most repeated failure written in code.
"""

import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_up(relpath):
    d = HERE
    while True:
        cand = os.path.join(d, relpath)
        if os.path.exists(cand):
            return os.path.abspath(cand)
        if os.path.isdir(os.path.join(d, ".git")):
            return os.path.abspath(os.path.join(d, relpath))
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.abspath(relpath)
        d = parent


SPEC = _find_up("docs/campaigns/F14-cooling-ladder/K0cS_SQUARE_CAVITY_GATE.md")
FOAM_BASHRC = os.environ.get("FOAM_BASHRC",
                             "/usr/lib/openfoam/openfoam2606/etc/bashrc")

GRADED = ["S_SST_c", "S_SST_f", "S_KE_c", "S_KE_f", "S_LS_c", "S_LS_f"]
PAIRS = {"kOmegaSST": ("S_SST_c", "S_SST_f"),
         "kEpsilon": ("S_KE_c", "S_KE_f"),
         "LaunderSharmaKE": ("S_LS_c", "S_LS_f")}
CONTROLS = ["C1_laminar", "C2_seed_d100", "C3_prt128", "C4_adiabatic"]
STRAT_Y = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70)

# convergence, K0cS_PREREGISTRATION.md Section 4
CONV_WINDOW, CONV_STRIDE = 400, 50
CONV = {"Nu_pct": 0.5, "Sp_abs": 0.005, "V_pct": 1.0}


def refuse(msg):
    sys.stderr.write(msg + "\n")
    raise SystemExit(2)


def foam(case, cmd):
    return subprocess.run(
        ["bash", "-c", f". '{FOAM_BASHRC}' >/dev/null 2>&1; "
                       f"cd '{case}'; {cmd}"],
        capture_output=True, text=True)


# ---------------------------------------------------------------------------
# specification
# ---------------------------------------------------------------------------

def read_spec():
    if not os.path.isfile(SPEC):
        refuse(f"REFUSE: specification not found at {SPEC}")
    txt = open(SPEC).read()
    flat = " ".join(txt.split())
    rows = {}

    def grab(tag, pat):
        m = re.search(pat, flat)
        if not m:
            refuse(f"REFUSE: Section 3.2 row {tag} could not be read.")
        return m

    for tag, name, pat in (
        ("G1", "Nu_hot", r"\| G1 \| Average Nu, hot wall \| ([\d.]+)[^|]*\|[^|]*\| REL <= ([\d.]+) %"),
        ("G2", "Nu_cold", r"\| G2 \| Average Nu, cold wall \| ([\d.]+)[^|]*\|[^|]*\| REL <= ([\d.]+) %"),
        ("G3", "Nu_bot", r"\| G3 \| Average Nu, bottom wall \| ([\d.]+)[^|]*\|[^|]*\| REL <= ([\d.]+) %"),
        ("G4", "Nu_top", r"\| G4 \| Average Nu, top wall \| ([\d.]+)[^|]*\|[^|]*\| REL <= ([\d.]+) %"),
        ("G5", "Nu_mid_hot", r"\| G5 \| Local Nu at mid-height, hot wall \| ([\d.]+)[^|]*\|[^|]*\| REL <= ([\d.]+) %"),
        ("G6", "Nu_max_hot", r"\| G6 \| Maximum local Nu on the hot wall \| ([\d.]+)[^|]*\|[^|]*\| REL <= ([\d.]+) %"),
        ("G8", "Vpeak", r"\| G8 \| Peak mid-height vertical velocity, magnitude \| ([\d.]+) m/s\s*\|[^|]*\| REL <= ([\d.]+) %"),
        ("G10", "uv_peak", r"\| G10 \| Peak Reynolds shear stress.*?\| ([\d.eE+-]+) m2/s2\s*\|.*?\| REL <= ([\d.]+) %"),
    ):
        m = grab(tag, pat)
        rows[tag] = dict(quantity=name, reference=float(m.group(1)),
                         band=float(m.group(2)), kind="REL", unit="%")

    m = grab("G7", r"\| G7 \| Stratification parameter Sp[^|]*\| ([\d.]+)[^|]*\|[^|]*\| absolute, \\\|Sp_solve - ([\d.]+)\\\| <= ([\d.]+)\s*\|")
    if abs(float(m.group(1)) - float(m.group(2))) > 1e-9:
        refuse("REFUSE: the G7 reference and its band centre disagree.")
    rows["G7"] = dict(quantity="Sp", reference=float(m.group(1)),
                      band=float(m.group(3)), kind="ABS", unit="")

    m = grab("G9", r"\| G9 \| Peak mid-height vertical velocity, location \| X = ([\d.]+) \|[^|]*\| within ([\d.]+) in X")
    rows["G9"] = dict(quantity="Vpeak_X", reference=float(m.group(1)),
                      band=float(m.group(2)), kind="ABS", unit="X")

    m = re.search(r"Hot wall \(x = 0\) \| Isothermal, ([\d.]+) \+/-", flat)
    m2 = re.search(r"Cold wall \(x = L\) \| Isothermal, ([\d.]+) \+/-", flat)
    mL = re.search(r"Geometry \| ([\d.]+) m high x ([\d.]+) m wide", flat)
    if not (m and m2 and mL):
        refuse("REFUSE: the Section 1 case rows could not be read.")
    return rows, dict(Th=float(m.group(1)), Tc=float(m2.group(1)),
                      L=float(mL.group(2)))


# ---------------------------------------------------------------------------
# OpenFOAM field readers
# ---------------------------------------------------------------------------

def read_internal(path, vector=False):
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*\n?\s*(\d+)\s*\(", txt)
    if m:
        k = txt.index("(", m.end() - 1) + 1
        body = txt[k:txt.index("\n)", k)]
        if vector:
            return [tuple(float(v) for v in t.split())
                    for t in re.findall(r"\(([^)]*)\)", body)]
        return [float(v) for v in body.split()]
    m = re.search(r"internalField\s+uniform\s+(\(([^)]*)\)|[-\d.eE+]+)", txt)
    if not m:
        refuse(f"REFUSE: could not read internalField from {path}")
    if vector:
        return [tuple(float(v) for v in m.group(2).split())]
    return [float(m.group(1))]


def read_patch(path, patch, vector=False):
    txt = open(path).read()
    i = txt.index("boundaryField")
    j = txt.index("\n    " + patch, i)
    seg = txt[j:]
    end = seg.index("\n    }")
    seg = seg[:end]
    m = re.search(r"value\s+nonuniform\s+List<(scalar|vector)>\s*\n?\s*(\d+)\s*\(", seg)
    if m:
        k = seg.index("(", m.end() - 1) + 1
        body = seg[k:seg.rindex(")")]
        if vector:
            return [tuple(float(v) for v in t.split())
                    for t in re.findall(r"\(([^)]*)\)", body)]
        return [float(v) for v in body.split()]
    m = re.search(r"value\s+uniform\s+(\(([^)]*)\)|[-\d.eE+]+)", seg)
    if m:
        return [tuple(float(v) for v in m.group(2).split())] if vector \
            else [float(m.group(1))]
    if "zeroGradient" in seg or "calculated" in seg:
        return None
    refuse(f"REFUSE: could not read patch {patch} from {path}")


def case_txt(case, key):
    for line in open(os.path.join(case, "CASE.txt")):
        if line.startswith(key + " "):
            return line[len(key):].strip()
    refuse(f"REFUSE: '{key}' not in {case}/CASE.txt")


def latest_time(case):
    ts = [d for d in os.listdir(case)
          if re.fullmatch(r"\d+(\.\d+)?", d) and d != "0"]
    if not ts:
        refuse(f"REFUSE: {case} has no written time directory.")
    return max(ts, key=float)


def lsq_slope(xs, ys):
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    return (n * sxy - sx * sy) / (n * sxx - sx * sx)


# ---------------------------------------------------------------------------
# measurement
# ---------------------------------------------------------------------------

def measure(case_dir, case):
    t = latest_time(case_dir)
    r = foam(case_dir, f"postProcess -func writeCellCentres -time {t} "
                       "> log.cellCentres 2>&1")
    if r.returncode != 0:
        refuse(f"REFUSE: writeCellCentres failed in {case}")
    cx = read_internal(os.path.join(case_dir, t, "Cx"))
    cy = read_internal(os.path.join(case_dir, t, "Cy"))
    T = read_internal(os.path.join(case_dir, t, "T"))
    U = read_internal(os.path.join(case_dir, t, "U"), vector=True)
    nut_p = os.path.join(case_dir, t, "nut")
    nut = read_internal(nut_p) if os.path.isfile(nut_p) else [0.0] * len(T)
    alphat_p = os.path.join(case_dir, t, "alphat")

    L = float(case_txt(case_dir, "L").split()[0])
    dT = float(case_txt(case_dir, "dT").split()[0])
    nu = float(case_txt(case_dir, "nu").split()[0])
    Pr = float(case_txt(case_dir, "Pr"))
    alpha = nu / Pr

    xs = sorted(set(round(v, 12) for v in cx))
    ys = sorted(set(round(v, 12) for v in cy))
    idx = {(round(x, 12), round(y, 12)): i for i, (x, y) in enumerate(zip(cx, cy))}

    # ---- wall Nusselt ----------------------------------------------------
    # Nu = -(L/dT) . dT/d(axis) . (alphaEff_wall / alpha)
    #
    # THE alphaEff FACTOR IS NOT DECORATION.  For the low-Reynolds-number
    # models nut is identically zero AT the wall, alphaEff = alpha, and this
    # reduces to the molecular two-point gradient the K0cT rung used.  For
    # kEpsilon with nutkWallFunction it does NOT: the wall function puts a
    # non-zero turbulent conductivity on the patch, and the wall heat flux is
    # alphaEff.dT/dn, not alpha.dT/dn.  Dropping the factor would report
    # kEpsilon's heat flux as the molecular part only and flatter it by
    # whatever its wall function is contributing.  The factor is READ from the
    # written alphat field, not assumed.
    def wall_nu(patch, axis, at_start):
        Tw = read_patch(os.path.join(case_dir, t, "T"), patch)
        if Tw is None:
            return None, None, None
        at = read_patch(alphat_p, patch) if os.path.isfile(alphat_p) else None
        along = ys if axis == "x" else xs
        wall_coord = (xs[0] if at_start else xs[-1]) if axis == "x" \
            else (ys[0] if at_start else ys[-1])
        wall_pos = 0.0 if at_start else L
        h = abs(wall_coord - wall_pos)
        vals = []
        for j, c in enumerate(along):
            key = (wall_coord, c) if axis == "x" else (c, wall_coord)
            T1 = T[idx[key]]
            Tf = Tw[j] if len(Tw) > 1 else Tw[0]
            # outward-from-wall difference, then converted to d/d(axis)
            grad_axis = (T1 - Tf) / h if at_start else (Tf - T1) / h
            aeff = 1.0
            if at is not None:
                av = at[j] if len(at) > 1 else at[0]
                aeff = 1.0 + av / alpha
            vals.append(-(L / dT) * grad_axis * aeff)
        return sum(vals) / len(vals), vals, along

    Nu_hot, hot_local, hot_y = wall_nu("hotWall", "x", True)
    Nu_cold, _, _ = wall_nu("coldWall", "x", False)
    Nu_bot, _, _ = wall_nu("bottomWall", "y", True)
    Nu_top, _, _ = wall_nu("topWall", "y", False)

    def interp(cs, vs, target):
        if target <= cs[0]:
            return vs[0]
        if target >= cs[-1]:
            return vs[-1]
        for i in range(len(cs) - 1):
            if cs[i] <= target <= cs[i + 1]:
                f = (target - cs[i]) / (cs[i + 1] - cs[i])
                return vs[i] + f * (vs[i + 1] - vs[i])
        return vs[-1]

    Nu_mid_hot = interp(hot_y, hot_local, 0.5 * L)
    Nu_max_hot = max(hot_local)

    # ---- mid-width stratification ---------------------------------------
    def col_at_x(xt):
        below = max([x for x in xs if x <= xt], default=xs[0])
        above = min([x for x in xs if x >= xt], default=xs[-1])
        f = 0.0 if above == below else (xt - below) / (above - below)
        return [T[idx[(below, y)]] + f * (T[idx[(above, y)]] - T[idx[(below, y)]])
                for y in ys]

    Tcol = col_at_x(0.5 * L)
    theta = [interp(ys, Tcol, yy * L) for yy in STRAT_Y]
    Tc_K = float(case_txt(case_dir, "T_cold").split()[0])
    Sp = lsq_slope(list(STRAT_Y), [(v - Tc_K) / dT for v in theta])
    theta_centre = (interp(ys, Tcol, 0.5 * L) - Tc_K) / dT

    # ---- mid-height vertical velocity ------------------------------------
    def row_at_y(yt, get):
        below = max([y for y in ys if y <= yt], default=ys[0])
        above = min([y for y in ys if y >= yt], default=ys[-1])
        f = 0.0 if above == below else (yt - below) / (above - below)
        out = []
        for x in xs:
            a, b = get(idx[(x, below)]), get(idx[(x, above)])
            out.append(a + f * (b - a))
        return out

    Uy = row_at_y(0.5 * L, lambda i: U[i][1])
    imax = max(range(len(Uy)), key=lambda i: Uy[i])
    Vpeak, Vpeak_X = Uy[imax], xs[imax] / L
    Vmin = min(Uy)

    # ---- Reynolds shear stress from the eddy-viscosity constitutive law --
    # u'v' = -nu_t (dv/dx + du/dy).  This is the MODEL'S OWN OUTPUT, which is
    # why it grades and the rms velocity components do not (specification
    # Section 3.2 amendment note).
    nut_row = row_at_y(0.5 * L, lambda i: nut[i])
    Ux_row = row_at_y(0.5 * L, lambda i: U[i][0])
    uv = []
    for i in range(1, len(xs) - 1):
        dvdx = (Uy[i + 1] - Uy[i - 1]) / (xs[i + 1] - xs[i - 1])
        uv.append((-nut_row[i] * dvdx, xs[i] / L))
    hot_half = [v for v in uv if v[1] <= 0.5]
    uv_peak, uv_peak_X = (max(hot_half, key=lambda v: v[0])
                          if hot_half else (0.0, 0.0))

    kf = os.path.join(case_dir, t, "k")
    kmax = max(read_internal(kf)) if os.path.isfile(kf) else None
    nut_max = max(nut) if nut else 0.0

    return dict(
        time=t, Nu_hot=Nu_hot, Nu_cold=Nu_cold, Nu_bot=Nu_bot, Nu_top=Nu_top,
        Nu_mid_hot=Nu_mid_hot, Nu_max_hot=Nu_max_hot, Sp=Sp,
        theta_centre=theta_centre, Vpeak=Vpeak, Vpeak_X=Vpeak_X, Vmin=Vmin,
        uv_peak=uv_peak, uv_peak_X=uv_peak_X, k_max=kmax,
        vrms_isotropic=(math.sqrt(2.0 * kmax / 3.0) if kmax else None),
        nut_over_nu_max=nut_max / nu,
        heat_balance_pct=(100.0 * abs(Nu_hot + Nu_bot - Nu_cold - Nu_top)
                          / abs(Nu_hot) if Nu_hot else None))


# ---------------------------------------------------------------------------
# convergence, from the function-object history
# ---------------------------------------------------------------------------

def convergence(case_dir, case):
    def series(sub, col):
        root = os.path.join(case_dir, "postProcessing", sub)
        if not os.path.isdir(root):
            return None
        pts = []
        for d in os.listdir(root):
            f = [x for x in os.listdir(os.path.join(root, d))]
            for fn in f:
                for line in open(os.path.join(root, d, fn)):
                    if line.startswith("#"):
                        continue
                    p = line.split()
                    if len(p) > col:
                        try:
                            pts.append((float(p[0]), float(p[col])))
                        except ValueError:
                            pass
        pts.sort()
        return pts

    out, ok = {}, True
    hot = series("hotFlux", 1)
    if not hot:
        refuse(f"REFUSE: {case} has no hotFlux history; convergence cannot "
               "be judged and this analyser does not guess.")
    tail = [v for tt, v in hot if tt >= hot[-1][0] - CONV_WINDOW]
    if len(tail) < 9:
        refuse(f"REFUSE: {case} has only {len(tail)} samples in the "
               f"{CONV_WINDOW}-iteration window; 9 are required.")
    span = 100.0 * (max(tail) - min(tail)) / abs(sum(tail) / len(tail))
    out["Nu_pct"] = span
    ok &= span < CONV["Nu_pct"]

    umax = series("Uymax", 2)
    if umax:
        tail = [v for tt, v in umax if tt >= umax[-1][0] - CONV_WINDOW]
        if len(tail) >= 9 and abs(sum(tail) / len(tail)) > 1e-12:
            sp = 100.0 * (max(tail) - min(tail)) / abs(sum(tail) / len(tail))
            out["V_pct"] = sp
            ok &= sp < CONV["V_pct"]
    out["pass"] = bool(ok)
    return out


# ---------------------------------------------------------------------------

def main():
    rows_spec, case_spec = read_spec()
    missing = [c for c in GRADED + CONTROLS
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: these cases have no completion marker, so their "
               f"outcome is unknown: {missing}. Absence of a process proves "
               "neither death nor completion; this analyser waits for the "
               "marker and does not read the process table.")

    cases = {}
    for c in GRADED + CONTROLS:
        d = os.path.join(HERE, c)
        marker = dict(l.strip().split("=", 1)
                      for l in open(os.path.join(HERE, f"DONE.{c}"))
                      if "=" in l)
        if marker.get("rc_solve") != "0":
            refuse(f"REFUSE: {c} exited rc_solve={marker.get('rc_solve')}.")
        cases[c] = dict(marker=marker, measure=measure(d, c),
                        convergence=convergence(d, c),
                        model=case_txt(d, "model"))

    graded, refused = [], []
    for model, (coarse, fine) in PAIRS.items():
        if not cases[fine]["convergence"]["pass"]:
            refused.append(fine)
            continue
        for tag, spec in sorted(rows_spec.items()):
            q = spec["quantity"]
            sv = cases[fine]["measure"][q]
            cv = cases[coarse]["measure"][q]
            ref = spec["reference"]
            if spec["kind"] == "REL":
                dev = 100.0 * abs(sv - ref) / abs(ref)
            else:
                dev = abs(sv - ref)
            graded.append(dict(
                row=tag, model=model, quantity=q, reference=ref,
                coarse=cv, solved=sv, deviation=dev, band=spec["band"],
                unit=spec["unit"], kind=spec["kind"],
                verdict="PASS" if dev <= spec["band"] else "GATE FAIL"))

    # mutation control: every row must be flippable both ways
    mut = []
    for g in graded:
        if g["kind"] == "REL":
            can_pass = True
            can_fail = 100.0 * abs(g["solved"] - g["reference"] * 3.0) \
                / abs(g["reference"] * 3.0) > g["band"]
        else:
            can_pass = True
            can_fail = abs(g["solved"] - (g["reference"] + 10 * g["band"])) \
                > g["band"]
        mut.append(dict(row=g["row"], model=g["model"],
                        reachable_PASS=can_pass, reachable_FAIL=bool(can_fail)))
    reachable = all(m["reachable_PASS"] and m["reachable_FAIL"] for m in mut)

    out = dict(spec=SPEC, reference_parsed_from_spec=rows_spec,
               cases={k: {kk: vv for kk, vv in v.items()} for k, v in cases.items()},
               graded_rows=graded, convergence_refusals=refused,
               mutation_control=mut, every_row_reachable_both_ways=reachable)
    with open(os.path.join(HERE, "gate_k0cs.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)

    fails = [g for g in graded if g["verdict"] != "PASS"]
    print(f"graded rows: {len(graded)}   GATE FAIL: {len(fails)}")
    print(f"convergence refusals: {refused}")
    print(f"every row reachable both ways: {reachable}")
    for model in PAIRS:
        rs = [g for g in graded if g["model"] == model]
        if not rs:
            print(f"\n{model}: REFUSED (convergence)")
            continue
        nf = len([g for g in rs if g['verdict'] != 'PASS'])
        print(f"\n{model}:  {nf} of {len(rs)} rows GATE FAIL")
        for g in rs:
            print(f"  {g['row']:>3} {g['quantity']:<12} ref {g['reference']:>9.4f} "
                  f"coarse {g['coarse']:>10.4f} fine {g['solved']:>10.4f}  "
                  f"dev {g['deviation']:>8.3f} {g['unit']:<2} "
                  f"band {g['band']:<6} {g['verdict']}")
    print("\nREPORTED, NOT GRADED:")
    for c in GRADED + CONTROLS:
        m = cases[c]["measure"]
        print(f"  {c:<14} theta_centre {m['theta_centre']:.4f}  "
              f"heat_bal {m['heat_balance_pct']:.4f} %  "
              f"nut/nu_max {m['nut_over_nu_max']:.1f}  "
              f"Nu_hot {m['Nu_hot']:.2f}  Sp {m['Sp']:.4f}  "
              f"Vpeak {m['Vpeak']:.4f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
