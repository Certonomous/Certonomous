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

Control room: **http://127.0.0.1:8765**. Toggle **presentation mode** for the
hero take — the `PRESENT` button, the `P` key, or launch with `?present=1`
(fonts up, rails hidden, one large current-action line). Other params:
`?forcelaunch=1` (preview launched layout), `?view=ask|credentials`,
`?mission=<id>` (replay a finished mission).

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
| Presentation mode | open `/?present=1`, confirm the big action line | renders |
| Autonomy counter | fresh page → launch → reads `HUMAN TOUCHPOINTS · 1` | 1 |
| Kill script armed (Act 1) | `ls scripts/kill_worker.sh`; arm slot 3 during Act 1 screening | present |
| Validation wall | open `/` dormant → wall shows 8 bodies, 4 VALIDATED | renders |
| SMTP | live report email is **Sanaa's** to send (WITH-SANAA) | note only |

---

## ACT 1 — Airliner L/D optimization (flagship, ~90 s on camera)

**Trigger:** type, no upload —
`Optimize the lift-to-drag ratio of a twin-aisle airliner carrying 300 passengers over a 6000 km range, with take-off at 85 m/s and landing at 72 m/s. Search the wing design space, mark any infeasible designs, and report the best feasible L/D with its envelope.` → Launch.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Interpretation | route panel: `AIRCRAFT OPTIMIZATION · interpretation confidence 46%` + rationale | routes elsewhere | re-read prompt; `demo-output/fallbacks/act1_airliner.png` |
| Researcher memo | CHIEF RESEARCHER: classification (2-parameter, smooth, steady) → strategy (ensemble; "the gradient is cheap and admissible") → rejected alternatives → admissibility → CHIEF ENGINEER "On it." | memo generic/absent | still frame `act1_airliner.png` |
| Compute audit | telemetry stack: `CAPACITY AVAILABLE · N requested / capacity M · cores free · memory · jobs · load` | panel missing | `act1_airliner.png` (panel bottom-left) |
| Design-space landscape | viewport: solved points coloured by objective, infeasible greyed (stall/range), optimum ringed, fog thinning | landscape absent | `act1_airliner.png` |
| Finalist solves | top 6 feasible wings promoted to **real vortex-lattice solves in parallel** (workers visible); per-finalist solved lines; winner picked on solved numbers | finalists absent → solver not reachable, check `OPENVSP_RUN_PREFIX` | screen-only path still completes honestly |
| Result + envelope | EVIDENCE: best feasible **L/D 19.7 (solved)** at span 64 m, AR 13.7; screen said 18.4, same winner | number differs | expected ~19.7 solved / 18.4 screened |
| Fidelity chip | **SOLVER-BACKED** when finalists solved (wing solved, buildup stated) — **CONCEPTUAL MODEL** on the screen-only path; headline reads value ± CI (95%) | chip over-claims | inspect verdict reason |
| Report + certificate | REPORT tab: figures first, results table with fidelity chips, Next investigations + sealed-certificate link | report empty | `act1_airliner_report.png` |
| **Worker-kill (resilience)** | arm slot 3 (`scripts/kill_worker.sh 3`) before the finalist wave → transcript: "Worker 3 stopped responding mid-solve — reprovisioning and re-running its wing" → `worker.killed` then `worker.reprovisioned` → **same six polars, same winner L/D 19.7** | no recovery | still `act1_05_worker_kill.png`; matched-numbers proof below |
| Autonomy counter | masthead `HUMAN TOUCHPOINTS · 1` | >1 with no steer | reset page |

Measured compute (uncontended): **~10 s** (well under 90 s; on-camera time is
the narration read-out, not compute — pace the transcript). Six real OpenVSP
3.51.1 vortex-lattice polars in parallel. Determinism verified over 5+ full
passes: identical six solved polars, winner L/D 19.7 @ span 64 m every run, all
beats present, all three V&V-20 channels noted.

**Worker-kill now rides the airliner wing, not a toy body** (content rule: no
sphere/cube/plate/cylinder on camera). Each finalist solves on a kill-checkable
worker slot; a sabotaged slot-3 run gives byte-identical solved polars and the
same winner as a clean run — the kill is narrated and recovered, the numbers do
not move:

| span (m) | 46 | 52 | 58 | 58 | 64 | 64 |
|---|---|---|---|---|---|---|
| clean L/D | 18.3 | 17.7 | 16.6 | 18.6 | 17.3 | 19.7 |
| sabotaged L/D | 18.3 | 17.7 | 16.6 | 18.6 | 17.3 | 19.7 |

