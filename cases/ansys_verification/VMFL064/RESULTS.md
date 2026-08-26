# VMFL064 — RESULTS

**Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion** (backward-facing
step). Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 195/196**.
Laminar `simpleFoam`, Re_D = 200. Graded **2026-08-26** by `ansys-lane-opus`.

## VERDICT — `NOT A RESULT`

**The frozen comparator REFUSED (exit 2) at L3** and never reached a verdict, a triple or a
GCI. Under CLAUDE.md rule 1 the honest label for a case that produced no gradeable value on
its frozen grading path is **`NOT A RESULT`**. It is not softened, and it is not a solver
failure: **all three levels ran clean.**

The refusal, verbatim (`verification/runs/ansys_verification/VMFL064/GRADING_ATTEMPT_REFUSED.txt`):

> `REFUSED (exit 2): L3: wall shear never changes sign -- no reattachment found`

## What ran, and what it cost

| level | cells | iterations to `SIMPLE solution converged` | rc | wall s | core-min |
|---|---:|---:|---:|---:|---:|
| L1 | 3 072 | 424 | 0 | 2 | 0.0333 |
| L2 | 12 288 | 907 | 0 | 18 | 0.300 |
| L3 | 49 152 | 2 152 | 0 | 303 | 5.05 |
| **total** | | | | **323** | **5.383** |

**Cost: 5.383 core-min measured** (RANKS = 1; `RUN_RC.txt` per level and
`verification/runs/ansys_verification/VMFL064/COST.txt`), against a frozen cap of
**90 core-min** — 6.0 % of cap. **Derived** dollars: 5.383 core-min = 0.08972 core-h ×
**$0.0513/core-h** = **$0.0046**. The rate is **reported-by-owner, NOT measured** — the box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so the dollar figure is
**derived, not measured**.

