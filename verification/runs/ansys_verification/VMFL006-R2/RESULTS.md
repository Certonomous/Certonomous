# VMFL006-R2 — RESULTS — Multicomponent Species Transport in Pipe Flow

**Verdict: `PASS`.** Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27–28.
Graded 2026-08-31 by `ansys-lane-opus48` (Opus 4.8). This record lives in the RUN ROOT
(`verification/runs/ansys_verification/VMFL006-R2/`) per FILING_CHARTER and this team's
standing ruling. Verdict read from the machine-readable grading record
`GRADING_VMFL006.json`, **never from stdout**.

**A note on the JSON filename, stated honestly:** the frozen comparator writes
`GRADING_VMFL006.json` (its `main()` was carried over from R1 with that literal), not
`GRADING_VMFL006_R2.json`. The frozen bytes are not edited to rename it (CLAUDE.md rule 6);
the file in this run root is `GRADING_VMFL006.json` and that is the authoritative grading
record for VMFL006-R2. sha256/blob of the JSON: `90535fae6b86e0b0db131d0c5ccc79336cedbca7`
(git hash-object; untracked run artifact).

**R2 SUCCEEDS R1 (register row #49, `NOT A RESULT`).** R1's frozen files are untouched and
its row stands. R2 is a new registration; the register row is #50, citing #49.

---

## 1. The verdict and the gate

| | |
|---|---|
| **Verdict** | **`PASS`** |
| Gate | \|θ_lab − REF_LAB\| / \|REF_LAB\| ≤ TOL = 0.01, every one of ten stations, at L3 |
| Worst station deviation (THE GATE) | **0.096545 % at x = 0.10 m** — inside the 1 % band, **10.4× margin** |
| GCI ceiling | fine-grid GCI = **0.009607 %** ≤ GCI_MAX = 1.0000 % |
| Roache triple @ x = 0.10 m | coarse/med/fine = 0.354896103 / 0.354983201 / 0.355020182; **state CONVERGING**; observed order **p = 1.2359**; GCI_fine (Fs = 1.25) = 9.607×10⁻⁵ = **0.009607 %**; Richardson extrapolated 0.3550474672 |
| rc_unknown | False (all three RUN_RC.txt present, rc 0) |
| Verdict ceiling | **PASS** (§14: analytical reference — the exact solution of the same continuum model — declared triple returning CONVERGING; graded by CLAUDE.md rule 5 step 3) |

**Why PASS is a credential here.** With equal densities and viscosities and no reaction the
species equation reduces exactly to div(ρuY) = div(ρD·grad Y), which is what
`scalarTransportFoam` solves, so REF_LAB is the exact solution of the identical continuum
model and the only difference from the lab field is discretisation error — bounded by the
CONVERGING triple's GCI (0.0096 %, well inside the band). ANSYS_VERIFICATION_CHARTER §11.1:
§2f.3's CONTINUUM cap is the NO-TRIPLE ceiling and does not reach a declared triple returning
CONVERGING; §11.1 limit 3 caps an EXPERIMENTAL reference, and this reference is ANALYTICAL.

## 2. THE REGISTERED PREDICTION, RESOLVED BY MEASUREMENT — it held

R2's one substantive change was a convergence clause satisfiable from "converged to machine
precision and flat" to "still descending at endTime", coupled with endTime 3000 → 8000. The
registration **predicted all three levels would reach a flat plateau ≤ RES_FLOOR = 1×10⁻⁹**.
Measured on the real run (from `GRADING_VMFL006.json`, convergence per level):

| Level | n_iters | window max (T resid) | peak over run | log10 range | flat_at_floor | ≤ RES_FLOOR? |
|---|---|---|---|---|---|---|
| L1 | 8000 | 8.874×10⁻¹⁵ | 1.0 | 0.0 | True | ✅ |
| L2 | 8000 | 9.989×10⁻¹⁵ | 1.0 | 0.0 | True | ✅ |
| L3 | 8000 | **9.938×10⁻¹⁵** | 1.0 | 0.0 | True | ✅ |

**The prediction held exactly.** All three levels descended from O(1) to a bit-exact flat
plateau at the machine floor (log10 range 0.0). **L3 — which at endTime = 3000 in R1 sat at
6.18×10⁻⁸, still descending, and tripped R1's floor limb — now reaches 9.938×10⁻¹⁵**, the
direct consequence of the endTime raise. And the exactly-flat plateau (log10 range 0.0) is
precisely the case R1's null-range refusal wrongly killed at L1/L2; R2's clause reads it as
CONVERGED. The clause that was jointly unsatisfiable in R1 grades all three levels CONVERGED.

## 3. Controls fired (each on the graded path)

- **Planted-zero AT EVERY LEVEL** (rule 3), and this is the first registration of this team
  where a refusal cannot cost the plant — the plant now fires BEFORE any completion/
  convergence clause that can refuse. Result per level: L1/L2/L3 each planted 1.234×10⁻³,
  production reader moved by exactly 1.234×10⁻³, passed=True. This closes the L1-only weakness
  rows #44, #46 and VMFL006 R1 carry.
- **Strict completion (rule 4)** at every level: rc 0; one `^End`; last time == endTime == 8000;
  **anchored `^Time = ` count == 8000 == endTime** (the registered clause-5 equivalent, since
  `scalarTransportFoam` emits zero `ExecutionTime` lines — confirmed 0 at every level); exactly
  two numeric time dirs [0, 8000]; T/U/phi present; age guard (endTime fields newer than 0/T);
  birth certificate mesh_ok with cells == NX·NR.
- **Convergence satisfiability control** passed (7 synthetic cases each landing the intended
  verdict); **AST no-assert guard** clean; **cross-instrument reference reproduction** within
  REF_REPRO_TOL; **conservation/orientation** (sum φ vs flat-wedge flux) within FLUX_REL_TOL at
  every station; **numeric time-dir selection** with cardinality refusal
  (lexicographic_would_have_misread_any = False).
- **Selftest** 55/55, 0 fail, rc 0 under `python3` and `python3 -O`, stdout byte-identical.
  **Mutation** 24/24 (incl. the two new convergence mutations G/H).

## 4. Per-station mixing-cup θ at L3 (the gate) with corroboration

| x (m) | lab θ (L3) | REF_LAB (EXACT, the GATE) | rel dev (GATE) | manual 4dp (corroboration only) |
|---|---|---|---|---|
| 0.01 | 0.822643449 | 0.822181458 | +0.05619 % | 0.8225 |
| 0.02 | 0.730702789 | 0.730506204 | +0.02691 % | 0.7308 |
| 0.03 | 0.659037314 | 0.658996267 | +0.00623 % | 0.6593 |
| 0.04 | 0.598864830 | 0.598933758 | +0.01151 % | 0.5992 |
| 0.05 | 0.546547892 | 0.546700651 | +0.02794 % | 0.5469 |
| 0.06 | 0.500142214 | 0.500361116 | +0.04375 % | 0.5006 |
| 0.07 | 0.458462568 | 0.458734367 | +0.05925 % | 0.4589 |
| 0.08 | 0.420723460 | 0.421037574 | +0.07460 % | 0.4212 |
| 0.09 | 0.386370262 | 0.386717905 | +0.08990 % | 0.3869 |
| 0.10 | 0.355020182 | 0.355363267 | **+0.09655 %** | 0.3555 |

Worst deviation against the **lab-evaluated EXACT reference** (the gate): **0.096545 % at
x = 0.10 m.** Worst against the manual's 4-dp printed **Target** column (**corroboration only,
decides nothing**): 0.136919 %. Ansys's Fluent column is context only. This box has no Fluent;
nothing here is a statement about Ansys.

