#!/usr/bin/env python3
"""RC4 comparator -- the three planted controls, the strict completion clause,
and the gates P0 / P1 / P2 / P3.

Registration: cases/RANS_LES_closure_models/RC4_kaandorp_propagation_repair/
PREREGISTRATION.md -- section 4 (metrics, and BOTH continuity readings),
section 5 (the gates), section 5.1 (the verdict ladder), section 6 (the three
planted controls), section 6.1 (no ast.Assert), section 8 (strict completion)
and section 11 (this module's registered job and refusals).

ORDER OF OPERATIONS, as registered
----------------------------------
1. ALL THREE planted controls (section 6) run FIRST, on every scoring pass:
   direction A and direction B on a real `U` field written by simpleFoam on
   this box, and the `kDeficit` plant that proves the P1 comparator can see a
   difference in the one file this item changes;
2. every row through section 8's completion clause;
3. P-1 (rc4_extract_R.py), which section 5 says runs FIRST of the gates;
4. P1 (rc4_onechange.py), P0, P2;
5. one verdict from the fixed vocabulary (section 5.1).

CONTINUITY, BOTH READINGS, NEITHER HIDDEN (section 4)
------------------------------------------------------
The BINDING bar is the predecessor's H5, RMS `div(U)` / gradient scale < 1e-3,
carried forward unchanged so RC4's rows stay comparable to the rows they
succeed.  The sibling Wu chain's stricter 1e-4 is computed and REPORTED beside
every row as a second reading.  Section 8 clause 8: a row outside the
carried-forward 1e-3 bar is NOT CONVERGED whatever its `U_rms`.

P3 MADE EXECUTABLE
------------------
Section 5's P3 forbids quoting the two-channel (T-bR) ceiling when grading a
b-only model.  `ceiling_for()` is the only accessor: asked for a b-only model's
ceiling it returns the T-b number, and asked to hand the T-bR number to a
b-only model it REFUSES.  A publication rule with no instrument is a promise;
this one has a `sys.exit(2)`.

REGISTERED REFUSALS (section 11), every one a sys.exit(2), never an assert:
  * any plant direction failing,
  * any completion clause failing,
  * a continuity violation silently accepted.

The third is structural: `gate_arithmetic()` REFUSES if a row carrying
`continuity_ok = False` ever reaches it, so no code path accepts one quietly.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).  `--selftest` parses this file and requires zero.

NO RC2 MODULE IS IMPORTED, CALLED, EDITED OR EXTENDED (section 11).  RC4 takes
RC2's convergence labels as authoritative where they land (section 0) and never
recomputes them; the completion determinations here apply ONLY to RC4's own new
runs.

REUSE, SCOPED (L-512): `r4_lib.solve_complete` is reused UNMODIFIED with
`required=()` for section 8's clauses 1-3 only (rc = 0, the End line, and the
registered-termination clause with BOTH its branches).  Clauses 4, 5 and 6 are
here, because section 8's field list carries `kDeficit` and clause 6 dates every
field against `0/U` specifically.
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
import build_rc4_cases as B                                        # noqa: E402
import rc4_onechange as OC                                         # noqa: E402
import rc4_extract_R as EX                                         # noqa: E402

PLANT = 1.234e-03

# ---- section 5, the thresholds.  FIXED.  Never moved (sections 7, 10).
P0_CUT = 0.80                     # T-bR cuts U_rms by >= 80% vs N NULL
P2_BAND = (0.9, 1.1)              # k/k_LES on the T-bR row
MIN_CASES = 2
N_INSCOPE = 3
CONTINUITY_BINDING = 1e-3         # section 4: the predecessor's H5, carried forward
CONTINUITY_SECOND = 1e-4          # section 4: the Wu chain's stricter reading
PLANT_MIN_MOVE = 1e-12
LOG_NAME = "log.solve"

SEC_LES_PCT = {"AR_1_Ret_360": 1.508, "AR_3_Ret_360": 1.411}
X_REATT_LES = {"CBFS13700": 4.241}

REAL_U = "/home/ubuntu/closure-data/aposteriori/kaandorp/AR_1_Ret_360__TRUTHR/788/U"
REAL_ULES = ("/home/ubuntu/closure-challenge-benchmark/data/DUCT/"
             "AR_1_Ret_360/0/U_LES")


def refuse(msg):
    sys.stderr.write("RC4 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


# ------------------------------------------- section 6, the reader control
def u_rms(U, U_LES, uref):
    e = np.linalg.norm(np.asarray(U, float) - np.asarray(U_LES, float), axis=1)
    return float(np.sqrt((e ** 2).mean()) / uref)


def swap_internal_vector(src_path, dst_path, vals):
    s = open(src_path).read()
    if "internalField" not in s or "boundaryField" not in s:
        refuse("not an OpenFOAM field file: " + src_path)
    i, j = s.index("internalField"), s.index("boundaryField")
    a = np.asarray(vals, float).reshape(-1, 3)
    rows = "\n".join("(" + " ".join("%.17g" % c for c in r) + ")" for r in a)
    body = ("internalField   nonuniform List<vector>\n" + str(a.shape[0])
            + "\n(\n" + rows + "\n)\n;\n\n")
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    open(dst_path, "w").write(s[:i] + body + s[j:])


def plant_control_U(u_path, U_LES, uref, scratch, reader=read_field):
    """Section 6, directions A and B, on a field simpleFoam wrote on this box.

    Direction A: PLANT at cell 0 and cell n // 2, written to DISK, re-read
    through the SAME reader the scorer uses; `U_rms` must move by more than
    1e-12.  Direction B: the unmodified copy must give a BITWISE identical
    `U_rms`.  Either failing: sys.exit(2).  `reader` is injectable so the
    selftest can drive a blinded and a non-deterministic reader and show that
    each direction actually FIRES.
    """
    if not os.path.exists(u_path):
        refuse("planted control has no real field to work on: " + u_path)
    U0 = np.asarray(reader(u_path), float).reshape(-1, 3)
    U_LES = np.asarray(U_LES, float).reshape(-1, 3)
    if U0.shape != U_LES.shape:
        refuse("planted control: " + u_path + " has shape " + str(U0.shape)
               + " but U_LES has " + str(U_LES.shape))
    base = u_rms(U0, U_LES, uref)

    copy_b = os.path.join(scratch, "control_B", "U")
    os.makedirs(os.path.dirname(copy_b), exist_ok=True)
    shutil.copyfile(u_path, copy_b)
    rms_b = u_rms(np.asarray(reader(copy_b), float).reshape(-1, 3), U_LES, uref)
    if rms_b != base:
        refuse("section 6 direction B: the reader does NOT see a genuine zero "
               "as zero -- U_rms of an unmodified copy is %.17g against the "
               "original's %.17g; the reader is not deterministic and no zero "
               "it produces is evidence" % (rms_b, base))

    n = U0.shape[0]
    idx = sorted({0, n // 2})
    Up = U0.copy()
    Up[idx, 0] = Up[idx, 0] + PLANT
    copy_a = os.path.join(scratch, "control_A", "U")
    swap_internal_vector(u_path, copy_a, Up)
    Ua = np.asarray(reader(copy_a), float).reshape(-1, 3)
    rms_a = u_rms(Ua, U_LES, uref)
    move = abs(rms_a - base)
    if not (move > PLANT_MIN_MOVE):
        refuse("section 6 direction A: the reader CANNOT see the plant -- "
               "U_rms moved by %.3g, not more than the registered %.3g, after "
               "PLANT = %g was written into %d cells of %s.  A zero from this "
               "reader is not evidence" % (move, PLANT_MIN_MOVE, PLANT,
                                           len(idx), copy_a))
    amax = float(np.abs(Up).max())
    tol = max(1e-12, 8.0 * float(np.finfo(float).eps) * amax)
    recov = float(np.abs((Ua[idx, 0] - U0[idx, 0]) - PLANT).max())
    if recov > tol:
        refuse("section 6 direction A read-back: max|recovered - PLANT| = "
               "%.3g > tol %.3g (field max %.3g)" % (recov, tol, amax))
    print("[P4 direction A] U_rms %.17g -> %.17g, moved %.3g (> %.3g) : PASS"
          % (base, rms_a, move, PLANT_MIN_MOVE))
    print("[P4 direction B] U_rms of the unmodified copy %.17g, bitwise "
          "identical : PASS" % rms_b)
    return {"field": u_path, "n_cells": int(n), "plant": PLANT,
            "planted_cells": idx, "u_rms_base": base, "u_rms_planted": rms_a,
            "u_rms_move": float(move), "u_rms_unplanted_copy": rms_b,
            "readback_error": recov, "readback_tol": tol, "verdict": "PASS"}


def run_all_controls(u_path, U_LES, uref, scratch):
    """All three of section 6's controls, on every scoring pass."""
    a = plant_control_U(u_path, U_LES, uref, scratch)
    c = OC.plant_control_kdeficit()
    return {"U_plant": a, "kDeficit_plant": c,
            "all_passed": a["verdict"] == "PASS" and c["verdict"] == "PASS"}


