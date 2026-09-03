# A1WRT — WALL-RESOLVED α-TAIL, INCOMPRESSIBLE ONLY — PRE-REGISTRATION **FROZEN 2026-09-03**

*(The filename retains `_DRAFT` so that every existing citation of this document
by path stays valid. **The file is frozen; the name is a stale label and this
line is the notice.** A rename would silently break references in
`LAB_STATE`, the A1WR results record and the parked queue row.)*

> ## ⚠ FROZEN BY COMMIT 2026-09-03. NOT ENQUEUED. NOT LAUNCHED.
>
> **FROZEN. NOT ENQUEUED. NOT LAUNCHED. ZERO COMPUTE SPENT.**
>
> **The freeze is this file's commit sha**, landed together with `a1wrt_read.py`
> in one commit so the prose and the grading path cannot diverge. **Gates,
> thresholds, caps and labels are CLOSED from that commit.** Changes land only
> as dated addenda appended at the foot, which may not alter a gate, a
> threshold, a cap or a label; the originals above are struck, never rewritten.
>
> **INSTRUMENT MANIFEST, PINNED BY THIS FILE:**
>
> | instrument | md5 | role |
> |---|---|---|
> | `a1wrt_read.py` | `705db5f7e972f6c033cbe303b7a6038f` | **the grading path** — the frozen reader; verify the file that ran IS this file by hashing it against the committed blob |
> | `a1wrt_fixture.log` | `4f6e870f74790af9238266c7cf10a0d2` | static control fixture (§6); the reader pins this same md5 internally at `a1wrt_read.py:90` |
> | `a1wr_alpha12_reference.tsv` | `26ce1af0b0e93af5b9f71efdc34446a4` | `G-REPRO`'s A1WR α = 12 reference series; pinned internally at `a1wrt_read.py:93` |
>
> **PRE-COMPUTE CONDITION, RE-CHECKED BY EXECUTION IN THE FREEZING SHELL
> (2026-09-03T18:29Z):** run root `/home/ubuntu/certonomous-runs/A1WRT/`
> **ABSENT** — `test -e` returned non-zero, and no path matching `*A1WRT*` exists
> anywhere under `/home/ubuntu/certonomous-runs/`. **That absence is what makes
> every edit landed in this commit lawful** under `CLAUDE.md` rule 2 limb 1 and
> `VERIFICATION_CHARTER` §2b: amendments before first compute are legal, and the
> condition is named and checked rather than asserted.
>
> **STILL OWED, AND IT GATES THE ENQUEUE, NOT THE FREEZE:** the supervisor's §3
> check 4 — the §4.3/§4.4 cap arithmetic and the §3.3/§3.5 control bands read
> personally, as arithmetic and not as a summary. **It is not delegable.** The
> queue row is drafted and PARKED OUTSIDE `verification/queue/` until that
> sign-off. **Enqueueing is not authorisation and no lane launches this item.**
>
> **The reader's own controls were driven at freeze time: `--selftest` returns
> `SELFTEST PASS: 39 controls, both directions, mutation controls included`,
> rc = 0**, including the four `G-PATCHPAIR` controls Q1–Q4 in their re-anchored
> form.
>
> **The successor is a NEW ITEM on a FRESH RUN ROOT with its OWN budget** —
> a fresh pre-registration under `VERIFICATION_CHARTER` §2b limb 1.
> **It is NOT a restart of A1WR Stage 2**, which is closed
> (`A1WR_STAGE12_RESULTS.md`, `NOT A RESULT`), whose freeze contains no restart
> rule, whose in-memory continuation state died with the process, and whose
> registered per-arm budget is 79.37 % spent with 165.03 core-min remaining
> against a 186.02 core-min need.

**Item:** `A1WRT` — NACA0012 α-tail 12…18° on the A1WR wall-resolved L3 mesh,
**incompressible only** (`DASimpleFoam`), run on a **REPAIRED patch identity
(`empty`, not `symmetry`)** with a one-variable pair at α = 12 that measures the
repair itself. **Eight points, three units.**
**Team:** dafoam **Lane:** lab-lane **Drafted:** 2026-09-03
**Status:** NO COMPUTE HAS BEEN SPENT ON THIS ITEM. Run root
`/home/ubuntu/certonomous-runs/A1WRT/` **does not exist** — checked, not
asserted, at draft time; the freeze must re-check it in its own shell.
**Verdict class:** `FEASIBILITY`. **Verdict ceiling:** `GATE REACHED`.

---

## 0. WHAT THIS ITEM IS FOR, AND WHAT IT INHERITS

A1WR Stage 2 measured a clean incompressible polar at α 0…12 on the
wall-resolved L3 mesh — CL strictly increasing, dCL/dα strictly decreasing, no
break, no kink — and was killed by a `shutdown -h now` at 02:25:05Z with α = 13
in flight at 2,500 of 4,000 iterations. **The tail α 13…18 is the part of the
registered polar that does not exist, and this item gets it legally.**

Inherited unchanged, by md5, from the A1WR freeze:

| instrument | md5 | role |
|---|---|---|
| `a1wr_runScript_incomp.py` | `d48f48c5e2e41e86981acbf6feccb3c4` | producer |
| `a1wr_cmd.sh` | `eba014f2c538611d2249c3fcf9b3ddd7` | in-container unit program |
| mesh | A1WR L3, **130,304 cells**, `/home/ubuntu/certonomous-runs/A1WR/L3/` | subject |
| image | `dafoam-idwarp-rot:v1`, `sha256:2927768a16ac…`, `libidwarp` md5 `85f59e87253e0a71a813f64ca6e4c425` | PATCHED build |

Frozen numerics carried unchanged: `primalMinResTol = 1.0e-8`, `endTime = 4000`,
SA, `useWallFunction: False`, **np = 1**, `OMP_NUM_THREADS=1`, one-core cpuset.
**Nothing about the discretisation, the numerics or the build moves.** Changing
any of them would make the tail non-comparable to the α 0…12 body it extends —
the two-variable trap A1WR refused four times.

---

## 1. THE COMPRESSIBLE ARM IS ABSENT, AND HERE IS ITS REASON ON THE RECORD

**A missing arm needs its reason on the record, the same way a missing point on
a polar does.** The compressible arm is **not run by this item**, and this is
why, measured:

- **11 of 11 compressible wall-resolved solves have failed** — A1WR's 9 sweep
  points (α 0…8) and MAAOA's 6 points collapse to the same outcome
  (`LAB_STATE` S-27), at every Mach and **including α = 0**.
- **It is not a near miss.** Across 409 print steps A1WR's arm C bound `U`
  659 + 507 times, `p` 385 + 385, `e` 383 + 384, `rho` 383 + 371. It produced
  **negative CD at five angles** (to −10.1252) and CL swinging +79.8907 to
  −80.4237. Arm I's entire census over the same run is `Bounding nuTilda>` ×
  559 — one per print step, the ordinary SA clip.
- **The setup defect is not identified.** Re-running it now would be a third
  attempt at something that has failed twice — Sanaa's 2026-09-03 envelope law
  item 4 names exactly that as an escalation trigger
  (`etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md`, read for this
  draft, not relayed).

**Registered position: the compressible arm returns as its own item behind a
DIAGNOSIS, not behind a retry.** Its absence here is a decision on evidence, and
this item may not be read as evidence about it either way.

---

## 2. THE DESIGN — A BLOCKING PHYSICS FIX, AND THE PAIR THAT MEASURES IT

### 2.0 The patch identity is repaired, under Sanaa's own classification

Sanaa, 2026-09-03 ~20:00Z, verbatim
(`etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md`, **read at source for
this draft, not relayed**):

> *Blocking physics fixes — a result can't be produced or trusted without them
> (**wrong patch identity on a mesh**, a residual print that isn't the max over
> equations, a boundary condition set wrong, a linear solver failing). These jump
> every queue, need no petition, and the team fixes them and records a lesson
> afterward, not before.*

**That names this defect exactly.** The A1WR L3 mesh's two bounding planes are
`type symmetry`, not `empty`; OpenFOAM therefore assembles a z-momentum equation
on a mesh one cell thick (§7). **Running the tail on the defective identity would
knowingly spend ~256 core-min producing seven numbers that cannot be trusted and
then say so on the certificate.** Under her classification the fix jumps the
queue, needs no petition, and the lesson is recorded afterward.

**REGISTERED: the tail runs on `empty`.**

### 2.1 Three units, because each comparison must move exactly ONE variable

| unit | patch | start | points | what it isolates |
|---|---|---|---|---|
| **U1** `alpha12_symmetry` | `symmetry` | COLD | α = 12 | **cold-vs-continued**, against A1WR's own continued α = 12 (`CL` 1.19079592024, `CD` 0.030665481166). This is `G-REPRO` exactly as §3 registers it, on A1WR's own configuration, unchanged. |
| **U2** `alpha12_empty` | `empty` | COLD | α = 12 | **`symmetry`-vs-`empty`**, against U1 directly above it. Both COLD, same mesh, same numerics, same operating point, same iteration budget — a true one-variable pair. |
| **U3** `tail_empty` | `empty` | CONTINUED from U2's **final** state, **in the same process as U2** | α = 13…18 | the trustworthy tail |

**Eight points, and the eighth is what makes the other seven interpretable.**
Comparing a cold `empty` α = 12 directly against A1WR's *continued* `symmetry`
α = 12 would move cold-vs-continued **and** `symmetry`-vs-`empty` at once and
measure neither. **U1 is bought precisely to remove that confound** (§4.3 prices
it at ~32 core-min), and it is the same one-variable discipline this item has
now applied five times.

U2 and U3 are **one process, one container**: `0/` reset from `0.orig` once
before U2's cold α = 12, then α = 13…18 ascending, each inheriting its
predecessor's final state **in memory** — converged or not; §7 registers that it
will not be. U1 is its own container and its own
case tree, because it carries a different mesh boundary file.

**No point is retried, relaxed, re-tuned or dropped**; a point that fails is
recorded with its residual history and the sweep continues, with every subsequent
point flagged `after_exception=TRUE`. **A missing point on a polar is a lie by
omission.**

### 2.2 What "runs on `empty`" actually requires on disk — registered, not waved

`empty` is not a one-word edit. **`G-PATCH` verifies all three by execution
before any primal:**

1. `constant/polyMesh/boundary`: `symmetry1`/`symmetry2` → `type empty;`
   (`inGroups 1(empty)`), 130,304 faces each, unchanged.
2. **Every field in `0.orig/`** — `U p nut nuTilda k omega epsilon` — must carry
   `type empty;` on those two patches. A mesh patch typed `empty` beside a field
   patch typed `symmetry` is a case that will not start, and a field left
   `symmetry` on a mesh patch typed `empty` is the silent-no-op class this lab
   has been bitten by twice.
3. **The solver's own log line is the acceptance test, and it is a measurement,
   not an assertion:** the `empty` units must print
   **`Mesh has 2 solution (non-empty) directions (1 1 0)`** and U1 must print
   **`Mesh has 3 solution (non-empty) directions (1 1 1)`**. `G-PATCH` refuses at
   exit 2 on any other combination. **This is the whole defect reduced to one
   line the solver prints about itself.**

