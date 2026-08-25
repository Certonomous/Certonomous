#!/usr/bin/env python3
"""Curriculum D8 -- the MECHANICAL step-selection rule, applied at the endpoint.

FROZEN INSTRUMENT (PREREGISTRATION.md s9, md5).  The rule is frozen before
compute; the PLAN is this script's deterministic output from (a) the endpoint
adjoint magnitudes |J_adj| and (b) the registered eta.  NO HUMAN CHOICE ENTERS.

The rule is `rung_n16_remaining_components/PREREGISTRATION.md` s4.2, carried
unchanged except for the two extended ladders registered in D8's s4.

    C(s) = 2 * |J_adj| * s / eta          eta = 1.0910e-05  (N-D13, registered)
    s_lo = smallest ladder rung with C >= 5
    s_hi = smallest ladder rung with s_hi >= 2 * s_lo
    graded step = s_hi.  It is NOT selected on agreement.

REGISTERED LIMITATION, carried verbatim from that item (RESULTS.md s3.1):
  "The rule has not been tried where the proxy |J_adj| is itself wrong -- which
   is the case it would be worst at, since it sizes the step from the very
   quantity under test."
and (PREREGISTRATION.md s9 item 9):
  "The step-selection rule of s4.2 is registered, not validated."

Usage:  d8_stepplan.py <d8_adj.json> <out fdplan.json>
        d8_stepplan.py --selftest
"""
import json, sys

ETA = 1.0910e-05

LADDER = {
    ("twist", None): [3e-2, 5e-2, 1e-1, 2e-1, 3e-1, 5e-1, 1e0],
    ("patchV", 0):   [3e-2, 1e-1, 3e-1, 1e0, 3e0],
    ("patchV", 1):   [1e-2, 3e-2, 1e-1, 3e-1, 1e0],
}
GRADEABLE = [("twist", 0), ("twist", 1), ("twist", 2), ("twist", 3),
             ("twist", 4), ("twist", 5), ("patchV", 0), ("patchV", 1)]
EXCLUDED_BY_NAME = [("twist", 6)]     # FD-ungradeable; named NOT A RESULT in advance
N_GRADEABLE = 8


def ladder_for(dv, idx):
    return LADDER.get((dv, idx), LADDER[(dv, None)]) if (dv, idx) not in LADDER else LADDER[(dv, idx)]


def clearance(J, s):
    return 2.0 * abs(J) * s / ETA


def select(dv, idx, J):
    """Return (s_lo, s_hi, C_lo, C_hi) or (None, None, ...) if no pair exists."""
    lad = ladder_for(dv, idx)
    s_lo = None
    for s in lad:
        if clearance(J, s) >= 5.0:
            s_lo = s
            break
    if s_lo is None:
        return None, None, None, None
    s_hi = None
    for s in lad:
        if s >= 2.0 * s_lo:
            s_hi = s
            break
    if s_hi is None:
        return s_lo, None, clearance(J, s_lo), None
    return s_lo, s_hi, clearance(J, s_lo), clearance(J, s_hi)


def build(adj):
    rows, plan = [], []
    for dv, idx in GRADEABLE:
        col = adj.get(dv)
        if col is None or idx >= len(col):
            raise SystemExit("REFUSE: adjoint column %s idx %d absent" % (dv, idx))
        J = float(col[idx])
        s_lo, s_hi, c_lo, c_hi = select(dv, idx, J)
        if s_lo is None or s_hi is None:
            rows.append((dv, idx, J, None, None, None, None, "NOT A RESULT"))
            continue
        rows.append((dv, idx, J, s_lo, s_hi, c_lo, c_hi, "PLANNED"))
        plan.append({"dv": dv, "idx": idx, "step": s_lo})
        plan.append({"dv": dv, "idx": idx, "step": s_hi})
    return rows, plan


