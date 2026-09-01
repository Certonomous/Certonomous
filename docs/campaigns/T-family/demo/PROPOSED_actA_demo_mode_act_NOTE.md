# DEMO MODE conformance for Act A and Act C — handover note for the cfd team

**Status: PROPOSAL. NOT APPLIED.** Nothing was written under `sdk/`. No server
was restarted or signalled. No solver was launched. All verification was done in
throwaway `git archive HEAD` copies.

Prepared by the heat-transfer team, 2026-09-01. `sdk/` is cfd territory; the
patch is yours to apply.

- Patch: `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/PROPOSED_actA_demo_mode_act.patch`
- **`git apply --check` passes against the real tree**, verified at HEAD
  `70047dcf`. All three files are NEW, so the patch carries no context lines and
  does not go stale as HEAD moves.
- Three files, all additions:

| file | what |
|---|---|
| `sdk/workflows/motor_thermal_act.py` | Act A, `motor-thermal`, fully conforming, registers itself |
| `sdk/workflows/battery_module_act.py` | Act C, `battery-module`, scaffold that **refuses to register** |
| `sdk/geometry/t23_solved_geometry.stl` | the solved-geometry surface, 90,084 bytes, sha256 `d2864232dbf6d87a89c7a2dab4fdf232bc61eae405cb35a174f364d24a935cc9` |

The STL is carried as a binary hunk so the patch is self-contained. Applying it
into a fresh `git archive HEAD` copy reproduces the file byte for byte: the
sha256 above equals the sha256 of the copy the solved case generates at
`verification/runs/T-family/T23_runs/display_surface/t23_solved_geometry.stl`.
If you would rather copy the file by hand than take it from the patch, that
sha256 is what to verify against.

---

## 1. Where heat-transfer stood before this, and where it stands after

Before: **zero.** `sdk/workflows/thermal_display.py` never imports `demo_mode`,
never subclasses `DemoAct` and never calls `register_act`. It is a
bundle-to-PDF presenter and it is untouched by this patch. Two acts were
registered, `jet-flap` and `adjoint-wing`, neither of them ours.

After: `validate_act(motor_thermal_act.ACT, check_files=True)` returns an
**empty list**, and the sequencer walks Act A from the prompt through to
feasibility, publishing every payload through the guard, before stopping on one
named external dependency (§4). Act C returns **nine** problems and registers
nothing, which is the correct output for it.

---

## 2. Act A, `motor-thermal` — what it is fed from, and what it says

Sixteen steady conjugate operating points, `chtMultiRegionSimpleFoam`,
k-omega SST, one grid of 39,680 cells over three regions. The solver name is
read from the run's own `Exec` header line **and** from `system/controlDict`'s
`application` entry and the two are cross-checked; neither is typed into the
module.

**There are no physical constants in the act.** Every number is read at the
moment it is asked for, from an artifact still on disk. The screen strings the
sequencer actually published in the test run:

| stage | what went through the guard |
|---|---|
| geometry | `Solved on this geometry, 39,680 cells.` |
| meshing | `39,680 cells`, wall-layer table over four surfaces |
| feasibility | `197.3 C`, and a go verdict quoting the 200 C limit |
| gates | one grid of 39,680 cells over 3 regions, checked cell by cell |
| results, solver line | `Solver: OpenFOAM chtMultiRegionSimpleFoam, steady conjugate heat transfer …, with the kOmegaSST closure resolved to the wall.` |
| results, cost | `578.8 core-minutes (gross), about $0.49, derived at the recorded rate` |
| results, estimate | `483.6 core-minutes` |
| elapsed | `579 minutes.` plus its basis sentence |

The sixteen-row map table went through the guard intact. Its hottest row is
**305 W at 10 m/s: core 107.7 C, housing 103.6 C, margin 92.3 K** — the peak
and the margin the board carries, reproduced by the act from the bundle rather
than transcribed into it.