## 5. THE BAND CAVEAT — carried on the row in these words, NOT softened (supervisor's ruling)

**git cannot prove the band `TOL = 0.01` predates the first VMFL006 field produced on this
box** (R1's comparator sat untracked on disk from 2026-08-26 and a pre-freeze smoke ran
2026-08-26; the band was first committed 2026-08-31). R2's band is byte-identical to R1's, so
**R2 inherits this caveat and does NOT resolve it.** The supervisor ruled 2026-08-31 to inherit
`TOL = 0.01` unchanged and this record does not let R2's strength imply the caveat has gone
away. R2 is *stronger* only in that R1 has now RUN: its accuracy sits 10.4–10.9× inside the
band, and R1's own §12 showed the only pre-band field (the smoke) sat ~7 band-widths *outside*,
so no band that could have been fitted to either would look like 1 %. **The band was
deliberately NOT tightened after seeing the answer — tightening would itself be fitting, in the
rigorous-looking direction — because a ceiling is the one the charter imposes, never the most
conservative available.** The caveat is real, bounded, and it rides on register row #50.

## 6. Cost (rule 12) — MEASURED, and the calibration

| Level | wall s | core-min (measured) | timeout_s | prereg estimate (core-min) |
|---|---|---|---|---|
| L1 | 12 | 0.200 | 1080 | ~0.22 (13.3 s) |
| L2 | 45 | 0.750 | 1068 | ~0.80 (48 s) |
| L3 | 236 | 3.933 | 1023 | ~3.33 (200 s) |
| **Total** | **293** | **4.883** | — | point 4.4, bracket 4.1–5.7 |

