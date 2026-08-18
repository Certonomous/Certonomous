#!/usr/bin/env python3
"""write_log_digest.py -- distil each case's solver log into a committable digest.
F14 rung K0c-T.

    python3 write_log_digest.py

WHY, AND WHAT IS BEING GIVEN UP, SAID PLAINLY.  This rung's nine solver logs
total **511 MB** -- one case alone ran 140 000 outer iterations to establish that
it never reaches steady state, and an OpenFOAM log is eight lines per iteration.
Gzipped they are still ~90 MB, which is not a thing to put in a documentation
repository.  The laminar rung committed its logs whole and could, because its
longest case was 12 000 iterations.

So the full logs are **gitignored for this rung**, and this is what replaces
them, generated rather than curated:

  * the entire header, verbatim, up to the first `Time =` -- solver banner,
    dictionary echoes, `Selecting turbulence model type ...`, `Selecting finite
    volume options ...`.  Every control's IN-LOG WITNESS of its plant lives here;
  * the counts that the controls are graded on: outer iterations, and the number
    of k, omega and epsilon solves (C1's witness is that these are ZERO);
  * every function-object block the running solver printed, decimated;
  * the residual lines, decimated;
  * the last 120 lines verbatim, which is where a solver says why it stopped;
  * the SHA-256 and byte length of the log this digest was taken from, so the
    digest is anchored to one artefact rather than floating.

WHAT IS LOST: the per-iteration residual trace between the decimated samples.
WHAT IS NOT LOST: the graded series, which lives in `<case>/MONITOR.tsv`, and
every in-log witness the controls rest on.

The logs are reproducible: `run_cases.sh` and the two continuation scripts are
committed, the dictionaries are committed, and `build_cases.py` regenerates every
dictionary byte-identically (verified from a fresh temporary directory).
"""
import hashlib
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ["T_lo_c", "T_lo_f", "T_hi_c", "T_hi_f", "M_hi_f_LS",
         "C1_hi_c_laminar", "C2_hi_c_Ra130", "B_hi_c_adiabatic", "S_hi_c_seed100"]
RESID_EVERY = 500
FO_EVERY = 5000
TAIL = 120


def digest_one(path, fh):
    raw = open(path, "rb").read()
    fh.write("=" * 78 + "\n")
    fh.write(f"LOG {os.path.basename(path)}\n")
    fh.write(f"  bytes      {len(raw)}\n")
    fh.write(f"  sha256     {hashlib.sha256(raw).hexdigest()}\n")
    lines = raw.decode("utf-8", "replace").splitlines()
    first_time = next((i for i, l in enumerate(lines) if l.startswith("Time = ")), len(lines))
    n_it = sum(1 for l in lines if l.startswith("Time = "))
    counts = {k: sum(1 for l in lines if f"Solving for {k}," in l)
              for k in ("k", "omega", "epsilon", "T", "Ux")}
    fh.write(f"  outer iterations in this log   {n_it}\n")
    fh.write(f"  solves: k={counts['k']} omega={counts['omega']} "
             f"epsilon={counts['epsilon']} T={counts['T']} Ux={counts['Ux']}\n")
    fh.write("-" * 78 + "\nHEADER, VERBATIM (every in-log witness of a plant is here)\n" + "-" * 78 + "\n")
    for l in lines[:first_time]:
        fh.write(l + "\n")
    fh.write("-" * 78 + f"\nBODY, DECIMATED (residuals every {RESID_EVERY} iterations, "
             f"function objects every {FO_EVERY})\n" + "-" * 78 + "\n")
    it = 0
    emit_resid = emit_fo = False
    for l in lines[first_time:len(lines) - TAIL]:
        m = re.match(r"^Time = (\d+)", l)
        if m:
            it = int(m.group(1))
            emit_resid = (it % RESID_EVERY == 0)
            emit_fo = (it % FO_EVERY == 0)
            if emit_resid or emit_fo:
                fh.write("\n" + l + "\n")
            continue
        if emit_resid and ("Solving for" in l or "continuity errors" in l
                           or "ExecutionTime" in l):
            fh.write(l + "\n")
        elif emit_fo and (" of " in l or "write:" in l or "Probe" in l):
            fh.write(l + "\n")
    fh.write("-" * 78 + f"\nLAST {TAIL} LINES, VERBATIM\n" + "-" * 78 + "\n")
    for l in lines[-TAIL:]:
        fh.write(l + "\n")
    fh.write("\n")


def main():
    for c in CASES:
        case = os.path.join(HERE, c)
        logs = sorted(f for f in os.listdir(case)
                      if f.startswith("log.buoyantBoussinesqSimpleFoam"))
        with open(os.path.join(case, "LOG_DIGEST.txt"), "w") as fh:
            fh.write(__doc__.split("\n\n", 1)[0] + "\n")
            fh.write(f"case {c}; stages in order: {logs}\n\n")
            for lg in logs:
                digest_one(os.path.join(case, lg), fh)
        sz = os.path.getsize(os.path.join(case, "LOG_DIGEST.txt"))
        print(f"{c:<18} {len(logs)} stage(s) -> LOG_DIGEST.txt {sz/1024:.0f} KB")


if __name__ == "__main__":
    main()