**The cell attribution is the right way round.** 35,200 fluid / 1,120 housing /
3,360 core, read from `T23_T24_MESH_FACTS.json`, whose own cross-check is the
`blockMeshDict` block arithmetic. The core is hotter than the housing at every
row of the map (107.7 against 103.6 at the worst point), which is the physical
check that the labels are not swapped.

### The one trap this act had to avoid, and did

**`ClockTime` is wall time. `ExecutionTime` is CPU time.** OpenFOAM prints both
on the same line and they are different numbers: 1814 against 1813.14 on the
primary case. The family's own cost record settles this at its §3.2. The act
reads `ClockTime` and says so at the point it reads it. An act that took the
first number on the line would misstate every cost on the screen.

---

## 3. The finding that most needs your eye: **the surface served for Act A today is the retired body**

`sdk/geometry/motor_in_duct.stl` is sha256 `131aab8e…`, which is exactly the
sha256 the solved case's own part manifest records under `retires`. It is the
surface that was withdrawn.

This is not an inference from the manifest. The generator's geometry guard was
run over it and it refuses on **fourteen** counts. Measured:

| what the guard measured | served body | solved case |
|---|---:|---:|
| axial extent | 0.260 m | 0.750 m |
| maximum radius | 0.2385 m | 0.1250 m |
| vertices between the body and the duct (the strut signature) | **7,954** | 0 |
| vertices inside the body radius at an interior station (nose and tail) | **216** | 0 |
| facets against the manifest | 6,288 | 1,800 |

So Sanaa's requirement at `569346b3` — the displayed geometry must BE the
solved geometry — is **not met on screen today**, and nothing in the current
Act A path would have said so. Under this patch it cannot fail silently:
`geometry()` runs the generator's own guard over the **served** copy and also
asserts that copy byte-identical to the one the solved case generates. Both
guards were shown able to fail:

| planted control | result |
|---|---|
| serve the retired body under the served name | **REFUSED** |
| change one byte of the served copy | **REFUSED** |
| bypass the identity check, hand the retired body to the shape guard | **REFUSED**, on all fourteen counts above |
| control restored | validator returns to zero problems |

The generator refuses by exiting rather than raising, which inside a validator
would take the process down. The act catches that exit and translates it into
the contract's own refusal, so it is collected as a problem rather than killing
the shoot. **The generator prints its refusal to stdout before exiting**; on a
shoot that lands in a log, not on a screen, but it is worth knowing it is
chatty.

---

## 4. THE BLOCKER: the shared replay reader cannot open a conjugate thermal run

**This is the single thing standing between "Act A conforms" and "Act A can be
shown", and it is in your territory, not ours.**

`SolveReplay.cases` is supplied EMPTY, deliberately, following the contract's
own instruction that an act with no `cases` must say to its supervisor how its
logs are read instead. `demo_sequencer._stage_solving` then refuses with
`the solving stage has no cases to read`, which is the honest outcome and is
where the test run stopped. Supplying the case list instead would have passed
`validate_act` and then died inside the reader with a `FileNotFoundError`
mid-shoot, which is worse.

Measured, by calling the reader directly on `T23_P305_U20`:

| reader | what it demands | what this run has |
|---|---|---|
| `replay_history.read_solve_history` | `log.simpleFoam`, hard-coded at `sdk/chief_engineer/replay_history.py:224` | `log.solve` |
| `replay_history.read_run_status` | a `RUN_STATUS.*.txt` carrying `rc`, `wall_s`, `ranks`, `core_min_MEASURED` (`:463`, `:467`) | the launcher status file was destroyed by a queue-runner name collision and re-derived; the run carries `STATUS.<case>` with three keys |
| `replay_history.read_run_history` | lift and drag coefficient columns | a conjugate thermal case has no force coefficients at all |

**What would unblock it:** a configurable solver-log name, a status source that
can be a re-derived cost record rather than only a launcher file, and a
temperature channel beside the coefficient one. The monitor files this act
needs are already named in its `series` and are on disk:
`postProcessing/{core,housing}/{core,housing}_T/0/fieldMinMax.dat`, one row per
hundred iterations, plus `log.solve` for the pressure residual.

