# CURRICULUM D12 — UNSTEADY ADJOINT, 2D CYLINDER TIME-AVERAGED DRAG — PRE-REGISTRATION

**Frozen instrument. Written 2026-08-25 by dafoam `lab-lane`. NOTHING IN THIS FILE IS
EDITED AFTER ITS COMMIT.** A departure is a dated amendment appended at the foot with a
version bump and `lines whose number changed above this section: 0` (`CLAUDE.md` rule 6).

**Version 1.0. Committed BEFORE any D12 compute.** The run root this pre-registration
governs — `/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady/` — **DOES NOT
EXIST at this commit**, and that is the condition under which amendments to this file are
still legal (`CLAUDE.md` rule 2). It was checked by `test -e` returning false immediately
before this file was written. After the first container, only dated addenda that cannot
alter a gate, a threshold, a cap or a label.

**Nothing in this item is filed, sent, uploaded, registered, posted or commented outside
this box** (`CLAUDE.md` rule 7).

---

## 0. Where this file lives, and why not under `ladder-a/A?/`

The supervisor's brief named `cases/dafoam/ladder-a/A?/curriculum_D12/`, with the rung to
be resolved from `cases/dafoam/INDEX.md`. **`INDEX.md` §1 enumerates every Ladder-A rung
and none of them is the 2D cylinder**: A1 NACA0012, A2 MACH tutorial wing, A3 ONERA M6,
A4 Ahmed body, A5 U-bend, A6 CRM wing-body. D12's substrate is the upstream DAFoam
`Cylinder` tutorial, which belongs to no A-rung. `INDEX.md` §0 records that the family's
own hygiene rule (`FAMILY_SUPERVISION_GUIDELINES.md` §7) makes *a satellite citing a path
its case file contradicts* a defect, so filing D12 under an unrelated rung would
manufacture exactly that defect. **This item therefore lives at
`cases/dafoam/curriculum_D12/`**, a sibling of `cases/dafoam/probes/` where D11's and
D12's rung-less probes already live. **The deviation is disclosed here rather than taken
silently, and it is the supervisor's to reverse.**

## 1. What is being bought, and what is already settled

**The PROBE-FIRST prerequisite is DISCHARGED.** `cases/dafoam/probes/curriculum_D12_unsteady_probe/RESULTS.md`
returned `GATE REACHED` — the unsteady adjoint (`DAPimpleFoam`, `unsteadyAdjoint mode
timeAccurate`, `reduceIO True`) evaluates and returns a finite non-zero total derivative
of a time-averaged objective on the shipped image, first attempt. **This item does not
re-grade that verdict and does not restate it.**

**What that probe explicitly does NOT establish, in its own §4:** correctness, accuracy,
FD agreement or sign of the unsteady adjoint; anything about a developed vortex-shedding
limit cycle; any window length; any `δ_repeat` on a time average. Its `CD = 0.0899` is a
cold-start 5-step number and **is not a drag coefficient**.

**This item buys all of that**, in the order the supervisor ruled binding:

1. `δ_repeat` on the time-averaged objective — **MEASURED FIRST, BEFORE ANY FD STEP IS SIZED.**
2. FD steps **sized from the measured noise floor**, with the arithmetic shown.
3. A **plateau demonstrated** — consecutive steps agreeing, never one step asserted.
4. The optimisation, and **only** if 1–3 permit a gradient to be verified at all.

**A noise floor so large that no admissible step exists is a RESULT, not a failure**, and
§5 registers that branch by name before any number exists.

## 2. The case, frozen

| item | value |
|---|---|
| substrate | upstream DAFoam `Cylinder` tutorial, `/home/ubuntu/dafoam-tutorials/Cylinder` |
| geometry | circular cylinder, `R = 0.5` (`genMesh.py:R = 0.5`), `zSpan = 0.1`, one cell in z |
| mesh | pyHyp `nPoints 50`, `NpExtrude 50`, `yWall 1e-3`, `marchDist 30.0` → **2,450 cells** (measured by the probe: `Global Cells: 2450`) |
| flow | `U0 = 10.0` m/s, `nu = 1.0e-5` m²/s (`constant/transportProperties`) → **Re_D = 1.0e6** |
| turbulence | Spalart–Allmaras, `useWallFunction True`, `nuTilda0 = 4.5e-5` |
| solver | `DAPimpleFoam`, `deltaT 1e-2` |
| objective | `CD`, `type force`, `patches ["cylinder"]`, `direction [1,0,0]`, `scale 1/(0.5·U0²·A0)` with `A0 = 0.1`, **`timeOp average`** |
| DVs | the tutorial's four FFD shape-function modes, `nom_addShapeFunctionDV(dvName="shape")`, `lower −1.0`, `upper 1.0`, `scaler 10.0` |
| adjoint | `unsteadyAdjoint {mode timeAccurate, PCMatPrecomputeInterval 100, PCMatUpdateInterval 1, reduceIO True, zeroInitFields False}` |
| ranks | **np = 1 throughout**, `numberOfSubdomains 1` |
| decomposition | **not applicable at np=1 and stated as such** (`DAFOAM_CHARTER.md` §5: serial before parallel; no parallel figure is graded in this item and no FD reference is carried to another np) |

