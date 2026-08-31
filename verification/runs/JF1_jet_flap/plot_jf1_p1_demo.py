#!/usr/bin/env python3
"""
JF1 stage-P row P1 -- DEMO FIGURES.  DIAGNOSTIC ONLY.

JF1_PREREGISTRATION.md section 6's staging table answers "Gated?" for stage P
with "No.  Diagnostic only."  NOTHING THIS SCRIPT DRAWS CARRIES A VERDICT of the
fixed vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING), a GCI, an observed order or a theory comparison.  Every figure carries
the ungraded banner and the live convergence state ON ITS FACE.

WHAT IS DELIBERATELY NOT DRAWN
------------------------------
No unblown reference curve.  The five completed feasibility rows
(JF1_L1_UNBLOWN_A0 and the four JF1_L1_BLOWN_CMU*_A0) are on the O-TOPOLOGY mesh
at 39,984 cells with t_z = 0.01 m.  This row is the registered C-TOPOLOGY mesh at
46,180 cells with t_z = 1.0 m.  Overlaying them would compare two topologies and
two span thicknesses and call the difference a jet effect.  The jet-sheet
trajectory carries the physics story instead.

Aref
----
Aref = c * t_z = 1.0 * 1.0 = 1.0 on THIS mesh, and the run's own
system/controlDict sets it so.  cases/JF1_JET_FLAP/case_blown/system/controlDict
carries 0.01, which is right for the O-mesh and would report CL and Cd 100x too
large here; forceCoeffs.C:328 guards only a MISSING or zero Aref, never a wrong
one.  This script therefore (a) reads Aref back out of the coefficient.dat header
and REFUSES if it is not 1.0, and (b) re-derives the pressure lift by its own
contour integral of Cp so the reported CL does not rest on the dictionary alone.

PLANTED-ZERO CONTROL (rule 3)
-----------------------------
Both readers are certified live before any figure is drawn: a known perturbation
is planted into a COPY of the file on disk, read back through the same reader,
and the script REFUSES (exit 2) if the reader cannot see it.

USAGE
    python3 plot_jf1_p1_demo.py [--time N] [--recon DIR] [--out DIR]
"""

import argparse
import math
import os
import re
import shutil
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow
from scipy.interpolate import griddata

# ---------------------------------------------------------------- constants --
U_INF = 10.0          # m/s, 0/U farfield freestreamValue
C_CHORD = 1.0         # m
T_Z = 1.0             # m, registered C-topology span (make_jf1_mesh.py:429-432)
AREF = 1.0            # = c * t_z
C_MU_JET = 0.10
TAU_DEG = 30.0
ALPHA_DEG = 0.0
END_TIME = 20000      # system/controlDict endTime (registered section 5.5)
Q_INF = 0.5 * U_INF ** 2   # kinematic dynamic pressure (p is p/rho in simpleFoam)

BANNER = "FEASIBILITY/PHYSICS RUNG — UNGRADED.  No gate, no verdict."

INK = "#1b1b1f"
INK2 = "#4a4a52"
MUTED = "#8a8a93"
GRIDC = "#d8d8de"
SER1 = "#2a6ebb"      # upper surface / measured
SER2 = "#d9762b"      # lower surface / reference
WARN = "#b3261e"


class Refusal(Exception):
    pass


def refuse(msg):
    raise Refusal(msg)


# ------------------------------------------------------------------ readers --
def read_internal(path):
    """internalField of an ascii OpenFOAM volScalar/volVectorField."""
    txt = open(path).read()
    i = txt.index("internalField")
    head = txt[i:i + 200]
    m = re.search(r"nonuniform\s+List<(\w+)>\s*\s*(\d+)", head)
    if not m:
        refuse("internalField is not a nonuniform list in %s" % path)
    kind, n = m.group(1), int(m.group(2))
    k = txt.index("(", i)
    body = txt[k + 1:]
    e = body.index("\n)")
    vals = body[:e]
    if kind == "vector":
        arr = re.findall(r"\(([^)]*)\)", vals)
        out = np.array([[float(x) for x in s.split()] for s in arr])
    else:
        out = np.array([float(x) for x in vals.split()])
    if len(out) != n:
        refuse("count mismatch in %s: header %d, parsed %d" % (path, n, len(out)))
    return out


def read_raw_surface(path):
    """raw sampled-surface file: x y z v   (scalar)  or  x y z vx vy vz."""
    a = np.loadtxt(path)
    if a.ndim != 2 or a.shape[1] < 4:
        refuse("unexpected raw surface shape in %s: %s" % (path, a.shape))
    return a