Worth saying plainly: the reader's discipline is right and we are not asking
for it to be loosened. It carries planted controls on every channel and refuses
when it cannot see its plant. It simply has one solver's file layout compiled
into it.

---

## 5. Three smaller decisions that are yours, not ours

**(a) The cost line on screen is in core-minutes, and our supervisor ruled it
should be wall time and dollars.** `demo_mode.cost_line` renders
`Compute used: 578.8 core-minutes (gross), about $0.49, derived at the recorded
rate.` and `demo_sequencer._stage_results` calls it. **We did not patch it**, on
purpose: it is one function shared by `jet-flap` and `adjoint-wing`, so changing
its wording changes two other teams' screens, and that is a cross-team call
rather than ours to make in a patch. The act supplies `cost_actual` in
core-minutes because that is what the type documents. If you want the ruling
honoured, the change is in `cost_line`, and it should be agreed with cfd and
dafoam first.

**(b) The geometry sentence is missing its point count.** Sanaa's Act A pattern,
quoted inside `demo_mode.Geometry.solved_geometry_sentence`'s own docstring,
reads *"16 operating points solved on this geometry, 39,680 cells."* The method
renders `Solved on this geometry, 39,680 cells.` The count is available to the
sequencer as `solve_replay().sweep_points`. Contract-side, so left alone.

**(c) `MeshPlan.cell_count` carries a pre-formatted string.** We pass `"39,680"`
rather than the integer `39680`, because `Measured.on_screen()` is called
without a format and the standard writes the number with a thousands separator.
The integer is still read from the mesh record and never typed; only the comma
is ours. If you would rather the type stayed numeric, the formatting belongs in
`on_screen`.

---

## 6. Act C, `battery-module` — a refusal, on purpose

**It registers nothing.** Importing the module leaves the registry empty and
`demo_sequencer.run_act("battery-module")` fails with
`no act is registered as 'battery-module'`. `ACT` is bound to `None` so a caller
expecting the module-level name every other act module exposes gets a readable
failure rather than an `AttributeError` that looks like a missing file.

All ten stages exist with their real signatures. Nine of them refuse by name,
saying which fact they lack. `prompt()` is the exception and returns real text,
because a user's request is not a result. `conformance_problems()` returns the
validator's list — **nine problems** — and
`register_when_a_solved_run_backs_it()` refuses while that list is non-empty.

**No placeholder number is anywhere in the file.** The reasons it is blocked
are recorded, from the record itself, in the module docstring and in a
screen-safe `BLOCKED_ON` tuple:

- 960 cells for the whole module, 120 per battery cell.
- The cooling channels are **not resolved as a fluid region**; the record's own
  outlet temperature field literally reads `NOT DEFINED`. A cooling
  demonstration whose coolant is not a fluid cannot show cooling.
- Largest temperature rise anywhere, 0.4198 K; largest spread across the
  module, 0.1105 K. Flat lines on a pack chart.
- The replacement run's first level **ran and diverged**: rc 134, one fatal,
  `Negative initial temperature T0: -14.46` at 1.5 s of a 900 s end time. Its
  other two levels are meshed with no solve. So the honest statement is
  stronger than "not yet run".

The caveat box that act will carry is written **now**, as `LIMITATIONS`, and is
language-checked at import. A caveat drafted beside a number it has to survive
is a caveat that gets negotiated.

---

## 7. Planted controls, because a guard not shown able to fail is not evidence

Rule 3. Every screen value in Act A goes through `_fact` (no default of any
kind, raises on a missing key) or `_cell` (renders a missing key as the words
`not recorded`). There is **no numeric default anywhere in either module**: a
grep for a numeric second argument to `dict.get` returns nothing, and the
pattern the thermal display module had eighteen of is not reintroduced.