`daOptions` is the tutorial's `runScript.py` block **verbatim**, with no reduction. The
probe's two registered reductions (5 steps, cold start) are **NOT carried into this item.**

### 2.1 Toolchain identity — the hash is the identity, the version string is not (`DAFOAM_CHARTER.md` §11)

| row | image | digest | IDWarp |
|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | stock `libidwarp.so`, md5 to be recorded in-container by the launcher |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | patched `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425` against stock `f0fcb488e0e98156575cd19548e91663` (`docs/dafoam/README.md:154`) |

**The patched row is `dafoam-idwarp-rot:v1` and not `dafoam-subpclu:v2` / `dafoam-team:v1`
because D12's chain contains IDWarp** — `inputInfo.aero_vol_coords type volCoord`, FFD
shape DVs and two `symmetryPlanes` — and the IDWarp rotation fix is the patch that can
touch this number. **Both md5s are read from inside their own containers at run time and
written to the ledger**; neither is taken from recall.

## 3. The pipeline, frozen, and the window frozen with it

Every stage is np=1, one container, `--user 0:0`, `--cpus=1`, `--memory=20g
--memory-swap=20g --oom-score-adj=500`, **no `--rm`** (so `docker inspect .State.OOMKilled`
survives — checkpoint blow-up is D12's own named failure mode), a per-stage `timeout`,
`mpirun --allow-run-as-root --bind-to none -np 1`, a per-invocation `STAMP` and a `.ok`
sentinel (L-251, L-252).

| stage | what | steps | from |
|---|---|---|---|
| **S0** | mesh: `genMesh.py` → `plot3dToFoam` → `autoPatch 30` → `createPatch` → `renumberMesh` → `checkMesh` | — | tutorial |
| **S1** | the tutorial's own `preProcessing.sh` spin-up at np=1: `cp -r 0_orig 0`, `potentialFoam`, `simpleFoam` 500 iters (`controlDict_simple`), then PIMPLE to `t = 10` at `deltaT 5e-2` (`controlDict_pimple_long`). The `10` directory becomes **FIELD_A** | 500 + 200 | `0_orig` |
| **S2** | **diagnostic primal**, `run_model`, `deltaT 1e-2`, `endTime 24.0` = **2,400 steps**, from FIELD_A | 2400 | FIELD_A |
| **S3** | `δ_repeat`: **3 identical `run_model` runs** over the graded window | 3 × W | FIELD_B |
| **S4** | checkpoint envelope: `compute_totals` at `n ∈ {20, 40, 80}`, **2 runs at each** | 6 runs | FIELD_B |
| **S5** | the adjoint at the graded window, `compute_totals` | W | FIELD_B |
| **S6** | the FD sweep, central, on `shape[0]` | 2 per step | FIELD_B |
| **S6b** | the trivial baseline at 10·h\* | 2 | FIELD_B |
| **S6c** | the 4-component vector FD at h\* | 6 | FIELD_B |
| **S7** | the plant stage | 2 | FIELD_B |
| **S8** | the optimisation, IPOPT | ≤ 15 majors | FIELD_B |

### 3.1 THE WINDOW, FROZEN NOW, BEFORE ANY MEASUREMENT

- **Transient discard: the FIRST 300 timesteps of S2 (`t ≤ 3.00`) are DISCARDED.** They
  absorb the restart transient created by S1's `deltaT 5e-2` limit cycle being handed to a
  `deltaT 1e-2` integration.
- **FIELD_B := the S2 field written at `t = 3.00`**, with `uniform/` and `polyMesh/`
  stripped, renamed to `0`. **FIELD_B is the frozen initial condition of EVERY graded run
  in S3–S8.** Its per-file md5 manifest is written to the ledger at creation and
  re-asserted before each stage; a mismatch is a **REFUSAL**, not a warning.
- **PRIMARY GRADED WINDOW `W = 300` timesteps** (`deltaT 1e-2`, 3.00 s), starting from
  FIELD_B. This is the tutorial's own optimisation window (`system/controlDict_pimple`
  `endTime 3.0`), and D12 is required to grade the case it names.
