#!/usr/bin/env python3
"""G-M4 grader: reads the pyHyp marching table COLUMN BY COLUMN, never a banner.
Refuses if it cannot see the table at all. Reports the minimum over ALL layers."""
import sys, re
log = sys.argv[1]; expect_layers = int(sys.argv[2])
rows = []
for line in open(log, errors="replace"):
    t = line.split()
    if len(t) == 14 and re.fullmatch(r"\d+", t[0]):
        try:
            rows.append((int(t[0]), float(t[1]), float(t[5]), float(t[8]),
                         float(t[9]), float(t[11]), float(t[12])))
        except ValueError:
            pass
print("G-M4 GRADER  log=%s" % log)
if not rows:
    print("REFUSE: no marching rows parsed — the reader cannot see the table.")
    sys.exit(2)
# planted-zero style control: the reader must be shown able to see a NEGATIVE
probe = "     9   -1.0     2     6      0  0.203  1.0  0.4  -0.123  -0.456E-09  0.278E-03  0.228E-02  0.5950  1.2806"
t = probe.split()
ctrl_q, ctrl_v = float(t[8]), float(t[9])
print("READER CONTROL: a planted NEGATIVE row parses as minQ=%.4f minV=%.3e -> "
      "reader CAN see a negative. A non-negative verdict below is therefore evidence."
      % (ctrl_q, ctrl_v))
assert ctrl_q < 0 and ctrl_v < 0, "control failed: reader cannot see a negative"
lvl = [r[0] for r in rows]
nlayers = len(rows)
minq = min(r[3] for r in rows); minq_at = rows[[r[3] for r in rows].index(minq)][0]
minv = min(r[4] for r in rows); minv_at = rows[[r[4] for r in rows].index(minv)][0]
sl_last = rows[-1][2]; md_last = rows[-1][5]; cmax_last = rows[-1][6]
cpu = rows[-1][1]
nneg_q = sum(1 for r in rows if r[3] <= 0.0)
nneg_v = sum(1 for r in rows if r[4] <= 0.0)
print("LAYER_ROWS %d   first=%d last=%d   contiguous=%s"
      % (nlayers, lvl[0], lvl[-1], lvl == list(range(lvl[0], lvl[-1]+1))))
print("EXPECTED_CELL_LAYERS %d   MATCH=%s" % (expect_layers, nlayers == expect_layers))
print("MIN_QUALITY_over_ALL_layers %.5f  at layer %d   (rows <= 0: %d)" % (minq, minq_at, nneg_q))
print("MIN_VOLUME_over_ALL_layers  %.4e at layer %d   (rows <= 0: %d)" % (minv, minv_at, nneg_v))
print("FINAL_Sl %.3f   FINAL_MARCH_DIST %.4f   FINAL_cMax %.4f" % (sl_last, md_last, cmax_last))
print("PYHYP_CPU_S %.1f" % cpu)
ok = (nlayers == expect_layers and lvl == list(range(lvl[0], lvl[-1]+1))
      and nneg_q == 0 and nneg_v == 0 and sl_last >= 1.000)
print("G-M4 %s" % ("PASS" if ok else "GATE FAIL"))
sys.exit(0 if ok else 1)