| control | result |
|---|---|
| `peak_core_T_degC` removed from every map row | the cell reads `not recorded`, never `0.0` |
| `envelope.limit_degC` removed | `results()` **REFUSED**, naming the missing key |
| the closing line removed from a solver log | `wall_clock_seconds` **REFUSED**, naming the case |
| control restored | wall reads 1814.0 s, and `ExecutionTime` on the same line reads 1813.14 s, a different number |
| retired body served, one byte changed, shape guard bypassed | all three **REFUSED** (§3) |

Act A's own instrument table on screen carries the family's four readers, each
having detected a planted 1.234e-03 K perturbation, read from the bundle rather
than asserted.

---

## 8. Two corrections to the brief we were given

**The brief said `sdk/tests/test_scope_down.py` is modified in the worktree by
another team, and that whoever applies must run that suite first. The first
half is not true.** Three hashes agree:

    worktree ffb3aba6927e0994fb2e9ff001a334ee8c9685bc
    index    ffb3aba6927e0994fb2e9ff001a334ee8c9685bc
    HEAD     ffb3aba6927e0994fb2e9ff001a334ee8c9685bc

The file is clean at HEAD, in the index and on disk. Running the suite before
applying is still sensible advice; it is just not urgent for the reason given.

What IS modified under `sdk/` in the shared worktree, and worth your eye before
you apply anything: `demo_mode.py`, `demo_sequencer.py`, `adjoint_act.py` and
`jet_flap_display.py` all read `MM`, and `sdk/tests/test_demo_sequencer_guard.py`
carries a **staged deletion** against HEAD while the file is present on disk and
untracked. A bare `git commit` by anybody would delete that test. The index is
chief's call, so this is reported and not touched.

**`sdk/geometry/motor_in_duct.stl` and `battery_module_8cell.stl` are untracked**
in the shared worktree, unlike every other surface in that directory. Our STL is
proposed as a tracked file, which is the majority practice there.

---

## 9. Restart scope

**This patch needs a restart.** Both modules are Python inside a package the
control-room server imports, and nothing imports them today, so applying the
patch changes no running behaviour until something imports
`workflows.motor_thermal_act` and the server is bounced. Batch it into the
single coordinated restart rather than bouncing a server Sanaa is sitting in.

Nothing in this patch is on the critical path of a running solve. It touches no
bundle, no figure and no `.tex` sheet. The Act A figures and the two sheets were
referenced by path only and were not opened for writing, because another lane is
working on them.

---

## 10. Cost calibration for the run this act shows (CLAUDE.md rule 12)

Computed by the act itself at read time, from the sixteen solver logs and the
sixteen launched records:

| figure | value | basis |
|---|---:|---|
| registered estimate, summed over sixteen points | **483.585 core-min** | sum of `cost_core_min_estimate` in the launched records |
| actual | **578.8 core-min** | sum of the closing `ClockTime` of sixteen `log.solve`, at 1 rank each |
| ratio actual / predicted | **1.197** | |
| derived dollars | **$0.49** | 578.8 core-min at $0.0513 per core-hour, **derived, never measured** — the box cannot read its own billing |

Attribution of the 19.7 % gap: **contention, not misprediction.** The four
`T23` points ran four-concurrent; the twelve `T24` points ran twelve-concurrent
on a sixteen-core box, and that family's own contention note measures the effect
at matched iteration bands. The per-point figures show it plainly: the
four-concurrent points cost 1781 to 1831 wall seconds each, the
twelve-concurrent points 2243 to 2353. Waste: nil, and separately named. No
point came near its registered cap.

**This lane's own compute: zero solver core-minutes.** No solve was launched.

---

## 11. What we could not verify

- **That the sequencer completes Act A end to end.** It cannot, today, for the
  reason in §4. Six stages were driven and published through the guard; the
  gates and results stages were driven separately and published clean; the
  solving stage was never exercised because the reader cannot open the run.
- **`expected_seconds` on the mesh plan is 30.0 and is not a measurement.** The
  case's `log.blockMesh` carries no timing line at all, so there is nothing to
  read. The field is a pacing hint, is not published to any screen, and nothing
  validates it. It is the one number in the act that was chosen rather than
  read, and it is named here for that reason.
