#!/usr/bin/env python3
"""
T9aH builder -- the T9a cases under Gauss harmonic, plus three extra cases.

*** NEW FILE.  Read it before believing anything built by it. ***

IT DOES NOT RE-DERIVE THE T9a CASES.  It imports the FROZEN build_t9a.py
(sha 516fee58...1958e4e9a2659e9, byte-identical to the blob at HEAD, copied
into this tree before any case existed) and reuses its generators UNMODIFIED:
wall_block_mesh, wall_field_T, wall_field_DT, fin_block_mesh, fin_field_T,
fin_field_DT, transport, control_dict, fv_solution, case_txt.  Re-deriving them
would have made "the single change is the interface scheme" a claim about a
script instead of a measurement.

THE SINGLE CHANGE, and it is PROVEN AT BUILD TIME rather than asserted: this
file takes the frozen fv_schemes() text and (1) sets the laplacianSchemes
default to the case's registered scheme and (2) appends an explicit
laplacian(DT,T) entry so the comparator can read the scheme back off disk
(the frozen comparator never reads fvSchemes -- section 6.2 of the
pre-registration).  It then DIFFS its own output against the frozen text and
ABORTS unless exactly those two things changed.  D_R_f in T9a-D carried the
same single added entry and reproduced the frozen W_f to 0.000e+00 K.

THE TWO CONTRAST CASES override the registered layer-2 conductivity IN MEMORY
for the duration of one build and restore it, with the restoration asserted.
The frozen T9a_registered.json on disk is never edited.

GUARD (section 6.4, and the strict completion rule's own precondition): this
builder REFUSES to write into a case directory that already holds 0/ or a time
directory.  A case that already has an answer is not rebuilt silently.

It builds ten cases and RUNS NOTHING: no blockMesh, no checkMesh, no solver.
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t9a as B          # noqa: E402  frozen generators, unmodified

HARMONIC = "Gauss harmonic corrected"
LINEAR = "Gauss linear corrected"

# name -> (kind, cells_per_layer | (nx, ny), scheme, k2 or None)
EXTRA = {
    "RL_f":    ("wall", [26, 51, 13], LINEAR, None),
    "H40_f":   ("wall", [26, 51, 13], HARMONIC, 0.4),
    "H4000_f": ("wall", [26, 51, 13], HARMONIC, 0.004),
}


def fv_schemes(scheme):
    """The frozen fvSchemes with the registered scheme, and the readback entry.

    Proven, not asserted: the output is diffed against the frozen text and any
    change beyond the laplacianSchemes default line plus one appended
    laplacian(DT,T) line aborts the build."""
    frozen = B.fv_schemes()
    out = re.sub(r"laplacianSchemes \{ default [^;]+; \}",
                 f"laplacianSchemes {{ default {scheme}; }}", frozen)
    out = out.rstrip("\n") + f"\nlaplacian(DT,T)  {scheme};\n"

    a, b = frozen.splitlines(), out.splitlines()
    added = [l for l in b if l not in a]
    removed = [l for l in a if l not in b]
    if len(added) != (1 if scheme == LINEAR else 2) or len(removed) > 1:
        raise SystemExit(f"ABORT: fvSchemes for {scheme} differs from the "
                         f"frozen text by more than the registered single "
                         f"change.\n  added: {added}\n  removed: {removed}")
    if not any(l.startswith("laplacian(DT,T)") for l in added):
        raise SystemExit("ABORT: the laplacian(DT,T) readback entry is missing")
    return out


def guard(d, name):
    """Refuse a case that already holds an answer (section 6.4)."""
    if not os.path.isdir(d):
        return
    if os.path.isdir(os.path.join(d, "0")):
        raise SystemExit(f"ABORT: {name} already holds 0/ -- a case with an "
                         f"answer is not rebuilt silently")
    for e in os.listdir(d):
        if re.fullmatch(r"\d+(\.\d+)?", e) and float(e) != 0.0:
            raise SystemExit(f"ABORT: {name} already holds the time directory "
                             f"{e} -- a case with an answer is not rebuilt")


def write_case(name, kind, geom, scheme, k2):
    d = os.path.join(HERE, name)
    guard(d, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    for sub in ("0.orig", "constant", "system"):
        os.makedirs(os.path.join(d, sub))

    def w(rel, txt):
        open(os.path.join(d, rel), "w").write(txt)

    saved = B.WALL["layers"][1]["k"]
    try:
        if k2 is not None:
            B.WALL["layers"][1]["k"] = k2
        w("system/controlDict", B.control_dict())
        w("system/fvSchemes", fv_schemes(scheme))
        w("system/fvSolution", B.fv_solution())
        if kind in ("wall", "wall_uniform_control"):
            cells = geom
            w("system/blockMeshDict", B.wall_block_mesh(cells))
            T_cold = (B.WALL["T_cold"] if kind == "wall" else B.WALL["T_hot"])
            w("0.orig/T", B.wall_field_T(B.WALL["T_hot"], T_cold))
            w("0.orig/DT", B.wall_field_DT(cells))
            w("constant/transportProperties", B.transport(B.WALL["layers"][0]["k"]))
            ncell = sum(cells)
            desc = dict(kind=kind, cells_per_layer=cells)
        else:
            nx, ny = geom
            w("system/blockMeshDict", B.fin_block_mesh(nx, ny))
            w("0.orig/T", B.fin_field_T(ny))
            w("0.orig/DT", B.fin_field_DT())
            w("constant/transportProperties", B.transport(B.FIN["k"]))
            ncell = nx * ny
            desc = dict(kind=kind, nx=nx, ny=ny)
        w("CASE.txt", B.case_txt(name, desc)
          + f"rung_override     T9aH: laplacian(DT,T) = {scheme}\n"
          + (f"k2_override       layer 2 k = {k2} W/mK "
             f"(contrast {16.0/k2:g}x)\n" if k2 is not None else ""))
    finally:
        B.WALL["layers"][1]["k"] = saved
    assert B.WALL["layers"][1]["k"] == 0.04, \
        "the frozen registered layer-k map was NOT restored"
    return ncell


def main():
    made = []
    for name, c in B.CASES.items():          # the seven frozen case names
        geom = (c["cells_per_layer"] if c["kind"].startswith("wall")
                else (c["nx"], c["ny"]))
        made.append((name, write_case(name, c["kind"], geom, HARMONIC, None),
                     c["kind"], HARMONIC, 0.04))
    for name, (kind, geom, scheme, k2) in EXTRA.items():
        made.append((name, write_case(name, kind, geom, scheme, k2),
                     kind, scheme, k2 if k2 is not None else 0.04))

    print(f"T9aH: {len(made)} cases built in {HERE}")
    print(f"  {'case':9s} {'cells':>6s}  {'k2':>6s}  scheme")
    for n, cells, kind, scheme, k2 in made:
        print(f"  {n:9s} {cells:6d}  {k2:6g}  {scheme}")
    print("\n  NOTHING WAS RUN: no blockMesh, no checkMesh, no solver.")
    print("  The seven frozen names are graded by the byte-identical frozen "
          "comparator; RL_f, H40_f and H4000_f are invisible to it and are "
          "graded only by analyse_t9aH.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
