#!/usr/bin/env python3
"""RC3 C4 EXACT-STRESS outer fixed point -- section 3.1, made executable.

Registration: cases/RANS_LES_closure_models/RC3_wu_ceiling_gate_validation/
PREREGISTRATION.md section 3.1 (the method, the stopping rule and the abort),
section 5.1 (the contraction threshold), section 7 (the third falsifier) and
section 11 (this module's registered job and its one registered refusal).

THE REGISTERED METHOD, verbatim from section 3.1
------------------------------------------------
  "Because the solver recomputes `b_linear` from the current strain rate each
   iteration, `b^Delta` cannot be set once to reconstruct `b_LES`.  Registered
   method: an outer fixed-point loop.  At outer pass m, set
   `b^Delta_(m) = b_LES - b_linear(U_(m-1))` using `b_linear` read from the
   previous pass's converged field, with `k` frozen at `k_LES`, and re-solve."

  "N_outer = 5 passes maximum.  Contraction criterion:
   `||b^Delta_(m) - b^Delta_(m-1)||_2 / ||b^Delta_(m-1)||_2` must fall
   monotonically across passes 2..5 and reach <= 1e-2."

  "If it does not, the C4 row is NOT A RESULT, the fact is printed with all
   five ratios, and the ceiling is read from the best of C1-C3 with C4 recorded
   as unavailable.  N_outer is not raised, and no relaxation of the fixed point
   is introduced to reach it."

HOW "ALL FIVE RATIOS" AND "PASSES 2..5" ARE RECONCILED
------------------------------------------------------
A ratio needs a predecessor, so passes 1..5 alone would yield FOUR ratios, and
section 3.1 requires FIVE to be printed.  The reading that makes every
registered number consistent is the one section 3.1's own wording implies: the
"previous pass's converged field" for pass 1 is configuration C3, which is
exactly `b^Delta = b_LES - b_RANS` with `k` frozen at `k_LES` -- i.e. pass 0 of
this same iteration.  With `b^Delta_0` = C3's injected field there are five
ratios, r_1 .. r_5, for five outer passes; monotonicity is required over
r_2 .. r_5 as registered (r_1 is the first, largest step and is excluded); and
section 10's budget of "C4 x3, up to 5 outer passes ... budgeted at 5 x C3" is
exactly five solves.  This reading is stated here rather than chosen silently,
so the supervisor's section 3 check-1 can accept or strike it as a diff.

NOTHING IS LAUNCHED BY THIS MODULE.  `drive()` takes the solve step as an
INJECTED callable and refuses outright while the registration is DRAFT /
UNFROZEN, so no path through this file can start a solver by accident.

REGISTERED REFUSAL (section 11): `sys.exit(2)` on N_outer exceeded without
contraction.  It is a `refuse()`, never an `assert` (section 6.1 / L-332).
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (HERE, COMMON, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from of_read import read_field, sym_to_full, anisotropy      # noqa: E402
import sst_baseline_metrics as SB                            # noqa: E402
import r4_lib                                                # noqa: E402
import build_rc3_ladder as B                                 # noqa: E402

N_OUTER = 5                 # section 3.1, FIXED.  Never raised (section 7).
CONTRACTION_MAX = 1e-2      # section 5.1, FIXED.
SYM_IDX = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def refuse(msg):
    sys.stderr.write("RC3 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


def to6(b33):
    b = np.asarray(b33, float)
    return np.stack([b[:, i, j] for i, j in SYM_IDX], axis=1)


def b_les_full(tag):
    """b_LES as (N,3,3), from the shipped tauij_LES and k_LES."""
    src, fam = B.CASES[tag]
    d = SB.load_case(tag, src, fam)
    kL = np.asarray(d["k_LES"], float)
    bL, okL = anisotropy(sym_to_full(np.asarray(d["tau_LES"], float)), kL)
    return np.nan_to_num(bL, nan=0.0, posinf=0.0, neginf=0.0), okL, d


def next_bdelta(b_LES33, C, U, nut, k, k_floor):
    """b^Delta_(m) = b_LES - b_linear(U_(m-1)), as an (N,6) symmTensor.

    b_linear is `-(nu_t/k) S(U)` recomputed from the PREVIOUS pass's converged
    field, which is what the solver itself will recompute at the next pass.
    """
    bl, ok = B.b_linear_from_fields(C, U, nut, k, k_floor)
    bd = np.where(ok[:, None, None], np.asarray(b_LES33, float) - bl, 0.0)
    return to6(np.nan_to_num(bd, nan=0.0, posinf=0.0, neginf=0.0))


def ratios(fields):
    """The five contraction ratios, r_m = ||b_m - b_(m-1)|| / ||b_(m-1)||.

    `fields` is [b^Delta_0 (= C3's field), b^Delta_1, ... b^Delta_N].
    """
    fs = [np.asarray(f, float).reshape(-1) for f in fields]
    if len(fs) < 2:
        refuse("ratios() needs at least b^Delta_0 and b^Delta_1, got "
               + str(len(fs)) + " field(s)")
    out = []
    for m in range(1, len(fs)):
        den = float(np.linalg.norm(fs[m - 1]))
        if den == 0.0:
            refuse("ratios(): ||b^Delta_" + str(m - 1) + "|| is exactly zero; "
                   "a contraction ratio has no denominator")
        out.append(float(np.linalg.norm(fs[m] - fs[m - 1]) / den))
    return out


def contraction_verdict(rs):
    """Section 3.1's stopping rule.  PRINTS ALL FIVE RATIOS WHATEVER HAPPENS."""
    rs = [float(r) for r in rs]
    print("[C4 fixed point] contraction ratios, all %d passes:" % len(rs))
    for m, r in enumerate(rs, start=1):
        print("    r_%d = %.6g" % (m, r))
    monotone = all(rs[i] < rs[i - 1] for i in range(2, len(rs)))
    reached = len(rs) >= 2 and rs[-1] <= CONTRACTION_MAX
    contracted = bool(monotone and reached and len(rs) == N_OUTER)
    print("[C4 fixed point] monotone over passes 2..%d: %s ; final r_%d = %.6g "
          "<= %g: %s ; CONTRACTED: %s"
          % (len(rs), monotone, len(rs), rs[-1] if rs else float("nan"),
             CONTRACTION_MAX, reached, contracted))
    return {"ratios": rs, "monotone_2_to_end": bool(monotone),
            "final_ratio": rs[-1] if rs else None,
            "threshold": CONTRACTION_MAX, "n_passes": len(rs),
            "n_outer_registered": N_OUTER, "contracted": contracted}


def read_converged(case):
    """(C, U, nut, k) at the last written time of a converged C4 pass."""
    lt = r4_lib.latest_time(case)
    if lt == "0":
        refuse("read_converged: no non-zero time directory in " + case)
    td = os.path.join(case, lt)
    for f in ("U", "nut", "k"):
        if not os.path.exists(os.path.join(td, f)):
            refuse("read_converged: " + f + " absent at " + td)
    U = np.asarray(read_field(os.path.join(td, "U")), float).reshape(-1, 3)
    nut = np.asarray(read_field(os.path.join(td, "nut")), float).reshape(-1)
    k = np.asarray(read_field(os.path.join(td, "k")), float).reshape(-1)
    return U, nut, k


def drive(tag, solve, b0, C, k_floor, out_dir=None, check_freeze=True):
    """Run the registered outer loop.  `solve(bdelta6, m) -> case_dir`.

    The solve step is INJECTED: this module never starts a solver itself.  The
    loop runs exactly N_OUTER passes -- section 3.1 requires the ratios over
    passes 2..N_OUTER to be judged, so it cannot stop early -- and refuses if
    the sequence does not contract.
    """
    if check_freeze:
        B.refuse_if_unfrozen()
    bles, _ok, _d = b_les_full(tag)
    fields = [np.asarray(b0, float).reshape(-1, 6)]
    cases = []
    for m in range(1, N_OUTER + 1):
        case = solve(fields[-1], m)
        cases.append(case)
        U, nut, k = read_converged(case)
        fields.append(next_bdelta(bles, C, U, nut, k, k_floor))
    rs = ratios(fields)
    rec = contraction_verdict(rs)
    rec.update({"tag": tag, "cases": cases,
                "n_cells": int(fields[0].shape[0])})
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        json.dump(rec, open(os.path.join(out_dir, "fixedpoint.json"), "w"),
                  indent=1, default=str)
    if not rec["contracted"]:
        refuse("section 3.1 abort: the C4 fixed point did not contract on "
               + tag + " within the registered N_outer = " + str(N_OUTER)
               + " passes (ratios " + ", ".join("%.6g" % r for r in rs)
               + ").  The C4 row is NOT A RESULT and C4 is recorded as "
               "unavailable; N_outer is NOT raised and no relaxation is "
               "introduced to reach it")
    return rec


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


def _seq(rs, n=64):
    """Synthetic b^Delta fields whose successive relative steps are exactly rs."""
    base = np.ones((n, 6))
    fields = [base.copy()]
    for r in rs:
        prev = fields[-1]
        step = np.zeros_like(prev)
        step[:, 0] = 1.0
        step = step / np.linalg.norm(step) * (r * np.linalg.norm(prev))
        fields.append(prev + step)
    return fields


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    want = [0.5, 0.2, 0.08, 0.03, 0.009]
    got = ratios(_seq(want))
    note("ratios reproduces a constructed relative-step sequence",
         max(abs(a - b) for a, b in zip(got, want)) < 1e-12,
         "max err %.3g" % max(abs(a - b) for a, b in zip(got, want)))
    note("ratios produces exactly five values for five outer passes",
         len(got) == N_OUTER)
    note("ratios REFUSES a single field", _fires(ratios, [np.ones((4, 6))]))
    note("ratios REFUSES a zero denominator",
         _fires(ratios, [np.zeros((4, 6)), np.ones((4, 6))]))

    v = contraction_verdict(want)
    note("CONTRACTED on a monotone sequence reaching <= 1e-2", v["contracted"])
    v2 = contraction_verdict([0.5, 0.2, 0.25, 0.03, 0.009])
    note("NOT contracted when the sequence is not monotone over passes 2..5",
         not v2["contracted"])
    v3 = contraction_verdict([0.5, 0.4, 0.3, 0.2, 0.1])
    note("NOT contracted when the final ratio never reaches 1e-2",
         not v3["contracted"])
    v4 = contraction_verdict([0.5, 0.2, 0.08, 0.03, CONTRACTION_MAX])
    note("CONTRACTED at exactly the registered 1e-2 bar", v4["contracted"])
    v5 = contraction_verdict([0.5, 0.2, 0.005])
    note("NOT contracted on fewer than the registered five passes",
         not v5["contracted"])

    tmp = tempfile.mkdtemp(prefix="rc3_fp_selftest_")
    try:
        n = 64
        C = np.stack([np.repeat(np.linspace(0, 1, 8), 8),
                      np.tile(np.linspace(0, 1, 8), 8), np.zeros(n)], axis=1)
        bles = np.zeros((n, 3, 3))
        bles[:, 0, 1] = 0.2
        bles[:, 1, 0] = 0.2
        U = np.stack([C[:, 1] * 2.0, np.zeros(n), np.zeros(n)], axis=1)
        nut = np.full(n, 0.02)
        k = np.full(n, 0.5)
        bd = next_bdelta(bles, C, U, nut, k, 1e-6)
        bl, _ = B.b_linear_from_fields(C, U, nut, k, 1e-6)
        note("next_bdelta = b_LES - b_linear(U) to machine precision",
             float(np.abs(bd - to6(bles - bl)).max()) < 1e-14)

        # A driver whose injected solve reproduces a chosen ratio sequence.
        def make_solve(seq):
            state = {"i": 0}

            def solve(bdelta6, m):
                case = os.path.join(tmp, "pass_%d_%d" % (id(seq) % 1000, m))
                td = os.path.join(case, "10")
                os.makedirs(td, exist_ok=True)
                os.makedirs(os.path.join(case, "0"), exist_ok=True)
                open(os.path.join(td, "U"), "w").write("0\n")
                state["i"] += 1
                return case
            return solve

        # `drive` needs real field reads, so it is exercised through a stub
        # `read_converged`/`next_bdelta` pair rather than fake OpenFOAM files.
        seq = [0.5, 0.2, 0.08, 0.03, 0.009]
        fields = _seq(seq)
        saved_rc, saved_nb, saved_bl = (read_converged, next_bdelta, b_les_full)
        g = globals()
        g["read_converged"] = lambda case: (np.zeros((n, 3)), np.zeros(n),
                                            np.ones(n))
        g["b_les_full"] = lambda tag: (np.zeros((n, 3, 3)), np.ones(n, bool), {})
        step = {"m": 0}

        def fake_next(b_LES33, C_, U_, nut_, k_, kf):
            step["m"] += 1
            return fields[step["m"]]
        g["next_bdelta"] = fake_next
        try:
            rec = drive("AR_1_Ret_360", make_solve(seq), fields[0], C, 1e-6,
                        out_dir=os.path.join(tmp, "out"), check_freeze=False)
            note("drive CONTRACTS on a converging injected sequence",
                 rec["contracted"], "final %.4g" % rec["final_ratio"])
            note("drive writes fixedpoint.json for the scorer to read",
                 os.path.exists(os.path.join(tmp, "out", "fixedpoint.json")))
            step["m"] = 0
            bad = _seq([0.5, 0.4, 0.45, 0.4, 0.4])
            fields[:] = bad
            note("drive REFUSES (sys.exit 2) when N_outer is exhausted without "
                 "contraction -- N_outer is not raised",
                 _fires(drive, "AR_1_Ret_360", make_solve(bad), bad[0], C,
                        1e-6, os.path.join(tmp, "out2"), False))
            note("the failed run STILL wrote all five ratios to disk",
                 os.path.exists(os.path.join(tmp, "out2", "fixedpoint.json"))
                 and len(json.load(open(os.path.join(tmp, "out2",
                                                     "fixedpoint.json")))
                         ["ratios"]) == N_OUTER)
            step["m"] = 0
            fields[:] = _seq(seq)
            note("drive REFUSES while the registration is DRAFT/UNFROZEN",
                 _fires(drive, "AR_1_Ret_360", make_solve(seq), fields[0], C,
                        1e-6, None, True))
        finally:
            g["read_converged"] = saved_rc
            g["next_bdelta"] = saved_nb
            g["b_les_full"] = saved_bl

        note("read_converged REFUSES a case with no non-zero time directory",
             _fires(read_converged, tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n2) for n2, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad = [n2 for n2, p, _ in ok if not p]
    if bad:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad) + "\n")
        raise SystemExit(1)
    print("rc3_fixedpoint selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    sys.stderr.write(
        "rc3_fixedpoint.py drives registered solves and therefore refuses "
        "while RC3 is DRAFT/UNFROZEN.  Run --selftest to exercise the "
        "instrument.\n")
    B.refuse_if_unfrozen()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
