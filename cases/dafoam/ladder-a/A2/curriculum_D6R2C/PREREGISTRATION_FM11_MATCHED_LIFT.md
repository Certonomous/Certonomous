# Curriculum D6R2C — PRE-REGISTRATION for arm `FM11`: THE COMPARISON AT MATCHED LIFT

**STATUS: FROZEN AT THE COMMIT THAT CARRIES THIS FILE. Gates, thresholds, caps and labels are closed
from that sha; changes land only as dated addenda (CLAUDE.md rule 2).**
**THE L-579 DEFECT THIS DOCUMENT CARRIED IS REPAIRED.** Its draft named two instruments that DID NOT
EXIST and gave them no md5. Both are built, both carry their md5 in the section 6 table, and
`d6r2c_fm11_prefreeze.sh` hashes that table's own rows -- see section 7.

---

## 1. WHY THIS ARM EXISTS, AND WHY IT IS NOT THE ARM I WAS BRIEFED TO REGISTER

I was briefed to register `FM11` as a **confirmation**: solve the baseline shape on a fresh mesh under
`FM10`'s own registration and warm-start rule, take the ratio against `FM10`'s `J_fresh`, and read off a
disjunction — ratio ≈ 0.75 means the 24.732 % gain is real, ratio ≈ 1.0 means it was a deformed-mesh
artefact and the optimisation result is withdrawn.

**That disjunction cannot be read off that ratio, and this section says why before the run rather than
after it.** Two findings from `FM10`'s own artifacts, both measured, stand between the brief and a
decidable arm.

### 1a. `FM10` DID NOT SOLVE AT THE REGISTERED LIFT CONDITIONS, AND ITS OWN REGISTERED TRIGGER SAYS SO BY A FACTOR OF THIRTY

`FM10` ran comparison **(i)** — *same DVs including `a*`, no re-trim* — registered at
`PREREGISTRATION_AFTER_ITEM9_R2.md` §3c on the reasoning that *"the only thing that differs is the
mesh."* **The producer's own record falsifies that sentence.** From
`d6r2c_freshmesh.json`, `solve.CL`:

| condition | registered `CL` target | `FM10` achieved | miss | vs `CL_FINDING_TRIGGER = 5.0e-3` |
|---|---|---|---|---|
| `cl04` | 0.400 | 0.549286441922 | **+0.149286** | **30×** |
| `cl05` | 0.500 | 0.651565777811 | **+0.151566** | **30×** |
| `cl06` | 0.600 | 0.752397662295 | **+0.152398** | **30×** |

The trigger is registered as *reported, never gated* — **and it fired at thirty times its value at every
condition.** So `FM10`'s `J_fresh = 0.036964341844` is the weighted drag of a wing flying **0.15 `CL`
above** the condition `Jf` was measured at. `J_fresh` against `Jf` is not a mesh comparison; it is a
comparison at two different lift coefficients, and the mesh difference is confounded with a lift
difference roughly three tenths of the operating `CL`.

**Arithmetic confirming `J` is the weighted drag and nothing else:**
`0.25 × 0.033999755140 + 0.50 × 0.036401294391 + 0.25 × 0.041055023453 = 0.036964341844` — the recorded
`solve.J` to all printed digits.

### 1b. THE LIKELIEST CAUSE IS NOT THE MESH AT ALL — IT IS THAT THE SHAPE WAS APPLIED TWICE

**This is a hypothesis with strong supporting evidence, registered as a hypothesis, and `FM11` is built
to decide it.** The evidence, all from `FM10`'s artifacts and the frozen producer:

1. **The fresh mesh is built on the ALREADY-DEFORMED surface.** `d6r2c_freshmesh.py` embeds the base
   surface's CGNS coordinates, calls `geo.DVGeo.update("cgnssurf")` — applying the optimisation's FFD
   delta — and writes the result to `surfaceMesh.cgns`, which `genWingMesh.py` then extrudes. Measured
   on disk: `surfaceMesh_base.cgns` = `3050ea454c2d0304bafa2c1a80c53b76`, while `surfaceMesh.cgns` and
   `surfaceMesh_final.cgns` are the same bytes, `9297fa5c830181d0ac0e75a540701e61`. **The volume mesh
   therefore already carries the optimised geometry**, corroborated by `h1`: the FOAM wall matches that
   CGNS surface bijectively at `worst_dist = 5.010837892761856e-09`.
2. **And then the solve applies `shape*` and `twist*` to it again.** `d6r2c_freshmesh.py:phase_solve`
   reads `dv_star` and sets every `shape`, `twist` and `patchV_*` entry before `prob.run_model()`. The
   FFD control points move by the optimisation delta a second time, and the embedded wall points with
   them.
3. **The signature matches a shape re-application and not a mesh effect.** The excess is `+0.1493`,
   `+0.1516`, `+0.1524` — **uniform across all three conditions**, i.e. a near-constant incidence-like
   offset of about `1.82°` at the fresh mesh's own lift slope. Mesh discretisation does not move `CL` by
   37 % at fixed incidence; extra camber does.
4. **The magnitude is the right size.** The optimiser reduced incidence by `2.353°`, `2.554°`, `2.903°`
   between `n = 2` and `n = 88` to hold lift while `shape*` was applied — so `shape*` is worth roughly
   `+0.19` to `+0.24` `CL` at fixed incidence. Re-applying it gave `+0.15`. **Same sign, same order, and
   the residual gap is what a nonlinear second application should leave.**

**If this is right, `J_fresh` is the drag of a wing that does not exist** — the optimised shape deformed
by the optimisation a second time — and it is not evidence about the 24.732 % in either direction.

### 1c. WHAT FOLLOWS FOR THE BRIEFED DESIGN

