# A1WRT — WALL-RESOLVED α-TAIL, INCOMPRESSIBLE ONLY — PRE-REGISTRATION **DRAFT**

> ## ⚠ THIS IS A DRAFT. IT IS NOT FROZEN.
>
> **NOT FROZEN. NOT ENQUEUED. NOT LAUNCHED. ZERO COMPUTE SPENT.**
> No md5 manifest is pinned by this file, no queue entry exists, and no solver,
> container or queue release was performed by the lane that wrote it. The
> supervisor's §3 check 4 — cap arithmetic and the reproduction-control
> threshold read personally — is owed **before** this becomes a freeze, and is
> not delegable. Until then nothing here binds anything.
>
> **The successor is a NEW ITEM on a FRESH RUN ROOT with its OWN budget** —
> a fresh pre-registration under `VERIFICATION_CHARTER` §2b limb 1.
> **It is NOT a restart of A1WR Stage 2**, which is closed
> (`A1WR_STAGE12_RESULTS.md`, `NOT A RESULT`), whose freeze contains no restart
> rule, whose in-memory continuation state died with the process, and whose
> registered per-arm budget is 79.37 % spent with 165.03 core-min remaining
> against a 186.02 core-min need.

**Item:** `A1WRT` — NACA0012 α-tail 12…18° on the A1WR wall-resolved L3 mesh,
**incompressible only** (`DASimpleFoam`).
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

## 2. THE DESIGN — COLD α = 12 FIRST, THEN THE CONTINUATION

**One process, one container, np = 1, one core:**

1. `0/` reset from `0.orig` **once**, on a fresh case tree, before anything runs.
2. **α = 12, COLD** — the reproduction control (§3).
3. **α = 13, 14, 15, 16, 17, 18 — CONTINUED, ascending**, each inheriting its
   predecessor's converged state **in memory**. This reproduces A1WR §5
   Stage 2's mechanics exactly rather than approximating them.

**Seven points total.** No point is retried, relaxed, re-tuned or dropped; a
point that fails is recorded with its residual history and the sweep continues,
with every subsequent point flagged `after_exception=TRUE`. **A missing point on
a polar is a lie by omission.**

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

| term | arithmetic | core-min |
|---|---|---|
| 7 points × 4,000 iterations × **0.4615 s/it** (MEASURED) | 12,922 s | **215.37** |
| container start + import | 93.85 s, MEASURED on `a1wr_sweep_I` (container wall 28,146.98 s − last `ExecutionTime` 28,053.13 s) | **1.56** |
| tail-stiffening allowance on α 14–18, **EXTRAPOLATED** | 5 × 4,000 × 0.4615 × 0.25 = 2,307.5 s | **38.46** |
| **ESTIMATE** | | **≈ 256 core-min** |

= 4.267 core-h ≈ **$0.2189 DERIVED, NOT MEASURED** at the owner-stated
$0.0513/core-h; `cost_basis` **REPORTED-BY-OWNER** — the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**The term most likely to carry the error is the tail-stiffening allowance**, and
it is named in advance, exactly as A1WR §7.5 named its own iteration-scaling
assumption.

### 4.4 The cap, and the deadline arithmetic **EXECUTED AND EVALUATED AT DRAFT TIME**

Sanaa, 2026-09-03, verbatim: *"still carries a hard per-run cap (set by the team
at ~3× its own estimate, not by me) … The estimate is an instrument, not a
permission slip."*

> **REGISTERED CAP: 768 core-min** = 3.00 × the 256 estimate.
> = 12.80 core-h ≈ **$0.6566 DERIVED** — under the $25 pre-authorisation and far
> under the $150 escalation trigger.

**D19T was frozen, md5-pinned, gate-checked and launched TWICE with a deadline
of exactly 0 s because nobody ever executed the arithmetic at freeze. It is
executed here, in this document, and its result is evaluated:**

```
ranks         = 1                       (np = 1, registered)
CAP_MARGIN_S  = 300                     (3.2x the MEASURED 93.85 s container start)
TMO           = int(768 * 60 / 1) - 300
              = 46080 - 300
              = 45780 s
```

**EVALUATED:** `TMO = 45780`. **`45780 > 0` ✓.** `45780 / 60 = 763.0 core-min
≤ 768 cap` ✓. **A freeze that cannot print a positive evaluated integer here
does not launch.**

### 4.5 The deadline against a BUSY box — the 331.7 core-min lesson, applied

A1WR lost **all six** cold controls and 331.6667 core-min for **zero physics** to
a 3,300 s deadline sized from a quiet-box rate and spent on a box the same item
had just filled 14-deep. Registered here rather than repeated:

| box state | s/iteration (MEASURED) | 7 points × 4,000 it | vs the 45,780 s deadline |
|---|---|---|---|
| quiet | 0.4615 | 12,922 s + 94 s = **13,016 s** | **28.4 % — finishes comfortably** |
| moderate contention, 2× | 0.923 | 25,938 s | 56.7 % — finishes |
| **break-even** | **1.635** | 45,780 s | **100 % — the ceiling** |
| A1WR's measured 14-way saturation | 1.781 | 49,868 s | **109 % — CAP-STOPPED at ~6.4 of 7 points** |

