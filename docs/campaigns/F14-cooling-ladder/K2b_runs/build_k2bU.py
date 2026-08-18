#!/usr/bin/env python3
"""build_k2bU.py -- K2b-U Test B: the TRANSIENT run that decides whether this
module's oscillation is physical.

    python3 build_k2bU.py          # writes K2bU_trans beside this file

Pre-registered in `K2b_UNSTEADINESS_PREREGISTRATION.md`
(sha256 932451adb8f4e57b6243777c239f9a93b56315a701455a8af7060460f5709e1d),
written and hashed BEFORE this case was built or run.

WHY A TRANSIENT RUN IS THE DECIDING TEST
----------------------------------------
A steady SIMPLE solver has no physical time. When its monitored quantity
oscillates, the iteration index is the only axis available and it cannot say
whether the flow itself is unsteady or whether the outer iteration is chasing
its tail. `buoyantBoussinesqPimpleFoam` puts a real clock on it: in physical
time the question is direct -- does the flow settle, or does it keep moving?

The case is IDENTICAL to `K2bP_under` in geometry, mesh, fluid and every
boundary condition. What changes is the solver, the time derivative
(`steadyState` -> `Euler`), and the solution control (SIMPLE -> PIMPLE). It
starts from `K2bP_under/5000` -- the oscillating state itself -- so the question
asked is exactly "does THIS state evolve as a limit cycle?" and not "can a
transient find some other state from scratch".

TIME STEP AND RUN LENGTH
------------------------
Adjustable at maxCo 2: implicit PIMPLE with outer correctors is stable well
above Co 1, and at a 12.5 mm cell with max|U| ~ 1.1 m/s that is dt ~ 0.023 s.
40 s of physical time is ~14 aisle transit times (1.2 m / 0.29 m/s = 4.1 s) and
~13 rack-face flow-through times, so a limit cycle on any of the timescales
Test C checks would show several periods.

T_in is written every 0.1 s, which resolves a period of ~1 s with ten points and
is far finer than the S13 monitor's 50-iteration cadence.
"""
import os, sys, shutil, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_k2b as B

NAME, SRC, SRCTIME = "K2bU_trans", "K2bP_under", "5000"
END_TIME, WRITE_INT, MON_INT, MAX_CO = 40.0, 5.0, 0.1, 2.0

