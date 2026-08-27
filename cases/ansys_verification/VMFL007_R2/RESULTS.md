# VMFL007-R2 — Non-Newtonian Flow in a Pipe, linear-solver / preconditioner slate: `NOT A RESULT` (comparator refused; the control arm diverged)

## VERDICT: `NOT A RESULT` — the frozen comparator REFUSED (exit 2) at its planted-zero control

VMFL007-R2 is a **single-grid linear-solver / preconditioner slate** (6 arms, no Roache
triple), whose case-level verdict ceiling is `NOT A RESULT` by construction (CLAUDE.md rule 5;
it seeks no gate — the frozen gate `[60217.40, 60822.60]` Pa is carried UNCHANGED for R3 and is
not applied here). The frozen comparator refused on its planted-zero control and produced no
graded number. Drafted by `ansys-lane-opus48` (lane H) for the supervisor's audit. Manual **p. 29**;
reference the **closed-form/exact** 60.52 kPa pressure drop (Hughes & Brighton, *Fluid Dynamics
for Mechanical Engineers*, McGraw-Hill 1991); tier ceiling for the CASE `GATE REACHED`, but this
single-grid R2's own ceiling is `NOT A RESULT`.

### The refusal, exactly

`grade_vmfl007_r2.py` (blob `0d29d3b8`, hash-verified == committed) → **exit 2**, verbatim:

> REFUSED (exit 2): PLANTED-ZERO CONTROL FAILED on …/A1_GAMG_GaussSeidel/postProcessing/pInlet/0/
> surfaceFieldValue.dat: planted 0.001234 at row 5000 (t=5001, v=7.1176e+73) and read back a
> change of 0. The reader CANNOT SEE a known non-zero at this magnitude, so any zero, plateau or
> bound it reports is NOT EVIDENCE.

### Diagnosis — the control arm DIVERGED (a real finding), measured on the comparator's own series

The refusal is not a reader defect: the reader is correct and the plant is genuinely invisible,
because arm A1's pInlet flux **diverged**. Measured on the same `pInlet` series the comparator
reads: A1 first exceeds 1e10 at **t = 353** (v = 1.016e10) and reaches **9.450e+144** at endTime
(t = 10000). A 1.234e-3 plant added to 7.1e+73 is lost to floating point, so the planted-zero
control refuses — a reader shown unable to see a known non-zero cannot certify a zero (CLAUDE.md
rule 3). **rc = 0 and an End line are not convergence** (L-15): the solve ran to endTime and
diverged.

**The slate, as context (NOT graded — the comparator refused on the first arm):** 4 of the 6
linear-solver arms diverged catastrophically at endTime — A1 9.45e+144, A2 (GAMG/DICGaussSeidel)
4.82e+148, A4 (PCG/GAMGprecon) 2.91e+135, A6 (smoothSolver/symGaussSeidel) 1.59e+161 — while 2
did not: **A3 (PCG/DIC)** last pInlet 71.9 and **A5 (PBiCGStab/DIC)** last 63.3. The slate exists
to screen which solver/preconditioner pairs are stable on this case for R3; on this evidence
only the DIC-preconditioned arms survived. This is a screening finding, not a graded gate.

### Provenance
- **Comparator:** `grade_vmfl007_r2.py` blob **`0d29d3b8`**, on-disk == committed at HEAD (hash-verified).
  `--selftest` **43 checks, 0 failures**.
- **Run root:** `verification/runs/ansys_verification/VMFL007_R2/` (6 arm dirs, COST.txt, CONTENTION.txt).
- **Prereg sha (from COST.txt):** `141185ad`.

## COST (rule 12 calibration)
- **Measured actual:** **9.2167 core-min** (total wall 553 s, serial; `COST.txt`), of a 90 core-min
  slate cap / 20 core-min per-arm cap.
- **$ derived:** 9.2167 core-min × $0.0513/core-h ÷ 60 = **$0.0079**, **REPORTED-BY-OWNER, NOT
  MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); the rate is
  owner-stated (Sanaa 2026-08-21/22).

**Ledger follow-up:** register row and COST_CALIBRATION row land with this record. No pre-registered
estimate/actual ratio is stated because the slate's value is the screening finding, not a cost gate;
the actual 9.2167 core-min is recorded against the 90 core-min cap (10.2 %).