- **CONTINGENCY WINDOW `W2 = 900` timesteps** (9.00 s), **and its firing condition is
  registered here, before any number exists:** W2 runs **if and only if** gate `G12R-4`
  returns `h_min > h_max` at `W = 300`, i.e. the primary window admits no FD step. **The
  `W = 300` row is then never replaced, struck or reinterpreted — W2 is an ADDITIONAL
  row and both are reported.** Registering the contingency and its trigger in advance is
  what stops a window from being chosen after seeing which one agrees.
- The 2,100 retained steps of S2 support the block-average analysis at **both** W and W2
  from **one** diagnostic run.

## 4. Instruments, and the hash that proves the file that ran is the file that was frozen

| file | role |
|---|---|
| `d12r_run_script.py` | the DAFoam driver. Every graded quantity is written to disk as JSON; **nothing is graded from stdout.** |
| `d12r_series.py` | the `CD(t)` series reader and block-average engine. Reads the stage **log file on disk**. |
| `d12r_grade.py` | the comparator. **REFUSES (exit 2) rather than degrading.** |
| `d12r_stage_and_run.sh` | the launcher. Asserts its own `CAP_CORE_MIN` against the value §6 names — the defect `D12-E′ RESULTS.md` §6.1 disclosed and this launcher is derived from. |

**Before each launch the launcher verifies, in the same shell invocation, that
`d12r_run_script.py` and `d12r_grade.py` on disk are md5-identical to their committed HEAD
blobs** (`git cat-file blob HEAD:<path> | md5sum`). A mismatch **aborts**. This is
`CLAUDE.md` rule 2's grading-path clause and it is executed, not asserted.

## 5. GATES — thresholds, bands and labels, frozen