def main():
    case = os.path.join(HERE, NAME); src = os.path.join(HERE, SRC)
    # REFUSE CLEARLY rather than dying on a missing file three functions in.
    # Time directories are .gitignore'd, so in a fresh clone this seed does not
    # exist until step 2 of the recipe has run. Measured: without this the
    # script died with a bare FileNotFoundError on `K2bP_under/5000/U`, which
    # tells a reader nothing about which step they skipped.
    need = os.path.join(src, SRCTIME)
    if not os.path.isdir(need):
        sys.stderr.write(
            f"REFUSE: {NAME} seeds from {SRC}/{SRCTIME}, which does not exist.\n"
            f"        Solved time directories are .gitignore'd, so in a fresh\n"
            f"        clone you must run step 2 of the recipe first:\n"
            f"            bash run_k2b.sh {SRC}\n")
        return 2
    for sub in ("system", "constant", "0.orig"):
        d = os.path.join(case, sub)
        if os.path.isdir(d): shutil.rmtree(d)
        shutil.copytree(os.path.join(src, sub), d,
                        ignore=shutil.ignore_patterns("polyMesh"))
    # seed from the oscillating state, keeping THIS case's own boundaryField
    out = os.path.join(case, "0")
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(out)
    RE_BF = re.compile(r"^boundaryField\s*$", re.M)
    for f in ("U", "T", "p_rgh", "k", "omega", "nut", "alphat"):
        sp, op = os.path.join(src, SRCTIME, f), os.path.join(case, "0.orig", f)
        h = RE_BF.search(open(sp).read()); t = RE_BF.search(open(op).read())
        open(os.path.join(out, f), "w").write(
            open(sp).read()[:h.start()] + open(op).read()[t.start():])
    # ddt: steadyState -> Euler. Everything else in fvSchemes is untouched.
    sch = os.path.join(case, "system", "fvSchemes")
    s = open(sch).read().replace("    default         steadyState;",
                                 "    default         Euler;", 1)
    open(sch, "w").write(s)
    # SIMPLE -> PIMPLE
    # PIMPLE needs a `<field>Final` solver for the last outer corrector. Omit it
    # and the run dies on iteration 1 with "Entry 'p_rghFinal' not found in
    # dictionary" -- which is exactly what happened here the first time, and is
    # why the solver keys below carry the optional `Final` suffix rather than
    # being copied across from the steady case unchanged.
    sol = os.path.join(case, "system", "fvSolution")
    s = open(sol).read()
    s = s.replace('    p_rgh\n', '    "p_rgh.*"\n', 1)
    s = s.replace('    "(U|T|k|omega)"\n', '    "(U|T|k|omega).*"\n', 1)
    s = s[:s.index("SIMPLE")] + """PIMPLE
{
    momentumPredictor   yes;
    nOuterCorrectors    2;
    nCorrectors         2;
    nNonOrthogonalCorrectors 0;
}

relaxationFactors
{
    fields
    {
        p_rgh           1;
    }
    equations
    {
        U               1;
        T               1;
        "(k|omega)"     1;
    }
}
"""
    open(sol, "w").write(s)
    fos = "\n".join([
        B._sfv("T_rack_in_mdot", "rack_in", "weightedAverage", "T", "phi"),
        B._sfv("T_rack_out_area", "rack_out", "areaAverage", "T"),
        B._sfv("T_return_mdot", "return", "weightedAverage", "T", "phi"),
        B._sfv("phi_return", "return", "sum", "phi")]) \
        .replace("executeControl  timeStep", "executeControl  runTime") \
        .replace(f"executeInterval {B.MONITOR_INTERVAL}", f"executeInterval {MON_INT}") \
        .replace("writeControl    timeStep", "writeControl    runTime") \
        .replace(f"writeInterval   {B.MONITOR_INTERVAL}", f"writeInterval   {MON_INT}")
    B.w(case, "system/controlDict", "dictionary", "controlDict", f"""application     buoyantBoussinesqPimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          0.005;
writeControl    adjustableRunTime;
writeInterval   {WRITE_INT};
purgeWrite      0;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
adjustTimeStep  yes;
maxCo           {MAX_CO};
maxDeltaT       0.05;

functions
{{
{fos}
    Tspan
    {{
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        fields          (T U);
        location        true;
        writeToFile     true;
        log             true;
        executeControl  runTime;
        executeInterval {MON_INT};
        writeControl    runTime;
        writeInterval   {MON_INT};
    }}
}}
""")
    open(os.path.join(case, "CASE.txt"), "w").write(f"""case               {NAME}
kind               K2b-U TEST B -- the transient discriminator
pre-registration   K2b_UNSTEADINESS_PREREGISTRATION.md sha256 932451ad...
solver             buoyantBoussinesqPimpleFoam (transient), Euler ddt, PIMPLE
identical to       {SRC} in geometry, mesh, fluid and EVERY boundary condition
started from       {SRC}/{SRCTIME} -- the oscillating state itself
endTime            {END_TIME} s physical, adjustable dt at maxCo {MAX_CO}
monitor            T_in every {MON_INT} s
graded on          T_in peak-to-peak over the FINAL 10 s, and whether that is
                   smaller than over the preceding 10 s
verdict thresholds >= 0.30 K non-decaying = PHYSICAL; <= 0.10 K or decaying =
                   NUMERICAL; otherwise undecidable at this run length
""")
    print(f"built {NAME}: transient from {SRC}/{SRCTIME}, {END_TIME} s, maxCo {MAX_CO}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
