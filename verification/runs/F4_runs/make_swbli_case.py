#!/usr/bin/env python3
"""
Axisymmetric cylinder-flare SWBLI case generator (Kussoy & Horstman, NASA TM
101075). rhoCentralFoam (reused from F4's inviscid hypersonic cylinder work
and from OpenFOAM's own biconic25-55Run35 tutorial, the nearest validated
axisymmetric hypersonic template on this host), + kOmegaSST turbulence (new
here -- no prior F-family case has run a turbulent compressible solve).

Geometry, real SI units (not F3/F4's nondimensional a=1 convention -- the
isothermal wall BC and Sutherland viscosity make dimensional consistency
matter here, and Table I in the primary source is already in SI):
  - Cylinder radius R_CYL = 0.1015 m (0.203 m model diameter, TM 101075).
  - Domain starts on the bare cylinder, not at the real 139-cm-forward flare
    station or the 2 m nose -- Table I already gives the fully-developed
    local state at the reference station, so the inlet is placed a few
    boundary-layer-thicknesses upstream of the corner and fed that state
    directly. This is a disclosed simplification, not a hidden one.
  - FLARE_DEG is a parameter: 20 deg for the free warm-up (attached, s=0
    per TM 101075 p.5), 32.5/35 deg held for the gate rungs.

Two hex blocks in the (x, r) plane, revolved into a thin wedge about the
axis using OpenFOAM's standard `wedge` patch pair -- the exact same pattern
already used and checkMesh-verified in F3_runs/make_cone_case.py (Block A
upstream / Block B downstream-of-the-angle-change), extended here with
wall-normal (r-direction) grading, which F3's inviscid cone case never
needed.
"""
import math
import os

ALPHA_DEG = 2.5  # axisymmetric wedge half-angle, same convention as F3/F4

R_CYL = 0.1015          # m, cylinder radius (TM 101075, model diameter 0.203 m)
L_UPSTREAM = 0.08       # m, cylinder length modelled upstream of the corner
                        # (~3x the reference delta0=2.5cm; NOT the real 139 cm --
                        # disclosed simplification, inlet fed Table I's local state)
L_FLARE_AXIAL_TARGET = 0.12  # m, target axial extent of the flare section

# Table I (Kussoy & Horstman 1989), reference/undisturbed station, SI:
P_INF = 576.0        # Pa
T_INF = 81.2          # K
RHO_INF = 0.0252      # kg/m^3
U_INF = 1274.0        # m/s
T_WALL = 311.0        # K, isothermal
TAU_W_INF = 25.0      # N/m^2, reference skin friction (undisturbed)
GAMMA = 1.4
R_SPECIFIC = 287.0    # J/(kg K), air

# y+=1 first-cell height at the reference station, derived from Table I
# (rho_wall from ideal gas at p_inf/T_wall, mu_wall from Sutherland at
# T_wall, u_tau from tau_w_inf) -- see F4 scoping note, same computation:
_AS, _TS = 1.458e-6, 110.0  # OpenFOAM Sutherland form: mu = As*sqrt(T)/(1+Ts/T)


def sutherland_mu(T):
    return _AS * math.sqrt(T) / (1.0 + _TS / T)


def first_cell_yplus1():
    rho_wall = P_INF / (R_SPECIFIC * T_WALL)
    mu_wall = sutherland_mu(T_WALL)
    u_tau = math.sqrt(TAU_W_INF / rho_wall)
    nu_wall = mu_wall / rho_wall
    return nu_wall / u_tau


FIRST_CELL = first_cell_yplus1()  # ~4.7e-5 m, computed not hardcoded

RES = {
    # (nx1 cylinder, nx2 flare, nr wall-normal)
    "coarse": (40, 50, 40),
    "medium": (80, 100, 80),
    "warmup": (120, 150, 110),
}


