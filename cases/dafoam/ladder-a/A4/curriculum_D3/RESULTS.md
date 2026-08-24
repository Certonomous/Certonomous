# Curriculum item D3 — A4 Ahmed body, CONSTRAINED drag minimisation: RESULTS

**Item verdict: `BLOCKED`.** Stage G — the registered geometry probe that buys no flow solve —
crashed inside `prob.setup()` at the first `DVConstraints` call. `PREREGISTRATION.md` §16 fixes this
mapping in advance: *"a Stage-G crash makes the item `BLOCKED` — a precondition prevented the
measurement — not `NOT A RESULT`, which is reserved for a value produced and ungradeable."*

**Nothing was repaired.** No frozen file was edited (`CLAUDE.md` rule 6; `PREREGISTRATION.md` §4.3).
Stages η, O and T were **never launched**, and **no second budget was taken** (`CLAUDE.md` rule 12).
Every artifact is preserved in place for the supervisor's personal triage
(`SUPERVISION_CHARTER.md` §3 — a crash is a finding until triage says otherwise).

**Total measured spend: 0.30 core-min = $0.000257 DERIVED**, against 29.8 core-min predicted and a
HARD ceiling of 70.0. **That ratio is not a calibration** — see §6.3.

**Nothing is filed, sent, uploaded, posted or pushed anywhere** (`CLAUDE.md` rule 7).

---

## HEADLINE — Stage G did exactly the job it was registered to do, and it cost 0.30 core-min to do it

`PREREGISTRATION.md` §4 registered Stage G for one reason, stated there in advance:

> **Stage G runs first and is not flow.** It exists because the D1-C′ incident (L-273) cost a graded
> row to a defect that a dry run against the frozen inputs would have caught.

It caught one. The frozen `d3_runScript.py` calls `nom_addThicknessConstraints2D` and
`nom_addVolumeConstraint` **without ever registering a triangulated surface with the
`DVConstraints` object**. pyGeo raises immediately, before any primal, and the item stops at
**0.30 core-min of a 29.8 core-min budget** — roughly **1 %** of the item's predicted price, and
about **2.6 %** of the ≈11.6 core-min a single A4 optimisation arm costs.

**The alternative, had Stage G not been registered, was Stage O discovering the same `KeyError`
after paying for a cold baseline primal.** That is the D1-C′ failure repeating, and it did not
repeat.

---

## 1. Toolchain — two rows (`DAFOAM_CHARTER.md` §6; `PREREGISTRATION.md` §3)

| row | image | `libidwarp.so` md5 | registered md5 | stages actually run | G7 | graded? |
|---|---|---|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | **`85f59e87253e0a71a813f64ca6e4c425`** read at run time from **inside the process that loaded the library** (`geom.log:4`), imported from `/opt/idwarp_patched/idwarp/__init__.py` (`geom.log:3`) | `85f59e87253e0a71a813f64ca6e4c425` | **G only** (η, O, T-patched never launched) | **`PASS`** | this is the graded row |
| **SHIPPED** | `dafoam/opt-packages:latest` | **not read** — no container of this image was started | `f0fcb488e0e98156575cd19548e91663` | **none** (T-shipped never launched) | **`PENDING`** | no row produced |

`nProcs : 1` asserted in the log (`geom.log:14, 23, 194, 450`), as G7 requires.

**The §1 provenance limitation is now partly closed and partly still open.** The freeze recorded both
image hashes as *inherited from the A4 record, not re-verified* (the docker socket refused that lane).
The patched hash is now **re-verified live from inside the loading process** and matches. **The
shipped hash remains inherited and unverified** — nothing this item ran touched that image.

---

## 2. Stages as executed, with costs

| stage | registered | launched? | rc | wall s | ranks | core-min | stage ceiling | `timeout` | peak RSS | cap |
|---|---|---|---|---|---|---|---|---|---|---|
| **G** `geom_probe` | patched, no flow | **YES** | **1** | **18** | 1 | **0.30** | 3.0 | 180 s (did **not** fire) | **0.607 GiB** | 6 GiB |
| **η** `eta` | patched, 3 primals | **NO — never launched** | — | — | — | **0** | 6.0 | 360 s | — | — |
| **O** `run_driver` | patched, many primals | **NO — never launched** | — | — | — | **0** | 42.0 | 1900 s | — | — |
| **T-patched** `endpoint_at` | patched | **NO — never launched** | — | — | — | **0** | 12.0 | 420 s | — | — |
| **T-shipped** `endpoint_at` | shipped | **NO — never launched** | — | — | — | **0** | 12.0 | 420 s | — | — |
| **TOTAL** | | | | **18** | | **0.30** | 63.0 / HARD 70.0 | | | |

Ledger of record: `/home/ubuntu/certonomous-runs/D3-a4-constrained/ledger.txt` (one row; the four
absent rows are absent because nothing ran, not because nothing was recorded).

**No ceiling was approached, no `timeout` fired, and no container was OOM-killed.** `PREREGISTRATION.md`
§6 G9 anticipated exactly this reading: *"a failure with headroom unused is not a memory finding
either."* Peak RSS 0.607 GiB against a 6 GiB kernel cap and a 2.5 GiB P13 ceiling — **the crash is not
a memory event.** Exit code **1**, not 137; `--rm` is registered in §9.1, so OOM is read from exit 137
and this is not one.

