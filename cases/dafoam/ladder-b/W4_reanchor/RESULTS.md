# W4-REANCHOR — RESULT: **`BLOCKED`**

**Dated 2026-09-06.** Item: `W4_reanchor` (the D12 FD-vs-adjoint bright-line re-anchor on the CBFS field-inversion case; the vehicle for S1_FD_PLATEAU). Regime: **INCOMPRESSIBLE** (`DASimpleFoam`, `runScript.py:67`). Supervisor: `dafoam-supervisor` (check-1 on the comparator diff and crash triage on the blocked leg discharged personally).

**Pre-registration:** `../W4_REANCHOR_PREREGISTRATION.md`, §14 FREEZE, §17 RE-FREEZE. **Grading path:** `analyse_w4_reanchor.py`, md5 `0172c7ad33b1725f4a554de0879614df` — **verified against the §17 pin in the grading invocation before the verdict was believed, and the two matched**; `freeze_check` confirmed disk == HEAD blob for all 7 frozen paths and every `STAGED_INSTRUMENTS` md5 registered OK.

**Run root:** `/home/ubuntu/certonomous-runs/W4-reanchor/`. Program complete 2026-09-06T21:38:58Z (16/16 legs `END rc=0` in `ledger.csv`).

**SUBMISSIONS PARKED.**

---

## 1. THE VERDICT, AS THE FROZEN COMPARATOR EMITTED IT

> ## ITEM TOKEN: **`BLOCKED`**

Exact command (from repo root, no bypass flag):
`python3 cases/dafoam/ladder-b/W4_reanchor/analyse_w4_reanchor.py --run-root /home/ubuntu/certonomous-runs/W4-reanchor` — exit 0, a graded verdict, **not** a refusal.

Reason verbatim: *"1 of 16 declared primals are not rule-4 complete (anchor8w). prereg 9.3: any blocked > 0 forces the arm's token to NOT A RESULT or BLOCKED. No success-reading token over a short program."*

**The FD-vs-adjoint bright line (the hypothesised D12 gap) is therefore NEITHER CONFIRMED NOR DENIED — it is UNTESTED, blocked on a single leg.**

---

## 2. THE GATES

| gate | question | measured | band | reading |
|---|---|---|---|---|
| **W1** | per-component adjoint↔FD move, bar ≤ 10% | cell 5491 **0.0387%**, cell 6740 **0.0000%**, cell 12486 **0.0007%** | ≤ 10% | all three **inside** |
| **F_W** | trivial baseline (cell 5491, h_F 0.75), predicted to FAIL W1 | predicted > 10% (19.12%); **measured 10.13%** | > 10% predicted | **fails W1 as PREDICTED** (prediction MET) |
| **W0** | base consistency: OBJ varianceU(anchor8w) == OBJ varianceU(base8w), 16 digits | **UNRESOLVED — CONTROL_NOT_PRODUCED** | 16-digit equality | anchor8w blocked → comparison cannot form |
| **W2** | tolerance readback, floor 1e-6 | tol 1e-08, diff 100, floor 1e-06, **unmoved 16/16** | inside floor | **inside** |

**PLANTED-ZERO CONTROL — FIRED and PASSED.** PLANT 1.234e-03 relative into the + leg of cell 6740 only, read back from a disk copy: cell 6740 moved 1.683e-06 → 3.788e-04 (observed delta == implied delta), cells 5491 and 12486 unchanged to the last digit. `PLANT SEEN. The comparator can report disagreement.` The reader is demonstrably able to see a non-zero (rule 3).

---

## 3. THE ONE BLOCKED LEG — CRASH TRIAGE (supervisor, personal): INFRASTRUCTURE, NOT A CAPABILITY GAP

**15/16 legs rule-4 COMPLETE. `anchor8w` is RAN-BUT-MISSED** (rc=0, last_time=2500, FAILED `fields_present` + `age_guard`).

Triage, from source:
- `anchor8w` and `base8w` ran identical 27-step primals and **both reached `Time = 2500`** (anchor log line 18579); `controlDict` `purgeWrite 0`, `writeInterval 500`, `endTime 2500`.
- `base8w` snapshot `fields_base8w/` = `0 500 1000 1500 2000 2500` (clean). `anchor8w` snapshot `fields_anchor8w/` = `0 0.0001 500 1000 1500 2000` — an extra `0.0001` dir and **missing the 2500 endTime dir**.
- `anchor8w` is the **only** leg that computes the ADJOINT (`compute_totals` with `-gradout anchor8w_grad.npy`). Sequence: primal writes 2500 → `End` → **the adjoint phase mutates the run dir (adds `0.0001`, drops `2500`)** → the driver `mv`s the *post-adjoint* dir into `fields_anchor8w/`.
- **Physics is fully present:** rc=0, primal to 2500, adjoint completed (`dRdWTPC 424/425`), gradient `anchor8w_grad.npy` (168128 B) written and valid.

**Conclusion: the adjoint-computing leg cannot double as the rule-4 endTime reference** — the adjoint mutates the time dirs after the primal's `End`. This is a driver-snapshot-timing defect, not a physics or OpenFOAM capability failure. The comparator was CORRECT to decline promoting `anchor8w` on rc=0 alone.

---

## 4. THE FIX (state (b), §2ay) — RE-RUN ONE LEG

Named fix: capture the anchor's clean primal endTime snapshot BEFORE the adjoint runs. Cleanest is to split the anchor into a pure-primal reference leg (produces the rule-4 snapshot in `fields_anchor8w/` and the W0 OBJ; deterministic beta=1 state) plus the existing gradient leg (writes `anchor8w_grad.npy`, which the comparator reads separately at `analyse_w4_reanchor.py:663-668`). The 15 FD legs, `base8w`, and the valid gradient are **not** re-run. Re-run cost ≈ **7.6 core-min** (primal only). The driver change is held to a **§2d.1 repair amendment** (four conditions analysed: the defect was found by rule-4's structural guard, independent of any graded number; no gate/threshold/cap/label moves) or to a surgical primal-only re-run under the unchanged frozen instruments — the provenance-honest path, ruling pending. Successor is dated and active; this is NOT a capability-gap filing.

**LESSON owed on fix:** a leg computing BOTH primal and adjoint mutates its time dirs after the primal's `End`; it cannot be the rule-4 endTime reference — snapshot pre-adjoint, or from a pure-primal twin.

---

## 5. COST — RULE 12

| field | value |
|---|---|
| unit | core-minutes = wall s × ranks ÷ 60 |
| **actual** | **132.330 core-min** (ledger.csv sum over all 16 END rows; comparator-confirmed at its `[10]` ACTUAL) |
| registered estimate | **133.23 core-min** (prereg §6 per-leg NEED table) |
| ratio actual/predicted | **0.9932** |
| cap | **150.0 core-min — respected**; no row over 3600 wall s (longest anchor8w 562 wall s) |
| dollars | **$0.1131 DERIVED** at $0.0513/core-h, reported-by-owner, NOT measured |

Calibration row filed: `docs/COST_CALIBRATION.md` (commit 2dbeda7a). Gap attribution: estimate precision, not waste or contention. The BLOCKED token is an infrastructure defect unrelated to cost and does not enter the ratio.

---

## 6. WHAT THIS DOES NOT CLAIM

It does not test the FD-vs-adjoint bright line (blocked on `anchor8w`), does not settle the D12 gap hypothesis, and quotes no gradient verdict over the arm. It establishes that 15/16 legs are rule-4 complete, W1/W2 are inside their bands on the produced legs, the trivial baseline fails as predicted, and the planted control can see a non-zero. The arm re-grades to a real verdict after the anchor re-run.