A baseline arm run *like-for-like* — `a*_base` held, no re-trim — inherits **both** defects. It would
fly at its own unintended lift, and on a mesh built from the base surface it would **not** be
double-deformed, so the two arms would differ in a way the ratio cannot separate. The ratio would then
be read against a disjunction whose branches assume matched lift and a common representation. **It would
produce a number, and the number would not mean what either branch says.**

---

## 2. THE ONE CHANGE, AND THE ARM

**Every solve in `FM11` is at ZERO shape and ZERO twist, on a mesh generated for that shape, TRIMMED to
the registered `CL` targets.** A mesh extruded around a given surface already *is* that geometry; the
correct design vector on it is zero, and lift is matched by trim rather than assumed.

**The change lives in exactly one place** — `d6r2c_fm11_states.py:dv_for_fm11` — and
`d6r2c_freshmesh.py --phase solve`, the function whose lines 423-425 re-apply `shape` and `twist`, **is
never called by this arm.** The launcher's own selftest asserts that the string `--phase solve` does not
appear in the emitted container block, and the pre-freeze check asserts it again on the emitted bytes.

### 2a. THE TWO SUB-ARMS AND THE FOUR STATES

| sub-arm | mesh extruded around | state | `shape`, `twist` | incidence | produces |
|---|---|---|---|---|---|
| **`Zb`** | `surfaceMesh_base.cgns` (`3050ea45…`) | **`Zb`** | **0** | **TRIMMED** to 0.4 / 0.5 / 0.6 | `J_base_fresh` |
| **`Zo`** | the FFD-updated surface (`9297fa5c…`) | **`Zo`** | **0** | **TRIMMED** to 0.4 / 0.5 / 0.6 | `J_opt_fresh` |
| **`Zo`** | the same mesh | **`Ez`** | **0** | `a*_opt`, **not trimmed** | `D1`'s measurement |
| **`Zo`** | the same mesh | **`Do`** | **`shape*`, `twist*`** | `a*_opt`, **not trimmed** | reproduces `FM10` |

`Zo`, `Ez` and `Do` share **one mesh and one process**, so nothing between them can differ except the
design vector. `Zb` and `Zo` are `d6r2c_dec5_decomp.py`'s **state `B`** — zero shape, zero twist,
re-trimmed — run on two independently generated meshes. **The trim machinery is not new and is not being
invented here:** `DEC7` trimmed six states with zero primal failures, worst lift miss `4.54e-08`, through
`optFuncs.findFeasibleDesign` with the registered incidence governor and continuation, and this arm
imports that file rather than re-spelling it.

**`Ez` IS WHY `D1` IS A GATE AND NOT A NOTE.** The draft of this document registered `D1` against a state
it did not run. `Ez` is that state: zero shape, zero twist, at the optimiser's own incidence, on the
optimised mesh. One extra objective evaluation, costed in section 5.

---

## 3. THE GATES, FROZEN

### `G1` — THE RATIO AT MATCHED LIFT, WHICH IS THE ONLY GATE THAT ADDRESSES THE HEADLINE

**`R_fresh = J_opt_fresh / J_base_fresh`**, both from trimmed solves on their own fresh meshes, and both
**recomputed by the grader from the per-condition `CD` and the frozen weights — never from a producer's
own `J`.**

**Compared against a quantity this run does not produce:**
`R_def = Jf / J0 = 0.0230632595286777639 / 0.0306416314389976151 = 0.752677270941`,
from the `O_mp` record — and `1 − R_def = 24.7323 %` reproduces the registered headline exactly.

**`RATIO_BAND` IS DERIVED IN THE GRADING INVOCATION AND THE DERIVED VALUE IS THE ONE USED.** It is the
already-registered `FM_BAND_ABS` propagated through the ratio, and no new tolerance is introduced:

```
FM_BAND_ABS            = 0.01 x J0                                      = 3.064163144e-04
relative on J_opt      = FM_BAND_ABS / Jf                               = 0.01328591
relative on J_base     = FM_BAND_ABS / J0                               = 0.01000000
combined in quadrature = sqrt(0.01328591^2 + 0.01000000^2)              = 0.01662875
RATIO_BAND             = R_def x 0.01662875                             = 0.012516082
PASS window on R_fresh = [0.740161, 0.765193]  <=>  gain in [23.481 %, 25.984 %]
```

**MEASURED AT THE FREEZE, from the grader's own `--selftest` run through `main()`:** the emitted window is
`[0.740161, 0.765193]`, which is the line above to six decimals.

**It is a DECLARED decision-relevance band inherited from `FM_BAND_ABS`, NOT a measured discretisation
uncertainty and NOT a GCI.** The grader writes that sentence into every record it produces.

**THE DISJUNCTION, REGISTERED BEFORE THE RUN, BOTH BRANCHES STATED:**
- **`R_fresh` inside the window** → the gain survives independent mesh generation at matched lift.
  **`PASS`**, and the 24.732 % stands as quoted.
- **`R_fresh ≥ 1.0`** → the optimised shape is not better on independently generated meshes.
  **`GATE FAIL`, and the 24.732 % is withdrawn.**
- **Anything between** → **`GATE FAIL`**, reported as a partial gain with both numbers, and the headline
  may then be quoted only with the fresh-mesh figure beside it.

**I do not predict which branch fires and nothing in this document is arranged so that one of them is
easier to reach.**

### `G2` — THE TRIM ACTUALLY REACHED THE REGISTERED CONDITIONS

**`|CL_p − target_p| ≤ TRIM_TOL` at every condition of `Zb` and `Zo`.** **`TRIM_TOL` IS DERIVED IN THE
GRADING INVOCATION** as `CL_FINDING_TRIGGER / 5.0 = 1.0e-3`: `PREREGISTRATION_AFTER_ITEM9_R2.md` §3c
fixes `CL_FINDING_TRIGGER = 5.0e-3` as *"five times the `G3` tolerance"*. A ratio of drags is only a
comparison if both sides sit at the same lift, and this clause is what makes `G1` mean anything.