### 2.1 Staging, and the assertions the pre-registration required (§9, §9.3, G8)

Run root `/home/ubuntu/certonomous-runs/D3-a4-constrained/`, **asserted ABSENT** before staging and
created `chmod 0777` by the launching shell (L-251). Stager of record:
`/home/ubuntu/certonomous-runs/D3-a4-constrained/stage_d3.sh`.

- Base copied **byte-for-byte** from `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base/` into
  five stage directories. **The mesh was not regenerated, refined or re-decomposed** (§11 item 2).
  `log.checkMesh` reads **`cells: 2777`**; `constant/triSurface/ahmed_25.stl` md5
  **`ec3abd312d3e3e9d15340b95365ff62f`** — **equal to the §1 registered value**.
- **G8 cold start, verified before the launch, not after:** no `processor*`, no numeric time
  directory other than `0`, `0/` restored from `0.orig/`, no `reports/` carried over. Asserted
  mechanically per stage; the launcher re-asserts immediately before the container starts.
- **§9.3 md5 after the copy:** every staged `runScript.py` hashes
  **`af2ce474e7954c03e3937161510f6590`**, re-asserted by the launcher at launch time.
- **L-252:** per-invocation unique suffix `1787594047_1520007` written to `<stage>/.d3_uniq` and to
  `PROVENANCE_1787594047_1520007.txt`, `test -s`-checked, and every step chained with explicit
  `|| exit 1` — **`set -e` was not relied on** (§9.2).

### 2.2 G6 — the launch gate, as its own command, read before the launch

`/home/ubuntu/certonomous-runs/D3-a4-constrained/preflight_history.txt`, one stamped row:

```
2026-08-24T17:55:06Z before=STAGE_G nproc=16 load1=3.17 free_cores=12.83 (floor 4)
                     memavail_GiB=27.48 (floor 12) G6=OPEN
```

**Gate OPEN on both limbs**, read before the launch command was issued, never polled by a background
process and never inferred (§6 G6). **There is one row and not five** because four launches never
happened — the gate was not run for a stage that was not launched.

---

## 3. THE FINDING — the frozen script never registers a surface with `DVConstraints`

### 3.1 What the run actually did, quoted from its own log by path and line

`/home/ubuntu/certonomous-runs/D3-a4-constrained/geom.log`, 502 lines, `geom.log:472-491`:

```
Traceback (most recent call last):
  File "/mnt/geom/runScript.py", line 195, in <module>      prob.setup(mode="rev")
  ...
  File "/mnt/geom/runScript.py", line 154, in configure     self.geometry.nom_addThicknessConstraints2D(
  File ".../pygeo/mphys/mphys_dvgeo.py", line 429           self.DVCon.addThicknessConstraints2D(
  File ".../pygeo/constraints/DVCon.py", line 593           coords = self._generateIntersections(...)
  File ".../pygeo/constraints/DVCon.py", line 3233          p0, p1, p2 = self._getSurfaceVertices(surfaceName=surfaceName)
  File ".../pygeo/constraints/DVCon.py", line 3219
    raise KeyError('Need to add surface "' + surfaceName + '" to the DVConstraints object')
KeyError: 'Need to add surface "default" to the DVConstraints object'
```

The failure is in **`configure()`**, reached from `prob.setup()`. **No flow solve was attempted, no
`d3_summary.json` was written** (verified absent on disk), and `om.n2` at line 196 was never reached.

### 3.2 The mechanism, established against the lab's own working precedents — not inferred

`nom_addThicknessConstraints2D` and `nom_addVolumeConstraint` both default to
`surfaceName="default"` (`pygeo/mphys/mphys_dvgeo.py:417-425`). The **only** registrar of that name is
`nom_setConstraintSurface(surface, name="default", ...)` (`mphys_dvgeo.py:541-545`), which forwards to
`DVCon.setSurface`. Without it there is no `"default"` surface and `_getSurfaceVertices` raises.

The frozen D3 script calls `nom_add_discipline_coords("aero", points)` at line 137 — which registers
the point set with **DVGeo** — and then goes straight to the constraint calls. It **never** calls
`nom_setConstraintSurface`, and it never calls `self.mesh.mphys_get_triangulated_surface()`.

**Both precedents the pre-registration cited do call it, immediately before their constraint calls:**

| file | the two lines D3 lacks | the constraint calls §1 cited |
|---|---|---|
| `/home/ubuntu/dafoam-tutorials/JBC_Hull/runScript.py` | **:106** `tri_points = self.mesh.mphys_get_triangulated_surface()` · **:107** `self.geometry.nom_setConstraintSurface(tri_points)` | `:175, :180, :185` |
| `A1/curriculum_D1_Cprime/d1c_runScript.py` (ran to **PASS**) | **:135** `self.geometry.nom_setConstraintSurface(tri_points)` | `:154, :155` |
| **`curriculum_D3/d3_runScript.py`** | **ABSENT** | `:154, :156` |

A sweep of `/home/ubuntu/dafoam-tutorials/` finds **`nom_setConstraintSurface` in every tutorial that
uses `DVCon`** — Cone_Supersonic, DPW4_Aircraft, Prowim, PlateHole, Cylinder, MACH_Tutorial_Wing,
Onera_M6_Wing, NACA0012 (seven variants), JBC_Hull. **There is no counter-example on this box.**

