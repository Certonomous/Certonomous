# VMFL054-R3 — Laminar Flow in a Trapezoidal Driven Cavity — PRE-REGISTRATION **FROZEN**

**THIS FILE IS THE FREEZE.** Drafted by `ansys-lane-opus` (running as **claude-opus-4-8**)
on **2026-09-07** for the `ansys-verification-supervisor`'s personal §3 check-4 diff
re-read and freeze commit. **No solver has produced a graded result for R3.** The only
compute against it is a scratch feasibility smoke (§7, §9), run OUTSIDE
`verification/runs/ansys_verification/` so it cannot create a `0/` or time dir and disarm
rule 4's age guard; **its numbers set NO gate, band, threshold or cap** (CLAUDE.md rule 2)
— and the smoke was kept ANSWER-BLIND (the converged centre `u_x` was never read), so the
graded quantity is not known to the drafting lane at freeze.

**THIS IS A FRESH REGISTRATION SUCCEEDING R2, NOT AN AMENDMENT OF IT.** First compute has
occurred on R2 (register row #53, `GATE FAIL`, freeze `489aef16`), so under rule 2 **R2's
gates are CLOSED and cannot be reopened.** R3 cites R2 and re-runs an EXTENDED ladder, per
§6, adding one finer grid level. **No gate, threshold, band, cap or label from R2 is
re-chosen here** — the band and GCI limit freeze byte-identical (proven below).

## 0. THE GRADING PATH IS PINNED BY BLOB SHA AT THIS COMMIT (rule 2)

- comparator `grade_vmfl054_r3.py` — blob **`fd959928280e178706b929899962918cd444a1ca`**
- driver `run_vmfl054_r3.sh` — blob **`f451c24ceb042c5784aa42807037af313be10a5e`**
- case inputs `case/` (all 9, byte-identical to R2's frozen inputs at `489aef16`):
  - `0/U` `4703ce8aa3c3970e7afeaca2fefc8d9bf347b237`
  - `0/p` `60bad011a3c5ed5c56c8b00f290ac3b6896c1d59`
  - `constant/momentumTransport` `f7d93d54ebae9785586564ad6eb86faf764ebcc3`
  - `constant/transportProperties` `d771424bf288ebf2caf92a15ad6ee15c791f2263`
  - `constant/turbulenceProperties` `f7d93d54ebae9785586564ad6eb86faf764ebcc3`
  - `system/blockMeshDict.template` `d15417a896764f13385fc88011ab9a74a0bb4f03`
  - `system/controlDict.template` `e328f6fe1d90ad3d4862eeef0339557e40fb7e06`
  - `system/fvSchemes` `09366c6b8875ee48d3aa59a8db2357e2d98d1be5`
  - `system/fvSolution` `9b5ca726722391248e1c726b0d60d132bf89d3e1`

Verify the frozen file IS the file that ran by hashing it against these blobs. **Gates are
CLOSED after this commit**; departures land only as dated addenda that cannot move a gate,
threshold, cap or label.

## 1. Case identity

- **Case:** VMFL054, *Laminar flow in a Trapezoidal Cavity*.
- **Manual:** Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 173**.
  **Title-page verified against the PDF (rule 15/L-144), 2026-09-07:** PDF page 1 reads
  "Ansys Fluid Dynamics Verification Manual", Release 2026 R1, March 2026, © 2026 Synopsys/ANSYS
  — matches the `.txt` sidecar and the p.173 content (Darr & Vanka reference, Re = 400).
- **Lineage:** R1 (freeze `05ec949e`, `NOT A RESULT` — infrastructure abort, register #52) →
  R2 (freeze `489aef16`, `GATE FAIL` — order limb, register #53) → **R3 (this file).**

## 2. What R3 tests, and why (the honest physics/numerics question)

R2 graded `u_x` at the cavity geometric centre (1.0, 0.5), `cellPoint`-interpolated, over
the r = 2 triple **L1/L2/L3 = 40/80/160**. It landed a **monotone CONVERGING** triple:

> L1 = −163.116224, L2 = −164.615056, L3 = −164.753374 m/s;
> R = 0.09228, observed order **p = 3.438**, fine-grid **GCI = 0.01067 %** (Fs = 1.25).

The **order limb FAILED** (3.438 ∉ [1.0, 3.0]); the **GCI limb PASSED**. Both were
required → `GATE FAIL`, **PREDICTED in the R2 freeze and the prediction held.**

**The open question R3 must honestly resolve.** A nominally 2nd-order scheme
(`bounded Gauss linear` convection + `Gauss linear corrected` diffusion) should show an
observed order p ≈ 2. R2's p = 3.438 rests on a THREE-POINT estimate with a small second
difference (d21 = −1.499, d32 = −0.138 on values ≈ −164). **A 3-point triple cannot
distinguish genuine super-2nd-order convergence from a PRE-ASYMPTOTIC artefact** of
near-cancelling leading error terms at these three meshes. The comfortable reading — "the
scheme superconverges, our band was too tight" — is the flattering one and **is not
supported by three points.**

**R3's single change: add a fourth, finer level L4 = 320×320 (r = 2).** This lets the
order be read on the **FINEST triple L2/L3/L4** — the one closest to the asymptotic range —
and a **4-point diagnostic** report whether the observed order is settling toward the
nominal 2 as h → 0. **Nothing else changes** (comparator gate constants, case inputs and
both R1/R2 rulings are byte-identical to R2's frozen package; only the driver's level set
and the running-total cap change — see §8).

## 3. The gate — UNCHANGED from R2, both limbs REQUIRED, band NOT widened

- **Graded functional:** `u_x` at the cavity geometric centre (1.0, 0.5), `cellPoint`
  interpolation (load-bearing — the default containing-cell sample shifts location between
  meshes and pollutes the order; R1 §9 caught this).
- **Both limbs REQUIRED (as R2):**
  1. observed order **p ∈ [1.0, 3.0]**, AND
  2. fine-grid **GCI ≤ 5 %** (Fs = 1.25).
- **The band FREEZES BYTE-IDENTICAL to R2** (verified: `P_OBS_LO 1.0`, `P_OBS_HI 3.0`,
  `GCI_FINE_MAX 0.05`, `RESID_FLOOR 1.0e-6`, `FS 1.25`, `R_REFINE 2.0`, `GATE_POINT (1.0,0.5)`
  are the same source lines in `grade_vmfl054_r3.py` as in the R2 comparator). **THE BAND IS
  NOT WIDENED** — widening [1.0, 3.0] now, having seen p = 3.4, would select the one gate
  that turns a `GATE FAIL` into a pass (gate-fitting, rule 2; L-487 anti-circularity).
- **Physical justification for [1.0, 3.0] (unchanged, restated so it is on the record BEFORE
  compute):** the formal order of the discretisation is 2; a driven cavity carries corner
  singularities that can DEPRESS the observed order below 2. So [1.0, 3.0] brackets the
  nominal 2 with generous margin on BOTH sides. A p ABOVE 3.0 is a `GATE FAIL`, not a
  band-widening trigger.

## 4. The graded-triple selection rule (STATED BEFORE ANY RUN — anti-fitting)

- **The graded triple is FIXED as the three FINEST levels: `GRADED_TRIPLE = (L2, L3, L4)`.**
  Named here, before compute, by the physics rationale (the finest triple is nearest the
  asymptotic range), NOT chosen after the run from whichever candidate converges.
- **NO fallback search.** The comparator does NOT try {(L1,L2,L3), (L2,L3,L4)} and grade
  whichever converges — that would be selecting the triple after seeing the answer
  (gate-fitting, rule 2). If the fixed finest triple L2/L3/L4 is **not CONVERGING** (rule 5),
  the verdict is **`NOT A RESULT`**; there is no rescue to a coarser triple.
- **The 4-point diagnostic is DIAGNOSTIC ONLY — it moves NO gate quantity.** It reports
  the coarse-triple order p(L1,L2,L3), the fine-triple order p(L2,L3,L4), and whether the
  fine triple's order is nearer the nominal 2 than the coarse triple's (`settling_toward_2`).
  This is what disambiguates a real >2 order from a pre-asymptotic artefact — but the
  VERDICT rests on the graded finest triple alone.

## 5. Roache triple gating (rule 5) and strict completion (rule 4), written in a-priori

- **Rule 5, in order:** (1) any of L1–L4 not iteratively converged (final Ux/p initial
  residual ≥ `RESID_FLOOR` 1e-6) → `NOT A RESULT`; (2) graded triple L2/L3/L4 not
  `CONVERGING` (DIVERGENT / OSCILLATORY / STAGNANT / EXACT) → `NOT A RESULT`, value and
  triple state printed; (3) `CONVERGING` → gate evaluated (§3). The gate can only turn a
  reached/failed gate INTO `NOT A RESULT`, never the reverse. GCI at Fs = 1.25; never quoted
  when the three graded values are not monotone.
- **Rule 4 (strict completion), per level:** solver `rc = 0` (persisted as `RUN_RC`), an
  `End` line AND no `FOAM FATAL`, latest-time fields present, the **age guard** (fields
  NEWER than the case's own `0/U`), and iterative convergence. Any failed limb REFUSES
  (exit 2), never grades a partial run. **`last time == endTime` and the `ExecutionTime`
  count are DELIBERATELY INAPPLICABLE** to a `residualControl`-terminated steady solve (it
  stops BEFORE `endTime`) and are not checked — same declared basis as R1/R2, VMFL038/VMFL063.

## 6. Guards (all four REFUSE with exit 2; validated by `--selftest` — §9)

- **(1) Planted-zero (rule 3), on BOTH gate-bearing readers** — the probe-file gate reader
  and the U-field reader. A known delta is planted into a COPY, read back, refuse if unseen.
  **L-487 compliance:** the gate reduction is a DIRECT read of one scalar (u_x at one point)
  and of a per-cell field list — neither is a sum/mean/ptp/max over a set, so neither cancels
  nor absorbs a plant; the plant is the value itself, read back by identity, and the U-field
  arm checks EVERY element moved.
- **(2) Strict completion (rule 4)** — §5.
- **(3) Known-bad input** — a corrupted probe row is fed to the reader, which MUST refuse.
- **(4) Gate-blind physical range (new in R3)** — centre `u_x` must be finite, non-collapsed
  (|u_x| ≥ 1.0) and bounded (|u_x| ≤ 800 = 2× the 400 m/s lid speed). Outside → REFUSE. This
  references NEITHER the order band NOR the GCI, so it cannot fit the gate; it only rejects a
  garbage read (a NaN-parsed-as-0, a units error, a blow-up) before it can masquerade as a
  grid-convergence datum.

## 7. Cost (rule 12)

- **Ranks:** 1 (serial, matching R1/R2 for a clean r = 2 comparison).
- **Grid levels and per-level compute (L1–L3 MEASURED in R2; L4 ESTIMATED from the §9 smoke):**

  | Level | NX×NY | cells | core-min |
  |---|---|---|---|
  | L1 | 40×40 | 1 600 | ~0.02 (R2 measured 0.0167) |
  | L2 | 80×80 | 6 400 | ~0.13 (R2 measured 0.1333) |
  | L3 | 160×160 | 25 600 | ~1.1 (R2 measured 1.1) |
  | L4 | 320×320 | 102 400 | **~15 ESTIMATED** (§9: 0.18 s/iter; convergence trajectory projects ~4 900 iters → ~882 s ≈ 15 core-min) |

- **Pre-registered estimate for the graded run (all four levels):** **~16.3 core-min.**
- **Running-total cap in the driver: `CAP_CORE_MIN = 60` core-min** (~4× margin above the
  ~16.3 estimate; an overrun STOPS the run, rc 124 — rule 12). Well under the $25/run
  pre-authorisation: 16.3 core-min = 0.272 core-h × $0.0513 ≈ **$0.014 DERIVED** (60-core-min
  cap ≈ $0.051 DERIVED).
- **`cost_basis`:** core-minutes = wall_s × ranks ÷ 60, MEASURED from the driver's own
  timing. Any dollar figure is DERIVED at **$0.0513/core-h, owner-stated, NOT measured** —
  this box cannot read its own billing (COMPUTE_BUDGET_CHARTER §5). The completion report
  will compare actual vs this estimate per rule 12 (`docs/COST_CALIBRATION.md`).

## 8. Solver / config path and buildability (FIX-UNTIL-RUNS, §2ay)

- **Solver:** `simpleFoam` (OpenFOAM v2606), steady laminar SIMPLEC (`consistent yes`),
  `bounded Gauss linear` convection, `Gauss linear corrected` diffusion, Re = 400 (ν = 1,
  ρ = 1, μ = 1), 2-D. **The case already runs to rc = 0 on this solver** (R2 graded L1/L2/L3
  clean). L4 is the SAME case on a finer mesh — **no new capability is needed.**
- **Mesh:** `blockMeshDict.template` with uniform `simpleGrading (1 1 1)`; `__NX__/__NY__`
  substituted per level by `run_vmfl054_r3.sh`. The r = 2 family doubles both counts each
  level, so L4 = 320×320 is a clean, systematic halving of every cell dimension.
- **L4 buildability CONFIRMED (§9):** `blockMesh` at 320×320 → 102 400 cells, `checkMesh`
  **Mesh OK** (max non-orthogonality 26.5, average 15.7 — well inside the MESH_STANDARD
  bands), and a `residualControl` solve showed MONOTONE convergence with no stall or
  divergence, projected ~15 core-min — ~4× under the 60 core-min cap (§9).

## 9. Disclosed scratch feasibility (NOT the freeze; sets NO gate/band)

Run in the scratchpad, OUTSIDE `verification/runs/`, so it cannot disarm rule 4's age guard;
**kept ANSWER-BLIND — the converged centre `u_x` was never read**, so the graded quantity is
unknown to the drafting lane at freeze (rule 2 anti-fitting, belt-and-braces):

1. **Comparator `--selftest`: 16/16 arms ALL PASS** — probe plant, U-field plant, known-bad
   refusal, four gate-blind physical-range arms (good + collapsed + blow-up + NaN), Roache
   converging/oscillatory classifier, two 4-point diagnostic arms (settling + persistence),
   and five strict-completion arms (good + no-End + missing-field + age-guard + rc≠0), each
   BAD arm visibly refusing exit 2.
2. **L4 mesh smoke:** `blockMesh` 320×320 → 102 400 cells, `checkMesh` **Mesh OK**, 0.18
   s/iter over the first 50 (non-converging, residualControl-disabled) iterations.
3. **L4 convergence smoke (answer-blind, cap de-risking):** a `residualControl` L4 solve
   was observed converging MONOTONELY with NO stall or divergence — Ux/p initial residuals
   fell steadily through ~1e-6 (at ~2 950 iters) toward the residualControl floors (p 1e-8,
   U 1e-9), on a trajectory projecting ~4 900 iters ≈ ~15 core-min at 0.18 s/iter, i.e. ~4×
   under the 60 core-min cap. **The probe `u_x` was deliberately NOT read** (answer-blind),
   so this smoke sets no gate. It DE-RISKS the cap; the graded convergence-to-floor is
   confirmed on the queue-launched GRADED run (which the comparator's rule-4 iterative-
   convergence limb enforces at exit 2), NOT on this smoke.

## 10. The lab's PREDICTION (stated in advance, rule 2)

**Primary expectation: the order limb persists in FAILING on the finest triple L2/L3/L4** —
i.e. the observed order stays ABOVE 3.0, so the verdict remains `GATE FAIL`. Reasoning: R2's
triple was monotone (not oscillating) with a steadily shrinking, same-sign second difference;
that is the signature of a value approaching an asymptote fast, and there is no mechanism in a
smooth interior functional at Re = 400 for a driven cavity to *raise* the observed order back
toward 2 on refinement — corner singularities depress order, they do not lift it. If p > 3.0
persists on the FINEST triple, that is a **genuine finding that the [1.0, 3.0] ceiling may be
mis-specified for this functional**, and the "is the ceiling right?" question is **ESCALATED
to the supervisor** — it is NOT rescued here by widening the band (rule 2).

**Named alternatives, and their honest verdicts:**
- **p settles into [1.0, 3.0] on L2/L3/L4 with GCI ≤ 5 %** → the R2 result was a coarse-grid
  pre-asymptotic artefact; verdict `GATE REACHED` (see the PASS note below).
- **The finest difference collapses toward machine level** (d43 ≈ 0) → triple `EXACT` →
  `NOT A RESULT` (rule 5). This is a real risk: values ≈ −164.75 with d32 = −0.138 already,
  so d43 may be small enough to lose significance — a possibility the register narration must
  respect, not paper over.
- **The finest triple is non-monotone** (L4 overshoots) → `OSCILLATORY`/`DIVERGENT` →
  `NOT A RESULT`.

**PASS vs GATE REACHED — a supervisor decision, flagged, NOT decided in these bytes.** The R3
comparator, like R1/R2, **NEVER emits `PASS`**: the external Darr & Vanka (1991) validation
limb is DEFERRED (the manual states the reference only as plotted figures) and the
BC-direction modelling choice is CAPPED at `GATE REACHED` by the standing R1 Ruling 1. So the
ceiling this round is `GATE REACHED`, even if the grid-convergence gate is fully met. **The
drafting lane deliberately did NOT promote GATE REACHED → PASS**, because promoting it would
claim a credential the case cannot earn while the D&V limb is deferred and the BC cap stands —
that is a gate/label question reserved to the supervisor (and ultimately to a ruling), not a
lane's to widen. **Flagged for the §3 read:** if the supervisor rules the grid-convergence
gate alone may be a PASS for this round, that is a one-line comparator change to make BEFORE
the freeze commit; as frozen, it caps at `GATE REACHED`.

## 11. Grading path and what remains

- **Comparator:** `cases/ansys_verification/VMFL054-R3/grade_vmfl054_r3.py` (blob pinned §0).
- **Driver:** `run_vmfl054_r3.sh` (blob pinned §0). **Case inputs:** `case/` (§0).
- **After the freeze commit** (by the supervisor's §3 check-4 diff re-read): a fresh run root
  `verification/runs/ansys_verification/VMFL054-R3/` and a top-level queue entry. **THE
  LAUNCH IS HELD** — a launch-permission block is on Sanaa's desk (rule 9, no laundering).
  **This lane froze nothing, launched nothing, graded nothing, and wrote no queue entry.**
