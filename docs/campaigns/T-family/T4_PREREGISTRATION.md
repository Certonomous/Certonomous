# T4 — impinging round jet, H/D = 2, Re = 23 000: pre-registration (FROZEN)

**FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN.** Campaign T, rung **T4**, the
first rung of H-5's tier-completion order and the rung H-5 names *"the
band-containment flagship"*. Verdict vocabulary fixed by `CLAUDE.md` rule 1 and
`VERIFICATION_CHARTER.md` §2: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.**

**Condition at freeze, and how it was checked** (`CLAUDE.md` rule 2, the
pre-compute amendment clause). The registered run tree is
`verification/runs/T-family/T4_runs/`. At the moment this file is committed that
tree holds **exactly five instruments** — `build_t4.py`, `analyse_t4.py`,
`mark_done_t4.py`, `run_one_t4.sh`, `launch_t4.sh` — and **no case directory of
any kind**: `T4_IJ_c`, `T4_IJ_m` and `T4_IJ_f` **do not exist**, no `0/`, no
`0.orig/`, no time directory, no mesh, no `log.solve`, no `STATUS` file and no
`DONE` marker. **Zero core-minutes have been spent on this rung.** Every ruling
below is therefore a **pre-compute** amendment and legal; after the first solver
starts, nothing in §1–§13 may move except by dated addendum that cannot alter a
gate, threshold, cap or label.