**A trim that does not converge is a MISSING MEASUREMENT.** `G2` also requires the producer's own
`trimmed` flag to be true, so a state that skipped the trim cannot pass by happening to land close.
**`primalMinResTol = 1.0e-8` is never loosened to make a trim close.**

### `D1` — THE DOUBLE-DEFORMATION DIAGNOSTIC, AND IT IS A REAL GATE WITH A STATE BEHIND IT

**The external anchor, a quantity this run does not produce** — `FM10`'s measured excess
`E_star = (+0.149286, +0.151566, +0.152398)`, read out of `FM10`'s own record, never re-typed.

```
E_zero(p) = CL_p(state Ez)  -  target_p
GATE: mean_p |E_zero(p)| / mean_p |E_star(p)| < DOUBLE_SPLIT = 0.50
```

- **Below 0.50** → the excess follows the shape design variables and not the mesh. **The double
  application is confirmed, `FM10`'s `J_fresh` is withdrawn as a measurement of anything**, and a
  defect note is drafted against `d6r2c_freshmesh.py` — **`NOT FILED`**, submissions parked (rule 7).
- **At or above 0.50** → §1b's hypothesis is **wrong**, the excess is a property of the fresh mesh, and
  that is a larger finding about the mesh than about the producer.

**`DOUBLE_SPLIT = 0.50` IS A DECLARED SPLIT OF A MEASURED INTERVAL, NOT A MEASUREMENT.** The interval
runs from zero to `E_star`; one half is the midpoint and I am not dressing it up as derived. The raw
ratio is printed whatever it is. **The anchor is not degenerate:** `min |E_star| = 0.149286`, so this is
not a sanity check at a state where the quantity under test is identically zero.

### `D2` — `Do` REPRODUCES `FM10`

`Do` must reproduce `J = 0.036964341844` to within `FM_BAND_ABS` and `CL = (0.549286, 0.651566,
0.752398)` to within `TRIM_TOL`. **This is the planted-control-in-the-large:** if the same inputs on the
same mesh do not return the same numbers, nothing else in this arm is evidence. **Failure here is
`NOT A RESULT` for the whole arm**, not for `Do` alone.

### `W1` — G-WALL: THE SOLVE-PHASE DV SET MOVED NO WALL POINT

**This is the guard that belongs with the one change, and it is the clause that would have caught
`FM10`.** After every state, the global point cloud the solver actually held is rebuilt from its own
`processor*/<latest time>/polyMesh/points` through `constant/polyMesh/pointProcAddressing`, restricted to
the `wing` patch, and compared against the generated mesh's own wall.

```
WALL_MOVE_ROUNDOFF = n_cgns_nodes(1031) x eps(2.220446e-16) x 1 m = 2.289e-13 m
WALL_MOVE_TOL      = 4 x WALL_MOVE_ROUNDOFF                       = 9.157120e-13 m
```

**DERIVED IN THE PRODUCER'S OWN INVOCATION and the derived value is the one used.** It is a ROUND-OFF
ALLOWANCE, not a physical band: the wing's coordinates are `O(1) m` and a warp of a wall point is a
weighted sum over the CGNS surface's 1031 nodes, so that is the worst a **zero** delta can leave.

- **GATED on `Zb`, `Zo` and `Ez`** — all three set the shape DVs to zero, so all three must move nothing.
- **REPORTED on `Do`** — `Do` applies `shape*` and `twist*`, so a **large** displacement there is the
  contrast that shows the guard is not simply blind.
- **The grader RE-MEASURES it from disk**, so a producer that mis-measured its own guard cannot carry
  the arm.
- **Driven to its failing side from OUTSIDE the producer** before the freeze — see §7.

### `M0` — THE GENERATED MESH AGAINST THE BASE MESH, MEASURED ON POINTS

Measured as the largest displacement between the generated cloud and the base mesh's, **not** as a
`points.gz` md5: gzip embeds an mtime, so a hash comparison answers *"were these files written
identically"*, which is an adjacent quantity to *"are these the same mesh"* (L-595).

- **`Zo`: GATED.** The mesh is extruded around the FFD-updated surface and **must** differ from the base
  mesh. Zero difference means the deformation never reached the mesher and `J_opt_fresh` would be the
  base geometry's drag under another name — the producer **REFUSES**.
- **`Zb`: REPORTED.** `Zb` regenerates the base geometry with the same family script at the same
  parameters, so reproducing the base mesh is the **expectation**; a large difference is a **finding**
  about the mesher's reproducibility, reported as one, and it is not a failure of this arm.

**An inherited guard is NOT weakened to make this arm pass.** `d6r2c_fm9_stage.py` carries
`REFUSE_FRESH_IS_BASE`, which fires when the generated `points.gz` md5 equals the base mesh's. On `Zb`
that is a clause this arm does not want, and **if it fires, `FM11` is `BLOCKED` and reported as such** —
this lane does not edit a frozen guard, and does not hand it a substituted hash, to get past it.

### `M1` — THE MESH THE RUNNING SOLVER LOADED (charter rule 17)

**The hash of the polyMesh the running solver loaded, rebuilt from `pointProcAddressing`, compared for
EXACT equality against the generated mesh** — `max |Δ| == 0.0` on all three conditions of both sub-arms,
with `n_processors == 4` on each.

**A tolerance here would let a mesh that is nearly the generated one pass as the generated one, and the
question `M1` answers admits no nearly.** `H2`-style checks — the mesh exists, it came from the pinned
script, it differs from the base — were **all three true in `FM5`, `FM7` and `FM8` while the solver read
something else.**

