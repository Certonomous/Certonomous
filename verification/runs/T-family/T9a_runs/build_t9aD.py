#!/usr/bin/env python3
"""
T9a-D builder: the diagnosis arm for T9a's 2.41 mK interface miss.

Written AFTER analyse_t9aD.py was written and hashed and AFTER the freeze
condition (no D_* directory in the run tree) was checked with a timestamped
command, to the specification in docs/campaigns/T-family/T9aD_PREREGISTRATION.md
and the case list in T9aD_registered.json.

THE FROZEN BUILDER IS IMPORTED, NEVER EDITED.  build_t9a.py supplies the
blockMeshDict, the T field, the DT field, transportProperties, controlDict and
fvSolution verbatim; this file adds exactly two things:

  1. an fvSchemes writer that takes the laplacian(DT,T) entry as a PARAMETER,
     because the frozen one hard-codes 'default Gauss linear corrected' -- the
     scheme is the whole of H-A;
  2. a temporary in-memory override of the layer-2 conductivity for the H-C
     cases, so that build_t9a.wall_field_DT writes 0.4 instead of 0.04.  The
     frozen file is never written to and the override is restored immediately.

EVERY D_* CASE WRITES AN EXPLICIT laplacian(DT,T) ENTRY, including the ones
whose scheme is unchanged.  'default Gauss linear corrected' and
'laplacian(DT,T) Gauss linear corrected' select the SAME scheme -- the explicit
line changes no number -- but it lets the comparator READ THE ARM'S SINGLE
CHANGE BACK OFF DISK instead of trusting this builder.  That the explicit line
is numerically inert is not asserted: D_R_f is the frozen W_f rebuilt with it,
and the comparator REFUSES if it does not reproduce W_f to 1e-9 K.

ONE CHANGE PER RUN:
  D_A_*  scheme only          (Gauss harmonic corrected; mesh and k frozen)
  D_B_x  mesh level only      (42/82/21 = f x 1.6, T1c integer rounding)
  D_C_*  layer-2 k only       (0.04 -> 0.4 W/mK, contrast 400x -> 40x)
  D_R_f  nothing              (replica control)

writeInterval STRICTLY LESS THAN endTime (L-140) and NO residualControl
(L-141) are inherited from the frozen controlDict/fvSolution writers.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t9a as B               # noqa: E402  frozen, imported, never edited

DREG = json.load(open(os.path.join(HERE, "T9aD_registered.json")))
CASES = DREG["cases"]


def fv_schemes(laplacian_entry):
    """The frozen fvSchemes with laplacian(DT,T) made explicit.  Every other
    line is byte-identical to build_t9a.fv_schemes()."""
    return B.header("dictionary", "fvSchemes", "system") + f"""
ddtSchemes      {{ default steadyState; }}
gradSchemes     {{ default Gauss linear; }}
divSchemes      {{ default none; }}
laplacianSchemes
{{
    default             Gauss linear corrected;
    laplacian(DT,T)     {laplacian_entry};
}}
interpolationSchemes {{ default linear; }}
snGradSchemes   {{ default corrected; }}
"""


def case_txt(name, c):
    k2 = c["k2"]
    layers = (DREG["wall_H_C"] if k2 != 0.04 else DREG["wall_frozen"])["layers"]
    lines = [f"case              {name}",
             "arm               T9a-D (diagnosis of T9a's 2.41 mK R1 miss)",
             f"hypothesis        {c['hypothesis']}",
             "grades            NOTHING against the T9a band; T9a is not re-solved",
             "solver            laplacianFoam (ESI v2606), steadyState ddt",
             f"laplacian(DT,T)   {c['scheme']}",
             f"contrast          {(layers[2]['k']/layers[1]['k']):.0f}x "
             f"(layer 2 k = {k2} W/mK)",
             f"endTime           {B.END_TIME}",
             f"writeInterval     {B.WRITE_INTERVAL}  (strictly less than endTime, L-140)",
             "residualControl   none (L-141; convergence from written checkpoints)"]
    for j, (ly, n) in enumerate(zip(layers, c["cells_per_layer"])):
        lines.append(f"layer_{j+1}           L = {ly['L']} m, k = {ly['k']} W/mK,"
                     f" {n} cells, dx = {ly['L']/n:.6e} m")
    ex = DREG["wall_H_C"] if k2 != 0.04 else None
    lines += [f"T_hot             {B.WALL['T_hot']} K",
              f"T_cold            {B.WALL['T_cold']} K"]
    if ex:
        lines += [f"reference_q       {ex['q']}  (re-derived at 40x)",
                  f"reference_T_i1    {ex['T_i1']}",
                  f"reference_T_i2    {ex['T_i2']}"]
    else:
        lines += [f"reference_q       {B.WALL['q']} W/m2",
                  f"reference_T_i1    {B.WALL['T_i1']} K",
                  f"reference_T_i2    {B.WALL['T_i2']} K"]
    if c["hypothesis"] == "CONTROL-R":
        lines.append("control           REPLICA -- the frozen W_f rebuilt with "
                     "NOTHING changed; the comparator REFUSES the whole arm if "
                     "it does not reproduce W_f to 1e-9 K")
    return "\n".join(lines) + "\n"


def main():
    made = []
    for name, c in CASES.items():
        d = os.path.join(HERE, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        for sub in ("0.orig", "constant", "system"):
            os.makedirs(os.path.join(d, sub))

        def w(rel, txt):
            open(os.path.join(d, rel), "w").write(txt)

        cells = c["cells_per_layer"]
        k2 = c["k2"]
        saved = B.WALL["layers"][1]["k"]
        try:
            B.WALL["layers"][1]["k"] = k2      # in memory only
            w("system/blockMeshDict", B.wall_block_mesh(cells))
            w("0.orig/T", B.wall_field_T(B.WALL["T_hot"], B.WALL["T_cold"]))
            w("0.orig/DT", B.wall_field_DT(cells))
            w("constant/transportProperties", B.transport(B.WALL["layers"][0]["k"]))
        finally:
            B.WALL["layers"][1]["k"] = saved
        assert B.WALL["layers"][1]["k"] == 0.04, "frozen k not restored"

        w("system/controlDict", B.control_dict())
        w("system/fvSolution", B.fv_solution())
        w("system/fvSchemes", fv_schemes(c["scheme"]))
        w("CASE.txt", case_txt(name, c))
        made.append((name, sum(cells), c["hypothesis"], c["scheme"], k2))

    print(f"T9a-D: {len(made)} cases built in {HERE}")
    print(f"  endTime {B.END_TIME}, writeInterval {B.WRITE_INTERVAL} "
          f"(STRICTLY less)")
    print(f"\n  {'case':8s} {'cells':>6s}  {'hypothesis':11s} "
          f"{'laplacian(DT,T)':26s} k2")
    for n, cl, h, s, k2 in made:
        print(f"  {n:8s} {cl:6d}  {h:11s} {s:26s} {k2}")
    print(f"\n  frozen build_t9a.py layer-2 k after all overrides: "
          f"{B.WALL['layers'][1]['k']} (must be 0.04)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
