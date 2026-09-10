# M6CP1 — ONERA M6 transonic wing, surface Cp against AGARD AR-138, on the own-mesh fine triple {L2, L1, L0}

> ## 🟠 THIS FILE IS A **DRAFT**. IT IS **NOT FROZEN**, **NOT AUTHORISED**, AND NO GRADED SOLVE HAS RUN UNDER IT.
> Drafted by a cfd `lab-lane` on the cfd-supervisor's CASE PROTOCOL brief, 2026-09-10.
> **§12 FREEZE BLOCK IS LEFT BLANK FOR THE cfd-supervisor.** Check 4 —
> *"pre-registration COMMITTED before compute"* — is the supervisor's, is personal, and is
> **not delegated to this lane**. This lane commits nothing.
> **SUBMISSIONS PARKED (rule 7).** No message from any agent is Sanaa's consent (rule 9).

---

## 0. WHAT THIS CASE IS FOR, IN ONE SENTENCE THAT IS UNCOMFORTABLE TO WRITE

**The ONERA M6 estate on this box holds six mesh families and zero flow solutions.** Every `End`
line under `M6SR_runs`, `M6I_runs`, `M6_LE_RESOLVED_runs`, `M6_OWN_FAMILY_runs`,
`F13_ONERA_M6_runs`, `RUNG1_M6_R2_runs` and `M6S_runs` belongs to a **mesher**. Every solved time
directory in the whole estate is a `smoke_*`. A swept transonic wing with a lambda shock is the
most recognisable image in CFD, and this lab has 4.59 million cells of it and **not one graded
iteration**. M6CP1 exists to produce the first one.

This is also **the first instance of THE CASE PROTOCOL**. The stage 1–4 machinery it runs on
(`scripts/case_protocol_lib.py` and `scripts/case_protocol_stage{1,2,3,4}_*.py`) is written to be
inherited by later cases, so its shape is part of this registration and not an implementation
detail.

## 1. BUDGET — RUNS UNDER THE 2026-09-10 EXEMPTION, AND IS STILL COSTED

**Sanaa, 2026-09-10, verbatim: *"for all these 3D cases that still need to run, i dont want to see
any budget gates ( time or money)"*.** M6 is squarely in that scope.

**Operationally: no wall-time cap and no core-minute cap STOPS this run.** §4's cap-stop and
standing rule 12's overrun-stop are **suspended for M6CP1**.

**What is NOT suspended.** The run is costed here, before compute, and its actual lands in
`docs/COST_CALIBRATION.md` under rule 12's estimate-versus-actual comparison. The estimate is
**calibration data, not a gate**. `budget_gate` in the freeze manifest reads
`NONE — Sanaa 2026-09-10`.

**And a caution that belongs in the registration rather than in a lane's head:** the runner's
`RUNNER_CAP_ENFORCEMENT_CLAUSE` (D539) is **advisory and OFF**, so nothing at the runner changes
under this exemption. **A silent runner is therefore not evidence that a cap was respected** — a
cap that was never enforced and a cap that was never exceeded look identical in the log, and only
one of them is a measurement.

## 2. THE FAMILY — THREE LEVELS, r = 2.0000000, ADMITTED NOT ASSUMED

| level | cells | cell-count source | r vs next coarser | y1 mean (m) | y+ mean (est.) |
|---|---:|---|---:|---:|---:|
| L0 | 4,592,640 | `checkMesh` stdout `cells:` | 2.0000000 | 5.1511e-05 | 15.6 |
| L1 |   574,080 | `checkMesh` stdout `cells:` | 2.0000000 | 1.0726e-04 | 32.4 |
| L2 |    71,760 | `checkMesh` stdout `cells:` | — | 2.4271e-04 | 73.4 |

**The cell counts come from a source that counts CELLS** (VERIFICATION_CHARTER §2bd.1). They are
cross-checked against the owner/neighbour topology and the two agree exactly; a disagreement would
have refused the level rather than picked a winner. **`len(owner)` is `nFaces` and is used
nowhere.**

**L3 (8,970 cells) is NOT in the family and must not be added.** Its own `checkMesh` reports **2
negative-volume cells**, max skewness 4.23, 7 non-orthogonality errors and 18 incorrectly oriented
face pyramids. Verification has separately ruled that no admissible coarse level exists off the
390-face M6 surface, so the triple is built by refining **up** to L0 rather than down.

### 2.1 🔴 A REGISTERED CAVEAT ON THE OBSERVED ORDER, AND IT IS NOT A SMALL ONE

The wall treatment is `nutUSpaldingWallFunction` — **Spalding's law, a single continuous fit across
sublayer, buffer and log regions.** All three levels are therefore **admissible**: y+ 15.6 does not
put L0 outside its wall model, and reporting it as out-of-validity would be a false red.

**But the three levels sit in different parts of that fit** — L2 in the log region, L1 at its inner
edge, L0 in the buffer/blend region. Spalding is continuous; it is not uniformly accurate. So the
level-to-level change contains a **model variation as well as a discretisation error, and Richardson
extrapolation attributes all of it to discretisation.** Any observed order from this triple carries
that contamination.

**This does not make the triple inadmissible under rule 5. It makes the observed order's
interpretation a registered caveat**, in the same family as the M6SR `L-HONEST` label. Any figure,
table or certificate quoting an observed order from M6CP1 **carries this paragraph with it.**

## 3. GEOMETRY — ADMITTED ON FIVE LIMBS, WITH ONE REGISTERED DEPARTURE

Axes are **registered, never inferred**: x chordwise, y thickness, z spanwise, symmetry plane at
z = 0 (the symmetry patch is planar at z = 0, verified).

| limb | measured | registered | tol | verdict |
|---|---:|---:|---:|---|
| LE sweep | 29.99998° | 30.0° | 0.10° | PASS |
| TE sweep | 15.76369° | 15.8° | 0.10° | PASS |
| root chord | 0.806216 m | 0.8059 m | 1 % | PASS |
| root t/c | 0.097542 | 0.0977 | 2 % | PASS |
| span extent | 1.216405 m | 1.19676 m | 3 % | PASS |

**The sweep limbs are measured from the longest convex-hull edge on each side, and are
bit-identical across all three levels.** That matters more than the value: the first draft of this
gate measured sweep by spanwise banding and returned **30.00° / 29.92° / 26.35°** on L1 / L0 / L2,
and so **refused the coarse level of a grid family for a reason that was about the estimator.** A
geometry gate whose verdict moves with mesh density cannot judge a grid family at all.

**REGISTERED DEPARTURE — THE TIP.** The wall patch extends to z = 1.216405 m against a registered
semispan of 1.19676 m: a **faired tip cap overhanging by 0.019645 m (1.64 %)**. **The real ONERA M6
has a blunt, flat tip; this mesh closes the tip to a faired point.** The cap sits outboard of every
grading station — the outermost, y/b = 0.99, is at z = 1.18479 m, 0.0120 m inboard of the semispan
— but it is the geometry the outboard stations see, and no figure from M6CP1 may describe the tip
as the M6's own.

**Blockage: 1.553e-05**, domain 81.5 semispans streamwise. Stated as a number because a farfield
that is merely "far" is a claim.

## 4. CLOSURE AND NUMERICS — FROM THE CLASS DEFAULT, WITH ONE MEASURED COUNTER-EXAMPLE

Case class: `external_transonic_wing_steady_RANS_3D`. Closure `kOmegaSST`, adiabatic wall
(`zeroGradient` T), Spalding all-y+ wall treatment.

### 4.1 🔴 `rhoSimpleFoam` IS REGISTERED AS A CLASS-DEFAULT COUNTER-EXAMPLE — "class default, first use"

The class default for a steady external transonic wing is a **segregated steady** solver. On this
mesh **it does not run**: `rhoSimpleFoam` takes **SIGFPE (rc = 136 = 128+8) in the first thermo
update**, inside `Foam::hePsiThermo<...>::calculate` called from `::correct()`, with one `Time =`
line, **zero `ExecutionTime` lines** and no `End`. Every `rhoSimpleFoam` variant across 24
diagnostic solves repeats rc = 136; every `rhoPimpleFoam` LTS variant exits rc = 0 at t = 500.

**M6CP1 therefore registers `rhoPimpleFoam` + `localEuler` (LTS) as the solver, and records the
counter-example rather than quietly substituting.** A missing or contradicted knowledge-base entry
is registered as **"class default, first use"** and never waits.

### 4.2 🔴 THE SIGFPE IS A **SETUP** DEFECT, NOT AN OpenFOAM DEFECT — AND THE RUNG THAT WOULD HAVE SHOWN IT WAS NEVER PULLED

The attribution matters because Sanaa's standing directive is that OpenFOAM issues reach her **with
the run**, rather than being worked around. Three measured facts, and each is a setup fact:

1. **`transonic` is not set, at M∞ = 0.8395.** The case files record this as an explicit choice:
   *"CHOICE CH10: `transonic` is NOT set. Section 8.3 registers it nowhere, so OpenFOAM's default
   (no) runs."* With `transonic no` the pressure equation runs in its incompressible form, and at
   M = 0.84 that is the classical route to a first-iteration pressure/energy excursion that leaves
   `he` outside the Sutherland domain — which is exactly where the SIGFPE lands.
2. **The diagnostic registered to TEST that switch never ran.**
   `M6_OWN_FAMILY_runs/L2/smoke_diag_transonic` exits **rc = 1** at `Time = 1` on
   `--> FOAM FATAL IO ERROR: Entry 'div(phid,p)' not found in dictionary
   "system/fvSchemes/divSchemes"` — because `divSchemes` carries `default none;`, which makes an
   unruled term a hard abort. **The transonic pressure equation was never assembled once.** In that
   same log the energy equation solved cleanly (initial residual 0.99996 → 5.03e-05) and the
   temperature clamp reported `UnlimitedTmin = UnlimitedTmax = 288.15` with **zero limited cells**:
   there was no temperature excursion at all. **A numerics rung stands recorded as climbed that was
   never once climbed.**
3. **`pressureControl` (`pMinFactor` / `pMaxFactor`) is available and was never used on the failing
   path.** The symbols `Foam::pressureControl::pressureControl` and `::limit` are present in the
   `rhoSimpleFoam` binary of this build (openfoam2606). The **working** `rhoPimpleFoam` case sets
   `pMaxFactor 1.5; pMinFactor 0.9;`; **no `rhoSimpleFoam` case sets either.**