def selftest():
    ok = True
    # (1) reproduce the rem item's OWN registered table from its stored adjoints.
    #     If this arithmetic were not the arithmetic that produced the published
    #     plan, the rule would have been silently substituted.
    known = {("twist", 1): (-1.750730e-03, 3e-2, 1e-1),
             ("twist", 2): (-1.469450e-03, 3e-2, 1e-1),
             ("twist", 4): (-6.277000e-04, 5e-2, 1e-1),
             ("twist", 5): (-3.797300e-04, 1e-1, 2e-1)}
    for (dv, idx), (J, e_lo, e_hi) in known.items():
        s_lo, s_hi, _, _ = select(dv, idx, J)
        good = (abs(s_lo - e_lo) < 1e-12 and abs(s_hi - e_hi) < 1e-12)
        ok &= good
        print("SELFTEST rem-repro %s %d -> {%g, %g} expected {%g, %g} %s"
              % (dv, idx, s_lo, s_hi, e_lo, e_hi, "OK" if good else "MISMATCH"))
    # (2) NEGATIVE CONTROL: a gradient too small for the whole ladder must yield
    #     NOT A RESULT, not a step.  twist idx6's stored -1.3619e-04 needs
    #     s >= 0.2003 deg for C=5, so the SHORT ladder must refuse it and the
    #     D8 ladder (which reaches 1e0) must NOT -- both branches proved live.
    s_lo, s_hi, _, _ = select("twist", 6, -1.3619e-04)
    print("SELFTEST idx6-on-D8-ladder -> {%s, %s}" % (s_lo, s_hi))
    ok &= (s_lo is not None)
    tiny = 1.0e-09
    s_lo2, s_hi2, _, _ = select("twist", 0, tiny)
    good = (s_lo2 is None and s_hi2 is None)
    ok &= good
    print("SELFTEST negative-control J=%g -> (%s, %s) %s"
          % (tiny, s_lo2, s_hi2, "REFUSED as required" if good else "FAILED TO REFUSE"))
    # (3) the plan must carry exactly 2 * N_GRADEABLE entries on a healthy adjoint
    adj = {"twist": [-2.1e-3, -1.75e-3, -1.47e-3, -1.01e-3, -6.28e-4, -3.80e-4, -1.36e-4],
           "patchV": [7.33e-4, 9.02e-3]}
    rows, plan = build(adj)
    good = (len(plan) == 2 * N_GRADEABLE)
    ok &= good
    print("SELFTEST plan-size %d expected %d %s" % (len(plan), 2 * N_GRADEABLE, "OK" if good else "BAD"))
    # (4) the excluded component must never appear in a plan
    good = not any((p["dv"], p["idx"]) in EXCLUDED_BY_NAME for p in plan)
    ok &= good
    print("SELFTEST twist-idx6-excluded %s" % ("OK" if good else "LEAKED INTO PLAN"))
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 2


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    if selftest() != 0:
        sys.exit("REFUSE: selftest failed; no plan written")
    adj = json.loads(open(sys.argv[1]).read())
    rows, plan = build(adj)
    print("\n| DV, idx | J_adj (endpoint) | s_lo | C(s_lo) | s_hi | C(s_hi) | status |")
    print("|---|---|---|---|---|---|---|")
    for dv, idx, J, s_lo, s_hi, c_lo, c_hi, st in rows:
        if s_lo is None:
            print("| `%s` %d | `%.6e` | - | - | - | - | **%s** |" % (dv, idx, J, st))
        else:
            print("| `%s` %d | `%.6e` | %g | %.2f | %g | %.2f | %s |"
                  % (dv, idx, J, s_lo, c_lo, s_hi, c_hi, st))
    planned = sorted(set((p["dv"], p["idx"]) for p in plan))
    print("\nPLANNED_COMPONENTS %d of %d gradeable: %s" % (len(planned), N_GRADEABLE, planned))
    print("EXCLUDED_BY_NAME_IN_ADVANCE %s  (FD-ungradeable, NOT A RESULT)" % (EXCLUDED_BY_NAME,))
    print("PLAN_ENTRIES %d  PERTURBED_PRIMALS %d" % (len(plan), 2 * len(plan)))
    open(sys.argv[2], "w").write(json.dumps(plan, indent=1))
    print("WROTE %s" % sys.argv[2])
