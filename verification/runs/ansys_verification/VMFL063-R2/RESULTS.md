# VMFL063-R2 — RESULTS (`GATE FAIL`, register row #68)

**Case:** VMFL063-R2 — Separated Laminar Flow Over a Blunt Plate (Ansys FDVM VM2026R1 p.193)
**Physics:** Re_2t = 260, steady 2D laminar, simpleFoam / SIMPLEC, zero numerical diffusion.
**Role:** resolution-only successor to register #44 (VMFL063, `GATE FAIL`). R2 changes only the mesh; band/gate/cap inherited (L-487: a successor never widens the band). **Row #44 stands.**

**Status of this file:** DRAFT written by an ansys-lane, not committed. The §3 check-1 comparator diff-read and the register commit are the supervisor's, separately gated (git-ref writes classifier-blocked this session).

---

## VERDICT: GATE FAIL

Row verdict is the **worst limb**. Limb A ceiling is **GATE REACHED**, so this row can **never read PASS and is NOT a credential** (`verdict_note` in the grading JSON).

### Instrument integrity (checked before grading)
- Comparator `cases/ansys_verification/VMFL063-R2/grade_vmfl063_r2.py` disk `git hash-object` = **5d94fecbfa35013943b60e758ff433ad50ef00f7** == HEAD blob. **disk == HEAD.**
- Prereg blob = **ec8575147edf18350fb94ba42eb4c5b5c16003dd** == HEAD blob.
- (Overall HEAD has advanced to `cea9c80c` since launch record's `4c2ccb96`; the two frozen blobs are byte-identical, which is what the grade rests on.)
- Dual-interpreter `--selftest`: **68 checks, 0 failures** under BOTH `python3` and `python3 -O` (RC=0 each).
- Planted-zero controls **REFUSE as designed** in selftest: P1a reader-sensitivity refusal and the BLIND-writer refusal both fire (the control is shown able to fail).
- **Live planted-zero on the graded run data both PASS** (control is live, not just in selftest): wall_shear channel — plant 5.937e-06 into all 160 plateTop faces moved the crossing upstream 0.0814 m, worst read-back error 1.0e-16; near-wall u_x channel — plant pushed the crossing out of the window, worst read-back error 5.0e-14.

### Completion rule (CLAUDE.md rule 4) — comparator ACCEPTED all four levels
Every level: `state = COMPLETE`, `rc = 0` MEASURED, `End` line present, `SIMPLE solution converged`, `ExecutionTime` count == last Time, all 5 physics-critical fields present and NEWER than `0/U` (age guard passed), numeric-latest time dir == log last Time.

**Early residual-convergence is treated as COMPLETE, not refused.** All levels converged via `residualControl` BELOW the `endTime` ceiling 30000 (last_time = 1944 / 1944 / 4177 / 10637). The frozen completion rule **refuses only when `last_time == endTime`** ("ran out of clock and did NOT converge") — a converged solve stopping before the ceiling is the accepted path.

### Limb A — CONTINUUM claim (`LR/(2t)`, gate limb), ceiling GATE REACHED
| level | cells | LR (m) | LR/(2t) |
|---|---|---|---|
| L1 | 23 040 | 0.5548232 | **6.164703** |
| L2 | 92 160 | 0.5040213 | **5.600237** |
| L3 (finest) | 368 640 | 0.4950746 | **5.500829** |

- **Roache triple: CONVERGING.** observed order **p = 2.505456**, **R = 0.176109** (d32/d21; monotone, both differences same sign), ratio r = 2.0, Fs = 1.25. Richardson-extrapolated f = 5.479580.
- **GCI_fine (Fs=1.25) = 0.004829 (0.48 %).**
- Reference (gate): manual Target **4.0** (Lane & Loehrke 1980, **EXPERIMENTAL**; Ansys Fluent 4.16 / CFX 4.05 carried as CONTEXT only, not the gate).
- Band: frozen **±10 %**.
- Finest **5.500829 vs 4.0 → deviation 37.52 %**, **OUTSIDE** the 10 % band → **GATE FAIL**.
- Rule-5 note: the triple is CONVERGING, so this is a valid GATE FAIL (not `NOT A RESULT`). The value is 2nd-order converged and lands ~37 % high; refinement moved it monotonically toward 4.0 (6.16 → 5.60 → 5.50) but the continuum answer of this laminar SIMPLE model is genuinely ~5.5, not 4.0.

### Limb B — SAME-DISCRETE-PROBLEM IDENTITY (determinism), ceiling PASS → PASS
- L1 vs L1D (bit-for-bit twin): same converged iteration count (1944), `LR` bitwise equal (0.5548232319529735), sha256 identical on `wallShearStress`, `U`, `p`. **PASS.**

### Row verdict
GATE FAIL (limb A) dominates PASS (limb B) → **ROW VERDICT: GATE FAIL**. Not a credential.

---

## Cost (CLAUDE.md rule 12) and est-vs-actual calibration
| | value |
|---|---|
| ranks | 1 (serial, all four solves) |
| **actual total** | **146.5166 core-min** (LAUNCH_RECORD.txt; L1 1.05 + L1D 1.05 + L2 10.3833 + L3 134.0333) |
| pre-registered ESTIMATE | 125 core-min |
| cap | 320 core-min (running total) — not exceeded |
| **calibration ratio actual/predicted** | **1.172** |
| cost_basis | c7a.4xlarge $0.0513/core-h, owner-stated 2026-08-21/22 — REPORTED-BY-OWNER, NOT MEASURED; $ DERIVED |
| $ derived at actual | $0.1253 (146.5166/60 × 0.0513) |

**Gap attribution:** misprediction on **L3**, not waste and not contention. Predicted L3 ≈ 108 core-min at ≈8 770 iterations (iters ∝ N^0.552); actual L3 134.03 core-min at **10 637 iterations** — the iteration-count extrapolation under-predicted by ≈21 %. L1/L1D/L2 landed on estimate (measured basis). No stall: every level reached `residualControl` convergence.

**Calibration row `C-20260909T021050.027684Z-99f2d7b1` landed in `docs/COST_CALIBRATION.md` (commit `b3a5c353`, 2026-09-09).**

---

## Artifacts
- Grading record: `verification/runs/ansys_verification/VMFL063-R2/GRADING_VMFL063_R2.json`
- Launch/cost: `verification/runs/ansys_verification/VMFL063-R2/LAUNCH_RECORD.txt`, `COST.txt`
- Frozen comparator: `cases/ansys_verification/VMFL063-R2/grade_vmfl063_r2.py` (blob 5d94fecb)
- Frozen prereg: `cases/ansys_verification/VMFL063-R2/PREREGISTRATION.md` (blob ec857514)