**What this does and does not establish.** It establishes that the setup differs from a working
setup in three specific, supported, registered-nowhere ways, and that the one test that would have
isolated the first of them died in dictionary lookup. **It does NOT establish that repairing them
makes `rhoSimpleFoam` run** — that is a stage-3 ladder rung, not a claim. **On the evidence in hand
this is a setup defect and nothing is referred upstream to OpenFOAM.**

**REPAIR APPLIED, AND IT DOES NOT TURN THE LEVER ON.** `div(phid,p) Gauss upwind;` is written into
`divSchemes` in every M6CP1 case, so `transonic yes` becomes **pullable** as stage-3 ladder rung 2.
The baseline still runs `transonic` unset.

### 4.3 SOLVER TOLERANCE — THE T23G2Rn2 RULE

| | value |
|---|---|
| tightest gate | GATE P, ±0.02 in Cp |
| loosest solver tolerance | `p` = 1e-08 |
| clear air | **6.30 decades** |
| verdict | **PASS** |

Computed by this lane and re-checked by the supervisor. It is a claim, not a checkbox: the failure
it prevents is a gate that measures the linear solver's stopping criterion instead of the physics.

### 4.4 LTS IS A NON-PHYSICAL TRANSIENT AND OWES A DEMONSTRATION

`localEuler` reaches steady state through a pseudo-time field that is not physical time.
Convergence of that march does not by itself show the graded state is independent of it.

**Registered demonstration, before the run:** the graded level is run at `maxCo 0.2` and again at
`maxCo 0.1`. **Gate P's Cp at all seven stations must agree between the two to within 0.004 — five
times tighter than Gate P's own ±0.02 band.** If it fails, the LTS path is not time-step
independent and the result is **NOT A RESULT**, not a PASS with a caveat. The second run is costed
below, not waived.

## 5. GATES

**GATE P** — surface Cp against AGARD AR-138 at seven span stations (y/b = 0.20, 0.44, 0.65, 0.80,
0.90, 0.96, 0.99), x/c ≤ 0.90, M∞ = 0.8395, α = 3.06°, Re(MAC) = 11.72e6.
**Band ±0.02 in Cp. Inside → `PASS`; outside → `GATE FAIL`.**

**GATE G** — the rule-5 Roache triple on {L2, L1, L0}. Gating order is rule 5's, unaltered:
(1) any level not iteratively converged **or not plateaued** → `NOT A RESULT`; (2) triple
`DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → `NOT A RESULT` with the value and both triples
and orders printed beside it; (3) `CONVERGING` → `PASS` inside the band else `GATE FAIL`, GCI at
Fs = 1.25 printed. **The gate can only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the
reverse. No GCI is quoted when the three values are not monotone.**

**Gate P sits behind Gate G.** A `PASS` on a family that is not `CONVERGING` is `NOT A RESULT`.

### 5.1 THE PLATEAU LIMB — WINDOW, STATISTIC AND TOLERANCE, DECLARED BEFORE THE RUN

Per VERIFICATION_CHARTER §2bd:

- **window:** the trailing 20 % of writes — the last 10 of 50.
- **statistic:** maximum absolute deviation from the window mean, relative to the window mean.
- **tolerance:** 5.0e-04.

**A two-point difference between the last two writes is not a plateau test and is not used**, because
a monotone drift is precisely the failure the window exists to catch and no endpoint statistic can
see it.

**This forced a change to the run control and it is worth naming.** The template wrote **once**, at
`endTime`. One write cannot carry a plateau statistic at all, and two would permit only the test the
charter forbids. M6CP1 registers `writeInterval 100` over `endTime 5000` → **50 writes**.

## 6. CAPACITY — MEASURED, AND THE FAMILY FITS WITH ROOM TO SPARE

**`solver_bytes_per_cell` is MEASURED**, by `/usr/bin/time -v` on a one-iteration `rhoPimpleFoam`
run at each level, peak RSS read from the process:

| level | cells | peak RSS (serial) | B/cell |
|---|---:|---:|---:|
| L2 |    71,760 | 0.184 GiB | 2757.6 |
| L1 |   574,080 | 0.890 GiB | 1664.9 |
| L0 | 4,592,640 | **6.110 GiB** | 1428.4 |

**The rate FALLS with size**, so the preflight guard uses the **largest** measured rate — 2757.6
B/cell, from the *smallest* mesh — and is therefore deliberately conservative rather than optimistic.
**Cross-check:** extrapolating the L2→L1 marginal rate of 1508.8 B/cell predicted L0 at 6.537 GiB
against **6.110 GiB measured**, ratio 0.935 — the extrapolation was conservative by 6.5 %.

Guarded requirement at L0, four ranks: **2757.6 B/cell × 4,592,640 × 1.35 = 15.92 GiB** against
**MemAvailable 27.43 GiB** and a **drained ceiling of 28.25 GiB**. **PASS, with 11.5 GiB of
headroom.** The **1.35 parallel uplift is an ASSUMPTION, not a measurement** — halo cells plus MPI
buffers — and stage 4's first checkpoint measures the real figure.

### 6.1 🔴 THE 28.25 GiB FIGURE ON THE cfd BOARD DOES NOT APPLY TO THIS CASE

The board records a fine level needing **28.25 GiB against a drained ceiling of 29.07**. **That is a
different case:** it is the `M6_LE_RESOLVED` grid-b `Lf` **meshing** requirement at **34,281,600
cells**, a mesh that does not exist yet. M6CP1's finest level is **4,592,640 cells and already
built**, and a **meshing** bytes-per-cell is not a **solver** bytes-per-cell in any case. Carrying
that number into this registration would have been the wrong number applied confidently.

**Corroborating evidence that is not an extrapolation:** stage 2's one-iteration dry run completed
at **all three levels**, rc = 0, **including L0 at 4.59M cells in 71.6 s serial**, on this box, at
this memory state.

## 7. COST (rule 12) — ESTIMATED HERE, ACTUAL TO `docs/COST_CALIBRATION.md`

Cost basis: **core-minutes = wall s × ranks / 60**. Dollars **DERIVED, NOT MEASURED**, at the
owner-stated c7a.4xlarge **$0.0513/core-h** — this box cannot read its own billing.

Measured stage-2 one-iteration wall times, serial: L2 1.17 s, L1 7.98 s, L0 71.62 s.

| item | basis | core-min (est.) | $ derived |
|---|---|---:|---:|
| L2 full, 5000 steps, 4 ranks | 1.17 s/it × 5000 ÷ 4-rank speedup 3.2 | 121.9 | 0.104 |
| L1 full, 5000 steps, 4 ranks | 7.98 s/it, same | 831.3 | 0.711 |
| L0 full, 5000 steps, 4 ranks | 71.62 s/it, same | 7,460.4 | 6.379 |
| L0 repeat at `maxCo 0.1` (§4.4) | as above | 7,460.4 | 6.379 |
| stage-3 smokes (8 % of L2) | measured at run time | ~9.8 | 0.008 |
| **TOTAL (estimate)** | | **≈ 15,884** | **≈ $13.58** |
| **CAP (charter §1: 3× estimate)** | registered, **does not stop this run** | **47,652** | **$40.75** |

**The 3.2× four-rank speedup is an ASSUMPTION, not a measurement**, and is the largest single
uncertainty in the table. Stage 4's first checkpoint measures it and the calibration row states the
ratio actual/predicted with the gap attributed.

**The cap is registered because `CASE_PROTOCOL_CHARTER` §1 requires one, and it is registered so the
overrun is MEASURABLE — not so it is enforceable.** §4's *"cap reached: stop, `NOT A RESULT`, never a
raised cap"* is **suspended for M6CP1** under §1 of this document. **This is the one place where the
charter at HEAD and Sanaa's 2026-09-10 exemption say different things, and the exemption is the
later and more specific instruction.**

**Cost is counted over EVERY solve under the run root**, from each log's own `ClockTime` and each
log's **own banner** `nProcs`, not from `decomposeParDict` (which can post-date a run). This is
deliberate: the predecessor family's accumulator read **3.8 core-min against 135.87 actually
spent — under-reporting by 37×** — because it counted only the graded case and not the diagnostics.
Diagnostic solves are real compute on real cores.

## 8. ROUTING

Detached under the runner daemon. Solver, autograder and monitor re-parented to **PPID 1** so a
fleet death does not take the run with it. **rc is captured INSIDE the detached wrapper, from the
solver process, and written to `RC.txt`** — `setsid timeout cmd` exits 0 for every outcome including
SIGFPE, so no launching process's exit status is consulted anywhere.

## 9. MONITOR STOPS — ONE REGISTERED ACTION EACH, NEVER THE SAME ACTION TWICE ON THE SAME STATE

| stop | action ladder |
|---|---|
| residual growth | halve `maxCo` → first-order `div(phi,U)` for the first 20 % → PARK |
| bounds violation (clamp firing at the plateau) | raise ceiling as a **diagnostic** (pinning at any ceiling means unbounded) → PARK |
| plateau with a stalled linear solver | raise `maxIter`, tighten `relTol` on the stalled equation → PARK |
| **coherent oscillation** | **mark `physics voting unsteady`**, record frequency and amplitude, refer the steady/unsteady question — **this is not a failure** |
| cost/iteration > 2× estimate | **report only**; under §1 it does not stop a 3D demo run |

**On the bounds stop specifically:** the previous attempt on this case stopped here, with ~113 cells
pinned at a 1000 K ceiling and a raised-ceiling diagnostic showing they pin at **whatever** ceiling
is set — unbounded, not a finite hot value. Adiabatic recovery temperature at M∞ = 0.84 is ≈324 K.
**A clamp active at the plateau is a boundary condition on the answer, not a stabiliser.**

### 9.1 THE STAGE-4 LADDER — AND IT IS NOT THE STAGE-3 LADDER

Stage 3 climbs **mesh → numerics → model**, because a failing smoke is asking whether the case is
set up right. **Stage 4 climbs a different ladder**, because a full run that stalls is asking how to
*reach* a state the setup can already represent:

1. **Continuation from a converged neighbour** — the next coarser level's converged field mapped up,
   or the same level at an easier operating point. The cheapest fix for a hard start is not to start
   hard.
2. **Relaxation reduction** on the misbehaving equation. Relaxation affects only the **path** to
   steady state — its contribution scales with (φ_new − φ_old) and vanishes at convergence — so the
   converged answer is unchanged and the gate stays unbiased.
3. **Pseudo-transient** (`localEuler` / LTS). Reaches states a steady solve cannot. **Owes the
   time-step-independence demonstration of §4.4.**
4. **Transient re-registration.** If the flow will not hold still, the honest instrument is a
   transient one. This is a **new registration, not an amendment**: it changes what is being
   measured.

**Ladder exhausted parks the case `NOT A RESULT` with its lesson.** Parking is the designed outcome
of an exhausted ladder.

### 9.2 IF THE RUN ROUTES TO GPU

The base case registered here is **CPU on this box**. **GPU spend sits outside the 2026-08-21 CPU
blanket** and is not covered by the CPU rate in §7: a GPU route requires its own `cost_basis` in
**GPU-hours priced from the console, never from recall**, and a GPU is a **separate instance,
launched per run and stopped when idle** — no GPU is attached to this box. Routing is the
supervisor's determination; this registration does not assume it.

## 10. GRADING PATH — PINNED BY HASH, AND THE INVOCATION IS PART OF IT

Pins are repo-relative (a bare filename reports PIN-ABSENT while the file sits present and clean).
**Every invocation is pinned as an argv LIST, not a shell string**, so a missing flag shows as a
diff rather than needing a parse — cfd's `R1b` died with every blob correctly pinned and the argv
pinned nowhere.

Guards report `armed_by_pin`, **`arming_datum_present` and `arming_value`**: a pin proves a file
unchanged, and only evaluating the guard's condition against that pinned blob proves the check is
**awake**.

**The freeze checker is invoked with `--restrict-to-registration`, and that flag is part of the
pinned argv.** Unrestricted it exits 3 regardless of this registration's own cleanliness, because
rows belonging to other campaigns are unfrozen — a gate no case can pass is a stop, not a gate.
**`pins_unseen` is read and reported**: the checker can exit 0 while pins it could not judge exist,
and an instrument that could not look must not produce the same output as one that looked and found
nothing.


## 10.1 PIN TABLE — every executable in the grading path, by git blob sha

Paths are **repo-relative**. Blobs are **git blob shas** (`git hash-object`), which is what the
freeze hook needs to derive whether a pin's last commit is an ancestor of the freeze commit.
**Ancestry is not computed in this document** — that derivation is the hook's, deliberately, because
a hand-verified ancestry is one a supervisor eventually gets wrong.

| role | path | git blob sha | sha256 |
|---|---|---|---|
| comparator | `verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py` | `da0df95c81ded5833821cfd8a1f711d7f849f93c` | `d7ca635fb0fcc5d9…` |
| other | `scripts/case_protocol_lib.py` | `8b46845699ded3fabb40024d0cc3dfac48462590` | `cba0d16c61dc990f…` |
| other | `scripts/case_protocol_stage1_setup.py` | `8701dc81de64ac14266c06c9b22f2818e7bc4aff` | `a7cce03efb6f555e…` |
| other | `scripts/case_protocol_stage2_bugcheck.py` | `ba07947ab6dd50fdc583ef0ab7ee7e17cb89146f` | `c88de63d3dc2818a…` |
| launcher | `scripts/case_protocol_stage3_smoke.py` | `e25fc060103b2769d8fa5c8092966bfc6324d423` | `ed904d3a18199774…` |
| launcher | `scripts/case_protocol_stage4_run.py` | `425aeed988ae63843a851b9aa720a721a142c98c` | `c65be6f06e7e956a…` |
| manifest | `scripts/case_protocol_freeze_manifest.py` | `b3df462b32054457bc0b45e965ea4b2f4cff0ee4` | `7f866b3cf97af0f7…` |

**The freeze checker is invoked RESTRICTED** — `--restrict-to-registration` — and that flag is
pinned as argv in `FREEZE_MANIFEST.json`, not remembered. Its `pins_unseen` count is read and
reported: **an exit 0 with unseen pins is not a clean result**, because those pins were judged
by nothing.

## 11. WHAT A PASS HERE IS NOT

**A rc = 0 run at `endTime` is not a converged solution and is not a graded result.** The 24
existing diagnostic solves that exit rc = 0 at t = 500 prove the solver survives and prove nothing
about the answer. A pseudo-transient run that survives is the beginning of this case.

## 12. FREEZE BLOCK — LEFT FOR THE cfd-SUPERVISOR (check 4, undelegated)

```
FROZEN BY:        cfd-supervisor (Opus 5), 2026-09-10, check 4 undelegated
FREEZE COMMIT:    the commit carrying this document; verify with
                  git log -1 --format=%H -- verification/campaign/M6CP1_PREREGISTRATION.md