**The item survives any contention up to 3.90× the solo rate.** Beyond that it
cap-stops, and **that outcome is registered in advance: a cap-stop is
`NOT A RESULT` on the unfinished points; points already in the ledger stand.**
No new budget is granted on an overrun.

**AND THE MECHANISM IS MEASURED, NOT GUESSED:** A1WR's cpusets were all disjoint
(A1WR 8–15, MAAOA 2–7, verified by `docker inspect`) and per-core throughput
still degraded 2.75–4.77×. **A one-core cpuset isolates a core, not memory
bandwidth.** The driver therefore **records box occupancy and MemAvailable at
launch and at every point boundary into the ledger row**, so contention is
attributed from measurement at calibration time instead of argued.

**This item is ONE np = 1 process on ONE core.** It consumes 1 of 16 cores, so it
is a legal filler under the never-idle rule without itself creating the
saturation that killed A1WR's controls.

### 4.6 Calibration at completion

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
| `G-REPRO` | §3, both limbs R1 and R2, bands registered above | inside → `CORROBORATED`; R2 outside → tail labels withdrawn, `NOT A RESULT`; control absent → `NOT A RESULT` on the control |
| `G-COMPLETE` | rule 4, **all** clauses: rc 0, `End` line, last time == `endTime`, fields present, `ExecutionTime` count == `endTime`, every field newer than the case's own datum | refuse (exit 2) rather than degrade. **⚠ REGISTERED WITH ITS IMPLEMENTATION OWED AND ITS ABSENCE MADE A FREEZE BLOCKER** — `G-COMPLETE` is registered in A1WR §9 and has **zero occurrences** in `a1wr_read.py`, so A1WR's completeness gate is unadjudicated to this day. **This item's reader does not freeze until `grep -c 'G-COMPLETE'` on it is non-zero and its planted control is driven.** |
| `G-CAPS` | **arithmetic, not prose**: measured core-min per unit against the 768 cap, computed by the reader and printed | cap-stop ⇒ `NOT A RESULT` on the affected points. **Also registered with implementation owed** — A1WR's reader mentions `G-CAPS` in one conditional sentence and computes nothing. |
| `G-YPLUS` | measured y+ min/mean/max on the wall patch, every α | `GATE FAIL` if y+max ≥ 1.0 anywhere; refuse (exit 2) on a blind channel for a point that ran ≥ 200 iterations. **The mesh is NOT re-cut** (A1WR §3.4) — an overshoot is a registered outcome |
| `G-WALLTREAT` | `useWallFunction: False` in the staged script **and** `BCType=nutLowReWallFunction` in the solver log for the `wing` patch | refuse (exit 2) if the log does not confirm the BC that actually ran |
| `G-FIXTURE` | **every planted control's fixture is STATIC and independent of the run being graded** | refuse (exit 2) if any fixture is read from this item's own run root. **THE L-435 REPAIR** — see §6 |
| `G-STALL` | no output binds a stall word to a numeric angle | refuse (exit 2) on a planted claim; must NOT fire on the honest caveat |
| `G-NOBAND` | no output presents a value as grid-converged or inside a band | refuse (exit 2) — the L3 family still has no Roache triple |
| `G-IMG` / `G-FREEZE` | image id and `libidwarp` md5 exact; every instrument md5 checked at launch | refuse (exit 4) on any mismatch |

**Composition:** D19M's repaired `compose_item` from `verdict_before_ceiling`,
hard-gate list tested for **both** `GATE FAIL` and `NOT A RESULT`. Ceiling
`GATE REACHED`.

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
- **Registered in advance, because A1WR's α 0…12 makes it likely:** the tail may
  well produce **seven more `NOT CONVERGED` points** — every A1WR arm-I point
  ran the full 4,000 iterations without satisfying 1e-8. **That is a registered
  outcome, not a defect, and it does not license raising `endTime`, relaxing the
  tolerance, or re-tuning anything.** Any of those would be result-shopping and
  is forbidden on this item; a different iteration budget is a NEW rung with its
  own pre-registration.
- **No adjoint claim.** Primal only, undeformed geometry, no optimiser, no trim.
- **The build confound stands and is restated:** the coarse sweeps ran the
  SHIPPED image, this and A1WR run the PATCHED `dafoam-idwarp-rot:v1`.

---

## 8. OWED BEFORE FREEZE

1. **Supervisor's §3 check 4, personally**: the §4.3/§4.4 cap arithmetic and the
   §3.3 reproduction-control bands, read as arithmetic and not as a summary.
2. The driver, run-script staging and **reader** written, with `G-COMPLETE` and
   `G-CAPS` actually implemented (§5) and `G-FIXTURE` enforced (§6), every
   control driven and its selftest passing, then md5-pinned by the freeze.
3. Run root `/home/ubuntu/certonomous-runs/A1WRT/` re-checked absent **in the
   freezing shell**.
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