**`0/` MUST be reset from `0.orig` for a genuinely cold start** — pyDAFoam
renames a converged solution back into `0/`, so a "cold" start that does not
reset is not cold. **`G-COLDSTART` verifies the reset ON DISK before the first
primal** (every field's `internalField` read back and asserted `uniform`), not
from the driver's own claim. A1WR's forensics are the reason this is a gate and
not a comment: its killed `sweep_I/case/0/` was left carrying a **nonuniform
130,304-cell `U`** under an α = 13 inlet beside a **uniform** `p`, `nut` and
`nuTilda` — a mixed state that a naive restart would have consumed silently.

### 2.1 Why the tail cannot simply be restarted from A1WR's disk — settled, not assumed

Measured (`A1WR_STAGE12_RESULTS.md` §8): no `processor*` directory exists
anywhere under the A1WR run root; no time directory other than `0` and `0.orig`
exists in either sweep; no `.bin`, restart or pickle file exists. The only
surviving converged data is the α = 12 velocity field, already stamped with the
α = 13 inlet, with the pressure and the entire SA turbulence state at their
uniform freestream values. **There is no checkpoint. The continuation state was
in memory and died with the process.**

---

## 3. ⚠ `G-REPRO` — THE REPRODUCTION CONTROL, AND A CORRECTION TO ITS PREMISE

This is the best part of the item and it is **registered as a gate, not as a
remark.** But the premise it was handed down with is **false for this data**,
and registering it unexamined would have produced a control nobody could read.

### 3.1 The premise as stated, and why it does not hold here

> *"A converged steady solution should be history-independent, so agreement
> corroborates that the continuation label was live."*

**A1WR's α = 12 point is NOT CONVERGED.** The frozen reader
`a1wr_read.py` grades all 13 arm-I points `NOT CONVERGED`; DAFoam's success
string `Minimal residual … satisfied the prescribed tolerance 1e-08` appears
**zero times** in `sweep_I/out/sweep.log`; every point ran the full 4,000
iterations; and at α = 12's last print the initial residuals were U0 1.18e-08,
p 1.66e-08, nuTilda 2.80e-08 — **above** the registered 1e-8 and still falling.

So the comparison this control performs is **not** "two roads to the same fixed
point". It is **"two roads to iteration 4,000"**, which is a *stronger and
rarer* property that no theory guarantees. **Registered consequence:
disagreement at iteration 4,000 would NOT by itself impeach the continuation
label**, and a band sized on converged-solution anchors would be far too tight.

### 3.2 The anchors, MEASURED, and what they do and do not bound

Converged cold-vs-continued pairs on the **coarse** mesh, α = 4, both regimes,
both sides reaching the 1e-8 tolerance:

| | continued CL | cold CL | relative |
|---|---|---|---|
| AOAI (incompressible) | 0.394096562948 | 0.394096584258 | **+5.407e-08** |
| AOAC (compressible) | 0.422884513911 | 0.422884515661 | **+4.140e-09** |

CD relative: AOAI **−8.781e-08**, AOAC **−4.10e-09**. Read from
`/home/ubuntu/certonomous-runs/CURRICULUM-AOA{I,C}-…/out/LEDGER.tsv`.

**These bound history-dependence of a CONVERGED solution at ≲ 1e-7 relative,
and they bound nothing else.** They are the anchor for §3.3's *plateau* limb and
are explicitly **not** the anchor for its *iteration-4,000* limb.

### 3.3 The residual-state term, MEASURED and EXTRAPOLATED, and the registered band

A1WR's α = 12 CL was still drifting monotonically at the cap. Measured from the
last 12 prints of that segment: increments per 100 iterations
−6.096e-05, −5.337e-05, −4.660e-05, −4.057e-05, **−3.522e-05**, decaying with a
geometric ratio of **0.8681**. Geometric-sum remaining drift to plateau:
**−2.319e-04 absolute = −1.947e-04 relative** — **EXTRAPOLATED, and labelled
so.** CD's tail gives ratio 0.9440 and remaining **+1.78e-04 relative**, more
sensitive to the ratio and therefore the weaker of the two.

**So the reported CL = 1.19079592024 sits roughly 2e-4 relative above its own
plateau, and two solves stopped at the same cap from different histories can
legitimately differ by that order.**

**REGISTERED, BEFORE THE RUN:**

| limb | quantity compared | band | basis |
|---|---|---|---|
| **R1** | CL and CD **at iteration 4,000**, cold α = 12 vs A1WR's continued α = 12 | **\|Δ/x\| ≤ 1.0e-3** | ≈ 5× the MEASURED-and-EXTRAPOLATED 1.95e-4 (CL) / 1.78e-4 (CD) residual-state head-room of §3.3 |
| **R2** | the **geometric-extrapolated plateau** of each series, computed by the identical frozen routine on both | **\|Δ/x\| ≤ 1.0e-4** | the §3.2 converged anchors (≲ 1e-7) widened ~1,000× for the extrapolation's own error, which is the term that dominates |

**Both limbs are published whichever way they fall. R2 is the limb that tests
the property that matters** — history-independence of the fixed point — and is
the reason the cold α = 12 is run to the **identical `endTime` 4,000 and the
identical `primalMinResTol` 1e-8**, so that the only thing differing between the
two series is the starting state.

### 3.4 What each outcome means — registered before the answer exists

- **R1 and R2 both inside band → `CORROBORATED`.** The continuation label on
  A1WR's α ≤ 12 body was live, and this item's tail is a faithful continuation
  of that body. The tail may be reported beside it.
- **R2 inside, R1 outside → the fixed point agrees and the iteration-4,000
  states do not.** That is a statement about *iterative history at a fixed
  budget*, not about the polar; the tail stands and the discrepancy is
  published with both series.
- **R2 outside band → THE FINDING, AND IT IS WORTH MORE THAN THE TAIL.** Two
  starting states reach different plateaus on the same mesh at the same α. The
  item reports that, the tail's `CONTINUED` labels are **withdrawn**, and the
  successor is a diagnosis, not more points. **Registered in advance so this
  cannot be narrated afterwards.**
- **The cold α = 12 fails outright** → `NOT A RESULT` on `G-REPRO`; the tail is
  still run and reported, with the control's absence named, never papered over.

**`G-REPRO` may only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the
reverse** (`CLAUDE.md` rule 5's permitted direction).

### 3.5 `G-PATCHPAIR` — THE SECOND COMPARISON, AND ITS THRESHOLDS ANCHORED ON MEASURED DRIFT

U1 (`symmetry`, cold) against U2 (`empty`, cold). **The like-for-like quantities
are not the two values at iteration 4,000**, because U1 stops at the cap still
drifting. Comparing those two directly would fold U1's own residual-state
head-room into the answer and call it contamination.

**REGISTERED: the comparison is U1's EXTRAPOLATED PLATEAU against U2's
EXTRAPOLATED PLATEAU, both computed by the IDENTICAL frozen `plateau()` routine
in `a1wrt_read.py`** — each solve's own best estimate of its own fixed point,
and both the same kind of estimate of the same kind of quantity. Both series and
both geometric fits are published whole so either extrapolation can be checked.

> **⚠ RE-ANCHORED 2026-09-03, BEFORE ANY COMPUTE, ON THE SUPERVISOR'S RULING.**
> An earlier form of this section compared U1's extrapolated plateau against
> **U2's *converged* value**. §7 now registers that **the `empty` units are
> expected NOT to converge** — `primalMaxRes` never contained `U2` to begin
> with. Under that registration the old anchor made `G-PATCHPAIR` return
> `NOT A RESULT` on **the outcome this item itself predicts**: a gate cannot be
> anchored on the outcome its own registration expects, because it can then
> never fire. A plateau is available from a drifting series and from a converged
> one alike, so the plateau-vs-plateau form **returns a real verdict on both
> outcomes**. U2's convergence state is still read and printed beside the
> verdict; it no longer decides whether the gate can fire. The prose and the
> reader were changed together, in the same commit, before the first primal.

**The registered prediction, written before the run — and it is the boring one:**
CL and CD are **unchanged** between `symmetry` and `empty` to within the
extrapolation's own error. **No tolerance is relaxed and `endTime` is not
raised.**

> **⚠ STRUCK 2026-09-03, BEFORE ANY COMPUTE. The sentence below stood here and
> is FALSIFIED. It is struck in place rather than rewritten, because this
> document registered both it and its withdrawal (§7) and the two contradicted
> each other on the page.**
>
> ~~"and **the only change is that the `empty` solve converges**, because with
> two solution directions there is no z-momentum equation to assemble and
> therefore no `U2` residual to floor. **It converges because the equation that
> floored is gone, not because anything was tuned.**"~~
>
> **Why it is false:** `primalMaxRes` **excludes the z-component of a vector
> equation**, so removing the z-momentum equation removes a residual that was
> **never in the convergence criterion**. Verified by the supervisor personally
> on D19T's own logs, with no source read required: in
> `/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening/`,
> arm T10's `U2` residual **floor** is **1.7164e-10 — 1.72× ABOVE its own 1e-10
> tolerance**, so `U2`'s best value over the whole run never reached tolerance,
> and yet T10 **declared convergence 22 times at ~9.0e-11**. A maximum over a
> set cannot fall below the minimum ever attained by a member, so `U2` is not a
> member of the declared quantity. The binding channel in D19T's converging arms
> is `he` and the declared number **is** its floor (T08: `he` 9.0893e-09 vs
> declared 9.0871e-09; T10: `he` 9.0350e-11 vs declared 9.0384e-11 — four
> significant figures, both arms). **The patch repair is still correct — a
> `symmetry` bounding plane on a one-cell mesh assembles a spurious equation and
> that is a genuine defect — but it must not be sold as the thing that makes the
> solve converge.** §7 carries the full withdrawal and the projection.

**The thresholds, RE-SET 2026-09-03 with the re-anchor above, BEFORE ANY
COMPUTE.** The comparison is now **two-sided** — a plateau on each side — so it
carries the extrapolation's own error **twice**, once per side. The old bands
were sized for a one-sided comparison and are superseded here:

```
plateau-extrapolation sensitivity, MEASURED (§3.3):   +-4.9e-05 relative
two sides, each carrying it, doubled as the old band was:
        2 x ( 4.9e-05 + 4.9e-05 )  =  1.96e-4   ->  rounded up to  2.0e-4
the 10x ratio between the two bands is preserved:        2.0e-4 x 10  =  2.0e-3
```

**These two numbers are the SUPERVISOR'S CONSTRUCTION (dafoam-supervisor,
2026-09-03), and they are `DERIVED` from a MEASURED sensitivity — they are NOT
themselves measured.** The measured input is the ±4.9e-05 of §3.3; everything
from there to 2.0e-4 is the arithmetic printed above.

| band | verdict | anchor |
|---|---|---|
| **\|Δ/x\| ≤ 2.0e-4** | **NOISE** — the repair does not move the coefficients | the plateau extrapolation's own sensitivity: CL's geometric ratio is 0.8681 and CD's is 0.9440, so a ±0.02 error in r moves the remaining term by ≈ ±25 %, i.e. **≈ ±4.9e-05 relative** on CL. **DERIVED** by the arithmetic above: that error on **both** sides, doubled, = 1.96e-4, rounded up. |
| **2.0e-4 < \|Δ/x\| ≤ 2.0e-3** | **INDETERMINATE** — reported, neither cleared nor called contamination | between the two-sided extrapolation error and the residual-state head-room; the instrument cannot separate them. The 10× ratio is carried over unchanged. |
| **\|Δ/x\| > 2.0e-3** | **⚠ CONTAMINATION, AND IT IS THE FINDING** | **10.3× the MEASURED residual-state head-room of 1.947e-04** (§3.3), so larger than any iteration-state effect can explain |

**If it lands in the third band the finding is large and its reach is stated in
advance: it would touch every incompressible number this ladder has produced on
a `symmetry`-bounded 2-D mesh**, not merely this item. That is registered here so
it cannot be discovered and then minimised.

**A cheaper coarse-mesh anchor of the same pair is registered separately on
D19T's 4,032-cell grid**, which also tests the mesh-scaling half of the account
(floor ~1.7e-10 there against the measured 3.238e-08 here). **Different mesh,
different item. This item does not register the coarse pair and must not.**

---

## 4. COST — REGISTERED BEFORE COMPUTE, FROM MEASURED WALLS

### 4.1 Which ledger this draws on — say it so nobody charges the wrong one

**This is Ladder A, not the industrial ladder.** It draws on `CLAUDE.md`
rule 12's under-$25 pre-authorisation and rule 12's bookkeeping. **It does NOT
draw on the $1,000 Rungs 0–3 benchmark envelope** of Sanaa's 2026-09-03 law,
which is a *ladder* budget for the industrial benchmark family. Nothing in this
item is charged against that envelope and it does not move its 80 % trigger.

### 4.2 The anchor — MEASURED on this exact mesh, image and solver

Every A1WR arm-I point ran **exactly 4,000 iterations**, so per-point cost is
essentially fixed and this is a measurement, not a model.

| basis | s/iteration | window |
|---|---|---|
| α = 9, 10, 11 | 0.41930 | quiet box (after 21:58Z) |
| **α = 12** | **0.46155** | quiet box |
| **α = 13, in flight when killed** (1,153.35 s / 2,500 it) | **0.46134** | quiet box |
| α = 0 | 1.15400 | **14 containers live** |
| `cold_I_4/14/17` | 1.781 / 1.810 / 1.784 | **14 containers live** |

**α = 11 → α = 12 rose 10.2 %; α = 12 → α = 13 was flat.** The rise is real but
did **not** compound, so the tail is priced at the α = 12/13 rate with an
explicit allowance rather than at a compounding trend. **Do not average blindly
across the trend** — the α = 0 and cold rows above are contention, not α.

### 4.3 The estimate

**Eight points across two containers.** Priced per unit, because each carries its
own deadline (§4.4).

| unit | term | arithmetic | core-min |
|---|---|---|---|
| **U1** | 1 point × 4,000 it × **0.4615 s/it** (MEASURED) | 1,846.0 s | 30.77 |
| **U1** | container start + import | 93.85 s (MEASURED on `a1wr_sweep_I`: container wall 28,146.98 s − last `ExecutionTime` 28,053.13 s) | 1.56 |
| | **U1 ESTIMATE** | | **≈ 32.33** |
| **U2+U3** | 7 points × 4,000 it × 0.4615 s/it | 12,922 s | 215.37 |
| **U2+U3** | container start + import | 93.85 s | 1.56 |
| **U2+U3** | tail-stiffening allowance on α 14–18, **EXTRAPOLATED** | 5 × 4,000 × 0.4615 × 0.25 = 2,307.5 s | 38.46 |
| | **U2+U3 ESTIMATE** | | **≈ 255.39** |
| | **ITEM ESTIMATE** | 32.33 + 255.39 | **≈ 288 core-min** |

= 4.800 core-h ≈ **$0.2462 DERIVED, NOT MEASURED** at the owner-stated
$0.0513/core-h; `cost_basis` **REPORTED-BY-OWNER** — the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Every point is priced at the FULL 4,000 iterations.** *(Corrected 2026-09-03,
before compute: this paragraph previously called that "deliberately conservative
for the `empty` units" on the ground that "§7 registers that they are expected to
converge and therefore to stop early". **§7 now registers the opposite** — the
`empty` units are expected NOT to converge, because `primalMaxRes` never
contained `U2`. Pricing at the full 4,000 is therefore the **expected** case, not
a conservative one, and the estimate below is unchanged in every figure: what
changes is that it no longer claims head-room it will not get.)* **No saving is
taken in advance**: an estimate that banks a predicted improvement is an estimate
arguing for its own hypothesis. If the `empty` units nevertheless **do** stop
early, the actual/predicted ratio comes in low and **that is reported at
calibration as a favourable misprediction with its cause named**, not quietly
absorbed — and it is also a finding about the coupling (§7). The `empty` solve
also drops one momentum equation per iteration, which should make it cheaper per
iteration; **that is UNMEASURED on this mesh and no credit is taken for it
either.**

**The term most likely to carry the error is the tail-stiffening allowance**, and
it is named in advance, exactly as A1WR §7.5 named its own iteration-scaling
assumption.

### 4.4 The cap, and the deadline arithmetic **EXECUTED AND EVALUATED AT DRAFT TIME**

Sanaa, 2026-09-03, verbatim: *"still carries a hard per-run cap (set by the team
at ~3× its own estimate, not by me) … The estimate is an instrument, not a
permission slip."*

**⚠ THE ESTIMATE AND THE CAP ARE SPLIT, BECAUSE CONFLATING THEM IS WHAT PRODUCED
THE CONFLICT.** A single figure that assumes a quiet box is the A1WR error; a
single figure that assumes a full one would report a ~0.26 ratio on a quiet night
and corrupt the calibration dataset. So:

**THE ESTIMATE IS A PREDICTION AND IS REPORTED AS A FUNCTION OF OCCUPANCY**
(solve time and the stiffening allowance scale with occupancy; the two container
starts do not):

| occupancy | item estimate |
|---|---|
| solo | **287.7 core-min** |
| 2× | **572.3 core-min** |
| **14-way, the MEASURED saturation (3.85915× solo)** | **1,101.4 core-min** |

**THE DEADLINE AND CAP ARE PROTECTION AND ARE SIZED ON THE WORST REGISTERED
CASE — the 14-way end:**

> **U1 = 361 core-min** (3.00 × 120.30) · **U2+U3 = 2,943 core-min**
> (3.00 × 981.11) · **ITEM CEILING = 3,304 core-min** = 3.00 × the 14-way
> estimate. = 55.07 core-h ≈ **$2.825 DERIVED** — under the $25
> pre-authorisation and far under the $150 escalation trigger.

**THE CERTIFICATE COMPARES ACTUAL AGAINST THE ESTIMATE AT THE MEASURED
OCCUPANCY**, using the occupancy `G-CONCURRENCY-PRECOND` records at launch and at
every point boundary. Like against like — that is the calibration payoff, and it
exists only because the occupancy recording is in the instrument.

**D19T was frozen, md5-pinned, gate-checked and launched TWICE with a deadline
of exactly 0 s because nobody ever executed the arithmetic at freeze. It is
executed here, in this document, and its result is evaluated:**

```
ranks         = 1                        (np = 1, registered)
CAP_MARGIN_S  = 300                      (3.2x the MEASURED 93.85 s container start)

TMO_U1        = int(  361 * 60 / 1) - 300 =  21660 - 300 =  21360 s
TMO_U2U3      = int( 2943 * 60 / 1) - 300 = 176580 - 300 = 176280 s
```

**EVALUATED, both of them, here, in this document:**

| unit | `TMO` | `> 0` ? | `TMO/60` core-min | ≤ its cap ? |
|---|---|---|---|---|
| U1 | **21,360 s** | ✓ | 356.00 | ≤ 361 ✓ |
| U2+U3 | **176,280 s** | ✓ | 2,938.00 | ≤ 2,943 ✓ |

Back-checks exact. Effective budget `356.00 / 120.30 = 2.96×` (U1) and
`2938.00 / 981.11 = 2.99×` (U2+U3), both against the **14-way** estimate.

**⚠ AND AN HONEST LIMIT ON WHAT THAT DEADLINE PROTECTS.** `TMO_U2U3` is
**176,280 s ≈ 49 hours**. **This box was powered off after 7 h 49 m on the night
this item's predecessor ran**, and its longest recorded uptime this week is
under 23 h. **A 49-hour in-container deadline is therefore not the binding
protection — the box's own uptime is**, and a poweroff is an infrastructure kill
that no cap can convert into a cap-stop. The deadline is sized correctly for the
registered worst case and is stated here as **necessary but not sufficient**;
the real protection against an over-long run on a busy box is the per-point
ledger row, which lands after every point and survives the kill.

**A freeze that cannot print a positive evaluated integer in this table does not
launch.** D19T was frozen, md5-pinned, gate-checked and launched **twice** with a
deadline of exactly 0 s because nobody ever executed this arithmetic.

### 4.5 The deadline against a BUSY box — the 331.7 core-min lesson, applied

A1WR lost **all six** cold controls and 331.6667 core-min for **zero physics** to
a 3,300 s deadline sized from a quiet-box rate and spent on a box the same item
had just filled 14-deep. Registered here rather than repeated:

