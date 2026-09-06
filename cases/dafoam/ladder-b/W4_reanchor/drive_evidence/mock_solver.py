#!/usr/bin/env python3
"""MOCK container solver for the W4-reanchor PRODUCTION DRIVE.

It is NOT a solver. It emulates what one `sudo docker run ... python runScript.py`
invocation PRODUCES, so the REAL W4 drivers (run_one.sh / run_plateau.sh) can be
run end to end without a real DAFoam container, and the frozen comparator can then
be shown to grade the DRIVER-PRODUCED tree (prereg section 16, fix step 2).

The objective is SYNTHETIC (a smooth cubic in the single perturbed cell). It is
deterministic and self-consistent so the comparator's arithmetic is well defined;
it is NOT a physics result and produces no verdict about DAFoam.

It receives the `docker run` argv (everything after `run`), reads the betafile from
the mounted case dir, prints the solver-level lines DASimpleFoam would print (the
DAOption tolerance dump, Time lines, Total Residual Norm2, End) plus runScript.py's
own OBJ/GRAD lines, writes the decomposed fields at endTime, and (for compute_totals)
writes the gradient to -gradout.
"""
import os
import re
import sys
import numpy as np

NCELLS = 21000
END_TIME = 2500
BASE_OBJ = 1.5279278906359758e-02   # W4 baseline objective at 1e-6 (prereg 3), synthetic anchor
A = 1.0e-4                           # linear coeff -> gradient at beta=1 is BASE_OBJ*A (non-zero)
C3 = 3.0e-5                          # cubic coeff -> makes d(h) grow with h so F_W fails the bar
FIELDS = ("U", "p", "k", "omega", "nut", "phi")


def synthetic_obj(beta):
    d = beta - 1.0
    return BASE_OBJ * (1.0 + A * float(d.sum()) + C3 * float((d ** 3).sum()))


def synthetic_grad():
    # d(OBJ)/d(beta_c) at beta = 1 : the cubic term's derivative is 3*C3*(b-1)^2 = 0 there
    return np.full(NCELLS, BASE_OBJ * A, dtype=float)


def main():
    argv = sys.argv[1:]
    base = workdir = None
    for i, a in enumerate(argv):
        if a == "-v" and i + 1 < len(argv):
            base = argv[i + 1].split(":")[0]
        elif a == "-w" and i + 1 < len(argv):
            workdir = argv[i + 1]
    cmd = argv[-1]                                   # the `bash -lc "<cmd>"` string
    # runScript args
    def opt(name, default=None):
        m = re.search(r"%s\s+(\S+)" % re.escape(name), cmd)
        return m.group(1) if m else default
    task = opt("-task", "run_model")
    betafile = opt("-betafile", "")
    primalTol = opt("-primalTol", "1e-6")
    gradout = opt("-gradout", "cbfs_beta_grad.npy")

    if base is None or workdir is None:
        sys.stderr.write("mock_solver: could not parse -v/-w from docker argv\n")
        return 1
    casedir = os.path.join(base, workdir[len("/mnt"):].lstrip("/"))  # /mnt/cbfs_beta -> BASE/cbfs_beta

    beta = np.ones(NCELLS)
    if betafile:
        bp = os.path.join(casedir, betafile)
        if os.path.isfile(bp):
            beta = np.load(bp)
    obj = synthetic_obj(beta)

    # ----- solver-level stdout (captured by run_one.sh into log.<tag>) -----
    out = sys.stdout
    out.write("Create mesh for time = 0\n\n")
    out.write("Selecting DASolver DASimpleFoam\n")
    # DAOption dump. RE_TOL / RE_DIFF anchor on whitespace + ';' (N-D43 prefix trap).
    out.write("DAOption\n{\n")
    out.write("    primalMinResTol %s;\n" % primalTol)
    out.write("    primalMinResTolDiff 100;\n")
    out.write("}\n")
    out.write("DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU\n")
    for t in (1, 2, END_TIME - 1, END_TIME):
        out.write("Time = %d\n\n" % t)
        out.write("Total Residual Norm2: %.14e\n" % (1.0e-3 / t))
        out.write("ExecutionTime = %d s\n\n" % t)
    if task == "compute_totals":
        out.write("TIMING primal_wall_s: 300.0\n")
        out.write("TIMING adjoint_wall_s: 300.0\n")
        out.write("TIMING compute_totals_total_wall_s: 600.0\n")
        out.write("OBJ varianceU: %.16e\n" % obj)
        g = synthetic_grad()
        out.write("GRAD n=%d norm=%.10e min=%.6e max=%.6e\n"
                  % (g.size, np.linalg.norm(g), g.min(), g.max()))
        np.save(os.path.join(casedir, gradout), g)   # -gradout is RELATIVE to cwd (=casedir)
    else:
        out.write("TIMING run_model wall_s: 220.0\n")
        out.write("OBJ varianceU: %.16e\n" % obj)
    out.write("End\n")
    out.flush()

    # ----- decomposed fields at endTime (run_plateau.sh moves these to fields_<tag>) -----
    for p in range(4):
        d = os.path.join(casedir, "processor%d" % p, str(END_TIME))
        os.makedirs(d, exist_ok=True)
        for fld in FIELDS:
            with open(os.path.join(d, fld), "w") as fh:
                fh.write("// mock %s field, processor%d, t=%d\n" % (fld, p, END_TIME))
    return 0


if __name__ == "__main__":
    sys.exit(main())