- **`SolveReplay.wall_seconds.source` names one log while the value sums
  sixteen.** The type carries one path. The `note` field says so explicitly, and
  the sum is recomputed from all sixteen logs on every call, but `validate_act`
  only checks the one path exists. A reviewer who wants the other fifteen
  checked would need a change on the contract side.
- **The feasibility beat's 197.3 C is a hand-correlation prediction taken from
  the grading record.** It is a real number from a real fast estimate and the
  act does not claim it was computed at any particular moment. If cfd or the
  supervisor reads that framing as implying a literal pre-solve sequence, say
  so and we will restate the beat.

---

## AMENDMENT 1 — 2026-09-01, in answer to three supervisor questions

Appended, not rewritten. Nothing above this line is edited or deleted; lines
whose number changed above this section: 0. One figure in §3 is **corrected
here and struck below**.

### A1.1 CORRECTION AGAINST ME — the retired body is 0.200 m axial, not 0.260 m

§3 says the served body is *"0.260 m axial against the solved 0.750 m"*.
**~~0.260 m axial~~ is wrong.** The manifest's own `/retires/reason`, which
says 0.200 m, is right. Measured over every vertex of both surfaces:

| surface | x extent | y extent | z extent |
|---|---:|---:|---:|
| `motor_in_duct.stl` (retired) | **0.200000003 m** | 0.259999990 m | 0.259999990 m |
| `t23_solved_geometry.stl` (solved) | 0.250000000 m | 0.250000000 m | **0.750000000 m** |

**The two surfaces do not share an axis convention.** The retired body is built
**x-axial**; the solved surface is **z-axial**. `check_surface` defaults to
`axis="z"`, so when it read the retired body it reported the **z** extent,
0.260 m, under the label "axial". The guard's refusal is sound on all fourteen
counts, and its axial lines are correct for the convention it was told to use;
what was wrong was my reading of that line as the body's own axial extent. The
retired body's true axial extent is **0.200 m against the solved 0.750 m**, a
factor of 3.75, and the manifest said so all along.

Worth keeping: a surface whose axis convention differs from the solved one
would render lying on its side in the viewport even if every dimension agreed.

### A1.2 The 197.3 C feasibility beat depends on NO solved quantity. It stands.

The narrower question was the right one to ask, and the answer is cleaner than
"honest regardless of when we recorded it": **197.3 C is not a post-hoc number
at all. It is a prediction registered before compute, in the frozen file.**

Derivation chain, input by input, from §2.1 of the frozen T23 registration:

    T_max = T_inf + P · R_tot(U)
    R_tot(U) = 1/(h(U)·A_housing) + R_wall + R_core        [K/W, DERIVED]

| input | what it is | solved? |
|---|---|---|
| `T_inf` = 288.0 K | the inlet air temperature, a fixed-value boundary condition; registered in §2.1 and separately readable from each case's own `0.orig/fluid/T` | **no**, it is an imposed input |
| `P` = 305 W | the dissipated power, the operating point being requested | **no**, an input |
| `h(U)` | Dittus-Boelter, from airspeed, air properties and duct hydraulic diameter | **no**, a correlation over inputs |
| `A_housing`, `R_wall`, `R_core` | geometry and the three registered conductivities | **no**, inputs |

Not one solved value appears. Every quantity is one a user has in hand before
any solver starts.

**Verified in the frozen file rather than trusted from the script's comment.**
`analyse_t23.py:100` calls its `PREDICTED` dict "transcribed from the frozen
file"; I checked the transcription. `docs/campaigns/T-family/T23_PREREGISTRATION.md:714`
carries the row `T23_P305_U20 | 197.3 °C | 120.3 °C | UNDECIDED, +2.70 K`, and
lines 713 to 716 carry all four points. The file's blob is
`c341476f3680c14ec593c52d12e49214cf83ebb3` on disk **and** at HEAD, and that is
the same blob the family's cost record verified against the freeze commit
`fe666fd5`.

