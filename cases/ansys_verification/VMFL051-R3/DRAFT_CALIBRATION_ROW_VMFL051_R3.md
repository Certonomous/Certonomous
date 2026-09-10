# DRAFT CALIBRATION ROW - VMFL051-R3

**DRAFT ONLY. NOT APPENDED, NOT COMMITTED.** Written by an `ansys-lane-opus`
2026-09-10. **This lane did not touch `docs/COST_CALIBRATION.md`.** The supervisor
appends, sequenced against the other lane's VMFL063-R3 work.

## How to append it

1. **Regenerate the row id in the same shell invocation as the append**, so it
   cannot collide with a peer's -- the `id` cell is a placeholder `C-<STAMP>-<HASH>`.
   Live convention: `C-` + UTC `%Y%m%dT%H%M%S.%f` + `Z-` + 8 hex. Assert the
   generated id is absent from the file before writing.
2. **Append at the foot of the table.** Append-only: an existing row is never
   edited, and a correction is a new row naming the row it corrects.
3. **Column contract, read from the file rather than assumed:** the header at
   `docs/COST_CALIBRATION.md:77` declares **10 columns**, and the rows at
   `:514-515` carry 10 under both a naive and an escape-aware split. **The row
   below is verified 10 by both, and contains no literal pipe at all** -- so
   neither parse can miscount it. (The peer row at `:513` reads 13 under a naive
   split because of unescaped pipes inside `"(U/T/h/k/omega)"`-style prose; that
   is theirs, and it is left alone.)
4. **Prove append-only afterwards:** the pre-append bytes must be a byte-exact
   prefix of the resulting file.

## The row, ready to paste

