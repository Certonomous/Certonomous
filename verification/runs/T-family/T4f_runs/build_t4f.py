#!/usr/bin/env python3
"""DRAFT builder for T4f -- the TRANSIENT / URANS impinging-jet rung.

T4f runs the correct transient solver (buoyantBoussinesqPimpleFoam) on the ONE mesh that sustains the
unsteadiness T4d/T4e measured: the FROZEN T4e fine level (N = 192, nrj = 3N/2, first_cell 3e-6,
138 240 cells).  The mesh, fields, BCs, transportProperties, turbulenceProperties and g are IMPORTED
FROZEN and never re-implemented:

  * block_mesh_dict  <- verification/runs/T-family/T4e_runs/build_t4e.block_mesh_dict  (byte-identical
    fine mesh; build-time import, NOT on the grading path).  The blockMeshDict this emits MUST be
    byte-identical to T4e_IJ_f/system/blockMeshDict -- the section-3 check confirms that.
  * fields(), constant_files(), header()  <- verification/runs/T-family/T4_runs/build_t4  (FROZEN).

The ONE substantive change vs the steady lineage is the SOLVER, expressed entirely in a NEW transient
system_files():
    application  buoyantBoussinesqSimpleFoam -> buoyantBoussinesqPimpleFoam
    ddtSchemes   default steadyState        -> default backward
    fvSolution   SIMPLE block               -> PIMPLE block (+ *Final solver entries; relax 1)
    controlDict  FIXED deltaT, endTime 0.08 s, fieldAverage + sampledSets functionObjects, purgeWrite 0

No band, threshold, floor, reference or reader is touched (T25 discipline).  Every transform of the
FROZEN steady writer's output is applied behind a refuse-guard that counts the match, so a change to the
inherited frozen writer cannot pass silently (the build_t4e discipline).

NO `assert` STATEMENT IN THIS FILE (L-332).  Refusals are explicit exits.

STATUS: DRAFT.  NOT FROZEN, NOT BUILT, NOT LAUNCHED.  This file writes case inputs only when RUN with
--root; it launches nothing and spends zero solver core-minutes.  Held for a later box window.

Usage:  build_t4f.py [--root <dir>] [--deltaT <s>]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T4 = os.path.join(os.path.dirname(HERE), "T4_runs")
T4E = os.path.join(os.path.dirname(HERE), "T4e_runs")
sys.path.insert(0, T4)
sys.path.insert(0, T4E)
import build_t4 as B          # noqa: E402  FROZEN (fields, constant_files, header, system_files)
import build_t4e as BE        # noqa: E402  FROZEN (block_mesh_dict -> byte-identical fine mesh)

CASE = "T4f_IJ_f"
LEVEL = "f"
N = 192
FIRST_CELL = 3.0e-6
# --- PARALLEL DECOMPOSITION (verification ruling 19b7330a, application of PARALLEL_GATE_DOCTRINE) ---
# method `simple` is deterministic geometric, reproducible from this dict ALONE (no cellProcAddressing
# artifact to pin) -- the only method fully specifiable pre-compute (doctrine C1 + ruling condition 1).
# wedge is one cell thick in z, so the z split MUST be 1.  Coeffs are a DRAFT choice; they may be
# balance-tuned at the staged build to target per-rank max/min cell ratio <= ~1.5, changing ONLY this
# dict (ruling condition 4).  numerics are identical to a serial run (adjustTimeStep off; see below).
NRANKS = 8                       # 138240/8 = 17280 cells/rank avg; doctrine codifies no numeric floor
DECOMP_METHOD = "simple"
SIMPLE_COEFFS = (4, 2, 1)        # (n_r n_y n_z); n_z=1 (wedge); product == NRANKS
END_TIME_S = 0.08          # T_end
T_INIT_S = 0.03            # fieldAverage timeStart (discard)
DEFAULT_DELTAT_S = 8.0e-7  # DRAFT placeholder POINT dt; the calibration probe PINS the committed value
SAMPLE_EVERY_STEPS = 25    # instantaneous G-row line sampling interval (for stationarity_t4f.py)
FULLFIELD_WRITE_S = 0.01   # full-field (incl. UMean) write interval
# graded stations r/D -> the runtime instantaneous sampling lines (same stations analyse_t4 grades)
STATIONS = ((1.0, "G1"), (2.0, "G2"), (3.0, "G3"))


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def _sampled_sets_block():
    """A `sets` functionObject writing instantaneous |U| along a wall-normal line at each graded r/D,
    every SAMPLE_EVERY_STEPS steps.  Geometry mirrors the frozen analyse_t4.sample_profile line
    (axis y, start (r 1e-6 0), end (r D 0), uniform) so the instantaneous series and the graded
    time-mean read the SAME station."""
    D = B.D
    lines = []
    for r_over_d, tag in STATIONS:
        r = r_over_d * D
        lines.append(
            "        %s\n        {\n            type    uniform;\n            axis    y;\n"
            "            start   (%.10g 1e-6 0);\n            end     (%.10g %.10g 0);\n"
            "            nPoints 400;\n        }\n" % (tag, r, r, 0.5 * D * 2.0))
    return (
        "    gLines\n    {\n        type            sets;\n"
        "        libs            (\"libsampling.so\");\n"
        "        writeControl    timeStep;\n        writeInterval   %d;\n"
        "        setFormat       raw;\n        interpolationScheme cellPoint;\n"
        "        fields          (U);\n        sets\n        (\n%s        );\n    }\n"
        % (SAMPLE_EVERY_STEPS, "".join(lines)))


def _field_average_block():
    """Time-average U p_rgh T k omega from timeStart = T_init; writes UMean etc. with the case write."""
    return (
        "    fieldAverage1\n    {\n        type            fieldAverage;\n"
        "        libs            (\"libfieldFunctionObjects.so\");\n"
        "        writeControl    writeTime;\n        timeStart       %.10g;\n"
        "        restartOnRestart false;\n        restartOnOutput  false;\n"
        "        fields\n        (\n"
        "            U     { mean on; prime2Mean off; base time; }\n"
        "            p_rgh { mean on; prime2Mean off; base time; }\n"
        "            T     { mean on; prime2Mean off; base time; }\n"
        "            k     { mean on; prime2Mean off; base time; }\n"
        "            omega { mean on; prime2Mean off; base time; }\n"
        "        );\n    }\n" % T_INIT_S)


def transient_system_files(deltaT):
    """The FROZEN steady build_t4.system_files() output with the solver made transient.

    Refuse-guards count every substitution against the frozen writer's output, so a drift in the frozen
    writer cannot pass silently.  endTime must be an exact multiple of deltaT (keeps the rule-4 clause-5
    generalisation exact/integer; see mark_done_t4f.py and T4f_PREREGISTRATION.md section 6)."""
    files = B.system_files(int(END_TIME_S))   # seeded with the frozen schemes/solvers; controlDict rebuilt below

    # ---- fvSchemes: ddt steadyState -> backward (exactly one), everything else byte-identical ----
    sch, n = re.subn(r"ddtSchemes\s*\{\s*default\s+steadyState;\s*\}",
                     "ddtSchemes      { default backward; }", files["fvSchemes"])
    if n != 1:
        refuse("fvSchemes: expected exactly one steadyState ddtScheme to change to backward, found %d "
               "-- the frozen build_t4 writer may have moved" % n)
    files["fvSchemes"] = sch

    # ---- fvSolution: SIMPLE -> PIMPLE; *Final solvers INJECTED into the existing solvers block ----
    sol = files["fvSolution"]
    # the SIMPLE block nests one sub-block (residualControl { ... }); match one level of nesting so the
    # block's own closing brace is not left dangling.
    sol, ns = re.subn(r"^SIMPLE\s*\{(?:[^{}]|\{[^{}]*\})*\}\s*\n", "", sol, flags=re.M)
    if ns != 1:
        refuse("fvSolution: expected exactly one SIMPLE block to remove, found %d" % ns)
    if "SIMPLE" in sol:
        refuse("fvSolution still mentions SIMPLE after removal")
    # remove the steady relaxationFactors block (transient uses relaxation 1, added below)
    sol, nr = re.subn(r"relaxationFactors\s*\{.*?\n\}\s*\n?", "", sol, flags=re.S)
    if nr != 1:
        refuse("fvSolution: expected exactly one relaxationFactors block to remove, found %d" % nr)
    # INJECT *Final entries INSIDE the existing solvers block, before its closing brace (no 2nd solvers
    # dict): match the end of the "(U|T|k|omega)" solver dict + the solvers-closing brace.
    inject = ('        relTol          0.1;\n    }\n'
              '    p_rghFinal\n    {\n        $p_rgh;\n        relTol          0;\n    }\n'
              '    "(U|T|k|omega)Final"\n    {\n        $U;\n        relTol          0;\n    }\n}')
    sol, ni = re.subn(r"        relTol          0\.1;\n    \}\n\}", inject, sol)
    if ni != 1:
        refuse("fvSolution: could not locate the solvers-closing brace to inject the *Final entries "
               "(found %d) -- the frozen build_t4 solvers block may have moved" % ni)
    # append PIMPLE + transient relaxation 1 (the $p_rgh / $U macros resolve inside the same solvers dict)
    sol = sol.rstrip() + "\n" + (
        "\nPIMPLE\n{\n"
        "    momentumPredictor           yes;\n"
        "    nOuterCorrectors            2;\n"
        "    nCorrectors                 2;\n"
        "    nNonOrthogonalCorrectors    1;\n"
        "    pRefCell                    0;\n"
        "    pRefValue                   0;\n"
        "}\n"
        "\nrelaxationFactors\n{\n    fields    { \".*\" 1; }\n    equations { \".*\" 1; }\n}\n")
    files["fvSolution"] = sol

    # ---- controlDict: rebuilt transient (fixed deltaT, functionObjects, purgeWrite 0) ----
    if abs((END_TIME_S / deltaT) - round(END_TIME_S / deltaT)) > 1e-9:
        refuse("endTime %.10g s is not an exact multiple of deltaT %.3e s -- the fixed-dt clause-5 "
               "generalisation requires endTime/deltaT to be integer" % (END_TIME_S, deltaT))
    n_steps = int(round(END_TIME_S / deltaT))
    control = (
        "%s\napplication     buoyantBoussinesqPimpleFoam;\n"
        "startFrom       startTime;\nstartTime       0;\n"
        "stopAt          endTime;\nendTime         %.10g;\n"
        "deltaT          %.10g;\nadjustTimeStep  no;\n"
        "writeControl    runTime;\nwriteInterval   %.10g;\npurgeWrite      0;\n"
        "writeFormat     ascii;\nwritePrecision  12;\nwriteCompression off;\n"
        "timeFormat      general;\ntimePrecision   8;\nrunTimeModifiable false;\n"
        "\nfunctions\n{\n%s%s}\n"
        % (B.header("dictionary", "controlDict", "system"),
           END_TIME_S, deltaT, FULLFIELD_WRITE_S,
           _field_average_block(), _sampled_sets_block()))
    files["controlDict"] = control
    return files, n_steps


def decompose_par_dict(nranks, coeffs):
    """Deterministic `simple` geometric decomposition (ruling 19b7330a condition 1; doctrine C1).
    Reproducible from this dict alone.  Refuses unless the coeff product equals nranks and the wedge
    z-split is 1."""
    n1, n2, n3 = coeffs
    if n1 * n2 * n3 != nranks:
        refuse("decomposeParDict: simpleCoeffs %s product %d != numberOfSubdomains %d"
               % (coeffs, n1 * n2 * n3, nranks))
    if n3 != 1:
        refuse("decomposeParDict: the 2.5 deg wedge is one cell thick in z; the z-split must be 1, got %d" % n3)
    return ("%s\nnumberOfSubdomains %d;\nmethod          %s;\n\n"
            "simpleCoeffs\n{\n    n           (%d %d %d);\n    delta       0.001;\n}\n"
            % (B.header("dictionary", "decomposeParDict", "system"),
               nranks, DECOMP_METHOD, n1, n2, n3))


def build(root, deltaT):
    case = os.path.join(root, CASE)
    if os.path.exists(case):
        refuse("%s already exists; this builder never overwrites a case" % case)
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub))

    # FROZEN byte-identical fine mesh from build_t4e
    bmd, info = BE.block_mesh_dict(N, FIRST_CELL)
    if info["cells"] != 138240:
        refuse("frozen build_t4e fine mesh returned %d cells, expected 138240" % info["cells"])
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(bmd)

    sysfiles, n_steps = transient_system_files(deltaT)
    for nm, txt in sysfiles.items():
        open(os.path.join(case, "system", nm), "w").write(txt)
    # PARALLEL: deterministic simple decomposition (ruling 19b7330a); ONLY this dict differs from serial
    open(os.path.join(case, "system", "decomposeParDict"), "w").write(
        decompose_par_dict(NRANKS, SIMPLE_COEFFS))
    for nm, txt in B.constant_files().items():
        open(os.path.join(case, "constant", nm), "w").write(txt)
    for nm, txt in B.fields(LEVEL).items():
        open(os.path.join(case, "0.orig", nm), "w").write(txt)

    open(os.path.join(case, "CASE.txt"), "w").write("\n".join([
        "case              %s" % CASE,
        "rung              T4f (TRANSIENT/URANS successor of T4e; ERCOFTAC case025 ij2lr, H/D 2, Re 23000)",
        "solver            buoyantBoussinesqPimpleFoam (ESI v2606, STOCK system path), kOmegaSST URANS, beta 0, wedge 2.5 deg",
        "mesh              N=192 nrj=3N/2 first_cell=%.1e -> %d cells (byte-identical to frozen T4e_IJ_f)" % (FIRST_CELL, info["cells"]),
        "deltaT            %.3e s (FIXED, adjustTimeStep no) -- DRAFT placeholder; the calibration probe PINS it" % deltaT,
        "endTime           %.4g s   n_steps = endTime/deltaT = %d (exact integer -> clause-5 generalisation exact)" % (END_TIME_S, n_steps),
        "time-average      fieldAverage over U p_rgh T k omega, timeStart %.3g s (discard)" % T_INIT_S,
        "instantaneous     sampledSets G1/G2/G3 |U| lines every %d steps (for stationarity_t4f.py)" % SAMPLE_EVERY_STEPS,
        "fields / BCs      build_t4.fields()/constant_files() FROZEN, called unchanged",
        "parallel          method simple, numberOfSubdomains %d, simpleCoeffs (%d %d %d) -- deterministic "
        "(ruling 19b7330a; PARALLEL_GATE_DOCTRINE C1). Numerics IDENTICAL to serial; ONLY decomposeParDict differs."
        % (NRANKS, SIMPLE_COEFFS[0], SIMPLE_COEFFS[1], SIMPLE_COEFFS[2]),
        "STATUS            DRAFT -- NOT FROZEN, HELD for a later box window; nothing launched (rule 7)",
    ]) + "\n")
    print("built %-10s cells=%d deltaT=%.3e endTime=%.4g n_steps=%d (DRAFT)"
          % (CASE, info["cells"], deltaT, END_TIME_S, n_steps))
    return info["cells"], n_steps


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--deltaT", type=float, default=DEFAULT_DELTAT_S,
                    help="fixed time step (s); default is the DRAFT POINT placeholder %.1e" % DEFAULT_DELTAT_S)
    a = ap.parse_args()
    build(a.root, a.deltaT)
    print("U_bulk = %.4f m/s   Re = %.0f   (DRAFT builder; no compute)" % (B.U_BULK, B.RE))