**U2+U3**, 7 points × 4,000 it = 28,000 iterations against a 45,720 s deadline:

| box state | s/iteration (MEASURED) | 28,000 it | vs the 45,720 s deadline |
|---|---|---|---|
| quiet | 0.4615 | 12,922 s + 94 s = **13,016 s** | **28.5 % — finishes comfortably** |
| moderate contention, 2× | 0.923 | 25,938 s | 56.7 % — finishes |
| **break-even** | **1.63286** | 45,720 s | **100 % — the ceiling** |
| A1WR's measured 14-way saturation | 1.781 | 49,868 s | **109.1 % — CAP-STOPPED at ~6.4 of 7 points** |

**U2+U3 survives contention up to 3.538× the solo rate** —
`45,720 / 28,000 = 1.63286 s/it`, and `1.63286 / 0.4615 = ` **3.53816**.

**U1**, 1 point × 4,000 it against a 5,520 s deadline: break-even
`5,520 / 4,000 = 1.38000 s/it`, i.e. **2.990× solo**. **U1 therefore has
MATERIALLY LESS headroom than U2+U3 and is the unit that will cap-stop first
under load.** That is stated because the two units are not interchangeable and
the §4.6 arithmetic must be evaluated **per unit**, not once for the item.

**⚠ AND A1WR'S OWN MEASURED WORST CONTENTION IS 1.781 s/it = 3.85915× SOLO,
WHICH IS ABOVE THAT CEILING. THE ITEM DOES NOT SURVIVE IT.** *(An earlier draft
of this section claimed 3.90× headroom. That was arithmetically wrong, it
contradicted this very table's 108.9 % row, and it overstated the real headroom
by 10 % — on the one number a reader would use to decide whether to launch
beside other work. Corrected by the supervisor's §3 check 4, and the error is
recorded rather than silently fixed.)*

Beyond the ceiling the item cap-stops, and **that outcome is registered in
advance: a cap-stop is `NOT A RESULT` on the unfinished points; points already
in the ledger stand.** No new budget is granted on an overrun.

**THIS IS WHY §4.6'S CONCURRENCY PRECONDITION IS A LAUNCH GATE AND NOT ADVICE.**
The margin between "finishes comfortably" and "cap-stops having bought nothing"
is a box-occupancy condition that no gate in this lab currently reads.

**AND THE MECHANISM IS MEASURED, NOT GUESSED:** A1WR's cpusets were all disjoint
(A1WR 8–15, MAAOA 2–7, verified by `docker inspect`) and per-core throughput
still degraded 2.75–4.77×. **A one-core cpuset isolates a core, not memory
bandwidth.** The driver therefore **records box occupancy and MemAvailable at
launch and at every point boundary into the ledger row**, so contention is
attributed from measurement at calibration time instead of argued.

**This item is at most TWO np = 1 processes on two cores** (U1 may run beside
U2+U3 or before it; U3 is serial with U2 by construction). It consumes 2 of 16
cores, so it is a legal filler under the never-idle rule without itself creating
the saturation that killed A1WR's controls.

### 4.6 `G-CONCURRENCY-PRECOND` — A LAUNCH GATE, BECAUSE §4.5's MARGIN IS NEGATIVE AGAINST MEASURED SATURATION

**THE DEFECT WAS NEVER CONCURRENCY. IT WAS A COST BASIS THAT ASSUMED A QUIET BOX
WHILE NOTHING CHECKED.** An earlier form of this clause demanded an empty
machine; that would fight Sanaa's standing order that the box is never idle, and
it would refuse launches the arithmetic says are perfectly safe.

**REGISTERED: the launcher records measured occupancy and `MemAvailable` at
launch AND at every point boundary into the ledger row, and REFUSES only if the
registered deadline does not cover the predicted rate AT THE MEASURED
OCCUPANCY.** The census must itself be shown able to return a NON-EMPTY answer
before an empty one is accepted (rule 3, applied to a census rather than to a
field reader — a census that cannot see a running container is not evidence that
none is running), but an empty census is **not** a launch condition.

**The test is the arithmetic, not an empty machine.**

**REFUSAL POINT, RE-DERIVED AGAINST THE NEW DEADLINES:**

| unit | deadline | iterations | break-even s/it | = × solo | refuses at |
|---|---|---|---|---|---|
| U1 | 21,360 s | 4,000 | 5.3400 | **11.57×** | occupancy > 11.57× |
| U2+U3 | 176,280 s | 28,000 | 6.2957 | **13.64×** | occupancy > 13.64× |

**The measured 14-way saturation is 3.859× solo, so both deadlines cover the
worst occupancy this box has ever exhibited with 3.0–3.5× margin, and this gate
NEVER REFUSES at any occupancy on record — n = 7 and n = 8 included.** It records
and it queues; it does not block. That is the correct outcome under
"reported, not gated" and under *"I prefer something to be running and watched
than too much governance and no run."*

**It is not decorative, and here is the condition that would still fire it:** an
occupancy above ~11.6× solo, i.e. roughly three times worse than anything
measured on this box. If that is ever recorded, the arithmetic refuses and the
refusal is the finding. Contention is otherwise attributed from measurement at
calibration time instead of argued.

**THE LAB-WIDE FINDING THIS GATE RESTS ON, STATED IN ITS GENERAL FORM BECAUSE IT
IS NOT AN A1WR FACT:**

> **A one-core cpuset isolates a core. It does not isolate memory bandwidth.**
> A1WR's cpusets were all disjoint — A1WR on cores 8–15, MAAOA on 2–7, **verified
> by `docker inspect` and not assumed** — and per-core throughput of a
> 130,304-cell OpenFOAM SIMPLE solve still degraded **2.75× to 4.77×** under
> 14-way concurrency. **No gate in this lab reads this**, every in-container
> deadline in the lab is sized on a solo rate, and **331.6667 core-min bought
> zero physics learning it** when all six of A1WR's cold controls timed out.

`G-PLACEMENT`'s cpuset-disjointness reading is **necessary and not sufficient**,
and this item registers that distinction on its face rather than discovering it
again.

### 4.7 Calibration at completion

Per rule 12 and `docs/COST_CALIBRATION.md`'s append rules: at completion the
estimate above is compared against the actual in core-minutes from logs, dollars
derived and labelled, the ratio stated, and the gap attributed with
**contention, waste and misprediction named separately** and waste never
absorbed into the ratio.

---

## 5. GATES

| gate | subject | verdict rule |
|---|---|---|
| `G-COLDSTART` | every field of `0/` read back from disk and asserted `uniform` **before** the first primal | refuse (exit 2) on any nonuniform field — A1WR's mixed `0/` is the precedent |
| `G-PATCH` | §2.2 — the patch identity ACTUALLY IN FORCE: mesh `boundary` types, every `0.orig/` field's entry on those patches, and the solver's own `Mesh has N solution (non-empty) directions` line | refuse (exit 2) unless U1 prints **3 (1 1 1)** and U2/U3 print **2 (1 1 0)**. **The defect reduced to one line the solver prints about itself** |
| `G-PATCHPAIR` | §3.5 — U1's extrapolated plateau vs **U2's extrapolated plateau**, both through the identical frozen `plateau()`, CL and CD | ≤ **2.0e-4** NOISE; ≤ **2.0e-3** INDETERMINATE, reported; > **2.0e-3** **CONTAMINATION and it is the finding**. **RE-ANCHORED 2026-09-03 (§3.5):** the old plateau-vs-*converged-value* form returned `NOT A RESULT` on the non-convergence §7 predicts — a gate anchored on its own registration's expected outcome can never fire. Both outcomes now yield a verdict; U2's convergence state is printed beside it |
| `G-REPRO` | §3, both limbs R1 and R2, bands registered above | inside → `CORROBORATED`; R2 outside → tail labels withdrawn, `NOT A RESULT`; control absent → `NOT A RESULT` on the control |
| `G-COMPLETE` | rule 4, **all** clauses: rc 0, `End` line, last time == `endTime`, fields present, `ExecutionTime` count == `endTime`, every field newer than the case's own datum | refuse (exit 2) rather than degrade, and **the distinction is registered**: a clause the reader CAN evaluate and that fails is a `GATE FAIL`; a clause it CANNOT evaluate is a REFUSAL. *(An earlier draft justified this gate by claiming A1WR had never implemented `G-COMPLETE`. **That claim was FALSE and is withdrawn** — see §5.1. The gate is implemented here because a single grading path is easier to audit than two, not because A1WR lacked one.)* |
| `G-CAPS` | **arithmetic, not prose**: measured core-min per unit against the 768 cap, computed by the reader and printed | cap-stop ⇒ `NOT A RESULT` on the affected points. *(The same withdrawn claim applied here; A1WR enforces its cap in `a1wr_chain_driver.sh`. See §5.1.)* |
| `G-CONCURRENCY-PRECOND` | §4.6 — measured occupancy and MemAvailable recorded at launch and at every point boundary, from a census PROVED able to return non-empty | **refuse to launch only if the registered deadline does not cover the predicted rate AT THE MEASURED OCCUPANCY.** An empty box is NOT a launch condition — this item survives 3.543x solo and must not block the box. The test is arithmetic |
| `G-YPLUS` | measured y+ min/mean/max on the wall patch, every α | `GATE FAIL` if y+max ≥ 1.0 anywhere; refuse (exit 2) on a blind channel for a point that ran ≥ 200 iterations. **The mesh is NOT re-cut** (A1WR §3.4) — an overshoot is a registered outcome |
| `G-WALLTREAT` | `useWallFunction: False` in the staged script **and** `BCType=nutLowReWallFunction` in the solver log for the `wing` patch | refuse (exit 2) if the log does not confirm the BC that actually ran |
| `G-FIXTURE` | **every planted control's fixture is STATIC and independent of the run being graded** | refuse (exit 2) if any fixture is read from this item's own run root. **THE L-435 REPAIR** — see §6 |
| `G-STALL` | no output binds a stall word to a numeric angle | refuse (exit 2) on a planted claim; must NOT fire on the honest caveat |
| `G-NOBAND` | no output presents a value as grid-converged or inside a band | refuse (exit 2) — the L3 family still has no Roache triple |
| `G-IMG` / `G-FREEZE` | image id and `libidwarp` md5 exact; every instrument md5 checked at launch | refuse (exit 4) on any mismatch |

**Composition:** D19M's repaired `compose_item` from `verdict_before_ceiling`,
hard-gate list tested for **both** `GATE FAIL` and `NOT A RESULT`. Ceiling
`GATE REACHED`.

### 5.1 ⚠ A WITHDRAWN ACCUSATION — `G-COMPLETE` AND `G-CAPS` **ARE** IMPLEMENTED IN A1WR

An earlier draft of this document, and this lane's census, recorded that A1WR
registers `G-COMPLETE` and `G-CAPS` and never implemented them, on the evidence
that `grep -c 'G-COMPLETE' a1wr_read.py` returns 0. **That inference was wrong
and is withdrawn in full.**

Verification's §2v ruling is the standard, and it refused a specimen of exactly
this shape: *"a gate is implemented where it must be, not where the reader is —
the grading path is every frozen instrument the registration names, not the one
file with `analyse_` in its name."* Checked against every frozen A1WR instrument:

| gate | implemented at | the line |
|---|---|---|
| `G-COMPLETE` | `a1wr_runScript_incomp.py:357-362` | `AOA_SWEEP_TRUNCATED n_declared=%d n_executed=%d -- NOT a completion` then `exit(97)` |
| `G-COMPLETE` | `a1wr_cmd.sh:68-71` | counts `AOA_POINT_END` markers, `A1WR_COUNTS declared=… point_end_markers=…`; the PROBE branch exits 97 on a missing endTime state |
| `G-CAPS` | `a1wr_chain_driver.sh:251-257` | `CAN_DUP = 'YES' if I_SPEND + 55.0 <= ARM_CAP_MIN`, else `A1WR_DUP_CAPSTOP … A cap-stop is NOT A RESULT on that control.` |

**And it fired LIVE.** All six A1WR cold controls carry the truncation marker in
their docker logs and exited **97** on it. It did **not** fire for the two
sweeps — because the 02:25:05Z SIGTERM killed the containers before the unit-end
block ran (no `sweep_*.docker.log` exists; `AOA_SWEEP_END` appears **0** times in
either sweep log). **A gate whose host process was killed is not an unimplemented
gate**, and conflating the two is how a false accusation gets made.

**What survives, narrowly:** `a1wr_read.py` does not itself name or adjudicate
either gate — it prints a bare `COUNT MISMATCH` and returns 0. That is an
observation about one instrument's division of labour. Under §2v it is reported
**CLEAN**, not as a suspicion.

---

## 6. `G-FIXTURE` — THE L-435 REPAIR, AND WHY IT IS A GATE HERE

MAAOA's entire grading was voided because a control's fixture was a live
artifact of the run it was grading. **A1WR came within one converged point of
the same fate and nobody knew.** `a1wr_read.py:447-457` *prefers* a live
artifact: it scans the run's own `sweep.log`, takes the first segment
classifying `CONVERGED` **and** carrying a y+ line, and uses it as the control
base. It fell back to its synthetic fixture **only because no point in either
arm converged**. Had one converged, the grading would have carried the defect.

*(A second, smaller defect in the same path, reported for the successor's
reader: A1WR's provenance line prints `source: no sweep log on disk yet` while
parsing a 520,063-byte sweep log four lines later — the `not is_file()` branch's
note reused for the "log present, nothing converged" case.)*

**REGISTERED: this item's reader takes its control fixtures ONLY from static
bytes committed with the reader, and refuses at exit 2 if any fixture path
resolves inside this item's run root.** The provenance line must state the
fixture's origin and its sha256, and must be true about the disk.

Per `CLAUDE.md` rule 3, every reader that can return a zero or an absence is
driven with a live planted perturbation on the static fixture, read back through
the **real** reader function, refusing at exit 2 if the reader cannot see it —
and **every control reads the target bytes before mutating, asserts the bytes
actually changed, drives the real reader, asserts the verdict flipped, restores,
and re-asserts the restore landed.** A no-op mutation followed by a passing check
is a control that proves nothing (A1WR §10).

**And the control that this item's own §3.2 anchor demands:** the convergence
channel must be shown able to read a **real** `Minimal residual … satisfied the
prescribed tolerance 1e-08` off real bytes, not only off a fixture. Three such
logs exist on this box and are named in `A1WR_STAGE12_RESULTS.md` §3.2, one of
them on this very mesh, image and solver.

---

## 7. WHAT THIS ITEM MAY NOT CONCLUDE

- **`FEASIBILITY`.** The L3 family has no Roache triple. **No value carries a
  band, none is grid-converged, and `PASS` against a threshold is unavailable**
  on any physical quantity. Ceiling `GATE REACHED`.
- **NO STALL ANGLE IS REPORTED AND NONE MAY BE DERIVED.** `G-STALL` refuses at
  exit 2 on any output binding such a word to a numeric angle. **The tail is
  exactly where that temptation lives**, which is why the gate is carried here
  unweakened.
- **A non-converged point is not evidence of separation** — it is evidence that
  the steady solver stopped converging, reported with its residual history.
- **A converged high-α point is not evidence of attached flow.** 2-D steady RANS
  with SA past the onset of significant separation is not a valid model of the
  flow at **any** resolution.
