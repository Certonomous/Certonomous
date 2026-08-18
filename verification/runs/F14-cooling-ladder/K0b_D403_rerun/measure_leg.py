#!/usr/bin/env python3
"""measure_leg.py -- run the VERBATIM analyse_k0b_mesh.measure() on one case.

    python3 measure_leg.py <case-dir> <tag>

Writes `measured_<tag>.json` beside this file.  The point of this wrapper is
that it adds no arithmetic of its own: `analyse_k0b_mesh.py` in this directory
is a byte-identical copy of the committed module (`cmp` asserted at setup), and
every number below comes out of its `measure()`.  A re-run that grades a
published number with a freshly written estimator grades the estimator.

It exists because `analyse_k0b_mesh.main()` hard-codes its three legs as
(K0b_m32, the archive case, K0b_m128) and this re-run measures FIVE cases --
including a fresh 64x64 leg, and a COPY of the archive case so that nothing is
written into the committed tree.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_k0b_mesh as A  # noqa: E402

case = os.path.abspath(sys.argv[1])
tag = sys.argv[2]
res = A.measure(case)
out = os.path.join(HERE, f"measured_{tag}.json")
with open(out, "w") as fh:
    json.dump(res, fh, indent=2)
print(f"{tag}: t={res['time']} mesh={res['mesh']} "
      f"Nu_avg_hot={res['Nu_avg_hot']!r}")
print(f"  wrote {out}")