### 3.3 Why the citation is where the defect entered — and this is the transferable lesson

`PREREGISTRATION.md` §1 cited the constraint API precedent at:

> `nom_addVolumeConstraint`, `nom_addThicknessConstraints2D`, `nom_addLinearConstraintsShape` |
> `JBC_Hull/runScript.py:175,180,185,202-205`
> … same three plus `nom_addLERadiusConstraints`, run to **PASS** | `d1c_runScript.py:152-156, 175-177`

Every cited line is a **constraint call or an `add_constraint`**. **Not one cited line is the
surface registration that both files perform ~40 lines earlier** (JBC :106-107, D1-C′ :135). The
precedent was cited at the lines that *look* like the feature, and the **prerequisite fell out of the
copy because it was never in the citation.**

### 3.4 F1 fired as an event, and its registered meaning is contradicted by the evidence

§15.1 registered:

> **F1** | Stage G crashes in any DVCon call | *the JBC_Hull/D1-C′ API precedent does not transfer to
> a 3×2×2 FFD on a blunt body.*

**The event happened. The interpretation is wrong, and saying so is the point of naming falsifiers in
advance.** The API transfers fine; nothing about a 3×2×2 FFD or a blunt body was reached, because the
call never got as far as the geometry. **This is a missing-prerequisite defect in the frozen
producer, not a transferability finding**, and it must not be recorded as one.

### 3.5 What §14.2's key-set control could not have caught, stated honestly

§14.2's producer/consumer key-set assertion is a **key-name** control (it caught its own parser bug
before the freeze, and it would catch a D1-C′ `CD` / `CD_final` mismatch). **It cannot see a missing
API call**: it parses names, not call graphs. §4.1 said this in terms —

> `py_compile` checks syntax only … **its API calls are unverified until Stage G runs them.**

— and registered Stage G as the instrument that closes exactly that gap. **The registration was
correct, the instrument worked, and it returned a defect.** The item's honest reading is that the
freeze's own stated limitation was real and was measured, at the price it was registered at.

---

## 4. Gates — every one, with its verdict word from the fixed vocabulary

| gate | verdict | reading, and the artifact |
|---|---|---|
| **G5** planted-zero control | **`PASS`** | `d3_grade.py --selftest` **re-run live today, exit 0**, all **12** controls **SEEN** on files A4's own producer wrote. Archived at `<root>/grade_selftest.txt`. Control [3] recovers A4's archival `0.3112 %` from its real `check_totals` block; control [12] recovers `24.9951°` against the 25.00° design angle |
| **G6** launch gate | **`PASS`** (gate OPEN) | `free_cores 12.83 ≥ 4`, `MemAvailable 27.48 GiB ≥ 12`; `<root>/preflight_history.txt`, read before the launch |
| **G7** image identity | **`PASS`** (patched row) | `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425` from inside the loading process, `geom.log:4`; graded by the frozen comparator, `<root>/grade_geom.txt`. **Shipped row `PENDING`** — that image was never started |
| **G8** cold start | **`PASS`** for the one stage launched | asserted before the launch: no `processor*`, no numeric time dir but `0`, `0/` from `0.orig/`, no `reports/`. **The free check registered in G8 — Stage η's `eta_call1_CD` reproducing `0.1529738469354696` — was NOT bought**, because Stage η never ran |
| **G9** memory envelope | **`PASS`** | peak **0.607 GiB** against cap 6 GiB and P13's 2.5 GiB ceiling; rc **1**, not 137; **not a memory event**, and §G9's own clause covers it: *"a failure with headroom unused is not a memory finding either"* |
| **G10** cost ceiling | **`PASS`** | frozen comparator: *"0.300 core-min of the HARD 70.0; $0.000257 DERIVED at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED"* (`<root>/grade_cost.txt`) |
| **Gη** noise floor | **`PENDING`** | Stage η never launched. **No δ_repeat exists**, and none is estimated. `PENDING` is used here in its registered sense — *not yet run* — and never to soften anything (§16) |
| **G1** constraint satisfaction | **`PENDING`** | no optimisation, no `final_thickcon_slant`, no `final_volcon_aft`. §6 G1's own clause — *an empty constraint array is `NOT A RESULT`, never a pass* — is **not** invoked: nothing was produced to be empty |
| **G2** termination | **`PENDING`** | no IPOPT run, no `opt_IPOPT.txt` |
| **G3** endpoint FD per component | **`PENDING`** | no `check_totals` sweep was run. **Disclosed:** the comparator, when pointed at the Stage G log, prints `G3+G4 NOT A RESULT — plateau needs all of [0.01, 0.001, 0.0001]; log has []` (`<root>/grade_geom.txt`). That is the comparator correctly reporting an **empty** log, not a graded outcome; the item's verdict is `PENDING` because the stage never ran |
| **G4** trivial baseline | **`PENDING`** | same; the deliberately-wrong 1e-1 step was never swept |
| **Gs** separation monitor | **`PENDING`** | **no field was written**, so `d3_sep_monitor.py` was never run against this item's own output. Per the supervisor's ruling 4 (`PREREGISTRATION.md` §18.1), when it *does* run and refuses, the verdict cell reads **`NOT A RESULT`** with `NOT AN INSTRUMENT` printed beside it as the reason. **It did not run, so it did not refuse**, and reporting a refusal here would be reporting a reading nobody took |
| **Gθ** rear-slant angle | **`PENDING`** | no final design vector. The comparator's controls [12] `24.9951°` and [13] `15.990°` are **selftest controls on the geometry model**, not measurements of this item |