- **⚠ REGISTERED AS A KNOWN PROPERTY OF THE `symmetry` CONFIGURATION, NOT AS AN
  EXPECTATION — AND IT IS WHY THE PATCH IS REPAIRED. U1 (`symmetry`) WILL READ
  `NOT CONVERGED`. U2 AND U3 (`empty`) ARE EXPECTED TO CONVERGE.**

  The mesh's two bounding planes are **`type symmetry`, not `empty`** — measured
  in `constant/polyMesh/boundary`, 130,304 faces each — so OpenFOAM reports
  **`Mesh has 3 solution (non-empty) directions (1 1 1)`** and assembles a
  **z-momentum equation on a mesh one cell thick**. `U2` therefore floors instead
  of converging. Measured on `A1WR sweep_I` across all 559 print steps:

  | channel | minimum `initRes` reached, whole run |
  |---|---|
  | U0 | 1.429824e-09 |
  | U1 | 1.738461e-09 |
  | p | 2.589369e-09 |
  | nuTilda | 8.288244e-09 |
  | **U2** | **3.238410e-08** |

  **Every channel but `U2` gets below 1e-8. `U2` never does.** It is the largest
  last-iteration residual at **12 of the 14** points, and its floor of
  **3.238e-08 sits ABOVE the registered `primalMinResTol = 1.0e-8`.**

  **So A1WR's thirteen points could never have converged, and neither can U1's.
  That is arithmetic, not a forecast.** Corroborated on `MAAOA INCOMP`
  (`U2` 2.48e-08) and on the coarse 4,032-cell mesh (~1.7e-10, i.e. the floor
  scales with the mesh); killed for the compressible arm, where `p` at 9.29e-01
  dominates and the mechanism is the separate one N-C9 documents.

  **AND THE OTHER HALF OF THE MECHANISM, READ FROM THE INSTALLED SOURCE RATHER
  THAN INFERRED — IT IS WHY THE LEDGER SAID `err=NONE` WITH ZERO CONVERGENCES.**
  `DASolver.C:188` stops early only when `primalMaxRes < primalMinResTol`
  (1.0e-8). `DASolver.C:2745` raises `Primal solution failed!` only when
  `primalMaxRes / primalMinResTol > primalMinResTolDiff`, and this item's
  registered `primalMinResTolDiff` is **100** — i.e. only above **1.0e-6**.
  **There is a deliberate 100× DEAD BAND between the two thresholds, and the
  measured floor of 3.238e-08 sits inside it** — 3.24× the tolerance, 0.0324× the
  failure threshold. **A1WR's arm I could neither converge nor be flagged as
  failed. That is the whole explanation of the "13 clean rows, all `error NONE`"
  that had zero convergences**, and it is registered here so this item's reader
  cannot repeat the misreading.

  **⚠ WITHDRAWN, AND THIS WOULD HAVE COST 288 CORE-MIN TO LEARN THE OTHER WAY.**
  An earlier version of this clause registered that the `empty` units are
  *expected to converge*, because removing the z-momentum equation removes the
  `U2` residual that floors. **That premise is FALSE, and the source says so.**

  `primalMaxRes` is **not** the max over the velocity components. **`U2` never
  entered the convergence criterion at all** — from α = 2 upward it is the
  *largest* of the three components, and the criterion discards it.

  **THE EVIDENCE, IN TWO INDEPENDENT FORMS, AND THEY ARE NOT OF EQUAL STANDING:**

  1. **BEHAVIOURAL, AND IT NEEDS NO SOURCE AT ALL — this is the load-bearing
     one.** On D19T
     (`/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening/`)
     arm T10's `U2` **floor** over the whole run is **1.7164e-10, i.e. 1.72×
     ABOVE its own 1e-10 tolerance**, and that arm nevertheless **declared
     convergence 22 times at ~9.0e-11**. A maximum over a set cannot fall below
     the minimum ever attained by a member, so **`U2` is not a member of the
     declared quantity.** Corroborated on the binding channel: in D19T's
     converging arms the declared number **is** `he`'s floor to four significant
     figures (T08 `he` 9.0893e-09 vs declared 9.0871e-09; T10 `he` 9.0350e-11 vs
     declared 9.0384e-11). **Verified by the supervisor personally, from logs
     that are on disk and will stay there.**
  2. **SOURCE-LEVEL, AND ITS CITATION IS WEAKER THAN ITS CONTENT.** The vector
     branch builds `scalarList initResList = {initRes[0], initRes[1],
     initRes[2]}`, calls `sort(initResList)`, and tests **`initResList[1]` — the
     MEDIAN of the three** — against `primalMaxRes`; the comment beside it says
     it exists precisely *"because we often need to run 2D simulations with
     symmetry BC"* so that *"one component of the residual vector … may be high
     while the other two components' residuals are low."* So
     `primalMaxRes` = max( **MEDIAN**(U0,U1,U2), p, nuTilda ).
     **Read at source by this lane, not relayed**, in
     `src/adjoint/DAUtility/DAUtility.C` (comment at :775-779, `sort` at :784,
     the median test at :786-788), **md5 `d5fb5b0a781b11a780133901a8c2241c`,
     863 lines.**
     **⚠ AND THE HONEST LIMIT ON THAT CITATION: the file is NOT in this
     repository and NOT anywhere durable on this box.** The only host-visible
     copy is an extraction under the session scratchpad, which `CLAUDE.md`
     rule 13 forbids this document to cite and which has been wiped three times
     in a day. Its durable home is **inside the pinned image
     `dafoam-idwarp-rot:v1`, `sha256:2927768a16ac…`**, whose absolute in-image
     path this lane did **not** verify, because verifying it means invoking
     `docker` and this item's lane is forbidden to. **The md5 above is what a
     successor re-checks against; the line numbers are this lane's read of that
     md5 and nothing else.** *(The earlier citation `DAUtility.C:762-790` in
     this document was a different lane's line numbering and did not match the
     bytes; it is replaced by the md5-anchored form above.)* **Limb 1 does not
     depend on any of this, and the registration below rests on limb 1.**

  **MEASURED on A1WR's `sweep_I` log by this lane, re-derived independently for
  this freeze.** Binding channel **at each point's LAST print step** (the
  definition matters and is stated so the count is checkable):
  **`nuTilda` at 7 of the 14 points, the median-of-`U` at 7, `p` at NONE, and
  `U2` at NONE.** `U2` **is** the largest of the three `U` components at
  **12 of the 14** points — every point except α = 0 and α = 1 — and the median
  discards it at all twelve. *(An earlier draft of this line read "`nuTilda` at
  8 of 14 points and the median-of-`U` at 6". **Corrected here before compute:**
  the measured split is 7 and 7. The claim that `U2` binds at NONE, which is the
  one the registration rests on, is unaffected and is confirmed.)*

  Per-α projection of the `empty` case, taking the z-residual to zero so the
  median of `{0, U0, U1}` becomes `min(U0,U1)`, i.e.
  `primalMaxRes` → max( min(U0,U1), p, nuTilda ):

  | α | projected `primalMaxRes` (`empty`) |
  |---|---|
  | **1 — the closest to tolerance** | **1.0182e-08** (a factor of **1.02**) |
  | 2…11 | 1.12e-08 … 1.59e-08 |
  | **12 — the largest of α 1…12** | **2.7954e-08** |
  | 0 | 2.2632e-07 |
  | **13 — killed at 2,500 of 4,000 iterations, 26 print steps not 41** | **4.1455e-07** |

  **Across α 1…12 the projection runs 1.0182e-08 … 2.7954e-08, and EVERY ONE OF
  ALL FOURTEEN POINTS IS ABOVE 1.0e-8.** *(An earlier draft of this line read
  "1.02e-08 … 2.80e-07 across α 1…13". **Two errors, both corrected here before
  compute:** the upper end was a decade wrong — 2.80e-07 for 2.7954e-**08** —
  and the range was labelled α 1…13 when α = 13's own projection is 4.1455e-07,
  outside the interval quoted. Fixing only the decade would have made the line
  false in a new way, which is why the whole line was re-measured rather than
  patched. α = 0 at 2.2632e-07 is likewise outside the quoted range and is
  stated separately.)*

  **REGISTERED, THEREFORE: U2 AND U3 ARE EXPECTED *NOT* TO CONVERGE EITHER.**
  The patch repair is still correct — a `symmetry` bounding plane on a one-cell
  mesh is a genuine defect and assembling a spurious equation is wrong whatever
  the residual bookkeeping does with it — **but it must NOT be sold as the thing
  that makes the solve converge.** It is not.

  **The honest projection is registered as a projection**: it assumes the other
  channels are unchanged by the patch swap, which they will not be exactly, since
  removing an equation changes the coupled system. The margins are factors of
  **1.02–41.5** above 1e-8 (α = 1 at the tight end, α = 13 at the loose), not
  orders at the tight end, so the swap alone is very unlikely to drop every
  channel below 1e-8. **If the `empty` units DO converge, that is a finding about the
  coupling and is reported as one** — it is not the outcome this document
  predicts.

  **AND THE CLAUSE THAT MATTERS MOST: none of this licenses relaxing anything.**
  It does not license raising `endTime`, **it does not license relaxing 1.0e-8 to
  1e-7 to manufacture a convergence**, it does not license widening
  `primalMinResTolDiff`, and it does not license re-tuning. A successor reading
  this page will reach for exactly one of those; each is result-shopping, all are
  forbidden on this item, and a different tolerance or iteration budget is a
  **NEW rung with its own pre-registration.** **The repair is to the mesh's patch
  identity — a defect — and to nothing else.**

- **`G-REPRO` KEEPS ITS VALIDITY BECAUSE U1 KEEPS A1WR's CONFIGURATION.** U1 runs
  on `symmetry`, cold, with the frozen numerics unchanged, so the cold-vs-
  continued comparison against A1WR's own continued α = 12 moves exactly one
  variable. **The patch repair does not contaminate it, because the repair lives
  in U2, and U1-vs-U2 is the separate one-variable pair that measures the repair
  itself** (§3.5). That is what the eighth point buys.

- **REGISTERED CONSEQUENCE, NOW SPLIT BY UNIT BECAUSE THE UNITS DIFFER:**
  **U1's** coefficients are an iteration-4,000 state on a configuration with a
  measured residual floor of 3.238e-08 and **may not be presented as a converged
  value** — only its extrapolated plateau, labelled EXTRAPOLATED, enters §3.5.
  **U2 and U3's** coefficients may be presented as converged **only if the solver
  actually printed its own `Minimal residual … satisfied the prescribed
  tolerance 1e-08` line for that point**; a point that instead ran to the cap is
  `NOT CONVERGED` like any other, expectation notwithstanding. **`G-NOBAND`
  independently forbids presenting ANY value of this item as grid-converged or
  inside a band** — the L3 family still has no Roache triple. **The two
  prohibitions are separate and both bind.**
- **No adjoint claim.** Primal only, undeformed geometry, no optimiser, no trim.
- **The build confound stands and is restated:** the coarse sweeps ran the
  SHIPPED image, this and A1WR run the PATCHED `dafoam-idwarp-rot:v1`.

---

## 8. OWED — WHAT THE FREEZE SETTLED AND WHAT IT DID NOT

**Updated at the freeze commit, 2026-09-03. `[DONE]` items were executed and
their evidence is named; `[OWED]` items gate the ENQUEUE, not the freeze.**

