#!/usr/bin/env python3
"""SUBOFF A1h L1M sweep -- REPORTED, NOT GRADED: window means over the registered window.

THIS FILE DOES NOT GRADE ANYTHING.  The grading path for this act is fixed by
`verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md` §8 at
`cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py`, and a grade produced by any other
path is NOT A RESULT.  This reader emits NUMBERS ONLY -- no gate, no band, no verdict.

THE WINDOW IS READ OUT OF THE FROZEN DOCUMENT, NOT INVENTED:
  - the graded instant is `endTime` (prereg §4.1: "from force.dat / moment.dat
    total_* columns at endTime").  That value is the comparator's, quoted here only
    so the mean can be read beside it.
  - the only window the document registers is the PLATEAU window of §8.1a, "the
    final 500 iterations".  The mean below is over exactly that tail, selected the
    same way the frozen comparator selects it (sorted rows, last 500).

RULE 3.  It plants a synthetic force.dat carrying a KNOWN mean over a known final-500
window plus a decoy row outside the window, reads it back FROM DISK through the same
function the real numbers use, and REFUSES (exit 2) if the reader cannot see it.  A
zero -- or any number -- from a reader not shown able to see a planted non-zero is not
evidence.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "cases", "navier_class", "SUBOFF_A1"))

END_TIME = 3000
WINDOW   = 500                      # prereg 8.1a, the only registered window
BETAS    = (-12, -8, -4, 0, 4, 8, 12)
CASE_DIRS = {-12: "BETA_m12", -8: "BETA_m08", -4: "BETA_m04", 0: "BETA_p00",
             4: "BETA_p04", 8: "BETA_p08", 12: "BETA_p12"}

import grade_suboff_a1h as G     # the frozen readers, reused, never reimplemented


def window_mean(case, fo, leaf, comp, end_time=END_TIME, window=WINDOW):
    """Mean of one total_* component over the final `window` rows at or below endTime.

    comp: 0/1/2 -> x/y/z of the total_ vector, the same tuple the frozen
    `read_force_dat` builds and the same one `grade_run_root` indexes.
    """
    series, _prov, _conf = G.fo_series(case, fo, leaf)
    ts = sorted(t for t in series if t <= end_time)
    tail = ts[-window:]
    if len(tail) < window:
        return {"n": len(tail), "mean": None,
                "note": f"only {len(tail)} rows available, the registered window is {window}"}
    vals = [series[t][comp] for t in tail]
    return {"n": len(tail), "t_first": tail[0], "t_last": tail[-1],
            "mean": sum(vals) / len(vals),
            "min": min(vals), "max": max(vals),
            "at_endTime": series[float(end_time)][comp] if float(end_time) in series else None}


# ------------------------------------------------------------- rule 3 plant ---
def plant(scratch):
    """A synthetic force.dat whose final-500 mean is EXACTLY known, plus a decoy row
    far outside the window.  The reader must return the planted mean and must NOT be
    dragged by the decoy."""
    d = os.path.join(scratch, "plant_window", "postProcessing", "forces", "0")
    os.makedirs(d, exist_ok=True)
    PLANTED = 1.234e-03           # the house plant constant
    DECOY   = 5.678e-03           # sits at t=1, OUTSIDE the final-500 window
    lines = ["# Force", "# CofR : (2.013 0 0)",
             "# Time  (total_x total_y total_z) (pressure_x pressure_y pressure_z) (viscous_x viscous_y viscous_z)"]
    for t in range(1, END_TIME + 1):
        z = DECOY if t == 1 else PLANTED
        lines.append(f"{t}\t(0 0 {z!r})\t(0 0 0)\t(0 0 0)")
    with open(os.path.join(d, "force.dat"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    case = os.path.join(scratch, "plant_window")
    got = window_mean(case, "forces", "force.dat", 2)
    if got["n"] != WINDOW:
        sys.stderr.write(f"REFUSED (rule 3): the window reader took {got['n']} rows, "
                         f"not the registered {WINDOW}.\n"); sys.exit(2)
    if got["mean"] is None or abs(got["mean"] - PLANTED) > 1e-15:
        sys.stderr.write(f"REFUSED (rule 3): planted final-500 mean {PLANTED!r} read "
                         f"back as {got['mean']!r}. The reader cannot see the plant, "
                         f"so nothing it prints about the real cases is evidence.\n")
        sys.exit(2)
    # the decoy must NOT be in the window -- a reader that took the FIRST 500 rows
    # would be dragged by it, and that is exactly the P-A failure in a mean's clothing
    dragged = PLANTED + (DECOY - PLANTED) / WINDOW
    if abs(got["mean"] - dragged) < 1e-12:
        sys.stderr.write("REFUSED (rule 3): the reader took the FIRST 500 rows; the "
                         "decoy at t=1 moved the mean.\n"); sys.exit(2)
    return {"planted_mean": PLANTED, "read_back": got["mean"], "decoy_at_t1": DECOY,
            "decoy_in_window": False, "window_rows": got["n"],
            "verdict_of_the_plant_only": "the reader sees the plant"}


def main():
    run_root, scratch, out = sys.argv[1], sys.argv[2], sys.argv[3]
    rep = {"file": os.path.relpath(os.path.abspath(__file__), REPO),
           "THIS_FILE_DOES_NOT_GRADE": (
               "REPORTED, NOT GRADED. The grading path is fixed at prereg 8 to "
               "cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py; a grade from any "
               "other path is NOT A RESULT. No gate, band or verdict is computed here."),
           "window_definition": (
               "final 500 iterations, prereg 8.1a -- the only window the frozen "
               "document registers. The GRADED instant is endTime (prereg 4.1)."),
           "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rep["rule3_plant"] = plant(os.path.abspath(scratch))
    rows = {}
    for b in BETAS:
        c = os.path.join(run_root, CASE_DIRS[b])
        r = {"case": c}
        for label, fo, leaf, comp in (("F_z_total_mesh", "forces", "force.dat", 2),
                                      ("M_y_total_mesh", "forces", "moment.dat", 1),
                                      ("F_z_hull_mesh", "forcesHull", "force.dat", 2),
                                      ("F_z_sail_mesh", "forcesSail", "force.dat", 2)):
            try:
                r[label] = window_mean(c, fo, leaf, comp)
            except Exception as e:
                r[label] = {"status": f"BLOCKED: {e}"}
        # the same numbers in Roddy's frame, via the FROZEN transform, reported only
        fm = r.get("F_z_total_mesh", {}).get("mean")
        mm = r.get("M_y_total_mesh", {}).get("mean")
        if fm is not None and mm is not None:
            yp, np_ = G.nondim(fm, mm)
            r["Y_prime_from_window_mean_REPORTED"] = yp
            r["N_prime_from_window_mean_REPORTED"] = np_
        rows[str(b)] = r
    rep["points"] = rows
    with open(out, "w") as fh:
        json.dump(rep, fh, indent=2, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