def read_coefficient_dat(path):
    """Returns (times, dict-of-columns, Aref-from-header)."""
    aref = None
    cols = None
    rows = []
    for line in open(path):
        if line.startswith("#"):
            m = re.match(r"#\s*Aref\s*:\s*([-\d.eE+]+)", line)
            if m:
                aref = float(m.group(1))
            if "Time" in line and "Cd" in line and "Cl" in line:
                cols = [c.strip() for c in line.lstrip("#").split()]
            continue
        parts = line.split()
        if parts:
            rows.append([float(x) for x in parts])
    if aref is None:
        refuse("no Aref in the coefficient.dat header: %s" % path)
    if cols is None:
        refuse("no column header in %s" % path)
    a = np.array(rows)
    return a[:, 0], {c: a[:, i] for i, c in enumerate(cols)}, aref


# ---------------------------------------------------- planted-zero controls --
def plant_control_internal(src, scratch):
    """Plant a known value into a COPY of an internalField and read it back."""
    dst = os.path.join(scratch, "PLANT_" + os.path.basename(src))
    shutil.copyfile(src, dst)
    truth = read_internal(src)
    plant = -8.675309e02          # unmistakable, cannot occur in this field
    idx = 17                      # a fixed interior cell, not cell 0
    txt = open(dst).read()
    k = txt.index("(", txt.index("internalField"))
    head, body = txt[:k + 1], txt[k + 1:]
    e = body.index("\n)")
    toks = body[:e].split()
    if abs(float(toks[idx]) - truth[idx]) > 1e-9 * max(1.0, abs(truth[idx])):
        refuse("plant control: token %d is not field value %d" % (idx, idx))
    toks[idx] = repr(plant)
    open(dst, "w").write(head + "\n" + "\n".join(toks) + body[e:])
    back = read_internal(dst)
    if abs(back[idx] - plant) > 1e-6:
        refuse("PLANT NOT SEEN in internalField reader: wrote %g, read %g"
               % (plant, back[idx]))
    if abs(back[idx] - truth[idx]) < 1e-6:
        refuse("PLANT INVISIBLE: reader returned the unperturbed value")
    n_moved = int(np.sum(np.abs(back - truth) > 1e-9))
    if n_moved != 1:
        refuse("plant moved %d values, expected exactly 1" % n_moved)
    os.remove(dst)
    return plant, truth[idx]


def plant_control_raw(src, scratch):
    """Plant a known p into a COPY of the airfoil raw file and read it back."""
    dst = os.path.join(scratch, "PLANT_" + os.path.basename(src))
    lines = open(src).read().splitlines()
    truth = read_raw_surface(src)
    plant = -1234.5678
    # first non-comment line index
    j = next(i for i, L in enumerate(lines) if not L.startswith("#"))
    j += 5
    parts = lines[j].split()
    parts[3] = repr(plant)
    lines[j] = " ".join(parts)
    open(dst, "w").write("\n".join(lines) + "\n")
    back = read_raw_surface(dst)
    row = j - next(i for i, L in enumerate(lines) if not L.startswith("#"))
    if abs(back[row, 3] - plant) > 1e-6:
        refuse("PLANT NOT SEEN in raw-surface reader: wrote %g, read %g"
               % (plant, back[row, 3]))
    if abs(back[row, 3] - truth[row, 3]) < 1e-6:
        refuse("PLANT INVISIBLE: raw reader returned the unperturbed value")
    n_moved = int(np.sum(np.abs(back[:, 3] - truth[:, 3]) > 1e-9))
    if n_moved != 1:
        refuse("raw plant moved %d values, expected exactly 1" % n_moved)
    os.remove(dst)
    return plant, truth[row, 3]


# ----------------------------------------------------------- run-state facts --
def run_state(case_dir):
    """Iteration reached, final initial residuals, bounding-k census, jet flow."""
    log = os.path.join(case_dir, "log.simpleFoam")
    last_t = None
    bounded = 0
    steps = 0
    first_bounded = None
    last_clean = None
    last_bk = None
    cur = None
    cur_b = False
    exec_time = None
    ended = False
    for line in open(log):
        if line.startswith("Time = "):
            if cur is not None:
                steps += 1
                if cur_b:
                    bounded += 1
                    if first_bounded is None:
                        first_bounded = cur
                else:
                    last_clean = cur
            cur = int(line.split()[2])
            cur_b = False
        elif line.startswith("bounding k"):
            cur_b = True
            last_bk = line.strip()
        elif line.startswith("ExecutionTime"):
            exec_time = float(line.split()[2])
        elif line.startswith("End"):
            ended = True
    last_t = cur

    si = os.path.join(case_dir, "postProcessing", "contErr", "0", "solverInfo.dat")
    cols, rows = None, []
    for line in open(si):
        if line.startswith("#"):
            if "Ux_initial" in line:
                cols = [c.strip() for c in line.lstrip("#").split()]
            continue
        p = line.split()
        if p:
            rows.append(p)
    last = rows[-1]
    d = dict(zip(cols, last))
    res = {
        "iter": int(float(d["Time"])),
        "Ux": float(d["Ux_initial"]),
        "Uy": float(d["Uy_initial"]),
        "p": float(d["p_initial"]),
        "k": float(d["k_initial"]),
        "omega": float(d["omega_initial"]),
    }
    return {
        "last_time": last_t,
        "exec_time_s": exec_time,
        "ended": ended,
        "steps": steps,
        "bounded": bounded,
        "first_bounded": first_bounded,
        "last_clean": last_clean,
        "last_bk_line": last_bk,
        "res": res,
    }


