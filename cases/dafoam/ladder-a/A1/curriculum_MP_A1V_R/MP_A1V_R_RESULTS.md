# MP-A1V-R — RESULTS

**Item.** A1 NACA0012 incompressible multipoint drag-minimisation at fixed lift.
FD-verification of the **demonstrated multipoint gradient** via **DIRECT-DV
central difference**. Successor to **MP-A1**, which was `NOT A RESULT` because
its forward-mode FD verification was unmeasurable (AV-2 — seeding forward mode
fails the primal on this exact case, on both images). MP-A1V-R resolves the
**§2ay state-(b)** open carried on MP-A1.

**VERDICT: `PASS` — TWO ROWS.**

| row | verdict |
|---|---|
| SHIPPED | `PASS` |
| PATCHED | `PASS` |

A full `DAFOAM_CHARTER.md` §6 two-row verdict. Both rows verified by the
dafoam-supervisor at source.

**Grade record (authoritative, cited by absolute path):**
`/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1V-R-a1-naca0012-multipoint-fixedlift-fdverify-directDVcentral/MPA1V_grade_20260907T202155Z.json`
(`verdict: PASS`, `rows: {SHIPPED: PASS, PATCHED: PASS}`).

---

## FD-verification table (G5J)

- **3 constraint-gradient members** (FFD shape indices 3, 6, 2) × **3 scenario
  points** (α ≈ 3.14 / 5.14 / 7.14 deg) = **9 gradeable FD/adjoint pairs per
  row**, **18 pairs total** across the two rows.
- **ALL 18 PASS.** 0 gate-fails, 0 sign-flips.
- Aggregate relative error per scenario: **0.085 %–0.13 %**. Worst single-pair
  relative error **≈ 0.33 %** — all far inside the pre-registered 5 % band
  (band_D / band_E).
- **Plateau step chosen at 3e-4** on the ladder `[3e-3, 1e-3, 3e-4, 1e-4]`.
- **CAVEAT — carried honestly, does not overstate the PASS:** the plateau proof
  is **ONE-SIDED on every pair** ("fine side only; coarse unmeasured"). This is
  the **frozen grader's registered criterion, not a defect**.
- **Strengthening context (beyond the one-sided plateau):** the raw
  `d_by_step` values show the FD gradient is **step-robust across the full
  4-step ladder** — the adjoint agrees to **< 0.3 % at every step**, which
  raises confidence beyond the one-sided plateau alone.
- **G-EVALFAIL:** 32/32 FD evaluations succeeded per F arm — direct-DV
  central-difference is the whole point of the successor.

**G6 dot-product duality: honestly `NOT MEASURED` (AV-2).** Seeding forward
mode fails the primal on this exact case on both images; named, never composed.
The successor's direct-DV central-difference route is what makes the gradient
verifiable at all here.

---

## Constraint and objective gates

- **G-CLHOLD — lift held at all 3 points, both rows.** Absolute deviation
  ≈ 4.3e-7 … 5.2e-7 against tolerance 1e-3, CL positive throughout. This fixes
  the SO-3 lift-collapse.
- **G-DRAG — drag reduced at fixed lift.** J_baseline **0.02180598** →
  J_final **0.02071195**, **≈ 5.0 %** at fixed lift.

---

## Controls fired (planted-zero discipline, CLAUDE.md rule 3)

- **Planted-F seen both rows** — worst residual **1.79e-16** (the reader sees
  the planted perturbation).
- **Planted-X flips PASS → GATE FAIL** — the reader sees a non-zero and the
  gate turns over, so a real defect could not have passed silently.

---

## Freeze verification (CLAUDE.md rule 2)

- Frozen grader: `cases/dafoam/ladder-a/A1/curriculum_MP_A1V_R/mpa1v_grade.py`.
- Disk md5 **0a41208e**; HEAD blob **32847ca2** == freeze-commit **2c2da399**
  blob (byte-identical; freeze verified by the supervisor).
- The **grading path is the frozen file**. The grader was run **without
  `--skip-freeze`** — it self-ran `freeze_check` + planted controls + F6.

---

## Chain and completion (CLAUDE.md rule 4)

- MESH rc=0, FV-S rc=0, FV-P rc=0; **3/3 arms**; `grader_rc=0`.

---

## Cost (CLAUDE.md rule 12)

- **Actual = 8.734 core-min GROSS** (MESH 0.167 + FV-S 4.367 + FV-P 4.2),
  MEASURED from the grade json.
- **Registered estimate 11.61 core-min**, cap **33.0** (NOT hit).
- **Ratio actual/predicted = 0.752** — a conservative-direction misprediction;
  no contention, no waste to name (all three arms under per-arm caps).
- Derived dollars: 8.734/60 × $0.0513 = **$0.00747 DERIVED, NOT MEASURED**
  (`cost_basis`: c7a.4xlarge $0.0513/core-h, REPORTED-BY-OWNER — the box cannot
  read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5).
- Calibration row landed in `docs/COST_CALIBRATION.md`, id
  **C-20260907T211628.203369Z-08adcd59**.

---

## §2ay state-(b) resolution

MP-A1 was `NOT A RESULT` (forward-mode FD unmeasurable, AV-2), leaving §2ay in
state (b). **MP-A1V-R resolves §2ay state-(b) for MP-A1**: it both
**demonstrates and verifies** the mandated A1 multipoint gradient capability via
a direct-DV central-difference FD verification, with the honest caveat that the
plateau proof is one-sided and G6 duality remains `NOT MEASURED`.