**The fresh mesh is staged into every condition case BEFORE the model is built.** In `FM11` the staging
is the first thing `d6r2c_fm11_states.py:run()` does, ahead of `load_frozen_model`, and the producer
**REFUSES** if any `processor*` directory survives the staging — so the ordering guarantee is a line of
code inside the process that builds the model, not an assumption about what a previous process did.

### `Q1` — checkMesh ON THE MESH THAT RAN (charter rule 31) — REPORTED, NAMED, NEVER SILENT

After the final DV application of **every** state, the producer exports a serial case whose
`constant/polyMesh` **is** the as-run cloud (topology from the generated mesh, which a warp does not
touch; points from the reconstruction) and runs `checkMesh` on it. The grader reads the max
non-orthogonality out of that log and compares it against **DAFoam's own declared `maxNonOrth`, PARSED
from the md5-asserted `d6r2c_opt_runScript.py`'s `checkMeshThreshold` block — 70.0 — never typed into the
grader.**

**MEASURED ELSEWHERE, AND THIS IS WHY THE CLAUSE EXISTS:** the optimisation mesh as-run **71.24** and
`FM10` as-run **79.21** BOTH BREACH the declared 70.0, against an as-built 66.32 — **and neither was ever
checked.**

**A breach does not flip this arm's label.** Its question is the drag ratio and no mesh-quality threshold
was pre-registered as its gate, and inventing one after the measurement exists is exactly what §2b
forbids. **It is written into the record, into the printed verdict line and into `findings`, and the
headline may not be quoted without it.**

### `H4` — COMPLETION, HYGIENE, AND A CONVERGENCE CHANNEL THAT HAS A WRITER

`rc = 0`; a `FOOTER` in both sub-arms; `uid 1000`; zero files under the arm newer than the age datum
owned by uid 0 or gid 0; both records newer than the datum; and the **convergence limb**.

**THE CHANNEL WITH NO WRITER IS DELETED (charter §22.4 clause 3).** `primal_residual.json` had **four
readers, zero writers and zero such files anywhere on disk**, and the default `conv[p] = True` stood for
every condition of every arm. **`d6r2c_fm11_states.py` neither writes nor reads it, and no clause of
`FM11` defaults to converged.**

**What replaces it is a channel whose writer is the solver itself.** The limb parses the arm log for
every primal block — the run of lines up to an `End` that printed at least two `CD:` lines — and requires
every block to be settled:

```
CD_SETTLE_REL = (FM_BAND_ABS / J0) / SETTLE_MARGIN = 0.01 / 1000 = 1.0e-5
```

**DERIVED in the grading invocation; `SETTLE_MARGIN = 1000` is DECLARED, not measured.** **Measured at
the freeze by running this very limb over `FM10`'s own log, a run this arm did not produce:** 6 primal
blocks, **worst last-step relative `CD` change 9.588e-08**, all settled — two orders inside the criterion.
(An earlier draft of this section quoted `1.4e-08`, which is the LAST block's change, not the worst of
the six. The worst is the number the gate reads and it is the number stated here.)

**An absent or primal-free log REFUSES (exit 2).** An absent source is **not** zero failures — that is
the shape of the defect §22.4 clause 3 names, and rule 3 forbids it.

**WHAT THIS CLAUSE DOES NOT MEASURE, STATED PLAINLY.** DAFoam's `primalMinResTol = 1.0e-8` applies to its
own normalised residual ratio, which the log prints only twice per condition. **`FM11` does not measure
whether that tolerance was met, and does not claim it was.** Gating the solver's per-equation `initRes`
against `primalMinResTol` would be a gate on an adjacent quantity (L-595), and this arm will not do it.

---

## 4. WHAT THIS ARM DOES NOT CLAIM

- It does **not** claim the 24.732 % is wrong. §1b is a hypothesis about `FM10`'s producer, and `D1`
  exists to decide it. **`FM10`'s `NOT A RESULT` stands and is not re-graded into anything else.**
- It does **not** claim the fresh mesh is better than the deformed mesh, or that either is correct.
- It does **not** measure discretisation error. `RATIO_BAND` is a declared decision band; **no GCI is
  computed and none may be quoted**, and a Roache triple would need three grid levels this arm does not
  run (rule 5).
- It does **not** settle whether the optimised shape is better at the off-design lift `FM10` flew at.
- It does **not** license quoting any fresh-mesh number against `J0` or `Jf` across meshes. `G1` compares
  fresh against fresh; **the cross-mesh ratio `0.036964 / 0.030642 = 1.2063` mixes a fresh-mesh numerator
  with a deformed-mesh denominator and is registered here as a quantity that must not be quoted.**
- It does **not** measure whether `primalMinResTol` was met — see `H4`.

---

## 5. COST (rule 12, and charter §22.5: per objective and per gradient evaluation SEPARATELY)

**Every figure below is RE-DERIVED from a named artefact. None is copied from this document's draft, and
the draft's 270.422 / 811.267 are SUPERSEDED — they assumed 18 trim evaluations for all three states,
which is `DEC7`'s shape-ON state `S`, where two of `FM11`'s three trimmed states are state `B` analogues.**

| quantity | value | anchor, and it is a run this arm did not produce |
|---|---|---|
| **per objective evaluation** (3 conditions, cold) | **5.447 core-min** | `DEC7` `d6r2c_dec5.jsonl` STATE `O`: 81.7 s wall at 4 ranks, `n_trim = 1` |
| **per gradient evaluation** | **11.863 core-min** | `O_mp` `d6r2c_evals.jsonl`: median of **26** `G` records, 177.944 s at 4 ranks |
| **gradient evaluations in this arm** | **0** | registered so the zero is BY DESIGN and visible, not by omission |
| `Zb` trim | 574.5 s | `DEC7` STATE `B` — zero shape, zero twist, trimmed. `Zb` is its exact analogue |
| `Zo` trim | 2400.3 s | `DEC7` STATE `S` — the deformed geometry, trimmed. The CONSERVATIVE analogue for `Zo` |
| mesh + deform + stage, per sub-arm | 88.2 s | `FM10` arm wall 160 s minus its solve 71.847 s |
| model load, per solve process | 14.1 s | `DEC7` FOOTER 5918.862 s minus the sum of its six state walls |