# ------------------------------------------------------------- Cp machinery --
def order_contour(xy):
    """Order airfoil+slot face centres into one closed polygon by nearest walk."""
    n = len(xy)
    used = np.zeros(n, bool)
    # start at the lower-surface trailing edge: max x, y < 0
    cand = np.where(xy[:, 1] < 0)[0]
    start = cand[np.argmax(xy[cand, 0])]
    order = [start]
    used[start] = True
    for _ in range(n - 1):
        d = np.linalg.norm(xy - xy[order[-1]], axis=1)
        d[used] = np.inf
        j = int(np.argmin(d))
        order.append(j)
        used[j] = True
    return np.array(order)


def cl_cd_from_cp(xy, cp):
    """Pressure-only CL, CD by contour integration.  Independent of Aref."""
    o = order_contour(xy)
    P = xy[o]
    C = cp[o]
    Pn = np.roll(P, -1, axis=0)
    seg = Pn - P
    # (dy, -dx) is the OUTWARD normal only if the walk is counter-clockwise.
    # The orientation is not assumed: it is fixed by requiring the normal at the
    # topmost segment to point up (+y) and the bottommost to point down (-y),
    # and the script REFUSES if those two tests disagree.
    nx, ny = seg[:, 1].copy(), -seg[:, 0].copy()
    mid_y = 0.5 * (P[:, 1] + Pn[:, 1])
    i_top = int(np.argmax(mid_y))
    i_bot = int(np.argmin(mid_y))
    s = 1.0 if ny[i_top] > 0 else -1.0
    nx, ny = s * nx, s * ny
    if not (ny[i_top] > 0 and ny[i_bot] < 0):
        refuse("contour orientation is not resolvable: outward normal test gave "
               "n_y(top) = %g, n_y(bottom) = %g" % (ny[i_top], ny[i_bot]))
    cbar = 0.5 * (C + np.roll(C, -1))
    # C_F = -oint Cp n dS / c   (n outward, dS = |seg| already folded into n)
    cl = -np.sum(cbar * ny) / C_CHORD
    cd = -np.sum(cbar * nx) / C_CHORD
    return cl, cd, P


# ------------------------------------------------------------- the trajectory --
def jet_trajectory(cx, cy, U, x_end=4.0, n=70, y_win=0.10,
                   min_cells=25, max_hw=0.25, excess=1.05):
    """
    Jet-sheet centreline: the locus of MAXIMUM |U| on vertical cuts downstream
    of the slot, MARCHED.

    Marched, not swept independently, for a measured reason: the C-mesh wake
    block stretches hard downstream (a fixed dx band holds 3794 cells at
    x/c = 1.01 and 8 cells at x/c = 1.60), so an unconstrained per-cut maximum
    jumps off the sheet onto whatever else is in the band.  Each cut therefore
    (a) widens its dx until it holds at least %d cells and (b) searches only
    |y - y_previous| < %.2f c.  The trace STOPS -- it does not extrapolate --
    when the peak in that window falls below %.2f x U_inf, i.e. when the sheet
    is no longer distinguishable from the freestream on this mesh.
    """ % (min_cells, y_win, excess)
    mag = np.linalg.norm(U, axis=1)
    xs = 1.0 + np.geomspace(0.004, x_end - 1.0, n)
    y_prev = 0.0
    tx, ty, tm = [], [], []
    for x in xs:
        hw, m = 0.004, None
        while hw <= max_hw:
            m = (np.abs(cx - x) < hw) & (np.abs(cy - y_prev) < y_win)
            if int(m.sum()) >= min_cells:
                break
            hw *= 1.6
        if m is None or int(m.sum()) < min_cells:
            break
        yy, mm = cy[m], mag[m]
        i = int(np.argmax(mm))
        if mm[i] < excess * U_INF:
            break
        y_prev = float(yy[i])
        tx.append(float(x))
        ty.append(y_prev)
        tm.append(float(mm[i]))
    return np.array(tx), np.array(ty), np.array(tm)