# ------------------------------------------ section 8, strict completion
EXEC_RE = re.compile(r"^ExecutionTime = ", re.M)
TIME_RE = re.compile(r"^Time = ", re.M)


def completion(case, required_fields=B.REQUIRED_FIELDS):
    """Section 8, all eight clauses, as (ok, reason, info).

    Clauses 1-3 from the frozen r4_lib.solve_complete (required=()); clauses 4,
    5 and 6 here; clause 7 is the builder's; clause 8 is continuity, measured by
    score_row and enforced by gate_arithmetic.
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
    missing = [f for f in required_fields
               if not os.path.exists(os.path.join(tdir, f))]
    if missing:
        return False, ("clause 4: fields absent at " + lt + "/: "
                       + ", ".join(missing)
                       + " -- a T-bR row without kDeficit on disk did not run "
                       "the configuration it claims"), info
    log = os.path.join(case, LOG_NAME)
    if not os.path.exists(log):
        return False, "clause 5: no " + LOG_NAME + " in " + case, info
    txt = open(log, errors="replace").read()
    n_exec, n_time = len(EXEC_RE.findall(txt)), len(TIME_RE.findall(txt))
    info["n_execution_time"], info["n_time_steps"] = n_exec, n_time
    if n_exec != n_time:
        return False, ("clause 5: ExecutionTime lines %d != steps taken %d"
                       % (n_exec, n_time)), info
    zu = os.path.join(case, "0", "U")
    if not os.path.exists(zu):
        return False, "clause 6: 0/U absent, the age guard has no reference", info
    t0 = os.path.getmtime(zu)
    stale = [f for f in required_fields
             if os.path.getmtime(os.path.join(tdir, f)) <= t0]
    if stale:
        return False, ("clause 6 AGE GUARD: field(s) at " + lt + "/ not newer "
                       "than 0/U: " + ", ".join(stale)), info
    # Section 8's registered note: RC4's runs are built fresh under clause 7
    # and are NEVER resumed, so wall_s is a real measurement on every row.
    info["resumed"] = False
    return True, "complete (" + str(info.get("stop_state")) + ")", info


# ------------------------------------------------- section 4, the metrics
def score_row(tag, case, bench):
    d = bench
    C, n = d["C"], d["n"]
    lt = r4_lib.latest_time(case)
    if lt == "0":
        refuse("score_row: no non-zero time directory in " + case)
    td = os.path.join(case, lt)
    U = np.asarray(read_field(os.path.join(td, "U")), float).reshape(-1, 3)
    k = np.asarray(read_field(os.path.join(td, "k")), float).reshape(-1)
    nut = np.asarray(read_field(os.path.join(td, "nut")), float).reshape(-1)
    kd = np.asarray(read_field_expand(os.path.join(td, B.KDEFICIT), n),
                    float).reshape(-1)
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
    bd = read_field_expand(os.path.join(case, B.TIME0, "bijDelta"), n)
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
        "k_rms": float(np.sqrt(((k - kL) ** 2).mean()) / kref),
        "kDeficit_rms": float(np.sqrt((kd ** 2).mean())),
        "b_rms_total": float(np.sqrt(((b_tot[both] - bL[both]) ** 2)
                                     .sum(axis=(1, 2)).mean())),
        "unrealisable_frac": float(viol.mean()),
        "divU_rms_over_gradscale": div_over_grad,
        "continuity_binding_bar": CONTINUITY_BINDING,
        "continuity_second_bar": CONTINUITY_SECOND,
        "continuity_ok": bool(div_over_grad < CONTINUITY_BINDING),
        "continuity_inside_1e4": bool(div_over_grad <= CONTINUITY_SECOND),
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
        row["x_sep"], row["x_reatt"] = r["x_sep"], r["x_reatt"]
        row["x_reatt_LES"] = X_REATT_LES[tag]
    return row


# ------------------------------------------------ section 5, the gates
def cut(u_rms_row, u_rms_null):
    if u_rms_null is None or u_rms_null <= 0.0:
        refuse("cut(): a NULL U_rms of " + repr(u_rms_null)
               + " cannot be a denominator")
    return (u_rms_null - u_rms_row) / u_rms_null


def ceiling_for(model_kind, case, ceilings, use=None):
    """Section 5's P3, made executable.

    A b-only model is graded against the B-ONLY ceiling, which is the T-b row.
    Handing it the two-channel T-bR number is forbidden by this registration,
    so this refuses rather than returning it.
    """
    if model_kind not in ("b_only", "two_channel"):
        refuse("ceiling_for: unknown model kind " + repr(model_kind)
               + "; the registered kinds are 'b_only' and 'two_channel'")
    if model_kind == "b_only" and use in ("T-bR", "two_channel"):
        refuse("section 5 P3: reporting the T-bR (two-channel) ceiling as "
               "'the ceiling' for a b-only model is FORBIDDEN by this "
               "registration.  The TBRF supplies no R; a b-only model is "
               "graded against the b-only (T-b) ceiling, which is published "
               "beside the repaired one and never substituted for it")
    row = "T-b" if model_kind == "b_only" else "T-bR"
    if case not in ceilings or row not in ceilings[case]:
        refuse("ceiling_for: no measured " + row + " ceiling for " + str(case))
    return {"case": case, "model_kind": model_kind, "row": row,
            "ceiling_cut": ceilings[case][row],
            "channels": 1 if row == "T-b" else 2}


def gate_arithmetic(rows, p1_results):
    """P0, P2 and the published ceilings.  REFUSES if a row that failed
    completion or continuity ever reaches the gates."""
    out = {"per_case": {}, "P0_cases": [], "P2_cases": [], "ceilings": {},
           "blocked": []}
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
                       + repr(r.get("divU_rms_over_gradscale"))
                       + ", outside the carried-forward "
                       + repr(CONTINUITY_BINDING) + " bar; it is NOT "
                       "CONVERGED whatever its U_rms and a continuity "
                       "violation is never silently accepted")
        null = cfgs.get("N", {})
        if null.get("status") != "SCORED":
            out["blocked"].append(tag)
            out["per_case"][tag] = {"status": "BLOCKED",
                                    "reason": "N NULL not scored"}
            continue
        u0 = null["u_rms"]
        per = {"status": "SCORED", "u_rms_N": u0, "cuts": {}}
        for cfg in ("T-b", "T-bR"):
            r = cfgs.get(cfg, {})
            per["cuts"][cfg] = (cut(r["u_rms"], u0)
                                if r.get("status") == "SCORED" else None)
        out["ceilings"][tag] = dict(per["cuts"])
        tbr = cfgs.get("T-bR", {})
        per["P1"] = p1_results.get(tag)
        per["k_over_k_LES_TbR"] = tbr.get("k_over_k_LES")
        if per["cuts"]["T-bR"] is not None and per["cuts"]["T-bR"] >= P0_CUT:
            out["P0_cases"].append(tag)
            kk = tbr.get("k_over_k_LES")
            per["P2"] = (kk is not None and P2_BAND[0] <= kk <= P2_BAND[1])
            if per["P2"]:
                out["P2_cases"].append(tag)
        else:
            per["P2"] = None
        out["per_case"][tag] = per
    out["P0_hold"] = len(out["P0_cases"]) >= MIN_CASES
    out["P2_hold"] = (out["P0_hold"]
                      and all(out["per_case"][t]["P2"] for t in out["P0_cases"]))
    return out


def verdict(rows, controls_ok, p1_results, p_minus_1):
    """Section 5.1's ladder.  One label from the fixed vocabulary, only.

    Order: P4 (the controls), section 8 completion, section 8 clause 8
    continuity, P-1 (which section 5 says runs FIRST of the gates), P1, P0, P2.
    """
    vocab = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
             "PENDING")
    res = {"verdict": None, "reasons": []}

    if not controls_ok:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append("P4: a section 6 planted control failed")
        return _seal(res, vocab)

    scored = [(t, c, r) for t in sorted(rows) for c, r in sorted(rows[t].items())
              if r.get("status") == "SCORED"]
    incomplete = [t + "/" + c for t, c, r in scored if not r.get("complete", False)]
    if incomplete:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append("section 8 strict completion failed on: "
                              + ", ".join(incomplete))
        return _seal(res, vocab)
    notconv = [t + "/" + c for t, c, r in scored
               if not r.get("continuity_ok", False)]
    if notconv:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append(
            "section 8 clause 8: NOT CONVERGED outside the carried-forward "
            + repr(CONTINUITY_BINDING) + " continuity bar on: "
            + ", ".join(notconv))
        return _seal(res, vocab)

    res["P_minus_1"] = p_minus_1
    if p_minus_1.get("item_blocked", False):
        res["verdict"] = "BLOCKED"
        res["reasons"].append(
            "P-1: only " + str(p_minus_1.get("n_admitted"))
            + " of " + str(N_INSCOPE) + " in-scope cases survive the "
            "R-extraction validity gate.  RC4 as a whole is BLOCKED; the "
            "denominator is NOT rescaled and no PASS is reported on one case")
        return _seal(res, vocab)

    p1_failed = sorted(t for t, v in p1_results.items() if v is not True)
    if p1_failed:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append(
            "P1: more than one file differs between T-b and T-bR on "
            + ", ".join(p1_failed) + ".  The row is NOT A RESULT and is not "
            "re-scored as it stands; the case is rebuilt from the read-only "
            "benchmark clone and re-run ONCE, and a second P1 failure "
            "WITHDRAWS the item (section 7, second falsifier)")
        return _seal(res, vocab)

    g = gate_arithmetic(rows, p1_results)
    res["gates"] = g
    scorable = [t for t in sorted(rows)
                if g["per_case"].get(t, {}).get("status") == "SCORED"]
    if len(scorable) < MIN_CASES:
        res["verdict"] = "BLOCKED"
        res["reasons"].append(
            "only " + str(len(scorable)) + " of " + str(N_INSCOPE)
            + " in-scope cases could be scored (benchmark fields absent at run "
            "time); the denominator is NOT rescaled")
        return _seal(res, vocab)

    if not g["P0_hold"]:
        res["verdict"] = "GATE FAIL"
        res["reasons"].append(
            "P0 FAILS: supplying the frozen-RANS extracted R does NOT restore "
            "the ceiling -- T-bR cut U_rms by >= " + str(int(P0_CUT * 100))
            + "% relative to N NULL on only " + str(len(g["P0_cases"])) + " of "
            + str(N_INSCOPE) + " cases.  RC4's premise, that kDeficit == 0 is "
            "the propagation defect, is FALSIFIED and the item is WITHDRAWN as "
            "a propagation repair.  The 80% threshold is NOT lowered and no "
            "additional channel is added to reach it (section 7)")
        return _seal(res, vocab)

    if not g["P2_hold"]:
        res["verdict"] = "GATE REACHED"
        res["reasons"].append(
            "P0 and P1 hold, P2 FAILS: k/k_LES on the T-bR row is outside "
            + repr(P2_BAND) + " on at least one P0-passing case.  Propagation "
            "is repaired; the k-budget mechanism is NOT confirmed as the sole "
            "channel, and that is reported as the open question rather than "
            "smoothed over.  The band is NOT widened (section 10)")
        return _seal(res, vocab)

    res["verdict"] = "PASS"
    res["reasons"].append(
        "P-1 admits " + str(p_minus_1.get("n_admitted")) + " of "
        + str(N_INSCOPE) + " cases, P0 holds on " + str(len(g["P0_cases"]))
        + " (" + ", ".join(g["P0_cases"]) + "), P1 holds on every scored row, "
        "P2 holds on the P0-passing cases, P4 holds.  The propagation path is "
        "demonstrated repaired, the repair is attributable to kDeficit alone, "
        "and the named mechanism is confirmed.  P3: both ceilings are "
        "published side by side and the two-channel one never grades a b-only "
        "model")
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


def _fake_case(root, name, iters=100, converged=True, fields=None,
               exec_lines=None, rc="0", end=True, age_ok=True):
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
            lines.append("ExecutionTime = " + str(i * 0.1) + " s")
    if converged:
        lines.append("SIMPLE solution converged in " + str(iters) + " iterations")
    if end:
        lines.append("End")
    open(os.path.join(case, LOG_NAME), "w").write("\n".join(lines) + "\n")
    t0 = os.path.getmtime(os.path.join(case, "0", "U"))
    for f in fields:
        p = os.path.join(tdir, f)
        open(p, "w").write("0\n")
        dt = 60 if age_ok else -60
        os.utime(p, (t0 + dt, t0 + dt))
    return case


def _row(u, kk=1.0, complete=True, cont=True, status="SCORED"):
    return {"status": status, "u_rms": u, "k_over_k_LES": kk,
            "complete": complete, "continuity_ok": cont,
            "divU_rms_over_gradscale": 1e-6, "reason": "synthetic"}


def _table(tbr_cut, kk=1.0, cases=("AR_1_Ret_360", "AR_3_Ret_360",
                                   "CBFS13700")):
    out = {}
    for t in cases:
        u0 = 0.19874
        out[t] = {"N": _row(u0),
                  "T-b": _row(u0 * 1.618),          # the predecessor's +62%
                  "T-bR": _row(u0 * (1 - tbr_cut), kk)}
    return out


def _p1_all(ok=True, cases=("AR_1_Ret_360", "AR_3_Ret_360", "CBFS13700")):
    return {t: (True if ok else "two files differ") for t in cases}


def _pm1(n=3, blocked=False):
    return {"n_admitted": n, "item_blocked": blocked, "n_inscope": N_INSCOPE}


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    tmp = tempfile.mkdtemp(prefix="rc4_score_selftest_")
    try:
        if os.path.exists(REAL_U) and os.path.exists(REAL_ULES):
            UL = np.asarray(read_field(REAL_ULES), float).reshape(-1, 3)
            uref = float(np.mean(np.linalg.norm(UL, axis=1)))
            rec = plant_control_U(REAL_U, UL, uref, os.path.join(tmp, "c"))
            note("P4 U-plant PASSES on a real simpleFoam-written U field",
                 rec["verdict"] == "PASS",
                 "U_rms moved %.3g" % rec["u_rms_move"])
            note("P4 direction A FIRES against a BLINDED reader",
                 _fires(plant_control_U, REAL_U, UL, uref,
                        os.path.join(tmp, "cA"),
                        lambda p, _c=[None]: (_c.__setitem__(
                            0, _c[0] if _c[0] is not None
                            else read_field(REAL_U)) or _c[0])))

            def noisy(path, _state=[0]):
                a = np.asarray(read_field(path), float)
                _state[0] += 1
                return a + (1e-9 if _state[0] > 1 else 0.0)

            note("P4 direction B FIRES against a NON-DETERMINISTIC reader",
                 _fires(plant_control_U, REAL_U, UL, uref,
                        os.path.join(tmp, "cB"), noisy))
            note("P4 FIRES when the field it is pointed at does not exist",
                 _fires(plant_control_U, os.path.join(tmp, "nope"), UL, uref,
                        os.path.join(tmp, "cC")))
            all3 = run_all_controls(REAL_U, UL, uref, os.path.join(tmp, "c3"))
            note("all three section 6 controls run together and PASS",
                 all3["all_passed"])
        else:
            note("a real simpleFoam U field is on disk for P4", False, REAL_U)

        good = _fake_case(tmp, "good")
        okc, reason, info = completion(good)
        note("completion PASSES a synthetic complete case", okc, reason)
        note("clause 1 FIRES on rc != 0",
             not completion(_fake_case(tmp, "rc", rc="1"))[0])
        note("clause 2 FIRES on a missing End line",
             not completion(_fake_case(tmp, "noend", end=False))[0])
        c = _fake_case(tmp, "nostop", converged=False, iters=50)
        open(os.path.join(c, "system", "controlDict"), "w").write(
            "endTime         100;\n")
        note("clause 3 FIRES when the run neither converged nor reached endTime",
             not completion(c)[0])
        note("clause 4 FIRES on a missing kDeficit -- the field this item "
             "exists to change",
             not completion(_fake_case(
                 tmp, "nokd",
                 fields=[f for f in B.REQUIRED_FIELDS if f != B.KDEFICIT]))[0])
        note("clause 4 FIRES on a missing phi",
             not completion(_fake_case(
                 tmp, "nophi",
                 fields=[f for f in B.REQUIRED_FIELDS if f != "phi"]))[0])
        note("clause 5 FIRES on ExecutionTime lines != steps taken",
             not completion(_fake_case(tmp, "exec", exec_lines=80))[0])
        note("clause 6 AGE GUARD FIRES on a field older than 0/U",
             not completion(_fake_case(tmp, "age", age_ok=False))[0])
        note("completion FIRES on an absent case directory",
             not completion(os.path.join(tmp, "absent"))[0])

        note("cut() REFUSES a zero NULL denominator", _fires(cut, 0.1, 0.0))

        v = verdict(_table(0.983), True, _p1_all(True), _pm1(3))
        note("PASS when P-1 admits 3, P0 holds, P1 holds and k/k_LES is in band",
             v["verdict"] == "PASS", v["verdict"])
        note("both ceilings are published side by side",
             set(v["gates"]["ceilings"]["AR_1_Ret_360"]) == {"T-b", "T-bR"})

        v2 = verdict(_table(0.983, kk=0.201), True, _p1_all(True), _pm1(3))
        note("GATE REACHED when k/k_LES is outside [0.9, 1.1] -- the "
             "predecessor's measured 0.201",
             v2["verdict"] == "GATE REACHED", v2["verdict"])
        v3 = verdict(_table(0.40), True, _p1_all(True), _pm1(3))
        note("GATE FAIL when T-bR does not clear the 80% bar",
             v3["verdict"] == "GATE FAIL", v3["verdict"])
        v4 = verdict(_table(0.983), False, _p1_all(True), _pm1(3))
        note("NOT A RESULT when a section 6 control fails",
             v4["verdict"] == "NOT A RESULT")
        v5 = verdict(_table(0.983), True, _p1_all(False), _pm1(3))
        note("NOT A RESULT when P1 finds more than one change",
             v5["verdict"] == "NOT A RESULT")
        v6 = verdict(_table(0.983), True, _p1_all(True), _pm1(1, True))
        note("BLOCKED when fewer than 2 in-scope cases survive P-1",
             v6["verdict"] == "BLOCKED")
        t7 = _table(0.983)
        t7["CBFS13700"]["T-bR"]["complete"] = False
        note("NOT A RESULT when a scored row fails strict completion",
             verdict(t7, True, _p1_all(True), _pm1(3))["verdict"]
             == "NOT A RESULT")
        t8 = _table(0.983)
        t8["CBFS13700"]["T-bR"]["continuity_ok"] = False
        t8["CBFS13700"]["T-bR"]["divU_rms_over_gradscale"] = 0.3219275282624856
        note("NOT A RESULT on the measured CBFS13700__TRUTHR continuity of "
             "0.3219, which is outside BOTH bars",
             verdict(t8, True, _p1_all(True), _pm1(3))["verdict"]
             == "NOT A RESULT")
        note("gate_arithmetic REFUSES a continuity-violating row handed to it "
             "directly -- no silent acceptance path exists",
             _fires(gate_arithmetic, t8, _p1_all(True)))
        t9 = _table(0.983)
        t9["CBFS13700"]["T-b"]["complete"] = False
        note("gate_arithmetic REFUSES an incomplete row handed to it directly",
             _fires(gate_arithmetic, t9, _p1_all(True)))

        # ---- P3, made executable
        ceilings = {"AR_1_Ret_360": {"T-b": -0.618, "T-bR": 0.983}}
        note("P3: a b-only model is graded against the T-b (one-channel) "
             "ceiling",
             ceiling_for("b_only", "AR_1_Ret_360", ceilings)["row"] == "T-b")
        note("P3 REFUSES (sys.exit 2) when asked to quote the T-bR "
             "two-channel ceiling for a b-only model",
             _fires(ceiling_for, "b_only", "AR_1_Ret_360", ceilings, "T-bR"))
        note("P3 returns the two-channel ceiling for a two-channel model",
             ceiling_for("two_channel", "AR_1_Ret_360", ceilings)["channels"]
             == 2)
        note("P3 REFUSES an unknown model kind",
             _fires(ceiling_for, "whatever", "AR_1_Ret_360", ceilings))
        note("_seal REFUSES a label outside the fixed vocabulary",
             _fires(_seal, {"verdict": "mostly repaired"},
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
    print("rc4_score selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def score_all(root=B.ROOT, out_path=None):
    """The scoring pass.  Refuses while RC4 is DRAFT/UNFROZEN."""
    B.refuse_if_unfrozen()
    scratch = os.path.join(root, "_control")
    rows, p1_results, controls = {}, {}, None
    for tag in sorted(B.CASES):
        src, fam = B.CASES[tag]
        bench = SB.load_case(tag, src, fam)
        UL = np.asarray(bench["U_LES"], float).reshape(-1, 3)
        uref = float(np.mean(np.linalg.norm(UL, axis=1)))
        rows[tag] = {}
        for cfg in B.CONFIGS:
            case = os.path.join(root, tag, cfg)
            if not os.path.isdir(case):
                rows[tag][cfg] = {"status": "BLOCKED",
                                  "reason": "case directory absent: " + case}
                continue
            okc, reason, info = completion(case)
            if controls is None:
                lt = r4_lib.latest_time(case)
                controls = run_all_controls(os.path.join(case, lt, "U"), UL,
                                            uref, scratch)
            row = {"status": "SCORED", "complete": okc, "reason": reason,
                   "completion": info}
            if okc:
                row.update(score_row(tag, case, bench))
            else:
                row["continuity_ok"] = False
            rows[tag][cfg] = row
        tb = os.path.join(root, tag, "T-b")
        tbr = os.path.join(root, tag, "T-bR")
        if os.path.isdir(tb) and os.path.isdir(tbr):
            try:
                OC.compare(tb, tbr)
                p1_results[tag] = True
            except SystemExit:
                p1_results[tag] = "P1 comparison refused"
    if controls is None:
        refuse("no case directory carried a field for section 6's controls; a "
               "zero from an unexercised reader is not evidence")
    pm1 = EX.p1_gate(sorted(B.CASES))
    res = verdict(rows, controls["all_passed"], p1_results, pm1)
    res["controls"] = controls
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
    sys.stderr.write("usage: rc4_score.py --selftest | --score\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
