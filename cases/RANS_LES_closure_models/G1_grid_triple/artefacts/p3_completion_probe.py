# Diagnostic ONLY. Imports the FROZEN comparator unmodified and calls its own
# completion() and iterative() to enumerate which clauses hold. It computes NO
# functional value, NO triple, NO order, NO GCI and NO verdict.
import sys, os
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/G1_grid_triple")
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import grade_g1 as G
from pathlib import Path
root = Path("/home/ubuntu/closure-data/g1")
for name, ncells, end in G.LEVELS:
    phys, infra, log = G.completion(root / name, end, ncells)
    it = G.iterative(log, end) if not phys else ["(not evaluated: physics clauses failed)"]
    p3 = [x for x in phys if x.startswith("P3")]
    other = [x for x in phys if not x.startswith("P3")]
    print("--- %s (%d cells, endTime %d)" % (name, ncells, end))
    print("    PHYSICS failures, P3 fatal-clause : %d  %s" % (len(p3), p3))
    print("    PHYSICS failures, ALL OTHER       : %d  %s" % (len(other), other))
    print("    INFRASTRUCTURE                    : %d  %s" % (len(infra), infra))
    print("    ExecutionTime lines = %d  (endTime %d)  End=%s  gradP prints=%d"
          % (log["exec_count"], end, log["end"], len(log["gradP_hist"])))
    print("    final residuals: %s" % {k: "%.3e" % v for k, v in sorted(log["final_res"].items())})
# iterative() with physics ignored, to see the convergence clauses themselves
print()
for name, ncells, end in G.LEVELS:
    _p, _i, log = G.completion(root / name, end, ncells)
    print("%s iterative clauses: %r" % (name, G.iterative(log, end)))