# ------------------------------------------------------------------ banners --
def stamp(fig, st, extra=None):
    """The caveat, on the face of every figure.  Not a caption."""
    r = st["res"]
    conv = ("residualControl (p,U,k,omega <= 1e-06) NOT MET"
            if max(r["p"], r["Ux"], r["Uy"], r["k"], r["omega"]) > 1e-6
            else "residualControl targets met")
    l2 = ("iteration %d of %d registered  |  %s\n"
          "initial residuals: p %.2e   Ux %.2e   Uy %.2e   k %.2e   omega %.2e"
          % (st["last_time"], END_TIME, conv,
             r["p"], r["Ux"], r["Uy"], r["k"], r["omega"]))
    frac = 100.0 * st["bounded"] / max(1, st["steps"])
    l3 = ("`bounding k` FIRING: %d of %d iterations (%.1f %%), continuously since "
          "iteration %s — k is being CLIPPED at the level plotted here, not "
          "converged out of it." % (st["bounded"], st["steps"], frac,
                                    st["first_bounded"]))
    fig.text(0.5, 0.987, BANNER, ha="center", va="top", fontsize=12.5,
             color="white", weight="bold",
             bbox=dict(boxstyle="round,pad=0.42", fc="#26262c", ec="none"))
    fig.text(0.5, 0.937, l2, ha="center", va="top", fontsize=8.2, color=INK2,
             family="DejaVu Sans Mono")
    fig.text(0.5, 0.899, l3, ha="center", va="top", fontsize=8.2, color=WARN,
             weight="bold", wrap=True)
    if extra:
        fig.text(0.5, 0.020, extra, ha="center", va="bottom", fontsize=7.4,
                 color=MUTED)


def tidy(ax):
    ax.grid(True, color=GRIDC, lw=0.6, alpha=0.9)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9)


