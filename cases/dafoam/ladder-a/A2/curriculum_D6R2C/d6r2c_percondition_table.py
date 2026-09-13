#!/usr/bin/env python3
# =============================================================================
# d6r2c_percondition_table.py -- D6R2C PER-CONDITION DRAG AND LIFT READER
#
# WHAT THIS IS.  Sanaa's D6R2 run instruction item 10 owes "per-condition drag
# and lift before/after".  d6r2c_evals.jsonl records the WEIGHTED objective
# obj.J and the three CLs, but it does NOT record the three per-condition CD
# values -- measured, by enumerating the keys of every kind=="F" record:
#   {'cl04.aero_post.functionals.CL', 'cl05...CL', 'cl06...CL',
#    'geometry_cl05.thickcon', 'geometry_cl05.volcon', 'obj.J'}
# The per-condition CD exists only as the solver's own per-primal print in the
# arm log ("CD: <v> final: <v>" / "CL: <v> final: <v>"), and the log carries NO
# scenario label on those lines.  This reader therefore attributes each primal
# block to a scenario BY A MEASURED QUANTITY, never by assumed ordering:
#
#   (1) a primal block is the text between two "Starting time loop" lines; its
#       converged CD and CL are the LAST such prints inside the block;
#   (2) a window of three consecutive blocks is a candidate evaluation;
#   (3) the window is ACCEPTED only if its three converged CLs match the three
#       CLs the driver recorded for the target evaluation (to CL_TOL), AND the
#       weighted sum 0.25*CD04 + 0.50*CD05 + 0.25*CD06 reproduces that
#       evaluation's recorded obj.J to J_TOL.
#
# Clause (3) is the whole evidentiary content: the weights and the objective
# are the registration's own (PREREGISTRATION.md section 1), so a window that
# reproduces obj.J from three drag coefficients has demonstrated that those
# three drag coefficients ARE the three this objective was built from.  A
# reader that could not do that would be guessing from order.
#
# IT IS A READER.  It adds no gate, grades nothing, changes no verdict, writes
# nothing into the run directory, and starts no solver.
#
# PLANTED CONTROL (standing rule 3).  --selftest perturbs the parsed CD of one
# accepted window by PLANT and requires the corroboration check to REJECT it;
# a reader that still accepts cannot see a disagreement of that size and its
# agreement is not evidence.  Exit 2 on failure.
# =============================================================================
import argparse, json, re, sys

PLANT   = 1.234e-03
CL_TOL  = 1.0e-8      # the log prints CL at 10 significant digits
J_TOL   = 1.0e-8      # CD likewise; the weighted sum inherits that resolution
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
POINTS  = ["cl04", "cl05", "cl06"]

CD_RE = re.compile(r"^CD: ([-0-9.eE+]+) final: ([-0-9.eE+]+)\s*$")
CL_RE = re.compile(r"^CL: ([-0-9.eE+]+) final: ([-0-9.eE+]+)\s*$")


def parse_blocks(log_path):
    """Every primal block, as (start_line, converged_CD, converged_CL)."""
    blocks, cur = [], None
    with open(log_path, "r", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if line.startswith("Starting time loop"):
                if cur is not None:
                    blocks.append(cur)
                cur = {"line": i, "CD": None, "CL": None}
                continue
            if cur is None:
                continue
            m = CD_RE.match(line)
            if m:
                cur["CD"] = float(m.group(2)); continue
            m = CL_RE.match(line)
            if m:
                cur["CL"] = float(m.group(2))
    if cur is not None:
        blocks.append(cur)
    return [b for b in blocks if b["CD"] is not None and b["CL"] is not None]


def match_window(blocks, rec, plant_idx=None):
    """Windows of three consecutive blocks that reproduce rec's CLs AND obj.J."""
    cls = [rec["funcs"]["%s.aero_post.functionals.CL" % p][0] for p in POINTS]
    jrec = rec["funcs"]["obj.J"][0]
    hits = []
    for s in range(len(blocks) - 2):
        w = blocks[s:s + 3]
        if any(abs(w[k]["CL"] - cls[k]) > CL_TOL for k in range(3)):
            continue
        cds = [w[k]["CD"] for k in range(3)]
        if plant_idx is not None:
            cds = list(cds); cds[plant_idx] += PLANT
        jrec_recon = sum(WEIGHTS[POINTS[k]] * cds[k] for k in range(3))
        if abs(jrec_recon - jrec) > J_TOL:
            continue
        hits.append({"start_line": w[0]["line"],
                     "CD": {POINTS[k]: cds[k] for k in range(3)},
                     "CL": {POINTS[k]: w[k]["CL"] for k in range(3)},
                     "J_reconstructed": jrec_recon,
                     "J_recorded": jrec,
                     "J_abs_diff": abs(jrec_recon - jrec)})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--evals", required=True)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    blocks = parse_blocks(a.log)
    rows = [json.loads(l) for l in open(a.evals)]
    F = [r for r in rows if r.get("kind") == "F"]
    good = [r for r in F if r.get("fail") == 0]
    first, last = good[0], good[-1]

    out = {"n_primal_blocks": len(blocks), "n_F": len(F), "n_F_ok": len(good),
           "weights": WEIGHTS, "CL_TOL": CL_TOL, "J_TOL": J_TOL}

    for tag, rec in (("before", first), ("after", last)):
        hits = match_window(blocks, rec)
        out[tag] = {"eval_n": rec["n"], "utc": rec["utc"], "fail": rec["fail"],
                    "n_windows_matched": len(hits), "windows": hits}

    if a.selftest:
        ok = True
        n_controls = 0
        for tag, rec in (("before", first), ("after", last)):
            base = match_window(blocks, rec)
            # A design is re-solved several times in one run (line search, then
            # the gradient's own primals), so the SAME window recurs.  What must
            # be unique is the VALUE, not the occurrence: every accepted window
            # must carry the identical CD triple, or the attribution is not a
            # measurement.
            if not base:
                print("SELFTEST REFUSE: %s matched no window" % tag)
                ok = False; continue
            n_controls += 1
            ref = base[0]["CD"]
            for w in base[1:]:
                if any(abs(w["CD"][p] - ref[p]) > 1.0e-12 for p in POINTS):
                    print("SELFTEST REFUSE: %s windows disagree on CD" % tag)
                    ok = False
            for idx in range(3):
                n_controls += 1
                if match_window(blocks, rec, plant_idx=idx):
                    print("SELFTEST FAIL: %s plant %.3e at %s still accepted"
                          % (tag, PLANT, POINTS[idx])); ok = False
        if not ok:
            print("D6R2C_PERCOND SELFTEST FAIL"); sys.exit(2)
        print("D6R2C_PERCOND SELFTEST PASS n=%d  (2 value-unique windows, "
              "6 planted rejections)" % n_controls)

    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
