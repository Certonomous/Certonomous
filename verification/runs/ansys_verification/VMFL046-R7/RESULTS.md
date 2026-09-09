# VMFL046-R7 — RESULTS (`NOT A RESULT`, register row #70)

**Case:** VMFL046-R7 — Supersonic Flow with a Normal Shock in a Converging-Diverging Nozzle (Ansys FDVM VM2026R1 p.155)
**Physics:** density-based transient, rhoCentralFoam (Kurganov/KNP, vanLeer reconstruction, Euler ddt, maxCo 0.2; Greenshields et al. 2010). Graded quantity: `x_shock` vs 1.250 m, band ±5.0 %.
**Role:** grid-convergence limb (r=2 triple L1/L2/L3). This R7 run is the answer-blind start-from-rest attempt after R6 core-dumped in startup.

**Status of this file:** DRAFT written by an ansys-lane, not committed. The §3 check-1 comparator diff-read and the register commit are the supervisor's, separately gated (git-ref writes classifier-blocked this session).

---

## VERDICT: NOT A RESULT

The finest/only level available crashed before completion; the comparator **REFUSED to grade (exit 2)** at the strict-completion check. No gate quantity was read — refusal precedes grading.

### Instrument integrity (checked before grading)
- Comparator `cases/ansys_verification/VMFL046-R7/grade_vmfl046_r7.py` disk `git hash-object` = **02113dbeaeb1cec940214178451c92c17b274b93** == HEAD blob. **disk == HEAD** (board-recorded freeze blob 02113dbe, confirmed).
- Prereg blob `cases/ansys_verification/VMFL046-R7/PREREGISTRATION.md` = **fda7d7ede8d542e81ea18ae6244c37e650fa596a** == HEAD blob.
- `--selftest`: **70 ok, 0 FAILED, rc=0.** Every planted-zero / plateau / read-window / N4(R6) physical-range control fires as designed (each control shown able to fail); rule-4 completion transliteration refuses truncated, early-stopped, cap-killed and restart-splice logs.

### Completion rule (CLAUDE.md rule 4) — comparator REFUSED (exit 2)
- **L1 crashed: `RUN_RC = 134`** (SIGABRT / core dump — `log.rhoCentralFoam` shows "Aborted"), last `Time = 0.02813` << `endTime = 0.08`, **no `End` line**, run incomplete. Board note: negative reconstructed temperature (T ≈ -18.33) at Time ≈ 0.0281 — a KNP numerical blow-up (rhoCentralFoam has no limitTemperature clamp).
- **L2 and L3 never ran.**
- Comparator refusal (first check to fire): `L1: RUN_RC = 134, not 0 (rule 4).` The comparator exits 2 rather than degrade → **NOT A RESULT.**
- (The refusal's generic text references the rc-124 cap-kill class; the actual value read is `RUN_RC = 134`, an abort/core-dump. Both are `!= 0` and both are rule-4 refusals → NOT A RESULT either way. No gate number exists to report.)

**Match vs board:** expected NOT A RESULT (L1 crashed rc134, negative T ~0.0281, no End, L2/L3 never ran) ✓. **Matches.**

---

## Cost (CLAUDE.md rule 12)
| | value |
|---|---|
| ranks | 1 (serial) |
| L1 actual (crashed) | **0.683333 core-min** (wall 41 s ÷ 60; `launch.out`) |
| L1 level cap | 27 core-min (not reached — crashed at 41 s) |
| L2 / L3 | not run (0 core-min) |
| cost_basis | c7a.4xlarge $0.0513/core-h, owner-stated 2026-08-21/22 — REPORTED-BY-OWNER, NOT MEASURED; $ DERIVED |
| $ derived | $0.000584 (0.683333/60 × 0.0513) |

The spend is a crashed-startup cost, not a graded solve; no est-vs-actual calibration is meaningful for a crash (the run never reached the estimated regime). Waste is named, not absorbed: 0.683 core-min consumed producing no result.

---

## Artifacts
- Grading record (materialized this session, the refusal): `verification/runs/ansys_verification/VMFL046-R7/GRADING_VMFL046_R7.txt`
- Crash log / rc: `verification/runs/ansys_verification/VMFL046-R7/L1/log.rhoCentralFoam`, `L1/RUN_RC` (=134)
- Launch/cost: `verification/runs/ansys_verification/VMFL046-R7/launch.out`
- Frozen comparator: `cases/ansys_verification/VMFL046-R7/grade_vmfl046_r7.py` (blob 02113dbe)
- Frozen prereg: `cases/ansys_verification/VMFL046-R7/PREREGISTRATION.md` (blob fda7d7ed)

**Calibration row `C-20260909T021050.027720Z-81cae542` landed in `docs/COST_CALIBRATION.md` (commit `b3a5c353`, 2026-09-09). Register Row #70 landed 2026-09-09 after Sanaa authorized the record-landing permissions.**