**Measured 4.883 core-min** against the EXTRAPOLATED bracket 4.1–5.7 (point 4.4): **ratio
actual/predicted = 1.110**, inside the bracket. Attribution: **misprediction** — the
linear-in-iterations scaling slightly under-estimated L3 (236 s actual vs 200 s; ratio 1.18),
so the whole-job miss is upward. **Waste = 0, named separately and never absorbed into the
ratio**: no level stalled (all under 3600 wall s), all three ran to completion and graded, no
re-run. Cap 18 core-min, 27 % used, never approached. Dollars **DERIVED not measured** (box
cannot read its own billing): 4.883 core-min × $0.0513/core-h ÷ 60 = **$0.004176**. cost_basis:
owner-stated rate, REPORTED-BY-OWNER, not measured. The rule-12 calibration row is appended to
`docs/COST_CALIBRATION.md`.

## 7. Freeze and provenance

- **Freeze commit:** `c067c56ffd914f9801262423e429b9637cc321a3` (PREREGISTRATION.md), with the
  technical bundle at `d0aa159008acbed514e53e6da5615498776d782b`. At `c067c56f` all frozen files
  are present and match disk. Verified this grading: disk == blob@`c067c56f` == blob@HEAD
  IDENTICAL for PREREGISTRATION.md (`f698ece8`), grade_vmfl006_r2.py (`3c8f4bbc`), make_u
  (`672a2018`), graetz_reference (`355f70bb`), run_vmfl006_r2.sh (`a0eda15b`). Freeze chain also
  personally verified by the supervisor (root absent at freeze 18:35:57Z; earliest run-root byte
  18:37:48Z; gap +111 s).
- **Comparator:** `cases/ansys_verification/VMFL006-R2/grade_vmfl006_r2.py` blob `3c8f4bbc`.
- **Run root:** `verification/runs/ansys_verification/VMFL006-R2/` (L1/L2/L3, GRADING_VMFL006.json,
  COST.txt, LAUNCH_RECORD.txt, CONTENTION.txt, per-level RUN_RC.txt and birth_certificate.json).
- **The runner-race finding:** the queue_runner daemon scans the filesystem, not git, and picked
  the top-level queue entry off disk and launched it before this lane's git commit of that copy
  could land — so the intended queue commit `8a4834fc` landed EMPTY and was honestly corrected by
  `a974d458` (the launched copy, with the runner's _launch block). The empty commit is not
  reverted (rule 10). This is CLAUDE.md §11.3 / the 2026-08-26 detached-runner ruling: the race
  avoided idle compute. Recorded here so it is in the record, not only in a report.

**Cells ×4 with constant aspect ratio (Roache entitlement):** L1 4000 (maxAR 8.8366) / L2 16000
(8.7493) / L3 64000 (8.7065) — both NX and NR double, cells grow ×4, aspect ratio holds. This is
what VMFL038 R1 lacked; it is why this triple is entitled to Roache treatment.
