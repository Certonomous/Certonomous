"""Eigenspace corners run the way Emory/Iaccarino (and F6a) run them: the
turbulence model stays LIVE and the perturbation is applied as a source that
is recomputed from the current k, nut, grad U every outer iteration.  Sign
CORRECTED (`eqn -=`, per the signcheck/ verification)."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_signdemo as bs

jobs = [("live_oneC", "oneC", "-="), ("live_twoC", "twoC", "-="),
        ("live_threeC", "threeC", "-=")]
procs = []
for name, corner, op in jobs:
    d = bs.build(name, corner, op)
    print("built", d, flush=True)
    procs.append(subprocess.Popen(["bash", "-lc",
        f"source {bs.FOAM} && cd {d} && simpleFoam > log.simpleFoam 2>&1"]))
for p in procs:
    p.wait()
print("live corners done")