Stronger still: §2.7 registered **in advance** that the lumped model might be
wrong, and §6.2 registered the contingency one-way before compute. So the beat
is not merely a fast estimate presented as one; it is a prediction the lab
committed to and then measured itself against. The act's assumption stage,
which reports the correlation overshooting by 3.4x, is that measurement.

**No change to the act.** The beat stands as written.

### A1.3 THE PATCH ALONE DOES NOT TAKE THE RETIRED BODY OFF SCREEN

This is the important one, and the honest answer is no.

**What actually decides which file reaches the screen today, traced end to end:**

1. The operator picks a file in the control room (`control_room.html:446`, the
   file input) and it POSTs to `/api/geometry/upload`.
2. `server.py:_accept_surface` writes it into `sdk/geometry/` **under the
   uploader's own filename**, stripped to a bare name.
3. Launch posts `surface: <that filename>` into the mission payload
   (`control_room.html`, `state.uploaded`).
4. `router.py:918` routes a thermal request to `THERMAL_DISPLAY`, whose module
   is `workflows.thermal_display`.
5. `thermal_display.py:799` reads `params.get("surface")` and announces **that
   name**, and nothing else.
6. `server.py:_serve_geometry` (`:344`) resolves `sdk/geometry/<name>` and
   returns it.

**So the filename comes from the operator's upload, end to end. No act, no
manifest, no configured default and no code constant is consulted at any step.**
The retired body reaches the screen because a file with that name was uploaded
once and has sat in the directory ever since.

**And `demo_sequencer` is referenced nowhere in `sdk/chief_engineer/`.** Not by
the server, not by the router. The demo-mode path is unreachable from the
control room. Registering `motor-thermal` therefore changes nothing on screen
on its own: the act is correct, guarded and inert.

**What else must change. All of it is inside `sdk/`, so all of it is cfd's.**

| # | change | why | shape |
|---|---|---|---|
| 1 | route the thermal intent to `demo_sequencer.run_act("motor-thermal")` instead of `workflows.thermal_display` at `router.py:918` | this is the real fix. Once routed, `demo_sequencer._stage_geometry` takes `g.served_stl.name` from the act, so the served file becomes the solved one automatically and **cannot** be an upload | a patch hunk, cfd's to write |
| 2 | delete `sdk/geometry/motor_in_duct.stl` | while the live path still takes the name from an upload, this is what makes `?name=motor_in_duct.stl` return 404 instead of the retired body | a file removal, not a hunk: the file is **untracked**, so no patch can express it |
| 3 | nothing stops it coming back | `_accept_surface` will re-create it on the next upload of a file with that name. Change 2 is necessary and **not sufficient**; only change 1 closes it | — |

**A fourth thing found on the way, and it is not small.** The live Act A screen
path carries phrases `demo_mode`'s own checker refuses. Run through
`check_demo_language`:

| line | string | verdict |
|---|---|---|
| `thermal_display.py:793` | "the screens come from that run's own fields" | **BANNED** |
| `thermal_display.py:806` | "Reference body received" | **BANNED** |
| `thermal_display.py:459` | "not recorded in this bundle" | **BANNED** |

Three of Sanaa's never-list phrases are on the current Act A path right now.
That is an independent argument for change 1: routing through the sequencer
puts every string through the guard, and these three would fail at authorship
instead of on camera.

**Bottom line for the applier: applying this patch is step one of two.** It
lands a correct, guarded, validating act and the right surface beside the wrong
one. It does not take the wrong one off screen. Changes 1 and 2 above do, and
both are yours.

### A1.4 Standing flag, restated as asked

`expected_seconds = 30.0` in `mesh_plan()` is **CHOSEN, NOT READ.** The case's
`log.blockMesh` carries no timing line, so there is nothing to read. It is the
only number in the act not taken from an artifact. It reaches no screen and
nothing validates it.
