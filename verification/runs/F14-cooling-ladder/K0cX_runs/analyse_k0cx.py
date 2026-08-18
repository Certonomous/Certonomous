#!/usr/bin/env python3
"""analyse_k0cx.py -- grade the F14 K0cX cross-geometry rung against the K0c spec.

    python3 analyse_k0cx.py      # writes gate_k0cx.json and GATE_TABLE.md

Exit 0 = every graded row passed.  Exit 1 = at least one graded row failed.
Exit 2 = refused to grade (specification unreadable, a measurement impossible).

REFERENCE VALUES AND BANDS ARE PARSED FROM THE SPECIFICATION, NOT TYPED HERE
----------------------------------------------------------------------------
Every one comes out of

    docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md

Sections 2.3 and 2.4 and addendum A1.2/A1.5, resolved by SEARCHING UPWARD for
the repository root rather than by an assembled relative literal.  The K0cT
rung's analyser was BROKEN AT HEAD by exactly that mistake, and its build script
beside it STILL IS -- verified by execution, see build_cases.py.  A comparator
holding its own copy of the reference is this lab's most repeated failure
written in code.

The Section 2.3 DERIVED rows are additionally RE-DERIVED here from the primary
ERCOFTAC data files and asserted equal to what the specification states, so a
typo in the specification is caught rather than graded against.

WHAT THIS GRADES AND WHAT IT REFUSES TO
---------------------------------------
20 rows per model per the specification Section 2.4 plus addendum A1: ten
quantities at each of two Rayleigh numbers.  Graded on the FINE mesh of the
mandatory pair, coarse carried in every row (Section 2.5).

The extra-fine 'x' cases and the Prt 'P_' cases are SENSITIVITIES.  They grade
nothing and they appear only in the reported sections.  A sensitivity cannot
pass or fail; it is a measured difference used to attribute a deviation.

The LAMINAR control is measured on every row and reported beside every model,
and its rows are counted toward NO model's verdict.

THE alphaEff FACTOR IN THE WALL NUSSELT IS NOT DECORATION
----------------------------------------------------------
For the low-Re models nut is identically zero AT the wall (nutLowReWallFunction),
alphaEff = alpha, and the Nusselt reduces to the molecular two-point gradient the
K0cT rung used.  For kEpsilon with nutkWallFunction it need NOT: the wall
function can put a non-zero turbulent conductivity on the patch, and the wall
heat flux is then alphaEff.dT/dn.  Dropping the factor would report kEpsilon's
heat flux as the molecular part only.  The factor is READ from the written
alphat field, never assumed -- and what it turns out to be is itself a reported
measurement, because the gate's own argument is that this mesh's y+ is far below
where a wall function is admissible.
"""

import copy
import json
import math
import os
import re
import subprocess
import sys
import datetime

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


SPEC = _find_up("docs/campaigns/F14-cooling-ladder/"
                "K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md")
DATA = _find_up("docs/campaigns/F14-cooling-ladder/reference-data/betts_bokhari")
FOAM_BASHRC = os.environ.get("FOAM_BASHRC",
                             "/usr/lib/openfoam/openfoam2606/etc/bashrc")

MODELS = {"SST": "kOmegaSST", "KE": "kEpsilon", "LS": "LaunderSharmaKE",
          "LAM": "laminar"}
RUNGS = ("lo", "hi")
PROBE_YH = (0.30, 0.40, 0.50, 0.60, 0.70)
REPORT_YH = (0.30, 0.50, 0.70)
CMU = 0.09

# convergence, K0cX_PREREGISTRATION.md Section 6.1, registered before compute
CONV_WINDOW, CONV_STRIDE = 400, 50
CONV = {"Nu_pct": 0.02, "S_abs": 0.001, "Uy_pct": 0.02}

# A TRANSFERRED CAUTION, NOT A BAND.  See the pre-registration's appended
# provenance correction: 8.8 % is the SQUARE cavity's rig-to-rig spread
# (Ampofo vs Tian, top-wall Nu).  This cavity's own reproducibility spread is
# NOT OBTAINED -- there is no second experiment.  It is carried here
# one-directionally and negatively: no agreement inside it is a validation.  It
# widens nothing and it rescues nothing.
TRANSFERRED_CAUTION_PCT = 8.8


def refuse(msg):
    sys.stderr.write(msg + "\n")
    raise SystemExit(2)


def foam(case, cmd):
    return subprocess.run(
        ["bash", "-c", f". '{FOAM_BASHRC}' >/dev/null 2>&1; cd '{case}'; {cmd}"],
        capture_output=True, text=True)


# ===========================================================================
# the specification
# ===========================================================================

