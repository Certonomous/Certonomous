import re, sys, json, shutil, os
LOG = "/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility/XM/XM.log"
START = re.compile(r"^Running Primal Solver\s")
TIME  = re.compile(r"^Time = (\d+)\s*$")
RES   = re.compile(r"^(\S+) initRes: ([0-9.eE+-]+) finalRes: ([0-9.eE+-]+) nIters: (\d+)\s*$")
TOL   = "satisfied the prescribed tolerance"

def parse(path):
    hists, cur, t = [], None, None
    ntol = 0
    with open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if START.match(line):
                if cur is not None: hists.append(cur)
                cur = {}
                continue
            if cur is None: continue
            m = TIME.match(line)
            if m: t = int(m.group(1)); continue
            m = RES.match(line)
            if m:
                cur.setdefault(m.group(1), []).append((t, float(m.group(2)), float(m.group(3)), int(m.group(4))))
                continue
            if TOL in line: ntol += 1
    if cur is not None: hists.append(cur)
    return hists, ntol

h, ntol = parse(LOG)
print("LOG:", LOG)
print("n_primals(Running Primal Solver blocks):", len(h))
print("n_tolerance_lines:", ntol)
for i, d in enumerate(h):
    print("  primal %d: eqs=%s  samples/eq=%s  first_U0_initRes=%.6e last_U0_initRes=%.6e"
          % (i, sorted(d.keys()), {k: len(v) for k, v in sorted(d.items())},
             d["U0"][0][1], d["U0"][-1][1]))
# PLANTED CONTROL: delete one 'Running Primal Solver' block's residual lines -> must read 2, not 3
import tempfile
TD = tempfile.mkdtemp(prefix="so3af2_plant_")
p2 = os.path.join(TD, "planted.log")
src = open(LOG).read().split("Running Primal Solver")
# drop residual lines from the LAST block only
import re as _re
src[-1] = _re.sub(r"^\S+ initRes: .*\n", "", src[-1], flags=_re.M)
open(p2, "w").write("Running Primal Solver".join(src))
h2, ntol2 = parse(p2)
nz = sum(1 for d in h2 if d)
print("PLANTED (residual lines stripped from primal #3):")
print("  blocks=%d  blocks_with_residuals=%d  n_tolerance_lines=%d" % (len(h2), nz, ntol2))
print("  CONTROL DEMONSTRATED:", (len([d for d in h if d]) == 3) and (nz == 2))
shutil.rmtree(TD)