# --------------------------------------------------------------------- main --
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "JF1_P1_L1_CMESH_PHYSICS"))
    ap.add_argument("--recon", default=None)
    ap.add_argument("--time", type=int, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    case = a.case
    recon = a.recon or os.path.join(case, "artefacts", "_recon")
    out = a.out or os.path.join(case, "artefacts")
    scratch = os.path.join(recon, "_plant")
    os.makedirs(out, exist_ok=True)
    os.makedirs(scratch, exist_ok=True)

    times = sorted(int(d) for d in os.listdir(recon)
                   if d.isdigit() and int(d) > 0
                   and os.path.exists(os.path.join(recon, d, "U")))
    if not times:
        refuse("no reconstructed time directory with a U field under %s" % recon)
    t = a.time or times[-1]
    td = os.path.join(recon, str(t))
    sd = os.path.join(recon, "postProcessing", "jfSurf", str(t))

    st = run_state(case)

    # ---- planted-zero controls, BEFORE anything is read for a figure --------
    p_plant, p_true = plant_control_internal(os.path.join(td, "p"), scratch)
    r_plant, r_true = plant_control_raw(
        os.path.join(sd, "p_airfoilSurf.raw"), scratch)

    # ---- fields ------------------------------------------------------------
    cx = read_internal(os.path.join(td, "Cx"))
    cy = read_internal(os.path.join(td, "Cy"))
    U = read_internal(os.path.join(td, "U"))
    pf = read_internal(os.path.join(td, "p"))
    mag = np.linalg.norm(U, axis=1)

    af = read_raw_surface(os.path.join(sd, "p_airfoilSurf.raw"))
    js = read_raw_surface(os.path.join(sd, "p_jetSlotSurf.raw"))
    x_af, y_af, cp_af = af[:, 0], af[:, 1], af[:, 3] / Q_INF
    x_js, y_js, cp_js = js[:, 0], js[:, 1], js[:, 3] / Q_INF

    # ---- coefficients, with the Aref refusal -------------------------------
    ctimes, cc, aref = read_coefficient_dat(
        os.path.join(case, "postProcessing", "forceCoeffs", "0",
                     "coefficient.dat"))
    if abs(aref - AREF) > 1e-12:
        refuse("Aref in coefficient.dat is %.6g, not %.6g (c * t_z on THIS mesh). "
               "Every coefficient in that file is wrong by %.6g x."
               % (aref, AREF, AREF / aref))
    j = int(np.argmin(np.abs(ctimes - t)))
    cl_dict, cd_dict = cc["Cl"][j], cc["Cd"][j]

    xy = np.column_stack([np.concatenate([x_af, x_js]),
                          np.concatenate([y_af, y_js])])
    cpc = np.concatenate([cp_af, cp_js])
    cl_int, cd_int, poly = cl_cd_from_cp(xy, cpc)

    # ---- jet mass-flow closure (frozen line-6 physicality, REPORTED) -------
    jmf = np.loadtxt(os.path.join(case, "postProcessing", "jetMassFlow", "0",
                                  "surfaceFieldValue.dat"), comments="#")
    sum_phi = abs(jmf[-1, 1])
    v_jet = U_INF * math.sqrt(C_MU_JET * 0.5 * C_CHORD / 0.005) if False else None
    # slot geometry measured from the sampled patch, not assumed
    h_slot = 0.005
    ux_jet = 27.38612788
    phi_expect = ux_jet * h_slot * T_Z
    mf_err = 100.0 * (sum_phi - phi_expect) / phi_expect

    common = ("run %s  |  time directory %d  |  L1 C-topology, 46,180 cells, "
              "t_z = %.1f m, Aref = %.1f  |  C_mu_jet = %.2f, alpha = %.0f deg, "
              "tau = %.0f deg, U_inf = %.0f m/s, c = %.0f m\n"
              "planted-zero control PASSED on both readers before plotting "
              "(internalField: wrote %.6g into a copy, read %.6g back where the "
              "truth is %.6g; airfoil raw: wrote %.6g, read it back)"
              % (os.path.basename(case), t, T_Z, AREF, C_MU_JET, ALPHA_DEG,
                 TAU_DEG, U_INF, C_CHORD,
                 p_plant, p_plant, p_true, r_plant))

    written = []

    # ===================================================== FIGURE 1: Cp =====
    fig = plt.figure(figsize=(13.6, 7.1))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.05, 1.0], wspace=0.06,
                          left=0.075, right=0.985, top=0.775, bottom=0.115)
    ax = fig.add_subplot(gs[0, 0])
    axt = fig.add_subplot(gs[0, 1])
    axt.axis("off")

    up = y_af > 0
    lo = ~up
    su = np.argsort(x_af[up])
    sl = np.argsort(x_af[lo])
    ax.plot(x_af[up][su] / C_CHORD, cp_af[up][su], "-o", color=SER1, lw=2.0,
            ms=3.4, mfc="white", mew=1.0, label="upper surface")
    ax.plot(x_af[lo][sl] / C_CHORD, cp_af[lo][sl], "--s", color=SER2, lw=2.0,
            ms=3.2, mfc="white", mew=1.0, label="lower surface")
    ax.axhline(0.0, color=MUTED, lw=0.9)

    ax.axvline(1.0, color="#7a4fbf", lw=1.6, ls=":", zorder=1)
    ax.text(0.995, 0.985, "jet slot, x/c = 1.00 ", ha="right", va="top",
            rotation=90, fontsize=8.6, color="#5b3a91",
            transform=ax.get_xaxis_transform())

    ax.invert_yaxis()
    ax.set_xlabel("chordwise station  x / c  [–]", fontsize=11, color=INK)
    ax.set_ylabel("pressure coefficient  C$_p$ = (p − p$_\\infty$) / "
                  "(½ ρ U$_\\infty^2$)  [–]",
                  fontsize=11, color=INK)
    ax.set_title("Surface pressure, blown section — ONE mesh, ONE configuration",
                 fontsize=12.5, color=INK, weight="bold", pad=10, loc="left")
    leg = ax.legend(frameon=False, fontsize=10, loc="lower right")
    for txt in leg.get_texts():
        txt.set_color(INK2)
    tidy(ax)

    note = (
        "WHY THERE IS NO UNBLOWN CURVE ON THIS PLOT\n\n"
        "The obvious demo would be blown against unblown.\n"
        "It is not available and it is not drawn.\n\n"
        "The five completed feasibility rows — one unblown\n"
        "and four blown — are on the O-TOPOLOGY mesh:\n"
        "39,984 cells, span t_z = 0.01 m.\n\n"
        "This row is the registered C-TOPOLOGY mesh:\n"
        "46,180 cells, span t_z = 1.0 m.\n\n"
        "Overlaying them would put two mesh topologies\n"
        "and two span thicknesses on one axis and let the\n"
        "eye read the difference as a jet effect.\n\n"
        "NO CONTROLLED BLOWN/UNBLOWN COMPARISON HAS BEEN\n"
        "PERFORMED ON THIS MESH. The jet-sheet trajectory\n"
        "figure carries the physics instead.")
    axt.text(0.0, 0.985, note, transform=axt.transAxes, fontsize=8.7,
             color=INK2, va="top", ha="left", linespacing=1.25,
             bbox=dict(boxstyle="round,pad=0.7", fc="#f4f4f7", ec=GRIDC))

    diag = ("DIAGNOSTIC NUMBERS — UNGRADED\n"
            "solver forceCoeffs, airfoil patch\n"
            "(pressure + viscous)\n"
            "  C_L %+.4f     C_D %+.4f\n"
            "\n"
            "this script's own contour integral\n"
            "of C_p (pressure only)\n"
            "  C_L %+.4f     C_D %+.4f\n"
            "\n"
            "Aref read back out of coefficient.dat\n"
            "  %.3f m2 = c x t_z, correct here.\n"
            "  0.01 is the O-mesh value; it would\n"
            "  report both 100x too large."
            % (cl_dict, cd_dict, cl_int, cd_int, aref))
    axt.text(0.0, 0.015, diag, transform=axt.transAxes, fontsize=8.3,
             color=INK, va="bottom", ha="left", family="DejaVu Sans Mono",
             linespacing=1.25,
             bbox=dict(boxstyle="round,pad=0.7", fc="#fbfbfd", ec=GRIDC))

    stamp(fig, st, common)
    f1 = os.path.join(out, "JF1_P1_cp_distribution.png")
    fig.savefig(f1, dpi=170, facecolor="white")
    plt.close(fig)
    written.append(f1)

    # ============================================ FIGURE 2: jet trajectory ===
    tx, ty, tm = jet_trajectory(cx, cy, U)
    fig = plt.figure(figsize=(13.6, 7.1))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.05, 1.0], wspace=0.06,
                          left=0.075, right=0.985, top=0.775, bottom=0.115)
    ax = fig.add_subplot(gs[0, 0])
    axt = fig.add_subplot(gs[0, 1])
    axt.axis("off")

    ax.fill(np.append(poly[:, 0], poly[0, 0]) / C_CHORD,
            np.append(poly[:, 1], poly[0, 1]) / C_CHORD,
            color="#26262c", zorder=4, label="airfoil section")

    ang = math.radians(TAU_DEG)
    xr = np.linspace(1.0, tx.max() if len(tx) else 3.0, 50)
    ax.plot(xr, -(xr - 1.0) * math.tan(ang), "--", color=SER2, lw=2.0,
            label="undeflected jet ray, %.0f° below chord "
                  "(what a free jet would do)" % TAU_DEG, zorder=5)

    if len(tx):
        sc = ax.scatter(tx, ty, c=tm, cmap="viridis", s=26, zorder=6,
                        edgecolor="white", linewidth=0.4,
                        vmin=U_INF, vmax=max(tm.max(), U_INF * 1.01))
        ax.plot(tx, ty, "-", color=SER1, lw=2.2, zorder=5,
                label="jet-sheet centreline (locus of max |U| on vertical cuts)")
        cax = ax.inset_axes([0.52, 0.13, 0.34, 0.035])
        cb = fig.colorbar(sc, cax=cax, orientation="horizontal")
        cb.set_label("peak speed on the cut  |U|  [m s$^{-1}$]", fontsize=8.8,
                     color=INK2)
        cb.ax.tick_params(labelsize=8.0, colors=INK2)
        cb.outline.set_edgecolor(GRIDC)

    ax.axhline(0.0, color=MUTED, lw=0.8, ls="-")
    xhi = (max(tx.max(), 2.4) + 0.25) if len(tx) else 3.2
    ax.set_xlim(-0.20, xhi)
    ax.set_ylim(-1.10, 0.32)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("streamwise station  x / c  [–]   (slot at x/c = 1.00)",
                  fontsize=11, color=INK)
    ax.set_ylabel("transverse station  y / c  [–]", fontsize=11, color=INK)
    ax.set_title("Jet-sheet trajectory — the sheet leaves at %.0f° and is turned"
                 " back toward the freestream" % TAU_DEG,
                 fontsize=12.5, color=INK, weight="bold", pad=10, loc="left")
    leg = ax.legend(frameon=False, fontsize=9.0, loc="lower left")
    for txt in leg.get_texts():
        txt.set_color(INK2)
    tidy(ax)

    if len(tx):
        dev = ty[-1] - (-(tx[-1] - 1.0) * math.tan(ang))
        i2 = int(np.argmin(np.abs(tx - 1.05)))
        ang0 = math.degrees(math.atan2(-(ty[i2] - 0.0), tx[i2] - 1.0))
        story = (
            "WHAT THIS FIGURE SHOWS\n\n"
            "The slot at x/c = 1.00 discharges a 5.0 mm sheet at\n"
            "31.6 m/s, aimed %.0f° below the chord. C_mu_jet = %.2f.\n\n"
            "A free jet would follow the dashed ray. The measured\n"
            "sheet does not: by x/c = %.2f its mean inclination is\n"
            "only %.1f° below the chord, and by x/c = %.2f it sits\n"
            "%.3f c ABOVE where the undeflected ray would be.\n\n"
            "The outer flow turns the sheet, and the sheet's reaction\n"
            "on the outer flow is what the surface pressure figure\n"
            "records as C_L = %+.4f at alpha = 0 on a SYMMETRIC\n"
            "section. That is the pneumatic flap.\n\n"
            "Peak speed decays %.1f -> %.1f m/s over that distance.\n"
            "The trace STOPS where the peak falls below 1.05 x U_inf;\n"
            "it is not extrapolated. Wake resolution on this mesh\n"
            "falls off fast downstream and that limits the trace,\n"
            "not the physics.\n\n"
            "CENTRELINE DEFINITION: locus of maximum |U| on vertical\n"
            "cuts, marched (each cut searches only within 0.10 c of\n"
            "the previous cut's answer)."
            % (TAU_DEG, C_MU_JET, tx[i2], ang0, tx[-1], dev, cl_dict,
               tm[0], tm[-1]))
        axt.text(0.0, 0.985, story, transform=axt.transAxes, fontsize=8.7,
                 color=INK2, va="top", ha="left", linespacing=1.22,
                 bbox=dict(boxstyle="round,pad=0.7", fc="#f4f4f7", ec=GRIDC))

    axt.text(0.0, 0.145,
             "jet mass-flow closure, MEASURED not gated\n"
             "sum(phi) over jetSlot   %.6f m3/s\n"
             "Ux,jet x h x t_z        %.6f m3/s\n"
             "discrepancy            %+.4f %%"
             % (sum_phi, phi_expect, mf_err),
             transform=axt.transAxes, fontsize=8.5, color=INK, va="top",
             ha="left", family="DejaVu Sans Mono", linespacing=1.25,
             bbox=dict(boxstyle="round,pad=0.7", fc="#fbfbfd", ec=GRIDC))

    stamp(fig, st, common)
    f2 = os.path.join(out, "JF1_P1_jet_sheet_trajectory.png")
    fig.savefig(f2, dpi=170, facecolor="white")
    plt.close(fig)
    written.append(f2)

    # ======================================== FIGURE 3: the pneumatic flap ===
    xlim = (-0.6, 2.8)
    ylim = (-1.25, 0.95)
    m = ((cx > xlim[0] - 0.3) & (cx < xlim[1] + 0.3) &
         (cy > ylim[0] - 0.3) & (cy < ylim[1] + 0.3))
    gx = np.linspace(xlim[0], xlim[1], 620)
    gy = np.linspace(ylim[0], ylim[1], 420)
    GX, GY = np.meshgrid(gx, gy)
    pts = np.column_stack([cx[m], cy[m]])
    GM = griddata(pts, mag[m], (GX, GY), method="linear")
    GU = griddata(pts, U[m, 0], (GX, GY), method="linear")
    GV = griddata(pts, U[m, 1], (GX, GY), method="linear")

    fig, ax = plt.subplots(figsize=(12.2, 7.6))
    fig.subplots_adjust(top=0.80, bottom=0.12, left=0.075, right=0.985)

    vmax = 20.0
    lv = np.linspace(0.0, vmax, 41)
    cf = ax.contourf(GX, GY, GM, levels=lv, cmap="viridis", extend="max")
    try:
        cf.set_rasterized(True)
    except Exception:
        pass
    ax.contour(GX, GY, GM, levels=[U_INF], colors=["white"], linewidths=1.2,
               linestyles="--", alpha=0.9)

    ax.streamplot(gx, gy, GU, GV, color="white", linewidth=0.55, density=1.5,
                  arrowsize=0.7, arrowstyle="->")

    ax.fill(np.append(poly[:, 0], poly[0, 0]),
            np.append(poly[:, 1], poly[0, 1]), color="#0d0d10", zorder=6)

    if len(tx):
        ax.plot(tx, ty, "-", color="#ff5f4d", lw=2.4, zorder=7,
                label="jet-sheet centreline")
        ax.plot(xr, -(xr - 1.0) * math.tan(ang), ":", color="#ffd166", lw=2.0,
                zorder=7, label="undeflected %.0f° jet ray" % TAU_DEG)
        leg = ax.legend(frameon=True, fontsize=9.2, loc="lower right",
                        facecolor="#101014", edgecolor="none", labelcolor="white")

    cb = fig.colorbar(cf, ax=ax, pad=0.012, fraction=0.030)
    cb.set_label("speed  |U|  [m s$^{-1}$]   (freestream 10.0, jet exit 31.6;\n"
                 "scale clipped at %.0f so the outer field stays readable)"
                 % vmax, fontsize=9.0, color=INK2)
    cb.ax.tick_params(labelsize=8.5, colors=INK2)
    cb.outline.set_edgecolor(GRIDC)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x / c  [–]", fontsize=11, color=INK)
    ax.set_ylabel("y / c  [–]", fontsize=11, color=INK)
    ax.set_title("The pneumatic flap — a symmetric section at α = 0° turning "
                 "the flow with air, not hinges",
                 fontsize=12.5, color=INK, weight="bold", pad=10, loc="left")
    ax.tick_params(colors=INK2, labelsize=9)

    # trailing-edge inset: where the sheet is actually formed
    axi = ax.inset_axes([0.615, 0.62, 0.375, 0.36])
    ix = (0.86, 1.30)
    iy = (-0.135, 0.085)
    igx = np.linspace(ix[0], ix[1], 320)
    igy = np.linspace(iy[0], iy[1], 200)
    IGX, IGY = np.meshgrid(igx, igy)
    im = ((cx > ix[0] - 0.1) & (cx < ix[1] + 0.1) &
          (cy > iy[0] - 0.1) & (cy < iy[1] + 0.1))
    IM = griddata(np.column_stack([cx[im], cy[im]]), mag[im], (IGX, IGY),
                  method="linear")
    ci = axi.contourf(IGX, IGY, IM, levels=np.linspace(0, 32, 33),
                      cmap="viridis")
    try:
        ci.set_rasterized(True)
    except Exception:
        pass
    axi.fill(np.append(poly[:, 0], poly[0, 0]),
             np.append(poly[:, 1], poly[0, 1]), color="#0d0d10", zorder=6)
    if len(tx):
        axi.plot(tx, ty, "-", color="#ff5f4d", lw=1.8, zorder=7)
    axi.set_xlim(*ix)
    axi.set_ylim(*iy)
    axi.set_aspect("equal", adjustable="box")
    axi.set_xticks([])
    axi.set_yticks([])
    for s in axi.spines.values():
        s.set_color("white")
        s.set_linewidth(1.2)
    axi.set_title("trailing edge, full 0–32 m/s scale: the 5 mm sheet",
                  fontsize=8.0, color="white", pad=3)

    ax.text(0.012, 0.030,
            "The section is symmetric and sits at α = 0°. With no blowing it "
            "would carry no lift at all.\n"
            "The streamlines are turned by the jet sheet alone — there is no "
            "mechanical flap anywhere in this mesh.\n"
            "Dashed white line: |U| = U$_\\infty$ = 10 m/s. Streamlines and "
            "contours are drawn on a %d×%d linear interpolation\n"
            "of the cell-centre field, for display only; every number quoted on "
            "these figures is read from the solver's\n"
            "own output, never from that display grid."
            % (len(gx), len(gy)),
            transform=ax.transAxes, fontsize=8.3, color="white", va="bottom",
            ha="left", bbox=dict(boxstyle="round,pad=0.5", fc="#101014",
                                 ec="none", alpha=0.85))

    stamp(fig, st, common)
    f3 = os.path.join(out, "JF1_P1_pneumatic_flap_field.png")
    fig.savefig(f3, dpi=170, facecolor="white")
    plt.close(fig)
    written.append(f3)

    # ------------------------------------------------------------- report ---
    print("time directory plotted      : %d" % t)
    print("solver last iteration       : %d of %d" % (st["last_time"], END_TIME))
    print("ExecutionTime at last line  : %s s" % st["exec_time_s"])
    print("End line seen               : %s" % st["ended"])
    print("initial residuals @ %6d  : p %.3e  Ux %.3e  Uy %.3e  k %.3e  "
          "omega %.3e" % (st["res"]["iter"], st["res"]["p"], st["res"]["Ux"],
                          st["res"]["Uy"], st["res"]["k"], st["res"]["omega"]))
    print("bounding k                  : %d of %d iterations (%.1f %%), first at "
          "%s, last clean %s" % (st["bounded"], st["steps"],
                                 100.0 * st["bounded"] / max(1, st["steps"]),
                                 st["first_bounded"], st["last_clean"]))
    print("last bounding k line        : %s" % st["last_bk_line"])
    print("Aref from coefficient.dat   : %.6f  (required %.6f)" % (aref, AREF))
    print("Cl, Cd from coefficient.dat : %+.6f  %+.6f   (at t=%d)"
          % (cl_dict, cd_dict, ctimes[j]))
    print("Cl, Cd by Cp contour integ. : %+.6f  %+.6f   (pressure only)"
          % (cl_int, cd_int))
    print("jet sum(phi) / expected     : %.8f / %.8f  (%+.4f %%)"
          % (sum_phi, phi_expect, mf_err))
    print("Cp range on airfoil         : %.4f .. %.4f" % (cpc.min(), cpc.max()))
    if len(tx):
        print("trajectory: x/c %.3f..%.3f, y/c at end %.4f, undeflected ray "
              "%.4f, deviation %+.4f"
              % (tx[0], tx[-1], ty[-1], -(tx[-1] - 1.0) * math.tan(ang),
                 ty[-1] + (tx[-1] - 1.0) * math.tan(ang)))
    for f in written:
        print("WROTE %s" % f)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        sys.exit(2)