def read_spec():
    if not os.path.isfile(SPEC):
        refuse(f"REFUSE: gate specification not found at {SPEC}")
    txt = open(SPEC).read()
    flat = " ".join(txt.split())
    ref, bands = {}, {}

    def row(label):
        m = re.search(r"^\|\s*" + label + r"[^|]*\|([^|]*)\|([^|]*)\|", txt, re.M)
        if not m:
            refuse(f"REFUSE: Section 2.3 row '{label}' not found. Nothing is "
                   "graded against a value this script supplies itself.")
        return m.group(1).strip(), m.group(2).strip()

    lo, hi = row(r"Core stratification S \(DERIVED\)")
    ref["S"], ref["S_increment"] = {}, {}
    for k, cell in (("lo", lo), ("hi", hi)):
        m = re.match(r"([\d.]+),", cell)
        if not m:
            refuse(f"REFUSE: cannot read S from Section 2.3 cell {cell!r}")
        ref["S"][k] = float(m.group(1))
        u = re.search(r"resolvable increment on S about\s*([\d.]+)", cell)
        if not u:
            refuse("REFUSE: the S row states no resolvable increment.")
        ref["S_increment"][k] = float(u.group(1))

    for name, label in (("Vup", r"Mid-height peak upward mean velocity \(DERIVED\)"),
                        ("Vdn", r"Mid-height peak downward mean velocity \(DERIVED\)")):
        lo, hi = row(label)
        ref[name], ref[name + "_x"] = {}, {}
        for k, cell in (("lo", lo), ("hi", hi)):
            m = re.match(r"([+-][\d.]+)\s*m/s at x =\s*([\d.]+)\s*mm", cell)
            if not m:
                refuse(f"REFUSE: cannot read '{label}' from cell {cell!r}")
            ref[name][k] = float(m.group(1))
            ref[name + "_x"][k] = float(m.group(2))

    lo, hi = row(r"Antisymmetry defect of the two peaks \(DERIVED\)")
    ref["asym"] = {}
    for k, cell in (("lo", lo), ("hi", hi)):
        m = re.match(r"([\d.]+)\s*percent", cell)
        if not m:
            refuse(f"REFUSE: cannot read the antisymmetry defect from {cell!r}")
        ref["asym"][k] = float(m.group(1))

    lo, hi = row(r"Mid-width mean temperature at y/H = 0\.30 / 0\.50 / 0\.70 \(DERIVED\)")
    ref["Tmid"] = {}
    for k, cell in (("lo", lo), ("hi", hi)):
        v = re.findall(r"([\d.]+)", cell)
        if len(v) < 3:
            refuse(f"REFUSE: cannot read the three mid-width temperatures from {cell!r}")
        ref["Tmid"][k] = [float(x) for x in v[:3]]

    # ---- Section 2.4 pass bands -------------------------------------------
    m = re.search(r"\|\s*Core stratification S, hi Ra\s*\|\s*\|S_solve\s*-\s*([\d.]+)\|\s*<=\s*([\d.]+)", txt)
    if not m:
        refuse("REFUSE: the Section 2.4 band on S at hi Ra could not be read.")
    if abs(float(m.group(1)) - ref["S"]["hi"]) > 1e-9:
        refuse("REFUSE: Section 2.4's S target disagrees with Section 2.3's S value.")
    bands["S_hi"] = float(m.group(2))

    m = re.search(r"\|\s*Core stratification S, lo Ra\s*\|\s*\|S_solve\|\s*<=\s*([\d.]+)", txt)
    if not m:
        refuse("REFUSE: the Section 2.4 bound on S at lo Ra could not be read.")
    bands["S_lo"] = float(m.group(1))

    m = re.search(r"\|\s*Mid-height peak velocities[^|]*\|\s*REL\s*<=\s*([\d.]+)\s*percent"
                  r"[^|]*peak location within\s*([\d.]+)\s*mm", txt)
    if not m:
        refuse("REFUSE: the Section 2.4 velocity band could not be read.")
    bands["V_pct"], bands["V_loc_mm"] = float(m.group(1)), float(m.group(2))

    m = re.search(r"\|\s*Mid-width temperature at y/H[^|]*\|\s*within\s*([\d.]+)\s*K \(lo\),"
                  r"\s*([\d.]+)\s*K \(hi\)", txt)
    if not m:
        refuse("REFUSE: the Section 2.4 mid-width temperature band could not be read.")
    bands["T_K"] = {"lo": float(m.group(1)), "hi": float(m.group(2))}

    m = re.search(r"\|\s*Antisymmetry of the two mid-height peaks\s*\|\s*defect\s*<=\s*([\d.]+)\s*percent", txt)
    if not m:
        refuse("REFUSE: the Section 2.4 antisymmetry band could not be read.")
    bands["asym_pct"] = float(m.group(1))

    m = re.search(r"temperature differentials\s*([\d.]+)\s*C and\s*([\d.]+)\s*C", txt)
    if not m:
        refuse("REFUSE: the two temperature differentials could not be read.")
    dT = {"lo": float(m.group(1)), "hi": float(m.group(2))}

    # ---- the NUSSELT PROVENANCE GUARD, carried unchanged from K0cT --------
    # Two-ended and whitespace-normalised.  Section 2.3's original "NOT
    # OBTAINED" sentence is superseded by addendum A1 BY DATE, never by
    # deletion (W-4), so BOTH must be present.  The first anchor is Section
    # 2.3's own continuation, not the bare sentence, because the bare sentence
    # now occurs three times -- once as the record and twice as A1's quotation
    # of it while superseding it.
    OLD_S = "reference NOT OBTAINED.** The database provides no Nusselt files"
    NEW_S = ("Nusselt number, turbulent rung: reference OBTAINED by addendum A1 "
             "dated 2026-08-18")
    if OLD_S not in flat:
        refuse("REFUSE: Section 2.3's original 'reference NOT OBTAINED' sentence "
               "has been REMOVED. It is superseded by date, never by deletion "
               "(W-4). Restore it; do not delete history to make a guard pass.")
    if NEW_S not in flat:
        refuse("REFUSE: addendum A1's marker sentence is absent; the Nusselt "
               "reference's provenance cannot be established.")

    m = re.search(r"\|\s*\*\*Average Nusselt number\*\*\s*\|\s*\*\*([\d.]+)\*\*"
                  r"\s*\|\s*\*\*([\d.]+)\*\*\s*\|", flat)
    if not m:
        refuse("REFUSE: the A1.2 'Average Nusselt number' row could not be read.")
    ref["Nu"] = {"lo": float(m.group(1)), "hi": float(m.group(2))}

    m = re.search(r"\|\s*\*\*u_val\*\*\s*\|\s*\*\*([\d.]+) %\*\*\s*\|\s*"
                  r"\*\*([\d.]+) %\*\*\s*\|", flat)
    if not m:
        refuse("REFUSE: the A1.5 u_val row could not be read.")
    bands["Nu_pct"] = {"lo": float(m.group(1)), "hi": float(m.group(2))}

    # the MEASURED Prt, A1.6b, for the sensitivity report
    rows = re.findall(
        r"\|\s*(lo|hi) Ra [\d.]+e6\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|"
        r"\s*\*\*([\d.]+)\*\*\s*\|\s*([\d.]+)\s*\|", flat)
    ref["Prt_measured"] = {k: float(v) for k, v, _ in rows}
    if set(ref["Prt_measured"]) != {"lo", "hi"}:
        refuse("REFUSE: A1.6b's measured turbulent Prandtl numbers could not be read.")

    # Betts Table 1's centre-line turbulence rows.  These are NOT gate rows --
    # the specification Section 2.4 does not grade them -- and they are parsed
    # so the rung can REPORT against them without inventing a band.
    m = re.search(r"\|\s*nu_T/nu at centre-line\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|", flat)
    if not m:
        refuse("REFUSE: A1.2's 'nu_T/nu at centre-line' row could not be read.")
    ref["nut_over_nu_centreline"] = {"lo": float(m.group(1)), "hi": float(m.group(2))}
    m = re.search(r"\|\s*Mid-cavity u'v' \(m2/s2 x 1e3\)\s*\|\s*([\d.]+)-([\d.]+)\s*"
                  r"\|\s*([\d.]+)-([\d.]+)\s*\|", flat)
    if not m:
        refuse("REFUSE: A1.2's mid-cavity u'v' row could not be read.")
    ref["uv_centreline"] = {"lo": [float(m.group(1)) * 1e-3, float(m.group(2)) * 1e-3],
                            "hi": [float(m.group(3)) * 1e-3, float(m.group(4)) * 1e-3]}

    return ref, bands, dT