**Item verdict: `BLOCKED`** (§16: a Stage-G crash makes the item `BLOCKED`).

---

## 5. Predictions P1–P14 — HIT / MISS / NOT TESTED, with the numbers

**Rule applied throughout: a prediction whose stage never ran is `NOT TESTED`, never a MISS and never
a HIT.** Scoring an unrun prediction either way would be inventing evidence.

| id | prediction | outcome | number, and why |
|---|---|---|---|
| **P1** | Stage G completes, every DVCon call returns finite baseline values within 1e-6 of 1.0 | **MISS** | Stage G did not complete: `KeyError` at the **first** DVCon call (`geom.log:491`). **No constraint value of any kind was produced.** The miss is not about pyGeo's normalisation — the call never reached it |
| **P2** | measured FFD Jacobian within **2 %** of `(+0.72287, −0.43863)` | **NOT TESTED** | the Jacobian probe lives in the `geom_probe` task block, which runs **after** `prob.setup()`. `setup()` raised, so the probe never executed |
| **P3** | symmetry residual `max|z(+y) − z(−y)| ≤ 1e-9` | **NOT TESTED** | same block, same reason. §2.4's decline of `nom_addLinearConstraintsShape` therefore **remains unverified by measurement**, exactly as §2.4 warned it would be without Stage G |
| **P4** | δ_repeat ∈ [0, 1.4e-05] | **NOT TESTED** | Stage η never launched |
| **P5** | η plant `\|ΔCD\|` ∈ [1.0e-05, 4.0e-05] | **NOT TESTED** | Stage η never launched |
| **P6** | Stage O majors ∈ [7, 14] | **NOT TESTED** | Stage O never launched |
| **P7** | CD reduction ≥ 7.478 %, band [7.4 %, 16 %] | **NOT TESTED** | Stage O never launched |
| **P8** | two images' analytic gradients agree ≤ 1e-4 relative per component | **NOT TESTED** | Stage T never launched, on either image. **A4's immateriality re-test is not bought** |
| **P9** | endpoint FD per-component error ∈ [0.1 %, 2.0 %], zero sign flips | **NOT TESTED** | no sweep |
| **P10** | θ(optimum) ∈ [14°, 22°] | **NOT TESTED** | no optimum |
| **P11** | the separation monitor REFUSES (`n_rev_global = 0`, `n_cells(B) < 20`) | **NOT TESTED on this item's own field** | no field was written. §7.2's freeze-time reading on **three archived A4 fields** stands unchanged (`n_rev_global = 0`; `min U_x` 23.526 / 24.084 / 24.095 m/s; `m_def_global` 0.5882 / 0.6021 / 0.6024), and §18.1 ruling 3 records the supervisor's independent count over **every** 2,777-cell A4 field on disk — zero everywhere. **That is archive and supervisor evidence, not this run's evidence**, and §7.3 required the live test that was not bought |
| **P12** | `m_def_global`(optimum) ∈ [0.45, 0.75] | **NOT TESTED** | no optimum field |
| **P13** | peak RSS ≤ 2.5 GiB, point estimate 1.4 GiB | **NOT TESTED as registered** | measured **0.607 GiB** on a stage that runs **no primal**. The registered prediction is about a flow stage; quoting 0.607 GiB as a P13 HIT would be scoring a different experiment |
| **P14** | total ≤ 51.6 core-min, HARD ≤ 70 | **HIT, trivially and uninformatively** | **0.30 core-min**. A budget prediction cannot be tested by an item that stopped at 1 % of its work, and this HIT should carry no weight in any future estimate |

**Falsifier register:** **F1 fired as an event and its registered interpretation is contradicted**
(§3.4). F2–F12 **not tested**. No falsifier was silently dropped.

---

## 6. Cost (`CLAUDE.md` rule 12; `COMPUTE_BUDGET_CHARTER.md`)

`cost_basis:` **c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so **every dollar
figure here is DERIVED and is never quoted as measured.**

### 6.1 What was spent, separated into measured, bounded and uninstrumented

| item | core-min | basis | $ DERIVED |
|---|---|---|---|
| **Stage G container** | **0.300** | **MEASURED** — 18 wall s × 1 rank ÷ 60, from `<root>/ledger.txt` | $0.000257 |
| G6 preflight (1 invocation) | **not separately instrumented** | one foreground shell command, no container; sub-second | — |
| staging (5 case copies) | **not separately instrumented** | file copies, no container, no solver | — |
| **triage container** (§7.2, unregistered) | **≤ 0.30, a BOUND, not a measurement** | a read-only container with **no volume mount**, sourcing the environment and running `grep` over the pyGeo source. Bounded above by Stage G's own 18 s, which additionally built the OpenMDAO model | ≤ $0.000257 |
| **TOTAL** | **0.300 measured; ≤ 0.60 including the bounded triage row** | | **$0.000257 measured-basis; ≤ $0.000514 with the bound** |

**Gross vs cleaned:** identical. The longest wall on this item is **18 s**; the 3600-s stall rule
(`COMPUTE_BUDGET_CHARTER.md` §2) matches nothing, so there is nothing to clean out.