def foam_header(cls, obj, note=""):
    return f"""FoamFile
{{
    version 2.0;
    format  ascii;
    class   {cls};
    object  {obj};
}}
{('// ' + note) if note else ''}
"""


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def ratio_for_first_cell(length, n, first_cell, lo=1.0 + 1e-9, hi=1.0e6):
    """Total simpleGrading expansion ratio (last/first cell) giving the
    requested first-cell height across n cells summing to `length`.
    Same bisection approach as sdk/workflows/tmr_verification.py's
    ratio_for_first_cell, reproduced here to keep this case self-contained
    (F4_runs has never imported sdk/workflows; not changing that now)."""
    if first_cell >= length / n:
        return 1.0
    def geometric_first_cell(total_ratio):
        r = total_ratio ** (1.0 / (n - 1))
        if abs(r - 1.0) < 1e-12:
            return length / n
        return length * (r - 1.0) / (r ** n - 1.0)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if geometric_first_cell(mid) > first_cell:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def make_case(case_dir, flare_deg, res_level="warmup"):
    alpha = math.radians(ALPHA_DEG)
    tanA = math.tan(alpha)
    theta = math.radians(flare_deg)

    nx1, nx2, nr = RES[res_level]

    x0 = 0.0
    x1 = L_UPSTREAM
    L2 = L_FLARE_AXIAL_TARGET
    x2 = x1 + L2

    r_wall0 = R_CYL
    r_wall1 = R_CYL
    r_wall2 = R_CYL + L2 * math.tan(theta)

    R_outer = R_CYL + 0.10  # m, farfield -- a few boundary-layer-thicknesses
                            # of margin beyond the wall (delta0=2.5cm), generous
                            # for the interaction/shock system without a full
                            # bow-shock-scale domain (this is a wall-bounded
                            # SWBLI, not a blunt-body problem)

    total_ratio = ratio_for_first_cell(R_outer - r_wall0, nr, FIRST_CELL)

    def fv(x, r):
        return (x, r, r * tanA)
    def bv(x, r):
        return (x, r, -r * tanA)

    # Block A: cylinder section, x in [x0, x1], r in [r_wall0, R_outer]
    # Block B: flare section, x in [x1, x2], r in [r_wall1..r_wall2, R_outer]
    # Vertices (front copies, then back copies), wall then outer:
    vA_w0 = fv(x0, r_wall0); vA_w1 = fv(x1, r_wall1)
    vA_o0 = fv(x0, R_outer); vA_o1 = fv(x1, R_outer)
    vA_w0b = bv(x0, r_wall0); vA_w1b = bv(x1, r_wall1)
    vA_o0b = bv(x0, R_outer); vA_o1b = bv(x1, R_outer)

    vB_w2 = fv(x2, r_wall2)
    vB_o2 = fv(x2, R_outer)
    vB_w2b = bv(x2, r_wall2)
    vB_o2b = bv(x2, R_outer)

    verts = [vA_w0, vA_w1, vA_o1, vA_o0,        # 0-3  front, block A
             vA_w0b, vA_w1b, vA_o1b, vA_o0b,     # 4-7  back,  block A
             vB_w2, vB_o2,                        # 8-9  front, block B far end
             vB_w2b, vB_o2b]                       # 10-11 back, block B far end
    vtxt = "\n".join(f"    ({v[0]:.10f} {v[1]:.10f} {v[2]:.10f})" for v in verts)

    # Block A: wall(0,1) outer(2,3) front / back(4,5,6,7)
    #
    # GRADING-DIRECTION BUG, found and fixed 2026-07-30 (diagnosing the
    # f4_swbli_warmup20 crash). `hex (3 2 1 0 7 6 5 4)`'s local vertex 0 (the
    # small-cell end when the 2nd simpleGrading entry is >1, per
    # blockDescriptor.H's convention: local y goes v0->v3, ratio =
    # size(v3)/size(v0)) is mesh-vertex "3" = vA_o0 = the farfield/OUTER
    # corner, and local vertex 3 (the large-cell end) is mesh-vertex "0" =
    # vA_w0 = the WALL corner. Using `total_ratio` (>1, computed FOR the
    # wall-resolving 47-micron first cell) directly here therefore put the
    # FINE cells at the farfield boundary (which only needs `zeroGradient`,
    # doesn't care) and the COARSE cells (~4mm, ~86x the intended y+~1 size)
    # at the wall -- the opposite of the design intent stated above and in
    # this case's own comments. checkMesh cannot catch this: a monotonically
    # graded mesh is geometrically valid regardless of which end is fine.
    # It was only found by tracing WHERE a bounded diagnostic solve's energy
    # clamp was firing (persistently at the wall-adjacent cell) and then
    # checking that cell's actual size against the design target. Fix:
    # invert the ratio so the small end lands at v3 (the wall), matching
    # intent, without touching vertex order (lower risk of a face-orientation
    # mistake than reordering the hex).
    wall_ratio = 1.0 / total_ratio
    blockA = (f"hex (3 2 1 0 7 6 5 4) ({nx1} {nr} 1) "
              f"simpleGrading (1 {wall_ratio:.6g} 1)")
    # Block B: wall(1,8) outer(9,2) front / back(5,10,11,6) -- same bug,
    # same fix (`hex (2 9 8 1 ...)`: local v0="2"=vA_o1=outer, local
    # v3="1"=vA_w1=wall).
    blockB = (f"hex (2 9 8 1 6 11 10 5) ({nx2} {nr} 1) "
              f"simpleGrading (1 {wall_ratio:.6g} 1)")

    blockMeshDict = f"""{foam_header("dictionary", "blockMeshDict")}
convertToMeters 1;

vertices
(
{vtxt}
);

blocks
(
    {blockA}
    {blockB}
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces ((0 4 7 3));
    }}
    outlet
    {{
        type patch;
        faces ((8 10 11 9));
    }}
    axis
    {{
        type empty;
        faces ();
    }}
    wall
    {{
        type wall;
        faces ((0 1 5 4)(1 8 10 5));
    }}
    farfield
    {{
        type patch;
        faces ((3 7 6 2)(2 6 11 9));
    }}
    frontWedge
    {{
        type wedge;
        faces ((0 3 2 1)(1 2 9 8));
    }}
    backWedge
    {{
        type wedge;
        faces ((4 5 6 7)(5 10 11 6));
    }}
);

mergePatchPairs
(
);
"""
    write(f"{case_dir}/system/blockMeshDict", blockMeshDict)
    return {
        "flare_deg": flare_deg, "res_level": res_level,
        "nx1": nx1, "nx2": nx2, "nr": nr,
        "cells": (nx1 + nx2) * nr,
        "first_cell_m": FIRST_CELL, "total_ratio": total_ratio,
        "R_outer": R_outer, "x1": x1, "x2": x2,
    }


if __name__ == "__main__":
    import json, sys
    out = sys.argv[1] if len(sys.argv) > 1 else "swbli_cylflare/warmup20"
    params = make_case(out, flare_deg=20.0, res_level="warmup")
    print(json.dumps(params, indent=2))
    print(f"first_cell = {FIRST_CELL*1e6:.2f} micron")