def reference_from_primary(dT):
    """Re-derive Section 2.3's DERIVED metrics from the primary data files."""
    def load(fn):
        xs, vs = [], []
        for line in open(os.path.join(DATA, fn)):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split()
            try:
                xs.append(float(p[0])); vs.append(float(p[1]))
            except (ValueError, IndexError):
                continue
        return xs, vs

    def ip(xs, vs, xt):
        for i in range(len(xs) - 1):
            if xs[i] <= xt <= xs[i + 1]:
                f = (xt - xs[i]) / (xs[i + 1] - xs[i])
                return vs[i] + f * (vs[i + 1] - vs[i])
        return vs[-1] if xt > xs[-1] else vs[0]

    out = {}
    for suf in RUNGS:
        ys, Ts = [], []
        for yh in PROBE_YH:
            xs, vs = load(f"mt_z0_{int(round(yh*100)):02d}_{suf}.dat")
            ys.append(yh); Ts.append(ip(xs, vs, 38.0))
        xs, vs = load(f"mv_z0_50_{suf}.dat")
        imax = max(range(len(vs)), key=lambda i: vs[i])
        imin = min(range(len(vs)), key=lambda i: vs[i])
        out[suf] = dict(
            S=lsq_slope(ys, Ts) / dT[suf],
            Vup=vs[imax], Vup_x=xs[imax], Vdn=vs[imin], Vdn_x=xs[imin],
            asym=100.0 * abs(abs(vs[imax]) - abs(vs[imin]))
                 / max(abs(vs[imax]), abs(vs[imin])),
            Tmid=[Ts[PROBE_YH.index(y)] for y in REPORT_YH])
    return out


def lsq_slope(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            / sum((x - mx) ** 2 for x in xs))


# ===========================================================================
# OpenFOAM field reading
# ===========================================================================

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


def read_patch(path, patch):
    txt = open(path).read()
    i = txt.index("boundaryField")
    j = txt.index("\n    " + patch, i)
    seg = txt[j:]
    seg = seg[:seg.index("\n    }")]
    m = re.search(r"value\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(", seg)
    if m:
        k = seg.index("(", m.end() - 1) + 1
        return [float(v) for v in seg[k:seg.rindex(")")].split()]
    m = re.search(r"value\s+uniform\s+([-\d.eE+]+)", seg)
    if m:
        return [float(m.group(1))]
    if "zeroGradient" in seg or "calculated" in seg:
        return None
    refuse(f"REFUSE: could not read patch {patch} from {path}")


def case_txt(case, key):
    for line in open(os.path.join(case, "CASE.txt")):
        if line.startswith(key + " ") or line.startswith(key + "\t"):
            return line[len(key):].strip()
    refuse(f"REFUSE: '{key}' not in {case}/CASE.txt")


def latest_time(case):
    ts = []
    for e in os.listdir(case):
        if os.path.isdir(os.path.join(case, e)):
            try:
                if float(e) > 0:
                    ts.append((float(e), e))
            except ValueError:
                pass
    if not ts:
        refuse(f"REFUSE: no written time directory in {case}")
    return sorted(ts)[-1][1]


def face_widths(centres, L):
    """Exact cell widths from cell centres on a 1D block, reconstructed from
    f_{j+1} = 2 c_j - f_j.  Uniform in y on this mesh, but formed exactly so
    that an area average never silently becomes an arithmetic one -- the K0cS
    rung found every Nusselt number wrong by 10-27 percent from that mistake."""
    f = [0.0]
    for c in centres:
        f.append(2.0 * c - f[-1])
    if abs(f[-1] - L) > 1e-8 * max(L, 1.0):
        refuse(f"REFUSE: face reconstruction closed at {f[-1]!r}, not {L!r}.")
    return [f[i + 1] - f[i] for i in range(len(centres))]