```
| C-<STAMP>-<HASH>   <-- PLACEHOLDER: regenerate at append time, in the same invocation | 2026-09-10 | ansys-verification | **VMFL051-R3** (Ansys VM2026R1 pp. 165-166, isentropic expansion around a convex corner / Prandtl-Meyer; r=2 triple L1 120x52 / L2 240x104 / L3 480x208 = 6 240 / 24 960 / 99 840 cells, all SERIAL 1 rank). Prereg FROZEN at **`5b9b086e`**; grading path `grade_vmfl051_r3.py` blob **`fedb1088bfdc6be028743246e0da5b404c6749b2`**, disk == freeze-commit blob == HEAD blob (re-hashed independently by a second lane), asserted in the SAME shell invocation as the grade (L-223). `grade_rc = 0`. **RUNG VERDICT `PASS`** -- triple `CONVERGING` (R 0.200910, p 2.3154, Fs 1.25, GCI(fine) 0.0153 %), every level settled (7.445e-06 / 3.058e-05 / 2.111e-05 against tol 5.0e-04), gate `abs(M_lab - 3.2370) / 3.2370 = 0.490891 % <= 0.5000 %` at the finest converging level. **THE PASS IS THIN AND THIS LEDGER SAYS SO RATHER THAN LEAVING IT TO THE REGISTER: headroom 0.009109 pp, 98.18 % of the band consumed, and the Richardson limit 3.2207146227 deviates 0.503101 % -- OUTSIDE the band, so a FINER grid moves this case OUT.** GCI(fine) 0.0153 % is 32.0x too small to explain the 0.4909 % gap, so the offset is a MODEL offset, corroborated by the exact-gas diagnostic at -0.446024 %, outside its own 0.25 % band. Verdict artifacts `GRADING_VMFL051_R3.json` + `COST.txt` committed at `fec84d23`. Predecessors unamended: VMFL051 run 1 `NOT A RESULT`; VMFL051-R2 Row #73 `NOT A RESULT` on an OSCILLATORY triple (R -1.184) despite a gate value that would have passed at -0.233 %. | **9.8 core-min** point estimate; **cap 28 core-min** running total (`timeout` = 28 x 60 / ranks), at `cases/ansys_verification/VMFL051-R3/PREREGISTRATION.md` §6. **BASIS: MEASURED, NOT GUESSED** -- R2's total of 9.8 core-min (588 wall s serial, `verification/runs/ansys_verification/VMFL051-R2/COST.txt`) for the **BYTE-IDENTICAL SOLVE** on this same box, plus a negligible-function-object assumption. Derived **$0.0084** at $0.0513/core-h -- **DERIVED, NOT MEASURED**. Under the $25 pre-authorisation. | **9.6333 core-min MEASURED** (578 wall s x 1 rank / 60, from the run's own `COST.txt`: total_wall_s=578, ranks=1, total_core_min=9.6333) = 0.16056 core-h = **$0.0082 DERIVED, NOT MEASURED** at $0.0513/core-h, owner-stated / reported-by-owner (`COMPUTE_BUDGET_CHARTER` §5 -- the box cannot read its own billing). **WITHIN the 28 core-min cap** (34.4 % consumed) -- no overrun, no cap-stop. | **= gross (9.6333).** **NO STALL** -- total wall 578 s is far below the charter §2 3600-s figure and no single level approaches it. **WASTE: 0.0000 core-min, and this field is STATED rather than omitted** (`COMPUTE_BUDGET_CHARTER` §6): all three levels ran to `endTime` 0.007, all three settled, the triple graded, and the spend bought exactly the verdict it was registered to buy. No superseded or discarded spend on this rung. | **0.983** (9.6333 / 9.8). **UNDER the estimate, by 1.7 %.** | **NEITHER A MISS NOR LUCK, AND THE ATTRIBUTION IS THE TRANSFERABLE LESSON. (1) NO WASTE COMPONENT: 0.0000 core-min, stated explicitly in the cleaned column rather than left blank. (2) NO CONTENTION COMPONENT, asserted NARROWLY rather than by omission:** the run took 578 wall s against a 588 wall s measured basis on the same box -- it came in 1.7 % FASTER than its own anchor, and a contended run does not beat its uncontended basis, so there is no degradation to attribute. **However, no per-process CPU-vs-wall ratio was recorded in this rung's `COST.txt`, so a descheduling channel is NOT separately quantified; that absence is stated rather than papered over**, and it is bounded above by the 1.7 % total gap, which is too small to conceal one. **(3) THE WHOLE OF THE 1.7 % IS MODEL RESIDUAL, AND THE REASON IT IS ONLY 1.7 % IS THE BASIS: THE ESTIMATE WAS MEASURED-ANCHORED, NOT REASONED.** It was taken from R2's total for a solve byte-identical in mesh, solver, schemes and `endTime`, on this same box -- R3 moved only the SPATIAL REDUCTION, a post-processing lever that costs nothing at solve time. **THE TRANSFERABLE LESSON: WHEN A SUCCESSOR CHANGES ONLY A POST-PROCESSING LEVER, THE PREDECESSOR'S MEASURED TOTAL IS THE ESTIMATE, AND IT LANDS INSIDE 2 %. THIS FAMILY'S BAD ESTIMATES ARE THE ONES THAT APPLIED A JUDGEMENT FACTOR TO A PREDECESSOR'S TOTAL INSTEAD OF USING THE TOTAL ITSELF** -- compare VMFL046-R8, where a flat ~2.0x start-from-rest factor on R5's totals produced 1.484x with the miss growing monotonically under refinement. **A measured anchor on an unchanged solve beat a reasoned factor by roughly thirty-fold in ratio error: 0.017 against 0.484.** The corollary is discipline, not luck -- the estimate was cheap to make correctly BECAUSE the lever that moved was identified precisely enough to know the solve itself was unchanged. | `cases/ansys_verification/VMFL051-R3/DRAFT_REGISTER_ROW_VMFL051_R3.md` (register row draft; its row NUMBER is a placeholder, assigned at append from the MAXIMUM existing `## Row #` in the same invocation, rule 11); verdict artifacts `verification/runs/ansys_verification/VMFL051-R3/GRADING_VMFL051_R3.json` and `.../COST.txt`, both committed at `fec84d23`; frozen prereg `cases/ansys_verification/VMFL051-R3/PREREGISTRATION.md` §6 at freeze commit `5b9b086e`; grading path `cases/ansys_verification/VMFL051-R3/grade_vmfl051_r3.py` blob `fedb1088bfdc6be028743246e0da5b404c6749b2`; measured basis `verification/runs/ansys_verification/VMFL051-R2/COST.txt` |
```

## What the row asserts, in short

| | |
|---|---|
| predicted | **9.8 core-min** (cap 28), **measured-anchored** on R2's byte-identical solve |
| actual | **9.6333 core-min MEASURED** (578 wall s x 1 rank / 60) |
| cleaned | **= gross (9.6333)**; no stall |
| **ratio** | **0.983** -- under the estimate by 1.7 % |
| waste | **0.0000 core-min -- stated, not omitted** |
| contention | **no component, asserted narrowly** -- the run beat its own uncontended anchor; the absence of a CPU-vs-wall figure in `COST.txt` is disclosed rather than glossed |
| dollars | **$0.0082 DERIVED, NOT MEASURED** at $0.0513/core-h |
| lesson | when a successor moves only a **post-processing lever**, the predecessor's **measured total** IS the estimate and it lands inside 2 % -- against 1.484x for VMFL046-R8's reasoned factor |

## Verified by this lane before drafting

Every figure above was recomputed from the committed
`GRADING_VMFL051_R3.json` and `COST.txt` rather than taken on trust: `d32`, `d21`,
`R`, `p`, `GCI(fine)`, the Richardson extrapolation, the gate deviation, the
Richardson deviation, the headroom and the ratio all reproduce **to the quoted
digit**. The freeze chain (disk == blob at `5b9b086e` == blob at HEAD) was
re-hashed. The claim that the gate is evaluated **at the finest converging level**
was checked at source in the frozen pre-registration (`:140`, `:637`) because the
whole "nothing is reinterpreted after the fact" defence rests on it.