Verdict vocabulary is fixed: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING`.

### G12R-0 — COMPLETION AND INSTRUMENT INTEGRITY (a REFUSAL, not a gate)

A stage is admissible only if **all** hold: `rc = 0`; an `End` line in its own log; the
last `Time = ` in the log equals the stage's `endTime`; the JSON carries
`status COMPLETE`; `docker inspect .State.OOMKilled` is `false`; the cold-start assertion
passed before launch (no `0.01`, no `<endTime>` directory pre-existing); the FIELD_B md5
manifest matched; **and the JSON `obj` equals the LAST `average:` value in the stage's own
log to ≤ `1.0e-12` relative.** That last clause is the log reader's own correctness
control: the series engine and the solver must agree on the one number they both compute.
Any failure → **REFUSE, exit 2.** The comparator degrades nothing.

### G12R-1 — LIMIT CYCLE ESTABLISHED

From S2's retained 2,100-step `CD` series: `PASS` iff **(a)** the sign of `CD − mean` changes
at least **6** times (≥ 3 full oscillations) **and (b)** peak-to-peak amplitude
`> 1.0 %` of `|mean|`. Otherwise **`NOT A RESULT` for every downstream claim that the
objective is a limit-cycle average** — an unsteady objective on a flow that has gone
steady is not the capability D12 names. The shedding period is reported in timesteps
either way, as an observation.

### G12R-2 — `δ_repeat`, MEASURED

Three identical `run_model` runs (S3) over W from FIELD_B, byte-identical inputs.
`δ_repeat := max(obj) − min(obj)`; `δ_repeat_rel := δ_repeat / |mean(obj)|`.

**Registered in advance, so it cannot be produced as a discovery:** at np=1 with a
deterministic solver and a byte-identical initial field, `δ_repeat` is **expected to be
0 to machine precision**. **If it is 0, that is the measurement and it is reported as
`PASS` with the value `0.000000e+00` — and the record states plainly, in the same
sentence, that a zero `δ_repeat` is NOT a clearance for the FD step**, because the noise
that threatens a time-averaged objective on a limit cycle is not repeat noise. `δ_window`
below is the quantity that carries that burden, and the FD step is sized from
`δ_eff := max(δ_repeat, δ_window)`.

### G12R-3 — `δ_window`, THE PHASE-NOISE FLOOR, MEASURED

From S2's retained 2,100-step series, the `W`-step block average is computed at **every**
start offset `k = 0 … 2100 − W` (1,801 windows at W=300; 1,201 at W2=900).
`δ_window := max − min` over those block averages; `δ_window_rel := δ_window / |grand mean|`.

**Registered rationale, before the number:** a shape perturbation shifts the shedding
phase. The part of `ΔJ` produced by that phase shift is **not** a design sensitivity, and
its magnitude is bounded by the spread of same-length averages taken at different phases.
`δ_window` is therefore the honest noise floor of the finite-window objective, and
`δ_eff := max(δ_repeat, δ_window)`.

### G12R-4 — FD STEP SIZING, ARITHMETIC REGISTERED BEFORE THE NUMBERS EXIST

For a central difference on component `i`, the noise-induced relative error is bounded by

    eps_noise(h)  =  delta_eff / ( h * |g_i| )

(two evaluations, each carrying up to `δ_eff` of phase error, over the `2h` denominator;
the factor 2 is deliberately **not** taken, so the bound is conservative).

**Registered target: `eps_noise ≤ 1.0 %`**, one fifth of `DAFOAM_CHARTER.md` §2's 5 % PASS
band, so noise cannot itself carry a component across the band. Hence

    h_min  =  100 * delta_eff / |g_i|

with `|g_i|` taken from **S5's adjoint** for `shape[0]`. *(Using the adjoint magnitude to
size the step does not bias the gate: the gate is on agreement, not on `|g|`.)*

**Registered `h_max = 0.05`, on physical grounds and not for convenience:** the FFD
shape-function modes displace surface points in `x` by `h` mesh units per unit DV, and the
cylinder radius is `0.5`. `h = 0.05` is a **10 % of radius** deformation — already at the
edge of what can be called a derivative probe rather than a redesign.

**REGISTERED BRANCH — and it is a RESULT, not a failure.** If `h_min > h_max`, **no
admissible FD step exists at that window**: the verdict for the gradient is
**`NOT A RESULT`**, `δ_eff`, `|g|`, `h_min` and `h_max` are all quoted beside it, the
contingency window W2 of §3.1 fires, and **D12's optimisation does not proceed on a
gradient that could not be verified.**

**The registered sweep** (only if `h_min ≤ h_max`): five steps on `shape[0]`, central,

    h in { h_min*1e-1 , h_min , h_min*10 , h_min*100 , h_min*1000 }

each rounded to one significant figure and **clipped at `h_max`**; steps that clip to a
duplicate are dropped and the dropped rows are named in the table. **Every step that runs
appears in the table, including the ones that fail** (`VERIFICATION_CHARTER.md` §7: a
sweep that hides its failed steps is reporting a plateau it did not measure).

### G12R-5 — THE PLATEAU

`PASS` iff **three or more consecutive sweep steps** have FD estimates of
`d(obj)/d(shape[0])` agreeing pairwise within **2.0 %** of their own mean. `h*` := the
middle step of the widest such run. **If no run of three exists, the gradient is
`NOT A RESULT`** and the full sweep table is printed regardless. **One step is never a
plateau**, and a step is never selected after seeing which one agrees.

### G12R-6 — THE BRIGHT LINE: adjoint vs FD at `h*` (`DAFOAM_CHARTER.md` §2)

Statistic **named, not implied**: the **vector-relative error**
`‖g_adj − g_fd‖ / ‖g_fd‖` over the four `shape` components at `h*` (S6c), **printed as
the aggregate**, with the **per-component relative errors reported beside it, never
instead of it**.

| band | verdict |
|---|---|
| ≤ **5 %** aggregate **and zero sign-flipped components** | `PASS` |
| **5 %–15 %** aggregate, zero sign flips, per-component breakdown mandatory | `CONDITIONAL` |
| **> 15 %** aggregate **or any sign-flipped component**, regardless of aggregate | `GATE FAIL` |

*(`CONDITIONAL` is the charter §2 band label, not a verdict from the `CLAUDE.md` rule-1
vocabulary; the RESULTS row carries the rule-1 verdict alongside it — `PASS` for ≤5 %,
`GATE FAIL` above 15 %, and for the 5–15 % band the rule-1 verdict is `GATE FAIL` against
the 5 % PASS threshold with the charter's `CONDITIONAL` reported as the band. This is
registered now so the mapping cannot be chosen later.)*

**A component whose FD estimate does not stabilise anywhere in the sweep is flagged and
excluded BY NAME from the aggregate, never dropped silently** (`DAFOAM_CHARTER.md` §3),
and the aggregate excluding flagged components is reported as a **separate column**, never
as the headline.

**Registered honesty clause on the harness floor:** `VERIFICATION_CHARTER.md` §7 step 4
puts a **2.5–5 %** floor on vector-relative FD error for **shape DVs through IDWarp** on
this stack, and D12's DV **is** a shape DV through IDWarp. **A measured aggregate far
below 2.5 % is therefore itself flagged in the record as a claim about the harness**, not
quietly celebrated.

**Forward-AD / complex-step reference (`DAFOAM_CHARTER.md` §2, second clause):** the
images ship `libDASolverADF.so`. **This item does NOT reach for it, and says so: the
forward-AD build's reachability under `DAFoamBuilderUnsteady` is unprobed by this lab,
and probing it is a separate capability question this pre-registration does not buy.**
The FD table is therefore the only reference here, and that is a stated limit.

### G12R-7 — THE REGISTERED TRIVIAL BASELINE (`DAFOAM_CHARTER.md` §4)

**The same probe at a deliberately wrong step: `h = 10 · h*`.** Registered prediction,
before its own run: **the wrong step's vector-relative error is `> 5 %`, i.e. it must NOT
reach `PASS`.**

**If the wrong step ALSO passes, gate G12R-6 is not measuring what it claims and the
verdict it produced is WITHDRAWN.**

### G12R-8 — CHECKPOINT-STORAGE ENVELOPE, DISK **AND** RAM, WITH REPEATS

D12-E′ left this **UNRESOLVED**: it measured a 1.3 MiB difference between 5 and 10 steps
with **one run per point**, below a run-to-run RSS noise scale it could not measure. So
this item measures the noise floor instead of assuming it.

S4: `compute_totals` at `n ∈ {20, 40, 80}`, **two runs at each `n`**, from FIELD_B.
Recorded per run: `maxrss` after primal, `maxrss` after adjoint, `ΔR :=` the rise, and the
case-directory disk delta in bytes.

- **RSS noise floor** `σ_R := max over n of |ΔR(run 1) − ΔR(run 2)|`.
- **REGISTERED IN ADVANCE:** the per-step RAM term is reported as **RESOLVED** only if
  `|ΔR(80) − ΔR(20)| > 3 σ_R`. **Otherwise it is `UNRESOLVED`, and the envelope is
  reported as bounded above by `3σ_R / 60` GiB per step — never as "flat".**
- The same rule, with the same `3σ` form, is applied to the **disk** delta.
- **Projection to the graded window:** `ΔR(W) ≤ ΔR(80) + (W − 80) ×` (the registered upper
  bound on the per-step term). Reported as a **bound**, with its basis, never as a value.
- `reduceIO: False` — which moves the same state to disk — is **NOT probed by this item**,
  and that is a stated limit, not an omission.

**MEMORY IS A PHYSICAL CEILING AND THE THRESHOLD IS STATED BEFORE MEASURING.**
`MemAvailable` is read from `/proc/meminfo` immediately before **every** container launch
and written to the ledger. **Floor: 14.0 GiB.** Below it the stage is **NOT LAUNCHED** and
is labelled **`BLOCKED`** with the reading quoted. Every graded container carries
`--memory=20g --memory-swap=20g`, so an OOM is a **measured** event and not a box crash.

### G12R-9 — PLANTED ZERO (`CLAUDE.md` rule 3)

Three readers in this item can emit a zero, and **each plants, reads back from disk, and
REFUSES if it cannot see the plant**:

1. **The objective/series reader.** A synthetic copy of a real stage log is written to
   disk with one `average:` line multiplied by a known factor; the reader must return the
   perturbed series. If it returns the unperturbed one → **REFUSE**.
2. **The FD comparator.** Stage `plant` (S7) runs `run_model` with `shape[0] = 1.234e-03`
   planted; `d12r_plant.json` on disk must carry that value, and `obj_plant` must differ
   from the unplanted `obj` by **more than `1.0e-9` relative**. If the objective cannot
   see a planted shape change, no FD number from this instrument is evidence → **REFUSE**.
3. **The envelope reader.** A synthetic ledger line with a known `du_delta_B` is written
   to disk and must be read back exactly. If not → **REFUSE**.

### G12R-10 — TWO ROWS, SHIPPED AND PATCHED (`docs/dafoam/README.md` §3)

**Registered scope, stated before compute and not to be softened afterwards.** The
**SHIPPED** row (`dafoam/opt-packages:latest`) carries the full item: S0–S8. The
**PATCHED** row (`dafoam-idwarp-rot:v1`) carries **its own S0, S1, S2 and FIELD_B**, its
own S5 adjoint, and an **FD pair at SHIPPED's `h*`** — because an FD reference is part of
a **configuration**, not a property of a case (`DAFOAM_CHARTER.md` §5), so a patched-row
FD number must come from patched-row primals.

**The patched row therefore carries a ONE-STEP FD table, not a sweep, and the verdict line
says so in the verdict line itself.** Registered reason: a second full sweep buys a second
plateau on the same physics; the two-row duty is about the number, not about duplicating
the sweep. **If the patched row's FD at `h*` disagrees with its own adjoint by > 15 %,
that is a `GATE FAIL` on the patched row and is reported as one** — the absent sweep is a
stated limit, never an excuse.

### G12R-11 — THE OPTIMISATION

**Runs ONLY if `G12R-6` returns `PASS` or the charter's `CONDITIONAL` band on the SHIPPED
row.** Otherwise the optimisation is **not launched** and D12's optimisation is
**`NOT A RESULT`**, with the reason quoted.

- IPOPT via `pyOptSparse`, 4 `shape` DVs, bounds ±1.0, `scaler 10.0`, minimise the
  time-averaged `CD` over the graded window from FIELD_B. No further constraints.
- **Registered stop: `max_iter 15` majors, or IPOPT's own convergence, whichever first.**
- **`GATE REACHED` iff** the run terminates with an IPOPT exit status present in its own
  log **and** `obj_final < obj_baseline − δ_eff`. **An objective reduction smaller than
  the measured phase-noise floor is `NOT A RESULT`, not a small win.** That threshold is
  registered here, before `δ_eff` is known.
- An endpoint `check_totals` is a **reported observation, not a gate** — and
  `DAFOAM_CHARTER.md` §9's warning that a gradient verified at iteration 0 is not verified
  at iteration 47 is a **stated limit of this item**, not a claim it discharges.

## 6. COST, AND THE CAP AS A RUNAWAY GUARD

Sanaa, 2026-08-25: *"no team stops anything in the name of saving compute."* **Caps here
are runaway guards, not budgets.** A cap crossing **STOPS the stage** and is **reported to
the supervisor by committing**; this lane neither silently continues nor silently abandons.
Costing and calibration are unchanged and continue in full.

Anchors, all measured, from `curriculum_D12_unsteady_probe/RESULTS.md` §3 and
`..._Eprime/RESULTS.md` §3: primal **0.195 s/step**; unsteady adjoint **2.158 s/step**;
`dRdWTPC` **≈ 3.92 s** once; startup **≈ 7.7 s**. Derived fits:

    run_model      wall(n)  ≈  7.7  + 0.195 n   seconds
    compute_totals wall(n)  ≈ 19.0  + 2.000 n   seconds     <-- UNDER TEST, see §6.1

| stage | runs | core-min |
|---|---|---|
| S0 mesh, 2 images | 2 | 0.10 |
| S1 spin-up, 2 images | 2 | 5.00 |
| S2 diagnostic 2,400 steps, 2 images | 2 | 15.90 |
| S3 `δ_repeat`, 3 × `run_model` at W | 3 | 3.30 |
| S4 envelope, 6 × `compute_totals` (20/40/80 ×2) | 6 | 11.23 |
| S5 adjoint at W, 2 images | 2 | 20.63 |
| S6 FD sweep, 5 steps × 2 halves | 10 | 11.00 |
| S6b trivial baseline | 2 | 2.20 |
| S6c 4-component vector FD at h\* | 6 | 6.60 |
| S6d patched FD pair at h\* | 2 | 2.20 |
| S7 plant + clean | 2 | 2.20 |
| **verification subtotal** | | **80.4** |
| S8 optimisation, 15 majors × 11.3 | | **170.0** |
| **TOTAL, primary window** | | **250.4 core-min** |
| contingency window W2, if §3.1 fires | | **+ 90.0** |

**Predicted total: 250.4 core-min (340.4 with the W2 contingency)
= $0.2141 ($0.2911) DERIVED, NOT MEASURED**, at $0.0513/core-h, c7a.4xlarge,
**reported-by-owner** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**REGISTERED CAP: 600.0 core-min total across EVERY container this item launches**, with a
**sub-cap of 350.0 core-min on S8**. The launcher asserts `CAP_CORE_MIN` against **600.0**
at start-up and aborts if it does not match — closing the defect `D12-E′ RESULTS.md` §6.1
disclosed, where a copied-forward launcher enforced a cap its pre-registration did not name.

### 6.1 THE WALL-TIME FIT IS ITSELF UNDER TEST

`curriculum_D12_unsteady_probe/LANE_REPORT.md` §4 prices D12 from a **two-point** fit,
`wall(n) = 19.0 + 2.000 n`, and on that basis calls the curriculum's `~1,000–3,000
core-min` estimate **4–23× high**. **A two-point fit of an unsteady solver is an
extrapolation, not a law**, and this item spends against it, so it tests it.

**Registered before any measurement:** the fit **HELD** if every uncontended
`compute_totals` wall — S4's six runs at `n = 20, 40, 80` and S5's at `n = W` — lies within
**± 20 %** of `19.0 + 2.000 n`. Otherwise the fit is **REFUTED**, the measured coefficients
are reported, and D12's price is restated from them. **S4 and S5 are run SERIALLY and
uncontended for exactly this reason**; any stage run concurrently with another container is
marked `contended=1` in the ledger and is **excluded from the fit test** while still
counting in full toward cost.

## 7. WHAT THIS ITEM WILL NOT ESTABLISH — written before it runs

1. Nothing at any `np > 1`. Every number is np=1 and no FD reference is carried across np.
2. Nothing about `reduceIO: False`.
3. Nothing about forward-AD or complex-step as a gradient reference under
   `DAFoamBuilderUnsteady` (§G12R-6).
4. Nothing about mesh convergence. **This item produces NO grid family, so `CLAUDE.md`
   rule 5 (Roache triple gating) has no row to gate here, and no GCI is quoted.** The
   2,450-cell mesh is the tutorial's and its adequacy is untested.
5. Nothing about the physical accuracy of `CD` against experiment. Re_D = 1.0e6 on a
   2,450-cell 2D URANS mesh with wall functions is **not** a validated drag prediction, and
   no number from this item is to be quoted as one.
6. Nothing about the endpoint gradient of the optimisation as a **gate** (§G12R-11).

## 8. The ten-line form

1. **Claim:** the DAFoam unsteady adjoint of a time-averaged objective on the 2D cylinder
   agrees with central finite differences at a step proved to lie in a plateau, on a noise
   floor measured before the step was sized — and a gradient so verified reduces
   time-averaged drag.
2. **Gates:** G12R-0 … G12R-11 above, thresholds as tabled.
3. **Trivial baseline:** the same probe at `10 · h*`, predicted `> 5 %` (G12R-7).
4. **Planted zero:** three readers, three plants, read back from disk, REFUSE on blindness
   (G12R-9).
5. **Completion:** rule 4 in full as far as this instrument carries it, plus the
   JSON-vs-log agreement clause (G12R-0).
6. **Cost:** 250.4 core-min predicted (340.4 with contingency); **cap 600.0**; S8 sub-cap
   350.0; `MemAvailable` floor **14.0 GiB**.
7. **Toolchain:** two rows, digests and IDWarp md5s in §2.1, read in-container at run time.
8. **Decomposition:** np=1, `numberOfSubdomains 1`, not applicable and stated.
9. **Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady/` —
   **does not exist at this commit.**
