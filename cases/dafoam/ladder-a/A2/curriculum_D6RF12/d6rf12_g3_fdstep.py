#!/usr/bin/env python3
"""G3-FDSTEP -- the repaired FD-completion gate, for the D6RF11 successor.

WHY IT EXISTS.  D6RF11's G3 counted `len(rows)` of ANY kind against a minimum of
1 and PRINTED the total as "FD sample rows".  It PASSED on a single
`kind: "endpoint_dvs"` DV-inventory row written at log line 8, BEFORE any FD work,
while the producer's terminal marker never printed and its first primal died at
line 2748.  A gate that cannot tell an FD sample from an inventory.

THIS GATE READS THE KIND, AND REQUIRES THE PRODUCER'S OWN TERMINAL MARKER.
Two independent limbs, because either alone is forgeable by an early exit.
"""
import json

FD_STEP_KIND = "fd_step"
TERMINAL_MARKER = "D6RF3_FD_ENDPOINT_WRITTEN"
G3_MIN_FD_STEP_ROWS = 1


def g3_fdstep(jsonl_text, log_text):
    rows, malformed = [], 0
    for line in jsonl_text.splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            malformed += 1                      # counted, never silently skipped
    kinds = {}
    for r in rows:
        k = r.get("kind", "<no kind field>")
        kinds[k] = kinds.get(k, 0) + 1
    n_fd = kinds.get(FD_STEP_KIND, 0)
    marker = TERMINAL_MARKER in log_text
    out = {"n_rows_total": len(rows), "n_malformed": malformed, "kinds": kinds,
           "n_fd_step_rows": n_fd, "min_required": G3_MIN_FD_STEP_ROWS,
           "terminal_marker": TERMINAL_MARKER, "terminal_marker_present": marker,
           "limb_fd_step_rows": n_fd >= G3_MIN_FD_STEP_ROWS,
           "limb_producer_completed": marker}
    out["verdict"] = "PASS" if (n_fd >= G3_MIN_FD_STEP_ROWS and marker) else "FAIL"
    return out


def drive_both_ways(real_jsonl_path, real_log_path):
    """The gate is driven in BOTH directions before it is trusted.
    A gate that has only ever seen its passing case is how G3 shipped."""
    real_jsonl = open(real_jsonl_path, errors="replace").read()
    real_log = open(real_log_path, errors="replace").read()
    ctrl = {}

    # --- NEGATIVE: D6RF11's REAL inventory-only file. MUST FAIL.
    neg = g3_fdstep(real_jsonl, real_log)
    ctrl["negative_real_d6rf11"] = neg

    # --- POSITIVE: the same file plus ONE PLANTED fd_step row, and a log
    #     carrying the producer's terminal marker. MUST PASS.
    planted_row = json.dumps({"kind": FD_STEP_KIND, "dv": "twist", "idx": 0,
                              "which": "central", "row": {"h": 1.234e-03,
                              "dJdx": 5.678e-04}}, sort_keys=True)
    pos = g3_fdstep(real_jsonl + "\n" + planted_row + "\n",
                    real_log + "\n%s d6rf3_fd_endpoint.jsonl n_rows=2\n" % TERMINAL_MARKER)
    ctrl["positive_planted_fd_step"] = pos

    # --- THIRD DIRECTION: fd_step row present but producer DID NOT complete.
    #     MUST FAIL -- an early exit must not be able to forge completion.
    half = g3_fdstep(real_jsonl + "\n" + planted_row + "\n", real_log)
    ctrl["negative_fd_step_without_marker"] = half

    ctrl["state"] = ("EXERCISED-PASS"
                     if (neg["verdict"] == "FAIL" and pos["verdict"] == "PASS"
                         and half["verdict"] == "FAIL") else "EXERCISED-FAIL")
    return ctrl


if __name__ == "__main__":
    import sys
    c = drive_both_ways(sys.argv[1], sys.argv[2])
    print(json.dumps(c, indent=1, sort_keys=True))
    sys.exit(0 if c["state"] == "EXERCISED-PASS" else 3)