def interp1(xs, vs, xt):
    if xt <= xs[0]:
        return vs[0]
    if xt >= xs[-1]:
        return vs[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= xt <= xs[i + 1]:
            f = (xt - xs[i]) / (xs[i + 1] - xs[i])
            return vs[i] + f * (vs[i + 1] - vs[i])
    return vs[-1]


# ===========================================================================
# measurement
# ===========================================================================

def measure(name):
    case = os.path.join(HERE, name)
    t = latest_time(case)
    r = foam(case, f"postProcess -func writeCellCentres -time {t} > log.cc 2>&1")
    if r.returncode != 0:
        refuse(f"REFUSE: writeCellCentres failed in {name}")
    cx = read_internal(os.path.join(case, t, "Cx"))
    cy = read_internal(os.path.join(case, t, "Cy"))
    for f in ("C", "Cx", "Cy", "Cz"):
        p = os.path.join(case, t, f)
        if os.path.isfile(p):
            os.remove(p)
    T = read_internal(os.path.join(case, t, "T"))
    U = read_internal(os.path.join(case, t, "U"), vector=True)

    H = float(case_txt(case, "H").split()[0])
    W = float(case_txt(case, "W").split()[0])
    dT = float(case_txt(case, "dT").split()[0])
    nu = float(case_txt(case, "nu").split()[0])
    Pr = float(case_txt(case, "Pr"))
    alpha = nu / Pr
    model = case_txt(case, "model")
    prt = float(case_txt(case, "Prt"))

    xs = sorted(set(round(v, 12) for v in cx))
    ys = sorted(set(round(v, 12) for v in cy))
    idx = {(round(x, 12), round(y, 12)): i for i, (x, y) in enumerate(zip(cx, cy))}

    def row_at_y(yt, field, comp=None):
        below = max([y for y in ys if y <= yt], default=ys[0])
        above = min([y for y in ys if y >= yt], default=ys[-1])
        f = 0.0 if above == below else (yt - below) / (above - below)
        out = []
        for x in xs:
            a, b = field[idx[(x, below)]], field[idx[(x, above)]]
            if comp is not None:
                a, b = a[comp], b[comp]
            out.append(a + f * (b - a))
        return out

    def col_at_x(xt, field):
        below = max([x for x in xs if x <= xt], default=xs[0])
        above = min([x for x in xs if x >= xt], default=xs[-1])
        f = 0.0 if above == below else (xt - below) / (above - below)
        return [field[idx[(below, y)]] + f * (field[idx[(above, y)]] - field[idx[(below, y)]])
                for y in ys]

    # --- core stratification, mid-width, y/H = 0.30 .. 0.70 -----------------
    Tcol = col_at_x(0.5 * W, T)
    Tprobe = [interp1(ys, Tcol, yh * H) for yh in PROBE_YH]
    S = lsq_slope(list(PROBE_YH), Tprobe) / dT
    Tmid_C = [interp1(ys, Tcol, yh * H) - 273.15 for yh in REPORT_YH]

    # --- mid-height vertical velocity ---------------------------------------
    Uy = row_at_y(0.5 * H, U, comp=1)
    imax = max(range(len(Uy)), key=lambda i: Uy[i])
    imin = min(range(len(Uy)), key=lambda i: Uy[i])
    Vup, Vup_x = Uy[imax], xs[imax] * 1000.0
    Vdn, Vdn_x = Uy[imin], xs[imin] * 1000.0
    asym = 100.0 * abs(abs(Vup) - abs(Vdn)) / max(abs(Vup), abs(Vdn))

    # --- average Nusselt, area-weighted, with the alphaEff wall factor -------
    alphat_p = os.path.join(case, t, "alphat")
    widths = face_widths(ys, H)
    tot = sum(widths)

    def wall_nu(patch, xwall):
        Tw = read_patch(os.path.join(case, t, "T"), patch)
        at = read_patch(alphat_p, patch) if os.path.isfile(alphat_p) else None
        xc = xs[0] if xwall == 0.0 else xs[-1]
        h2 = abs(xc - xwall)
        vals, aeffs = [], []
        for j, y in enumerate(ys):
            Tface = Tw[j] if len(Tw) > 1 else Tw[0]
            T1 = T[idx[(xc, y)]]
            aeff = 1.0
            if at is not None:
                aeff = 1.0 + (at[j] if len(at) > 1 else at[0]) / alpha
            aeffs.append(aeff)
            vals.append(abs(Tface - T1) / h2 * W / dT * aeff)
        return (sum(v * w for v, w in zip(vals, widths)) / tot,
                max(aeffs) - 1.0, vals)

    Nu_hot, wall_at_hot, hot_local = wall_nu("hotWall", W)
    Nu_cold, wall_at_cold, _ = wall_nu("coldWall", 0.0)
    Nu_avg = 0.5 * (Nu_hot + Nu_cold)

    # --- y+ at the first cell off each plate, from the solve's own gradient --
    # NOT from the yPlus function object, which reports the WALL FUNCTION's own
    # y+ and prints exactly zero where there is no wall function.  A zero
    # printed by a check that cannot see the quantity is not a measurement.
    yplus_max = 0.0
    for xwall, xc in ((W, xs[-1]), (0.0, xs[0])):
        h2 = abs(xc - xwall)
        for y in ys:
            u1 = U[idx[(xc, y)]]
            dudn = math.sqrt(u1[0] ** 2 + u1[1] ** 2) / h2
            yplus_max = max(yplus_max, h2 * math.sqrt(nu * dudn) / nu)

    # --- RELAMINARISATION DIAGNOSTICS ---------------------------------------
    # The K0cS rung's sharpest finding was a model that stopped modelling
    # turbulence when its near-wall mesh was refined.  These are the numbers
    # that showed it, computed the same way, on every case.
    diag = dict(nut_over_nu_max=0.0, nut_over_nu_centre=None,
                uv_centre=None, k_max=None, eps_max=None,
                Re_t_first_cell_midheight=None,
                fmu_launder_sharma_formula_first_cell=None,
                fmu_implied_max=None, cmu_k2_eps_max=None,
                uv_peak_midheight=None, nut_wall_over_alpha=None,
                wall_alphat_over_alpha=max(wall_at_hot, wall_at_cold))
    nutp = os.path.join(case, t, "nut")
    if os.path.isfile(nutp):
        nut = read_internal(nutp)
        diag["nut_over_nu_max"] = max(nut) / nu
        nut_row = row_at_y(0.5 * H, nut)
        uv, uvx = [], []
        for i in range(1, len(xs) - 1):
            dvdx = (Uy[i + 1] - Uy[i - 1]) / (xs[i + 1] - xs[i - 1])
            uv.append(abs(-nut_row[i] * dvdx))
            uvx.append(xs[i])
        diag["uv_peak_midheight"] = max(uv) if uv else 0.0
        # BETTS TABLE 1 REPORTS ITS EDDY VISCOSITY AND ITS u'v' AT THE
        # CENTRE-LINE, so the commensurate comparison is at the centre-line and
        # not at the domain maximum.  K0cT_NUSSELT_REGRADE.md 5.1 compared a
        # domain maximum against a centre-line value and said so; this measures
        # the like-for-like quantity beside it.
        diag["nut_over_nu_centre"] = interp1(xs, nut_row, 0.5 * W) / nu
        diag["uv_centre"] = interp1(uvx, uv, 0.5 * W) if uv else 0.0
        kp = os.path.join(case, t, "k")
        if os.path.isfile(kp):
            kf = read_internal(kp)
            diag["k_max"] = max(kf)
            # THE CAUSAL VARIABLE BEHIND RELAMINARISATION, measured directly.
            # LaunderSharmaKE damps with fMu = exp(-3.4/(1 + Re_t/50)^2) where
            # Re_t = k^2/(nu.epsilonTilda).  fMu is what collapsed at K0cS; Re_t
            # in the FIRST NEAR-WALL CELL is what drives it, and it is the
            # quantity that can be compared across two geometries.  Reported for
            # every two-equation model, and the formula is applied only where it
            # is the model's own.
            ep2 = os.path.join(case, t, "epsilon")
            if os.path.isfile(ep2):
                ef2 = read_internal(ep2)
                j = min(range(len(ys)), key=lambda q: abs(ys[q] - 0.5 * H))
                ret = []
                for xw in (xs[0], xs[-1]):
                    i = idx[(xw, ys[j])]
                    if ef2[i] > 1e-30:
                        ret.append(kf[i] ** 2 / (nu * ef2[i]))
                if ret:
                    diag["Re_t_first_cell_midheight"] = min(ret)
                    # The formula is LaunderSharmaKE's OWN and is evaluated only
                    # for that model.  kEpsilon has no fMu (it is identically 1),
                    # and printing an inapplicable damping function beside it
                    # would invite the reader to compare two different things.
                    # kEpsilon's implied fMu is computed the other way, from its
                    # written nut, and must come out at 1 -- which is this
                    # measurement's own sanity check.
                    if model == "LaunderSharmaKE":
                        diag["fmu_launder_sharma_formula_first_cell"] = math.exp(
                            -3.4 / (1.0 + min(ret) / 50.0) ** 2)
            ep = os.path.join(case, t, "epsilon")
            if os.path.isfile(ep):
                ef = read_internal(ep)
                diag["eps_max"] = max(ef)
                # nut = Cmu . fMu . k^2 / epsilonTilda  ->  fMu implied
                ratios, cmus = [], []
                for kk, ee, nn in zip(kf, ef, nut):
                    if kk > 1e-14 and ee > 1e-30:
                        c = CMU * kk * kk / ee
                        cmus.append(c)
                        if c > 1e-30:
                            ratios.append(nn / c)
                diag["cmu_k2_eps_max"] = max(cmus) if cmus else None
                diag["fmu_implied_max"] = max(ratios) if ratios else None

    # bounding-event counts come from the run's own completion marker, which the
    # runner wrote from the solver log at the moment the solve ended.
    mk = os.path.join(HERE, f"DONE.{name}")
    for key in ("bounding_k_events", "bounding_epsilon_events",
                "bounding_omega_events", "exec_seconds", "clock_seconds",
                "wall_seconds", "iterations"):
        diag[key] = None
    if os.path.isfile(mk):
        for line in open(mk):
            k, _, v = line.strip().partition("=")
            if k in diag:
                try:
                    diag[k] = float(v)
                except ValueError:
                    diag[k] = v

    return dict(
        case=name, time=t, model=model, cells=len(T), Prt=prt,
        rung=case_txt(case, "rung"), mesh_level=case_txt(case, "mesh_level"),
        S=S, Tmid_C=Tmid_C, Vup=Vup, Vup_x=Vup_x, Vdn=Vdn, Vdn_x=Vdn_x,
        asym=asym, Nu_hot=Nu_hot, Nu_cold=Nu_cold, Nu_avg=Nu_avg,
        yplus_max=yplus_max,
        # A NEAR-IDENTITY on a sealed cavity.  Reported, NEVER gated on
        # (VERIFICATION_CHARTER.md:106-111).
        heat_balance_pct=100.0 * abs(Nu_hot - Nu_cold) / Nu_avg,
        diagnostics=diag)


# ===========================================================================
# convergence
# ===========================================================================

def series(name, rel, col, vector_comp=None):
    p = os.path.join(HERE, name, "postProcessing", rel)
    if not os.path.isdir(p):
        return None
    rows = []
    for sub in sorted(os.listdir(p), key=lambda s: float(s)):
        for fn in os.listdir(os.path.join(p, sub)):
            for line in open(os.path.join(p, sub, fn)):
                if line.startswith("#"):
                    continue
                parts = line.replace("(", " ").replace(")", " ").split()
                if len(parts) <= col:
                    continue
                try:
                    rows.append((float(parts[0]), float(parts[col])))
                except ValueError:
                    pass
    ded = {}
    for it, v in sorted(rows):
        ded[it] = v
    return sorted(ded.items())


def spread(vals):
    return (max(vals) - min(vals)) if vals else None


def convergence(name, dT_rung):
    """Peak-to-peak over the last CONV_WINDOW iterations, sampled every
    CONV_STRIDE.  Registered in K0cX_PREREGISTRATION.md Section 6.1 BEFORE any
    case ran.  Not residuals, not an endpoint difference, and not loosened."""
    out = {}
    flux = series(name, "hotFlux", 1)
    if not flux:
        refuse(f"REFUSE: {name} has no hotFlux history; convergence cannot be "
               "measured and nothing is graded on a case whose steadiness is "
               "unknown.")
    last = flux[-1][0]
    win = [v for it, v in flux if it >= last - CONV_WINDOW]
    out["Nu_pct"] = 100.0 * spread(win) / abs(win[-1]) if win else None
    out["window_samples"] = len(win)
    # The pre-registration names a 400-iteration window sampled every 50, which
    # is nine samples.  Fewer means the window is not the registered one and the
    # spread is not the registered statistic.
    if len(win) < 9:
        refuse(f"REFUSE: {name} gives only {len(win)} samples in the registered "
               "400-iteration convergence window (nine required). The criterion "
               "is not loosened to fit the data available.")

    umax = series(name, "Uymax", 2)
    umin = series(name, "Uymin", 2)
    if umax:
        w = [v for it, v in umax if it >= last - CONV_WINDOW]
        wn = [v for it, v in umin if it >= last - CONV_WINDOW] if umin else []
        peak = max(abs(w[-1]), abs(wn[-1]) if wn else 0.0)
        out["Uy_pct"] = 100.0 * max(spread(w), spread(wn) if wn else 0.0) / peak
    else:
        out["Uy_pct"] = None

    # S from the five core probes
    pr = os.path.join(HERE, name, "postProcessing", "coreT")
    Sv = []
    if os.path.isdir(pr):
        rows = {}
        for sub in os.listdir(pr):
            for fn in os.listdir(os.path.join(pr, sub)):
                for line in open(os.path.join(pr, sub, fn)):
                    if line.startswith("#"):
                        continue
                    p = line.split()
                    if len(p) >= 6:
                        try:
                            rows[float(p[0])] = [float(v) for v in p[1:6]]
                        except ValueError:
                            pass
        for it in sorted(rows):
            if it >= last - CONV_WINDOW:
                Sv.append(lsq_slope(list(PROBE_YH), rows[it]) / dT_rung)
    out["S_abs"] = spread(Sv) if Sv else None
    out["S_window"] = [min(Sv), max(Sv)] if Sv else None

    fails = []
    for key, lim in (("Nu_pct", CONV["Nu_pct"]), ("S_abs", CONV["S_abs"]),
                     ("Uy_pct", CONV["Uy_pct"])):
        if out[key] is None or out[key] > lim:
            fails.append(key)
    out["failed"] = fails
    out["converged"] = not fails
    return out


# ===========================================================================
# grading
# ===========================================================================

def rows_for(rung, meas, ref, bands):
    """The ten graded rows at one Rayleigh number."""
    R, B = ref, bands
    out = []

    def add(tag, quantity, reference, value, dev, band, unit, note=""):
        out.append(dict(rung=rung, tag=tag, quantity=quantity,
                        reference=reference, value=value, deviation=dev,
                        band=band, unit=unit,
                        verdict="PASS" if dev <= band else "GATE FAIL",
                        note=note))

    if rung == "hi":
        add("R1", "core stratification S", R["S"]["hi"], meas["S"],
            abs(meas["S"] - R["S"]["hi"]), B["S_hi"], "absolute")
    else:
        add("R1", "core stratification S (BOUND)", 0.0, meas["S"],
            abs(meas["S"]), B["S_lo"], "absolute",
            "reference 0.016 is below its own 0.02 resolvable increment, so "
            "the specification makes this row a bound and not a target")
    add("R2", "mid-height peak upward velocity, magnitude", R["Vup"][rung],
        meas["Vup"], 100.0 * abs(meas["Vup"] - R["Vup"][rung]) / abs(R["Vup"][rung]),
        B["V_pct"], "percent")
    add("R3", "mid-height peak upward velocity, location", R["Vup_x"][rung],
        meas["Vup_x"], abs(meas["Vup_x"] - R["Vup_x"][rung]), B["V_loc_mm"], "mm")
    add("R4", "mid-height peak downward velocity, magnitude", R["Vdn"][rung],
        meas["Vdn"], 100.0 * abs(meas["Vdn"] - R["Vdn"][rung]) / abs(R["Vdn"][rung]),
        B["V_pct"], "percent")
    add("R5", "mid-height peak downward velocity, location", R["Vdn_x"][rung],
        meas["Vdn_x"], abs(meas["Vdn_x"] - R["Vdn_x"][rung]), B["V_loc_mm"], "mm")
    for i, yh in enumerate(REPORT_YH):
        add(f"R{6+i}", f"mid-width temperature at y/H = {yh:.2f}",
            R["Tmid"][rung][i], meas["Tmid_C"][i],
            abs(meas["Tmid_C"][i] - R["Tmid"][rung][i]), B["T_K"][rung], "K")
    add("R9", "antisymmetry defect of the two peaks", R["asym"][rung],
        meas["asym"], meas["asym"], B["asym_pct"], "percent-absolute",
        "a 2-D Boussinesq cavity is nearly centro-symmetric by construction; "
        "K0cT_RESULTS.md 2.1 already records this row as NOT evidence")
    E = 100.0 * (meas["Nu_avg"] - R["Nu"][rung]) / R["Nu"][rung]
    r = dict(rung=rung, tag="R10", quantity="average Nusselt number",
             reference=R["Nu"][rung], value=meas["Nu_avg"],
             deviation=abs(E), signed_deviation=E, band=B["Nu_pct"][rung],
             unit="percent", verdict="PASS" if abs(E) <= B["Nu_pct"][rung] else "GATE FAIL",
             E_over_uval=abs(E) / B["Nu_pct"][rung],
             inside_transferred_caution=bool(abs(E) <= TRANSFERRED_CAUTION_PCT),
             note="band is addendum A1.5's u_val, external to every solve value")
    out.append(r)
    return out


def gate_table(graded, laminar_rows, disc, path):
    L = []
    L.append("# K0cX gate table -- generated by analyse_k0cx.py, not retyped\n")
    L.append(f"Generated {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}.\n")
    L.append("Reference values and bands parsed at run time from "
             "`docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` "
             "Sections 2.3, 2.4 and addendum A1.2/A1.5. Graded on the FINE mesh of "
             "the mandatory pair; the COARSE mesh is carried in every row.\n")
    for tag in ("SST", "KE", "LS"):
        if tag not in graded:
            continue
        g = graded[tag]
        nf = sum(1 for r in g["rows"] if r["verdict"] != "PASS")
        L.append(f"\n## {MODELS[tag]} -- {g['verdict']}, {nf} of {len(g['rows'])} graded rows failed\n")
        L.append("| Ra | row | quantity | reference | coarse | **fine** | deviation | band | unit | verdict | laminar same row |")
        L.append("| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |")
        for r in g["rows"]:
            lam = laminar_rows.get((r["rung"], r["tag"]))
            lamtxt = (f"{lam['value']:.4g} ({lam['verdict']})" if lam else "-")
            L.append(f"| {r['rung']} | {r['tag']} | {r['quantity']} | "
                     f"{r['reference']:.4g} | {r.get('coarse', float('nan')):.4g} | "
                     f"**{r['value']:.4g}** | {r['deviation']:.4g} | {r['band']:.4g} | "
                     f"{r['unit']} | **{r['verdict']}** | {lamtxt} |")
    L.append("\n## Discrimination against the laminar control\n")
    L.append("| model | D-a: rows the model PASSES and laminar FAILS | count | D-b: rows separated by more than the band | count |")
    L.append("| --- | --- | ---: | --- | ---: |")
    for tag in ("SST", "KE", "LS"):
        if tag not in disc:
            continue
        d = disc[tag]
        L.append(f"| {MODELS[tag]} | {', '.join(d['Da']) or '**EMPTY**'} | {len(d['Da'])} | "
                 f"{', '.join(d['Db']) or '**EMPTY**'} | {len(d['Db'])} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ref, bands, dT = read_spec()

    # the specification's DERIVED rows, RE-DERIVED from the primary files
    prim = reference_from_primary(dT)
    crosscheck = {}
    for rung in RUNGS:
        crosscheck[rung] = {
            "S": [ref["S"][rung], prim[rung]["S"]],
            "Vup": [ref["Vup"][rung], prim[rung]["Vup"]],
            "Vdn": [ref["Vdn"][rung], prim[rung]["Vdn"]],
        }
        if abs(prim[rung]["S"] - ref["S"][rung]) > 0.002:
            refuse(f"REFUSE: Section 2.3's S at {rung} Ra ({ref['S'][rung]}) does "
                   f"not re-derive from the primary files ({prim[rung]['S']:.4f}).")

    present = [c for c in sorted(os.listdir(HERE))
               if os.path.isdir(os.path.join(HERE, c))
               and os.path.isfile(os.path.join(HERE, c, "CASE.txt"))]
    done = {c for c in present if os.path.isfile(os.path.join(HERE, f"DONE.{c}"))}
    missing = sorted(set(present) - done)

    meas, conv = {}, {}
    for c in sorted(done):
        meas[c] = measure(c)
        conv[c] = convergence(c, dT[meas[c]["rung"]])

    # ---- graded models -----------------------------------------------------
    graded, laminar_rows = {}, {}
    for rung in RUNGS:
        cf = f"X_{rung}_f_LAM"
        if cf in meas:
            for r in rows_for(rung, meas[cf], ref, bands):
                laminar_rows[(rung, r["tag"])] = r

    for tag in ("SST", "KE", "LS", "LAM"):
        rows, refused = [], []
        for rung in RUNGS:
            cc, cfi = f"X_{rung}_c_{tag}", f"X_{rung}_f_{tag}"
            if cfi not in meas or cc not in meas:
                refused.append(f"{rung}: mesh pair incomplete "
                               f"({'fine' if cfi not in meas else 'coarse'} missing); "
                               "specification 2.5 forbids grading a solve without "
                               "its grid-sensitivity pair")
                continue
            if not conv[cfi]["converged"]:
                refused.append(f"{rung}: {cfi} REFUSED, convergence failed on "
                               f"{','.join(conv[cfi]['failed'])}")
            rr = rows_for(rung, meas[cfi], ref, bands)
            cr = {x["tag"]: x for x in rows_for(rung, meas[cc], ref, bands)}
            for r in rr:
                r["coarse"] = cr[r["tag"]]["value"]
                r["coarse_deviation"] = cr[r["tag"]]["deviation"]
                r["coarse_verdict"] = cr[r["tag"]]["verdict"]
                r["mesh_moved_toward_experiment"] = bool(
                    r["deviation"] < r["coarse_deviation"])
            rows.extend(rr)
        nfail = sum(1 for r in rows if r["verdict"] != "PASS")
        graded[tag] = dict(
            model=MODELS[tag], rows=rows, n_rows=len(rows), n_fail=nfail,
            convergence_refusals=refused,
            verdict=("NOT A RESULT" if not rows else
                     ("PASS" if nfail == 0 else "GATE FAIL")))

    # ---- discrimination against the laminar control -------------------------
    disc = {}
    for tag in ("SST", "KE", "LS"):
        Da, Db, both_fail = [], [], []
        for r in graded[tag]["rows"]:
            lam = laminar_rows.get((r["rung"], r["tag"]))
            if not lam:
                continue
            key = f"{r['rung']}/{r['tag']}"
            if r["verdict"] == "PASS" and lam["verdict"] != "PASS":
                Da.append(key)
            # The separation threshold is the row's OWN band, expressed in the
            # row's own units.  "percent" bands are percentages OF THE
            # REFERENCE, so they convert; "percent-absolute" (the antisymmetry
            # defect, whose VALUE is itself a percentage) does not, and getting
            # that wrong made the antisymmetry row separate at 0.05 percent
            # instead of 10.
            if r["unit"] == "percent":
                thr = r["band"] * abs(r["reference"]) / 100.0
            elif r["unit"] in ("absolute", "mm", "K", "percent-absolute"):
                thr = r["band"]
            else:
                refuse(f"REFUSE: no separation threshold defined for unit "
                       f"{r['unit']!r}; a row cannot be silently skipped.")
            if abs(r["value"] - lam["value"]) > thr:
                Db.append(key)
            if r["verdict"] != "PASS" and lam["verdict"] != "PASS":
                both_fail.append(key)
        disc[tag] = dict(Da=Da, Db=Db, both_fail=both_fail,
                         Da_empty=(len(Da) == 0))

    # ---- mutation control: every graded row flippable both ways -------------
    # EVERY ROW IS RE-GRADED AGAINST A MUTATED REFERENCE, and the verdict must
    # actually flip in both directions.  The first version of this control
    # asserted `0 <= band` and `10*band > band` -- arithmetic truisms that never
    # call the grader at all.  A check that cannot fail is decorative, and this
    # lab has shipped three false zeros from checks whose populations were
    # empty.
    mutation = []
    for tag in ("SST", "KE", "LS"):
        for rung in RUNGS:
            cfi = f"X_{rung}_f_{tag}"
            if cfi not in meas:
                continue
            m = meas[cfi]
            # (a) reference driven ONTO the solve value -> every row must PASS
            ref_pass = copy.deepcopy(ref)
            ref_pass["S"][rung] = m["S"]
            ref_pass["Vup"][rung], ref_pass["Vdn"][rung] = m["Vup"], m["Vdn"]
            ref_pass["Vup_x"][rung], ref_pass["Vdn_x"][rung] = m["Vup_x"], m["Vdn_x"]
            ref_pass["Tmid"][rung] = list(m["Tmid_C"])
            ref_pass["asym"][rung] = m["asym"]
            ref_pass["Nu"][rung] = m["Nu_avg"]
            got_pass = {r["tag"]: r["verdict"] for r in rows_for(rung, m, ref_pass, bands)}
            # (b) reference driven 10 bands AWAY -> every row must FAIL
            ref_fail = copy.deepcopy(ref)
            B = bands
            sb = B["S_hi"] if rung == "hi" else B["S_lo"]
            ref_fail["S"][rung] = m["S"] + 10.0 * sb
            ref_fail["Vup"][rung] = m["Vup"] * (1.0 + 10.0 * B["V_pct"] / 100.0)
            ref_fail["Vdn"][rung] = m["Vdn"] * (1.0 + 10.0 * B["V_pct"] / 100.0)
            ref_fail["Vup_x"][rung] = m["Vup_x"] + 10.0 * B["V_loc_mm"]
            ref_fail["Vdn_x"][rung] = m["Vdn_x"] + 10.0 * B["V_loc_mm"]
            ref_fail["Tmid"][rung] = [t + 10.0 * B["T_K"][rung] for t in m["Tmid_C"]]
            ref_fail["asym"][rung] = m["asym"]        # R9 grades the VALUE
            ref_fail["Nu"][rung] = m["Nu_avg"] / (1.0 + 10.0 * B["Nu_pct"][rung] / 100.0)
            got_fail = {r["tag"]: r["verdict"] for r in rows_for(rung, m, ref_fail, bands)}
            # R9's verdict does not depend on the reference at all -- the
            # specification grades the DEFECT itself against 10 percent.  Its
            # FAIL branch is reached by mutating the SOLVE value instead, and
            # that asymmetry is recorded rather than papered over.
            m9 = dict(m); m9["asym"] = bands["asym_pct"] * 10.0
            got_fail["R9"] = {r["tag"]: r["verdict"]
                              for r in rows_for(rung, m9, ref, bands)}["R9"]
            # R1 at lo Ra is a BOUND on |S| and likewise ignores the reference.
            if rung == "lo":
                m1 = dict(m); m1["S"] = m["S"] + 10.0 * bands["S_lo"]
                got_fail["R1"] = {r["tag"]: r["verdict"]
                                  for r in rows_for(rung, m1, ref, bands)}["R1"]
                got_pass["R1"] = {r["tag"]: r["verdict"] for r in rows_for(
                    "lo", dict(m, S=0.0), ref, bands)}["R1"]
            for t in sorted(got_pass):
                mutation.append(dict(
                    model=tag, rung=rung, tag=t,
                    reachable_PASS=(got_pass[t] == "PASS"),
                    reachable_FAIL=(got_fail[t] != "PASS")))
    every_reachable = all(m["reachable_PASS"] and m["reachable_FAIL"]
                          for m in mutation)

    total_rows = sum(graded[t]["n_rows"] for t in ("SST", "KE", "LS"))
    total_fail = sum(graded[t]["n_fail"] for t in ("SST", "KE", "LS"))

    out = dict(
        generated_utc=datetime.datetime.now(datetime.timezone.utc)
                          .strftime("%Y-%m-%dT%H:%M:%SZ"),
        specification=SPEC,
        reference_parsed=ref, bands_parsed=bands,
        reference_cross_check_against_primary_files=crosscheck,
        convergence_criterion=CONV,
        transferred_caution_pct=TRANSFERRED_CAUTION_PCT,
        cases_present=present, cases_missing_marker=missing,
        measurements=meas, convergence=conv,
        graded=graded, laminar_rows={f"{k[0]}/{k[1]}": v
                                     for k, v in laminar_rows.items()},
        discrimination=disc,
        mutation_control=mutation, every_row_reachable_both_ways=every_reachable,
        rung_verdict=("GATE FAIL" if total_fail else "PASS"),
        total_graded_rows=total_rows, total_failed_rows=total_fail)
    with open(os.path.join(HERE, "gate_k0cx.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    gate_table(graded, laminar_rows, disc, os.path.join(HERE, "GATE_TABLE.md"))

    print("K0cX CROSS-GEOMETRY RUNG -- Betts and Bokhari tall cavity")
    print("=" * 96)
    for tag in ("SST", "KE", "LS", "LAM"):
        g = graded[tag]
        lab = "control, NOT counted" if tag == "LAM" else g["verdict"]
        print(f"{MODELS[tag]:<18} {lab:<14} {g['n_fail']} of {g['n_rows']} rows failed")
        for r in g["convergence_refusals"]:
            print(f"    REFUSAL  {r}")
    print("-" * 96)
    for tag in ("SST", "KE", "LS"):
        d = disc[tag]
        print(f"{MODELS[tag]:<18} D-a {len(d['Da']):>2} rows "
              f"{'*** EMPTY -- this gate cannot tell the model from no model ***' if d['Da_empty'] else d['Da']}")
        print(f"{'':18} D-b {len(d['Db']):>2} rows separated by more than the band")
    print("-" * 96)
    print(f"graded rows {total_rows}   FAIL {total_fail}   "
          f"rung verdict: {out['rung_verdict']}")
    print(f"every graded row reachable both ways: {every_reachable}")
    if missing:
        print(f"NO COMPLETION MARKER (not measured): {missing}")
    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