10. **Nothing is filed, sent or posted. `NOT FILED` applies to every artifact this item
    produces that names anything upstream.**

---

## AMENDMENT 1 — 2026-08-25 — **THIS DOCUMENT IS COMMITTED AS RECOVERED, NOT AS AN ARMED FREEZE**

**Version 1.0 → 1.1.**
**lines whose number changed above this section: 0.**

Appended at the foot by a second dafoam `lab-lane`; **nothing above is edited, struck or
reinterpreted, and NO GATE, THRESHOLD, CAP OR LABEL MOVES.** Made **before first compute** —
the condition and how it was checked are in §A1.3.

### A1.1 — WHY THIS AMENDMENT EXISTS

The lane that wrote this document was killed by a session limit at ~20:45Z, mid-sentence. Its
work was recovered and is committed so it is not lost. **But this document must not be read as
a rule-2 freeze, because §4 names FOUR instruments and TWO OF THEM DO NOT EXIST:**

- **`d12r_series.py` — ABSENT.** Survivable: `d12r_grade.py` carries its own series reader inline
  and contains no reference to it.
- **`d12r_stage_and_run.sh` — ABSENT. This is the launcher. There is nothing to run.**

Neither was ever committed to any branch (`git log --all` on both paths returns nothing) and
neither is anywhere on this filesystem (`find /home/ubuntu -name 'd12r_*'` returns only the two
files that exist). **Every clause §4 asserts about the launcher — the `CAP_CORE_MIN` assertion,
the in-container md5 verification against HEAD blobs, the `MemAvailable` read, the FIELD_B
manifest — is a claim about a file that does not exist.**