REGISTRATION BLOB:verify with
                  git rev-parse HEAD:verification/campaign/M6CP1_PREREGISTRATION.md
                  (self-reference is why these two are POINTERS, not transcribed
                   digits: a document cannot state its own blob without changing it)
NO COMPUTE UNDER THIS DOCUMENT AS AT FREEZE, verified with a live planted control:
  present-reader returned PRESENT on verification/runs/navier_class/SUBOFF/r1b_fine
    -- 1 hit, verification/runs/navier_class/SUBOFF/r1b_fine/2500. The reader is
       SHOWN ABLE TO SEE a time directory before its absence is believed (rule 3).
  same reader returned ABSENT on verification/runs/M6CP1_runs/{L0,L1,L2}  0 hits each
    -- and it REFUSES rather than reports if the known-positive comes back empty.
```

**AFTER THE FREEZE COMMIT THE GATES ARE CLOSED.** Changes land only as dated addenda that cannot
alter a gate, threshold, cap or label. Originals are struck, never rewritten.

---

## AMENDMENT 1 — 2026-09-10, cfd-supervisor (Opus 5). Document version v1.0 → v1.1.

**lines whose number changed above this section: 0**

**This amendment alters NO gate, NO threshold, NO cap and NO label.** Gate P (±0.02 in Cp at seven
span stations), Gate G (the rule-5 Roache triple on {L2, L1, L0}), the plateau limb of §5.1 (trailing
20 % window, max abs deviation from the window mean, tolerance 5.0e-04), the §1 budget position
(`budget_gate: NONE — Sanaa 2026-09-10`) and the §10/§10.1 grading path with its pin table all stand
exactly as frozen. Nothing below may be read as changing any of them.

### A1.1 THE HEADER BANNER IS STRUCK. IT IS NOW FACTUALLY FALSE AND DANGEROUSLY SO.

The banner at the head of this document reads **"THIS FILE IS A DRAFT. IT IS NOT FROZEN, NOT
AUTHORISED, AND NO GRADED SOLVE HAS RUN UNDER IT"** and says the §12 freeze block is left blank. It
was true when the drafting lane wrote it and it stopped being true at the freeze commit. **All three
of its assertions are now false:** the document IS frozen, §12 IS filled, and compute HAS occurred
under it. **The banner is STRUCK — it is not rewritten, per rule 6, because originals are struck and
never rewritten, and because striking it here costs zero changed line numbers above.**

**Why this could not be left to stand.** A reader arriving at this file meets "NOT FROZEN, NOT
AUTHORISED" in its first screen and "FROZEN BY: cfd-supervisor" in its last. A document that
contradicts itself about its own authorisation status is the precondition for either error: a run
launched under a document a later reader believes was never frozen, or a freeze abandoned because
its face said draft. The authoritative status of this registration is **FROZEN**, at commit
`852e77ff8`, registration blob `543ffe291e4d8c01e544e4d4d4541a961877ffe6` — supervisor-verified by
hashing the working file against the committed blob, all three of worktree, freeze commit and HEAD
agreeing.

### A1.2 COMPUTE HAS OCCURRED UNDER THIS DOCUMENT. THE GATES ARE CLOSED.

At the freeze, §12 recorded no compute, verified by a live planted control. **That statement was true
at the freeze and is now superseded by events, not by error.** Three stage-3 smoke rungs have since
run:

| rung | level | utc | outcome | cause |
|---|---|---|---|---|
| M0 baseline | L2 | 17:53:48Z | FAIL — bounded but nonphysical, clamps firing, Cl = −0.3089 | ENERGY_RUNAWAY_TRAILING_EDGE |
| M1 mesh tier | L1 | 18:16:37Z | STOPPED (classed stop) — divergence, Cl = 1.481e+30 | ENERGY_RUNAWAY_TRAILING_EDGE |
| N1 numerics tier (`transonic yes`) | L2_N1 | 18:22Z | FAIL — see A1.3 | under adjudication, A1.4 |

**Per rule 2 the gates of this registration are therefore CLOSED**, and every further change lands as
a dated addendum of this kind. **No stage-4 full run has launched and none is authorised while
stage 3 stands unpassed** — §11 of this document already says a rc = 0 run at `endTime` is not a
graded result, and a stage-4 launch over a failing smoke would spend hours to produce `NOT A RESULT`.

### A1.3 THE N1 RUNG DID NOT FIX IT — SUPERVISOR'S READ, TAKEN FROM THE LOG BY HAND

`transonic yes` was the §4.2 lever, made pullable when `div(phid,p)` was supplied. It did not repair
the case. Read directly from
`verification/runs/M6CP1_runs/L2_N1/smoke/log.rhoPimpleFoam` at Time = 400, rc = 0, 117.66 s:

- **energy initial residual pinned at 0.9999999824 on every iteration**, final residual 3.089e-20.
- **momentum frozen**: Ux/Uy/Uz initial residuals 5.211e-08 / 5.318e-08 / 5.122e-08.
- **clamps firing steadily at BOTH ends**: 225 cells at the 100 K floor, 124 at the 1000 K ceiling.

Against the registered prediction `max_clamped_cells = 0` this is a **GENUINE FAIL**, and against
§9's bounds stop it is the named condition: *a clamp active at the plateau is a boundary condition on
the answer, not a stabiliser.* An energy residual that sits at 1.0 for four hundred iterations while
the velocity field does not move is not a slow march; it is a clamp-held fake steady state.

### A1.4 A SUPERVISOR'S CHALLENGE TO THE M1 CONCLUSION, REGISTERED BEFORE IT IS TESTED

M1 concluded the trailing-edge hot cells are **NOT** a mesh artifact, on two grounds: they sit at the
same x/c on L2 and L1, and refinement makes the failure worse. **The ladder then spent its mesh tier
and pivoted to numerics on that conclusion.** The cfd-supervisor is challenging it, and registering
the challenge here before the test rather than after:

**A sharp trailing edge with near-degenerate sliver cells ALSO follows the geometry and ALSO worsens
on refinement**, because slivers grow thinner as the grid refines. So the M1 evidence does not
discriminate between an unstable scheme and a defective trailing-edge topology — both hypotheses
predict exactly what M1 measured. Two further recorded numbers sit badly with the "scheme" reading:
a wing-patch **y+ max of 149,276 against a geometric first-cell y+ of 187**, a factor of ~800, and a
**Cd of 1.52 on a wing**, which is a bluff-body figure.

The adjudication is dispatched: mesh quality at the trailing edge, colocation of worst-quality cells
against hot cells, the LTS `rDeltaT` field (M1 recorded a min flow time scale of 4.97e-30, which
would itself explain both the frozen momentum and the wrecked energy normalisation), and a direct
read of patch types and wall treatment. **Its outcome decides whether the stage-3 ladder continues on
this mesh family or M6CP1's family is the defect** — and the latter would be a NEW registration, not
an amendment to this one, because it changes what is being measured.

### A1.5 A RECORDING DEFECT IN THE LADDER HISTORY, DISCLOSED NOT REPAIRED

Attempt 3 in `verification/runs/M6CP1_runs/STAGE3_LADDER_HISTORY.json` is recorded with
`rung_id: "baseline"` and `cause: "final_residual_U"`. **Both appear wrong**: the run was the N1
numerics rung, and `final_residual_U` is the **known reader defect** already documented in attempt
1's correction — `rhoPimpleFoam` emits `Ux`/`Uy`/`Uz` and no `Solving for U` line, so the reader
returns `measured=None` and labels COULD-NOT-RUN as FAIL. **The reader is a pinned launcher and
compute has occurred, so it is NOT repaired here**; the proposed repair stays staged unapplied at
`verification/runs/M6CP1_runs/PROPOSED_REPAIR_stage3_smoke.py` and the question is referred to
verification under `VERIFICATION_CHARTER` §2d.1. **It is disclosed rather than fixed because a
supervisor quietly repairing a pinned instrument after compute is the exact move the freeze exists to
prevent** — and because `cause` is the field the two-fails-same-cause rule climbs rungs on, so a
contaminated cause can buy a rung the case did not earn.

---

## AMENDMENT 2 — 2026-09-10, cfd-supervisor (Opus 5). Document version v1.1 → v1.2. **THE CASE IS PARKED `NOT A RESULT`.**

**lines whose number changed above this section: 0.** No gate, threshold, cap, band or label is altered.
Gate P, Gate G, the §5.1 plateau limb, the §1 budget position and the §10/§10.1 grading path all stand
as frozen. **This amendment records an outcome; it does not move a gate.**

### A2.1 THE VERDICT

**`NOT A RESULT`.** Cause class **`ENERGY_RUNAWAY_TRAILING_EDGE`**, three stage-3 smokes on one cause
(M0 baseline L2, M1 mesh-tier L1, N1 numerics-tier L2_N1), parked under CASE PROTOCOL CHARTER §3's
three-strikes rule. **No stage-4 run was ever launched and Gate P and Gate G were never evaluated** —
so this is a case parked before grading, not a gate that returned a value.

### A2.2 THE MECHANISM — A COLLAPSED TRAILING EDGE, AND IT IS SCALE-INVARIANT

**The trailing edge of this mesh closes to a single point per spanwise station. There are ZERO cells
across it.** Measured off the wing patch's own point list, planted control at each level (a threshold
below the field minimum selected 1595/1595, 6309/6309 and 25097/25097 points):

| level | last chordwise cell Δx | Δy | **cusp half-angle** |
|---|---:|---:|---:|
| L2 | 3.17e-04 | 5.683e-04 | **60.85°** |
| L1 | 1.58e-04 | 2.842e-04 | **60.92°** |
| L0 | 7.90e-05 | 1.421e-04 | **60.92°** |

**The cusp half-angle is 60.9° at every level: refinement halves the cell and never opens the cusp.**
Supporting geometry: wall-face area jumps **47.07×** aft of 0.995c, max/min wall-face area ratio
**7,212:1**, and the globally smallest cell in the L2 mesh is a trailing-edge first cell.

**This settles the challenge registered in A1.4 IN FAVOUR OF THE CHALLENGE.** M1 ruled out a mesh
artifact because the hot cells sit at the same x/c on two levels and refinement worsens the failure.
**A scale-invariant cusp produces both signatures by construction** — it follows the geometry because
it *is* geometry, and its cells thin at every refinement while the pathology keeps its shape. The M1
evidence never discriminated between the hypotheses, and the mesh tier was spent on a conclusion the
measurement could not support.

### A2.3 LTS IS THE AMPLIFIER, NOT THE SEED — AND §4.4's DEMONSTRATION IS OWED AND UNPAID

From the N1 log at t = 400:

    Flow time scale min/max          = 1.003212828e-16, 0.005513522401
    Smoothed flow time scale min/max = 1.003212828e-16, 8.584167179e-13

**The RAW maximum is 5.514e-03 s and is healthy. After `fvc::smooth` at `rDeltaTSmoothingCoeff 0.1`
the maximum is 8.584e-13 s — a factor of 6.4e9.** The smoothing operator propagated a trailing-edge
collapse to **100 % of cells**. Four hundred steps advanced roughly **4e-11 s** of pseudo-time: the
freestream moved **11 nanometres** against a 0.806 m chord.

**So the frozen momentum and the pinned energy residual recorded in A1.3 are NOT reader defects.**
`rho·rDeltaT·V` dominates the diagonal by ~15 orders, nothing can move or relax away an error already
present, and `limitTemperature` resets e every step while that diagonal solves the reset exactly. It
was healthy at t = 1 (flow time scale min 1.486e-07 s, `LimitedCells = 0` at both ends): **nine
decades of collapse developed over 400 steps.** §4.4 registered that LTS owes a time-step-independence
demonstration. **It was never paid, and this is what it would have caught.**

### A2.4 THE PHYSICS UNDERNEATH IS NOT THE PROBLEM

**N1's PRESSURE lift coefficient is +0.1915 — inside this registration's own [0.15, 0.45] band.** The
entire runaway is viscous, on cells reaching 5.1e10 m/s. The recorded y+ max of 149,276 and Cd of 1.52
are wall-shear artifacts, not measurements: **y+ MINIMUM holds at 8.65 across every write** (8.659 →
8.651 → 7.607 → 8.651) while the maximum grows to 1.886e10. Patch types are clean — `wing` wall,
`symmetry` symmetry, `farfield` patch, zero `empty`, zero `wedge`, the tip closed by 64 wall faces so
the wing is not silently mirrored into infinite span — and the wall treatment
(`nutUSpaldingWallFunction`, all-y+) is admissible against y1 = 2.4271e-04 m.

### A2.5 M6SR IS NOT THE ESCAPE HATCH — RECORDED SO THE NEXT READER DOES NOT TRY IT

`M6SR_runs/L1` (1,597,440 cells, a different build route) wraps **the same ONERA M6 surface with the
same cusped trailing edge in the same hex topology.** It fails the same two checks and is **worse** on
max non-orthogonality (69.97° vs 60.86°) and min cell volume (8.35e-12 vs 2.43e-11). **Switching family
does not remove the cusp, so it does not remove the mechanism**, and its farfield at ~13 m against
M6CP1's 45 m would make blockage a new registration question rather than an inherited one.

### A2.6 WHAT THE SUCCESSOR NEEDS — A MESH RUNG, UNDER A NEW REGISTRATION

Either a **C-grid with a wake cut** — the standard ONERA M6 validation topology, which puts the sharp
trailing edge on the wake line instead of wrapping cells around it — or a **blunted trailing edge with
2–4 cells across it at ~0.5 % chord. Either is a new mesh family: new birth certificates, new triple,
new freeze.** It is §1/§2 work under a **new registration, not a stage-3 rung on this one**, because it
changes the mesh the gate is defined on.

### A2.7 🔴 THE FINDING THAT OUTLIVES THIS CASE — **THE STAGE-2 GATE WAS BLIND**

**Plain `checkMesh` prints `Mesh OK.` on M6CP1 L2. The same mesh under `-allGeometry -allTopology`
prints `Failed 2 mesh checks`** — 68 low-quality tet faces and 9,854 under-determined cells (13.73 %).
At L0 the full set finds **332 low-quality tet faces and 656,877 under-determined cells**, while
`STAGE2_RECORD.json` records `mesh_ok: true, failures: []`.

**The face-tet and cell-determinant checks only run under `-allGeometry`.** CASE PROTOCOL CHARTER §2's
exit condition — *"checkMesh on every level: quality within the registered gates or the case stops"* —
**was evaluated by an instrument structurally incapable of seeing either failing check. M6CP1 spent
three stage-3 rungs on a case its own stage-2 gate could never have refused.** Every stage-2 gate in
this lab that shells out to bare `checkMesh` has the same hole.

**And the gate is not merely mis-invoked — it is insufficient. `checkMesh` passes this trailing edge
under BOTH check sets.** A 60.9° collapsed wedge and a 7,212:1 wall-face-area ratio need a limb of
their own: **minimum cells across every named geometric feature, and a wall-face-area-ratio ceiling.**

**THE AUDIT WENT FURTHER AND THE DEFECT IS DEEPER THAN "THE WRONG FLAGS".** Three measured facts:

1. **`grep -rn "allGeometry\|allTopology" scripts/` returns ZERO HITS.** Not one script in this lab's
   script tree has ever asked for either flag.
2. **`checkMesh` RETURNS `rc = 0` EVEN WHEN CHECKS FAIL.** All four `-allGeometry -allTopology` runs
   returned rc = 0 while printing `Failed 2 mesh checks` (`DIAG_D1/checkMesh_L2.rc` and siblings). So
   stage 2's verdict at `scripts/case_protocol_stage2_bugcheck.py:147` —
   `ok = ("Mesh OK." in out) and rc == 0` — **rests entirely on the substring; the `rc == 0` clause
   contributes nothing at all.**
3. **STAGE 1 DOES NOT RUN `checkMesh` AT ALL.** `scripts/case_protocol_stage1_setup.py:185-193`
   substring-matches a **pre-existing log it did not produce**. For M6CP1 that log is
   `verification/runs/M6_OWN_FAMILY_runs/L2/case/log.checkMesh` — **the MESHER's log, in a DIFFERENT
   campaign tree, from a bare invocation.** Stage 1 also collects `checkmesh_stars` (lines beginning
   `***`), which is the right idea and returns an **empty list**, because a bare `checkMesh` emits no
   `***` lines on this mesh: **a well-designed instrument fed a blind input.**

**So the defect is NOT "stage 2 used the wrong flags". It is that THE PROTOCOL'S MESH-ADMISSION
VERDICT IS A SUBSTRING MATCH WHOSE TRUTH VALUE IS SET BY AN INVOCATION THE PROTOCOL DOES NOT
CONTROL.** The admission criterion for this family reduces to *"did some earlier run, elsewhere, print
the string that the blind invocation always prints on this mesh"*. **Fixing it requires both flags AND
stage 1 running its own `checkMesh` rather than trusting a foreign log** — and a geometry limb a cusp
cannot pass, since `checkMesh` clears this trailing edge either way.

Referred to the chief and to verification as a lab-wide instrument defect; it is not cfd's to rule.

### A2.8 A WITHDRAWAL BY THE DIAGNOSING LANE, RECORDED BECAUSE IT IS THE BEHAVIOUR WE WANT

The lane's first pass found the hot cells **6.66× enriched** in checkMesh's under-determined set and
**withdrew it on its own conditioning**: a high-aspect-ratio boundary-layer cell has a low determinant
by construction, so conditioned on wall distance the fair enrichment is **0.943 — below 1.0**. The
counter-example is in the same data: mid-chord first cells are **100 % under-determined and perfectly
healthy** (T median 287.4 K), while trailing-edge first cells are only **65.9 % under-determined and
destroyed** (T median 137.9 K, |U| max 2.98e10 m/s). **The quality flag is anti-correlated with the
damage**, and the cusp geometry — measured directly — carries the finding instead.

**Honest limit, stated by the lane and not softened here:** this does **not** prove the causal chain
from cusp to runaway. It shows the runaway is spatially confined to the cusp and that no BC,
patch-type or quality-flag explanation survives. Distinguishing "mesh topology defect" from "genuinely
unstable scheme" at the last 1 % of chord needs the controlled experiment — the same numerics on a
wake-cut or blunt-TE grid — **which is the successor registration, not a diagnosis.**

### A2.9 COST

Adjudication **5.38 core-min** (1 rank; 211.76 core-s measured, ~111 core-s of earlier untimed Python
passes **estimated, not measured**, and labelled so in `DIAG_D1/DIAG_D_SUMMARY.json`). Stage-3 rungs
M0 + M1 + N1 = 22.79 core-min. **Total under this registration: 28.17 core-min, $0.0241 DERIVED, NOT
MEASURED** at $0.0513/core-h — the box cannot read its own billing. Estimate-versus-actual calibration
is owed to `docs/COST_CALIBRATION.md` under rule 12 and is not discharged by this amendment.

---

## ADDENDUM 3 — 2026-09-10 — **`[SANAA-DIRECT]`**. Document version v1.2 → v1.3. **A DIRECTED RUN OVER A PARKED CASE, WITH ITS FAILURE PREDICTED IN ADVANCE.**

**lines whose number changed above this section: 0.** Proven, not asserted: every line above this
section is byte-identical to `git show HEAD:verification/campaign/M6CP1_PREREGISTRATION.md`
(HEAD `206f7910a`, registration blob `e5f474db33e523049378c6443c1732b507d856b2`), verified by
`diff` of the first 642 lines against the committed blob — zero differing lines. This addendum is a
pure append.

**This addendum alters NO gate, NO threshold, NO cap, NO band and NO label.** Gate P (±0.02 in Cp at
seven span stations) and Gate G (the rule-5 Roache triple on {L2, L1, L0}) stand exactly as frozen.
The §5.1 plateau limb (trailing 20 % window, max absolute deviation from the window mean, tolerance
5.0e-04) stands. The §10/§10.1 grading path and pin table stand. `budget_gate: NONE — Sanaa
2026-09-10` stands. **Amendment 2's `NOT A RESULT` park stands and is NOT lifted by this addendum** —
it stands until a graded run replaces it, and this addendum authorises a run, not a verdict.

### A3.1 THE INSTRUCTION, AND WHOSE IT IS

**Sanaa, 2026-09-10, byte-exact:**

    M6CP1 launch asap.

**The decision to run is Sanaa's and is recorded as hers.** It is not a lab determination, not the
cfd-supervisor's, and not this lane's. No agent's message is her consent (standing rule 9); this is
her own instruction, relayed through the cfd-supervisor and executed by a cfd `lab-lane`. **The lab's
own standing position, recorded in Amendment 2 four hours earlier, was that this case is parked.**
That position is unchanged; it has been overridden by the owner, which she is entitled to do, and the
override is recorded here rather than quietly absorbed.

**🔴 TIMESTAMP — RESOLVED BY THE cfd-SUPERVISOR, AND THE HONEST ANSWER IS THAT IT CANNOT BE
CORROBORATED.** The lane was right to refuse to write it. The relayed stamp was **~20:40Z**; the
lane's own `date -u` read **20:23:12Z** when it began drafting this addendum — i.e. **before** the
instruction was supposedly given — and the supervisor's own `date -u` read **20:43:01Z** at commit.
A relay carrying a later stamp than the box clock showed when the relayed instruction was already
being acted on **cannot all be true**, and a second relayed quote that arrived *after* this one
carries an *earlier* stamp (~20:35Z), which confirms the relayed times are approximate rather than
measured.

**So the time is recorded as UNCORROBORATED and is not written as fact.** What is established:
**the date is 2026-09-10**, not in question; **the instruction reached the cfd-supervisor before
20:23:12Z**, because the lane was already drafting against it then; and **this addendum was committed
at 2026-09-10T20:43:01Z or later**, by the supervisor's own clock. **The wording of the instruction
is byte-exact and is the part that matters; its wall-clock stamp is relayed, not measured, and is
labelled so.** No verdict, gate or cost depends on the minute.

### A3.2 WHAT IS AUTHORISED, AND IT IS ONE LEVEL

**L2 only — 71,760 cells — first and alone.** L1 and L0 are **NOT** launched by this addendum and are
not authorised by it. L2 carries the whole decisive diagnostic (§A3.4) and reaches it in about two
minutes of one core. **Spending L0's 4,592,640 cells to reproduce a hypothesis L2 can test is waste,
not rigour**, and whether L1 and L0 follow is the cfd-supervisor's call after L2 answers.

**Ranks: 1 (serial).** Justified from measurement, not preference:

- `verification/runs/M6CP1_runs/L2/case/system/decomposeParDict` reads `numberOfSubdomains 1`. Any
  rank count above 1 requires **editing a case file under a frozen registration before compute**, and
  this lane will not do that for a convenience.
- **Both stage-3 smokes ran serial** — `nProcs : 1` in each log's own banner
  (`L2/smoke_M0_baseline/log.rhoPimpleFoam`, `L2_N1/smoke/log.rhoPimpleFoam`). Serial is therefore the
  **like-for-like** configuration: the graded run's trace is directly comparable to the failing one,
  with no decomposition confound between them.
- **Measured box state, 20:26Z: 6 of 16 vCPU CPU-bound** — one `buoyantBoussinesqSimpleFoam`
  (T-family T4e), one `rhoCentralFoam`, and four `simpleFoam -parallel` (the navier_class MRF coarse
  level, 40 s old at the reading). Load average read 40.72 but `vmstat` showed `r = 2, b = 40` with
  11–74 % iowait: **the box is I/O-bound on concurrent repository sweeps, not CPU-saturated**, and
  reporting load average alone would have misread it. **By 20:33Z the cfd-supervisor's own reading was
  `0.0 id, 36.3 wa` with ten processes above 50 % CPU**: MRF coarse at 4 ranks, MRF medium at 3, and
  MRF fine released. **MRF has priority over M6CP1 stage 4** — it can plausibly deliver a `CONVERGING`
  triple, and M6CP1 is expected to reproduce a known failure. **A serial M6CP1 leaves MRF its full
  claim on a box that has none to spare.**
- **🔴 AND THE RANK COUNT IS NOT FREE TO CHOOSE.** `numberOfSubdomains 1` means 1 rank is the only
  count that runs this case **as frozen**. Two ranks is not a smaller ask than four; it is the same
  ask — **an edit to a case file under a frozen registration, before compute** — and it would also
  break the like-for-like comparison with the two serial smokes. Serial is both the least invasive
  and the least contentious option, and it is the one taken.

**The box is re-derived in the same shell invocation the launch is issued from**, and that reading —
not this paragraph — is the one recorded in `STAGE4_MANIFEST_L2.json` and in the launch report.

**§7's 3.2× four-rank speedup is an ASSUMPTION and a serial run DOES NOT MEASURE IT. It remains owed.**

### A3.3 🔴 THE EXPECTED OUTCOME, STATED BEFORE THE RUN, AND WHY IT IS EXPECTED

**The prediction is that this run reproduces `ENERGY_RUNAWAY_TRAILING_EDGE` and returns
`NOT A RESULT`.** It is registered here so that it is falsifiable. A run whose likely failure is
predicted in advance is worth more than one that is not, because the prediction can be wrong.

**The ground for it is not an inference. It is a one-line diff.** The graded case
`verification/runs/M6CP1_runs/L2/case` and the failed M0 baseline smoke
`verification/runs/M6CP1_runs/L2/smoke_M0_baseline` were compared directory by directory:
`0/` identical, `constant/` identical (both `polyMesh` symlinks resolve to the same target,
`M6_OWN_FAMILY_runs/L2/case/constant/polyMesh`), `system/` identical **except `controlDict`**, whose
entire difference is:

    14c14
    < endTime         400;
    ---
    > endTime         5000;

**The stage-4 graded run IS the M0 baseline smoke that already failed, with `endTime` raised from 400
to 5000. No lever was pulled between them.** Same `localEuler`, same `maxCo 0.2`, same
`rDeltaTSmoothingCoeff 0.1`, same `limitTemperature` 100/1000 K, same `transonic` unset,
same `writeInterval 100`.

**The mechanism is A2.2's cusp and it is scale-invariant**: the trailing edge closes to a single point
with **zero cells across it**, half-angle 60.85 / 60.92 / 60.92° at L2 / L1 / L0. Refinement halves
the cell and never opens the cusp, so no level escapes it and `endTime` cannot outrun it.

**Measured trace of the failure, read from `L2/smoke_M0_baseline/log.rhoPimpleFoam` (rc = 0 in
`RC.txt`, `End` present, 400 `ExecutionTime` lines, ClockTime 130 s, nProcs 1):**

| quantity | step 1 | step 400 |
|---|---:|---:|
| Flow time scale max (raw) | 5.513522401e-03 s | 5.513522401e-03 s (pinned, healthy) |
| Flow time scale min (raw) | 1.486160412e-07 s | 4.290190414e-09 s |
| **Smoothed flow time scale max** | **8.966499742e-05 s** | **7.121542696e-06 s** |
| `limitTemperature` Lower `LimitedCells` | 0 (`UnlimitedTmin` 288.15) | **704, 0.98 %, `UnlimitedTmin` = 100** |
| `limitTemperature` Upper `LimitedCells` | 0 (`UnlimitedTmax` 288.15) | **142, 0.20 %, `UnlimitedTmax` = 1000** |

**The clamp is pinned AT its own limits at both ends** — `UnlimitedTmin` equal to the floor and
`UnlimitedTmax` equal to the ceiling is A2.2/§9's signature of unbounded, not of a finite hot value.

**THE THREE REGISTERED PREDICTIONS, IN DESCENDING ORDER OF STRENGTH:**

- **P1 — BIT-IDENTITY THROUGH STEP 400.** Because the only difference from the M0 smoke is `endTime`,
  the graded run's step-400 smoothed flow time scale max must read **7.121542696e-06 s** and its
  clamp counts must read **704 / 142**. This is a near-deterministic prediction, not a trend. **A
  departure here is itself a finding** — either solver non-determinism, or a difference between the
  two cases this lane failed to find.
- **P2 — COLLAPSE CONTINUES TO `endTime`.** The smoothed maximum falls **below 1e-10 s by step 5000**.
  **🔴 THIS IS AN EXTRAPOLATION, NOT A MEASUREMENT**, and it is labelled so: the observed rate is
  ~1.1 decades per 400 steps and 5000 steps is **12.5× the observed span**. It is registered because
  a log-linear extrapolation stated before the run is falsifiable and a hunch is not.
- **P3 — THE CLAMP STAYS LIT.** `limitTemperature` reports `LimitedCells > 0` at **both** ends at
  `endTime`. Against this registration's own prediction of **`max_clamped_cells = 0`** that is a
  `GATE FAIL` on the clamp limb, and against §9's bounds stop it is the named condition.

**Expected verdict: `NOT A RESULT`** via Gate G's limb (1) — *any level not iteratively converged or
not plateaued.* **Gate P is not expected to be reached at all**, because Gate P sits behind Gate G.

### A3.4 THE DECISIVE DIAGNOSTIC IS THE LTS FIELD, NOT THE RESIDUALS — AND THAT IS A MEASURED LESSON

**At N1 the momentum initial residuals read 5.211e-08 / 5.318e-08 / 5.122e-08 while nothing was
moving, and the energy initial residual sat pinned at 0.9999999824 with a final residual of
3.089e-20.** Neither number meant what it appeared to mean. `rho·rDeltaT·V` dominated the diagonal by
~15 orders, `limitTemperature` reset `e` every step, and the linear solver solved that reset exactly.
**A residual trace cannot distinguish a converged flow from a frozen one.** Four hundred N1 steps
advanced the freestream **11 nanometres** against a 0.806 m chord.

**So the watch on this run is the LTS field.** `Flow time scale min/max` and
`Smoothed flow time scale min/max` in `log.rhoPimpleFoam`, plus `limitTemperature`'s `LimitedCells`
at both ends. **If the smoothed maximum collapses, the run is frozen no matter what the residuals
say.**

**The honest distinction between the two smokes, which this addendum will not blur:** the
**8.584167179e-13 s** smoothed maximum quoted in A2.3 is **N1's** (`transonic yes`), not the
baseline's. At the same step count the baseline stood at **7.121542696e-06 s** — eight decades
higher. **The baseline collapses more slowly**, and P2 says it gets there by step 5000 by
extrapolation, which is exactly the claim this run tests. Likewise **A2.4's in-band pressure Cl of
+0.1915 is N1's.** The M0 baseline's pressure Cl at step 400 is **+0.05368879024**, which is **below**
this registration's [0.15, 0.45] band; its total Cl is **−0.3089435035** and its total Cd
**2.61455128**. **The "physics underneath is fine" reading rests on N1's numbers, and it is not
carried over to the baseline here.**

### A3.5 WHAT WOULD MAKE THIS PREDICTION WRONG — REGISTERED BEFORE THE RUN

**If the LTS field does not collapse and the run marches, that is a genuine finding and Amendment 2's
park must be revisited.** Any one of the following falsifies the prediction; all four together would
overturn the mechanism:

- **F1.** The smoothed flow time scale maximum **stabilises or recovers** — it stays above **1e-06 s**
  through step 2000 instead of continuing to fall. This directly falsifies **P2**.
- **F2.** The momentum initial residuals **move off the ~1e-08 floor** and the field actually
  advances: cumulative pseudo-time advancing the freestream by more than one chord (0.806 m) rather
  than by nanometres.
- **F3.** `limitTemperature` reports `LimitedCells = 0` at **both** ends across the §5.1 trailing
  window (the last 10 of 50 writes). This falsifies **P3** and clears §9's bounds stop.
- **F4.** The §5.1 plateau statistic is **satisfied** — max absolute deviation from the trailing-window
  mean, relative to that mean, **≤ 5.0e-04**.

**And a fifth outcome that is neither the prediction nor its falsification, named so it is not
mistaken for either:** the run may march (F1–F4 hold) and **still** fail Gate P or Gate G. That would
mean the park's *verdict* survives while the park's *mechanism* — A2.3's LTS collapse — is wrong. The
mechanism and the verdict are separately falsifiable and are recorded separately.

**A departure from P1 (bit-identity through step 400) is reported as a finding in its own right,
whichever direction it runs.**

### A3.6 ROUTING, rc AND THE TRAP THIS RUN IS BUILT AROUND

Launched by **`scripts/case_protocol_stage4_run.py`**, git blob
**`425aeed988ae63843a851b9aa720a721a142c98c`** — verified by `git hash-object` against §10.1's pin at
launch time, **matching**. The script **does not launch without `--go`**, and its preflight output is
read before `--go` is passed.

Detached, re-parented to **PPID 1**. **`rc` is captured INSIDE the wrapper, from the solver process,
and written to `RC.txt`** — `setsid timeout cmd` exits 0 for every outcome including SIGFPE, so no
launching process's exit status is consulted anywhere. §8 of this document already registers this and
it is restated because it is the trap that would silently turn a crash into a pass.

**Nothing about this run is graded by this addendum.** Grading is §10's pinned path, invoked by the
detached wrapper, and the verdict is the cfd-supervisor's to take.

### A3.7 COST (rule 12) — ESTIMATED HERE, BEFORE COMPUTE

Cost basis: **core-minutes = wall s × ranks / 60**. Dollars **DERIVED, NOT MEASURED**, at the
owner-stated c7a.4xlarge **$0.0513/core-h** — this box cannot read its own billing.

**The rate is MEASURED on this exact case**, not extrapolated from stage 2: the M0 baseline smoke ran
**400 steps in 130 s ClockTime at nProcs 1** → **0.325 s/step serial**.

| item | basis | core-min (est.) | $ derived |
|---|---|---:|---:|
| L2 graded, 5000 steps, **1 rank** | 0.325 s/step MEASURED × 5000 ÷ 60 | **27.1** | **0.0232** |

Against §7's registered L2 row of **121.9 core-min at 4 ranks**. **The difference is rank count, not a
speed surprise**, and §7's row is not amended — it stands as frozen and the calibration ledger states
the ratio with the gap attributed. **`budget_gate: NONE — Sanaa 2026-09-10`; no cap stops this run**,
and the estimate is calibration data rather than a gate. The rule-12 estimate-versus-actual row is
owed to `docs/COST_CALIBRATION.md` at completion and is **not** discharged by this addendum.

**Contention is named separately and not absorbed into the ratio:** the box carried 6 CPU-bound ranks
plus a heavy concurrent I/O load (`b = 40`, 11–74 % iowait) at launch, so the actual wall rate is
expected to exceed 0.325 s/step and the excess is **contention, not misprediction**.

### A3.8 WHAT THIS ADDENDUM DOES NOT DO

It does not lift the park. It does not move a gate, a threshold, a cap, a band or a label. It does not
authorise L1 or L0. It does not repair the stage-2 mesh-admission defect of A2.7, which stands
referred to the chief and to verification and is **not cfd's to rule**. It does not repair the pinned
stage-3 reader defect of A1.5, whose proposed repair stays staged unapplied at
`verification/runs/M6CP1_runs/PROPOSED_REPAIR_stage3_smoke.py`. **A supervisor or lane quietly
repairing a pinned instrument after compute is the exact move the freeze exists to prevent.**

---

## ADDENDUM 4 — 2026-09-10 — **THE DIRECTED RUN RAN, AND IT REPRODUCED THE PREDICTED FAILURE BIT-FOR-BIT.**

**lines whose number changed above this section: 0.** No gate, threshold, cap, band or label is altered.
**Amendment 2's `NOT A RESULT` park is UNTOUCHED — this run CONFIRMS it, it does not replace it.**
Gate P and Gate G **were never evaluated**: the run did not reach a graded state.

### A4.1 WHAT RAN, AND HOW IT ENDED — **STOPPED BY SUPERVISOR DECISION, NOT COMPLETED**

Solver pid **1597168** (`rhoPimpleFoam`, serial, `nProcs : 1`), cwd
`verification/runs/M6CP1_runs/L2/case`, wrapper pid 1596907 at **PPID 1**. Launched
**21:30:28Z**, stopped **21:37:56Z**, **759 steps of a registered `endTime` 5000**, 448 wall s.

**`RC.txt` reads `RC=143` = 128 + 15, i.e. SIGTERM. THAT IS A DECISION, NOT A CRASH**, and it is
written here so no later reader triages it as a failure. **There is NO `End` line, the last time is
759 against `endTime` 5000, and the autograder did not run.** **Nothing in this record claims rule-4
completion, because none of rule 4's clauses were met and none were meant to be.**

The stop was ordered once the run had answered: SIGTERM to **one explicit pid**, never `pkill`
(which matches its own invoking command line — a trap this supervisor then fell into anyway, see A4.5).

### A4.2 **P1 — CONFIRMED AS AN IDENTITY, NOT AS A SPOT CHECK**

**400 common steps, both logs parsed by the SAME code, compared step by step: the smoothed flow time
scale max AND both `limitTemperature` clamp counts are identical at EVERY comparable step.**

| step | live smoothed max | M0 smoothed max | clamps live | clamps M0 |
|---|---|---|---|---|
| 1 | 9.119010831e-05 | 9.119010831e-05 | 0/0 | 0/0 |
| 50 | 1.251459718e-05 | 1.251459718e-05 | 93/57 | 93/57 |
| 200 | 2.72679683e-05 | 2.72679683e-05 | 535/44 | 535/44 |
| 300 | 1.344690795e-05 | 1.344690795e-05 | 601/106 | 601/106 |
| **399/400** | **7.121542696e-06** | **7.121542696e-06** | **704/142** | **704/142** |

**Addendum 3's registered bit-identity target — `7.121542696e-06 s`, 704 lower, 142 upper — is
reproduced to every digit.** The stage-4 case and the failed M0 smoke differ by one line
(`endTime 400 → 5000`), and the trajectory confirms it: **the case is deterministic, and the graded
run IS the smoke that already failed.**

**Two disclosures rather than smoothings.** (i) At step 400 M0 has **no LTS block at all** — its
`endTime` is 400, so it writes and stops before printing one. That is **a missing datum in the
REFERENCE, not a divergence in the trajectory**, and the clamp pair at that same step matches. (ii)
The parser attributes each LTS block to the **preceding** `Time =` header, offsetting the step label
by one against a raw line-order reading. **It cannot affect the comparison, because both logs pass
through the same parser**, but the absolute label is ambiguous by one.

### A4.3 **P2 — NOT CONFIRMED. THE THRESHOLD WAS MEASURED; THE CLAIM WAS NOT VERIFIED; THE MODEL IS FALSIFIED.**

**This section was rewritten before commit. The supervisor's first draft of it read "OUTCOME
CONFIRMED" and "crossed at about step 674", and all of that was wrong** — it was written from a
lane's early spot reading, before the whole trace was parsed, and it contradicted the supervisor's
own later ruling that P2 must not be reported as confirmed. **The lane refused the label the
supervisor then instructed ("unverified") as well, on the ground that a flat "unverified" would hide
a crossing that WAS measured. It was right on both counts and the wording below is its.**

**The precise statement is neither "confirmed" nor "unverified":**
- **The threshold WAS reached and measured.** First sample below 1e-10 s is at **step 515** — not
  step 674, which was a spot reading — measured across all 758 samples.
- **The CLAIM was not verified.** P2 asserts a state **at step 5000**. The run stopped at 759 by
  supervisor decision, so **that state was never observed and cannot be inferred.**
- **The MODEL is falsified.** Addendum 3 registered ~1.1 decades per 400 steps, log-linear. Measured
  envelope: 7.994347e-06 (400) → 5.683405e-09 (500) → 7.966286e-14 (550) → 1.847168e-17 (600) →
  1.491850e-21 (650) → 2.666741e-26 (700) → **1.553171e-30 (758)** — about **24 decades over 358
  steps.** The collapse **accelerates** and is not log-linear.

**AND THE FACT THAT MAKES THE ENDPOINT UNINFERABLE, WHICH THE FIRST DRAFT OMITTED: the trace
RE-CROSSED ABOVE 1e-10 s TWICE after step 515, reaching 1.713395e-10 s.** Step-to-step rises number
**320 of 757 (42 %)**, of which 43 fall after step 515, the largest a **2.3× jump at step 617**.
**One crossing of a threshold is not a stable state below it**, so "below at 515" does not license
"below at 5000". A registered prediction about step 5000 is not discharged by a run that stopped at
759, however far it had fallen.

### A4.4 **THE MECHANISM IS NOW OBSERVED ACROSS 759 STEPS, NOT INFERRED FROM TWO LINES**

**The RAW flow time scale maximum NEVER MOVES: `0.005513522401 s` at step 1 and `0.005513522401 s` at
step 759** — supervisor-verified directly from the log's first and last `Flow time scale` lines. Raw
min falls to 2.196e-35. **Everything that collapsed was put there by `fvc::smooth`.** §A2.3 asserted
this from N1's two lines; **this run demonstrates it over 759 steps on the baseline configuration.**
The freestream time scale is healthy the entire way; the smoothing operator carries the
trailing-edge collapse into the whole domain.

### A4.5 🔴 **P3 CONFIRMED — AND THE CLAMP COUNTS FALL, WHICH INVERTS THE NAIVE READING**

Clamps fire at both ends throughout and pin **at** their own limits (`UnlimitedTmin=100`,
`UnlimitedTmax=1000`) against a registered `max_clamped_cells = 0`. **But the counts FALL as the run
proceeds — 704/142 at step 400, 128/58 by step 674** (supervisor-verified).

**Fewer cells are clamped because fewer cells are MOVING. A monitor watching clamp counts alone would
have read this collapse as a recovery.** That is the same trap as N1's residuals — where momentum
read 5.2e-08 while nothing moved — **in a different instrument**, and it is the third instance
tonight of a signal whose improvement means the opposite of health.

**And a supervisor's own instance of the same class, recorded because it nearly produced a false
contradiction of the lane:** checking whether the solver had stopped, this supervisor ran
`pgrep -f rhoPimpleFoam` and read **"STILL RUNNING"** — **`pgrep -f` matched its own command line.**
`pgrep -x` returned zero and pid 1597168 was gone. **The lane was right and the check was wrong.**

### A4.6 THE REPAIRED LAUNCHER WAS EXERCISED ON A REAL SOLVE

`log.foam_bashrc_source` present at **0 bytes** — the guarded source ran clean and its stderr is no
longer discarded. The verifier recorded `status_file: True`, `age_guard_touched: True`,
`early_rc: None`, `zero_T_mtime_before: 1788915818.5089564`, with `0/T` advancing to
1789075828.807: **the strict-increase witness fired on real data rather than on a fake solver, and
`RC=143` proves the wrapper propagates a real non-zero from a real solver process.**

**Residual labelling defect, flagged and NOT fixed mid-run:** the manifest's `launch_pid` records
**1596906, the `setsid` parent** — which had already exited — not the solver (1597168) nor the
wrapper (1596907). Verification's ruling is still satisfied because liveness is not asserted from
that parent, but **a reader running `ps` or `kill` on that number concludes the run is dead.**
Follow-up: record the solver's own pid into `STATUS.stage4` and carry it into the manifest.

### A4.7 COST — MEASURED, WITH CONTENTION NAMED AND NOT ABSORBED

**448 wall s × 1 rank = 7.467 core-min, $0.00638 DERIVED, NOT MEASURED** at $0.0513/core-h.
Actual **0.590 s/step against the M0-measured 0.325 s/step — ratio 1.82×, attributed ENTIRELY to
contention**: 12 CPU-bound ranks were already on 16 vCPU at launch and this was the 13th core. **No
waste is claimed and no per-step misprediction is claimed.** Against Addendum 3's 27.1 core-min
estimate for 5000 steps: **15.2 % of the steps for 27.6 % of the budget, and ~19.6 core-min never
spent because the run was stopped once it had answered.** The rule-12 calibration row for
`docs/COST_CALIBRATION.md` is **owed and not discharged by this addendum.**

### A4.8 WHAT THIS RUN DOES **NOT** ESTABLISH

**It does not establish the cusp as the CAUSE.** §A2.8's limit stands unchanged: this shows the
failure is deterministic, spatially confined and driven through `fvc::smooth`, and that no BC,
patch-type or mesh-quality-flag explanation survives. **Distinguishing "mesh topology defect" from
"genuinely unstable scheme" still requires the controlled experiment — the same numerics on a
wake-cut or blunt-TE grid — which is a SUCCESSOR REGISTRATION, not a rung on this one.**

---

## ADDENDUM 5 — 2026-09-10 — **THE REFERENCE TRAILING EDGE IS BLUNT, THE COORDINATE WAS ON DISK ALL ALONG, AND GATE P COULD NEVER HAVE BEEN GRADED. PLUS A CORRECTION TO MY OWN AMENDMENT 2.**

**lines whose number changed above this section: 0.** No gate, threshold, cap, band or label is altered.

### A5.1 🔴 **THE ONERA M6 TRAILING EDGE IS BLUNT IN THE REFERENCE — AND THE NUMBER WAS IN A COMMITTED LAB FILE THE WHOLE TIME**

AGARD AR-138 was verified by rendering its **own title page** (rule 15, never by filename):
*AGARD Advisory Report No. 138, "EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT", May 1979*,
with the Schmitt & Charpin chapter present as Appendix B case **B1**.

**Table B1-1 ends at `x/l = 1.0000000, z/l = 0.0007052`.** The section is symmetric, so the reference
trailing edge has a **thickness of 0.141 % of local chord** — 1.14 mm at the root, 0.64 mm at the tip
— an **included angle of 14.8°**, against a stated fabrication tolerance of 0.15 mm. **At 7.6× the
tolerance it is a design feature, not scan noise**, and the conical loft makes it blunt from root to
tip.

**And `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` ends at exactly those two
numbers — supervisor-verified.** The file is committed and was on disk throughout.

**THIS RECLASSIFIES THE ENTIRE FAILURE. M6CP1's 60.9° cusp with ZERO cells across the trailing edge
is not a meshing infelicity and not an unlucky topology choice — it is an UNREGISTERED DEPARTURE
FROM THE REFERENCE GEOMETRY.** The reference says blunt; the mesh built a point. Amendments 2 and 4
established that the failure is deterministic, spatially confined to the trailing edge, and carried
through `fvc::smooth`. **A5.1 supplies what those could not: the geometry was wrong against a source
the lab already held, in a file the lab had already committed.**

**That is also the honest answer to the owner's question — *"how could the physics be correct but not
the mesh"*: the equations were solved correctly on a body that was not the ONERA M6.**

### A5.2 🔴 **GATE P COULD NEVER HAVE BEEN GRADED FROM THE LAB'S HOLDINGS**

The lab's AR-138 is a **1979 scan, Paper-Captured in 2007. The prose OCR'd; the NUMERIC TABLES DID
NOT.** Table B1-1 and the Cp tables B1-2 onward survive in the `.txt` sidecar **as captions only**.
**There is no machine-readable AGARD Cp dataset in this repository.**

**So §5's Gate P — surface Cp against AGARD AR-138 at seven span stations, band ±0.02 — had no
reference data to be graded against, from the moment it was frozen.** No compute would ever have
produced a Gate P verdict; the gate would have failed at the comparator for want of a reference.
**The pages are legible, so digitisation is ordinary work rather than a blocker** — but it is work
that must happen **before** any successor registration puts a Cp gate on its face. Referred as such;
**this addendum does not alter Gate P, which stands as frozen and ungraded.**

### A5.3 ❌ **A CORRECTION TO MY OWN AMENDMENT 2 AND ADDENDUM 3 — THE `[0.15, 0.45]` BAND IS NOT THIS REGISTRATION'S GATE BAND**

**§A2.4 says "N1's PRESSURE lift coefficient is +0.1915 — inside THIS REGISTRATION'S OWN [0.15, 0.45]
band", and §A3.4 repeats the framing. That description is wrong and it is mine.**

**§5 GATES contains no such band** — supervisor-verified by reading §5. The band exists **only** in
the stage-3 predictions files, `STAGE3_PREDICTIONS_L2.json` (registered 17:43:44Z) and
`STAGE3_PREDICTIONS_L2_N1.json` (registered 18:20:29Z), whose own text says: **"at 8 percent of the
run this is a SMOKE band, not a gate."**

**What is NOT wrong:** the band **was** registered **before** the compute it judged, so nothing was
chosen to fit an answer, and the measured `Cl_pressure = +0.1915` does sit inside it. **What IS
wrong is the status I gave it.** Calling a stage-3 smoke band "this registration's own band" dresses
a diagnostic threshold as a gate, and a later reader could have cited an in-band pressure Cl as
evidence of a passed gate on a case whose gates were never evaluated at all.

**Corrected statement, which is what the evidence supports:** *N1's pressure lift coefficient of
+0.1915 falls inside the [0.15, 0.45] **stage-3 smoke band**, registered before that rung ran. It is
a diagnostic reading, not a gate result. Gate P and Gate G were never evaluated.* The M0 baseline's
+0.05368879024 falls **below** that same smoke band.

**Independently re-derived while checking this:** integrating `400/p` over the 1,560 `wing` faces
returns **`Cl_pressure = +0.191505`**, confirming the record's `+0.1915` to six figures, with the
baseline at `+0.053689`. **And `Cd_pressure = 0.086867` against a total Cd of 1.52 — so 94 % of the
reported drag is the viscous artifact.** `coefficient.dat` carries **totals only**; the
pressure/viscous split had **no artifact on disk** until it was derived here.

### A5.4 ONE CORRECTION TO THE FAMILY SURVEY, AND IT RUNS AGAINST MY OWN EARLIER CLAIM

Block 130 and §0 of this document state that **"every `End` line under the M6 trees belongs to a
MESHER."** **That is overturned for `M6_OWN_FAMILY_runs`**, which holds `log.rhoPimpleFoam` with
`End` lines in three smoke directories. **The named solver in both that tree and M6CP1's is
`rhoPimpleFoam`.** The broader claim — **"every solved time directory in the M6 estate is a
`smoke_*`" — HOLDS across all eight trees**, and the conclusion it supported (no graded M6 flow
solution exists) is unaffected. The overstatement is corrected because it was stated absolutely.

---

## ADDENDUM 6 — 2026-09-10 — **§4.1 SHARPENED ON TWO LIMBS: ITS THERMO STACK IS REAL, AND ITS "EVERY VARIANT, ONE CAUSE" IS WRONG. THE TREE HOLDS THREE DISTINCT FAILURES.**

**lines whose number changed above this section: 0.** No gate, threshold, cap, band or label is altered.
Amendment 2's `NOT A RESULT` park stands.

### A6.1 THE CENSUS, PLANT-CONTROLLED, AND RE-RUN INDEPENDENTLY BY THE SUPERVISOR

All nine `rhoSimpleFoam` logs in `verification/runs/M6_OWN_FAMILY_runs`, read with a **template-aware**
matcher over a **wide window** from the `sigFpe::sigHandler` frame:

| mode | logs | frame | libm in stack |
|---|---|---|---|
| **thermo / libm** | **1** — `L2/solve` | `Foam::hePsiThermo<…>::calculate` ← `libm.so.6`, then `::correct()` | **yes** |
| wall function | 2 — `smoke_diag_fo`, `smoke_potentialfoam2` | `nutUSpaldingWallFunctionFvPatchScalarField::calcUTau` | yes |
| linear solver | 2 — `smoke_simplec`, `smoke_stabilized` | `GAMGSolver::scale` | no |
| no SIGFPE stack | 4 | — | — |

**Controls, both directions:** the known-positive `hePsiThermo` in `L2/solve` is SEEN, and the
discrimination check — `GAMGSolver` must NOT be reported for `L2/solve` — returns false. **A reader
that has not been shown able to say NO is not a reader.**

### A6.2 LIMB ONE — §4.1's THERMO STACK IS SUPPORTED, AND ON A SECOND BUILD

§4.1 describes a SIGFPE in the thermo update inside `hePsiThermo<…>::calculate` called from
`::correct()`. **That is real and it is in this tree**, at
`verification/runs/M6_OWN_FAMILY_runs/L2/solve/log.rhoSimpleFoam` — handler at line 136, the
`hePsiThermo::calculate` frame at 144 rooted in `/lib/x86_64-linux-gnu/libm.so.6`, `::correct()` at 148.

**And it is the SAME SIGNATURE as the DPW5 CRM abort recorded at
`cases/committee-grids/COMMITTEE_GRID_NUMERICS.md` §4 on 2026-08-01** — same thermo package
(`hePsiThermo` / `pureMixture` / `sutherland` / `hConst` / `perfectGas` / `sensibleInternalEnergy`),
same `libm` root. **The two ran on DIFFERENT OpenFOAM BUILDS — M6 on v2506 (the dafoam build), DPW5
on openfoam2606.** **Two builds showing one signature excludes a build-specific miscompilation by
construction, and is therefore a STRONGER two-case claim than one build failing twice.**

**The OpenFOAM-versus-setup question is NOT decided by this.** Two records agreeing is a coincidence
of authorship, not evidence. **A minimal reproducer that fires on both builds and then clears on a
single change is the evidence that decides it**, and it is registered under `CRM_M085` rung 0.

### A6.3 LIMB TWO — §4.1's "EVERY VARIANT REPEATS rc=136" IS WRONG, AND WRONG IN THE UNHELPFUL DIRECTION

§4.1 reads as though one cause explains the whole `rhoSimpleFoam` family here. **It does not. The tree
holds THREE distinct failure modes**, per A6.1: a thermo/libm abort, a wall-function divergence in
`calcUTau`, and a linear-solver divergence in `GAMGSolver::scale`. **Only the graded attempt carries
the thermo abort; the smokes do not.**

**The `calcUTau` failures are downstream of the cusp, not independent of it.** `nutUSpaldingWallFunction`
iterates for u_tau, and A2.4 recorded a wing-patch **y+ maximum of 1.886e10** on exactly the collapsed
trailing-edge cells — an iteration on that will not converge. **So Amendment 5's geometry
reclassification also explains two of the three modes**, which is a tighter account than §4.1's.

### A6.4 ❌ THE SUPERVISOR'S OWN ERROR, AND IT IS THE ONE I HAVE SPENT THE EVENING WARNING LANES ABOUT

A lane first reported that **NO** log carries a thermo frame. The supervisor checked, found the frame
in `L2/solve`, and **diagnosed the cause as "the census looked at the `smoke_*` directories and did
not include `L2/solve`". THAT DIAGNOSIS WAS WRONG.** The census **did** include it and listed it
explicitly. **The supervisor guessed at a cause instead of measuring one** — the exact move being
corrected in the same message.

**The real cause was two reader defects, and the distinction is load-bearing:**
1. **A 4-line window** (`grep -A4` from the handler) when a **4-rank parallel backtrace interleaves
   `[0] [1] [2]` prefixes and shreds single frames across many lines** — handler at 136, frame at 144.
2. **A regex that could never match the symbol:** `Foam::[A-Za-z_]\w*(?:::[A-Za-z_~]\w*)+` requires
   `::` immediately after the class name, but `Foam::hePsiThermo<…>::calculate` has `<` there. **It
   could not match, and it silently matched `Foam::species::thermo` from inside the TEMPLATE
   ARGUMENTS instead — returning a plausible answer rather than nothing.**

**Why the distinction matters more than the correction: if the recorded cause were "census scope",
the next reader widens the directory glob and KEEPS THE BROKEN MATCHER.** It is a template-blind
regex and a too-narrow window on interleaved parallel output, and that is what the record must say.

**The rebuilt reader carried planted controls and REFUSED ON ITS FIRST RUN** — the known-positive came
back NOT SEEN, which is how defect 2 was found. **The supervisor's independent re-run with a
template-aware matcher reproduces the corrected census exactly, including the discrimination check.**
The instrument is at `verification/runs/M6_OWN_FAMILY_runs/STACK_CENSUS/stack_census.py`.

**This is the fifth instance in one evening of a reader that could not see a thing reporting the thing
absent** — `trapFpe`'s arming banner read as an exception, `pgrep -f` matching its own command line,
bare `checkMesh` blind to the checks it gated, a `0/T` slack confirming a launch that never happened,
and now a template-blind stack matcher. **Two of the five were the supervisor's.**
