# PRE-REGISTRATION — VMFL063: Separated Laminar Flow Over a Blunt Plate

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — page 193
(Test Case and geometry), page 193 Table .63.1 (Results Comparison for Ansys Fluent)
and Table .63.2 (Ansys CFX).** Sidecar title-page verified against the PDF beside it
under `CLAUDE.md` rule 15 on 2026-08-28: the sidecar's first page and the PDF's page 1
both read *"Ansys Fluid Dynamics Verification Manual / ANSYS, Inc. / Southpointe /
2600 Ansys Drive / Canonsburg, PA 15317 / Release 2026 R1 / March 2026"*, and
`pdfinfo` reports `Title: Fluid Dynamics Verification Manual`, `Pages: 290`,
`Creator: DocBook XSL Stylesheets V1.76.1`, `Producer: XEP 4.22`. Not by filename,
file type or hash.

Drafted by `ansys-lane-opus`, **2026-08-28**, for the supervisor to freeze. This file
is a frozen file under `CLAUDE.md` rule 6 from the moment its commit lands: departures
are dated addenda at the foot, never edits above.

**FIRST REGISTRATION OF THIS CASE.** VMFL063 has **no** row in
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (`grep -c VMFL063`
returns **0** at 2026-08-28T16:21:53Z) and no prior VMFL063 case directory,
comparator, launcher or run root has ever existed. It is not a re-registration and it
supersedes nothing.

---

## 0. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**NOT YET RUN. NO VMFL063 SOLVER HAS EVER STARTED, ANYWHERE ON THIS BOX.** The gate,
the bands, the ceilings, the mesh family, the cap and the named outcomes below are
therefore predictions, which is the entire evidentiary content of this document.

Checked at **2026-08-28T16:10:08Z** and again at **16:21:53Z**, and stated so a reader
can re-run each check rather than take it on trust:

| condition | how it was checked | result |
|---|---|---|
| the run root does not exist | `test -e verification/runs/ansys_verification/VMFL063` | **false** |
| it is absent from the runs tree listing | `ls verification/runs/ansys_verification/` — 45 entries, none of them `VMFL063` | **absent** |
| no VMFL063 artefact exists anywhere under the repository or `/home/ubuntu/certonomous-runs/` | `find ... -iname '*063*'` outside the new case directory | **only unrelated frame/log filenames containing the digits 063; zero VMFL063 artefacts** |
| the register carries no VMFL063 row | `grep -c VMFL063` on the register | **0** |
| this case directory holds no `0/` or numeric time directory | the case directory contains only `case/`, this file, the comparator and the launcher | **no answer on disk** |

**There is no VMFL063 number on this box for any band, ceiling or window in this
document to have been fitted to.**

**Amendments before first compute are legal and must restate this condition and how it
was checked, naming the run directory that does not exist. After first compute the
gates close: dated addenda only, and no addendum may alter a gate, threshold, band,
cap or ceiling.**

---

## 1. THE TEN-LINE FORM

```
1.  CASE       : VMFL063 -- Separated laminar flow over a blunt plate, manual p.193.
                 Solver = simpleFoam (OpenFOAM v2606), steady incompressible laminar
                 SIMPLEC, 2-D Cartesian, half domain by symmetry about the plate
                 centreline. Re_2t = U*2t/nu = 0.0517*0.090/1.7894e-5 = 260.031.
2.  REFERENCE  : LR/(2t) = 4.0  -- manual Table .63.1 column "Target".
                 EXPERIMENTAL: J.C. Lane & R.I. Loehrke, "Leading Edge Separation from
                 a Blunt Plate at Low Reynolds Number", Trans. ASME Vol.102 pp.494-496,
                 1980 -- the manual's own cited Reference.
3.  CONTEXT    : Ansys Fluent 4.16 (Ratio 1.04), Ansys CFX 4.05 (Ratio 1.01).
                 CONTEXT ONLY. NEVER the gate, in this document or in the comparator.
4.  CEILINGS   : limb A (physics)      -> GATE REACHED   -- PASS is UNAVAILABLE
                 limb B (determinism)  -> PASS
                 ROW verdict = the WORST limb, so THE ROW CAN NEVER READ PASS and this
                 registration CANNOT produce a credential. Stated before compute.
5.  GATE (A)   : |LR/(2t) - 4.0| / 4.0 <= 0.10  at the FINEST level L3,
                 AND a CONVERGING Roache triple on LR/(2t) (CLAUDE.md rule 5).
6.  GATE (B)   : L1 and its twin L1D -- byte-identical inputs, second independent solve
                 -- must agree EXACTLY: same converged iteration count, sha256-identical
                 <t>/wallShearStress, <t>/U, <t>/p, and bitwise-equal LR.
7.  FAMILY     : three levels, r = 2, cells 5 760 / 23 040 / 92 160 (x4 per level;
                 all four block counts doubled). Plus L1D at L1's counts exactly.
8.  COMPLETION : CLAUDE.md rule 4 in full, with the age guard, adapted for a
                 residualControl-terminated steady solve (sec.6). Comparator REFUSES
                 (exit 2) on any failed clause rather than grading a partial run.
9.  CONTROLS   : planted zero in TWO stages on TWO channels (sec.8); cardinality guard
                 on every file read; cross-instrument agreement within 3 cell widths.
10. COST       : ESTIMATE 16 core-min, RANKS = 1. CAP 90 core-min, RUNNING TOTAL across
                 all four solves. An overrun STOPS the run (rule 12); endTime is never
                 reduced to fit a cap. cost_basis $0.0513/core-h, reported-by-owner.
```

---

## 2. THE CASE, EXACTLY AS THE MANUAL STATES IT

Manual p.193, quoted for the load-bearing numbers and reproduced without adjustment:

> *"The flow separation over a blunt leading edge in laminar flow is modeled. The flow
> separates and reattaches along the plate. The reattachment length predicted by the
> solvers is validated against experimental results. Due to symmetry, only half of the
> domain shown in Figure .63.1: Flow Domain (p. 193) is modeled. The Reynolds number
> based on plate thickness is 260."*