```
2 x 88.2  (mesh/deform/stage, both sub-arms)   =  176.4 s
2 x 14.1  (model load, both solve processes)   =   28.2 s
          Zb trim                              =  574.5 s
          Zo trim                              = 2400.3 s
2 x 81.7  (Ez and Do, one evaluation each)     =  163.4 s
TOTAL PREDICTION   3342.8 s x 4 ranks / 60     =  222.853 core-min
REGISTERED CAP     3.00 x 222.853              =  668.559 core-min
```

**The cap is 3.00× the REGISTERED prediction, and it has ONE SOURCE:** `d6r2c_fm11_grade.py` derives it
and `d6r2c_fm11_run_arm.sh` asks the grader for it (`--print-cap`). The launcher carries no cap literal,
and its selftest asserts that. `FM12` and `FM13` are the registered re-run ids and carry the **identical**
figure under another key.

**Derived dollars at the owner-stated `$0.0513/core-h`: prediction $0.1905, at the cap $0.5716 —
DERIVED, NOT MEASURED**; `cost_basis` is **reported-by-owner**, because the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**THE STANDING CONFLICT, RESOLVED HERE AND NOT LEFT OPEN.** The draft recorded a conflict between "an
overrun stops the run" and Sanaa's 2026-09-12 NO-CAP ruling. **Her ruling is the later and it governs:
nothing is stopped by the cap.** The launcher starts a container and waits; it kills nothing. A crossing
is **REPORTED** in the ledger, the row is graded **`NOT A RESULT`** by `H4`, and **the cap is never
raised.**

**`FM10`'s calibration row, owed under rule 12:** predicted **11.400** core-min, actual **10.677**,
**ratio 0.937** — misprediction in the conservative direction, no contention and no waste. **The row is
still OWED to `docs/COST_CALIBRATION.md` and this document does not land it.**

---

## 6. THE INSTRUMENTS

**Every row below names a file that EXISTS at the md5 stated, and `d6r2c_fm11_prefreeze.sh` hashes this
table's own rows to prove it (charter §22.4 clause 1, L-579). A row with no md5 is a FAILURE of that
check, not a blank to be filled later.**

| instrument | role | md5 |
|---|---|---|
| `d6r2c_fm11_states.py` | **NEW** — the producer. The `Zb`/`Zo`/`Ez`/`Do` state table, the ONE CHANGE, `G-WALL`, `M0`, the staging, the as-run export and `checkMesh` | `0cb143738c124b55067a7b19bc1a0c43` |
| `d6r2c_fm11_grade.py` | **NEW** — the grader. `G1`, `G2`, `D1`, `D2`, `M0`, `M1`, `W1`, `Q1`, `H4`, the planted control and the cap | `ddceb552b4b4dcf749000d2b784f06d8` |
| `d6r2c_fm11_run_arm.sh` | **NEW** — the launcher. A fork of `d6r2c_fm9_run_arm.sh`; the guard bodies are that file's bytes | `b6972fc3dca1f45ed487519f8119ce60` |
| `d6r2c_fm11_prefreeze.sh` | **NEW** — the §22.4 check, driven before this document was frozen | `2d07cd563484bacaf3dc5d5332d9181d` |
| `d6r2c_freshmesh.py` | **REUSED UNCHANGED, AND IT IS THE SUSPECT** — `--phase deform` and `--phase mesh` only. **Its `phase_solve` is NEVER CALLED by `FM11`** | `1d15ce361673ca600d565280441b67e0` |
| `d6r2c_fm9_stage.py` | **REUSED UNCHANGED** — the OpenFOAM readers, `reconstruct_loaded_points`, `stage_mesh` | `ea6d180fda38a3980bbb275b86d192c1` |
| `d6r2c_dec5_decomp.py` | **REUSED UNCHANGED** — the trim, the incidence governor, the continuation, the frozen-model loader | `fb19791784ebb73747c2f6c466a0d174` |
| `d6r2c_decomp.py` | **REUSED UNCHANGED** — imported by `d6r2c_freshmesh.py` | `42ec0dd582584812a69129a474b2783e` |
| `d6r2c_opt_runScript.py` | **THE FROZEN MODEL** — loaded from its own bytes up to the task dispatch; `Q1`'s declared limit is parsed out of it | `2f2ae43a627146cf8e0f065b035ada4b` |

**THE PLANTED CONTROL (rule 3).** The grader plants `PLANT = 1.234e-03` into six channels it **reads back
from disk** — the per-condition `CD` of each sub-arm, the `M1` reconstruction, the `W1` wall cloud, `D1`'s
excess and `D2`'s `J` — re-grades, and **REFUSES** unless every plant moves a graded quantity. The plant
never goes into a registered copy, which is a reader compared against itself. **And the control itself is
driven to its failing side:** the selftest substitutes a grader that ignores the plant and requires
`REFUSE_PLANT_UNSEEN`.

**WHAT EACH CLAUSE CAN AND CANNOT SEE (L-588).** `G1`, `G2`, `D1` and `D2` are computed from the same
producer records and share their failure modes; they are **not** four independent checks. The genuinely
external anchors are exactly four: **`R_def` from `O_mp`**, **`E_star` and `J` from `FM10`**, **the trim
and evaluation walls from `DEC7`**, and **`maxNonOrth` from the frozen runScript**. `M1` is the only
clause that can see a mesh the solver did not load; `W1` the only one that can see a DV set that moved
the wall; `D2` the only one that can see a producer that does not reproduce itself. **No clause in this
document can see an FFD that is wrong in the same way on both meshes**, and `D1` is the closest thing to
a check on that — which is why it is a gate with a state behind it.