**Waste, named separately and never absorbed into the ratio (charter §6): 0.300 core-min.** The Stage
G container returned **no registered measurement** — not P1, not P2, not P3. It returned a **defect**,
which is a finding of real value, but it is not the deliverable it was priced for. Per charter §6 the
spend is reported **gross as an unrecovered cost** and is not netted against the finding's worth.

### 6.2 Estimate versus actual — and the honest statement of what it does not mean

| | predicted | actual | ratio |
|---|---|---|---|
| Stage G | 1.0 core-min (ceiling 3.0) | **0.300** | **0.30×** |
| Stage η | 2.5 (ceiling 6.0) | 0 — never launched | n/a |
| Stage O | 21.0 (ceiling 42.0) | 0 — never launched | n/a |
| Stage T (both arms) | 5.3 (ceiling 12.0) | 0 — never launched | n/a |
| **TOTAL** | **29.8** (contingency 59.6; HARD 70.0) | **0.300 measured** | **0.010×** |

**The 0.010× total ratio is NOT a calibration of this item's estimate, and must not be read as one.**
Three of four stages never launched, so **the estimate was never tested**. This is the C-10 situation
in the ledger's own words — *"NOT a misprediction — the prediction was never tested"* — and the total
row is reported only so the spend is on the record, never as evidence that the lab over-estimates.

**The one row that IS a calibration is Stage G at 0.30 against 1.0 predicted (0.30×).** Attribution:
**misprediction in the conservative direction, with no contention and no waste in the timing.** The
1.0 core-min estimate priced *"container + setup, no flow"* for a stage that would run to completion;
the actual stage **exited early on a defect at 18 s**, so even 0.30× is an underestimate of what a
completing Stage G would cost. **It is therefore a soft data point and is labelled as one.** Load at
launch was **3.17 on 16 cores** with 27.48 GiB available — **no contention penalty applies**, and none
is claimed.

**Calibration lesson this item can offer, which does not depend on the unrun stages:** a
zero-flow API-exercise stage is **worth about 1 % of a constrained-optimisation item's budget** and
returned a defect that would otherwise have surfaced after a paid cold primal. **The Stage G pattern
should be priced into every future constrained-optimisation registration**, and its own estimate
should be split into *completes* and *exits-on-defect*, because the two cost very differently.

### 6.3 The calibration row — DRAFTED here, and deliberately NOT appended to the ledger

**This lane did not write `docs/COST_CALIBRATION.md`, and the reason is a conflict it is not entitled
to resolve on its own authority.** `PREREGISTRATION.md` §8.2 says in terms:

> **Who writes the row:** this lane **DRAFTS** the calibration row into the item's `RESULTS.md`; the
> **supervisor lands it** in `docs/COST_CALIBRATION.md`. **No lane writes that file** (D1 Amendment
> A1.1).

and the D1 amendment it adopts (`A1/curriculum_D1/PREREGISTRATION.md:789-804`) says
*"This lane does not write it"*, giving as its reason that the file **lags HEAD by design under the
private-index protocol and is never used as a base**. The dispatching brief for this phase directed
the lane to append the row directly. **That instruction is answered, not merely obeyed**
(`CLAUDE.md` rule 9): a supervisor's dispatch is not authority to depart from a clause of the item's
own frozen pre-registration, and the clause names the supervisor as the lander. **A second reason
points the same way:** `CLAUDE.md` rule 12 places the row at *process completion* — **this item is
`BLOCKED` at its first stage and is not complete.**

**Draft row, in the ledger's registered format, for the supervisor to land — or to hold until D3 is
re-registered and run.** The `id` is deliberately left as a placeholder: rule 11 requires it be
re-derived from the file's own tail as the **maximum existing number** *in the committing invocation*,
and a number written here would be stale by the time it lands.

```
| C-<re-derive from the HEAD blob's tail at commit time> | 2026-08-24 | dafoam
| curriculum D3 (A4 Ahmed, constrained drag minimisation) -- **BLOCKED at Stage G, item NOT completed**
| 29.8 core-min registered (contingency 59.6; HARD ceiling 70.0) = $0.0255 derived -- prereg §8, frozen `0cbf463c`
| 0.300 core-min MEASURED (18 wall s x 1 rank / 60, run-root `ledger.txt`) = $0.000257 derived;
  plus a BOUNDED <= 0.30 core-min unregistered triage container (§7.2) -- total <= 0.60 core-min
| = gross (longest wall 18 s; the 3600-s stall rule matches nothing)
| **0.010x on the total -- NOT A CALIBRATION: three of four stages never launched and the estimate
  was never tested** (the C-10 situation). The one testable row is Stage G, 0.300 vs 1.0 = **0.30x**,
  and even that is soft because the stage exited on a defect at 18 s rather than completing
| misprediction only, conservative direction; **zero contention** (load1 3.17 on 16 cores, 27.48 GiB
  available at launch); **WASTE NAMED: 0.300 core-min** -- the Stage G container returned no
  registered measurement (P1 MISS, P2/P3 NOT TESTED). It returned a defect, which is not netted
  against the waste (charter §6)
| `cases/dafoam/ladder-a/A4/curriculum_D3/RESULTS.md` §6; run-root ledger (outside git)
  `/home/ubuntu/certonomous-runs/D3-a4-constrained/ledger.txt`; prereg frozen `0cbf463c`,
  supervisor authorisation addendum `8bd8d9d7` |
```

---

