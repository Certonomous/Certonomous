# Certonomous — demo-day runbook (three acts)

Every number, envelope, and field on screen comes from a real evaluation on this
machine. The PATH is scripted (pinned geometries, cached meshes); the RESULTS are
never. Human/method language on camera — no file paths, no tool or vendor names.

**Start the lab** (one terminal, left running the whole demo):

```
cd sdk
$env:CHIEF_ADAPTER = "openfoam"
$env:OPENFOAM_RUN_PREFIX = "wsl -d Ubuntu -- openfoam2606"
$env:OPENVSP_RUN_PREFIX = "wsl -d Ubuntu --"
python -m chief_engineer.server
```

Control room: **http://127.0.0.1:8765**. The full three-column layout is the
hero take on its own. Use the `PACE` chip to switch between READING (a steady
reading pace) and FAST (replays at the real event timing). Params:
`?forcelaunch=1` (preview launched layout), `?view=ask|credentials`,
`?mission=<id>` (replay a finished mission), `&static=1` (deterministic still
capture).

---

## Preflight checklist (T-30)

| Check | Command / action | Expect |
|---|---|---|
| OpenFOAM reachable | `wsl -d Ubuntu -u foam -- openfoam2606 simpleFoam -help \| head -3` | usage banner |
| VSPAERO reachable | `wsl -d Ubuntu -- vspaero \| head -1` | version banner (v7.x) |
| No stray load | `wsl -d Ubuntu -u foam -- bash -c "pgrep -c -f '[c]ertonomous' \|\| echo 0"` | 0 |
| Ports clear | `netstat -ano \| grep :8765` | nothing listening before you start |
| Tests green | `cd sdk && python -m unittest discover tests` | all OK |
| Mesh cache warm (Act 2) | run the motorBike once so the snapped mesh caches under `~/certonomous-runs/.mesh-cache/motorBike`; later runs say "reusing it, skipping the mesh build" | cache present, mesh skipped |
| Parallel solve (Act 2 slot) | start the server with `CERTONOMOUS_SOLVE_RANKS=6` on the quiet demo box | warm solve fits ~2 min |
| Pace chip | `PACE` toggles READING ↔ FAST (real event timing) | toggles |
| Autonomy counter | fresh page → launch → reads `HUMAN TOUCHPOINTS · 1` | 1 |
| Kill script armed (Act 1) | `ls scripts/kill_worker.sh`; arm slot 3 during Act 1 screening | present |
| Validation wall | open `/` dormant → wall shows 8 bodies, 4 VALIDATED | renders |
| SMTP | live report email is **Sanaa's** to send (WITH-SANAA) | note only |

---

## Demo structure — short cut vs long cut

Two running orders off the same lab, same real solves:

- **Short demo (hero cut, ~5-6 min):** Act 1 (airliner optimization) → Act 2
  (motorBike pressure field) → Act 3 (valve). One optimization act, one solved
  body, one research act.
- **Long demo (~9-11 min, more geometry on screen):** Act 1 (airliner, now a
  96-wing sweep that morphs span, area, AND sweep with 9 real finalist solves) →
  Act 2 (motorBike Cp) → **Act 2b (NACA 4412 finite wing, VALIDATED)** → Act 3
  (valve). Two solved-and-painted bodies back to back, and the optimization act
  shows the geometry changing many more times. Pre-warm both mesh caches
  (motorBike + naca4412_wing) before the long cut.

Every candidate and every body is a real evaluation in both cuts — the extra
length is more solved geometry on screen, not more talk.

---

## ACT 1 — Airliner L/D optimization (flagship, ~90 s on camera)

