#!/usr/bin/env python3
"""RC3 ceiling-gate comparator -- the two-direction reader control, the strict
completion clause, and the V0 / V1a / V1b / V2 gates.

Registration: cases/RANS_LES_closure_models/RC3_wu_ceiling_gate_validation/
PREREGISTRATION.md -- section 4 (metrics), section 5 (gates and thresholds),
section 5.2 (the verdict ladder), section 6 (the planted-zero control), section
6.1 (no ast.Assert), section 8 (strict completion) and section 11 (this
module's registered job and refusals).

ORDER OF OPERATIONS, as registered
----------------------------------
1. the two-direction planted control (section 6) runs FIRST, on a real field
   written by simpleFoam on this box, on EVERY scoring pass -- "a control that
   runs only in the test harness certifies the test harness";
2. every row is put through the strict-completion clause (section 8);
3. the rows are scored (section 4);
4. V0, then V1a and V1b, then V2 (section 5);
5. one verdict from the fixed vocabulary (section 5.2).

REGISTERED REFUSALS (section 11), every one a sys.exit(2), never an assert:
  * either plant direction failing,
  * any strict-completion clause failing,
  * a continuity violation being silently accepted.

The third is made structural rather than promissory: a row that fails section
4's continuity criterion is carried with `continuity_ok = False`, and
`gate_arithmetic()` REFUSES if such a row ever reaches it.  There is no code
path by which a continuity violation can enter a gate quietly.

WHY THE PLANT BAR IS ABSOLUTE HERE AND THAT IS NOT L-508
---------------------------------------------------------
Section 5.1 registers direction A as "recomputed `U_rms` must move by > 1e-12".
That is a FLOOR to exceed, not a ceiling to fall under, so the L-508 hazard --
an absolute 1e-15 read-back tolerance false-refusing on O(1)+ data -- does not
bite: a bigger field makes the measured move bigger, not smaller.  Where this
module chooses a tolerance of its own (the read-back of the planted copy) the
bar IS plant-relative: machine epsilon at the field's own largest magnitude,
floored at 1e-12.  The real fields here are O(1e2) (the duct `U` is ~108 m/s),
which is exactly the regime L-508 was paid for.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).  `--selftest` parses this file with `ast` and requires zero.

REUSE, SCOPED (L-512)
---------------------
`r4_lib.solve_complete` (R4_sparta_build/r4_lib.py:494) is reused UNMODIFIED,
called with `required=()` so that only the clauses it actually shares with
section 8 are taken from it: clause 1 (rc = 0), clause 2 (the End line) and
clause 3 (termination registered -- it carries BOTH branches, the
residualControl convergence line and the endTime backstop).  Its own field loop
is deliberately not used, because section 8's clause 4 has a different field
list and clause 6 dates every field against `0/U` specifically rather than
against each field's own `0/` copy; those two clauses, plus clause 5's
ExecutionTime accounting and clause 8's continuity, are implemented here.  The
helper is neither edited nor reimplemented, and its new use is exercised in
both directions by `--selftest`.
"""
from __future__ import annotations

import ast
import json
import os
import re
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

from of_read import (read_field, read_field_expand, sym_to_full,   # noqa: E402
                     anisotropy, realisability_violation, plane_axes,
                     structured_gradient, structured_shape)
import sst_baseline_metrics as SB                                  # noqa: E402
import r4_lib                                                      # noqa: E402
import build_rc3_ladder as B                                       # noqa: E402

PREREG = B.PREREG
PLANT = 1.234e-03                    # the lab's established comparator constant

# ---- section 5.1, the thresholds.  FIXED.  Never moved (sections 7, 9).
CEILING_CUT = 0.80                   # V0 / V1: "cuts U_rms by >= 80% vs NULL"
MIN_CASES = 2                        # "on >= 2 of the 3 in-scope cases"
N_INSCOPE = 3
CONTINUITY_MAX = 1e-4                # section 4, carried verbatim
PLANT_MIN_MOVE = 1e-12               # section 5.1, V3 plant
FALSIFIED_BARS = (0.30, 0.50)        # section 5's V2: the predecessors' bars

# The DNS / LES references section 4 registers.
SEC_LES_PCT = {"AR_1_Ret_360": 1.508, "AR_3_Ret_360": 1.411}
X_REATT_LES = {"CBFS13700": 4.241}

# The log and rc filenames this campaign writes, matching the frozen helper
# r4_lib.solve_complete that reads clauses 1-3 out of them.
LOG_NAME = "log.solve"