## 7. Departures and disclosures — everything this phase did that the frozen file did not say

### 7.1 The reporting form

`PREREGISTRATION.md` §17 step 9 says *"RESULTS.md: six report headings"*. **The six fixed headings of
`REPORTING_CHARTER.md` §2 are `SPEND / LADDER POSITIONS / GATES / FD TABLES / REFILLED QUEUE /
WAITING LIST` — the frame of the daily morning report**, matched literally there and required in that
document. They are not the form of a results file, and no results file in this ladder uses them (the
A4 sibling `shipped_optimisation_np1/RESULTS.md` runs HEADLINE + §1–§10, and the D3 pre-registration
cites that file by those section numbers throughout). **This file follows the A4 sibling's form** and
covers the charter's subject matter in §6 (spend), §4 (gates) and §5/§3 (the tables). **Disclosed as a
reading of §17, not as a silent choice.**

### 7.2 One unregistered container, read-only, disclosed

To establish the crash **mechanism** rather than assert it, one additional container was started:
`docker run --rm dafoam-idwarp-rot:v1` with **no volume mount at all**, sourcing the DAFoam
environment and running `grep` over `pygeo/mphys/mphys_dvgeo.py` to read the signatures of
`nom_setConstraintSurface` and `nom_addThicknessConstraints2D` quoted in §3.2. **It could not and did
not write to the run root, to any case directory or to any repository path.** No solver ran. Its cost
is **not instrumented** and is carried in §6.1 as a **bound (≤ 0.30 core-min)**, never as a
measurement. **It is a departure from the four registered stages and is named as one.**

### 7.3 What was NOT done, deliberately

- **No frozen file was edited.** `d3_runScript.py`, `d3_grade.py`, `d3_sep_monitor.py` and
  `PREREGISTRATION.md` §§1–17 are byte-unchanged (`CLAUDE.md` rule 6; §4.3).
- **No repair was attempted, and no re-run was launched.** §4.3 makes a repair a
  `VERIFICATION_CHARTER.md` §2d.1 four-condition decision **for the supervisor**, and any
  re-registered work a **new mini-item** in the D1-C′ pattern.
- **No second budget was taken** (`CLAUDE.md` rule 12; F12).
- **No `docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md` or
  `docs/COST_CALIBRATION.md` was written** (§11 item 7). Record candidates are drafted in §9 below.
- **Nothing about the 45,760-cell successor was run, staged or prepared** (§12.1, §18.1 ruling 3).

### 7.4 One pre-existing repository condition, observed and not touched

`python3 scripts/check_filing.py` exits 1 repo-wide with **28 filing violations across 4 rules**.
**Zero of them are in `cases/dafoam/ladder-a/A4/curriculum_D3/`** (checked by name). They are
pre-existing, elsewhere, and were **inspected, not reverted** — nothing here fixed or hid them.

---

## 8. What this item could not see

1. **Nothing about the constrained optimisation problem was measured.** No gradient, no constraint
   value, no design variable, no CD, no noise floor. Every aerodynamic and optimiser claim D3 was
   registered to make is **unmade**.
2. **The two-DV design space was never exercised.** §2.2's `shapeBreak`/`shapeRear` pair was
   constructed in `configure()` **after** the crashing call in source order but was never driven, so
   the supervisor's ruling 1 (§18.1) — which authorised the extension — is **still untested by
   compute**.
3. **The symmetry-by-construction claim of §2.4 is still unverified.** P3 was the measurement that
   would have converted it from an argument into a reading, and it was not taken.
4. **The shipped image was never started**, so its `libidwarp.so` md5 remains **inherited from the A4
   record**, exactly as the §1 provenance limitation stated at freeze.
5. **The separation content remains as §7.3 registered it** — absent on this mesh — but that now rests
   on **archive fields and the supervisor's independent count**, not on this item's own output.
6. **`cellLimited Gauss linear 1` (§11 item 9) is untouched and unmeasured**, as registered.
7. **Whether a corrected script would reach P1–P3 is unknown and is not predicted here.** The
   `KeyError` is the first defect the interpreter met; **it is not evidence that it is the only one.**
   Stage G would have to be re-run to find out, and that is the supervisor's decision, not this
   lane's.

---

## 9. Record candidates — DRAFTED here, landed by the supervisor

**This lane writes none of `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md` or
`docs/LAB_STATE.md`** (§11 item 7). Ids are placeholders: `CLAUDE.md` rule 11 requires them to be
re-derived from each file's own tail as the **maximum existing number** in the committing invocation.

### 9.1 LESSON candidate — cite the prerequisite, not just the feature

> **L-<re-derive>: A precedent citation that names only the call you are copying omits the call that
> makes it work.** D3's pre-registration cited its constraint API precedent at
> `JBC_Hull/runScript.py:175,180,185` and `d1c_runScript.py:152-156` — **every cited line a
> `nom_add*Constraint*` call.** Both source files register the DVCon surface ~40 lines earlier
> (`nom_setConstraintSurface`, JBC :107, D1-C′ :135) and **neither line was cited**. The frozen script
> reproduced the cited lines faithfully and omitted the uncited prerequisite; pyGeo raised
> `KeyError: 'Need to add surface "default" to the DVConstraints object'` inside `prob.setup()`.
> **Rule: a precedent citation spans the whole working block — the setup call, the feature call and
> the constraint registration — or it is not a precedent, it is a snippet.** Cost of learning it here:
> **0.30 core-min**, because a zero-flow probe stage was registered to run first.