Winner identical (span 64 m, L/D 19.7); `worker.killed`/`worker.reprovisioned` = 1
in the sabotaged run, 0 clean. Arm the marker during the screening phase so slot
3 catches it as the finalist wave begins.

Captures in `demo-output/acts/act1/`: `act1_01_launched` (badge, landscape,
winner ringed, result card), `act1_02_conversation` (Chief Researcher
method-memo), `act1_03_report` (figures-first report + fidelity chip), `act1_04_present`
(presentation mode), `act1_05_worker_kill` (kill + reprovision on the wing).

---

## ACT 2 — Real-CFD production floor (~2 min, mesh-cache dependent)

**Trigger (upload-driven):** write the objective, then Load-a-surface, then Launch —
`Solve the external aerodynamics of the supplied B-52 geometry at 240 m/s, sea-level conditions. Select the appropriate turbulence model and solver, gate the mesh on quality, and report drag and lift with confidence envelopes.` + upload `b52.stl`
(or `Solve the external aerodynamics of the supplied motorcycle-with-rider geometry at highway speed, sea-level conditions. Select the appropriate turbulence model and solver, gate the mesh on quality, and report the drag coefficient with a confidence envelope.` + `motorBike.obj`,
or `Solve the external aerodynamics of the supplied NACA 4412 finite-wing geometry at cruise Reynolds number. Select the appropriate turbulence model and solver, gate the mesh on quality, and report the lift and drag coefficients with confidence envelopes.` + `naca4412_wing.stl`).

Each directive names the physics and asks the lab to **select** the closure —
the response must carry the selection with its rationale (`Selected: k-omega
SST, steady RANS — standard closure for attached external flow…`), not just
run silently.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Upload → run | surface renders in the viewport as supplied; objective stays natural language (no filename) | upload ignored | re-load surface; check note |
| Researcher memo | CHIEF RESEARCHER: single fixed body, steady RANS — measurement not optimisation, mesh-quality-gated → "On it." | absent | still frame |
| Mesh + gates | mesh built; non-orthogonality / skewness reported against the acceptance band | gate not shown | check monitor line |
| Cp-painted geometry | the body painted by solved surface pressure (coolwarm), legend in Pa | flat / unpainted | `field.ready` didn't fire — check solve |
| Cache reuse (warm) | on a pre-warmed body: "Snapped mesh found in cache — reusing it, skipping the mesh build" → checkMesh still reports the real gate numbers | re-meshes cold | see pre-warm below |
| Envelope + chip | drag as value ± CI (95%); **VALIDATED** where a published reference grades it, else **SOLVER-BACKED** | envelope missing | inspect verdict |
| Certificate | sealed-certificate PDF link atop the report | absent | `/api/certificate/geometry-study` |

The worker-kill resilience beat **moved to Act 1** (it now rides the airliner
wing — no toy bodies on camera). The cylinder machinery stays in the repo for
the CI tests only.

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
| Result | best **1345 ± 421 Pa (95%) at 80°**, chip **CONCEPTUAL MODEL** | number differs | expected ~1345 Pa |
| Model-form honesty | reduced-order orifice model; phase-interaction neglected; leaflets fixed; Newtonian blood — all listed | list incomplete | inspect uncertainty channel |
| Research agenda | agenda panel shows 3 lines: harmonic-balance cycle solve, unsteady FSI, non-Newtonian blood (each scope + rough cost) | agenda empty | `agenda.updated` didn't fire |

Measured compute: **0.4 s** (reduced-order; on-camera time is narration). The real
steady internal-flow solve is the marked next step (not run) — say so on camera:
"a real internal-flow solve is what would move this off a screen."

---

## Timing table (measured vs target)

| Act | Target | Measured (compute) | On-camera driver | Note |
|---|---|---|---|---|
| 1 — airliner | ~90 s | ~10 s (6 real VSPAERO polars) | narration read-out | screen conceptual, finalists solved; worker-kill on the wing |
| 2 — real CFD | ~2 min | mesh cached (−374 s); solve ≈ 4.5 min serial / ~2 min at 6 ranks | the real solve | **pre-warm the cache**; `CERTONOMOUS_SOLVE_RANKS=6` for the slot |
| 3 — valve | ~90 s | 0.4 s | narration read-out | reduced-order screen, real solve is next step |

Acts 1 and 3 are compute-light — their length on camera is the paced transcript,
so they comfortably hit ~90 s. Act 2 is the only solve-bound act; pre-warming
removes the mesh and a parallel solve brings the remaining steady solve into the
slot on a quiet machine.

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
