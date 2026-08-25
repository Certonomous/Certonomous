# F12 attempt ledger — RAE 2822, AGARD AR-138 Case 9

One row per attempt at the case. **The gate is not an attempt.** Every row below
grades against the SAME frozen pre-registration,
`verification/campaign/F12_PREREGISTRATION.md`, blob
`080303c57aee52849bb625579565a84ca5469717`, v1.2, whose admission gate A, gate B,
Gates 1–4, thresholds, caps, labels and PASS rule are as frozen **2026-07-30** and
are **not touched by any row here**.

Earlier attempt trees are **preserved undeleted and unrenamed**. The builder of
each new attempt asserts the earlier trees still exist before it starts, and
asserts its own run root ABSENT by `test -e` in its own invocation.

---

## Attempt 1 — 2026-08-25 — `GATE FAIL` at admission gate A, all three levels

**Run root:** `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/` (rung 1,
fired) and `verification/runs/F12_runs/mesh_audit_2026-08-25/` (all three levels,
mesh only). **Both preserved.**

**Mesh instrument:** `sdk/workflows/rae2822_case9.py`, `blockmesh_dict` — an
O-grid of four quarter blocks around the section, corners at the leading edge,
both mid-chord points and the trailing edge, mapped onto a far-field circle of
radius 50 centred on the trailing edge.

**Measured, from three real `checkMesh` logs:**

| level | cells | max non-orthogonality | faces > 70° | max skewness | gate A |
| --- | --- | --- | --- | --- | --- |
| coarse | 23,040 | **70.64625857** | 892 | 0.8270270496 | `GATE FAIL` |
| medium | 92,160 | **70.86145203** | 3,598 | 0.8273655771 | `GATE FAIL` |
| fine | 368,640 | **72.54215374** | 14,399 | 0.8273339689 | `GATE FAIL` |

Artifact: `verification/runs/F12_runs/mesh_audit_2026-08-25/mesh_audit.json`.
The over-threshold face count scales ×4.03 then ×4.00 across a ladder that
quadruples the cell count — **a fixed FRACTION of the mesh, so refinement does
not cure it.** Rung 1's solver then diverged to negative temperature at
iteration 180; that is recorded in `verification/campaign/F12_RESULTS.md` and is
not re-litigated here.

## Attempt 2 — 2026-08-25 — new mesh instrument, same frozen gate

**Reason for the attempt, as stated by Sanaa on 2026-08-25 and quoted verbatim:**

> "original ladder inadmissible at all levels, worsening under refinement — mesh
> instrument replaced, gate unchanged."

**Run root:** `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/`,
registered by name and asserted ABSENT by `test -e` in the committing invocation
and again inside the builder.

**Mesh instrument:** `mesh_ladder_attempt2_2026-08-25/build_ladder_attempt2.py`,
registered in `ATTEMPT2_MESH_REGISTRATION.md` beside it. The frozen
pre-registration is **not edited**; `sdk/workflows/rae2822_case9.py` is **not
edited** and is imported read-only.

**What changed:** the mesh only. **What did not change:** gate A (≤ 70°, ≤ 4),
gate B, Gates 1–4 and their thresholds (0.08 / 0.04 / 0.020 chord / 5 % / 20 %),
the CM-reported-not-gated clause, the overall PASS rule, the caps
(120 / 160 / 700 / 160 / 160 = 1,300 core-min), the labels, the three cell counts
(23,040 / 92,160 / 368,640), the far-field radius, the wake length, the patch
names and their face assignment, the wall-normal first-cell anchoring
(2.0e-6 / 1.0e-6 / 5.0e-7 chord) and the y+ convention.

**Gate A result:** recorded in `mesh_ladder_attempt2_2026-08-25/RESULTS_GATE_A.md`
and `gate_a_attempt2.json`, from three real `checkMesh` logs.

### Attempt 2, rung 1 — fired 2026-08-25T17:06:57Z — `NOT A RESULT`

**Run directory:** `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/`
(registered by name in the pre-registration's LAUNCHER ADDENDUM §3 and asserted
ABSENT before launch). Record: `RESULTS_RUNG1.md` beside it.

| gate | outcome |
| --- | --- |
| admission gate A | **`PASS`** — 51.12365363°, skewness 0.9572299919 |
| admission gate B | **`GATE FAIL`** — no convergence statement; the run aborted |
| strict completion rule | **fails all six limbs**; `rc = 134` read from disk |
| Gates 1–4 | **`PENDING`** — no values exist and none is quoted |
| **overall** | **`NOT A RESULT`** |

**The finding: the same failure as attempt 1, on a mesh 19.5° better.**
`Negative initial temperature T0` at iteration **148** (attempt 1: **180**), on a
mesh whose max non-orthogonality fell 70.646° → 51.124°, average 30.213° →
17.375°, faces over 70° 892 → 0. **Removing the gate-A breach did not remove the
failure**, so `F12_RESULTS.md` §6.3's *"CONSISTENT BUT NOT DEMONSTRATED"* reading
of the breach as the cause is not sufficient. Crash triage is the supervisor's
and is not done here.

**The rate-calibration rung did its job anyway:** measured **3.8975e-6 s per
cell-iteration**, against Basis A's 4.7015e-6 (1.21×) and Basis B's 4.6010e-5
(**11.80×**). Cost **0.3007 core-min** of a frozen 120; cap not breached.