| quantity | manual value | in the frozen case files |
|---|---|---|
| density | 1 kg/m³ | `nu = mu/rho`; kinematic pressure, `rho = 1` |
| viscosity | 1.7894e-5 kg/m-s | `constant/transportProperties`: `nu 1.7894e-05` |
| plate thickness 2t | 90 mm | `TWO_T = 0.090`; plate top surface at `y = t = 0.045` |
| plate length | 1500 mm | outlet at `x = 1.5 m`, the plate's own end |
| inlet velocity | 0.0517 m/s | `0/U`: `fixedValue uniform (0.0517 0 0)` |
| Reynolds number | 260 | derived 260.031 — the comparator's `--selftest` checks this reproduces the manual's stated 260 to better than 2e-4 relative |

**The manual gives a DISCRETE TARGET, not a figure.** Table .63.1 is a numeric table
with a column headed *Target* and the single entry **4.0** for *Non-dimensionalized
Reattachment length (LR/2t)*. This is why VMFL063 was selected: the reference is a
citable number in the manual itself, not a curve to be digitised. (Contrast VMFL011,
whose reference exists only as Figure .11.2 and whose three attempts are register rows
#26, #31 and #36.)

**THE ARCHIVE WAS NOT OPENED.** `VMFL063_WB.wbpz` exists at
`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/VMFL063_WB.wbpz`
(sha256 `8b037b7b79cf13b9b1a4f91469639a40815364dc17f31c6692b02600085b48fa`) and was
**not read for this registration** — the reference number comes from the manual's own
table. **Consequently Ansys's domain extents are unknown to this registration and the
domain below is THIS LAB'S CHOICE, disclosed with its blockage in sec.9.** Neither
archive copy is written to, moved or deleted by this case.

---

## 3. THE REFERENCE TIER, AND WHY `PASS` IS OUT OF REACH FOR LIMB A

**Reference kind: EXPERIMENTAL.** Lane & Loehrke measured the reattachment length on a
blunt plate at low Reynolds number; the manual carries their value as *Target*.

Limb A therefore makes a **CONTINUUM claim** — a statement about the property of the
continuum solution — and `VERIFICATION_CHARTER.md` §2f.3's classification table puts
the ceiling of a continuum limb at **`GATE REACHED`**: *"a property of the continuum
solution, from which discretisation error is not separable ... `GATE REACHED` maximum.
`PASS` is unavailable."* §2h.4 condition 1 is the only route to a `PASS` on a physics
limb and it requires the reference to be *"the exact or manufactured solution of the
same continuum model the solver discretises. Not an experiment, not a correlation, not
a different model."* **An experimental reattachment length is expressly not that.**

The ceiling is **hard-coded** in `grade_vmfl063.py` (`TIER_CEILING_A = 'GATE REACHED'`)
and `verdict_for_limb_a()` **refuses (exit 2) if it ever produces `PASS`**. The
comparator's `--selftest` drives that function over every triple state and both
band outcomes and checks that `PASS` never appears.

**Limb B is different in kind and the difference is the charter's own.** §2f.3's second
row: **SAME-DISCRETE-PROBLEM IDENTITY** — *"that two computations of the SAME discrete
problem agree ... `PASS` available. A triple is irrelevant to it: both sides carry the
same discretisation error on the same mesh, it cancels exactly, and the claim is
identity, not accuracy."* Serial determinism (L1 vs its twin L1D) is exactly that
claim, and it is named in that row's own enumeration.

**AND IT STILL PRODUCES NO CREDENTIAL, BY CONSTRUCTION.** The ROW verdict is the WORST
limb (`row_verdict()` takes the minimum over the fixed ordering
`NOT A RESULT < GATE FAIL < GATE REACHED < PASS`). Limb A's ceiling is `GATE REACHED`,
so the ROW's maximum is `GATE REACHED`. `ANSYS_VERIFICATION_CHARTER` §6: *"Only `PASS`
rows are credentials."* **This registration's best possible register row is
`GATE REACHED`, which is not a credential, and that is registered here before compute
so nobody later reads limb B's `PASS` as one.** Limb B's own verdict is printed
separately and honestly, as `VMFLGPU003` (row #38) printed its three limbs.

---

## 4. THE MESH FAMILY AND THE ROACHE TRIPLE

Cartesian 2-D, all-hex, three blocks, built by `blockMesh` from
`case/system/blockMeshDict.template`. Origin at the blunt leading-edge face on the
plate centreline: `x = 0` is the blunt face, `y = 0` is the centreline, `y = t = 0.045`
is the plate top surface, and `x` increases downstream.

| block | extent | role |
|---|---|---|
| A | x ∈ [−0.9, 0], y ∈ [0, 0.045] | upstream of the blunt face, below plate-top level |
| B | x ∈ [−0.9, 0], y ∈ [0.045, 1.8] | upstream, above plate-top level |
| C | x ∈ [0, 1.5], y ∈ [0.045, 1.8] | **downstream, above the plate — the graded region** |

Domain extents, chosen a priori and never from a run: upstream `Lu = 0.900 m = 10·2t`;
downstream `Ld = 1.500 m`, the manual's own plate length, with the outlet at the plate
end; far field `H = 1.800 m = 20·2t`.

Boundaries: `inlet` (fixedValue 0.0517 m/s), `outlet` (zeroGradient U, p = 0),
`centreline` (`symmetryPlane`, y = 0, x < 0), `plateFace` (`wall`, the blunt face
x = 0, 0 ≤ y ≤ 0.045), **`plateTop` (`wall`, y = 0.045, 0 ≤ x ≤ 1.5 — the wall the
reattachment length is measured along)**, `farfield` (`symmetryPlane`, y = 1.8),
`frontAndBack` (`empty`).

### The three levels, r = 2

| level | NXU | NXD | NYL | NYU | block A | block B | block C | **total cells** |
|---|---|---|---|---|---|---|---|---|
| **L1** | 32 | 80 | 12 | 48 | 384 | 1 536 | 3 840 | **5 760** |
| **L2** | 64 | 160 | 24 | 96 | 1 536 | 6 144 | 15 360 | **23 040** |
| **L3** | 128 | 320 | 48 | 192 | 6 144 | 24 576 | 61 440 | **92 160** |
| L1D | 32 | 80 | 12 | 48 | 384 | 1 536 | 3 840 | 5 760 (limb B twin, identical to L1) |

**Every one of the four counts doubles at every level**, so the cell count is exactly
×4 per level and the refinement is systematic in both directions. Grading ratios are
held FIXED across levels (block A `(0.1 0.2 1)`, block B `(0.1 160 1)`, block C
`(20 160 1)`), which halves every local cell dimension.

| resolution | L1 | L2 | L3 |
|---|---|---|---|
| first cell off `plateTop` | 1.1291 mm | 0.5740 mm | 0.2894 mm |
| first cell at the leading edge, Δx | 2.9319 mm | 1.4721 mm | 0.7376 mm |
| Δx at the expected reattachment x = 0.36 m | 16.7771 mm | 8.1761 mm | 4.1130 mm |

**AN HONEST LIMIT ON r, DISCLOSED BEFORE THE FREEZE AND NOT CORRECTED FOR.** The
Roache formula uses **r = 2.0**, which is exact in cell count. Because the total
expansion ratios are held fixed while the counts double, the *local* size ratio between
consecutive levels is not exactly 2: measured from the table above it lies in
**[1.967, 2.052]**, i.e. within −1.65 % / +2.60 % of 2. Since `p = ln|d21/d32| / ln r`,
an error `dr/r` in the ratio produces `dp/p = −(dr/r)/ln r`, so a 2.60 % departure
gives at most **3.75 %** in the observed order and a comparable error in the GCI. This
is stated rather than adjusted; the alternative (retuning the expansion ratio per level)
would make the three meshes members of different families, which is worse.

### The triple, and rule 5

- Functional: **`LR/(2t)` itself**, at each level.
- `roache(f_L1, f_L2, f_L3)` with `r = 2.0`, **`Fs = 1.25`**, observed-order floor
  **`P_MIN = 0.05`** (`docs/ansys_verification/FINDING_p_floor.md` §4).
- **A triple that is not `CONVERGING` makes the row `NOT A RESULT`, whatever the
  value** (`CLAUDE.md` rule 5 step 2). `DIVERGENT`, `STAGNANT`, `OSCILLATORY`, `EXACT`
  and an observed order below `P_MIN` all land there.
- **A GCI is NEVER quoted unless the triple is `CONVERGING`** — the comparator returns
  `gci_fine = None` in every other state, and `--selftest` checks all four.
- **Rule 5 is ONE-WAY.** The gate can turn a `GATE REACHED` or `GATE FAIL` *into*
  `NOT A RESULT` and never the reverse. `--selftest` drives that direction explicitly.

---

## 5. THE GATE

### Limb A — CONTINUUM, ceiling `GATE REACHED`

```
LR = the LAST reversed-to-attached crossing of the physical wall shear on plateTop,
     inside the frozen window  X_WIN_LO < x <= X_WIN_HI,  linearly interpolated
     between the bracketing face centres.
GATE:  |LR/(2t) - 4.0| / 4.0  <=  0.10     at the finest level L3
AND    the Roache triple on LR/(2t) is CONVERGING
```

**THE BAND, JUSTIFIED WITHOUT A RUN.** `TOL = 0.10` (10 %, relative) is
- **the band this register already uses for exactly this quantity class** — an
  experimental reattachment length reproduced in `simpleFoam` — at row **#30**
  (`VMFL064-R2`, `|LR/s − 5.0|/5.0 ≤ 0.10`), which is the nearest precedent on the
  register and was itself frozen before its own compute;
- **wider than the manual's own agreement class**, which is Ratio **1.04** (Fluent) and
  **1.01** (CFX) — 4 % and 1 % — so a lab solver that matched Ansys's agreement would
  clear the band with 60 % of it unspent, and a band tuned to flatter this lab would
  have been tighter, not wider;
- **not tighter than the reference can support**: the Target is quoted as **4.0**, two
  significant figures, so the reference itself is resolved to no better than
  ±0.05/4.0 = **±1.25 %**, and a band below about 3 % would be gating against the
  rounding of the number it is gating on;
- **chosen before any VMFL063 mesh existed** (sec.0), and byte-frozen in the comparator
  as `TOL = 0.10`.

**THE SEARCH WINDOW, JUSTIFIED WITHOUT A RUN.** `X_WIN_LO = 0.0` (**open** at the lower
end: a crossing exactly at x = 0 is the separation point, not a reattachment) and
`X_WIN_HI = 1.2 m`. In the graded units that upper bound is **13.33 · 2t**, i.e.
**3.33 times the expected answer** of 4.0, and it stops **0.3 m short of the outlet**.
A window spanning more than three times the reference cannot be read as tuned to an
answer, and one stopping 0.3 m short of the outlet cannot admit an outlet artefact as
"the last crossing".

**WHY THE LAST CROSSING AND NOT THE FIRST — a repair adopted in advance, not after a
failure.** Register row **#29** (`VMFL064`) landed `NOT A RESULT` because its frozen
reader took the **FIRST** negative-to-positive crossing and refused whenever the profile
did not *start* negative; a secondary counter-rotating eddy at the foot of the step,
resolved only at the finest level, added an upstream crossing and flipped the starting
sign. A blunt leading edge has the same corner. **VMFL063 registers the last-crossing
reader from the outset.** The first-crossing locator is carried in the comparator
**off the grading path**, solely so the corner-eddy control can drive it on the same
constructed bytes and show it returns a different, wrong number where the gate reader
returns the primary length — the defect demonstrated, not described.

**THE SIGN CONVENTION IS NOT ASSUMED.** OpenFOAM's reported `wallShearStress` sign is
fixed **from the data** at `X_SIGN_REF = 1.35 m`, which lies **outside** the search
window, deep in the attached boundary layer, 0.15 m short of the outlet. The comparator
multiplies by the resulting orientation so the attached region is positive, and
**refuses** if that reference face carries |τ| below `TAU_EPS = 1e-14`. `--selftest`
drives both conventions and checks they yield the same LR.

**CROSS-INSTRUMENT CHECK, AND IT GATES.** An independent instrument — the sign change
of streamwise velocity `u_x` in the **first cell row above the plate**, a different
field with a different discretisation — must locate the same event within
**`CROSS_TOL_CELLS = 3.0` local cell widths**, at every level. Beyond that the
comparator **refuses (exit 2)**; it does not average, prefer or degrade.

### Limb B — SAME-DISCRETE-PROBLEM IDENTITY, ceiling `PASS`

```
L1D is a SECOND independent solve of L1's discrete problem: identical case inputs,
identical mesh counts, identical endTime, run in its own directory.
GATE:  same converged iteration count
  AND  sha256(<t>/wallShearStress), sha256(<t>/U), sha256(<t>/p) identical between
       L1 and L1D
  AND  LR bitwise equal between L1 and L1D
```

**Band: EXACT IDENTITY. There is no tolerance and none is registered.** Serial
`simpleFoam` on one rank has no RNG and no thread-order nondeterminism; if the two
solves differ at all, that is a finding about this lab's toolchain and the limb reads
`GATE FAIL`, honestly. `--selftest` shows the limb **can** fail: a one-part-in-3.6e6
difference between the twins is detected.

**Why this limb is worth 0.17 core-min.** Every reproducibility claim this team has
ever made — every re-grade, every "byte-identical to attempt 1", every GPU-vs-CPU
comparison — rests on the solver being deterministic, and **this lab has never measured
it.** It is the cheapest measurable premise on the register.

---

## 6. STRICT COMPLETION (CLAUDE.md rule 4, IN FULL)

Applied at **every** level including the L1D twin. The comparator **REFUSES (exit 2)
rather than grading a partial run.**

**PHYSICS-CRITICAL — each clause gates:**

1. **`rc = 0`** — from `RUN_RC.<level>`, captured *inside* the detached subshell.
2. **An `End` line** in `log.simpleFoam`, matched by **exact filename** through the
   cardinality guard — never a `log*` glob, which matches `log.blockMesh` first.
3. **`SIMPLE solution converged` present.**
4. **last `Time` < `endTime`.** **This is the declared adaptation of rule 4's
   "last time == endTime" clause for a `residualControl`-terminated STEADY solve, and
   it is declared HERE, before compute, not improvised in the comparator.** For a
   steady solve `last == endTime` means the solver **ran out of clock without
   converging**, which is the opposite of completion; the honest completion condition
   is that it stopped on its own residual criterion strictly before the ceiling. The
   precedent is register row #30 (`VMFL064-R2`), whose three levels converged at
   424 / 907 / 2 152 iterations against an `endTime` of 20 000.
5. **`ExecutionTime` count == the iteration count.**
6. **Fields present at that time:** `U`, `p`, `wallShearStress`, `Cx`, `Cy`.
7. **The numerically-latest time directory (sorted `key=float`) equals the log's last
   `Time`.** A disagreement refuses. This is a direct guard against the
   lexicographic-sort hazard: a grader that picks one of these without checking the
   other reads `950` as later than `2000`.
8. **AGE GUARD.** Every field at `endTime` is **strictly newer** than the case's own
   `0/U`, which the launcher `touch`es **last**, immediately before the solver, so it
   dates the run allowed to produce the answer. The launcher **additionally refuses to
   launch into a level directory that already holds a `0/` or a numeric time
   directory**, matched by regex and never by a `[0-9]*` glob (which also matches
   `0.orig`).

**INFRASTRUCTURE (L-342, Sanaa 2026-08-26 — *a bookkeeping failure invalidates the
bookkeeping, never the physics artefacts*):** `RUN_RC.<level>` and `COST.txt`.
**ABSENT** → rc is reported **`NOT MEASURED`**, disclosed in the record, and the grade
**proceeds** on the physics-critical clauses, which are the stronger evidence.
**PRESENT AND non-zero** → **REFUSE**, because a recorded non-zero rc is evidence about
the solver, not about the poller. Absence is a disclosure, never a licence.

---

## 7. COST (CLAUDE.md rule 12)

| item | value |
|---|---|
| **ranks** | 1 (serial, all four solves) |
| **ESTIMATE** | **16 core-min** total |
| **CAP** | **90 core-min, RUNNING TOTAL across all four solves** |
| `cost_basis` | c7a.4xlarge at **$0.0513/core-h**, owner-stated 2026-08-21/22 — **REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **DERIVED**. |
| **$ at estimate** | **$0.01368 derived** |
| **$ at cap** | **$0.07695 derived** |

**How the estimate was built, from a MEASURED rate and not a guess.** Register row #30
(`VMFL064-R2`) records L3 at **49 152 cells, 2 152 iterations, 300 wall s, RANKS = 1**
→ **2.837e-6 s per cell per iteration** on this box. Its three levels converged at
424 / 907 / 2 152 iterations for 3 072 / 12 288 / 49 152 cells, which fits
`iterations ∝ N^0.586`. Applying both to this family:

| solve | cells | predicted iterations | predicted wall s | predicted core-min |
|---|---|---|---|---|
| L1 | 5 760 | 613 | 10 | 0.17 |
| L1D | 5 760 | 613 | 10 | 0.17 |
| L2 | 23 040 | 1 381 | 90 | 1.50 |
| L3 | 92 160 | 3 110 | 813 | 13.55 |
| **total** | | | **923** | **≈ 15.4 → registered 16** |

**Why the cap is 5.6× the estimate and not 2×.** The throughput rate is measured but
the *iteration* model is extrapolated **from a different geometry**: a channel-expansion
bubble is a shorter, better-conditioned separated flow than a leading-edge bubble on a
long plate in a tall far field, and the extrapolation is the weak link. 90 core-min is
the same cap magnitude this register already used for the same quantity class (row #30)
and it stops the run at 5.6× the prediction rather than letting it run indefinitely.
**An overrun STOPS the run (rc 124) and does NOT get a new budget; `endTime` is never
silently reduced to fit a cap.** The cap is enforced in the launcher's executable path
as `timeout_s = remaining_core_min * 60 / RANKS`, drawn down level by level.

**Estimate-versus-actual calibration is OWED at completion** (rule 12, Sanaa's
directive of 2026-08-23): actual core-minutes from `COST.txt` and each
`RUN_RC.<level>`, the ratio actual/predicted, attribution (contention / waste /
misprediction, waste named separately and never absorbed into the ratio), dollars
derived and labelled derived, one row in `docs/COST_CALIBRATION.md`.

---

## 8. THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3)

*A zero from a reader not shown able to see a non-zero is not evidence.* This
comparator carries the control in **two stages on two channels**, and the two stages
exist because this team has recorded **two distinct ways** the control has failed here.

| stage | what is planted | what must happen | which recorded failure it answers |
|---|---|---|---|
| **P1a — reader sensitivity** | a **sized** offset `K_PLANT · max\|τ\|` (`K_PLANT = 0.05`) added to the x-component of **EVERY** `plateTop` face, in place, on a **copy of the real solver bytes** — header, dimensions and every other patch untouched | every value read back **from disk** through the real reader moves by exactly the plant | **SIZED**: register row **#26** (`VMFL011`), where a fixed 1.234e-3 single-point plant was diluted by an averaging reader to 3.68e-7 and the control refused a working reader (**L-340**). **EVERY FACE**: register row **#31** (`VMFL011-R2`), where a correctly sized point plant landed on a row **outside the point reader's support** and moved it by exactly 0 (**L-347**). |
| **P1b — gate-functional sensitivity** | the **same** planted file | the **full gate functional** must move: shifting the physical wall shear up by a positive constant must move the last reversed-to-attached crossing **upstream**, or push it out of the window entirely | **A plant the raw reader sees but the GATE does not is precisely row #31's failure.** P1a alone would not have caught it. |

The same two stages run on the **independent near-wall `u_x` channel**
(`K_PLANT_U = 0.05 · U_inf`).

**Either stage failing REFUSES (exit 2). The only way the control function returns is
to have seen the plant on both stages.** There is no path in which a refusal is
downgraded to a warning.

**AND THE CONTROL IS SHOWN ABLE TO FAIL, not merely to pass.** `--selftest` monkeypatches
the *writer* so the plant never reaches disk and checks the control then **refuses**;
it also checks the control refuses on a channel that is identically zero, so there is
nothing to size against. A control never shown failing is a control never tested
(row #31: *"a control standing behind another control's refusal is an untested
control"*).

**THE CARDINALITY GUARD.** Every file this comparator opens goes through
`one_match(pattern, what)`, which **refuses (exit 2) unless the pattern matches exactly
one path**. `sorted(glob.glob(...))[-1]` appears nowhere in the file: it sorts numeric
directory names **lexicographically**, so `950` beats `2000`, and 19 such hazard sites
across 9 files are measured in this territory (HEAD `c7176346`). Where a numeric order
is genuinely needed, `numeric_latest_time_dir()` sorts with **`key=float`** and its
answer is **cross-checked against the solver log's own last `Time`**, with a
disagreement refusing. `--selftest` builds the directories `0`, `950`, `2000` and
checks both that the helper returns `2000` and that the lexicographic answer would
have been `950`.

**NO `assert` STATEMENT APPEARS IN THE COMPARATOR.** `python3 -O` deletes every assert,
so a control written as one exists under a flag and not under another (**L-332**).
`_ast_guard()` walks the file's own AST — from the **source**, so the count is the same
under both interpreters — and **refuses if the `ast.Assert` count is not 0**. It runs
in `--selftest` **and on the grading path**. Independently verified at drafting:
`ast.Assert` count **0**, `ast.Raise` count **43**.

**`--selftest`: 62 checks, 0 failures, rc 0, and BYTE-IDENTICAL output under `python3`
and `python3 -O`** (`__pycache__` cleared before each, L-333). The launcher runs both,
`cmp`s them, and refuses before spending a core-minute if they differ, if any `[FAIL]`
line appears, or if any of **nine named control markers** is missing from the output —
so a selftest that silently stopped exercising a control cannot pass the launcher.

---

## 9. ERROR BUDGET — disclosed BEFORE the freeze

**`ANSYS_VERIFICATION_CHARTER` Amendment 1.4 CLAUSE A DOES NOT APPLY TO THIS CASE, and
that is stated rather than left to be inferred.** Clause A binds the disclosure of the
axisymmetric-`wedge` geometric bias. **VMFL063 is Cartesian 2-D with `empty` front and
back patches; there is no wedge, no azimuthal discretisation and no `sec(t/2)` bias.**
A clause that does not apply is recorded as not applying so a reader does not read its
absence as an omission.

| source | magnitude | sign / direction | how it was obtained |
|---|---|---|---|
| **Blockage of the far field** | plate half-thickness `t/H = 0.045/1.8 = 2.50 %`; the flow area contracts from 1.800 m at inlet to 1.755 m over the plate, so the free stream accelerates by **+2.564 %** | **SIGN NOT ASSERTED.** The direction of the effect on LR/(2t) is **not** claimed, because this lane has no measurement of it and asserting an unverified sign is exactly what Clause A's second boundary forbids. It is a real bias of known magnitude and unknown sign, and it is disclosed as that. | geometry, exactly; `H` chosen a priori |
| **Reference resolution** | the Target is **4.0**, two significant figures → the reference is resolved to no better than **±1.25 %** | symmetric | manual Table .63.1 as printed |
| **Domain length upstream** | `Lu = 10·2t` ahead of the blunt face | not quantified | chosen a priori |
| **Outlet placement** | `x = 1.5 m`, the manual's plate length; **3.17 LR downstream of the expected reattachment** | not quantified | geometry |
| **Refinement ratio** | local r ∈ [1.967, 2.052] against the formula's r = 2.0 → ≤ **3.75 %** in the observed order p and comparably in the GCI | symmetric | sec.4, computed from the grading |
| **Two-dimensionality** | the experiment is a nominally 2-D plate of finite span | **NOT QUANTIFIED — named, not priced** | — |
| **Ansys's own domain** | unknown to this registration; the archive was not opened | — | sec.2 |

**None of these widens the band. The band is 10 % and the disclosure obligation is on
the disclosure, never on the tolerance.**

---

## 10. NAMED LIVE OUTCOMES — every one of these can happen, and each is written down now

The fixed vocabulary and nothing else (`CLAUDE.md` rule 1).

| # | outcome | the condition that produces it |
|---|---|---|
| 1 | **ROW `GATE REACHED`** *(the best attainable row)* | triple `CONVERGING`, L3 inside the 10 % band, limb B exactly identical. Limb A prints `GATE REACHED`, limb B prints `PASS`, the row is the worse of the two. **Not a credential.** |
| 2 | **ROW `GATE FAIL` (physics)** | triple `CONVERGING`, L3 **outside** the 10 % band. A finding, recorded with its numbers, never softened and never deleted. |
| 3 | **ROW `GATE FAIL` (determinism)** | limb A holds but the L1/L1D twins differ in any hash, iteration count or LR bit. A real finding about this lab's toolchain. |
| 4 | **ROW `NOT A RESULT` — triple not `CONVERGING`** | `DIVERGENT` (R ≥ 1), `OSCILLATORY` (R < 0), `STAGNANT` (a zero difference, or p below `P_MIN = 0.05`), or `EXACT`. **Whatever the value.** No GCI is printed. |
| 5 | **`NOT A RESULT` — the solve never converged** | no `SIMPLE solution converged` line, or last `Time` == `endTime` (ran out of clock). **This is the largest scientific risk in this registration** and it is named, not glossed: a leading-edge separation bubble can become unsteady, and a steady SIMPLE solve of an unsteady flow does not converge. It is registered as admissible because Lane & Loehrke's study is specifically of the **steady** low-Re regime and both Ansys solvers reported converged steady solutions (Ratio 1.04 / 1.01) — but if it does not converge here, **the honest answer is `NOT A RESULT` and the row will say so.** |
| 6 | **`NOT A RESULT` — no crossing in the window** | the plate-top wall shear has no reversed-to-attached crossing in (0, 1.2] m: the bubble does not close inside the window, most plausibly on the coarsest level. The comparator refuses; it does not extend the window. |
| 7 | **`NOT A RESULT` — cross-instrument disagreement** | wall shear and near-wall `u_x` locate the reattachment more than 3 local cell widths apart. |
| 8 | **`NOT A RESULT` — a control did not fire** | either plant stage unseen on either channel; the cardinality guard matching ≠ 1 file; the orientation reference face carrying \|τ\| < 1e-14; the AST guard finding an `assert`. |
| 9 | **`NOT A RESULT` — completion clause failed** | missing `End`, `ExecutionTime` mismatch, a missing field, the age guard, a recorded non-zero rc, or the time-directory cross-check disagreeing. |
| 10 | **`BLOCKED`** | the toolchain is absent (no `simpleFoam`, no `blockMesh`) or `blockMesh` fails. **A crash is a FINDING, not a retry**; the launcher stops and the crash is triaged. |
| 11 | **`PENDING`** | registered and not yet run — the state this document is in as it is committed. |

**`PASS` at row level is not in this table because it is unreachable by construction
(sec.3). Only limb B can print it, and the row takes the worse limb.**

**THE PREDICTION.** This lane declines to predict which of outcomes 1–3 lands. What is
predicted, and is the falsifiable content of this document, is that **the gate above
can return any of them**: it is not constructed so that only one answer is possible.

---

## 11. THE GRADING PATH, FROZEN

| artefact | path |
|---|---|
| pre-registration | `cases/ansys_verification/VMFL063/PREREGISTRATION.md` (this file) |
| comparator | `cases/ansys_verification/VMFL063/grade_vmfl063.py` |
| launcher | `cases/ansys_verification/VMFL063/run_vmfl063.sh` |
| case inputs | `cases/ansys_verification/VMFL063/case/` — 9 files |
| run root | `verification/runs/ansys_verification/VMFL063/` — **does not exist** |

**The launcher refuses to spend a core-minute unless, at launch:** this file and the
comparator on disk hash equal to their **HEAD blobs**; **all nine case inputs** hash
equal to their own HEAD blobs (so the case that runs is the case that was frozen);
the comparator's `--selftest` is green and byte-identical under both interpreters and
carries all nine named control markers; and each level directory holds no `0/` and no
numeric time directory. It records both blobs in `LAUNCH_RECORD.txt` and in every
`RUN_RC.<level>` **before** the solver starts, and it mints a `birth_certificate.json`
per level from that level's own `checkMesh` (`MESH_STANDARD` §6).

`grade_vmfl063.py --verify-frozen` re-hashes this file and the comparator against HEAD
at grade time and returns rc 2 on any mismatch.

**PRE-FLIGHT SMOKE (`ANSYS_VERIFICATION_CHARTER` Amendment 1.4 Clause B).** After this
registration is committed and before the graded run, the launcher is run with
`VMFL_SMOKE=1` on **L1 only at `endTime 1`**. **It refuses any run root not under a
scratch directory**, so a smoke can never create a `0/` or a time directory inside
`verification/runs/ansys_verification/` and can never disarm or consume the age guard.
The smoke directory is never the graded artefact and is never cited by a record. **A
smoke failure ABORTS and is a finding, not a retry** — Clause B's warrant is that a
comparator `--selftest` proves the GRADER and never the CASE (VMFL045 run 1: selftest
45/45, solver dead on the first timestep; VMFL003 run 1: selftest 60/60, case
unrunnable). **Nothing in this registration has been executed against OpenFOAM. The
`blockMeshDict` has never been meshed and the case has never been solved.**

---

## 12. WHAT THIS REGISTRATION DOES NOT CLAIM

- **It is not a statement about Ansys.** This box has no Ansys solver. It is a
  statement about **this lab's `simpleFoam`** against the manual's reference result.
  Ansys's own 4.16 and 4.05 are carried as context and are never the gate.
- **It does not claim the archive's setup.** `VMFL063_WB.wbpz` was not opened; the
  domain is this lab's choice, disclosed with its blockage.
- **It cannot earn a credential.** Ceiling `GATE REACHED` at row level, by construction
  and by declaration, before compute.
- **It establishes nothing about meshes finer than L3.** A triple establishes the
  behaviour across the levels run and nothing about finer ones.
- **Nothing here is sent anywhere.** Submissions are parked; the manual is proprietary
  Ansys documentation held for this lab's private use (`CLAUDE.md` rules 7 and 8).

---

## AMENDMENT 1 — 2026-08-28 — THE LAUNCHER'S SELFTEST GATE WAS UNSATISFIABLE

**Version: v1.0 (freeze commit `2df23798`) → v1.1.**
**Lines whose number changed above this section: 0.** This block is appended at the
foot under `CLAUDE.md` rule 6. Nothing above line 547 was edited, moved, struck or
rewritten; the body's line numbering is unchanged and every citation into it still
resolves. Authorised by the ansys-verification supervisor's ruling of 2026-08-28,
`[lab-attributed]` — not Sanaa's word and not any agent's consent (rule 9).

### A. THE RULE-2 CONDITION, NAMED AND CHECKED

Rule 2 permits amendment **before first compute** provided the condition is stated
and the check is named. It was checked at 2026-08-28T16:45Z, five ways:

1. **`verification/runs/ansys_verification/VMFL063/` DOES NOT EXIST.** That is the
   run directory rule 2 asks to be named. `ls -d` returns
   *"No such file or directory"*.
2. **Zero paths under `verification/runs/ansys_verification/VMFL063` at HEAD** —
   `git ls-tree -r HEAD --name-only | grep -c` returns `0`.
3. **Zero `log.*` files anywhere under `cases/ansys_verification/VMFL063/`** — no
   solver log of any kind exists.
4. **Zero `wallShearStress` artefacts** anywhere under the case.
5. **Zero solver time directories.** The only directories under the case are
   `case/`, `case/0/`, `case/constant/`, `case/system/`.

The launcher refused at the old line 109 gate **before its own `mkdir -p "$RUN_ROOT"`
(old line 129)**, so the run root was never created and the rule-4 age guard is
**unconsumed**. **Solver compute to date: 0 core-minutes. No `simpleFoam` iteration
has ever run for VMFL063.**

**THE LEGALITY OF THIS AMENDMENT RESTS ON THAT ABSENCE.** No gate quantity exists —
no `LR`, no `LR/(2t)`, no reattachment length, no Roache triple, no observed order,
no GCI, no residual history. **There is no number in existence that a gate could have
been fitted to.** The amendment is therefore made in the state rule 2 protects.

### B. THE DEFECT — A GUARD THAT COULD NOT PASS

Frozen launcher `run_vmfl063.sh` line 109 (blob `ad864596`) read, verbatim:

    cmp -s "$ST" "$ST.O" || { echo "ABORT: --selftest differs between python3 and python3 -O -- a control that vanishes under -O is not a control (L-332)"; exit 2; }

It demanded **byte-identical** output from `python3` and `python3 -O`. That is
**unsatisfiable by construction**, and not by accident of environment:

- `grade_vmfl063.py:867` opens the selftest sandbox with
  `tempfile.mkdtemp(prefix="vmfl063_selftest_")`, which mints a **fresh random
  absolute path on every invocation**.
- **20 of the 78 output lines quote that path** — they are refusal messages that name
  the file the reader refused on, which is exactly what makes them useful.
- Therefore **two runs of the SAME interpreter also differ**, by the same 20 lines.

**Measured, 2026-08-28T16:4xZ, `__pycache__` cleared before each run:**

| comparison | lines differing, raw | lines differing, after normalising the one random token |
|---|---|---|
| `python3` vs `python3 -O` | **20** of 78 | **0** |
| `python3` vs `python3` (same flag, twice) | **20** of 78 | **0** |

`sed -E 's#vmfl063_selftest_[A-Za-z0-9_]+#…NORM#g'` is the only normalisation applied.

**THE INSTRUMENT IS SOUND; THE GATE ON IT WAS IMPOSSIBLE.** Under both interpreters:
**62 `[PASS]`, 0 `[FAIL]`, rc 0**, `SELFTEST: all checks passed` present, all nine
named control markers present, `ast.Assert` count **0** and `ast.Raise` count **43**
(re-derived here by walking the file's AST, not taken from §8).

**AND THE GUARD WAS ALSO REDUNDANT.** Old lines 110–112 already `grep` for
`^SELFTEST: all checks passed`, already abort on any `^  \[FAIL\]` line, and already
require all nine named markers. The intent of line 109 — *a control must not vanish
under `-O`* (L-332) — was already carried by them for the plain interpreter. Line 109
was **both unsatisfiable and redundant**, and the redundancy is why the case is not
harmed by replacing it.

### C. WHAT CHANGED, AND WHAT DID NOT

**In `run_vmfl063.sh` only** (the launcher is not the frozen comparator; the
comparator `grade_vmfl063.py` is **untouched**, blob `fc339a79` before and after):

1. The byte-identity `cmp` is replaced by the **satisfiable form of the same intent**:
   the two interpreters must agree on **`[PASS]` count**, on **`[FAIL]` count** and on
   **exit rc**, and the marker `AST guard: ast.Assert count is 0 in this file` must be
   present in **BOTH** outputs. Each of the five conditions aborts `exit 2` with a
   message **naming which quantity differed and both values**.
2. The two `--selftest` invocations now capture `RC_PLAIN` / `RC_O` explicitly instead
   of testing rc inline with `||`. Behaviour is identical — a non-zero rc still aborts
   with the same wording plus the rc value — and the capture is what makes the rc
   comparison in (1) possible.
3. The block comment above the check, which asserted *"The two runs must be
   BYTE-IDENTICAL"*, is corrected to state what is now checked and why byte-identity
   is impossible.
4. The success `echo` at old line 125, which printed *"byte-identical under python3
   and python3 -O"*, now prints the three agreeing counts and the marker result.

**Old lines 110–112 and the nine-marker loop are unchanged, character for character.**

**THE NEW CHECK IS STRICTER THAN THE OLD CODE IN ONE RESPECT:** the AST-guard marker
is now required in the `-O` output as well. The nine-marker loop greps `"$ST"` only.
That is precisely the L-332 concern the original was reaching for and did not achieve.

**NO GATE, BAND, THRESHOLD, CAP, CEILING OR LABEL MOVED.** Verified constant by
constant against the HEAD blobs, before and after, by extraction and `diff` — **0
lines differ**:

| constant | value | where | moved? |
|---|---|---|---|
| `TOL` | `0.10` | `grade_vmfl063.py:52` | no |
| `X_WIN_LO` / `X_WIN_HI` | `0.0` / `1.2` | `:67`, `:68` | no |
| `X_SIGN_REF` | `1.35` | `:72` | no |
| `FS` | `1.25` | `:75` | no |
| `RATIO` | `2.0` | `:76` | no |
| `P_MIN` | `0.05` | `:77` | no |
| `K_PLANT` / `K_PLANT_U` | `0.05` / `0.05` | `:81`, `:82` | no |
| `TIER_CEILING_A` | `"GATE REACHED"` | `:93` | no |
| `TIER_CEILING_B` | `"PASS"` | `:94` | no |
| `U_INF`, `NU`, `RE_2T` | `0.0517`, `1.7894e-05`, `260.0` | grader head | no |
| `RANKS` | `1` | `run_vmfl063.sh:38` | no |
| `CAP_CORE_MIN` | `90` (running total, four solves) | `:39` | no |
| `ENDTIME` | `30000` | `:40` | no |
| `SMOKE_ENDTIME` | `1` | `:61` | no |
| level list | `L1 L1D L2 L3` | `:46` | no |
| cell counts `NXU/NXD/NYL/NYU` | `32/80/12/48`, `64/160/24/96`, `128/320/48/192`, L1D = L1 | `:51`–`:54` | no |
| cost estimate / cap in §7 | **16** core-min / **90** core-min | this file | no |

The comparator's blob hash is **identical before and after** (`fc339a79d1b0…`), which
is a stronger statement than the table: **not one byte of the grading instrument
changed.**

### D. THE §8 CLAIM CORRECTED

**§8 line 440 reads, and is STRUCK as written:**

> `--selftest`: 62 checks, 0 failures, rc 0, and **BYTE-IDENTICAL output under
> `python3` and `python3 -O`**

**§11 line 512 carries the same wording — *"green and byte-identical under both
interpreters"* — and is STRUCK on the same ground.** The supervisor's ruling scoped
this correction to §8; I extended it to §11 because it is the *same* claim in the same
document, and correcting one while leaving the other standing would leave a false
sentence in a frozen record. That extension is disclosed here and is the only place
this amendment goes beyond its scope.

**WHAT IS TRUE INSTEAD, and it is the substance the claim was reaching for:**

> `--selftest`: **62 checks, 0 failures, rc 0 under BOTH `python3` and `python3 -O`**,
> `__pycache__` cleared before each. The two outputs are **NOT byte-identical and
> cannot be** — the selftest sandbox path is random per invocation and appears in 20 of
> 78 lines, so the same interpreter run twice also differs by 20 lines. **After
> normalising that single token the two outputs are identical, 0 lines differing.** The
> launcher checks **PASS count, FAIL count, exit rc and the AST-guard marker under both
> interpreters**, plus the all-checks-passed line, the absence of any `[FAIL]` line and
> all nine named control markers, and refuses before spending a core-minute if any of
> those fails.

The original sentence was **false as written and true in substance**. Recording which
of those two it was is the point of this block: the check it described was never
performed by any run, because the check it *demanded* could not be performed at all.

### E. THE LESSON — A GUARD THAT COULD NOT PASS

This family has already recorded *a guard that could not fail*. This is its exact
mirror: **a guard that could not pass.** Both are **launcher-level** defects, and
**neither can ever be caught by a comparator `--selftest`, because the guard lives
outside the instrument it guards.** The comparator was green 62/62 throughout; the
gate on it was impossible; and no amount of testing the comparator would ever have
revealed it. It took **driving the launcher** to find it.

**The transferable rule, offered as a candidate LESSONS entry and NOT filed here:**

> **A guard must be driven to BOTH its outcomes before it is trusted — shown able to
> PASS on good input AND shown able to FAIL on bad. A guard that has only ever been
> seen to fail is exactly as unproven as one that has only ever been seen to pass.**

The number is not assigned in this document: rule 11 requires it be re-derived from the
tail of `docs/LESSONS.md` at commit time, and this file is not the place it lands.

### F. A GAP IN THE SUPERVISOR'S OWN §3 CHECK, RECORDED AS THE SUPERVISOR'S

Recorded verbatim at the supervisor's direction, as the supervisor's own:

> *"My §3 check 1 read `grade_vmfl063.py` as code and did not read `run_vmfl063.sh`'s
> smoke gate. Check 1 covers any script that produces, grades or aggregates a measured
> number, and a launcher that decides whether the comparator runs at all is on that
> path. My check was incomplete and the pre-flight smoke caught what I missed."*

The pre-flight smoke of `ANSYS_VERIFICATION_CHARTER` Amendment 1.4 Clause B is what
found this. **That is Clause B earning its place a second way:** it was warranted as
proof that a green comparator does not mean a runnable case (VMFL045, VMFL003), and it
here caught something different again — a launcher gate that no case and no comparator
could ever have exposed.

### G. WHAT THIS AMENDMENT DOES NOT DO

- It does not touch the comparator. Blob unchanged.
- It does not move a gate, band, threshold, cap, ceiling or label. See §C.
- It does not establish that the case solves. **No `simpleFoam` iteration has run.**
  Clause B's warrant remains undischarged; §11's closing sentence still holds in full.
- It does not license a second amendment. **After first compute, gates are closed**
  and any further departure is a dated addendum that cannot alter a gate.
