# D10-P′ — THE PLANT RE-BUY — RESULTS

## 1. Verdict

**`GATE REACHED`.** A thermal objective — `DAFunctionWallHeatFlux`, `addToAdjoint: True`
— **reaches the adjoint** on image
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`.

Pre-registration frozen `25c735ff`; grading path `d10p_grade.py` md5
`00949e6d8d5431c65a49f7add4f93f09`, verified against the HEAD blob before the launch.
**No amendment; no addendum; nothing was changed after the freeze.**

## 2. Gates, all five

| gate | verdict | measured |
|---|---|---|
| **G10-1** | `PASS` | `wallHeatFlux` constructed; `HFX` present, `status COMPLETE` |
| **G10-2** | `PASS` | `HFX_base = 2.8462869283e+03`, finite, above the `1.0e-12` floor |
| **G10-3a** | `PASS` | clean copy reproduces base to **`0.000e+00`** relative (tol `1.0e-12`) |
| **G10-3b** | `PASS` | **plant response `2.056667e-02` relative**, floor `1.0e-6` — `HFX_plant = 2.9048255628e+03` |
| **G10-4** | `PASS` | `max |d(HFX)/d(patchV)| = 1.9771502962e+02` over **2** components: `[1.9771502962e+02, −3.7575031648e+01]` |

The plant read-back is on disk: `plant/0/T` carries `uniform 354.384;`, `base/0/T` and
`clean/0/T` carry `uniform 353.15;`.

## 3. What this is worth, stated against D10

D10 and D10-P′ ran a **byte-identical case and a byte-identical run script**
(`d10p_run_script.py` md5 `1d04151dba68061fce2c34b35f9fcb4e` = D10's;
`d10p_case/0.orig/T` md5 `78f76f52d06624ad0d8e734558c37cb6` = D10's). **The only
difference in the world between a `NOT A RESULT` and this `GATE REACHED` is where the
plant sits** — initial field versus boundary condition. `HFX_base` is identical to
D10's `2846.286928273276`, which is the same fact from the other side: the solve never
changed, only the question asked of it.

A `2.06e-2` relative response to a `+1.234 K` change on a `353.15 K` wall (a `0.35 %`
boundary change) is the physically expected order for a near-wall heat flux.

## 4. What this does NOT establish

Reachability only. **Nothing** about the correctness, accuracy or sign of `HFX` or of
`d(HFX)/d(patchV)`; nothing about the U-bend mesh, CHT coupling, `DAHeatTransferFoam`,
wall-function sensitivity, or a two-objective front; nothing about D10 at its own scale.
**A correct plant-and-refuse is evidence about the gate it guards, never about the file.**

## 5. Cost

| | |
|---|---|
| predicted | **0.45 core-min** (itself measured, from D10's identical three stages) |
| actual gross | **0.4168 core-min** — `base` 0.1667 + `plant` 0.1167 + `clean` 0.1167, plus the mesh container |
| ratio | **0.926×** |
| cap | 5.0 core-min; **`0.083×` of cap**, guard never fired |
| derived | **$0.000356 DERIVED, NOT MEASURED**, $0.0513/core-h c7a.4xlarge, reported-by-owner |
| waste | **0.000 core-min** on this row; D10's 0.4167 is named separately and is not absorbed here |

Calibration row **C-69**.

## 6. What D10 proper now has

The Tier-4 D10 row's `PROBE FIRST` prerequisite is **discharged**: a thermal objective is
reachable in value **and in the adjoint** on the stock image. The row's own
pre-registration still owes everything else — the U-bend at scale, the three weightings,
the front-monotonicity check, and its own cost.

---

## AMENDMENT 1 — 2026-08-25 — THE FD TABLE §2 DEMANDS NOW EXISTS

**Version 1.0 → 1.1.**
**lines whose number changed above this section: 0.**

Appended at the foot; **nothing above is edited, struck or reinterpreted**, and **no gate,
threshold, cap or label in this file moves** (`CLAUDE.md` rule 6).

**This file's verdict — `GATE REACHED` — STANDS UNCHANGED.**

`PROBE_REPORT_D10_D11_D12.md` §7(b) flagged that §4's gradient
`max |d(HFX)/d(patchV)| = 1.9771502962e+02` entered this record with **no finite-difference
table beside it**, against `DAFOAM_CHARTER.md` §2's bright line, and declined to rule on
whether an explicit non-claim satisfies the clause. **The supervisor ruled that it does not.**

**That table has now been bought**, as arm **D10-F′**, pre-registration frozen at commit
`120dddd2` **before any container started**:

> **`PASS`.** Adjoint `1.9771502962421681e+02` against a central FD of
> `1.9771503832566850e+02` at `h = 1.000e-03` m/s — **`4.401007e-08` relative**, against a
> pre-registered PASS band of `5.0e-2`. Plateau demonstrated over **all six** registered
> steps; δ_repeat measured at **exactly `0.000000e+00`**.

**The record: `../curriculum_D10_probe_Fprime/RESULTS.md`.**

**D10-F′ re-ran `compute_totals` on this case with a three-delta derivative of this arm's own
run script and reproduced §2's gate G10-4 values BIT-FOR-BIT** — both adjoint components and
`HFX` — at a threshold of zero. **So the number in §2 above is not merely defended; it is
independently reproduced, and the FD table is a table about THIS gradient.**

**§4 of this file is unchanged and remains correct:** this arm established reachability, and
nothing else. **The correctness of `d(HFX)/d(patchV[0])` is now established by D10-F′, not by
this file**, and a reader wanting the gradient's verification must cite that record, not this
one. **The patched toolchain row remains UNBOUGHT there and is named as unbought.**

**NOT FILED. Nothing in this amendment was sent, uploaded, registered, posted or commented.**