**A freeze's entire evidentiary content is that it proves the gate could not have been chosen to
fit the answer.** Freezing this document against a half-absent instrument set would prove
nothing about the missing half, and would make the supervisor's non-delegable check — *the
pre-registration is committed before compute* — certify a document rather than an armed item.

> **STATUS: `PENDING`. D12-proper has NOT RUN and CANNOT RUN until the launcher exists.**
> **ZERO core-minutes have been spent against this pre-registration.**

### A1.2 — WHAT WAS REPAIRED IN `d12r_grade.py`, AND WHAT WAS NOT

As recovered, `d12r_grade.py --selftest` **exited 1**, with **2 of 38 units failing**. A mutation
battery then found a third gap. **In all three cases the gate logic was RIGHT and the TEST was
wrong.** Three repairs were made — **all to test fixtures, NONE to a gate, threshold, cap, band
or label**:

1. **`U-06`** used `W = 2` on a period-2 series, so `W` was an exact multiple of the period and
   every block average was identical: `δ_window = 0` **by construction**. Now `W = 3`. **New unit
   `U-06c` locks the zero-spread case in as expected behaviour, because it is a real hazard for
   this item: if `W = 300` is a multiple of the measured shedding period, `δ_window` collapses to
   zero and G12R-4's `h_min` collapses with it.**
