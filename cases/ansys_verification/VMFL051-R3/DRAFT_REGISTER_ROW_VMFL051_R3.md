# DRAFT REGISTER ROW — VMFL051-R3

**DRAFT ONLY. NOT APPENDED, NOT COMMITTED.** Written by an `ansys-lane-opus`
2026-09-10 at the supervisor's instruction. **This lane deliberately did not touch
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`** — a VMFL063-R3 row
is being drafted for the same append-only file by another lane, and two lanes
appending concurrently is how a row gets lost. The supervisor appends both,
sequenced.

> ## ⚠ ROW NUMBER IS A PLACEHOLDER — `## Row #NN`
>
> **Do not use the number below as written.** Assign it at append time from the
> **MAXIMUM EXISTING** `## Row #` in the register, **in the same shell invocation as
> the append** (rule 11: the maximum, never a count — the count of headings and the
> highest number are different figures, and the `.tsv` is a derived view that lags).
> The VMFL063-R3 row was still being drafted when this file was written, and **it
> has since landed as `## Row #76`** — observed by this lane at 2026-09-10, which is
> exactly the reason this number is a placeholder rather than a value.
>
> **Measured state as this note was last touched: maximum existing `## Row #` = 76**
> (`#75` VMFL046-R9-REGRADE, `#76` VMFL063-R3), so `NN` is **expected to be 77**.
> **That is an expectation, not a value.** Peers commit constantly; re-derive it in
> the append invocation and assert the number is unused before writing.

---

## Row #NN — VMFL051-R3 — Isentropic Expansion Around a Convex Corner (Prandtl–Meyer), mass-flux-weighted spatial reduction (VM2026R1 pp. 165–166) — **`PASS`**

> # THE VERDICT AND ITS CAVEAT, TOGETHER
>
> **`PASS`** — the frozen gate is `|M_lab − 3.2370| / 3.2370 ≤ 0.5000 %` **at the
> finest converging level**, and the measured deviation is **0.490891 %**.
>
> **THIS PASS IS REAL AND IT IS THIN, AND THE THINNESS IS PART OF THE CREDENTIAL,
> NOT A FOOTNOTE TO IT.** Three things a reader must be told in the same breath as
> the word PASS:
>
> 1. **HEADROOM IS 0.009109 PERCENTAGE POINTS.** The result consumes **98.18 %** of
>    the band and passes by **1.82 %** of it. A shift of one part in eleven thousand
>    in `M_lab` would flip this verdict.
> 2. **THE GRID-CONVERGED LIMIT IS OUTSIDE THE BAND.** Richardson extrapolation to
>    zero grid spacing gives **3.2207146227**, deviating **0.503101 %** — **outside
>    ±0.5 %**. The gate as frozen is evaluated **at the finest converging level**
>    (`PREREGISTRATION.md:140` and `:637`, verified by this lane at source), so the
>    PASS stands **exactly as registered** and nothing whatever is being
>    reinterpreted after the fact. But the honest direction of travel must be
>    stated: **a finer grid moves this case OUT of the band, not further in.**
> 3. **THAT IS NOT A NUMERICS PROBLEM — IT IS A MODEL OFFSET.** `GCI(fine)` is
>    **0.0153 %**, **32.0× smaller** than the 0.4909 % gap to the reference. The
>    discretisation uncertainty cannot explain the offset. The **exact-gas
>    diagnostic** corroborates it independently: 3.2355411372, deviation
>    **−0.446024 %**, **outside its own ±0.25 % band**.
>
> **What that adds up to: the solver is converging cleanly to an answer that is
> genuinely, if slightly, offset from the manual's reference — and the frozen band
> is wide enough to admit the finest-level value and narrow enough to exclude the
> continuum limit.** Read this row as a PASS that is *earned and narrow*, never as a
> demonstration that the lab's solver reproduces this reference.

### Provenance and freeze (rule 2) — re-verified independently by this lane