Every clause of strict completion (rule 4) passed at **all three** levels — `rc = 0`, an
`End` line in `log.simpleFoam` by exact name, `SIMPLE solution converged`, last time strictly
below `endTime` (424 / 907 / 2152 against 20 000, i.e. the solver stopped on its own
residualControl and did **not** run out of clock), all five fields present at that time,
`ExecutionTime` count equal to the iteration count, and the age guard (fields newer than the
case's own `0/U`). `completion()` returned for L1, L2 **and L3** before the L3 refusal.

## The numbers that exist

| level | LR (m) | **LR/s** | cross-instrument LR (m) | agreement | cell dx (m) |
|---|---:|---:|---:|---:|---:|
| L1 | 0.023101 | **4.714416** | 0.023101 | 2.42e-07 m | 1.56e-03 |
| L2 | 0.023524 | **4.800738** | 0.023524 | 5.77e-08 m | 7.81e-04 |
| L3 | — refused — | — | — | — | 3.91e-04 |

**The cross-instrument control PASSED and is the load-bearing good news here.** The
pre-registration's §7 named exactly one principal risk — that OpenFOAM reports wall shear as
`-(nHat & devTau)`, so a silently inverted sign convention would place the reattachment point
inside the recirculation bubble. The independent instrument (sign change of near-wall `u_x`)
agreed with the wall-shear instrument to **2.4e-07 m and 5.8e-08 m**, against a refusal
threshold of 3 cell widths (4.7e-03 and 2.3e-03 m) — **four to five orders of margin**.
`ORIENT = -1` is confirmed correct on real data, not assumed.

The planted-zero control (rule 3) and the p-floor planted control (PRE-COMPUTE AMENDMENT 1)
both fired clean on the real run: the comparator printed
`p-floor planted control OK (P_MIN = 0.05): (1.0,1.1,1.2) -> NOT A RESULT, no GCI`
before reading any level.

## TRIAGE — why L3 refused (a FINDING, not a retry)

**The L3 mesh resolves a secondary corner vortex at the foot of the step; L1 and L2 do not.**
Measured directly from `L3/2152/wallShearStress` on the `bottomWall`, converted to physical
sign with the frozen `ORIENT = -1`:

| face | x (m) | x/s | physical wall shear (m²/s²) |
|---|---:|---:|---:|
| 1 | 1.95e-04 | 0.040 | **+7.481e-06** |
| 2 | 5.86e-04 | 0.120 | **+9.281e-07** |
| 3 | 9.77e-04 | 0.199 | −3.337e-05 |
| 4 | 1.37e-03 | 0.279 | −8.051e-05 |

The profile therefore **starts positive** at L3 and carries **two** sign changes (near
x ≈ 7e-04 m, the end of the corner eddy, and near x ≈ 2.38e-02 m, the true reattachment). At
L1 and L2 it starts negative and carries **one**.

The frozen reader `first_sign_change()` returns `None` when `vs[0] >= 0` — its comment reads
*"no recirculation at all behind the step"* — and `main()` refuses on `None`. On L3 that
premise is false in a way the pre-registration did not anticipate: there **is** recirculation,
and there is also a **counter-rotating corner eddy inside it** whose wall shear is positive,
sitting upstream of the main bubble. **A reader that keys on the FIRST negative-to-positive
crossing of a profile it requires to START negative cannot survive the appearance of a
secondary corner vortex under refinement.**

**This failure mode is NOT in the pre-registration's §14 falsification clause.** §14 named a
`GATE FAIL` outside the band, a `NOT A RESULT` from a non-monotone LR triple, and a refusal
from the cross-instrument control. It did not name *the finest level resolving a flow feature
the coarser levels do not, and thereby invalidating the reader's starting premise.* That is
the new thing this case bought, and it is recorded rather than patched.

**The comparator behaved correctly.** It refused rather than degrading (rule 4's standing
form) — it did **not** return the corner eddy's x ≈ 7e-04 m as a reattachment length, which
would have been a wrong number wearing a right shape (LR/s ≈ 0.14). A refusal is the designed
outcome and it fired.

## What was NOT done, said plainly

- **The comparator was NOT edited after compute.** Rule 2 closes the gates at first compute;
  the frozen grading path stands and this verdict stands with it.
- **Nothing was retried.** A refusal is a finding; re-running the same case against the same
  frozen reader would produce the same refusal.
- **No GCI, no observed order and no gate comparison are quoted for this row.** The triple was
  never formed.

### OFF-PATH DIAGNOSTIC — explicitly NOT a result, NOT a verdict, NOT for the register

For triage only, and for whoever registers a successor: taking the **last** negative-to-positive
crossing instead of the first (which the frozen reader does not do, and which this row does not
claim) gives LR/s = 4.714416 / 4.800738 / **4.853056**, a `CONVERGING` triple with p = 0.7224
and GCI_fine = 2.07 %, and the finest level 2.94 % from the experimental 5.0. **These numbers
are computed by a reader that is not the frozen one and they buy nothing.** They are stated
because they show the refusal cost a credential rather than concealing a bad one — the same
shape as L-338 — and because they size the prize for a successor registration.

**Successor (for the supervisor to decide, not claimed here):** a new registration —
`VMFL064-R2` under `ANSYS_VERIFICATION_CHARTER` §6, a NEW row citing this one — whose reader
locates the reattachment as the **last** sign change of the physical wall shear along the
bottom wall, or excludes the corner-eddy region explicitly, and whose selftest **DRIVES a
constructed profile carrying a secondary corner eddy** so the failure mode is a tested one and
not a remembered one. This row stays `NOT A RESULT` whatever the successor returns.

## Provenance

- Pre-registration: `cases/ansys_verification/VMFL064/PREREGISTRATION.md`, blob
  `7b9fd0dcaa141cacf4e0f3dee5a6ceab0b9f48b5` (freeze `1dc0e4d5`; PRE-COMPUTE AMENDMENT 1 at
  `a7c42398`, landed before the run root existed).
- Comparator (the grading path): `cases/ansys_verification/VMFL064/grade_vmfl064.py`, blob
  `0be9126cd6a3e3c860b98854a4e21ba1102edfdc`, **verified equal to its HEAD blob by the
  launcher before the first solver started** and again before grading.
- Run root: `verification/runs/ansys_verification/VMFL064/{L1,L2,L3}` — per-level
  `RUN_RC.txt`, `log.simpleFoam`, `birth_certificate.json`, `postProcessing/`; plus
  `LAUNCH_RECORD.txt`, `CONTENTION.txt`, `COST.txt`, `GRADING_ATTEMPT_REFUSED.txt`.
- Meshes birth-certified from `checkMesh`: 3 072 / 12 288 / 49 152 cells, **Mesh OK** at every
  level, max aspect ratio 9.615, max skewness ≤ 3.47e-13.
- Compute authority: Sanaa's permission at commit `bc0e687e`.
- Box contention at launch (`CONTENTION.txt`): 11 of 16 cores already busy (5 ×
  `buoyantBoussinesqSimpleFoam`, 1 × `rhoCentralFoam`, 1 × DAFoam, 4 × MPI FD arms). The run
  still finished at 6.0 % of its cap.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING.*