**Disclosure — a dry run of the mesh specification, and it found two defects.**
Before this file was frozen, `build_t4.py` was executed against a **scratch root
outside the repository** and `blockMesh`/`checkMesh` were run there, to establish
that §5's block decomposition is realisable. That dry run wrote nothing into the
repository, involved no solver and cost no core-minutes. It is disclosed because
it **changed this document**: the first version of the mesh emitted two distinct
vertices on the axis (both at `z = 0`), and `checkMesh` returned
`Zero or negative face area detected. Minimum area: 0` with
`Max skewness = 2.4e+145` — a divide-by-zero, not a mesh; and `grading_ratio()`
answered an infeasible first-cell request by silently returning `1.0`. Both are
repaired in the frozen `build_t4.py` (the axis is now a **collapsed edge**, and
the grading solver **raises** rather than returning a plausible wrong number),
and the three registered meshes now build with `blockMesh` rc 0, `checkMesh`
rc 0, max skewness **0.3308**, max non-orthogonality **0**. **Freezing a
document against an unrealisable mesh is the failure this dry run exists to
prevent** (the precedent and its wording are T8's).

---

## 1. The case

A normally-impinging round air jet from a **fully developed pipe**, striking a
flat plate at nozzle-to-plate spacing **H/D = 2**, at **Re_D = 23 000**.

| quantity | value |
|---|---|
| `D` (nozzle diameter) | 0.02 m |
| `H/D` | 2 |
| target radius `R/D` | 6 |
| pipe length upstream of the nozzle exit | 10 `D`, with a **recycling inlet** (§3) |
| `ν` | 1.5e-05 m²/s |
| `U_bulk` = `Re·ν/D` | 17.25 m/s |
| `Pr` / `Pr_t` | 0.71 / 0.85 |
| plate thermal condition | **constant heat flux**, 1000 W/m² (Baughn's configuration) |
| jet temperature | 293.15 K |

This is the DC-cooling **impingement** physic: the H-2 spine carries separated
thermal (T3), rack (T5), aisle (T8) and room (T12); T4 carries the local
high-`Nu` impingement that every direct-to-chip and rack-door cooler depends on.

---

## 2. THE PRIMARY SOURCES, STATED HONESTLY

**Rule 15 governs: verification is by title page, never by filename or hash.**
Absences below were established with a **positive control on the same reader in
the same invocation** — the same search that returns **0** for `baughn`,
`shimizu` and `cooper` returns **1** for `meinders`, a paper known to be held.
A zero from a reader not shown able to see a non-zero is not evidence.

| source | what it would referee | status on disk |
|---|---|---|
| **Baughn & Shimizu (1989); Baughn et al. (1992)** — the `Nu(r/D)` data | local `Nu`, incl. `Nu_stag` | **NOT OBTAINED.** ASME/IJHMT, closed. Zero hits repo-wide. |
| **Cooper, Jackson, Launder & Liao (IJHMT 36, 1993)** — the flow field | mean and fluctuating velocity | **NOT OBTAINED.** Closed. Zero hits repo-wide. |
| **ERCOFTAC Classic Collection case025**, `ij2lr` family | both, as digitised tables | **HELD**, `docs/campaigns/T-family/reference-data/ercoftac_case025/`, retrieved 2026-08-21, bulk archive sha256 `6d324a86…f0d8`, site licence CC BY-NC-SA 4.0, provenance in `PROVENANCE.md`. |
| **Martin correlation**, via NREL/TP-540-38787 (Narumanchi, Hassani & Bharathan, Dec 2005) | **area-averaged** `Nu` | **HELD, OPEN, title-page verified** — the sidecar's title page reads *"Modeling Single-Phase and Boiling Liquid Jet Impingement Cooling in Power Electronics, NREL/TP-540-38787, December 2005"*. Correlation at §2.1.1 eq (2.1). |

### 2.1 The consequence, and it is a real constraint

**No graded row in this rung is a `Nu` row.** The ERCOFTAC page states an
uncertainty for the **flow field** verbatim — *"mean velocity within ±2 percent
of bulk; u' ±4, v' ±6, uv about ±9 percent except near impingement"* — and
states **none at all** for its four Nusselt files. The only `Nu` uncertainty
available is a **second-hand 2.4 %** attributed to Baughn & Shimizu by the
ERCOFTAC KB Wiki, unverified against a closed primary. **A band armed on a
second-hand uncertainty is not a band**, so the `Nu` rows are **REPORT-ONLY**
(§8) and their gradeable status is **BLOCKED** pending the closed primaries.

**A correction to `T_FAMILY_INDEX.md`, recorded here rather than smoothed.** The
index's T4 row says the Martin correlation arrives "with stated validity from an
open NREL report", which is **true**, and this lane's first reading of the
sidecar wrongly concluded it was absent. It is present, 16 whole-word hits, and
its stated validity is `2 000 ≤ Re_J ≤ 400 000`, `2.5 ≤ R/d ≤ 7.5`,
`2 ≤ S_NP/d ≤ 12`. **This configuration is inside all three**, with `S_NP/d = 2`
sitting exactly at the lower limit — recorded because a referent used at the edge
of its range is used at the edge of its range. Martin refereeing is nonetheless
**REPORT-ONLY**, for a reason independent of validity: `Nu = h_avg·d/k` is an
**area average over the target**, so it cannot referee a local `Nu(r/D)` and
cannot referee `Nu_stag` at all.

---

## 3. Solver, closure, and the registered modelling choices

| choice | value | why, registered before the run |
|---|---|---|
| solver | `buoyantBoussinesqSimpleFoam` | with `beta = 0` the temperature field is **passive**, so this is pure forced convection. Same convention T1b uses (`beta 0` in its `transportProperties`), which means the family's tested field set, launcher form and completion rule apply unchanged. |
| closure | **`kOmegaSST`** | the registered closure, and **the rung's subject**: the stagnation-point anomaly of linear eddy-viscosity models is what §10's prediction P1 is about. |
| formulation | steady, axisymmetric **wedge**, 2.5° half-angle | the case is statistically axisymmetric; a wedge is the cheapest faithful discretisation. |
| nozzle-exit condition | **recycling (`mapped`) inlet**, sampling 5 `D` upstream, on `U`, `k` and `omega` | the experiment specifies a *fully developed* pipe exit. A uniform inlet over 10–20 `D` does **not** reach full development at this `Re`, so imposing one would quietly make the inlet profile a free parameter. Recycling makes development a property of the solution rather than an assumption, and **C2 checks it** (§9). |
| wall treatment | **wall-resolved on every level**, `y+ < 1` | a family that switches to a wall function between levels breaks the smooth-refinement assumption the GCI rests on. C1 enforces it (§9). |

---

## 4. THE GRADED ROWS, AND WHERE EACH BAND COMES FROM

Three rows. All three are **mean-velocity** quantities, because the mean
velocity is the only quantity in this case with a **first-hand stated
uncertainty**.

| row | quantity | reference file | reference value | **registered band** |
|---|---|---|---|---|
| **G1** | peak wall-jet mean velocity `U_max/U_bulk` at `r/D = 1.0` | `ij2lr-10-sw-mu.dat` | **1.0890** | **[1.0690, 1.1090]** |
| **G2** | same at `r/D = 2.0` | `ij2lr-20-sw-mu.dat` | **0.7888** | **[0.7688, 0.8088]** |
| **G3** | same at `r/D = 3.0` | `ij2lr-30-sw-mu.dat` | **0.4632** | **[0.4432, 0.4832]** |

**Band derivation, and it is the whole of it.** The ERCOFTAC case page states
the mean-velocity uncertainty as *"within ±2 percent of bulk"*. That is an
**absolute** statement in bulk-velocity units, not a relative one: the band is
`±0.02` in `U/U_bulk`, identically at every station. It is therefore **wider in
relative terms as the wall jet decays** — ±1.8 % at G1, ±2.5 % at G2, ±4.3 % at
G3 — and that asymmetry is a property of the experiment's own stated uncertainty,
not a choice made here. **The alternative reading (±2 % relative to the local
value) is rejected** because the page says "of bulk"; it is recorded so that the
reading can be overturned rather than re-derived.

**What a PASS here is and is not.** A PASS is a **joint code-plus-closure
statement**: it says this solver with `kOmegaSST` on this mesh family reproduces
the measured wall-jet peak within the experiment's stated uncertainty. **It is
NOT a code-verification claim** and may not be cited as one.

---

## 5. THE MESH FAMILY — three levels, exactly r = 2

Sanaa's standing grid ruling: a converging three-level family with observed order
and GCI is the gate standard; more levels are a research option, never a gate
requirement. **Three levels.**

One parameter `N` sets every division, so the family is **geometrically similar
under h → h/2** rather than merely having more cells; the near-wall first-cell
height halves with `N` as well.

| level | `N` | **cells** | first cell at the plate | `endTime` (iterations) | est. `y+` at the plate |
|---|---|---|---|---|---|
| `T4_IJ_c` | 48 | **5 184** | 2.4e-05 m | 20 000 | ≈ 0.75 |
| `T4_IJ_m` | 96 | **20 736** | 1.2e-05 m | 30 000 | ≈ 0.38 |
| `T4_IJ_f` | 192 | **82 944** | 6.0e-06 m | 40 000 | ≈ 0.19 |

Cells are exactly `2.25 N²`, so **`r21 = r32 = 2` exactly**, in every direction,
by construction rather than by measurement. The `y+` column is an **estimate at
`u_τ ≈ 0.94 m/s`, not a measurement**; C1 measures it from the run and refuses
if any level exceeds 1.0.

**Measured at freeze, on the scratch dry run:** `blockMesh` rc 0 and `checkMesh`
rc 0 at all three levels; max skewness **0.3308** and max non-orthogonality
**0** identically at all three (the equality across levels is itself the
geometric-similarity check); max aspect ratio 1626 / 1639 / 1645, which is
near-wall clustering on a wall-resolved mesh and is disclosed rather than hidden.

---

## 6. Ranks and concurrency

**`ranks = 1` for every level. Three levels run CONCURRENTLY, 3 cores total.**
Serial per case removes decomposition, `reconstructPar` and processor
directories from the completion rule's surface. The three are independent and
are launched together by `launch_t4.sh` under `setsid`, so a fleet kill — a usage
limit terminates every agent at once — does not take the solvers with it.

---

## 7. THE GATE — `CLAUDE.md` rule 5, in its fixed order

Implemented in `analyse_t4.py`, in `apply_gate()`, which is **the only function
in that file that writes a verdict**:

1. **any level not iteratively converged or not plateaued → `NOT A RESULT`**;
2. **triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → `NOT A RESULT`**,
   with the value, the triple and the state printed beside it;
3. only then is the band consulted: inside → **`PASS`**, outside → **`GATE
   FAIL`**, GCI printed.

**GCI at `Fs = 1.25`.** An observed order is never quoted for a non-monotone
triple, and a GCI is never quoted where no order exists. **The gate can only turn
a PASS or GATE FAIL *into* NOT A RESULT, never the reverse** — enforced
structurally, since step (1) and step (2) return before the band is read.

**Every refusal is `sys.exit(2)`. There is no `assert` statement in any of the
five instruments** — verified by **AST**, not by grep, and under a planted
positive control: the same checker that reports 0 real `assert` statements
reports 1 when a real `assert` is appended. `assert` is stripped by `python -O`,
and a gate a flag can remove is not a gate.

**The Richardson sign convention is stated because this lab has a live defect in
it.** `analyse_t3.py:384` and `analyse_t1c.py:337` both compute
`richardson = f_fine + e21/den` where the correct form is `f_fine - e21/den`.
`analyse_t4.py` uses the **correct** form, and the extrapolate is **REPORTED and
never gated on**, so the defect could not become load-bearing here even if the
sign were wrong.

---

## 8. REPORT-ONLY ROWS — recorded, never graded

| row | quantity | referent | why it is not graded |
|---|---|---|---|
| **R1** | `Nu_stag` (local, `r/D = 0`) | Baughn via ERCOFTAC: `Nu/Re^0.7 = 0.1223` → **`Nu = 138.24`** | no first-hand uncertainty (§2.1); and §11 forbids banding it |
| **R2** | secondary `Nu` peak at `r/D ≈ 2` | the reference exhibits a minimum at `r/D = 1.26` (`Nu` 87.6) and a secondary maximum at `r/D = 1.94` (`Nu` 106.4) | a binary shape claim, not a value with a band |
| **R3** | area-averaged `Nu` over `r/D ≤ 6` | **Martin**, evaluated for this exact configuration: `G = 0.145833`, `F = 455.267`, **`Nu_avg = 57.50`** | area-averaged, cannot referee a local value; and it is a correlation, not data |
| **R4** | peak `u'/U_bulk` at `r/D = 1.0` | 0.14004 | recovering `u'` from `k` needs the **isotropy assumption** `u' = √(2k/3)`, which is known to be poor in a wall jet. Grading a row whose comparison rests on an assumption the closure does not make would be a closure claim wearing a verification label. |
| **R5** | `y/D` of the wall-jet peak at `r/D = 1.0`, 2.0 | 0.01884, 0.02593 | the page states no uncertainty on `y/D` |

**Recorded now, before the run:** Martin's `Nu_avg = 57.50` and an area-average
of the Baughn local data over `r/D ≤ 5.05` (`Nu_avg ≈ 70.7`) **differ by ~19 %**.
The averaging radii differ, which explains part of it and not obviously all.
**Two referents that disagree by 19 % before any solve is a fact about the
referents**, and it is registered here so that a computed value landing between
them cannot later be presented as agreeing with both.

---

## 9. CONTROLS — every one MET, or the rung does not grade

| id | control | refusal |
|---|---|---|
| **C1** | `y+_max` at the plate **< 1.0 on all three levels** | a level in the buffer layer breaks systematic refinement → `NOT A RESULT` |
| **C2** | nozzle-exit `U_c/U_bulk` within **±3 %** of the 1/7-power-law value **1.2245** | the recycling inlet did not develop → `NOT A RESULT` |
| **C3** | global mass conservation, `|ṁ_in − ṁ_out|/ṁ_in < 1e-3` | not a converged solution |
| **C4** | **planted-zero control (rule 3), BOTH ARMS** | see §9.1 — `exit 2` |
| **C5** | **strict completion rule with the age guard (rule 4)**, all three levels | see §9.2 — `NOT DONE` |
| **C6** | **three-part convergence** on every level: C1 sustained residual floor **AND** C2 not growing **AND** C3 graded-quantity field change `<= 2.0e-04` | see §9.4 — this is gate (1) of §7 |

### 9.1 The planted-zero control — `CLAUDE.md` rule 3

`analyse_t4.py:planted_zero_control()`. **Both arms run and both must give their
registered answer, or the comparator refuses.**

- **`PLANT` = `1.234e-03` m/s** — the same constant `analyse_t3.py:81` uses.
- **Planted by LINE INDEX, never by value match.** A value-matching plant can
  silently fail to land and then report success having done nothing.
- **Copy, never touch.** The control copies the case to scratch and **refuses**
  if the copy resolves inside the case tree. It never writes into a case
  directory and never near a running solver.
- **Read back through the production reader** — the same `sample_profile()` that
  produces the graded number, not a reimplementation. A reimplemented reader
  tests the reimplementation.
- **POSITIVE ARM:** the reader must SEE the plant. If it returns exactly zero →
  **REFUSE**: the reader is blind and every zero it has produced for this rung is
  worthless.
- **NEGATIVE ARM:** the reader must return **exactly `0.0`** on identical bytes.
  If it returns anything else → **REFUSE**: the reader is noisy and its zeros are
  not zeros. A reader that always reports a difference passes the positive arm
  while being just as useless.

### 9.1a THE DEMONSTRATED DETECTION FLOOR — the control measures its own sensitivity

**A max-norm change gate has a detection floor equal to its own current
`dmax`, and that floor rises exactly as the case gets worse.** Measured on T8: a
registered plant of `1.234e-03` was **invisible**, `1.5e-01` was **invisible**,
and only `1.0` moved the gate — because `dmax` was `1.012e-01`, **82× the
plant**. A control of that shape passes while seeing nothing, on precisely the
runs where it matters most.

**So this control does not assert its sensitivity, it measures it.** A
descending ladder of plant magnitudes — `1.0, 1e-1, 1e-2, 1.234e-03, 1e-4,
1e-5, 1e-6` — is driven through the same production reader, and **the smallest
magnitude the reader still resolves is recorded as the demonstrated detection
floor** and written into `gate_t4.json`. **If the registered `PLANT` sits at or
below that floor the control REFUSES**, naming the magnitude that *was* visible,
rather than passing on a plant the reader could not have seen.

**And the plant is AIMED.** The reader is a line sample at one radial station;
a plant dropped into an arbitrary cell is nowhere near that line, the reader
returns exactly zero, and the control condemns a sound reader. The aim is
recovered from the mesh's **own cell centres written to disk** by
`writeCellCentres`, the nearest cell to the sampled peak is chosen, and **the
chosen cell's distance to the sampling line is reported**. The safety property
is the asymmetry: **a mis-aimed plant can only make the positive arm FAIL, never
pass falsely.**

### 9.4 CONVERGENCE — a residual is not convergence

**Measured on T8:** the fine level's `T` initial residual reached **5.932e-07
against a registered `1e-6`** — a pass on residuals alone — while the
temperature field was **still moving 0.101 K between checkpoints, wrong by
16 400×**. A residual measures how well the current linear system was solved,
not whether the solution has stopped moving.

The registered criterion is therefore three-part, and all three must hold:

| | criterion | value |
|---|---|---|
| **C1** | sustained residual floor: the last **200** `p_rgh` initial residuals | `<= 1.0e-06` |
| **C2** | **not growing** — the residual is not trending upward | directional |
| **C3** | **field change**: the graded quantity's movement between the **last two written checkpoints** | `<= 2.0e-04` in `U/U_bulk` |

**C2 is directional deliberately.** The form used is this territory's own —
`analyse_e4a2.py:300`'s *"C2 not growing"*, implemented at `:308` as
`c2 = not cl["growing"]` — and **not** a trend-divided-by-spread form, which
admits a run that never converged at all (measured: T8's coarse level passes
one).

**C3's tolerance is tied to the band, not chosen freely:** `2.0e-04` is **1 % of
the band half-width** (0.02), so the graded quantity must be stationary to well
inside the interval it is graded against.

### 9.2 The strict completion rule — `CLAUDE.md` rule 4

`mark_done_t4.py`, all-or-nothing: `rc = 0`; an `End` line; last time ==
`endTime`; fields `T U p_rgh alphat nut k omega` present; `ExecutionTime` count
== `endTime`; and **every field at `endTime` NEWER than the case's own `0/T`** —
the age guard, because `run_one_t4.sh` touches `0/T` **last** at launch and so
dates the run allowed to produce the answer. `run_one_t4.sh` **refuses to launch**
a case in which `0/` or any numeric time directory already exists.

**AN ABSENT `STATUS` FILE IS `NOT DONE`, NEVER AN INFERENCE.** This is the
consumer side of the defect that made K0d's L1 pair `NOT DONE` permanently: its
launcher started the solver and never captured an exit status, and the right
answer was to refuse rather than to read `rc = 0` off an `End` line. An `End`
line is what `rc = 0` normally accompanies; it is not the measurement the clause
requires.

### 9.3 THE `capped` WITNESS — why `rc` alone is not enough, measured

Measured on this box, GNU coreutils 9.4, 2026-08-26:

| condition | wrapper `rc` |
|---|---|
| child exits 0 | 0 |
| child exits 7 | 7 (crash, passed through) |
| child takes SIGFPE | 136 (crash, passed through) |
| wall-clock expiry, default | **124** |
| expiry with `--kill-after`, TERM ignored | **137** |
| **child genuinely exits 124** | **124 — collides with expiry** |

and **137 is also what the OOM killer produces**. So `rc` alone cannot separate a
**cap-stop** (rule 12: the run stops, `NOT A RESULT`) from a **crash** (a
finding, needing triage) from an **OOM kill**. `run_one_t4.sh` therefore records
an **independent expiry witness** — `capped`, derived from measured `wall_s`
against the registered `timeout_s` — and `mark_done_t4.py` decides from the
witness. **A `STATUS` file carrying no `capped` field is itself a refusal**: it
was not written by the registered launcher.

**`run_one_t4.sh` exits with the solver's own `rc`, never `0`.**
`run_one_t8.sh` ends `exit 0`, so a queue driver chaining on `&&` marches
straight past a SIGFPE that killed the solve. The `STATUS` file records the
truth either way, but a launcher that reports success to its own caller has
merely moved the defect one level up.

All six paths were exercised against a synthetic case before this freeze,
including the one that matters: the **same `rc = 124`** yields **CAPPED** when
`wall_s ≥ timeout_s` and **CRASH** when it is below.

---

## 10. THE PREDICTIONS — registered before any compute, and scored afterwards

**P1. `kOmegaSST` will OVER-predict `Nu_stag`, by between +10 % and +60 %** of
the Baughn datum `Nu = 138.24` — i.e. the computed fine-level `Nu_stag` lands in
**[152.1, 221.2]**. The stagnation-point anomaly of linear eddy-viscosity models
is documented; this registers its **direction and a magnitude bracket** in
advance. **A value outside that bracket in EITHER direction scores the prediction
WRONG, and it is recorded as wrong** — including the comfortable case where the
model does better than predicted.

**P2. `kOmegaSST` will NOT reproduce the secondary `Nu` peak.** Judged as a
binary on the computed `Nu(r/D)`: a local minimum followed by a local maximum
within `r/D ∈ [1.0, 2.6]`. The reference has both.

**P3. G1–G3 will PASS.** Registered *because* it is the comfortable answer. If
they do not, that is the more valuable outcome and is recorded as such — **not
re-run until it agrees, not weakened, and not attributed to the instrument.**

**P4. The three triples will be CONVERGING.** Registered so that a
`NOT A RESULT` on gate (2) is a scored failure of this prediction and not an
unremarkable outcome.

---

## 11. THE §2e RULING — WHY NO EIGENSPACE BAND IS ARMED ON THIS RUNG

H-5 sharpens T4 with the shelf-D finding and asks *whether eigenspace bands
contain the documented stagnation-`Nu` bias*. **They may not be armed here, on
two independent grounds, both established before any compute, in
`VERIFICATION_CHARTER.md` §2e's own terms.**

**Ground 1 — the quantity's class.** §2e requires each banded row to be
classified **SHAPE** or **FORCING/production**, and draws a bright line: *"an
envelope that perturbs eigenvalues only never perturbs `k` magnitude and may not
be used to band a quantity that depends on `k` magnitude."* **`Nu_stag` is
hereby classified FORCING-class**, as `T_FAMILY_INDEX.md` requires it to be. The
documented stagnation-point anomaly *is* an over-production of `k` **magnitude**
under normal strain — not a misprediction of Reynolds-stress **shape**. L-220
gives the construction reason: *"Emory's eq. (4) keeps `k` outside the bracket,
so magnitude is untouched by construction."* **The envelope cannot move the
quantity, so it cannot bound it.** This is a matter of the envelope's
construction, not of degree, and no amount of `delta_B` repairs it.

**Ground 2 — the containment fraction is not transferable.** §2e also requires
the pre-registration to **cite the measured containment fraction for that
class**. The lab's measured forcing-class fractions — **0.9279 to 0.9433** — were
measured on **five hills and a curved step**; the shape fractions on **ducts**.
L-219: *"An uncertainty magnitude is a calibration, and it inherits the flow
class it was calibrated on."* **A normally-impinging round jet is neither a 2-D
separated flow nor a duct.** No containment fraction has been measured on this
box for this flow class, so §2e's citation requirement **cannot be satisfied**,
and citing the hill figure would be exactly the error L-219 names.

**Registered consequence: T4 arms NO eigenspace band on any row.** `Nu_stag`
stays REPORT-ONLY (§8 R1). **H-5's flagship question is answered here in the
negative, before compute and at zero cost, rather than after a solve** — and the
falsifiable content that replaces it is §10's P1, which registers the bias's
direction and magnitude bracket without pretending to bound it.

**What would unblock it, stated so this is a finding and not a refusal:** a
measured per-cell containment fraction for the impinging-jet class, on the
forcing term `P_k = −R_ij ∂U_i/∂x_j` as well as on `b` — L-220's requirement that
the two be reported separately *"and expect them to fail on different cases"*.
That is a separate rung with its own pre-registration and its own cost.

---

## 12. COST — `CLAUDE.md` rule 12

**Rate basis, and the hazard is named.** The rate is **measured on this box
tonight**, from T1b L4's three live arms: 209 920 cells, `ranks = 1`,
`buoyantBoussinesqSimpleFoam`, giving **1.135e-05 to 2.193e-05 core-s per
cell-iteration** across the three arms (the spread is the `p_rgh` solver
iteration count, which varies with `Re`). **POINT = 1.55e-05** (the middle arm),
**CEILING = 2.20e-05** (the slowest).

**T8's R6 hazard was checked and does not apply:** that rung's rate was borrowed
from a **transient PIMPLE** case for a **steady SIMPLE** run, and per-step cost
differs between solver modes. Here the basis and the target are both **steady
SIMPLE `buoyantBoussinesqSimpleFoam`, same box, same rank count**. The remaining
transfer risk is the `p_rgh` iteration count on a different geometry, and the
CEILING is what covers it.

| level | cells | iterations | **POINT core-min** | CEILING core-min | **cap (core-min)** | `timeout` (s) |
|---|---:|---:|---:|---:|---:|---:|
| `T4_IJ_c` | 5 184 | 20 000 | 26.78 | 38.02 | **50** | 3 000 |
| `T4_IJ_m` | 20 736 | 30 000 | 160.70 | 228.10 | **300** | 18 000 |
| `T4_IJ_f` | 82 944 | 40 000 | 857.09 | 1 216.51 | **1 600** | 96 000 |
| **total** | | | **1 044.58** | **1 482.62** | **1 950** | |

**POINT 1 044.58 core-min = 17.41 core-h = $0.8931.
CEILING 1 482.62 core-min = 24.71 core-h = $1.2676.
CAP 1 950 core-min = 32.50 core-h = $1.6672.**
Priced at **$0.0513/core-h, c7a.4xlarge, reported-by-owner (2026-08-21/22), not
measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md`
§5). **Every dollar figure here is DERIVED, NOT MEASURED.** Inside Sanaa's
standing under-$25 pre-authorisation.

### 12.1 The cap is a runaway guard, and that is a deliberate choice

`timeout = cap_core_min × 60 ÷ ranks`, coded that way in `run_one_t4.sh`, so a
later parallel level cannot inherit a silent factor-of-ranks overrun. At the cap
the solver is killed, `capped=yes` lands in `STATUS`, and `mark_done_t4.py`
refuses. **An overrun stops the run; it does not get a new budget. A capped level
is `NOT A RESULT` and is not re-launched with a larger cap.**

**The margin is chosen against a measured lesson.** T1b's `R_10k_x` registered a
cap of 1 100 core-min against a POINT of 1 073.6 — a margin of **2.46 %**. A cap
that close to the estimate is not a runaway guard; it is a coin-flip on the
estimate, and it is why that arm read as at-risk all night when it was in fact
running at 0.79× its POINT. **T4's caps sit at 1.87× POINT and 1.32× CEILING —
an 86.7 % margin.** That is wide enough that a healthy run of any plausible speed
finishes, and tight enough that a genuinely pathological run — a `p_rgh` solve
that stops converging, the failure mode with the most room to run away here — is
stopped rather than left to burn the night.

### 12.2 Calibration at completion is not optional

At rung completion the pre-registered POINT above is compared against actual
core-minutes from `STATUS.T4_IJ_*` (`wall_s × ranks ÷ 60`), stating the ratio
actual/predicted, attributing the gap (contention, waste, misprediction — waste
named separately, never absorbed into the ratio), and landing as a row in
`docs/COST_CALIBRATION.md`. **A completion report without this comparison is
incomplete.**

---

## 13. THE FREEZE SET — the grading path is fixed at this commit

These five files are committed **in the same commit as this document**, so §13's
assertion is true at the moment it binds. Verify the frozen file is the file that
ran by hashing it against its committed blob.

| file | sha256 (first 16) | lines |
|---|---|---|
| `verification/runs/T-family/T4_runs/build_t4.py` | `88e0207c25e0b029` | 434 |
| `verification/runs/T-family/T4_runs/analyse_t4.py` | `9842dbc8146d4f15` | 538 |
| `verification/runs/T-family/T4_runs/mark_done_t4.py` | `be76807821791c37` | 174 |
| `verification/runs/T-family/T4_runs/run_one_t4.sh` | `6db90ff2753e5c2d` | 137 |
| `verification/runs/T-family/T4_runs/launch_t4.sh` | `19514e54dcfc3615` | 33 |

The reference data is **not** in the freeze set and is not modified by this
rung; it is cited by path and by the archive sha256 in §2.

---

## 14. What this document does not do

- It **does not** modify any frozen file.
- It **does not** authorise a launch. Firing is the supervisor's call.
- It **does not** create, move or retire any gate, threshold, band, cap or label
  outside this rung.
- It **does not** claim a capability. **No rung is a capability until it has
  reported**, and naming a plan as a capability is the error campaign T exists to
  avoid.
- It **does not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7), and
  nothing here has been sent, filed, uploaded, registered or posted outside this
  box.

---

## AMENDMENT 1 — 2026-08-26 — PRE-COMPUTE REPAIR OF A SELF-CONTRADICTORY LAUNCH GUARD

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.**
Nothing above is edited; §§0–14 stand exactly as committed at `248ad27c`.
**No gate, threshold, band, cap or label is created, moved or retired by this
amendment**, and none could be: the defect repaired here governs *whether the
launcher runs at all*, never *what it computes*.

### A1.1 The defect, stated at its full strength

The frozen `run_one_t4.sh` carried, two lines apart:

- **:62** `for d in "$CDIR"/[0-9]*; do [ -d "$d" ] && die "...already has time directory..."`
- **:65** `[ -d "$CDIR/0.orig" ] || die "...has no 0.orig to arm from"`

`[0-9]*` is a **shell glob**, and it matches **both** `0` and `0.orig`. So on a
freshly built case :62 died on `0.orig`, calling it a time directory — while
:65, never reached, **requires that same `0.orig` to exist.**

> **Two adjacent guard lines imposed contradictory requirements on the same
> directory: :62 refused the exact state :65 demanded. The launcher could not
> pass its own guard on any case its own builder produced.**

That is the statement worth recording, and it is stronger than "a glob matched
`0.orig`". The failure was **fail-safe** — it refused rather than corrupting —
and it was found before any solver started.

### A1.2 Why a pre-compute amendment and not a re-registration

1. **The freeze binds at the first GRADED SOLVE, not at the first process.**
   `VERIFICATION_CHARTER` §2d.1's operative form is *"a change on the grading
   path made after the first graded solve"*. `blockMesh` produces no graded
   value, no completion marker, no `log.solve` and no `STATUS`;
   `check_comparator_freeze.py` compares against the first completion marker,
   and there is none.
2. **The decisive test is that the amendment CANNOT MOVE ANY NUMBER.** The
   launcher refuses every case and has therefore produced no value and can
   produce none. Changing a match idiom changes whether it runs, never what it
   computes.
3. **§2d.1 is NOT invoked, and deliberately so.** The same ruling declined to
   invoke it for T8's `assert`→`exit 2` conversion on the ground that
   *invoking a narrow exception where it is not needed stretches it*.
   Consistency requires the same answer here: this is an ordinary pre-compute
   amendment and needs no exception.
4. **A re-registration would be the mirror error** — retiring a frozen document
   over a one-line idiom that cannot affect a result would teach the lab that
   re-registration is the answer to any defect, and the K0d record shows what
   five amendments that never reach a fixed point cost.

### A1.3 The condition, MEASURED, with an absence control on the reader itself

Measured independently at source by the heat-transfer supervisor, and
re-measured by this lane at **2026-08-26T03:44:21Z** immediately before the
repair landed:

| case | `constant/polyMesh` | `0.orig` | `0` | `log.solve` | `STATUS` | time dirs |
|---|---|---|---|---|---|---|
| `T4_IJ_c` | present | yes | **absent** | **absent** | **absent** | **none** |
| `T4_IJ_m` | present | yes | **absent** | **absent** | **absent** | **none** |
| `T4_IJ_f` | present | yes | **absent** | **absent** | **absent** | **none** |

**THE ABSENCE CONTROL, because a zero from a search not shown able to find a
known instance is not evidence of absence.** Standing rule 3, applied to a file
search rather than a field reader. A `0/` directory was planted into
`T4_IJ_c`, the enumeration re-run and observed to return it, and the plant
removed — **the reader was shown able to see a positive before its zero was
believed.** The supervisor applied the same control independently.

**WHAT DID RUN, stated plainly rather than implying a pristine state.**
`blockMesh` ran on all three levels with **rc 0**, producing **5 184 / 20 736 /
82 944** cells, and `constant/polyMesh/owner` is present on all three. **The
meshes stand and nothing is rebuilt** — `blockMesh` writes `constant/polyMesh`
and never a time directory. **Solver core-minutes spent: zero.**

### A1.4 The repair

Time directories are matched by a **regex-equivalent form with fullmatch
semantics** — `[0-9]+(\.[0-9]+)?` — never a shell glob:

```
find "$CDIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended \
     -regex '.*/[0-9]+(\.[0-9]+)?'
```

`find -regex` anchors the whole path, so `0.orig` cannot match. **Both
directions were driven, not reasoned about:** on the case as built the guard
**passes**; with a `1500/` directory planted it **fires**; with the plant
removed it **passes** again.

**§13 IS NOT REWRITTEN. The original is struck and superseded here** (rule 2:
originals are struck, never rewritten). `run_one_t4.sh`'s entry in §13 read
`6db90ff2753e5c2d`, 137 lines, and is **superseded by `d8549c6e4b662d98`,
150 lines**, at the commit carrying this amendment. The other four
freeze-set entries are unchanged and remain valid.

### A1.5 The third instance makes it a check, not a lesson

This is the **third** recorded instance of one defect class:

1. `THERMAL_K0_runs/run_cases.sh:70` — a `rm -rf [0-9]*` trim written that way
   *"deleted every case's initial conditions"*.
2. `K2e_runs/build_cases.py:76` — the same collision, recorded again.
3. this launcher.

**A defect class that has bitten three times gets an executable check.**
`scripts/check_time_dir_globs.py` is filed with this amendment, as a **shared**
instrument for verification and cfd as well as heat-transfer; no team claims it.

**It MEASURES rather than guesses.** Rather than judging a pattern by its shape,
it drives each glob against `0.orig` and against a real time name with
`fnmatch`, and flags only patterns that match **both**. That distinction is not
cosmetic: the shape heuristic returned **61** hits, tightening `[0-9]+`
(a regex quantifier — shell globs have no `+`) cut it to **17**, and the
measured form returns **8**. `0.[0-9]*`, `[1-9]*` and `[0-9]*.[0-9]*` are
excluded **by measurement**, and each is a selftest case. The selftest carries a
**planted positive control** — the T4 defect verbatim — so the checker's zeros
are evidence.

**Python instruments are already clean** and are not the exposure:
`re.fullmatch(r"[0-9]+(\.[0-9]+)?")` rejects `0.orig`, tested rather than read.
The exposure is shell. Of the 8 measured hits, **7 lie outside this team's
territory** (`F12_runs`, `F6b_runs`) and are **reported, not repaired** — they
belong to cfd, and a lane does not edit another team's instruments.

---

## AMENDMENT 2 — 2026-08-26 — THE NEAR-WALL TREATMENT IS REGISTERED, AND THE BOUNDARY CONDITIONS ARE NOW PART OF THE REGISTRATION

**Version 1.1 → 1.2. Lines whose number changed above this section: 0.**
Nothing above is edited. **No gate, threshold, band, cap or label is created,
moved or retired.**

### A2.1 THE GROUND FOR LEGALITY IS "NOTHING HAS RUN" — AND EXPLICITLY NOT "NOTHING MOVES"

All three arms exited **rc = 1 at ZERO iterations**, 0.034 core-min, no
`Time = 1` on any arm, no time directory, no field written. Rule 2's
**pre-compute** clause applies and the gates are not yet closed. **That is the
whole licence.**

**The "can this amendment move a number?" test is NOT available here, and must
not be borrowed.** `alphat` is the turbulent thermal **diffusivity**, and its
wall treatment **is** the wall heat-transfer model, on a rung whose reported
quantity is a Nusselt-class number. The three amendments authorised earlier
today — T8's `assert`→`exit 2`, T4's AMENDMENT 1 glob idiom, K0f's missing
`etc/bashrc` — were **plumbing**, each provably unable to change a computed
value. **This one is PHYSICS.** Reaching for the same sentence a fourth time,
when the fourth case differs in kind, is how a narrow test becomes a rubber
stamp. **Legal because nothing has run; not legal because nothing moves.**

### A2.2 THE REAL FINDING — the registration had no opinion about the boundary conditions

§3 named the solver; §9.2 registered the completion field set. **Neither said
anything about wall-function types.** That is *why* a `compressible::` wall
function survived into a frozen case: **nothing in the document was capable of
noticing it, and nothing would have noticed the next one.**

**Registered here, per field, per patch. This is a TIGHTENING** — it adds a
refusal channel and removes none.

| field | `plate` | `pipeWall` | `inlet` | `entrainment` / `farfield` |
|---|---|---|---|---|
| `U` | `noSlip` | `noSlip` | `mapped` (recycling) | `pressureInletOutletVelocity` |
| `p_rgh` | `fixedFluxPressure` | `fixedFluxPressure` | `zeroGradient` | `totalPressure`, `p0 = 0` |
| `T` | `fixedGradient`, `q" = 1000 W/m²` | `zeroGradient` | `fixedValue` 293.15 K | `inletOutlet` |
| `k` | **`kLowReWallFunction`** | **`kLowReWallFunction`** | `mapped` | `inletOutlet` |
| `omega` | `omegaWallFunction` | `omegaWallFunction` | `mapped` | `inletOutlet` |
| `nut` | **`nutLowReWallFunction`** | **`nutLowReWallFunction`** | `calculated` | `calculated` |
| `alphat` | **`calculated`** | **`calculated`** | `calculated` | `calculated` |

### A2.3 THE REPAIR IS NOT A NAMESPACE SWAP, AND THAT IS THE POINT

The failing entry was `compressible::alphatWallFunction`, which does not exist
for this incompressible solver. **The obvious substitution is the wrong one.**
The available incompressible alternative, `alphatJayatillekeWallFunction`, is a
**HIGH-Re wall function**, and this mesh is **wall-resolved**: `nut` carries
`nutLowReWallFunction` and `k` carries `kLowReWallFunction`.

> **A high-Re thermal wall function running quietly on a low-Re resolved mesh
> would produce a case that RUNS AND IS SILENTLY WRONG on exactly the quantity
> this rung reports. The crash was honest. Trading an honest refusal for a
> plausible wrong number is the worst trade available here.**

`calculated` is the consistent low-Re choice: on a resolved wall `nut → 0`, so
`alphat = nut/Pr_t → 0` and no wall function is wanted. `Pr_t = 0.85` still
governs `alphat` in the interior via `constant/transportProperties`; it is the
**wall** treatment that changes, not `Pr_t`.

**This is also this lab's own established convention on this exact solver.**
`verification/runs/T-family/T1_runs/R_10k_x/0/alphat` carries
`wall { type calculated; value uniform 0; }` beside `nutLowReWallFunction` and
`kLowReWallFunction` — a wall-resolved `buoyantBoussinesqSimpleFoam` case that
has been running all night.

### A2.4 NEAR-WALL SPACING, MEASURED OFF THE BUILT MESHES

Read from `constant/polyMesh/points`, not assumed:

| level | cells | first-cell **height** (m) | first-cell **centre** `y_p` (m) | `y_p/D` |
|---|---:|---:|---:|---:|
| `T4_IJ_c` | 5 184 | 2.400000e-05 | **1.200000e-05** | 6.000e-04 |
| `T4_IJ_m` | 20 736 | 1.200000e-05 | **6.000000e-06** | 3.000e-04 |
| `T4_IJ_f` | 82 944 | 6.000000e-06 | **3.000000e-06** | 1.500e-04 |

Centres are in exact ratio **4 : 2 : 1**, confirming the family refines
systematically at `r = 2` in the wall-normal direction.

**ACHIEVED `y+` IS A SOLUTION QUANTITY AND CANNOT BE READ OFF A MESH** —
`y+ = y_p u_τ/ν` and `u_τ` is not known until the case runs. Reported against
three stated bases rather than asserted:

| level | `y+` at `u_τ` = 0.94 m/s | at 1.50 m/s | at 2.50 m/s |
|---|---:|---:|---:|
| `c` | 0.752 | **1.200** | **2.000** |
| `m` | 0.376 | 0.600 | **1.000** |
| `f` | 0.188 | 0.300 | 0.500 |

*(a) the freeze-time estimate approximately 0.055 `U_bulk`; (b) the wall-jet peak
`U_max = 1.089 U_bulk` at `c_f` approximately 0.006; (c) a deliberately pessimistic
stagnation-region bound.*

**REGISTERED RISK, disclosed now rather than discovered at grading: the COARSE
level is marginal.** Under bases (b) and (c) it exceeds `y+ = 1` and **control
C1 would fire**, sending the rung to `NOT A RESULT` on gate (1). C1 is
unchanged and measures `y+` from the run; **no threshold is relaxed to
accommodate this.** If C1 fires on `c`, that is the registered answer.

### A2.5 A THIRD DEFECT OF THE SAME ROOT CAUSE, FOUND BY THE NEW ARM

With `alphat` repaired, ARM 2 (below) failed again on
`div(((rho*nuEff)*dev2(T(grad(U)))))` — the **compressible** spelling of a
scheme this incompressible solver looks up as
`div((nuEff*dev2(T(grad(U)))))`. Same root cause, same blind spot, and
**invisible to `blockMesh` and `checkMesh`**. Repaired. Note that the arm
printed `Time = 1` *and* returned rc = 1 on this one: **requiring both is what
caught it**, and either alone would have passed it.

### A2.6 THE ONE-ITERATION ARM IS ADOPTED — `scripts/check_launcher_can_launch.py`

`scripts/check_time_dir_globs.py` is **renamed** for what it actually enforces:
**a frozen launcher that cannot launch.** Two arms:

- **ARM 1** — no shell glob is used as a time-directory matcher (AMENDMENT 1).
- **ARM 2** — the **real solver** runs for **one iteration** on the coarse case
  in a **scratch root** and must reach **`Time = 1`** with **rc = 0**.

**ARM 2 exists because every prior check exercised the channel its author was
thinking about rather than the channel that consumes the artifact.** Four
instances: T4's guard; T4's `alphat` (the mesh dry run could not see it —
`blockMesh` and `checkMesh` **never read `0.orig/`**); K0d's readability arm,
which passed while `0/U` was unreadable because `blockMesh` never reads `0/`;
and K0f's selftest, which passed **with a fake solver on PATH**. ARM 2 is the
only arm that consumes `0/`.

**Shown able to see the defect it was built for**, so its PASS is evidence: with
the original `compressible::alphatWallFunction` planted back in, ARM 2 returns
**FAIL** naming `Unknown patchField type compressible::alphatWallFunction`; with
the repair it returns **PASS — solver rc = 0 and reached `Time = 1`**.

### A2.7 Freeze-set update

`build_t4.py`'s §13 entry read `88e0207c25e0b029`, 434 lines, and is **struck
and superseded by `5f72576625a4d083`, 461 lines**. `run_one_t4.sh`'s entry stands as
superseded by AMENDMENT 1. `analyse_t4.py`, `mark_done_t4.py` and
`launch_t4.sh` are unchanged.

### A2.8 The `capped` witness proved itself in the field

Recorded because it is the one instrument from this rung that has now answered a
real question: on its **first live exercise, on a real failure**, the witness
read `capped=no` on all three arms, and `mark_done_t4.py` classified them
**CRASH, not cap-stop** — *"rc=1 at wall_s=0, BELOW the registered
timeout_s=3000, so this is not a cap-stop."* That is the discriminator built
after the measured `124`/`137`/OOM collisions, and it worked the first time it
was asked.