| object | value |
|---|---|
| frozen pre-registration | `cases/ansys_verification/VMFL051-R3/PREREGISTRATION.md`, freeze commit **`5b9b086e`** |
| grading path | `cases/ansys_verification/VMFL051-R3/grade_vmfl051_r3.py`, blob **`fedb1088bfdc6be028743246e0da5b404c6749b2`** |
| freeze chain | disk == blob at `5b9b086e` == blob at HEAD — **all three equal**, re-hashed by this lane |
| grading invocation | run by the supervisor, asserting disk == freeze blob **in the same shell invocation as the grade** (L-223) |
| `grade_rc` | **0** |
| verdict artifacts | `verification/runs/ansys_verification/VMFL051-R3/GRADING_VMFL051_R3.json`, `.../COST.txt`, committed at **`fec84d23`** |
| manual | VM2026R1 **pp. 165–166**, title-page verified under rule 15 and carried forward |

### The gate

| | |
|---|---|
| gate quantity | `M_lab` — **mass-flux-weighted `p0/p` Mach** on the frozen cross-plane `postExpPlane`, time-meaned over the last 50 % of rows |
| reference | **3.2370** (VM2026R1) |
| band | **±0.5000 % relative, at the finest converging level** — carried from R2 **unchanged** (L-487) |
| measured (`L3`, finest converging) | **3.2211098484** |
| deviation | **−0.490891 %** |
| **verdict** | **`PASS`** — `0.490891 % ≤ 0.5000 %` |
| headroom | **0.009109 pp** (98.18 % of the band consumed) |

### Roache triple gating (rule 5) — `CONVERGING`, and every level settled

| level | grid | cells | gate-plane faces | `M_lab` | settledness | vs tol 5.0e-04 |
|---|---|---|---|---|---|---|
| L1 | 120×52 | 6 240 | 6 | 3.2305059776 | 7.445e-06 | settled |
| L2 | 240×104 | 24 960 | 11 | 3.2226818021 | 3.058e-05 | settled |
| L3 | 480×208 | 99 840 | 23 | **3.2211098484** | 2.111e-05 | settled |

```
d32 = 7.824176e-03   d21 = 1.571954e-03   R = 0.200910   ->  0 < R < 1, CONVERGING
p = 2.3154   r = 2.0   Fs = 1.25   GCI(fine) = 0.0153 %   Richardson = 3.2207146227
```

Every level is iteratively converged and plateaued (rule 5 step 1 passes), the
triple is `CONVERGING` (step 2 passes), and the value lies inside the
pre-registered band (step 3) — **so `PASS` is reached in rule 5's own order, with
no step skipped.** The GCI is quoted because and only because the three values are
monotone.

### ⚠ A CAVEAT THE SUPERVISOR'S BRIEF DID NOT NAME, RECORDED BECAUSE THE CREDENTIAL IS THIN

**The `CONVERGING` state is plane-dependent, and on this run the neighbouring
diagnostic plane is `OSCILLATORY`.** Computed by this lane from the same committed
JSON, on the same three solves:

| reduction | L1 | L2 | L3 | R | state |
|---|---|---|---|---|---|
| **gate plane** (`postExpPlane`, frozen) | 3.2305059776 | 3.2226818021 | 3.2211098484 | **+0.2009** | **`CONVERGING`** |
| diagnostic plane (cross-check only, gates nothing) | 3.2271098604 | 3.2211023620 | 3.2266530555 | **−0.9240** | **`OSCILLATORY`** |
| short-window variant (25 % window) | 3.2305134230 | 3.2227123781 | 3.2210887416 | **+0.2081** | `CONVERGING` |

**None of this disturbs the verdict, and it is not offered as an objection.** The
gate plane is the **frozen** one; the diagnostic plane gates nothing by
registration; and the plane-consistency check passes comfortably at L3
(`|diag − gate| / gate = 0.1721 %` against its 1.0 % tolerance). The short-window
variant converging at essentially the same rate (R +0.2081 vs +0.2009) is a
genuine robustness signal for the **temporal** reduction.

**But a reader of a PASS that consumes 98.18 % of its band is entitled to know that
a differently-placed plane on the same solves does not converge monotonically.**
It bounds how much this row should be leaned on: it is a credential for **this
reduction on this plane**, not a general statement that the case is grid-converged
under any reasonable spatial reduction.

### What the contribution actually was — the lever, and the two rows before it

This case has now been run three times, and **the first two produced no number the
lab could stand behind:**

| attempt | outcome | why |
|---|---|---|
| VMFL051, run 1 | **`NOT A RESULT`** | — |
| **VMFL051-R2**, **Row #73** | **`NOT A RESULT`** | the triple was **`OSCILLATORY`** (R = −1.184). **Its gate VALUE would have passed, at −0.233 %** — and rule 5 discarded it anyway, because a row whose triple is not `CONVERGING` is `NOT A RESULT` **whatever its value**. |
| **VMFL051-R3** (this row) | **`PASS`** | see below |