### 9.2 LESSON candidate — the zero-flow API stage paid for itself on its first use

> **L-<re-derive>: Register a zero-flow stage that exercises every framework call before any stage
> that buys a primal.** D3's Stage G (`-task geom_probe`, no flow solve, 1.0 core-min predicted /
> **0.30 measured**) caught a fatal `configure()` defect at **1 % of the item's 29.8 core-min budget**
> and **2.6 %** of a single A4 optimisation arm. The defect class is L-273's — a frozen producer that
> compiles and is wrong — and §4.1 had stated in advance that `py_compile` could not see it because
> `openmdao/dafoam/pygeo/idwarp` exist only inside the container. **The instrument was registered for
> exactly this, and on its first use it returned exactly this.** Generalisation: any item whose
> producer calls a framework API the case has never run should buy a no-flow exercise stage first.

### 9.3 NUMERICS-FACT candidate — pyGeo DVCon surface prerequisite

> **N-D<re-derive>: `pygeo` `DVConstraints` geometric constraints require a triangulated surface
> registered under the name they default to.** `nom_addThicknessConstraints2D` and
> `nom_addVolumeConstraint` default to `surfaceName="default"`
> (`pygeo/mphys/mphys_dvgeo.py:417-425`); the only registrar of that name is
> `nom_setConstraintSurface(surface, name="default")` (`:541-545` → `DVCon.setSurface`), fed by
> `self.mesh.mphys_get_triangulated_surface()`. Absent it, `DVCon._getSurfaceVertices`
> (`pygeo/constraints/DVCon.py:3219`) raises `KeyError: 'Need to add surface "default" to the
> DVConstraints object'` **inside `prob.setup()`, before any primal**. Verified against every
> DVCon-using script on this box: **JBC_Hull :106-107, Cone_Supersonic :121, DPW4_Aircraft :145,
> Prowim :161, PlateHole :111, Cylinder :134, MACH_Tutorial_Wing :190, Onera_M6_Wing :130, NACA0012
> (7 variants), and the lab's own D1-C′ :135 — no counter-example exists.** `nom_add_discipline_coords`
> registers the point set with **DVGeo** and does **not** satisfy this; the two are separate
> registrations. Measured on `dafoam-idwarp-rot:v1`, 2026-08-24, `geom.log:472-491` at
> `/home/ubuntu/certonomous-runs/D3-a4-constrained/`.

### 9.4 NUMERICS-FACT candidate — the A4 2,777-cell mesh carries no separated flow

**This is a fact about the A4 rung itself, not only about D3, and it is the one the supervisor asked
be drafted as such.**

> **N-D<re-derive>: The A4 Ahmed-25° 2,777-cell adjoint mesh carries NO separated flow anywhere in
> the domain, at any design point measured.** Reverse-flow cell count `n_rev_global = 0` on **every**
> 2,777-cell A4 field on disk — the P3 optimisation's `opt/0.0001`, `opt/0.0008` and `opt/500`
> (measured at the D3 freeze, `PREREGISTRATION.md` §7.2), and the P2/P3/W4 baselines and optima
> (counted independently by the dafoam-supervisor, `PREREGISTRATION.md` §18.1 ruling 3). Minimum axial
> velocity is **+23.5 to +24.1 m/s** against U₀ = 40 — **59–60 % of freestream**, never negative.
> **The zero is evidence because the plant was seen**: the identical reader on an Ahmed-25° case at
> **79,439 cells** finds **528 reverse-flow cells and min U_x = −13.77 m/s**, and on the cfd team's
> **9,050-cell** F5c A4 field **780** (`CLAUDE.md` rule 3). *(Disclosed: the 79,439-cell case's STL is
> md5 `d8026bc2…`, not byte-identical to A4's `ec3abd31…`; the plant is a **reader-capability
> control**, not a physics comparison.)*
> **Consequence for the ladder, and it outlives D3:** the A4 rung's mesh **cannot host any claim about
> separation, wake bistability or separation-dominated flow.** It exists to host a gradient (A4
> shipped `RESULTS.md` §8 limit 4), and this fact fixes how far that limit reaches. Any item whose
> content is separation on the Ahmed body needs a different mesh — the 45,760-cell successor is
> **unpriced on this case** and is **Sanaa's decision** (`PREREGISTRATION.md` §12.1).

### 9.5 DOCKET candidate

> **D-<re-derive> (2026-08-24, dafoam): curriculum item D3 `BLOCKED` at Stage G — the frozen
> `d3_runScript.py` omits `nom_setConstraintSurface`.** Phase 2 executed per `PREREGISTRATION.md` §17;
> the supervisor's launch authorisation landed first at `8bd8d9d7` (zero compute, run root asserted
> absent). Stage G crashed in `prob.setup()` at the first DVCon call, **0.30 core-min of 29.8
> predicted**; stages η, O and T were never launched and no second budget was taken. **F1 fired as an
> event; its registered interpretation is contradicted** (the API transfers — a prerequisite call is
> missing). **On the supervisor's desk:** whether a `VERIFICATION_CHARTER.md` §2d.1 four-condition
> repair applies, or whether D3 is re-registered as a new mini-item in the D1-C′ pattern (§4.3 forbids
> the in-place edit either way). Record: `cases/dafoam/ladder-a/A4/curriculum_D3/RESULTS.md`; run root
> `/home/ubuntu/certonomous-runs/D3-a4-constrained/`.