2. **`U-09c`** asserted the CONDITIONAL band from a 30 % **per-component** error, but this gate's
   statistic is the **vector-relative** error, which for that vector is 20.02 % — the FAIL band.
   **That fixture bug is exactly the confusion `DAFOAM_CHARTER.md` §2 forbids.** Now `3.0·1.1`,
   a 7.526 % aggregate genuinely inside (5 %, 15 %].
3. **`U-09s2`, NEW.** A mutation test found that **deleting the sign-flip override from
   `g6_bright_line` entirely left the whole selftest passing.** `U-09s` could not catch it: its
   aggregate is 160 %, so the aggregate alone condemns the vector and the override is never
   load-bearing. The new unit uses an aggregate of **0.1414 %** — inside the PASS band — with one
   flipped component, so **only the override can condemn it.**

**After repair: selftest exit 0, 40 units, 0 failures; 6 of 6 mutants caught** (PASS band, FAIL
threshold, sign-flip override, `h_max`, noise target, harness floor). `check_grader_self_blindness.py`
clean — **which is not a proof of correctness and is not offered as one.**

**NOT REPAIRED, and left for the supervisor because they are not a lane's to change** (rule 9):

- **G12R-4's `δ_eff` may not see the floor that actually matters.** `δ_eff = max(δ_repeat,
  δ_window)`; both terms come from **unperturbed** runs. Arm **D12-F′** measured, hours before
  this amendment, a **perturbation-response floor of ≈ 1.65e-06 absolute (1.8e-05 relative)** on
  shape component 3 against a `δ_repeat` of **exactly `0.000000e+00`** — three-plus orders apart,
  component-dependent, shown **model-free**. **Recommended: `δ_eff := max(δ_repeat, δ_window,
  δ_pert)`, which can only raise `h_min` and can only make the `NOT A RESULT` branch easier to
  fire.** Evidence: `cases/dafoam/probes/curriculum_D12_unsteady_probe_Fprime/RESULTS.md`.
- **G12R-0 does not carry two limbs of `CLAUDE.md` rule 4** — the **age guard** and
  **`ExecutionTime` count == `endTime`**. Every input G12R-0 reads comes from the manifest the
  **launcher** writes, so this repair and the missing launcher are one piece of work.

### A1.3 — THE CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady/` DOES NOT
> EXIST.**

**`test -e` on that exact path returned false at 2026-08-25T21:11Z**, and no container has been
started for this item by anyone since: `docker ps` was empty of DAFoam containers throughout,
and the only containers this lane launched were the two probe FD arms, whose run roots are
`…/CURRICULUM-PROBES-D10-D11-D12/D10F` and `…/D12F`. **So amendments to this document remain
legal, and §A1.2's repairs are within rule 2.**

### A1.4 — WHAT MUST HAPPEN BEFORE THIS DOCUMENT IS FROZEN AS AN ARMED ITEM

1. `d12r_stage_and_run.sh` is authored — **the supervisor's call as to by whom.**
2. §4's instrument table is made to match what exists.
3. The `δ_pert` and rule-4-limb rulings in §A1.2 are taken.
4. The document is then re-frozen as **v1.2**, and only then may a container start.

**The full state, with the evidence for every claim above, is in
`INSTRUMENT_STATE_AND_DEFECTS.md` in this directory.**

**NOT FILED. Nothing in this amendment was sent, uploaded, registered, posted or commented.**