**R3 changed exactly ONE lever: the SPATIAL reduction** — an unweighted volume
average became a **mass-flux-weighted `p0/p` Mach on a frozen downstream plane**.
R2's **temporal** reduction was kept unchanged. That single change turned a
non-monotone triple into a cleanly `CONVERGING` one at **p = 2.3154**.

> **THE PASS IS DOWNSTREAM OF THE REDUCTION, AND THE ROW SAYS SO RATHER THAN
> CLAIMING THE SOLVER GOT BETTER.** Nothing about the physics, the mesh family, the
> solver or the gate moved between R2 and R3. What moved was **how the field is
> reduced to one number**, and that is what converted an ungradeable triple into a
> gradeable one. Row #73's `NOT A RESULT` was correct when written and remains
> correct; it is not superseded, amended or struck, and **neither is Row #71**.
>
> Note the shape of it, because it is the most useful thing this case has taught:
> **R2's value was closer to the reference (−0.233 %) than R3's (−0.491 %), and R2
> is still the row with no result while R3 is the row with a PASS.** A better-looking
> number under a reduction that will not converge is worth less than a worse-looking
> number under one that will.

### The planted controls (rule 3) — all three fired on real data, with PROPER subsets

| control | subject | plant | planted into | seen | expected |
|---|---|---|---|---|---|
| **PZ-1** | the plane `.dat` reader | 1.234e-03 | **1 679 of 3 357** window rows | **6.17184e-04** | 6.17184e-04 |
| **PZ-2** | the field reader | 7.77e-02 | **49 920 of 99 840** cells | **3.885e-02** | 3.885e-02 |
| **PZ-3** | the reference construction | 5 deg | (identity leg 15 deg) | delta **0.300027** | fired |

**Each plant covers a PROPER SUBSET of its reduction set, which is the point.** A
plant spanning the whole set is a rigid translation that a mean cannot see —
the CANCELLATION defect this family has already paid for. PZ-1 at 1 679/3 357 and
PZ-2 at 49 920/99 840 are each almost exactly half, and both readers recovered
exactly the half-magnitude the subset implies. **A reader shown able to see a
non-zero.**

### Cost (rule 12)

**9.6333 core-min MEASURED** (578 wall s × 1 rank ÷ 60) against a **9.8 core-min**
point estimate and a **28 core-min** running-total cap — **ratio 0.983, no
overrun, 34 % of cap.** **$0.0082 DERIVED, NOT MEASURED** at c7a.4xlarge
$0.0513/core-h, owner-stated / reported-by-owner (`COMPUTE_BUDGET_CHARTER` §5 — the
box cannot read its own billing). Calibration row drafted alongside this file.

### Context — recorded, and gating nothing

Ansys's own published values, **for context only and never the gate**: Fluent
**3.2316** (ratio 0.9980), CFX **3.2354** (ratio 0.9995). The lab's 3.2211098484
sits below both. **These numbers do not appear in any gate, band or threshold and
must never be cited as agreement.**

### What this row refuses to claim

| | |
|---|---|
| that the lab reproduces the manual's reference | **NO.** It lands 0.490891 % below it and consumes 98.18 % of the band doing so. |
| that the case is grid-converged **into** the band | **NO — the opposite.** The Richardson limit 3.2207146227 is **outside** at 0.503101 %. A finer grid moves it out. |
| that the offset is a discretisation artefact | **NO.** GCI(fine) 0.0153 % is 32.0× too small to explain a 0.4909 % gap, and the exact-gas diagnostic sits outside its own 0.25 % band. |
| that the case converges under any spatial reduction | **NO.** The diagnostic plane on these same solves is `OSCILLATORY` (R = −0.9240). This credential is for **this** reduction on **this** frozen plane. |
| that R2 was wrong, or is superseded | **NO.** Row #73 stays `NOT A RESULT`; Row #71 is untouched. R2's triple genuinely did not converge. |
| that the solver improved between R2 and R3 | **NO.** One lever moved — the spatial reduction. Physics, mesh, solver and gate are unchanged. |
| that Fluent/CFX agreement supports this row | **NO.** Context only; they gate nothing. |