def refuse(msg):
    sys.stderr.write("RC3 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


# ------------------------------------------- section 6, the reader control
def u_rms(U, U_LES, uref):
    e = np.linalg.norm(np.asarray(U, float) - np.asarray(U_LES, float), axis=1)
    return float(np.sqrt((e ** 2).mean()) / uref)


def swap_internal_vector(src_path, dst_path, vals):
    """Write a copy of an OpenFOAM vector field with a new internalField.

    The header and the whole boundaryField block are carried over byte for
    byte, so the copy differs from the original in exactly the values planted.
    Re-implemented here: the predecessor's version lives in a file section 1.5
    forbids this item to touch (Kaandorp2020_TBRF/aposteriori/frozen_R.py:32).
    """
    s = open(src_path).read()
    if "internalField" not in s or "boundaryField" not in s:
        refuse("not an OpenFOAM field file: " + src_path)
    i = s.index("internalField")
    j = s.index("boundaryField")
    a = np.asarray(vals, float).reshape(-1, 3)
    rows = "\n".join("(" + " ".join("%.17g" % c for c in r) + ")" for r in a)
    body = ("internalField   nonuniform List<vector>\n" + str(a.shape[0])
            + "\n(\n" + rows + "\n)\n;\n\n")
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    open(dst_path, "w").write(s[:i] + body + s[j:])


def plant_control(u_path, U_LES, uref, scratch, reader=read_field):
    """Section 6, BOTH directions, on a field simpleFoam wrote on this box.

    Direction A -- can the reader SEE a non-zero?  PLANT is added at cell index
    0 and cell index n // 2, the copy is written to DISK, and it is re-read
    through the SAME reader the scorer uses.  The recomputed `U_rms` must move
    by more than 1e-12 (section 5.1).  Otherwise: sys.exit(2).

    Direction B -- does the reader see a genuine zero AS zero?  The unmodified
    copy is re-read through the same reader; the recomputed `U_rms` must be
    BITWISE identical to the original's.  Otherwise: sys.exit(2).

    `reader` is injectable so `--selftest` can drive a blinded reader and a
    noisy reader and show that each direction actually FIRES.
    """
    if not os.path.exists(u_path):
        refuse("planted control has no real field to work on: " + u_path)
    U0 = np.asarray(reader(u_path), float).reshape(-1, 3)
    U_LES = np.asarray(U_LES, float).reshape(-1, 3)
    if U0.shape != U_LES.shape:
        refuse("planted control: field " + u_path + " has shape "
               + str(U0.shape) + " but U_LES has " + str(U_LES.shape))
    base = u_rms(U0, U_LES, uref)

    # Direction B first: an unmodified copy, byte for byte.
    copy_b = os.path.join(scratch, "control_B", os.path.basename(u_path))
    os.makedirs(os.path.dirname(copy_b), exist_ok=True)
    shutil.copyfile(u_path, copy_b)
    Ub = np.asarray(reader(copy_b), float).reshape(-1, 3)
    rms_b = u_rms(Ub, U_LES, uref)
    if rms_b != base:
        refuse("section 6 direction B: the reader does NOT see a genuine zero "
               "as zero -- U_rms of an unmodified copy is %.17g against the "
               "original's %.17g (difference %.3g); the reader is not "
               "deterministic and no zero it produces is evidence"
               % (rms_b, base, rms_b - base))

    # Direction A: PLANT at cell 0 and cell n // 2, written to disk.
    n = U0.shape[0]
    idx = sorted({0, n // 2})
    Up = U0.copy()
    Up[idx, 0] = Up[idx, 0] + PLANT
    copy_a = os.path.join(scratch, "control_A", os.path.basename(u_path))
    swap_internal_vector(u_path, copy_a, Up)
    Ua = np.asarray(reader(copy_a), float).reshape(-1, 3)
    rms_a = u_rms(Ua, U_LES, uref)
    move = abs(rms_a - base)
    if not (move > PLANT_MIN_MOVE):
        refuse("section 6 direction A: the reader CANNOT see the plant -- "
               "U_rms moved by %.3g, which is not more than the registered "
               "%.3g, after PLANT = %g was written into %d cells of %s.  A "
               "zero from this reader is not evidence"
               % (move, PLANT_MIN_MOVE, PLANT, len(idx), copy_a))

    # A stronger, plant-RELATIVE read-back of the planted values themselves
    # (L-508: never an absolute 1e-15 bar on O(1)+ data).  Reported either way;
    # it refuses only if the planted cells did not survive the round trip.
    amax = float(np.abs(Up).max())
    tol = max(1e-12, 8.0 * float(np.finfo(float).eps) * amax)
    recov = np.abs((Ua[idx, 0] - U0[idx, 0]) - PLANT).max() if len(idx) else 0.0
    if float(recov) > tol:
        refuse("section 6 direction A read-back: the planted value did not "
               "survive the round trip -- max|recovered - PLANT| = %.3g > "
               "tol %.3g (field max %.3g)" % (float(recov), tol, amax))

    print("[V3 planted-zero control] field=%s n=%d PLANT=%g at cells %s"
          % (u_path, n, PLANT, idx))
    print("[V3 direction A] U_rms %.17g -> %.17g, moved %.3g (> %.3g) : PASS"
          % (base, rms_a, move, PLANT_MIN_MOVE))
    print("[V3 direction B] U_rms of the unmodified copy %.17g, bitwise "
          "identical : PASS" % rms_b)
    return {"field": u_path, "n_cells": int(n), "plant": PLANT,
            "planted_cells": idx, "u_rms_base": base, "u_rms_planted": rms_a,
            "u_rms_move": float(move), "min_move": PLANT_MIN_MOVE,
            "u_rms_unplanted_copy": rms_b, "bitwise_identical": True,
            "readback_error": float(recov), "readback_tol": float(tol),
            "verdict": "PASS"}


# ------------------------------------------ section 8, strict completion
EXEC_RE = re.compile(r"^ExecutionTime = ", re.M)
TIME_RE = re.compile(r"^Time = ", re.M)


def completion(case, required_fields=B.REQUIRED_FIELDS):
    """Section 8, all eight clauses, as a (ok, reason, info) triple.

    Clauses 1, 2 and 3 come from the frozen helper r4_lib.solve_complete,
    called with `required=()` (see the module docstring).  Clauses 4, 5 and 6
    are here.  Clause 7 is the builder's (build_rc3_ladder.guard_no_existing_times).
    Clause 8 is continuity, measured by `score_row` and enforced by
    `gate_arithmetic`.
    """
    info = {}
    if not os.path.isdir(case):
        return False, "clause 0: case directory absent: " + case, info
    ok, reason, sub = r4_lib.solve_complete(case, required=())
    info.update(sub)
    if not ok:
        return False, "clauses 1-3 (r4_lib.solve_complete): " + reason, info
    lt = r4_lib.latest_time(case)
    info["latest_time"] = lt
    if lt == "0":
        return False, "clause 3: no non-zero time directory in " + case, info
    tdir = os.path.join(case, lt)

    # clause 4: fields present at the last written time
    missing = [f for f in required_fields
               if not os.path.exists(os.path.join(tdir, f))]
    if missing:
        return False, ("clause 4: fields absent at " + lt + "/: "
                       + ", ".join(missing)), info

    # clause 5: ExecutionTime count == the number of steps the log reports
    log = os.path.join(case, LOG_NAME)
    if not os.path.exists(log):
        return False, "clause 5: no " + LOG_NAME + " in " + case, info
    txt = open(log, errors="replace").read()
    n_exec = len(EXEC_RE.findall(txt))
    n_time = len(TIME_RE.findall(txt))
    info["n_execution_time"] = n_exec
    info["n_time_steps"] = n_time
    if n_exec != n_time:
        return False, ("clause 5: ExecutionTime lines %d != steps taken %d"
                       % (n_exec, n_time)), info

    # clause 6: THE AGE GUARD.  Every field at the last written time must be
    # NEWER than the case's own 0/U, which the builder touches last.
    zu = os.path.join(case, "0", "U")
    if not os.path.exists(zu):
        return False, "clause 6: 0/U absent, the age guard has no reference", info
    t0 = os.path.getmtime(zu)
    info["age_reference_mtime"] = t0
    stale = [f for f in required_fields
             if os.path.getmtime(os.path.join(tdir, f)) <= t0]
    if stale:
        return False, ("clause 6 AGE GUARD: field(s) at " + lt + "/ not newer "
                       "than 0/U: " + ", ".join(stale)
                       + " -- they came from somewhere else"), info
    return True, "complete (" + str(info.get("stop_state")) + ")", info


# ------------------------------------------------- section 4, the metrics
def score_row(tag, case, bench):
    """Section 4's metrics for one configuration directory."""
    d = bench
    C, n = d["C"], d["n"]
    lt = r4_lib.latest_time(case)
    if lt == "0":
        refuse("score_row: no non-zero time directory in " + case)
    td = os.path.join(case, lt)
    U = np.asarray(read_field(os.path.join(td, "U")), float).reshape(-1, 3)
    k = np.asarray(read_field(os.path.join(td, "k")), float).reshape(-1)
    nut = np.asarray(read_field(os.path.join(td, "nut")), float).reshape(-1)
    UL = np.asarray(d["U_LES"], float).reshape(-1, 3)
    kL = np.asarray(d["k_LES"], float).reshape(-1)
    uref = float(np.mean(np.linalg.norm(UL, axis=1)))
    e = np.linalg.norm(U - UL, axis=1)
    A = structured_gradient(C, U)
    S = 0.5 * (A + A.transpose(0, 2, 1))
    divU = np.einsum("nii->n", A)
    gscale = float(np.sqrt((A ** 2).sum(axis=(1, 2)).mean()))
    kref = float(np.mean(np.abs(kL)))
    tau = ((2.0 / 3.0) * k)[:, None, None] * np.eye(3)[None] \
        - 2.0 * nut[:, None, None] * S
    bd = read_field_expand(os.path.join(case, "0", "bijDelta"), n)
    tau = tau + 2.0 * k[:, None, None] * sym_to_full(np.asarray(bd, float))
    b_tot, okb = anisotropy(tau, k, k_ref=kref)
    bL, okL = anisotropy(sym_to_full(np.asarray(d["tau_LES"], float)), kL)
    both = okb & okL & np.isfinite(b_tot).all(axis=(1, 2))
    viol, _ = realisability_violation(np.nan_to_num(b_tot[both]), tol=1e-6)
    div_over_grad = float(np.sqrt((divU ** 2).mean()) / gscale)
    row = {
        "time": lt, "n_cells": int(n),
        "u_rms": float(np.sqrt((e ** 2).mean()) / uref),
        "u_mae": float(e.mean() / uref),
        "k_mean": float(k.mean()),
        "k_over_k_base": float(k.mean() / float(np.asarray(d["k"], float).mean())),
        "k_over_k_LES": float(k.mean() / kref),
        "b_rms_vs_LES": float(np.sqrt(((b_tot[both] - bL[both]) ** 2)
                                      .sum(axis=(1, 2)).mean())),
        "unrealisable_frac": float(viol.mean()),
        "divU_rms_over_gradscale": div_over_grad,
        "continuity_ok": bool(div_over_grad <= CONTINUITY_MAX),
        "continuity_bar": CONTINUITY_MAX,
    }
    keep, thin = plane_axes(C)
    if tag in SEC_LES_PCT:
        ip = np.delete(U, thin, axis=1)
        ub = float(np.abs(U[:, thin]).mean())
        row["inplane_pct_bulk"] = float(np.mean(np.linalg.norm(ip, axis=1))
                                        / ub * 100.0)
        row["inplane_pct_bulk_DNS"] = SEC_LES_PCT[tag]
    if tag in X_REATT_LES:
        ns, nf = structured_shape(C)
        r = SB._longest_reversed_run(C[:nf, keep[0]], U[:nf, keep[0]])
        row["x_sep"] = r["x_sep"]
        row["x_reatt"] = r["x_reatt"]
        row["x_reatt_LES"] = X_REATT_LES[tag]
    return row


# ------------------------------------------------ section 5, the gates
def cut(u_rms_row, u_rms_null):
    """The fraction by which a row cuts U_rms relative to C0 NULL."""
    if u_rms_null is None or u_rms_null <= 0.0:
        refuse("cut(): a NULL U_rms of " + repr(u_rms_null)
               + " cannot be a denominator")
    return (u_rms_null - u_rms_row) / u_rms_null


def criterion(cut_value):
    """The CANDIDATE ceiling criterion under validation (section 5, V1):
    'the ceiling row for a case is the row that cuts U_rms by >= 80% relative
    to NULL'.  Returns 'PASS' or 'FAIL' -- and nothing else, ever."""
    return "PASS" if cut_value >= CEILING_CUT else "FAIL"


def gate_arithmetic(rows):
    """Turn the scored rows into V0 / V1a / V1b / V2 readings.

    REFUSES (section 11) if a row that failed section 4's continuity criterion
    or section 8's completion clause is handed to it: a continuity violation
    cannot be silently accepted, because there is no path here that accepts one.
    """
    out = {"per_case": {}, "V0_cases": [], "V1b_cases": [], "blocked": []}
    for tag in sorted(rows):
        cfgs = rows[tag]
        for cfg, r in sorted(cfgs.items()):
            if r.get("status") != "SCORED":
                continue
            if not r.get("complete", False):
                refuse("gate_arithmetic: row " + tag + "/" + cfg + " reached "
                       "the gates without passing section 8: "
                       + str(r.get("reason")))
            if not r.get("continuity_ok", False):
                refuse("gate_arithmetic: row " + tag + "/" + cfg + " reached "
                       "the gates with divU_rms_over_gradscale = "
                       + repr(r.get("divU_rms_over_gradscale")) + " > "
                       + repr(CONTINUITY_MAX) + "; it is NOT CONVERGED and a "
                       "continuity violation is never silently accepted")
        null = cfgs.get("C0", {})
        if null.get("status") != "SCORED":
            out["blocked"].append(tag)
            out["per_case"][tag] = {"status": "BLOCKED",
                                    "reason": "C0 NULL not scored"}
            continue
        u0 = null["u_rms"]
        per = {"status": "SCORED", "u_rms_C0": u0, "cuts": {}, "criterion": {}}
        for cfg in ("C1", "C2", "C3", "C4", "CX"):
            r = cfgs.get(cfg, {})
            if r.get("status") != "SCORED":
                per["cuts"][cfg] = None
                per["criterion"][cfg] = None
                continue
            c = cut(r["u_rms"], u0)
            per["cuts"][cfg] = c
            per["criterion"][cfg] = criterion(c)
        # V2: the b-only ceiling is max(cut over C1, C2, C3), configuration named
        bonly = [(per["cuts"][c], c) for c in ("C1", "C2", "C3")
                 if per["cuts"][c] is not None]
        if bonly:
            best = max(bonly)
            per["b_only_ceiling_cut"] = best[0]
            per["b_only_ceiling_config"] = best[1]
            per["bars_falsified_by_measurement"] = [
                bar for bar in FALSIFIED_BARS if best[0] < bar]
        out["per_case"][tag] = per
        if per["criterion"].get("C4") == "PASS":
            out["V0_cases"].append(tag)
            if per["criterion"].get("CX") == "FAIL":
                out["V1b_cases"].append(tag)
    out["V0_hold"] = len(out["V0_cases"]) >= MIN_CASES
    out["V1a_hold"] = out["V0_hold"]          # definitional: same rows, same criterion
    out["V1b_hold"] = len(out["V1b_cases"]) >= MIN_CASES
    return out


def verdict(rows, plant_ok, fixedpoint):
    """Section 5.2's ladder.  One label from the fixed vocabulary, and only
    from it.  `fixedpoint` maps case -> bool (did C4's outer loop contract)."""
    vocab = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
             "PENDING")
    res = {"verdict": None, "reasons": []}

    if not plant_ok:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append("V3: the section 6 reader control failed")
        return _seal(res, vocab)

    incomplete = [t + "/" + c for t in sorted(rows) for c, r in sorted(rows[t].items())
                  if r.get("status") == "SCORED" and not r.get("complete", False)]
    if incomplete:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append("section 8 strict completion failed on: "
                              + ", ".join(incomplete))
        return _seal(res, vocab)
    notconv = [t + "/" + c for t in sorted(rows) for c, r in sorted(rows[t].items())
               if r.get("status") == "SCORED" and not r.get("continuity_ok", False)]
    if notconv:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append("section 8 clause 8 (continuity) NOT CONVERGED "
                              "on: " + ", ".join(notconv))
        return _seal(res, vocab)

    contracted = [t for t in sorted(fixedpoint) if fixedpoint[t]]
    res["c4_fixed_point_contracted"] = contracted
    if len(contracted) < MIN_CASES:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append(
            "section 7 third falsifier: C4's fixed point contracted on only "
            + str(len(contracted)) + " of " + str(N_INSCOPE)
            + " cases, so there is no reference to validate against; N_outer "
            "is NOT raised above 5")
        return _seal(res, vocab)

    g = gate_arithmetic(rows)
    res["gates"] = g
    scorable = [t for t in sorted(rows)
                if g["per_case"].get(t, {}).get("status") == "SCORED"]
    if len(scorable) < MIN_CASES:
        res["verdict"] = "BLOCKED"
        res["reasons"].append(
            "only " + str(len(scorable)) + " of " + str(N_INSCOPE)
            + " in-scope cases could be scored (benchmark fields absent at run "
            "time); the denominator is NOT rescaled (section 9)")
        return _seal(res, vocab)

    if not g["V0_hold"]:
        res["verdict"] = "GATE FAIL"
        res["reasons"].append(
            "V0 FAILS: the exact LES Reynolds stress cut U_rms by >= "
            + str(int(CEILING_CUT * 100)) + "% relative to NULL on only "
            + str(len(g["V0_cases"])) + " of " + str(N_INSCOPE)
            + " cases.  The apparatus cannot express the correct answer; the "
            "ceiling gate is not repairable by re-registration.  The 80% "
            "threshold is NOT lowered (section 7)")
        return _seal(res, vocab)

    if not g["V1b_hold"]:
        res["verdict"] = "GATE REACHED"
        res["reasons"].append(
            "V0 and V1a hold, V1b FAILS: the criterion also ADMITS the "
            "SCRAMBLED-truth row on " + str(len(g["V0_cases"])
                                             - len(g["V1b_cases"]))
            + " of the " + str(len(g["V0_cases"]))
            + " V0 cases.  A gate that passes a structureless tensor passes "
            "anything; the criterion form is WITHDRAWN, not re-tuned "
            "(section 7, second falsifier), and the apparatus finding stands "
            "alone")
        return _seal(res, vocab)

    res["verdict"] = "PASS"
    res["reasons"].append(
        "V0 holds, V1a and V1b hold on the same " + str(len(g["V1b_cases"]))
        + " of " + str(N_INSCOPE) + " cases (" + ", ".join(g["V1b_cases"])
        + "), V3 holds.  The ceiling criterion is a VALIDATED INSTRUMENT: it "
        "admits the exact-stress reference and rejects the scrambled-truth "
        "planted negative on the same cases")
    return _seal(res, vocab)


def _seal(res, vocab):
    if res["verdict"] not in vocab:
        refuse("verdict '" + str(res["verdict"]) + "' is not in the fixed "
               "vocabulary " + str(vocab))
    return res


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


REAL_U = "/home/ubuntu/closure-data/aposteriori/kaandorp/AR_1_Ret_360__TRUTHR/788/U"
REAL_ULES = ("/home/ubuntu/closure-challenge-benchmark/data/DUCT/"
             "AR_1_Ret_360/0/U_LES")


def _fake_case(root, name, iters=100, converged=True, fields=None,
               exec_lines=None, rc="0", end=True, age_ok=True):
    """A synthetic OpenFOAM case directory, complete by section 8 unless a
    clause is deliberately broken by the caller."""
    fields = list(fields if fields is not None else B.REQUIRED_FIELDS)
    case = os.path.join(root, name)
    os.makedirs(os.path.join(case, "0"))
    os.makedirs(os.path.join(case, "system"))
    tdir = os.path.join(case, str(iters))
    os.makedirs(tdir)
    for f in B.REQUIRED_FIELDS:
        open(os.path.join(case, "0", f), "w").write("0\n")
    open(os.path.join(case, "system", "controlDict"), "w").write(
        "endTime         " + str(iters) + ";\n")
    open(os.path.join(case, "rc"), "w").write(rc + "\n")
    n_exec = iters if exec_lines is None else exec_lines
    lines = []
    for i in range(1, iters + 1):
        lines.append("Time = " + str(i))
        if i <= n_exec:
            lines.append("ExecutionTime = " + str(i * 0.1) + " s  ClockTime = 1 s")
    if converged:
        lines.append("SIMPLE solution converged in " + str(iters) + " iterations")
    if end:
        lines.append("End")
    open(os.path.join(case, LOG_NAME), "w").write("\n".join(lines) + "\n")
    t0 = os.path.getmtime(os.path.join(case, "0", "U"))
    for f in fields:
        p = os.path.join(tdir, f)
        open(p, "w").write("0\n")
        os.utime(p, (t0 + (60 if age_ok else -60), t0 + (60 if age_ok else -60)))
    return case


def _row(u, complete=True, cont=True, status="SCORED"):
    return {"status": status, "u_rms": u, "complete": complete,
            "continuity_ok": cont, "divU_rms_over_gradscale": 1e-6,
            "reason": "synthetic"}


def _table(c4_cut, cx_cut, cases=("AR_1_Ret_360", "AR_3_Ret_360", "CBFS13700")):
    """A synthetic score table with a chosen C4 cut and CX cut on every case."""
    out = {}
    for t in cases:
        u0 = 0.20
        out[t] = {"C0": _row(u0),
                  "C1": _row(u0 * (1 - 0.10)),
                  "C2": _row(u0 * (1 - 0.15)),
                  "C3": _row(u0 * (1 - 0.29)),
                  "C4": _row(u0 * (1 - c4_cut)),
                  "CX": _row(u0 * (1 - cx_cut))}
    return out


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    tmp = tempfile.mkdtemp(prefix="rc3_ceiling_selftest_")
    try:
        # ---- 1. the section 6 control, on a REAL simpleFoam field, both
        #         directions, and BOTH directions shown to FIRE.
        if os.path.exists(REAL_U) and os.path.exists(REAL_ULES):
            UL = np.asarray(read_field(REAL_ULES), float).reshape(-1, 3)
            uref = float(np.mean(np.linalg.norm(UL, axis=1)))
            rec = plant_control(REAL_U, UL, uref, os.path.join(tmp, "ctl"))
            note("V3 control PASSES on a real simpleFoam-written U field",
                 rec["verdict"] == "PASS",
                 "U_rms moved %.3g" % rec["u_rms_move"])
            note("V3 direction A FIRES against a BLINDED reader (returns the "
                 "original whatever path it is given)",
                 _fires(plant_control, REAL_U, UL, uref,
                        os.path.join(tmp, "ctlA"),
                        lambda p, _c=[None]: (_c.__setitem__(0, _c[0] if _c[0]
                                              is not None else read_field(REAL_U))
                                              or _c[0])))

            def noisy(path, _state=[0]):
                a = np.asarray(read_field(path), float)
                _state[0] += 1
                return a + (1e-9 if _state[0] > 1 else 0.0)

            note("V3 direction B FIRES against a NON-DETERMINISTIC reader",
                 _fires(plant_control, REAL_U, UL, uref,
                        os.path.join(tmp, "ctlB"), noisy))
            note("V3 FIRES when the field it is pointed at does not exist",
                 _fires(plant_control, os.path.join(tmp, "nope"), UL, uref,
                        os.path.join(tmp, "ctlC")))
        else:
            note("V3 control has a real simpleFoam field to work on", False,
                 "absent: " + REAL_U)

        # ---- 2. section 8, each clause shown to FIRE on its own violation.
        good = _fake_case(tmp, "good")
        okc, reason, info = completion(good)
        note("completion PASSES a synthetic complete case", okc, reason)
        c = _fake_case(tmp, "bad_rc", rc="137")
        note("clause 1 FIRES on rc != 0", not completion(c)[0])
        c = _fake_case(tmp, "bad_end", end=False)
        note("clause 2 FIRES on a missing End line", not completion(c)[0])
        c = _fake_case(tmp, "bad_stop", converged=False, iters=50)
        open(os.path.join(c, "system", "controlDict"), "w").write(
            "endTime         100;\n")
        note("clause 3 FIRES when the run neither converged nor reached endTime",
             not completion(c)[0])
        c = _fake_case(tmp, "bad_fields",
                       fields=[f for f in B.REQUIRED_FIELDS if f != "phi"])
        note("clause 4 FIRES on a missing field (phi)", not completion(c)[0])
        c = _fake_case(tmp, "bad_exec", exec_lines=90)
        note("clause 5 FIRES on ExecutionTime lines != steps taken",
             not completion(c)[0])
        c = _fake_case(tmp, "bad_age", age_ok=False)
        note("clause 6 AGE GUARD FIRES on a field older than 0/U",
             not completion(c)[0])
        c = _fake_case(tmp, "bad_zero")
        os.remove(os.path.join(c, "0", "U"))
        note("clause 6 FIRES when 0/U is absent (no age reference)",
             not completion(c)[0])
        note("completion FIRES on an absent case directory",
             not completion(os.path.join(tmp, "absent"))[0])

        # ---- 3. the gate arithmetic and the verdict ladder.
        note("criterion ADMITS a row at exactly the 80% bar",
             criterion(0.80) == "PASS")
        note("criterion REJECTS a row at 79.9%", criterion(0.799) == "FAIL")
        note("cut() REFUSES a zero NULL denominator", _fires(cut, 0.1, 0.0))

        v = verdict(_table(c4_cut=0.90, cx_cut=0.05), True,
                    {t: True for t in ("AR_1_Ret_360", "AR_3_Ret_360",
                                       "CBFS13700")})
        note("PASS when C4 is admitted and CX is rejected on all three",
             v["verdict"] == "PASS", v["verdict"])
        note("V2 publishes the b-only ceiling with its configuration named",
             v["gates"]["per_case"]["AR_1_Ret_360"]["b_only_ceiling_config"] == "C3")
        note("V2 records the predecessors' 30% and 50% bars as FALSIFIED BY "
             "MEASUREMENT where the measured ceiling falls below them",
             v["gates"]["per_case"]["AR_1_Ret_360"]
             ["bars_falsified_by_measurement"] == [0.30, 0.50],
             "measured ceiling cut %.3f"
             % v["gates"]["per_case"]["AR_1_Ret_360"]["b_only_ceiling_cut"])

        # THE REJECTING LIMB, shown rejecting: CX admitted -> GATE REACHED.
        v2 = verdict(_table(c4_cut=0.90, cx_cut=0.90), True,
                     {t: True for t in ("AR_1_Ret_360", "AR_3_Ret_360",
                                        "CBFS13700")})
        note("GATE REACHED when the criterion ALSO admits SCRAMBLED (V1b's "
             "rejecting limb is what fails, and it is what fires)",
             v2["verdict"] == "GATE REACHED", v2["verdict"])
        note("V1b is the limb that failed, not V0/V1a",
             v2["gates"]["V0_hold"] and not v2["gates"]["V1b_hold"])

        v3 = verdict(_table(c4_cut=0.50, cx_cut=0.05), True,
                     {t: True for t in ("AR_1_Ret_360", "AR_3_Ret_360",
                                        "CBFS13700")})
        note("GATE FAIL when the exact stress does not clear 80%",
             v3["verdict"] == "GATE FAIL", v3["verdict"])

        v4 = verdict(_table(c4_cut=0.90, cx_cut=0.05), False,
                     {t: True for t in ("AR_1_Ret_360",)})
        note("NOT A RESULT when the V3 reader control fails",
             v4["verdict"] == "NOT A RESULT")

        t5 = _table(c4_cut=0.90, cx_cut=0.05)
        t5["CBFS13700"]["C4"]["complete"] = False
        v5 = verdict(t5, True, {t: True for t in ("AR_1_Ret_360",
                                                  "AR_3_Ret_360", "CBFS13700")})
        note("NOT A RESULT when any scored row fails strict completion",
             v5["verdict"] == "NOT A RESULT")

        t6 = _table(c4_cut=0.90, cx_cut=0.05)
        t6["CBFS13700"]["C1"]["continuity_ok"] = False
        t6["CBFS13700"]["C1"]["divU_rms_over_gradscale"] = 3.2e-1
        v6 = verdict(t6, True, {t: True for t in ("AR_1_Ret_360",
                                                  "AR_3_Ret_360", "CBFS13700")})
        note("NOT A RESULT when a row violates the 1e-4 continuity criterion",
             v6["verdict"] == "NOT A RESULT")
        note("gate_arithmetic REFUSES (sys.exit 2) if a continuity-violating "
             "row is handed to it directly -- no silent acceptance path exists",
             _fires(gate_arithmetic, t6))
        t7 = _table(c4_cut=0.90, cx_cut=0.05)
        t7["CBFS13700"]["C2"]["complete"] = False
        note("gate_arithmetic REFUSES an incomplete row handed to it directly",
             _fires(gate_arithmetic, t7))

        v8 = verdict(_table(c4_cut=0.90, cx_cut=0.05), True,
                     {"AR_1_Ret_360": True, "AR_3_Ret_360": False,
                      "CBFS13700": False})
        note("NOT A RESULT when C4's fixed point contracts on fewer than 2 of 3",
             v8["verdict"] == "NOT A RESULT")

        t9 = _table(c4_cut=0.90, cx_cut=0.05)
        for t in ("AR_3_Ret_360", "CBFS13700"):
            t9[t]["C0"]["status"] = "BLOCKED"
        v9 = verdict(t9, True, {t: True for t in ("AR_1_Ret_360",
                                                  "AR_3_Ret_360", "CBFS13700")})
        note("BLOCKED when fewer than 2 in-scope cases can be scored, and the "
             "denominator is not rescaled", v9["verdict"] == "BLOCKED")

        note("_seal REFUSES a label outside the fixed vocabulary",
             _fires(_seal, {"verdict": "roughly converged"},
                    ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
                     "BLOCKED", "PENDING")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad = [n for n, p, _ in ok if not p]
    if bad:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad) + "\n")
        raise SystemExit(1)
    print("rc3_ceiling selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def score_all(root=B.ROOT, out_path=None):
    """The scoring pass.  Refuses while RC3 is DRAFT/UNFROZEN."""
    B.refuse_if_unfrozen()
    scratch = os.path.join(root, "_control")
    rows, fixedpoint, plant = {}, {}, None
    for tag in sorted(B.CASES):
        src, fam = B.CASES[tag]
        bench = SB.load_case(tag, src, fam)
        UL = np.asarray(bench["U_LES"], float).reshape(-1, 3)
        uref = float(np.mean(np.linalg.norm(UL, axis=1)))
        rows[tag] = {}
        for cfg in ("C0", "C1", "C2", "C3", "C4", "CX"):
            case = os.path.join(root, tag, cfg)
            if not os.path.isdir(case):
                rows[tag][cfg] = {"status": "BLOCKED",
                                  "reason": "case directory absent: " + case}
                continue
            okc, reason, info = completion(case)
            if plant is None:
                lt = r4_lib.latest_time(case)
                plant = plant_control(os.path.join(case, lt, "U"), UL, uref,
                                      scratch)
            row = {"status": "SCORED", "complete": okc, "reason": reason,
                   "completion": info}
            if okc:
                row.update(score_row(tag, case, bench))
            else:
                row["continuity_ok"] = False
            rows[tag][cfg] = row
        fp = os.path.join(root, tag, "C4", "fixedpoint.json")
        fixedpoint[tag] = (json.load(open(fp)).get("contracted", False)
                           if os.path.exists(fp) else False)
    if plant is None:
        refuse("no case directory carried a field for the section 6 control; "
               "a zero from an unexercised reader is not evidence")
    res = verdict(rows, plant.get("verdict") == "PASS", fixedpoint)
    res["plant_control"] = plant
    res["rows"] = rows
    print("VERDICT: " + res["verdict"])
    for r in res["reasons"]:
        print("  " + r)
    if out_path:
        json.dump(res, open(out_path, "w"), indent=1, default=str)
    if res["verdict"] == "NOT A RESULT":
        raise SystemExit(2)
    return res


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--score" in argv:
        score_all()
        return 0
    sys.stderr.write("usage: rc3_ceiling.py --selftest | --score\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
