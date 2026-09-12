#!/usr/bin/env python3
"""Write CAP_FLAG.cumulative.txt at the CUMULATIVE cap crossing.

ADDITIVE.  It never writes, moves or reads-for-overwrite the instrument's own
CAP_FLAG.txt, never edits monitor_k2g.py, never restarts it, and never signals
the solver.  It is a SECOND READING beside the instrument's, and the file it
writes says which is which.

Ruled by the heat-transfer supervisor 2026-09-12 on this lane's request.
"""
import os
import time

CASE = "/home/ubuntu/Certonomous/verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3"
LOG = os.path.join(CASE, "log.solve")
OUT = os.path.join(CASE, "CAP_FLAG.cumulative.txt")
INSTRUMENT_FLAG = os.path.join(CASE, "CAP_FLAG.txt")
RANKS = 4
CAP = 1260.0
POINT = 420.0
MONITOR_T0 = 1789249767          # 2026-09-12T21:49:27Z -- the RESUME, not the launch


def segments():
    segs, cur = [], None
    with open(LOG, errors="replace") as fh:
        for line in fh:
            if line.startswith("Build  :"):
                cur = []
                segs.append(cur)
            elif cur is not None and line.startswith("ExecutionTime = "):
                try:
                    cur.append(float(line.split("=")[1].split("s")[0]))
                except (ValueError, IndexError):
                    pass
    return [s[-1] if s else 0.0 for s in segs]


while True:
    if os.path.exists(OUT):
        break
    try:
        ex = segments()
    except OSError:
        time.sleep(60)
        continue
    tot = sum(ex)
    cm = tot * RANKS / 60.0
    if cm > CAP:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        mono = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                             time.gmtime(MONITOR_T0 + CAP * 60.0 / RANKS))
        rows = "\n".join(
            "  segment %d : %10.2f solver wall-s = %8.2f core-min" % (i, e, e * RANKS / 60.0)
            for i, e in enumerate(ex, 1))
        with open(OUT, "w") as fh:
            fh.write(f"""{now}

CAP_FLAG -- CUMULATIVE READING.  A SECOND READING, NOT THE AUTHORITATIVE FLAG.

THE AUTHORITATIVE FLAG IS THE INSTRUMENT'S OWN CAP_FLAG.txt, written beside this
file by monitor_k2g.py.  This file exists because the two readings disagree by a
knowable amount for a knowable reason, and a reader standing in this directory
should find the reason here rather than infer it.

THE REGISTERED CAP IS 1260 core-min (K2h_PREREGISTRATION.md section 8).  IT IS
NOT RAISED BY THIS FILE OR BY ANY AGENT.  Raising or retiring a cap is Sanaa's
alone.  PER HER 2026-09-12 04:20Z DIRECTIVE #17 THE CAP IS A FLAG AND NOT A STOP:
the run is NOT stopped, no guard is armed, no signal is sent.

--------------------------------------------------------------------------------
THE TWO READINGS

  THIS FILE (cumulative)   : {cm:.1f} core-min, crossed cap {CAP:g} at {now}
  monitor_k2g.py CAP_FLAG  : charges the RESUMED SEGMENT ONLY, and will therefore
                             stamp its own crossing at approximately {mono}

  The gap is {(cm - ex[-1] * RANKS / 60.0):.2f} core-min of segment-1 work, which is
  about 54.5 minutes of wall clock.

PER-SEGMENT SPLIT, summed from each segment's own last ExecutionTime line after
splitting log.solve at its `Build  :` banners:

{rows}
  ------------------------------------------------------------
  TOTAL     : {tot:10.2f} solver wall-s = {cm:8.2f} core-min
              = {cm / POINT:.2f}x POINT {POINT:g}, {cm / CAP:.2f}x cap {CAP:g}

--------------------------------------------------------------------------------
THE CAUSE, NAMED

monitor_k2g.py computes its cap charge as (time.time() - t0) * ranks / 60, and
its t0 is its own start: {MONITOR_T0} = 2026-09-12T21:49:27Z.  THAT IS THE
RESUME, NOT THE ORIGINAL LAUNCH.  Segment 1's 3,269.86 solver wall-s = 217.99
core-min are therefore invisible to it.

THIS IS NOT A DEFECT THE MONITOR INTRODUCED, AND IT IS NOT BROKEN FOR THE RUN IT
WAS WRITTEN FOR.  Its t0 is correct for a single-segment run, and K2h_L3 is the
first RESUMED run it has ever monitored.  This is a gap the resume EXPOSED, not
one the instrument created.

THE INSTRUMENT WAS NOT EDITED.  It is live on a live run and other records cite
it; AMENDMENT 1 section A1.3's own discipline is that an instrument is EXTENDED
rather than edited to make a rule true.  This file is the extension.

--------------------------------------------------------------------------------
WHAT THIS CROSSING MEANS, AND WHAT IT DOES NOT

Under this entry's own `_field_classes` rule (L-342) cost is an INFRASTRUCTURE
field.  A crossing VOIDS NO PHYSICS and STOPS NOTHING.  The cause of the overrun
is registered in ADDENDUM 2 as a MISPREDICTION and specifically a WRONG SCALING
LAW: section 8 scaled a Courant-limited time step by the linear cell-count ratio
1.69 when the true ratio is 13.6x, because on a locally refined mesh the Courant
limit is set by the SMALLEST cell and not the mean.  Measured mean deltaT is
0.0059102 s against a registered 0.0475 s.

WHETHER A CAP CROSSING FORCES `NOT A RESULT` IS ESCALATED AND UNRULED, and this
file does not settle it.  The conflict on the record: her item 7 ("cap -> NOT A
RESULT, never raised") against her 2026-08-26 universal rule that bookkeeping
never voids physics, against `_field_classes`.  The comparator therefore reports
the physics gate on its own merits and states this crossing as a SEPARATE, NAMED
infrastructure fact beside it, folding it into the verdict in NEITHER direction.

Instrument CAP_FLAG.txt present at the moment this was written: {os.path.exists(INSTRUMENT_FLAG)}
Written by the heat-transfer lane's cumulative cap watcher, on the supervisor's
2026-09-12 ruling.  Nothing here is sent, filed, uploaded, registered, posted or
commented outside this box (rule 7).
""")
        break
    time.sleep(60)