---

## 7. THE PRE-FREEZE CHECKLIST (DAFOAM_CHARTER.md §22.4) — DRIVEN, WITH ITS RESULTS

`bash d6r2c_fm11_prefreeze.sh` was run before the freeze commit. **Its three clauses, each stated
individually, with what was measured:**

### 7a. CLAUSE 1 — EVERY INSTRUMENT NAMED IN THE FROZEN TABLE EXISTS AT ITS STATED md5

**RESULT: PASS.** All **nine** rows of §6 were parsed out of this document, the named file hashed on
disk, and the hash compared against the row's own md5. **Nine of nine agree.** The check carries no list
of its own — it reads §6 — so a row added here is a row it hashes, and **a row with no md5, or naming a
file that is absent, is a FAILURE of this clause, never a skip.**

**This clause failed once during the check and that is worth recording:** on its first complete run it
reported `d6r2c_fm11_prefreeze.sh md5 on disk 2d07cd56…, table says bf6597fa…` — the check caught the
drift of its own bytes against the table. The table was corrected to the file; the file was not
re-described to the table.

**The L-579 defect is gone.** The draft of this document named `d6r2c_fm11_states.py` and
`d6r2c_fm11_grade.py` as `NOT BUILT` with `—` in the md5 column. Both exist, both are hashed, and the
row parser was shown able to resolve a file name out of a synthetic row naming a file that does not
exist.

### 7b. CLAUSE 2 — THE CHECK DRIVES THE CLI THE LAUNCHER EMITS, NOT THE GRADED FUNCTION

**RESULT: PASS.** The launcher was **asked** for its grading command (`--emit-grade-cmd`) and the string
it returned was **executed** against a synthetic arm:

```
python3 .../d6r2c_fm11_grade.py --item FM11 --arm-dir <arm> --datum-file <arm>/.d6r2c_age_datum \
        --core-min 10.000 --rc 0 --log <log> --out <verdict.json>
```

- it **ran and returned 0**;
- it produced **`label=PASS`** on a tree built to pass — *not* `NOT A RESULT` by construction, which is
  the only thing the FM9 grader's frozen command line could ever have returned (L-595, L-570);
- it **wrote the verdict file the launcher names**;
- **and the same command REFUSED when a sub-arm was deleted** — so the green above is not vacuous.

`grade_cmd()` is the single source of that string: the end-of-run banner and `--emit-grade-cmd` both call
it, so the command that was checked and the command that will run cannot drift.

**The producer's own argument vectors were lifted out of the EXACT container block** (`--emit-cmd`) and
driven through its argparse and input validation (`--parse-only`) for both sub-arms — **both accepted** —
and an unregistered sub-arm was **rejected**, so that check is not vacuous either.

**And on the emitted bytes: `d6r2c_freshmesh.py --phase solve` — the function whose lines 423-425 apply
the shape a second time — DOES NOT APPEAR IN THE BLOCK THIS ARM RUNS.**

### 7c. CLAUSE 3 — EVERY CHANNEL A GATE READS HAS A WRITER THAT RAN

**RESULT: PASS, by deleting the channel that had none and gating on one that has a writer.**

- **`primal_residual.json`: ZERO read sites in the three FM11 instruments.** The sweep looks for the
  *shape of a read* — the name on a line that also opens, joins or stats a path — not for the word, and
  it was **driven to its failing side**: the same sweep finds **2 real read sites** in the inherited
  `d6r2c_freshmesh.py`. The FM11 files **mention** the channel 5 times, all of them explaining the
  deletion, and **read** it 0 times; the sweep separates the two.
- **`d6r2c_fm11_states.py` writes no such file and no clause of FM11 defaults to converged.** The
  producer's own selftest asserts both on its executable body, with the comment lines excluded (its
  header quotes both needles) and with the sweep driven to its failing side.
- **The channel `H4` does read has a writer that ran:** `FM10`'s own arm log carries **66 `CD:` lines**,
  written by the solver itself. Running `H4`'s limb over that real log gives **6 primal blocks, worst
  last-step relative `CD` change 9.588e-08, all settled.**
- **An absent writer REFUSES.** `grade_log()` on a nonexistent log raises `REFUSE_NO_ARM_LOG`, and on a
  log with no primal block `REFUSE_NO_PRIMAL_BLOCKS`. **An absent source is not zero failures.**

### 7d. THE THREE STANDING REQUIREMENTS, ALSO DRIVEN

- **Every gate has a failing control driven from OUTSIDE the instrument.** `G-WALL` was driven from the
  check, not from the producer's selftest: it passes an unmoved wall, **sees the planted `1.234e-03` at
  the exact point it was planted on**, and fails just above its own derived tolerance. The grader's
  planted control was run from outside too: **the plant is SEEN in all six channels**, and a substituted
  grader that ignores the plant raises `REFUSE_PLANT_UNSEEN`.
- **Every verification constant is DERIVED in the same invocation and the DERIVED value is USED.** Each
  was recomputed from its stated basis and compared against what the instrument serves:
  `FM_BAND_ABS = 3.0641631439e-04`, `R_def = 0.752677270941`, `RATIO_BAND = 0.0125160819516`,
  `TRIM_TOL = 1.0e-3`, `CD_SETTLE_REL = 1.0e-5`, `MAX_NONORTH = 70.0` (parsed from the frozen runScript),
  `WALL_MOVE_TOL = 9.157120e-13`. **Seven of seven agree to machine precision.**
- **No sanity anchor sits where the quantity under test is identically zero.** `D1`'s anchor is `FM10`'s
  measured excess, `min |E_star| = 0.149286`; `D2`'s is `FM10`'s measured `J = 0.036964341844`; `G1`'s is
  `R_def = 0.752677271`. **All three non-degenerate.**

