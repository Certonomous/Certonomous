# VMFL054-R3 — RESULTS (`GATE REACHED`, register row #69)

**Case:** VMFL054-R3 — Laminar Flow in a Trapezoidal Driven Cavity (Ansys FDVM VM2026R1 p.173)
**Physics:** steady 2D laminar, lid-driven trapezoidal cavity, simpleFoam / SIMPLEC. Graded quantity: `u_x` at the cavity centre.
**Role:** grid-convergence (Roache) limb. External Darr & Vanka (1991) validation limb is DEFERRED (manual states the reference only as a plotted profile; figure digitization pending) and the BC-direction cap from R1 Ruling 1 stands.

**Status of this file:** DRAFT written by an ansys-lane, not committed. The §3 check-1 comparator diff-read and the register commit are the supervisor's, separately gated (git-ref writes classifier-blocked this session).

---

## VERDICT: GATE REACHED

The grid-convergence gate is MET, but PASS is WITHHELD: the external experimental validation limb (Darr & Vanka 1991) is deferred and the BC-direction cap (R1 Ruling 1) stands. A GATE-REACHED row is not a credential.

### Instrument integrity (checked before grading)
- Comparator `cases/ansys_verification/VMFL054-R3/grade_vmfl054_r3.py` disk `git hash-object` = **fd959928280e178706b929899962918cd444a1ca** == HEAD blob. **disk == HEAD** (board-recorded freeze blob fd959928, confirmed).
- Prereg blob `cases/ansys_verification/VMFL054-R3/PREREGISTRATION.md` = **0fd58845b6425f32a0adcb9dc31bbbf530858df8** == HEAD blob.
- `--selftest`: **16/16 arms passed, rc=0.** Planted-zero controls both PASS and both known-bad guards REFUSE as designed (control shown able to fail): probe planted-zero read-back error 3.6e-15, U-field planted-zero read-back error 7.1e-15; physical-range garbage (collapse/blow-up/NaN) all refused (exit 2); rule-4 completion refusals (no-End, missing-field, age-guard, rc!=0) all fire.

### Completion rule (CLAUDE.md rule 4) — comparator ACCEPTED all four levels
- Every level: `RUN_RC = 0` MEASURED, `End` line present, fields present and newer than `0/` (age guard), no FOAM FATAL.
- **endTime = 50000; every level converged via `residualControl` BELOW that ceiling** (last Time L1=741, L2=985, L3=1990, L4=7118). This is the PRE-DECLARED frozen completion path for a residualControl-terminated steady solve (comparator header, same basis as R1/R2, VMFL038/VMFL063), **not a defect** — the frozen rule refuses only a run that reached `endTime` without converging.

### The grade
| level | u_x(centre) (m/s) |
|---|---|
| L1 | -163.116224 |
| L2 | -164.615056 |
| L3 | -164.753374 |
| L4 (finest) | -164.813793 |

- **Graded triple = L2/L3/L4** (a-priori fixed selection rule, anti-fitting — comparator header). Roache state **CONVERGING**, **R = 0.4368**, observed order **p = 1.195**, **GCI_fine = 0.03554 %** (Fs = 1.25).
- 4-point diagnostic (NOT a gate): p(L1,L2,L3) = 3.438, p(L2,L3,L4) = 1.195, settling_toward_2 = True.
- Gate limbs: p in [1.0, 3.0]? **True.** GCI_fine <= 5.0 %? **True.** → **GATE REACHED.**
- Rule-5: triple is CONVERGING, so the gate verdict stands (not `NOT A RESULT`).

**Match vs board:** u_x triples -163.12 / -164.62 / -164.75 / -164.81 ✓; finest triple CONVERGING R=0.437 p=1.195 GCI 0.0355 % ✓; both gate limbs met → GATE REACHED ✓. **All match.**

---

## Cost (CLAUDE.md rule 12) and est-vs-actual calibration
| | value |
|---|---|
| ranks | 1 (serial, all four solves) |
| launcher-reported total | **18.7833 core-min** (launcher.queue.out; board-recorded 18.78) |
| per-level sum (measured) | **19.9167 core-min** (L1 0.0166667 + L2 0.116667 + L3 1.0 + L4 18.7833) |
| cost_basis | c7a.4xlarge $0.0513/core-h, owner-stated 2026-08-21/22 — REPORTED-BY-OWNER, NOT MEASURED; $ DERIVED |
| $ derived (per-level sum) | $0.01703 (19.9167/60 × 0.0513) |

**FINDING (surfaced, not resolved here):** the launcher's final `core_min_used` field reads **18.7833**, which equals the L4 level alone, not the four-level cumulative total. The honest cumulative cost across all graded levels is **19.9167 core-min**. The board figure (18.78) inherits the launcher's single-level total. The gap (1.13 core-min, L1+L2+L3) is a launcher reporting quirk, not compute waste. Est-vs-actual: an ESTIMATE OVERRUN was reported-not-enforced (elapsed 1102 s > 1.10 × estimate 960 s; no registered cap on this entry — `ESTIMATE_OVERRUN.txt`).

**Calibration row `C-20260909T021050.027704Z-c524627f` landed in `docs/COST_CALIBRATION.md` (commit `b3a5c353`, 2026-09-09).**

---

## Artifacts
- Grading record (materialized this session): `verification/runs/ansys_verification/VMFL054-R3/GRADING_VMFL054_R3.txt`
- Cost/launch: `cases/ansys_verification/VMFL054-R3/launcher.queue.out`, `ESTIMATE_OVERRUN.txt`, `STATUS.queue.VMFL054-R3`
- Frozen comparator: `cases/ansys_verification/VMFL054-R3/grade_vmfl054_r3.py` (blob fd959928)
- Frozen prereg: `cases/ansys_verification/VMFL054-R3/PREREGISTRATION.md` (blob 0fd58845)

**Register row commit is classifier-blocked this session and is parked on Sanaa's desk (SUBMISSIONS PARKED, rule 7 / rule 10).**