**Trigger:** type, no upload —
`Optimize the lift-to-drag ratio of a twin-aisle airliner carrying 300 passengers over a 6000 km range, with take-off at 85 m/s and landing at 72 m/s. Search the wing design space, mark any infeasible designs, and report the best feasible L/D with its envelope.` → Launch.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Interpretation | route panel: `AIRCRAFT OPTIMIZATION · interpretation confidence 46%` + rationale | routes elsewhere | re-read prompt; `demo-output/fallbacks/act1_airliner.png` |
| Researcher memo | CHIEF RESEARCHER: classification (3-parameter, smooth, steady) → strategy (ensemble; "the gradient is cheap and admissible") → rejected alternatives → admissibility → CHIEF ENGINEER "On it." | memo generic/absent | still frame `act1_airliner.png` |
| Compute audit | telemetry stack: `CAPACITY AVAILABLE · N requested / capacity M · cores free · memory · jobs · load` | panel missing | `act1_airliner.png` (panel bottom-left) |
| Design-space landscape | viewport: the candidate wing visibly morphs — span, area, AND quarter-chord sweep all change as the 96-wing sweep fills the plot; solved points coloured by objective, infeasible greyed (stall/range), optimum ringed | landscape absent | `act1_airliner.png` |
| Finalist solves | top 9 feasible wings promoted to **real vortex-lattice solves in parallel** (workers visible); per-finalist solved lines; winner picked on solved numbers | finalists absent → solver not reachable, check `OPENVSP_RUN_PREFIX` | screen-only path still completes honestly |
| Result + envelope | EVIDENCE: best feasible **L/D 19.7 (solved)** at span 64 m, sweep 35°, AR 13.7; screen said 18.5, same winner; the solve moved the sweep pick (screen favoured 25°, solve prefers 35°) | number differs | expected ~19.7 solved / 18.5 screened |
| Fidelity chip | unlabeled when finalists solved (SOLVER-BACKED is the platform's unlabeled default); **RESEARCH MODEL** shows on the screen-only path; headline reads value ± CI (95%) | chip over-claims | inspect verdict reason |
| Report + certificate | REPORT tab: figures first, results table with fidelity chips, Next investigations + sealed-certificate link | report empty | `act1_airliner_report.png` |
| **Worker-kill (resilience)** | arm slot 3 (`scripts/kill_worker.sh 3`) before the finalist wave → transcript: "Worker 3 stopped responding mid-solve; reprovisioning and re-running its wing" → `worker.killed` then `worker.reprovisioned` → **same nine polars, same winner L/D 19.7** | no recovery | still `act1_05_worker_kill.png`; matched-numbers proof below |
| Autonomy counter | masthead `HUMAN TOUCHPOINTS · 1` | >1 with no steer | reset page |

Measured compute (uncontended): **~10 s** (well under 90 s; on-camera time is
the narration read-out, not compute — pace the transcript). Nine real OpenVSP
3.51.1 vortex-lattice polars in parallel; the screen phase now sweeps **96
candidate wings** over span × area × quarter-chord sweep so the wing morphs many
times on camera before the finalists solve. Determinism verified: identical nine
solved polars, winner L/D 19.7 @ span 64 m (sweep 35°) every run, all beats
present, all three V&V-20 channels noted.

**Sweep is a real third design variable, not decoration.** The candidate wing
now rocks through the quarter-chord sweep angles (20°/25°/30°/35°) as well as
growing and shrinking in span and area — the planform visibly changes many times
across the screening. Every candidate is a real evaluation; the winner physics
stays honest (the solved polar picks 35° at span 64, the screen would have said
25°).

**Worker-kill rides the airliner wing, not a toy body** (content rule: no
sphere/cube/plate/cylinder on camera). Each finalist solves on a kill-checkable
worker slot; a sabotaged slot-3 run gives byte-identical solved polars and the
same winner as a clean run — the kill is narrated and recovered, the numbers do
not move (the nine solved finalists, sorted by solved L/D):

| span (m) / sweep (°) | 64/35 | 64/30 | 64/25 | 64/20 | 58/30 | 58/25 | 58/20 | 46/20 | 46/25 |
|---|---|---|---|---|---|---|---|---|---|
| clean L/D | 19.74 | 19.68 | 19.64 | 19.60 | 18.66 | 18.63 | 18.60 | 18.31 | 18.30 |
| sabotaged L/D | 19.74 | 19.68 | 19.64 | 19.60 | 18.66 | 18.63 | 18.60 | 18.31 | 18.30 |

Winner identical (span 64 m, sweep 35°, L/D 19.74 → 19.7);
`worker.killed`/`worker.reprovisioned` = 1 in the sabotaged run, 0 clean. Arm the
marker during the screening phase so slot 3 catches it as the finalist wave begins.

Captures in `demo-output/acts/act1/`: `act1_01_launched` (badge, landscape,
winner ringed, result card), `act1_02_conversation` (Chief Researcher
method-memo), `act1_03_report` (figures-first report + fidelity chip),
`act1_05_worker_kill` (kill + reprovision on the wing). (The former
`act1_04_present` presentation-mode still is retired — presentation mode was
removed; the standard layout is the hero take.)

---

## ACT 2 — Real-CFD production floor (~2 min, mesh-cache dependent)

**Trigger (upload-driven):** write the objective, then Load-a-surface, then Launch —
`Solve the external aerodynamics of the supplied B-52 geometry at 240 m/s, sea-level conditions. Select the appropriate turbulence model and solver, gate the mesh on quality, and report drag and lift with confidence envelopes.` + upload `b52.stl`
(or `Solve the external aerodynamics of the supplied motorcycle-with-rider geometry at highway speed, sea-level conditions. Select the appropriate turbulence model and solver, gate the mesh on quality, and report the drag coefficient with a confidence envelope.` + `motorBike.obj`,
or `Solve the external aerodynamics of the supplied NACA 4412 finite-wing geometry at cruise Reynolds number. Select the appropriate turbulence model and solver, gate the mesh on quality, and report the lift and drag coefficients with confidence envelopes.` + `naca4412_wing.stl`).

Each directive names the physics and asks the lab to **select** the closure,
the response must carry the selection with its rationale (`Selected: k-omega
SST, steady RANS, standard closure for attached external flow…`), not just
run silently.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Upload → run | surface renders in the viewport as supplied; objective stays natural language (no filename) | upload ignored | re-load surface; check note |
| Researcher memo | CHIEF RESEARCHER: single fixed body, steady RANS: measurement not optimisation, mesh-quality-gated → "On it." | absent | still frame |
| Mesh + gates | mesh built; non-orthogonality / skewness reported against the acceptance band | gate not shown | check monitor line |
| Cp-painted geometry | the **vehicle body** painted by solved surface pressure (coolwarm), legend in Pa: a recognizable painted body, face count in the tens of thousands, camera auto-framed on it | flat / unpainted, or two flat rectangles | `field.ready` didn't fire — check solve; if it paints the domain box see field-paint note below |
| Cache reuse (warm) | on a pre-warmed body: "Snapped mesh found in cache, reusing it, skipping the mesh build" → checkMesh still reports the real gate numbers | re-meshes cold | see pre-warm below |
| Envelope + chip | drag as value ± CI (95%); **VALIDATED** where a published reference grades it, else unlabeled (SOLVER-BACKED is the platform's unlabeled default) | envelope missing | inspect verdict |
| Certificate | sealed-certificate PDF link atop the report | absent | `/api/certificate/geometry-study` |

The worker-kill resilience beat **moved to Act 1** (it now rides the airliner
wing — no toy bodies on camera). The cylinder machinery stays in the repo for
the CI tests only.

**Field-paint selects the vehicle, not the wind-tunnel box.** The painter merges
only the body patches (the `motorBike_*` group for the motorcycle; the single
body patch for the B-52 / NACA wing) and excludes every domain boundary (inlet,
outlet, ground/floor, sky, sym\*, frontAndBack, upper/lowerWall, defaultFaces).
Two safeguards make the earlier "5,747 faces as two flat rectangles" failure
un-shippable: (a) a face-count sanity check — if the painted body is below a
robust fraction of the input surface's triangle count the selection is logged as
`field-paint patch selection suspect` and the viewport keeps the wireframe rather
than painting the wrong thing; (b) the `field.ready` payload carries a
bounding-box hint so the viewport auto-frames the camera on the painted body.
Measured painted-body face counts (real solves on this machine): motorBike
**101,235** faces (shown decimated ~19k), B-52 **15,660**, NACA 4412 **27,748** —
all in the tens of thousands, all recognizable painted bodies.

**Mesh cache (implemented, measured).** The snapped mesh is cached per body
(`~/certonomous-runs/.mesh-cache/<body>`) after the first cold run and reused on
every later run of that body, keyed by name. Only the mesh topology (the PATH)
is cached — the flow is solved live every time. Measured on motorBike (353,578
cells):

| stage | cold | warm |
|---|---|---|
| surfaceFeatureExtract | 3 s | skipped |
| blockMesh | 1 s | skipped |
| snappyHexMesh | **374 s** | **skipped (cache)** |
| checkMesh gate | ~few s | ~few s (real numbers: non-ortho 65, skew 8.94) |
| potentialFoam | ~9 s | 3–9 s |
| simpleFoam (300 iters) | solve-bound | solve-bound |

Pre-warming removes the ~6-min mesh from the on-camera run. The steady solve is
then the only pole: **300 iterations serial ≈ 4.5 min on a quiet 14-core box**
(the motorBike force is settled by ~iteration 120, so 300 is a converged, honest
window — the run now honours the iteration count it reports).

**Fitting the ~2-min slot — parallel solve.** Set `CERTONOMOUS_SOLVE_RANKS=6` on
the server (the motorBike tutorial ships a 6-way decomposition) to run the warm
steady solve in parallel via `mpirun`; it decomposes, solves, and reconstructs,
same mesh and same numbers, and brings the 300-iteration solve toward the ~2-min
slot on a quiet machine. Default is serial (the fully-tested path); the parallel
path falls back to serial on any failure. NOTE: on the build night the shared
box was saturated by a concurrent compute agent (load ~13/14), so a clean
end-to-end warm *parallel* wall-time could not be measured — the parallel stages
were each validated individually (decomposePar 3 s, mpirun potentialFoam 9 s,
mpirun simpleFoam iterating, reconstructPar). Re-measure on the quiet demo box.

Captures in `demo-output/acts/act2/`: `act2_01_mesh_gate` (OPENFOAM badge,
surface rendered, measurement-not-optimisation memo, mesh-quality gate, compute
audit); painted-field + drag capture added from the completed warm run.
Round-2 painted-body captures: `demo-output/acts/round2/motorbike/` and
`demo-output/acts/round2/b52/` (five beats each, `03-cp-painted.png` is the money
shot).

---

## ACT 2b — NACA 4412 finite wing (optional second solved-geometry act, ~2 min)

The **long-demo** second solved body: same gated CFD chain as Act 2, on a
curriculum wing that carries a published experimental reference, so it reaches
**VALIDATED** (the highest tier the lab awards) rather than SOLVER-BACKED — the
viewer sees a second real geometry solved and painted, and sees the result graded
against experiment.

**Trigger (upload-driven):** objective, then Load-a-surface, then Launch —
`Solve the external aerodynamics of the supplied NACA 4412 finite-wing geometry at cruise Reynolds number. Select the appropriate turbulence model and solver, gate the mesh on quality, and report the lift and drag coefficients with confidence envelopes.` + upload `naca4412_wing.stl`.

| Beat | Expected on screen | Measured |
|---|---|---|
| Scale + Reynolds | chord-first orientation, Re_c ~ 1e6 at 15 m/s (curriculum hints applied) | streamwise X, span Z |
| Mesh + gates | snappyHexMesh to **137,569 cells**, non-ortho 45.8°, skew 1.88 — inside the gate | real numbers |
| Cp-painted wing | the cambered section painted by solved surface pressure — **27,748-face** body, camera auto-framed | recognizable painted wing |
| Result + grade | **Cd 0.0217 ± 4.7e-06 (95%), VALIDATED** — 28% from Abbott & von Doenhoff (band ±40%); Cl 0.2516 | reaches VALIDATED |

**Mesh cache pre-warmed** (`~/certonomous-runs/.mesh-cache/naca4412_wing`), so the
on-camera run reuses the snapped mesh and the solve is the only pole. Surface
staged at `sdk/geometry/naca4412_wing.stl` (identical to the curriculum body).
Captures: `demo-output/acts/round2/naca4412/` (five beats).

---

## ACT 3 — Heart valve (research, ~90 s on camera)

**Trigger:** type, no upload —
`Optimize the leaflet opening angle of the aortic valve to minimize pressure loss over the cardiac cycle. Decompose the cycle into representative phase points, rule on the admissible method, and report the cycle-weighted loss with its uncertainty.` → Launch.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Interpretation | route panel: `VALVE STUDY` + pulsatile-internal-flow rationale | routes elsewhere | `demo-output/fallbacks/act3_valve.png` |
| Periodicity + Womersley | CHIEF RESEARCHER: "pulsatile but periodic…" → **Womersley α ≈ 16.7 displayed** with the ruling (above strict limit 1, under screening ceiling 25 → admissible as a SCREEN, phase-interaction rides in the model channel) | α not shown | `act3_valve.png` |
| Plan | k=3 phase points (weights 0.25 / 0.50 / 0.25), cycle-weighted pressure-loss objective, "backpropagation stays cheap at every phase point" | weights absent | still frame |
| Rejected / deferred | single snapshot rejected (cycle-blind); harmonic-balance + unsteady-FSI deferred to the agenda | not on record | check digest |
| Multi-point run | 4 angles × 3 phases; cycle-weighted loss per candidate with MC envelope; 35° infeasible (min-orifice) | run errors | inspect evidence |
| Result | best **1327 ± 421 Pa (95%) at 80°**, chip **RESEARCH MODEL** | number differs | expected ~1327 Pa |
| Model-form honesty | reduced-order orifice model; phase-interaction neglected; leaflets fixed; Newtonian blood, all listed | list incomplete | inspect uncertainty channel |
| Research agenda | agenda panel shows 3 lines: harmonic-balance cycle solve, unsteady FSI, non-Newtonian blood (each scope + rough cost) | agenda empty | `agenda.updated` didn't fire |

Measured compute: **0.4 s** (reduced-order; on-camera time is narration). The real
steady internal-flow solve is the marked next step (not run) — say so on camera:
"a real internal-flow solve is what would move this off a screen."

---

## RACE — Speed, certified (in-GUI split-screen act, ~90 s on camera)

**Trigger:** type, no upload —
`Race a full Monte-Carlo sweep against the reduced-order path on the NACA 4412 finite wing: same objective, same tolerance, both timed. Report the polar, the agreement, and the measured speedup.` → Launch.

The whole race is a real, in-GUI act: the centre stage becomes two lanes and
**both paths solve for real, concurrently, under one shared four-slot pool** (the
compute treaty). Left lane runs a full Monte-Carlo alpha sweep (every evaluation
a direct solve); right lane runs the reduced-order path (real anchors, fitted
surface, one real confirmation). Nothing is choreographed — the clocks on screen
are the machine's.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Interpretation | route panel: `RACE COMPARISON` + head-to-head rationale | routes elsewhere | re-read prompt; `demo-output/website/race-gui/01-start.png` |
| Lanes live | centre stage splits: FULL MONTE-CARLO \| REDUCED-ORDER, each with its own polar, progress bar, and ticking clock | lanes absent | `race.init` didn't fire — check route |
| Reduced-order crosses first | right lane flags FINISHED in a handful of solves (anchors + surface + one confirmation); left lane still grinding | rom stalls | `03-reduced-order-finished.png` |
| Monte-Carlo grinds on | left lane keeps solving to earn its envelope; nominal-Reynolds polar drawn as the running answer line | mc stalls | check solver reachable |
| Speedup card | finish card: measured core-minutes both lanes, wall times, **measured speedup**, agreement statement — numbers from THIS run only | card blank | `race.result` didn't fire |

Measured on this machine (RACE_MC_SAMPLES=5, four-slot cap, shared box):
**full MC 55 real solves · 17.9 core-min · wall 74.5 s · peak L/D 18.13 ± 0.04;
reduced-order 5 real solves · 1.9 core-min · wall 11.1 s · peak L/D 18.14 — the
two paths agree to 0.1%, measured speedup 9.2× in core-minutes (6.7× wall).**
The speedup scales with the ensemble size (RACE_MC_SAMPLES) and the box load; the
card always shows only what this run measured. The fuller 8-sample benchmark
(21.5× / 29.8× under load) lives in `demo-output/website/race/benchmarks.md`.

Captures in `demo-output/website/race-gui/`: `01-start` (both lanes live),
`02-mid-mc-grinding` (Monte-Carlo mid-sweep), `03-reduced-order-finished`
(right lane crosses first), `04-finish` (speedup card + agreement). Shotlist with
per-beat narration in the same folder.

---

## Timing table (measured vs target)

| Act | Target | Measured (compute) | On-camera driver | Note |
|---|---|---|---|---|
| 1 — airliner | ~90-120 s | ~10 s (9 real VSPAERO polars) + 96-wing screen (paced) | narration + the morphing sweep | screen conceptual, 9 finalists solved; worker-kill on the wing |
| 2 — real CFD (motorBike) | ~2 min | mesh cached (−374 s); solve ≈ 4.5 min serial / ~2 min at 6 ranks | the real solve | **pre-warm the cache**; `CERTONOMOUS_SOLVE_RANKS=6` for the slot |
| 2b — NACA 4412 (long cut) | ~2 min | mesh cached (137,569 cells); 300-iter solve | the real solve | **pre-warm** `naca4412_wing`; reaches VALIDATED |
| 3 — valve | ~90 s | 0.4 s | narration read-out | reduced-order screen, real solve is next step |
| race — split-screen | ~90 s | wall 74.5 s (60 real solves, 4-slot cap) | the two live clocks | both lanes real; rom crosses at 11 s, mc at 74 s; 9.2× measured |

Acts 1 and 3 are compute-light — their length on camera is the paced transcript
plus, for Act 1, the 96-wing sweep visibly morphing. Acts 2 and 2b are the
solve-bound acts; pre-warming removes the mesh and a parallel solve brings the
remaining steady solve into the slot on a quiet machine. Short cut = 1/2/3; long
cut = 1/2/2b/3.

---

## Fallback captures (still frames, `demo-output/fallbacks/`)

Real-run screenshots at 1920×1080, the still-frame fallback if a live beat
stalls. Full screen-recordings need a human operator (do one clean pass per act
into the same folder before demo day).

- `act1_airliner.png` — Act 1 launched: memo, compute-audit, landscape.
- `act1_airliner_report.png` — Act 1 report: results + fidelity chip + certificate.
- `act3_valve.png` — Act 3 launched: Womersley memo, model-form, compute-audit.
- `dormant_wall.png` — the validation wall (open on the dormant screen).
- Act 2 still: capture during a pre-warmed B-52/motorBike run (painted field) and
  a worker-kill run; add before recording.