### 7e. THE INSTRUMENTS' OWN SELFTESTS, FOR COMPLETENESS AND NOT IN PLACE OF THE ABOVE

`d6r2c_fm11_states.py --selftest` **PASS, n = 51**; `d6r2c_fm11_grade.py --selftest` **PASS, n = 43**;
`d6r2c_fm11_run_arm.sh --selftest` **PASS**. **These prove the functions. §7b is what proves the frozen
command line, and it is the one the charter added.**

---

## 8. THE LAUNCH

```
bash /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_fm11_run_arm.sh \
     FM11 sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
```

- **4 ranks**, on a cpuset **chosen at launch from cores no container holds and no busy sample shows
  working** — never hardcoded. `G-CPUSET` refuses to start on any intersection and **stops nothing**.
- The container is the registered digest, `--user 1000:1000`, `/mnt/parent` mounted **read-only**.
- On success the launcher prints, as its second-to-last line:

```
D6R2C_FM11_LAUNCHED name=d6r2c_fm11_FM11_<UTC>_<pid> arm=FM11 uid=1000:1000+1002 ranks=4 cpuset=<chosen>
```

- **Nothing is stopped by the cap** (Sanaa directive #17). A crossing is reported and graded
  `NOT A RESULT`.
- **SUBMISSIONS PARKED (rule 7).** Nothing in this arm sends, files, uploads or posts anything.

---

## ADDENDUM 1 — 2026-09-13 — THE LAUNCH, AND A DEFECT IN §8's OWN LAUNCH LINE

**Appended after the freeze. It alters no gate, no threshold, no cap and no label, and it inserts and
edits nothing above itself.**

| assertion | value |
|---|---|
| lines whose number changed above this section | **0 — proved on BYTES by `cmp -n 33302` against the frozen blob at `6190e070c6f53fe07f058dfcfa610ba7fb246596`, exit 0** |
| gates, thresholds, caps or labels altered | **none** |

### A1.1 THE DEFECT — §8's LAUNCH LINE IS NOT A RUNNABLE IMAGE REFERENCE

§8 spells the image as `sha256:2927768a…` with **no repository**. `G-IMG` accepts it, because it matches
the registered digest as a substring — but `docker run` cannot resolve a bare digest, so **the line as
written in the frozen document would not have started a container.** The runnable form, and the one the
lineage's own `FM9_wrapper.sh` used, is:

```
dafoam-idwarp-rot@sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
```

**THE ARM WAS LAUNCHED WITH THAT FORM.** This is recorded as a defect in the frozen text rather than
corrected in place (rule 6). It is the same class as `G-IMG` itself: a guard that matches a substring
proves the digest is *mentioned*, not that the reference *resolves*.

### A1.2 THE LAUNCH, AS IT HAPPENED

| fact | value |
|---|---|
| freeze sha | `6190e070c6f53fe07f058dfcfa610ba7fb246596` |
| wrapper | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM11-a2-wing-matched-lift/FM11_wrapper.sh`, detached with `setsid`, **no timeout and no kill** (directive #17) |
| wrapper pid | **1594844** |
| container | `d6r2c_fm11_FM11_20260913T173321Z_1594848` |
| ranks / cpuset | **4 ranks on cores 4,5,6,7**, chosen at launch |
| cores the guard found already busy | **48 of 96**, none of them 4-7 |
| cap printed at launch | **668.559 core-min**, from `d6r2c_fm11_grade.py --print-cap` |
| command block md5 | `204f961540b28e82ec82d864a20d1586` |
| age datum | `1789320801` |

All five launch guards passed: `G-ROOT`, `G-BOX` (load1 45.88 of 96, zero solver swap offenders,
646 GB available), `G-FREEZE`, `G-DEPS` (6 staged, 6 scanned), `G-CPUSET`.

### A1.3 FIRST MEASUREMENT OFF THE ARM — THE `Zb` MESH AS BUILT

`checkMesh` in `mesh_generation.log`: **max non-orthogonality 66.97, average 11.49, "Mesh OK."**
**Within DAFoam's declared `maxNonOrth = 70.0`.** This is the mesh **AS BUILT**; `Q1` measures the mesh
**AS RUN**, after the final DV application, and the two are different numbers — on the optimisation mesh
they were 66.32 as built and **71.24 as run**.

**SUBMISSIONS PARKED (rule 7).**

---

## ADDENDUM 2 — 2026-09-13 — **`FM11` IS `BLOCKED` AT ITS FIRST STAGING STEP, ON THE EXACT CONDITION §3's `M0` REGISTERED. AND TWO OF MY OWN CLAIMS ARE FALSIFIED BY IT.**

**Appended after the freeze. It alters no gate, no threshold, no cap and no label.**

| assertion | value |
|---|---|
| lines whose number changed above this section | **0 — proved on BYTES by `cmp -n 33302` against the frozen blob at `6190e070c6f53fe07f058dfcfa610ba7fb246596`, exit 0** |
| gates, thresholds, caps or labels altered | **none** |

### A2.1 THE VERDICT

**`BLOCKED`.** Arm `FM11`, container `d6r2c_fm11_FM11_20260913T173321Z_1594848`, **rc = 1, wall 22 s,
1.467 core-min** against a registered cap of 668.559. The Zb sub-arm's `--phase mesh` succeeded
(`checkMesh`: max non-orthogonality **66.97**, "Mesh OK.") and the producer then refused at its staging
step, before `load_frozen_model` and before one primal ran:

```
d6r2c_fm9_stage.Refusal: REFUSE_FRESH_IS_BASE the generated mesh's points.gz md5 equals
the BASE mesh's (0fb1935a9b8781b73ac4ccb136e3ec68)
```

**This is the condition §3's `M0` registered in advance, and the registered consequence is the one
taken:** the guard is inherited and frozen, it is not this arm's to weaken, it was not handed a
substituted hash, and the arm is **`BLOCKED`** rather than passed. The Zo sub-arm never started, because
the command block aborts on a non-zero rc.

### A2.2 FALSIFIED CLAIM 1 — MY OWN JUSTIFICATION FOR MEASURING `M0` ON POINTS IS WRONG

§3's `M0` says a `points.gz` md5 comparison is an adjacent quantity **"because gzip embeds an mtime, so
two byte-identical point lists written a second apart have different hashes."** **THAT SENTENCE IS
FALSE FOR THIS WRITER, AND THE RUN PROVES IT.** Measured on the arm's own output:

| quantity | value |
|---|---|
| `FM11/Zb/constant/polyMesh/points.gz` md5 | `0fb1935a9b8781b73ac4ccb136e3ec68` |
| the registered base mesh's md5 | `0fb1935a9b8781b73ac4ccb136e3ec68` — **identical** |
| gzip header MTIME field | **0** — OpenFOAM stores no timestamp |
| points, regenerated vs base | 40209 vs 40209 |
| **max point difference** | **0 m, exactly** |

**The conclusion the clause reached is still right and its stated reason was wrong.** Measuring on points
is correct because it answers the question directly; it is *not* correct because hashes are unreliable
here — **here they are exactly reliable.** A right answer with a false justification is still a false
claim (§18.6), and it is recorded as one.

**AND THE FINDING THAT COMES FREE IS A GOOD ONE:** `genWingMesh.py` plus the family's
`plot3dToFoam / autoPatch / createPatch / renumberMesh` sequence **regenerates the base mesh BYTE FOR
BYTE** from `surfaceMesh_base.cgns`, 46 days after the original was written. That is `M0`'s `Zb`
expectation confirmed at the strongest level available, and it is the first bit-exact reproducibility
measurement this family has on its mesher.

### A2.3 FALSIFIED CLAIM 2 — §7b's GREEN IS NARROWER THAN IT READS, AND THE GRADER CANNOT LOAD ITS OWN EXTERNAL ANCHOR

Running the launcher's own emitted grading command **against the real arm and the real `O_mp` record**:

```
D6R2C_FM11_GRADE REFUSED
REFUSE_NO_J_IN_RECORD keys=['cl04.aero_post.functionals.CL', 'cl05.aero_post.functionals.CL',
 'cl06.aero_post.functionals.CL', 'geometry_cl05.thickcon', 'geometry_cl05.volcon', 'obj.J']
```

**`load_inherited` cannot read the file `R_def` comes from.** Three measured reasons, and all three had
to be true at once:

1. its key probe tries `<pt>.aero_post.CD`, `<pt>_CD`, `CD_<pt>`, then `obj`, `J`, `fun`,
   `weighted_CD` — **and the real key is `obj.J`**, which is none of them;
2. `obj.J`'s value is a **one-element list**, `[0.030641631438997615]`, which `_finite()` would reject
   even if the key matched;
3. an `F` record carries **no per-condition `CD` at all**, so the preferred "recompute from the
   per-condition CD" path can never fire on this file and the fallback is the only path there is.

**The anchor itself is intact and recoverable** — `obj.J` at `n = 2` and `n = 88` give
`J0 = 0.030641631438997615` and `Jf = 0.023063259528677764`, reproducing
**`R_def = 0.752677270941`** to twelve places, exactly the registered figure. **Nothing about the
physics is in doubt; the reader is.**

**WHY §7b's CHECK DID NOT CATCH IT, STATED AGAINST MY OWN WORK.** Clause (b) ran the emitted command with
`--evals SYNTHETIC --fm10-record SYNTHETIC`, because the synthetic arm has no real anchors beside it.
**So the check drove the command line and NOT THE DATA THE COMMAND LINE READS.** That is the same shape
as the defect §22.4 clause 2 exists to prevent, one layer down: FM9's selftest exercised the function and
not the entry point; mine exercised the entry point and not the external anchors. **§7b's "PASS" is true
as written and narrower than it reads, and the honest statement is that it did not cover the anchor
loaders.**

**The repair belongs to a re-registered arm.** First compute has happened (1.467 core-min), so `FM11`'s
gates are closed and this addendum alters none of them. `FM12` is the registered re-run id, carrying the
**identical** cap of 668.559 under another key. **What `FM12` must carry is a supervisor's call, not this
lane's**, and it is named here so it cannot be lost:

- an `M0`-shaped clause for `Zb` that does not route through `REFUSE_FRESH_IS_BASE`, without weakening
  that guard for `Zo`, where it is exactly right;
- `load_inherited` reading `obj.J` and unwrapping a one-element list, with **the real file in the
  control**, not a synthetic stand-in;
- a pre-freeze clause (b) that drives the emitted command **against the real external anchors**.

### A2.4 COST CALIBRATION (rule 12, charter §22.5)

| quantity | value |
|---|---|
| predicted | **222.853 core-min** |
| **actual** | **1.467 core-min** (ledger row, 22 s wall x 4 ranks / 60) |
| ratio actual/predicted | **0.0066** |
| attribution | **NOT misprediction, and not contention or waste.** The arm was `BLOCKED` by a registered refusal 22 s in, before the model was built and before one primal ran. The prediction was never exercised; it is neither confirmed nor falsified by this row. |
| dollars | **$0.00125 DERIVED** at the owner-stated $0.0513/core-h — **derived, never measured**; the box cannot read its own billing |

**This row is OWED to `docs/COST_CALIBRATION.md` and this document does not land it**, exactly as
`FM10`'s row (predicted 11.400, actual 10.677, ratio 0.937) is still owed.

**SUBMISSIONS PARKED (rule 7).**