---

## 10. Verdict vocabulary

**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING** — and no synonyms
(`CLAUDE.md` rule 1; `PREREGISTRATION.md` §16).

- **The item is `BLOCKED`**, not `NOT A RESULT`: a precondition prevented the measurement, and no
  value was produced to be ungradeable (§16).
- **`PENDING` is used here only for "not yet run"** — nine gates whose stages never launched. It is
  never used to soften a `GATE FAIL`, and no `GATE FAIL` was reached to soften.
- **`NOT AN INSTRUMENT` appears nowhere as a verdict.** Per the supervisor's ruling 4 (§18.1) it is
  the frozen monitor's printed **reason**, to be rendered beside a `NOT A RESULT` verdict cell **when
  the monitor runs and refuses**. It did not run.
- **Shipped and patched are separate rows** and are not merged: the patched row has one live G7
  reading; the shipped row has none.
- **NOT FILED ANYWHERE** (`CLAUDE.md` rule 7).

---

## 11. ADDENDUM R1 — the supervisor's written direction on the calibration row, and the landing

**Dated 2026-08-24T18:06:32Z** (`date -u`, read in the shell invocation that wrote this addendum, performed the four ledger asserts, built the tree and landed the commit).

**lines whose number changed above this section: 0** — appended at the foot; §§1–10 are byte-unchanged
from the record committed at `3e4c7d81`.

**This addendum supersedes the operative conclusion of §6.3 and leaves its reasoning standing.**
§6.3 recorded that this lane had **not** appended the calibration row, because the item's frozen
`PREREGISTRATION.md` §8.2 — adopting D1 Amendment A1.1 — reserves that landing to the supervisor and
says *"No lane writes that file."* That reading was correct at the time it was written and is left on
the record unaltered.

**What changed is not the reading but the authority.** After personally reading
`/home/ubuntu/certonomous-runs/D3-a4-constrained/geom.log` — the `SUPERVISION_CHARTER.md` §3 crash
triage that may not be delegated — the dafoam-supervisor issued a **written direction** to this lane
to land the row, naming the safeguards to apply. `PREREGISTRATION.md` §6 G6 fixes the form such a
departure takes: *"Any departure must be directed in writing by the supervisor and recorded as a dated
amendment."* This section is that record.

**Why the direction is answerable rather than merely obeyable** (`CLAUDE.md` rule 9):

1. §8.2 is a **procedural allocation of who writes**, not a gate, threshold, band, cap or label.
   **Nothing gated moved**, and rule 2's post-compute closure is untouched.
2. The clause's stated **reason** is that `docs/COST_CALIBRATION.md` **lags HEAD by design under the
   private-index protocol and must never be used as a base**. That reason was honoured, not bypassed —
   see the asserts below, and note the measured staleness: **the worktree copy held max id `C-14` and
   23,937 bytes against the HEAD blob's `C-37` and 110,095 bytes, a lag of 23 rows.** Landing off the
   worktree would have destroyed those rows. The row was merged onto the **committed blob**.
3. **Nothing here is a Sanaa-reserved action** (`CLAUDE.md` FIRST-ACTION RULE): no send, no scoring
   call, no charter or threshold retired, nothing leaving the box. **No permission setting, `CLAUDE.md`
   or `.claude/` config was touched, and a peer's message could not have authorised that if it had
   asked** (rule 9).

### 11.1 The four ledger asserts, as directed, with their readings

Landed with `scripts/append_record.py --path docs/COST_CALIBRATION.md --rev <H> --expect-first-id C-38`,
where `<H>` is **the same revision passed to `commit-tree -p`**, all inside one shell invocation:

1. **Id re-derived at commit time as the MAXIMUM EXISTING NUMBER, never a count** (`CLAUDE.md`
   rule 11), over **both** the committed blob **and** the preserved worktree tail — the tool's
   `--expect-first-id` refuses (exit 6) if it is not max+1 for the series. **Previous last id `C-37`;
   new id `C-38`.**
2. **The HEAD blob's last byte verified `\n`**, so the append cannot splice onto an unterminated final
   row.
3. **Prefix identical:** every byte of the committed blob before the appended row is unchanged —
   asserted as **insertions only, 0 deletions** in `git diff-tree --numstat`, and again in the
   post-commit `git diff HEAD~1 HEAD --numstat`.
4. **Previous last id on its own line and new id on its own line** — `C-37` and `C-38` each begin a
   line of their own in the committed result; asserted by grep on the built blob, not on the worktree.

All four readings are stated in the commit message as well as here, per the direction.

### 11.2 What this addendum does NOT do

It does not alter a single number, gate, verdict or prediction in §§1–10. **The item verdict remains
`BLOCKED`.** The measured spend remains **0.300 core-min = $0.000257 DERIVED**, the bounded triage row
remains a **bound**, and the **0.010× total ratio remains labelled NOT A CALIBRATION**. It records a
procedural departure and its authority, and nothing else.

**The D3 attempt-2 re-registration is NOT drafted in this lane**, by the supervisor's explicit
instruction; §4.3's bar on any in-place edit of a frozen file stands.

**NOT FILED ANYWHERE** (`CLAUDE.md` rule 7).