1. **`[OWED — AND IT IS THE ONE THAT GATES THE QUEUE] Supervisor's §3 check 4,
   personally**: the §4.3/§4.4 cap arithmetic and the §3.3/§3.5 control bands,
   read as arithmetic and not as a summary. **Not delegable, and a lane's
   arithmetic is not a substitute for it.** The queue row is drafted and PARKED
   outside `verification/queue/` until this lands.
2. **`[DONE]`** The **reader** written, with `G-COMPLETE` and `G-CAPS`
   implemented **in this item's reader** (§5) and `G-FIXTURE` enforced (§6).
   Every control driven: `python3 a1wrt_read.py --selftest` →
   **`SELFTEST PASS: 39 controls, both directions, mutation controls
   included`, rc = 0**. md5-pinned by the manifest in §0.
   *(Implemented in the reader for auditability, NOT because A1WR lacked
   them — §5.1 withdraws that claim.)*
   **`[OWED]` the driver and run-script staging are NOT written**; they are not
   part of this freeze and carry no gate, threshold, cap or label of their own.
3. **`[DONE]`** Run root `/home/ubuntu/certonomous-runs/A1WRT/` re-checked
   **ABSENT by execution in the freezing shell** at 2026-09-03T18:29Z — see the
   §0 banner. This is the condition under rule 2 limb 1 that made the freeze's
   own edits lawful.
4. Mesh, image and instrument md5s re-verified against the A1WR manifest in that
   same shell.
5. Queue entry drafted so the run is durable by construction — the deadline lives
   **inside the container**, so the cap stops the run even if the driver, the
   daemon and every agent die. **A1WR's own kill is the argument: the driver was
   polling healthily at 02:24:58Z and the box went down seven seconds later.**

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---

**Drafted 2026-09-03 by lab-lane (dafoam). No solver, container or queue entry
was launched, released or moved. Every figure above is read from an artifact
named beside it.**

---

## ADDENDUM 1 — 2026-09-03T19:06Z — THE SOURCE CITATION MADE DURABLE, AND THE LAUNCH PATH

**Document version 1.0 → 1.1.**
**Lines whose number changed above this section: 0.** This addendum is appended
at the foot; nothing above it was edited, and the assertion was verified by
diffing this file against its blob at the freeze commit `a62d8d75` — the only
hunk is this section, appended.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** It records
provenance and names the launch path. Every gate, band, cap, deadline and
verdict label registered above stands exactly as frozen.

### A1.1 The `DAUtility.C` citation, re-anchored on the pinned image

§7 cites the median form of `primalMaxRes` and this document was frozen carrying
an honest limit on that citation: the file was nowhere durable on this box, its
only host-visible copy was under the session scratchpad, which `CLAUDE.md`
rule 13 forbids this document to cite, and the lane that froze it could not
verify the in-image path because reading it means invoking `docker` and that
lane was forbidden to.

**The supervisor performed that read** — image identification is a supervisor act
under §6 — read-only, `--rm --network=none`, no mount, on **both** toolchain rows:

| row | image | id | `DAUtility.C` md5 |
|---|---|---|---|
| shipped | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd…` | `d5fb5b0a781b11a780133901a8c2241c` |
| **patched — the row THIS ITEM RUNS** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16ac…` | `d5fb5b0a781b11a780133901a8c2241c` |

**In-image path:
`/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DAUtility/DAUtility.C`**;
`sort(initResList)` at `:784`, `if (initResList[1] > primalMaxRes)` at `:786`,
`primalMaxRes = initResList[1]` at `:788`; the `<scalar>` overload's true max at
`:747-751`; the "2D simulations with symmetry BC" comment at `:775-780`.

**THE CORROBORATION IS WHAT MATTERS AND IT IS NOT A RESTATEMENT.** The md5 above
was reached **twice, independently**: by this lane reading the extracted bytes it
could see, and by the supervisor reading the file inside each image. **The two
agree to the digit, and the line numbers agree.** The citation is therefore now
anchored in a **durable, pinned home** — the image this item's own `G-IMG` gate
already refuses to run without — and no scratch path is cited.

**AND THE HALF THAT IS NEW EVIDENCE, NOT NEW WORDING:** the md5 is **identical in
the SHIPPED and the PATCHED rows**. The residual-bookkeeping behaviour §7 rests
on is therefore **measured to be the same in both builds**, rather than assumed
to transfer across the build confound this item registers at §7's closing bullet.

**What does NOT change:** §7's registration rests on the **behavioural** limb —
D19T arm T10's `U2` floor of 1.7164e-10 standing 1.72× above its own 1e-10
tolerance while that arm declared convergence 22 times at ~9.0e-11. That limb
needs no source read at all and remains the primary. The source limb is now
citable instead of being dropped; it was never the load-bearing one.

### A1.2 The launch path — `launch_cmd` is no longer null

The driver and its patch-identity instrument are written, and the parked queue
row's `launch_cmd` is filled in from them. **Both are pinned here:**

| instrument | md5 | role |
|---|---|---|
| `a1wrt_run_unit.sh` | `288bc6904f908eb852e024ca0d61762c` | the unit launcher — one unit, one container, one process, np 1 |
| `a1wrt_patch_assert.py` | `7f3a2c8e70684daba975ac9a2ee50385` | `G-PATCH` clauses 1 and 2, host-side and PRE-PRIMAL |

**Nothing in the launcher moves a registered number.** It **re-derives** the cap
frame at run time from §4.4's own registered form — `TMO = int(CAP × 60 / RANKS)
− 300`, asserted `> 0`, with the back-check `(TMO + 300) × RANKS / 60 == CAP`
inverted and re-added so no edit can silently widen the cap — and **executes**,
rather than trusting, the arithmetic this document already evaluated:

| unit | cap | TMO re-derived | `> 0` | back-check | ≤ cap |
|---|---|---|---|---|---|
| `alpha12_symmetry` | 361.0 | **21,360 s** | ✓ | 361.000000 | ✓ |
| `tail_empty` | 2943.0 | **176,280 s** | ✓ | 2943.000000 | ✓ |

**The frame allowance is 300 s and this document is its authority.** Three
constants live in this family and the difference is registered, not drift:
**A1WRT 300** (§4.4, 3.2× the MEASURED 93.85 s container start), D6R/D6RF 90,
A1/D19 60. A 60 s form was proposed for this item on 2026-09-03 and is **not
this item's registered form**; the launcher uses 300 and says so on its face.

**The ITEM CEILING is asserted before every unit** against the ledger's own
accumulated spend, and a ledger that exists but cannot be parsed is `UNMEASURED`
and **refuses** — an unknown prior spend plus this unit's cap cannot be shown to
fit under 3,304 core-min, and a zero meaning "could not read" is a planted zero.
Note for the reader: 361 + 2943 = **3,304 exactly**, so the ceiling is the sum of
the two caps and can only refuse when a unit has already overrun.

**`G-OCC` RECORDS AND QUEUES; IT NEVER REFUSES.** `G-QUIET`'s refuse-to-launch
form is ruled out of this family (dafoam-supervisor, 2026-09-03). §4.6's refusal
arithmetic is still **computed and printed** — break-even 11.571× solo for U1 and
13.642× for U2+U3, against a worst measured box occupancy of 3.859× — because the
arithmetic is the finding even where it never fires. Where the box is busy the
launcher **queues, boundedly (30 min), and then launches anyway with the mismatch
RECORDED AS A PREDICTION**, per Sanaa's 2026-09-03 ~21:00Z rule: pre-registration
predicts, the monitor watches, the grader judges afterward on the certificate.

**One integration defect was found and fixed in the launcher, not in the frozen
grader.** `a1wrt_read.py:965-966` reads `<run>/tail_empty/out/rc` and treats its
**absence as a REFUSAL**, not as a pass. The launcher now writes that artefact
from **the kernel's** exit code — `docker inspect .State.ExitCode`, taken before
`docker rm`, never from `$?` of a `timeout` or `setsid` line — and reads it back
and asserts it landed. Found by reading the frozen grader, not by watching a
graded run refuse at exit 2.

**STILL OWED, AND IT STILL GATES THE ENQUEUE:** the supervisor's §3 check 4, and
a personal diff read of the launcher. **Nothing has been launched, enqueued or
released. Zero compute has been spent on this item.**

---

## ADDENDUM 2 — 2026-09-03T20:40Z — THE 19:38Z ABORT, THE controlDict A1WRT NOW WRITES, AND THE FFD IT WAS NEVER STAGING

**Document version 1.1 → 1.2.**
**Lines whose number changed above this section: 0.** This addendum is appended
at the foot and nothing above it was edited. **The figure is COMPUTED, not
claimed:** in the amending invocation the first 1,060 lines of this file — its
entire length before this append — were compared byte-for-byte against its blob
at `HEAD` and are identical; the only hunk in `git diff` for this path is this
appended section. The pre-append length 1,060 is the same shell's `wc -l`.

**PRE-COMPUTE CONDITION, RE-CHECKED BY EXECUTION, TWICE:** the registered run
root `/home/ubuntu/certonomous-runs/A1WRT/` is **ABSENT** — `test -e` returned
**rc 1** at **2026-09-03T20:40:05Z**, and the check was re-run **inside the
appending invocation itself** at **2026-09-03T20:42:58Z**, which was written to
refuse the append outright had the root existed. Neither reading is from recall
and neither is the freeze's earlier one.

**AND THE FREEZE'S SECOND SENTENCE NO LONGER HOLDS, WHICH IS DISCLOSED RATHER
THAN REPEATED.** The freeze recorded that *no path matching `*A1WRT*` exists
anywhere under `/home/ubuntu/certonomous-runs/`*. **That is now false**, and this
addendum says so instead of reprinting the frozen sentence: exactly one such path
exists, `/home/ubuntu/certonomous-runs/A1WRT_ABORTED_S6_20260903T1938Z/`, the
staged tree of the aborted launch below, **moved and not deleted** under this
item's own no-`rm -rf` rule. What rule 2 limb 1 requires is that the registered
run root be absent, and it is.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.**

---

### A2.1 The launch attempt, disclosed — and why amending is still lawful

**A launch of this item was attempted at 2026-09-03T19:38:15Z and aborted at
19:38:26Z — eleven seconds.** It is disclosed here by name; this item is not
described as untouched.

The supervisor's ruling on lawfulness, carried here as his:

> The 2026-09-03T19:38:15Z launch attempt aborted at 11 s with `launcher_rc=5`,
> **created no container, produced no gate reading and no measurement, and cost
> ~0 core-min**. No gate could have been chosen to fit an answer that does not
> exist. The addendum is therefore lawful under rule 2 / rule 6, and it
> **discloses the launch attempt explicitly** rather than describing the item as
> untouched.

**The abort's own artefacts corroborate every limb of that, and they were read in
the amending invocation rather than taken from the report:**

| claim | artefact read | what it says |
|---|---|---|
| aborted at S6, both units | `A1WRT_ABORTED_S6_20260903T1938Z/{alpha12_symmetry,tail_empty}_STAGING_EVIDENCE.txt` | last line of each: `ABORT S6 controlDict endTime=1000, registered 4000` |
| `launcher_rc=5`, 11 s | `STATUS.queue.A1WRT` (untracked, beside this file) | `launcher_rc=5 end=2026-09-03T19:38:26Z` |
| **no container** | the same tree | **no `out/`, no `rc` artefact, no container log anywhere under it**; `ledger.txt` holds one line, `ITEM=A1WRT` |
| no gate reading | the same tree | staging stopped at S6, which is **before** `S7` (the image digest) and before any `docker run` |

**ADDENDUM 1's CLOSING SENTENCE IS STRUCK BY THIS ADDENDUM, NOT REWRITTEN.** It
reads *"Zero compute has been spent on this item."* — true when it was written at
19:06Z, false after 19:38Z. It stands unedited above and **this line is its
correction**; the true figure is below.

**Spend, gross:** two units × 11 s wall × 1 rank ≈ **0.37 core-min**, against an
`ITEM CEILING` of 3,304.0 — recorded, not absorbed. **No calibration row is
opened in `docs/COST_CALIBRATION.md`**: nothing completed, nothing was graded,
and a row against a process that produced no result would be a ratio with no
numerator.

---

### A2.2 (a) NO GATE, THRESHOLD, CAP OR LABEL MOVES — named unchanged

Naming them is the proof, so they are named rather than asserted:

| registered thing | value, as frozen | after this addendum |
|---|---|---|
| `endTime` / iteration budget | **4000**, §7, FROZEN | **4000**, unchanged |
| `primalMinResTol` | **1e-8**, §7, not relaxable | **1e-8**, unchanged |
| cap, `alpha12_symmetry` | **361.0** core-min | **361.0**, unchanged |
| cap, `tail_empty` | **2943.0** core-min | **2943.0**, unchanged |
| `ITEM CEILING` | **3304.0** core-min | **3304.0**, unchanged |
| frame allowance | **300 s** (§4.4) | **300 s**, unchanged |
| `TMO` re-derived | 21,360 s / 176,280 s | unchanged |
| ranks | **np = 1**, one unit one container | unchanged |
| toolchain row | **patched**, `dafoam-idwarp-rot:v1`, digest `sha256:2927768a16ac…` | unchanged |
| declared points | 1 and 7 | unchanged |
| `G-PATCH`, `G-REPRO`, `G-OCC`, `G-COLDSTART`, `G-STALL` | as frozen | **unchanged; none is re-anchored, re-worded or re-thresholded** |
| verdict labels | as frozen | unchanged |

**What this addendum changes is the STAGING, and only the staging.** Two inputs
the item was not putting on disk are now put on disk, and both are asserted
against A1WR's own bytes. No number in the table above is touched.

---

### A2.3 (b) WHAT A1WRT CONTROLS IN `system/controlDict`, AND WHAT IT INHERITS

**This distinction is the item's claim to being one variable, so it is written
out rather than left to a reader's inference.**

`S6` no longer asserts an inherited `controlDict`. It **writes** one, derived
from `a1wr_chain_driver.sh`'s own `stage_unit()` heredoc (`:126-154`) with `$et`
bound, and then **reads it back from disk through the same verifier**. So in the
literal sense A1WRT writes every byte of the file — and the honest split is
between the fields it **GATES** and the fields it merely **CARRIES**:

**CONTROLLED — written, then READ BACK FROM DISK and individually gated
(`a1wrt_controldict.py:verify`, and again in the launcher's own shell so the
launch record carries the three values itself):**

| field | registered value | gate |
|---|---|---|
| `endTime` | **4000** | `!= 4000` → REFUSE, naming §7's freeze |
| `writeInterval` | **4000** | `!= 4000` → REFUSE (without it the `endTime` state is never written and the age guard has nothing to date) |
| `deltaT` | **1** | `!= 1` → REFUSE |

An unreadable value in any of the three is **UNMEASURED and refuses**; it is
never defaulted to the registered number.

**INHERITED — carried verbatim from A1WR's heredoc, chosen by A1WR and not by
this item:** `startFrom startTime`, `startTime 0`, `stopAt endTime`,
`writeControl timeStep`, `purgeWrite 0`, `writeFormat ascii`,
`writePrecision 16`, `writeCompression on`, `timeFormat general`,
`timePrecision 16`, `runTimeModifiable true`,
`DebugSwitches { SolverPerformance 0; }`, and the `functions { yPlus1 … }` block.
**FROM WHERE, exactly:**
`cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/a1wr_chain_driver.sh:126-154`,
md5-pinned at `9bff59b63509e76d5dfa373a42a47074` inside the deriver — **if A1WR's
template moves, the derivation REFUSES rather than silently re-deriving.**

**These fourteen are not left ungated; they are gated as a BLOCK, and by a
stronger check than a field test.** The derived bytes are asserted **byte-identical
to the `controlDict` A1WR's driver ACTUALLY WROTE** for the sweep this tail
extends — `/home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_I/case/system/controlDict`,
md5 `85656349b8c31277e51883d2df9f8217`, 653 bytes — an external artefact this
instrument did not produce. Where the reference is unavailable the note says
**UNMEASURED**; where the endTime is not the registered one it says **NOT
COMPARED**; it claims a comparison only when one was made.

**THE REST OF THE CASE IS INHERITED FROM A1WR'S `L3` MESH DIRECTORY** (`cp -a`
at `S2`), and the inheritance was MEASURED against `sweep_I/case` in the amending
invocation rather than assumed:

| inherited file | `L3` vs `sweep_I/case` |
|---|---|
| `constant/polyMesh/points.gz` | **IDENTICAL** `7dab2ae9bd9d719757f7b9f555269d3f` |
| `system/fvSchemes` | **IDENTICAL** `f8c63ea5edf64abb6f4de333ceee60df` |
| `system/fvSolution` | **IDENTICAL** `68aff91e03f2d622fcb8b02a9c894c69` |
| `system/createPatchDict` | **IDENTICAL** `5e89709961881491e3f05dc97bbcf75c` |
| `constant/transportProperties` | **IDENTICAL** `931e6f0f1e263e04eed2ff0a513b2463` |
| `constant/turbulenceProperties` | **IDENTICAL** `8c78a44cd53f17e62cd71eac0e67585d` |
| `0.orig/{U,p,nut,nuTilda,k,omega,epsilon}` | **IDENTICAL**, all seven |
| `system/controlDict` | **DIFFERS** — `endTime 1000` vs `4000`. This is the defect the 19:38Z abort caught, and `S6` now writes over it. |
| `system/decomposeParDict` | **DIFFERS — DISCLOSED, NOT REPAIRED** (below) |

**`system/decomposeParDict` DIFFERS AND IS DISCLOSED HERE RATHER THAN QUIETLY
FIXED.** `L3`'s copy carries `numberOfSubdomains 2` plus a `kahipCoeffs` block;
`sweep_I`'s carries `numberOfSubdomains 1` and no such block
(`c3f5f05d45f0b9a70d645b107a837727` vs `e6f1b0060944bc86d6dff56480ad2bd4`, the
latter identical to the incompressible skeleton's, so `sweep_I` inherited the
skeleton's and A1WR's driver never wrote one). **It is the same defect class as
the `controlDict`: `L3` is a mesh-generation directory and its `system/` is
mesh-generation furniture.** It is argued **inert** here, and the argument is
stated so it can be attacked: `decomposePar` appears **zero times** in both
`a1wr_cmd.sh` and `a1wr_runScript_incomp.py`, this item runs **np = 1**
(`RANKS=1`, `--cpus=1`, one container one process), and no decomposition is
therefore performed. **What is NOT established:** that pyDAFoam never reads the
dictionary internally — proving that needs a container, which this amendment did
not open. **`DAFOAM_CHARTER` §5 makes decomposition a first-class disclosure, so
it is disclosed as an open inherited difference rather than counted as clean, and
whether `S6` should write it too is left to the supervisor.**

---

### A2.4 (c) THE FFD, AND WHY STAGING IT MOVES NO VARIABLE

`a1wr_runScript_incomp.py:129` constructs `OM_DVGEOCOMP(file="FFD/wingFFD.xyz")`.
**It is the producer's only external file input** — measured: that is the sole
`file=`/`open(` reference to an input path in the whole producer — and it is
**resolved relative to the container's cwd**, which `a1wr_cmd.sh:29` sets with
`cd /mnt/case`, which this launcher mounts as `-v "$WORK":/mnt/case`. So the
staged copy must land at `$WORK/FFD/wingFFD.xyz`, and it now does.

**A1WR's `L3` mesh directory has no `FFD/` at all.** A1WR never hit this because
`stage_unit()` copies a case **skeleton** and overlays `L3`'s `polyMesh`; A1WRT
stages **from the mesh directory**, which carries the mesh and the fields but not
the case furniture. The staging introduced the gap.

**Registered source and its md5:**

| | |
|---|---|
| `FFD_SRC` | `/home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_I/case/FFD/wingFFD.xyz` |
| `MD5_FFD` | **`6ddf378b028d03d8a18270488bee1759`** |

**IT MOVES NO VARIABLE, AND THE EVIDENCE IS A CENSUS RATHER THAN A SAMPLE.**
**Thirteen** copies of `wingFFD.xyz` exist on this box and **all thirteen carry
that one md5**: A1WR's nine `STAGE12` unit cases (`sweep_I`, `sweep_C`,
`cold_{I,C}_{4,14,17}`, `probe_I`, `probe_C`), the three cases in its two
failed-staging roots, and the incompressible skeleton A1WR's own driver copies
from (`a1wr_chain_driver.sh:33`, `SKEL_I`). **Staging it restores an input A1WR
always had; it does not introduce one.**

**Why `sweep_I` and not another path, since the bytes cannot differ today.** The
choice is made on provenance and on source count. `sweep_I/case` **is** the
alpha 0..12 incompressible sweep this tail extends — driver `:239`, `CONTINUED`,
tol `1.0e-8`, `endTime 4000`, the exact configuration `G-REPRO` compares
against — so these are the bytes the **body's own numbers** were produced with,
not a template they were copied from. It is also inside A1WR's preserved run
root, which this launcher already treats as its single read-only source
(`MESH_SRC`, and `G-ROOT.1a` names that root by name); `SKEL_I` would be a
**second** external source and is a live curriculum directory another item may
restage.

**`S5b` asserts the md5 on BOTH SIDES of the copy** — source and staged
destination — so a corrupt source and a corrupt copy are distinct refusals.

---

### A2.5 (d) THE FFD DEFECT WAS MASKED BY `S6` — ONE ABORT SURFACED TWO BLOCKERS

**The 19:38Z abort stopped at `S6`, which sits before the primal.** The missing
FFD could only have failed **inside the container**, at
`a1wr_runScript_incomp.py:129`, after `docker run` — and `a1wr_cmd.sh`'s own
point-of-use guards (`:31-33`: `runScript.py`, `0.orig`, `points.gz`) **do not
check for the FFD**, so nothing before the model build would have caught it.

**So the `controlDict` refusal bought the second finding.** Had `S6` inherited
the wrong `endTime` quietly, the launch would have proceeded to a container that
died building its model — and the two defects would have been found one at a
time, the second one having spent real core-minutes to be found. **One abort at
11 s and ~0 core-min surfaced two blockers, and that is recorded as the value of
refusing early rather than as a nuisance.**

**This also means `S5b` was never exercised by the 19:38Z attempt.** It is new
and unexercised by any launch, which is why it is driven directly — see A2.6.

---

### A2.6 (e) THE INSTRUMENT PINS, AND THE DRIVEN EVIDENCE BEHIND THEM

**PINNED AS FROZEN INSTRUMENTS OF THIS ITEM, at their post-repair bytes:**

| instrument | md5 | role |
|---|---|---|
| `a1wrt_controldict.py` | **`a77c9bac486dce940707bdf9c00e1a6b`** | **new** — the `controlDict` **deriver**: derives A1WR's own bytes, writes them, reads them back. `S6`'s whole content. |
| `a1wrt_run_unit.sh` | **`718b5d47bdc857e074c1f6e6fa18f24f`** | the unit launcher, repaired. Supersedes ADDENDUM 1's `288bc6904f908eb852e024ca0d61762c`, which is the pre-repair blob and remains the correct pin for that addendum's text. |
| `a1wrt_read.py` | `705db5f7e972f6c033cbe303b7a6038f` | **unchanged** — the grading path did not move |
| `a1wrt_patch_assert.py` | `7f3a2c8e70684daba975ac9a2ee50385` | **unchanged** |

**The grading path is untouched.** `a1wrt_read.py` carries the same md5 the
freeze pinned. Nothing in this addendum reaches the grader.

**`a1wrt_controldict.py` IS ITSELF PINNED AND DRIVEN AT LAUNCH, at a new `S0b`,
on the same argument `S0` already makes for the patch instrument.** `S6` both
writes the control dictionary with this code and reads it back with it, so a
broken deriver would agree with its own bad bytes; an instrument trusted from a
selftest that passed once at freeze time is not evidence about this box at this
moment. `S0b` refuses on **exit 4** if the md5 has moved and on **exit 6** if the
instrument fails its own controls. **Exit 6 is added to the launcher's registered
exit-code table** and is the deriver's own `RC_CD_REFUSAL`, so the launcher and
the instrument agree on one number.

**DRIVEN EVIDENCE, all zero-container and taken in the amending session:**

| suite | interpreter | result |
|---|---|---|
| `a1wrt_controldict.py --selftest` | `python3` / `python3 -O` | **13/13 PASS**, 0 FAIL, **0 NOT RUN**, rc 0 in both |
| `a1wrt_patch_assert.py --selftest` | `python3` / `python3 -O` | **11/11 PASS**, rc 0 in both |
| `a1wrt_read.py --selftest` | `python3` / `python3 -O` | **39/39 PASS**, rc 0 in both |
| `S5b` block, extracted from the launcher's own bytes | `bash -u` | **5/5 legs as registered** |
| `S0b` block, extracted from the launcher's own bytes | `bash -u` | **3/3 legs as registered** |

`S5b`'s five legs: an **undefined** `FFD_SRC` under `set -u` (rc 127, outside the
registered exit-code set, and the staging evidence file **empty** — no
`stage_say` ran); an **absent** source (rc 5, naming the path and
`runScript:129`); a **corrupted** source (rc 4, "the geometry parametrisation has
MOVED"); a copy that **lands corrupted** (rc 4, "the copy did not land intact");
and the **correct** source (rc 0, staged copy re-read at the pinned md5).
`S0b`'s three: correct pin and instrument (rc 0), a **wrong** pin (rc 4), and a
**mutated** deriver whose pin matches but whose own controls fail (rc 6).

**Two controls were added to the deriver because a note claimed a comparison it
had not made.** Its external-corroboration branch was guarded on the reference
file merely existing while the comparison itself additionally required the
registered `endTime` — so at any other `endTime` **no comparison ran and the note
still read "BYTE-IDENTICAL to A1WR's own generated controlDict"**. A guard that
reports a property it did not check is a defect in its own right, even though
`verify()`'s field assertions would have caught a wrong `endTime` a moment
later: **the later guard's catch is not this guard's evidence.** The branch now
answers **COMPARED**, **NOT COMPARED** (with the reason) or **UNMEASURED**, and
both directions are driven — `D12` fails against the pre-repair form, `D13` fails
against a "repair" that merely deletes the sentence. Both were confirmed by
planting each form and driving it.

**One control was demoted, not repaired.** `D2` previously took `chk(..., True,
…)` when the external reference was absent — a PASS awarded on a literal that
cannot fail, the same vacuous shape one frame up. A control with nothing to
compare is now **NOT RUN**, counted in its own column and never folded into
either PASS or FAIL, and the selftest's closing line names the NOT RUN count
explicitly rather than leaving a reader to subtract.

---

### A2.7 WHAT IS STILL OWED, AND THE ITEM IS STILL NOT ENQUEUED

**Nothing has been launched, enqueued or released by this addendum.** The
registered run root is absent, asserted by execution above.

**Still owed, and it still gates the enqueue:** the supervisor's §3 check 1 — a
**personal diff read** of the changed hunks in `a1wrt_run_unit.sh` and of
`a1wrt_controldict.py` — and check 4, the freeze blob against disk against
`HEAD`. Neither is a lane's to perform on his behalf. **Open and referred to
him:** whether `S6` should also write `system/decomposeParDict`, per A2.3.

---

## ADDENDUM 3 — 2026-09-03T20:47Z — A CENSUS FIGURE IN ADDENDUM 2 WAS WRONG AND IS CORRECTED HERE

**Document version 1.2 → 1.3.**
**Lines whose number changed above this section: 0.** Appended at the foot;
nothing above was edited, **and the figure is COMPUTED, not claimed** — in the
amending invocation the first 1,375 lines of this file, its entire length before
this append, were compared byte-for-byte against its blob at `HEAD` and are
identical, and `git diff` for this path shows one hunk with zero deleted lines.

**PRE-COMPUTE CONDITION, BY EXECUTION IN THE APPENDING INVOCATION:** the
registered run root `/home/ubuntu/certonomous-runs/A1WRT/` is **ABSENT**; the
appending shell was written to refuse the append had it existed.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Every value
in ADDENDUM 2's §A2.2 table stands. What it corrects is a **count**, and the
correction makes the claim narrower, not wider.

### A3.1 The error, stated as mine

**ADDENDUM 2 §A2.4 says: *"Thirteen copies of `wingFFD.xyz` exist on this box and
all thirteen carry that one md5."* THAT SENTENCE IS FALSE AND IT IS STRUCK.** The
lane that wrote it ran its census with `find` rooted at
`/home/ubuntu/certonomous-runs/A1WR`, got 13, and then reported the figure as
*"on this box"*. It is the error this lab names by its own rule — **asking what a
glob cannot see** — committed inside a sentence whose whole purpose was to be a
census rather than a sample. Its own enumeration did not even add up: it listed
*"nine STAGE12 unit cases"* plus three plus one, which is thirteen only because
the nine is also wrong.

### A3.2 The measured figures, box-wide and scoped

**BOX-WIDE**, `find /home/ubuntu -name wingFFD.xyz` excluding `.git`:

| | |
|---|---|
| files named `wingFFD.xyz` | **484** |
| **distinct md5s among them** | **9** |
| carrying `6ddf378b028d03d8a18270488bee1759` | **284** |

**So these bytes are NOT globally unique, and nothing in this item's argument
requires them to be** — a different geometry gets a different FFD, and the other
eight hashes belong to the M6, CRM, RAE2822 and tutorial cases.

**SCOPED — and the scope is the whole claim.** Inside **A1WR's own preserved run
root**, `/home/ubuntu/certonomous-runs/A1WR/`:

| where | files | md5 |
|---|---|---|
| `STAGE12/` unit cases — `sweep_I`, `sweep_C`, `cold_{I,C}_{4,14,17}`, `probe_I`, `probe_C` | **10** | all `6ddf378b028d03d8a18270488bee1759` |
| `STAGE12_failed_meshcheck_20260902T181325Z/` | **2** | same |
| `STAGE12_failed_staging_20260902T180915Z/` | **1** | same |
| **total inside A1WR's root** | **13** | **one md5, no exceptions** |
| plus `SKEL_I`, the incompressible skeleton the driver copies from (`a1wr_chain_driver.sh:33`) | **1** | same, giving **14** |

**THE ONE-VARIABLE ARGUMENT IS UNCHANGED AND IS NOW CORRECTLY SCOPED.** What it
needs is that the FFD does not vary *inside the item A1WRT is compared against*,
and that is measured: 13 of 13 within A1WR, 14 of 14 including the skeleton those
13 descend from. The registered `FFD_SRC` and `MD5_FFD` do not move.

### A3.3 `a1wrt_run_unit.sh` RE-PINNED, because the comment carrying the false figure was corrected

The launcher's `S5b` comment repeated the same wrong sentence, so it was
corrected to the scoped form and now states the box-wide 484/9 explicitly so no
reader can take the scoped claim for a global one.

| instrument | md5 | supersedes |
|---|---|---|
| `a1wrt_run_unit.sh` | **`0b00f8bf8d4425131c37bc585e249f4e`** | ADDENDUM 2's `718b5d47bdc857e074c1f6e6fa18f24f`, which remains the correct pin for that addendum's text |

**Comment text only — no executable line changed.** `bash -n` passes, and the
`S5b` guard block was **re-driven after the edit: 5/5 legs as registered**, the
same five as ADDENDUM 2 §A2.6. `a1wrt_controldict.py` is untouched at
`a77c9bac486dce940707bdf9c00e1a6b`, and the grading path `a1wrt_read.py` remains
`705db5f7e972f6c033cbe303b7a6038f`. **Still not enqueued, still not launched.**

---

## ADDENDUM 4 — 2026-09-03T20:56Z — THE INHERITED SET CLOSED AND ENUMERATED, `decomposeParDict` STAGED, AND THE GUARD SUITE MADE A COMMITTED ARTEFACT

**Document version 1.3 → 1.4.**
**Lines whose number changed above this section: 0** — **COMPUTED, not claimed:**
in the appending invocation the first **1,452** lines of this file, its entire
length before this append, were compared byte-for-byte against its blob at `HEAD`
and are identical; `git diff` for this path shows **one hunk, zero deleted
lines**.

**PRE-COMPUTE CONDITION, BY EXECUTION IN THE APPENDING INVOCATION:** the
registered run root `/home/ubuntu/certonomous-runs/A1WRT/` is **ABSENT**; the
appending shell was written to refuse the append outright had it existed.

**Landed on the dafoam-supervisor's ruling of 2026-09-03**, which discharged
check 1 and check 4 on ADDENDUM 2/3's work and ordered this pass.

### A4.1 NO GATE, THRESHOLD, CAP OR LABEL MOVES — named unchanged, again

`endTime` **4000** · `primalMinResTol` **1e-8** · caps **361.0** and **2943.0** ·
`ITEM CEILING` **3304.0** · frame allowance **300 s** · `TMO` **21,360 s** and
**176,280 s** · ranks **np = 1** · toolchain row **patched**,
`dafoam-idwarp-rot:v1`, digest `sha256:2927768a16ac…` · declared points **1** and
**7** · `G-PATCH`, `G-REPRO`, `G-OCC`, `G-COLDSTART`, `G-STALL` **as frozen, none
re-anchored, re-worded or re-thresholded** · verdict labels **as frozen**.
**Every one unchanged.** What moves is the staging and the registered
controlled/inherited split, which A4.3 rewrites in full.

---

### A4.2 THE CLOSED SET — every file A1WRT inherits from `L3`, enumerated

**Two second-variable candidates had been found in `L3/system/` and both were
found REACTIVELY, by something else tripping first.** That set had never been
enumerated. It is enumerated here and registered as **closed**.

**THE ENUMERATOR, stated so a successor re-runs it rather than trusts it.**
`A1WRT` inherits exactly what `cp -a "$MESH_SRC" "$WORK"` delivers at `S2`, where
`MESH_SRC=/home/ubuntu/certonomous-runs/A1WR/L3`. The path set is therefore
**`find /home/ubuntu/certonomous-runs/A1WR/L3 -type f`** — **31 files**, no
exclusions, `constant/polyMesh` included (9 of the 31) — each compared by md5
against the same relative path under
**`/home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_I/case`**, the run case whose
alpha 0..12 series this tail extends. **31 = 21 + 4 + 6**, and the three groups
below are exhaustive and disjoint.

**STATE (i) — BYTE-IDENTICAL, inherited, nothing to do. 21 files.**

| files | md5 |
|---|---|
| `0.orig/U` | `c6678d41923f6f1ee868da0a4d6e1a07` |
| `0.orig/p` | `9508b3825e96dc218c23a2351d1dc9b6` |
| `0.orig/nut` | `ba6041c403dfd7131b6dfb487bf3886f` |
| `0.orig/nuTilda` | `d0165ec400b2ab18309e8f17cfb73284` |
| `0.orig/k` | `1c065e15a59e811953be7963eeb20026` |
| `0.orig/omega` | `191f3f7bee9a531c767d3a816c1e5d72` |
| `0.orig/epsilon` | `f793e246c094d210cc6c0cedf584efc2` |
| `constant/polyMesh/points.gz` | `7dab2ae9bd9d719757f7b9f555269d3f` |
| `constant/polyMesh/faces.gz` | `bb644581c397733ea36b1999a84d598b` |
| `constant/polyMesh/owner.gz` | `71c37ed4cd7a757b2bb30f27fa436c16` |
| `constant/polyMesh/neighbour.gz` | `90e17aeb33c63f5b573e3ff44391ff90` |
| `constant/polyMesh/boundary` | `3a469a74b1adb167e145fe50e14790e6` |
| `constant/polyMesh/cellZones.gz` | `01003fa50e99eacae9e4078b1583b8aa` |
| `constant/polyMesh/faceZones.gz` | `c9c0f2a9389cdf8935e03c9f4597f39a` |
| `constant/polyMesh/pointZones.gz` | `dedc6402d08ae5fd038b0cff708fdd97` |
| `constant/polyMesh/sets/highAspectRatioCells.gz` | `4ed1ea026c2ce7cff7129b3eaee8b9db` |
| `constant/transportProperties` | `931e6f0f1e263e04eed2ff0a513b2463` |
| `constant/turbulenceProperties` | `8c78a44cd53f17e62cd71eac0e67585d` |
| `system/fvSchemes` | `f8c63ea5edf64abb6f4de333ceee60df` |
| `system/fvSolution` | `68aff91e03f2d622fcb8b02a9c894c69` |
| `system/createPatchDict` | `5e89709961881491e3f05dc97bbcf75c` |

**The mesh, the discretisation, the linear solvers, the fluid properties, the
turbulence model and every initial field are in this group.** Nothing in the
physics of the run is in any other group, and that is the finding.

**STATE (ii) — DIFFERS AND IS STAGED from A1WR's own bytes, md5-asserted on BOTH
sides of the copy. 2 files.**

| file | `L3` (inherited, WRONG) | staged from `sweep_I` | stage |
|---|---|---|---|
| `system/controlDict` | `46bb883cfc235d12df020bafbe3a9e78`, `endTime 1000` | `85656349b8c31277e51883d2df9f8217`, `endTime 4000` | **`S6`** — DERIVED from A1WR's own heredoc, written, read back |
| `system/decomposeParDict` | `c3f5f05d45f0b9a70d645b107a837727`, `numberOfSubdomains 2` + `kahipCoeffs` | `e6f1b0060944bc86d6dff56480ad2bd4`, `numberOfSubdomains 1` | **`S5c` — NEW in this addendum** |

Plus the input that was **absent altogether** and is staged at `S5b`:
`FFD/wingFFD.xyz`, `6ddf378b028d03d8a18270488bee1759`. `L3` has no `FFD/`, so it
appears in no row above; it is named here so the staged set is complete at three.

**`decomposeParDict` IS STAGED RATHER THAN ARGUED INERT, AND THE DIFFERENCE
MATTERS.** The inertness argument was available and is measured —
`decomposePar` appears **zero** times in both `a1wr_cmd.sh` and
`a1wr_runScript_incomp.py`, and this item runs np = 1 — but it **leaves the
question open**, because it rests on a claim about pyDAFoam's internals that
cannot be settled without opening a container. Staging **closes** it: whether
anything reads the dictionary stops mattering once A1WRT and the body it extends
carry identical bytes. **A removed variable beats a defended one.**

**And the direction of the repair is established, not assumed.** `sweep_I`'s
`decomposeParDict` is **byte-identical to the incompressible skeleton's**
(`/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible/case/system/decomposeParDict`,
same `e6f1b006…`), and A1WR's driver **never writes one** — `decompos` and
`numberOfSubdomains` appear zero times in `a1wr_chain_driver.sh`. So **`1` is
what A1WR actually ran**, and `L3`'s `2` is the odd one out: mesh-generation
furniture, exactly like `L3`'s `controlDict`. Staging makes A1WRT match A1WR; it
introduces nothing.

**STATE (iii) — DIFFERS OR IS EXTRA, AND IS INHERITED DELIBERATELY. 8 files.
THESE NEED THE SUPERVISOR'S SIGN-OFF BEFORE ENQUEUE.**

**(iii-a) Two files that DIFFER and are deliberately NOT staged:**

| file | `L3` | `sweep_I` |
|---|---|---|
| `surfaceMesh.xyz` | `022ee2e7ba89056b62b683f053a77491` | `ed3e2abaa49ebb8d83eeb1d032aaf405` |
| `volumeMesh.xyz` | `35d9f01d8f6b676083431c6dce9c5f92` | `406627551850708ea6f64f7057334f4d` |

**The argument, on the face of the registration, and it INVERTS the pattern of
the other two.** These are plot3d artefacts of mesh generation. **Nothing reads
them:** `surfaceMesh`, `volumeMesh` and `plot3d` appear **zero** times in
`a1wr_runScript_incomp.py`, **zero** times in `a1wr_cmd.sh` and **zero** times in
the frozen grader `a1wrt_read.py`; the single `.xyz` reference in the producer is
`FFD/wingFFD.xyz` at `:129`. **And `sweep_I`'s copies are the SKELETON's** —
byte-identical to `CURRICULUM-AOAI-…/case/{surfaceMesh,volumeMesh}.xyz` — i.e.
stale plot3d files describing the skeleton's mesh, left behind when
`stage_unit()` overlaid `L3`'s `polyMesh` on the skeleton. **`L3`'s copies are
the plot3d form of the mesh actually being run.** So here, uniquely, staging from
`sweep_I` would import files describing a **different mesh**, and inheriting
`L3`'s is correct on the merits rather than merely convenient. **Registered as a
deliberate divergence and referred for sign-off.**

**(iii-b) Six files present in `L3` and absent from A1WR's run case entirely:**
`log.autoPatch` `9a2f8e6fa9e3ead117555096647b9e08` · `log.checkMesh`
`44dbd5df2324a14482aa27374d81d756` · `log.createPatch`
`cfd4e38344af7342f49d2cd8ff76c6bd` · `log.genmesh`
`f75ba282195a7b16e95e8ba4e4affc6e` · `log.plot3dToFoam`
`5beba89ffd4a43d680132181f4e928bc` · `log.renumberMesh`
`966fb9589e205934e662b72417d49acd`.

**This is a fourth state and it is named rather than forced into the other
three.** They are not divergent bytes; they are **extra files A1WRT carries that
A1WR's run case never had**. `log.` appears **zero** times in the producer and in
`a1wr_cmd.sh`; the three hits in `a1wrt_read.py` (`:931`, `:951`, `:1038`) are
prose and local variables, not these files. They are `L3`'s mesh-generation
provenance and are kept for that reason. **Referred for sign-off with (iii-a).**

**THE SET IS NOW CLOSED.** 21 + 2 + 8 = 31, plus the one staged input `L3` never
had. Any future difference is a change to `L3` or to `sweep_I`, and both are
inside A1WR's preserved run root.

---

### A4.3 THE CONTROLLED / INHERITED SPLIT, REWRITTEN — it moved, so it is restated in full

**ADDENDUM 2 §A2.3's split is superseded by this section.** It is this item's
claim to being one-variable and cannot be true by omission.

**CONTROLLED — written or staged by A1WRT, and asserted:**

| what | how | assertion |
|---|---|---|
| `controlDict` `endTime` = **4000** | written (`S6`) | read back from disk, gated individually; unreadable ⇒ **UNMEASURED and refuses** |
| `controlDict` `writeInterval` = **4000** | written (`S6`) | as above |
| `controlDict` `deltaT` = **1** | written (`S6`) | as above |
| the **whole** `controlDict`, all 17 lines | derived from `a1wr_chain_driver.sh:126-154` | byte-identical to `85656349b8c31277e51883d2df9f8217`, A1WR's own generated file — **COMPARED / NOT COMPARED / UNMEASURED**, never a claim it did not make |
| `FFD/wingFFD.xyz` | staged (`S5b`) | md5 `6ddf378b…` on **both** sides of the copy |
| `system/decomposeParDict` | staged (`S5c`) | md5 `e6f1b006…` on **both** sides of the copy |

**INHERITED — the 21 files of state (i)**, byte-identical to A1WR's own run case,
from `L3` via `cp -a` at `S2`. **The fourteen non-gated `controlDict` fields**
(`startFrom`, `startTime`, `stopAt`, `writeControl`, `purgeWrite`, `writeFormat`,
`writePrecision`, `writeCompression`, `timeFormat`, `timePrecision`,
`runTimeModifiable`, `DebugSwitches`, and the `functions { yPlus1 … }` block) are
carried from A1WR's heredoc, md5-pinned at `9bff59b63509e76d5dfa373a42a47074`,
and covered as a block by the byte-identity assertion above.

**INHERITED DELIBERATELY AND DIVERGENT — the 8 files of state (iii)**, listed
above with their argument, pending sign-off.

---

### A4.4 AN FFD IS A NAME, NOT AN IDENTITY

**Enumerator: `find /home/ubuntu -name wingFFD.xyz -not -path '*/.git/*'`, then
`md5sum` on each. Measured 2026-09-03: 484 files, 9 distinct md5s, of which 284
carry `6ddf378b028d03d8a18270488bee1759`.** The A1WR geometry is only the
plurality; **200 files under that same filename are eight other geometries** —
the M6, CRM, RAE2822 and tutorial cases. **An FFD is the design-variable
parametrisation, so two files of the same name with different bytes are
different design spaces, and a finite-difference table computed against the wrong
one is a table at the wrong wing** — which reaches the bright line, where the FD
table is what converts a DAFoam gradient into a result. `DAFOAM_CHARTER.md` §6
already fixes that identity is a hash and never a version string; **this is that
rule arriving at geometry inputs rather than at images**, and it is recorded here
because the extension is not written anywhere else. This item pins its FFD by
md5 and asserts it on both sides of the copy for exactly this reason.

---

### A4.5 THE GUARD SUITE IS NOW A COMMITTED ARTEFACT, AND THE PINS MOVE WITH IT

**`a1wrt_drive_guards.sh` is promoted out of the session scratchpad and into this
item.** A harness that lives only in scratch is wiped and is not a handoff
channel (rule 13 / L-186); a guard suite a successor cannot re-drive is a claim
about one box at one moment. It extracts the launcher's shell blocks **from the
launcher's own bytes** between its section markers, and reads the constants it
drives them with **out of the launcher**, so it cannot drift away from the file
it tests — and it **REFUSES (rc 2)** rather than guessing if the launcher's shape
moves.

| instrument | md5 | role |
|---|---|---|
| `a1wrt_run_unit.sh` | **`f73191dea23877c99aaf802d21441009`** | the launcher, with `S5c`. Supersedes ADDENDUM 3's `0b00f8bf8d4425131c37bc585e249f4e` |
| `a1wrt_drive_guards.sh` | **`72b3caf7c4280afbe97396e3edc2b111`** | **new** — the standing guard suite, 221 lines |
| `a1wrt_controldict.py` | `a77c9bac486dce940707bdf9c00e1a6b` | **unchanged** |
| `a1wrt_read.py` | `705db5f7e972f6c033cbe303b7a6038f` | **unchanged — the grading path did not move, and nothing in this pass touches it** |
| `a1wrt_patch_assert.py` | `7f3a2c8e70684daba975ac9a2ee50385` | **unchanged** |

**DRIVEN, this session, zero containers: `23/23` legs as registered, 0
mismatched, 0 NOT RUN.** Six instrument-selftest legs — `a1wrt_patch_assert.py`
**11/11**, `a1wrt_read.py` **39/39**, `a1wrt_controldict.py` **13/13**, each
under `python3` **and** `python3 -O`; `S0b` **3** legs; `S5b` **7**; `S5c` **7**.

**AND THE HARNESS'S OWN CONTROLS WERE DRIVEN, because a harness that has never
failed is not known to be able to.** With an instrument removed it reports
**`21/21` legs and `1 NOT RUN`, named, folded into neither column**; with one of
`S5c`'s two md5 assertions deleted from a copy of the launcher it **refuses at
rc 2** naming the block and the expected-versus-found count.

**Still not enqueued, still not launched, zero compute.** Outstanding before
enqueue: **the supervisor's sign-off on the eight state-(iii) files**, and his
check 1 and check 4 against these new bytes.

---

## ADDENDUM 5 — 2026-09-03T21:08Z — THE EIGHT STATE-(iii) FILES RULED, THE mtime HAZARD REGISTERED AND DEMONSTRATED, AND THE QUEUE ROW DRAFTED BUT HELD

**Document version 1.4 → 1.5.**
**Lines whose number changed above this section: 0** — **COMPUTED:** in the
appending invocation the first **1,685** lines of this file, its entire length
before this append, were compared byte-for-byte against its blob at `HEAD` and
are identical; `git diff` shows **one hunk, zero deleted lines**.

**PRE-COMPUTE CONDITION, BY EXECUTION IN THE APPENDING INVOCATION:** the
registered run root `/home/ubuntu/certonomous-runs/A1WRT/` is **ABSENT**; the
appending shell was written to refuse the append had it existed.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** `endTime`
4000 · `primalMinResTol` 1e-8 · caps 361.0 / 2943.0 · ceiling 3304.0 · frame
allowance 300 s · `TMO` 21,360 / 176,280 s · np = 1 · patched row
`sha256:2927768a16ac…` · declared points 1 and 7 · `G-PATCH`, `G-REPRO`,
`G-OCC`, `G-COLDSTART`, `G-STALL`, `G-FIXTURE` **as frozen** · verdict labels as
frozen. **All unchanged.**

---

### A5.0 THE FINDING OF THIS PASS, AND IT BELONGS ABOVE THE TABLE

**A rule induced from the first two divergent files would have been WRONG on the
next two, and would have introduced a real defect while believing it was
removing one.** `L3`'s `controlDict` and `decomposeParDict` are both
mesh-generation furniture and both are correctly replaced from the body's own
copy. Generalising that to *"`L3` is stale, take `sweep_I`'s"* and applying it
mechanically to `surfaceMesh.xyz` and `volumeMesh.xyz` would have **imported a
description of a different mesh** — because for those two the direction inverts
and it is `sweep_I`'s copies that are stale. **The exception was found by
enumerating the set rather than generalising from its first members**, which is
why the order was to close the class and not to fix a file.

---

### A5.1 (iii-a) `surfaceMesh.xyz` and `volumeMesh.xyz` — RULED: INHERIT `L3`'s

**Ruled by the dafoam-supervisor, 2026-09-03, on his own re-derivation.** He
independently reproduced the 31-file partition (his grouping: 21 identical + 4
differing + 6 absent-in-body; the same partition as A4.2's 21 + 2 + 8 regrouped)
and confirmed the direction inversion against the skeleton:

| | `A1WR/L3` | `sweep_I/case` | the incompressible **skeleton** |
|---|---|---|---|
| `surfaceMesh.xyz` | `022ee2e7ba89056b62b683f053a77491` | `ed3e2abaa49ebb8d83eeb1d032aaf405` | **`ed3e2abaa49ebb8d83eeb1d032aaf405`** |
| `volumeMesh.xyz` | `35d9f01d8f6b676083431c6dce9c5f92` | `406627551850708ea6f64f7057334f4d` | **`406627551850708ea6f64f7057334f4d`** |

`sweep_I`'s copies are **byte-identical to the skeleton's** — stale, left behind
when `stage_unit()` overlaid `L3`'s `polyMesh` onto the skeleton — and **`L3`'s
`log.plot3dToFoam` references `volumeMesh`/`.xyz`**, so `L3`'s plot3d files are
the *input to the conversion that produced `L3`'s own `polyMesh`*. **INHERIT
from `L3`. Staging from `sweep_I` would have imported a description of a
different mesh.** Nothing reads either file in any case: `surfaceMesh`,
`volumeMesh` and `plot3d` are zero hits in the producer, zero in `a1wr_cmd.sh`
and zero in the frozen grader.

### A5.2 (iii-b) The six `log.*` files — RULED: KEEP. **And the ground is corrected here.**

**RULED KEEP.** The conclusion stands. **The ground given for it does not, and
the correction is recorded rather than the reasoning quietly repaired.**

The ruling rested on a grep for `mtime|st_mtime|getmtime|AGE|age_|-newer|TIMEDIR`
across the item's three files reportedly returning *"no age logic of any kind …
every hit is a comment, a path or `RC_USAGE`"*, and therefore *"there is no age
clause here to poison."* **THAT RESULT DOES NOT REPRODUCE.** It holds for
`a1wrt_run_unit.sh` and `a1wrt_controldict.py`. It is **false for
`a1wrt_read.py`**, which carries a **live age clause** — `G-FIXTURE`, at
**`a1wrt_read.py:291-294`**:

> `if p.stat().st_mtime >= run.stat().st_mtime:` → `raise Refusal("G-FIXTURE:
> mtime(%s) >= mtime(run root) -- a fixture not older than the run it grades is
> not independent of it")`

declared at `:25` and with its own known limitation disclosed at `:30-44`.
**There IS an age clause in this item.**

**THE CORRECT GROUND, AND IT IS NARROWER AND CHECKABLE.** The clause compares the
fixture against **the ITEM RUN ROOT `$BASE`**, not against any inherited file —
`a1wrt_read.py` is given `$BASE` because it reads `<run>/tail_empty/out/rc` at
`:965-966`. **`$BASE`'s mtime is set by the launcher's own writes at launch
time** (`mkdir`, then `runScript.py`, `cmd.sh`, the unit directory entry and the
staging-evidence file), whereas `cp -a` preserves mtimes only on **`$WORK` and
its contents**. **The six `log.*` files sit inside `$WORK`, where nothing
compares them to anything.** So the hazard does not reach them — for a reason
about *which directory the clause reads*, not because no clause exists.

### A5.3 THE LATENT PROPERTY, REGISTERED AS A STANDING WARNING TO A SUCCESSOR — AND DEMONSTRATED

**This is not a defect of this item. It is a trap laid for the next one, and it
is registered because it is the one that bites.**

`S2` is `cp -a "$MESH_SRC" "$WORK"`, so **`$WORK` and every file under it carry
`L3`'s PRESERVED mtimes** — `constant/polyMesh/points.gz` is stamped
**2026-09-01 17:18:35**, and a run executing days later inherits that stamp.
**Measured and driven both directions, zero compute:**

| the clause at `a1wrt_read.py:291`, evaluated | mtime | verdict |
|---|---|---|
| fixture `a1wrt_fixture.log` | 2026-09-03 17:18:42 | — |
| `run = $BASE`, built as the launcher builds it (`mkdir` + its own writes) | 2026-09-03 21:06:55 | **PASSES** |
| `run = $WORK`, built by the real `cp -a` from `L3` | **2026-09-01 17:18:37** | **REFUSES** |

**A successor that points the grader's `run` at a UNIT directory instead of the
item root — or that adds any age clause taking the staged tree's mtimes as its
datum — reproduces `F3S`'s unsatisfiable-by-construction clause exactly**: a
fixture newer than a run root that was stamped two days before the run existed.
**The staged tree's mtimes are the SOURCE's, not this item's. They date `L3`, not
the run.** Any age datum must come from something the launcher itself wrote —
which is what `S8` already does for the *fields* age guard, writing
`$WORK/.a1wrt_age_datum` from a `touch` of `0.orig/*` **last**, after every other
staging step.

---

### A5.4 THE QUEUE ROW IS DRAFTED AND **HELD**, AND WHY

The supervisor authorised the enqueue with eight conditions. **Seven are
discharged; one cannot be discharged before the move; and the row is HELD at its
draft path on a premise of the authorisation that was measured false after it was
given.**

**Draft path:** `cases/dafoam/ladder-a/A1/wall_resolved_alpha_tail/A1WRT_U1_alpha12_symmetry.json`
— beside the case, **not** in `verification/queue/dafoam/`, and nothing reads it
there.

**THE PREMISE THAT FAILED.** The authorisation stated *"the box is at ~95 % and
`D6RF2` is already held on capacity, so expect A1WRT to sit behind it — that is
queued, not blocked."* **Measured, with the runner's own reader
(`scripts/queue_runner.py` `measure_box`) and corroborated by
`verification/queue/runner.log` across every tick:** the box is at **69.9 %**
(~11.2 of 16 cores), MemAvailable **26.2 GB**. `D6RF2_chain` and
`F28G_L1_dp1000_U20` are held **only because they are 4-rank** — the admission
rule at `queue_runner.py:936` is `busy_cores + ranks > 0.9 × ncpu`, i.e.
11.2 + 4 = 15.2 > 14.4. **This row is `ranks = 1`: 11.2 + 1 = 12.2 ≤ 14.4, busy
69.9 < the 85 % ceiling, MemAvailable 26.2 ≥ the 8.0 floor. It passes every
limb.** And the runner does not queue FIFO — on a held entry it logs *"trying the
next entry"* and continues — **so this row does not sit behind those two, it
overtakes them.** With this queue's own README amendment of 2026-09-01 —
**"THE DROP IS THE LAUNCH … placing a validated entry in this directory starts
compute within about a minute, with no further human step"** — the drop is not a
proposal that waits. **It is a launch on the next ~60 s tick.**

**The item is cheap and that is not the point.** 32.33 core-min = **$0.0276
DERIVED, NOT MEASURED**; the whole item's ceiling of 3,304.0 core-min = **$2.82
DERIVED** — both far inside the under-$25 pre-authorised band. **What is held is
not the spend but the premise**: an authorisation given in the expectation of a
wait, where the measured effect is an immediate launch. `CLAUDE.md` rule 9 — an
instruction is answered, not merely obeyed.

**CONDITIONS, AS DISCHARGED:**

| # | condition | state |
|---|---|---|
| 1 | drafted beside the case, to be **moved** never copied | **DONE** — drafted; the move is what is held |
| 2 | pins match disk **and** HEAD, verified in the invocation; superseded pin marked SUPERSEDED **in the row** | **DONE** — all seven verified; `288bc690`, `718b5d47` and `0b00f8bf` all named SUPERSEDED against the live `f73191de` |
| 3 | `prereg_commit` and `prereg_md5_at_freeze` reproduced independently | **DONE** — `a62d8d7524b233c747a9d83b9098c3d10042dd49` found by `git rev-list --grep`, verified to exist, to be an **ancestor of HEAD**, and to hold the path; md5 `e58643efd7ab15cfa571daf31749704e` taken by `git show … \| md5sum` in the same shell |
| 4 | `launch_cmd` names a driver that **exists** | **DONE** — `a1wrt_run_unit.sh` present and executable; and the image it names, `dafoam-idwarp-rot:v1`, resolves to digest `sha256:2927768a16ac…`, **the digest `S7` requires** |
| 5 | cap and estimate transcribed, `cost_basis` honest | **DONE** — cap **361.0**, estimate **32.33** (§4.3's U1 line), `REPORTED-BY-OWNER, NOT MEASURED` |
| 6 | `--require-binding` must ACCEPT and bind to `dafoam/` | **NOT RUN — and it CANNOT be run before the move.** The validator refuses by design outside the team directory; on the draft it reports **`TEAM-BINDING: NOT CHECKED`**, which the supervisor's own condition calls an unchecked condition and not a passing one. Driven both ways: **ACCEPTED** without the flag, **REFUSED (rc 2)** with it, so the check is live and not decorative |
| 7 | run root **ABSENT BY EXECUTION** at enqueue | **DONE** — `test -e` non-zero at 2026-09-03T21:04:20Z, to be re-asserted in the moving invocation |
| 8 | queue depth in estimated core-minutes after the drop | **DONE** — `verification/queue/dafoam/` now: **215.77 core-min** (1 row, `D6RF2_chain`). With this row: **248.10 core-min** (2 rows) = **$0.21 DERIVED**. If U2 follows: **503.49 core-min** = **$0.43 DERIVED** |

**Validator, on the draft:** `ACCEPTED … team=dafoam case=A1WRT_U1_alpha12_symmetry
ranks=1 est=32.33 core-min`, all five mechanical checks — SCHEMA, COMMIT-EXISTS,
PREREG-AT-COMMIT, AGE-GUARD, RANKS — with TEAM-BINDING reported NOT CHECKED as
above. Its own controls: **36 controls fired, each shown able to fail**, rc 0.

**ONE ROW, ONE RUN — AND U2 IS DELIBERATELY NOT DRAFTED.** §3 registers that U1
does **not** gate U2 (*"the cold α = 12 fails outright → `NOT A RESULT` on
`G-REPRO`; the tail is still run and reported"*), so there is no dependency
argument for enqueueing both blind. And **both units default to the same core**:
`a1wrt_run_unit.sh` sets `CPUSET="${A1WRT_CPUSET:-10}"`, so two rows enqueued
together would both take cpuset 10, and the launcher's `G-OCC` **records and
queues, it never refuses** — it would not stop the collision. **Referred to the
supervisor, not resolved by a lane.**

**Nothing has been launched. Zero compute. The run root is absent.**

---

## ADDENDUM 6 — 2026-09-03T21:14Z — U1 IS ENQUEUED ON A CORRECTED PREMISE, AND U1/U2 ARE SERIALISED ONTO ONE CORE RATHER THAN SPLIT ACROSS TWO

**Document version 1.5 → 1.6.**
**Lines whose number changed above this section: 0** — **COMPUTED:** in the
appending invocation the first **1,866** lines of this file, its entire length
before this append, were compared byte-for-byte against its blob at `HEAD` and
are identical; `git diff` shows **one hunk, zero deleted lines**.

**PRE-COMPUTE CONDITION, BY EXECUTION IN THE APPENDING INVOCATION:** the
registered run root `/home/ubuntu/certonomous-runs/A1WRT/` is **ABSENT**. **This
is the LAST addendum for which that will be true**, and it is landed **before**
the drop for exactly that reason: the queue's own README records that **the drop
is the launch**, so everything this document has to say is said while the item is
still at zero compute.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** `endTime`
4000 · `primalMinResTol` 1e-8 · caps 361.0 / 2943.0 · ceiling 3304.0 · frame
allowance 300 s · `TMO` 21,360 / 176,280 s · np = 1 · patched row
`sha256:2927768a16ac…` · declared points 1 and 7 · `G-PATCH`, `G-REPRO`, `G-OCC`,
`G-COLDSTART`, `G-STALL`, `G-FIXTURE` **as frozen** · verdict labels as frozen.
**All unchanged. What this addendum records is a scheduling ruling and an
enqueue, and neither touches a registered number.**

---

### A6.1 The premise was wrong twice over, and the record says how

ADDENDUM 5 held the queue row because the authorisation's capacity premise was
measured false. **The supervisor re-derived both errors himself and
re-authorised on the true premise.** They are recorded because they are
instrument failures, not arithmetic slips:

1. **A stale value carried across scopes.** The 94.9 % figure was read from the
   runner's log at **20:30Z** and carried to **21:0xZ** without re-reading.
2. **The wrong instrument entirely.** `uptime`'s **load average** was read as an
   occupancy measure. **Load average is a run-queue length, not a utilisation
   percentage** — it counts runnable *and* uninterruptible-sleep tasks, so an
   I/O-heavy box reads "saturated" while its cores are not. **Measured on this
   box at 21:12:28Z: load average 24.34 against 70.6 % busy.**
   `scripts/queue_runner.py` `measure_box` is the instrument; `uptime` is not.

**The true reading, at the drop:** busy **70.6 %** (~11.3 of 16 cores),
MemAvailable **26.1 GB**, headroom **3.1 cores** to the `0.9 × ncpu` line.
`D6RF2_chain` and `F28G_L1_dp1000_U20` are held **only because they are 4-rank**
(`queue_runner.py:936`, `busy_cores + ranks > 0.9 × ncpu`), and the runner is
**first-fit over the whole queue, not FIFO** — its own comment: *"a held wide
entry must not block a narrow one behind it."* **So this 1-rank row overtakes
them, and the drop is a launch on the next tick.**

**THE COST, ACCEPTED AND NAMED RATHER THAN WAVED PAST** (the supervisor's, in his
words): this row raises `busy_cores` to ~12.3, so **`D6RF2` will need `W3` to
release ~1.9 cores instead of ~0.9** before it admits. It is taken because
`D6RF2` is held by `W3`'s occupancy and **not by this row**, and holding a
fully-checked 1-rank item idle for hours to marginally speed an item blocked by
something else is the wrong trade under the standing directive that idle capacity
is a defect.

### A6.2 U1 ENQUEUED — `A1WRT_U1_alpha12_symmetry`

The **reproduction control**: `symmetry`, COLD, one point at α = 12, against
A1WR's own CONTINUED α = 12 (`CL` 1.19079592024, `CD` 0.030665481166) — `G-REPRO`
on A1WR's own configuration, unchanged. **Estimate 32.33 core-min against the
registered cap 361.0**; **$0.0276 DERIVED, NOT MEASURED**, and the whole item's
ceiling of 3,304.0 core-min is **$2.82 DERIVED** — both inside the under-$25
pre-authorised band. Row at
`verification/queue/dafoam/A1WRT_U1_alpha12_symmetry.json`, **moved and not
copied** from beside the case.

### A6.3 U1 AND U2 ARE SERIALISED ONTO ONE CORE — and the obvious repair is REFUSED

**Ruled by the dafoam-supervisor, 2026-09-03, and it is the more consequential of
the two rulings.**

Both units default to `CPUSET="${A1WRT_CPUSET:-10}"`, so two rows enqueued
together would collide on core 10 — and the launcher's `G-OCC` **records and
queues but never refuses**, so it would not stop the collision. **The apparent
repair is to give U2 a second core. THAT IS REFUSED.**

> **U1 and U2 exist TO BE COMPARED — that comparison IS the item, and its whole
> claim is to be one-variable. Running the two arms on different cores makes CPU
> PLACEMENT a variable that differs between them, and this family already carries
> `G12_cpu_placement_F-P` `GATE FAIL` on record: placement is demonstrably not
> free in these measurements. Solving a scheduling collision by splitting the
> arms would buy throughput by spending the very thing the item exists to
> measure.**

**The shared `CPUSET` default is therefore not a defect to route around — it is
the one-variable design expressing itself**, and the collision is the reason to
**serialise**, not the reason to split. **U2's row is drafted and HELD at
`cases/dafoam/ladder-a/A1/wall_resolved_alpha_tail/A1WRT_U2_tail_empty.json`
until U1 has landed and been read**, then moved. Both arms run on core 10,
sequentially, on identical placement.

**AND THE HOLD ON U2 IS A SCHEDULING RULING, NOT A DEPENDENCY. It must never be
reported as one.** §3 registers that U1 does **not** gate U2: if the cold α = 12
fails outright the verdict is `NOT A RESULT` on `G-REPRO` and **the tail is still
run and reported**, with the control's absence named.

**Serialising is also what CLOSES the `G-OCC` gap** rather than relying on a
guard that reports and does not refuse. That `G-OCC` cannot catch a same-item
cpuset collision is recorded here as a known limitation of that guard, not as a
defect of this run.

### A6.4 The `S8` pattern is the shape a successor copies

ADDENDUM 5 §A5.3 registered the `cp -a` mtime hazard and named the remedy; it is
repeated here because it is the operative half. **Any age datum must come from
something the launcher itself wrote, never from the staged tree.** `S8` is the
shape to copy: it `touch`es `$WORK/0.orig/*` **last, after every other staging
step**, and writes `$WORK/.a1wrt_age_datum` from that `touch` — so the datum
dates *the run that was allowed to produce the answer*, which is precisely what
`CLAUDE.md` rule 4's age guard requires. **The staged tree's mtimes date `L3`.**

### A6.5 What happens next, and what this lane may not do

**The verdict is the frozen grader's and the reading is the supervisor's.** This
lane does not grade, and does not diagnose an abort into a repair: **an abort is
a finding about the case until triage says otherwise, and triage is the
supervisor's** (`SUPERVISION_CHARTER.md` §3, the check that may never be
delegated). The grading path is `a1wrt_read.py`,
`705db5f7e972f6c033cbe303b7a6038f`, **unchanged since the freeze and unmoved by
any of the six addenda**.

**A completion report is incomplete without the estimate-versus-actual
comparison** (`CLAUDE.md` rule 12): actual/predicted against **32.33** for U1 and
**255.39** for U2, in core-minutes from the logs, dollars **derived, not
measured**, waste named separately and never absorbed into the ratio, landing as
a row in `docs/COST_CALIBRATION.md`.
