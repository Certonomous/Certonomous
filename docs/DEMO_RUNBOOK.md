# Certonomous — demo-day runbook (three acts)

Every number, envelope, and field on screen comes from a real evaluation on this
machine. The PATH is scripted (pinned geometries, cached meshes); the RESULTS are
never. Human/method language on camera — no file paths, no tool or vendor names.

**Start the lab** (one terminal, left running the whole demo):

```
cd sdk
$env:CHIEF_ADAPTER = "openfoam"
$env:OPENFOAM_RUN_PREFIX = "wsl -d Ubuntu -- openfoam2606"
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
| No stray load | `wsl -d Ubuntu -u foam -- bash -c "pgrep -c -f '[c]ertonomous' \|\| echo 0"` | 0 |
| Ports clear | `netstat -ano \| grep :8765` | nothing listening before you start |
| Tests green | `cd sdk && python -m unittest discover tests` | 127 OK |
| Mesh cache warm (Act 2) | pre-run the Act 2 body once so the snapped mesh is cached (see Act 2) | cached case present |
| Presentation mode | open `/?present=1`, confirm the big action line | renders |
| Autonomy counter | fresh page → launch → reads `HUMAN TOUCHPOINTS · 1` | 1 |
| Kill script armed | `ls scripts/kill_worker.sh` | present |
| Validation wall | open `/` dormant → wall shows 8 bodies, 4 VALIDATED | renders |
| SMTP | live report email is **Sanaa's** to send (WITH-SANAA) | note only |

---

## ACT 1 — Airliner L/D optimization (flagship, ~90 s on camera)

**Trigger:** type, no upload —
`Optimize the L/D of an airliner for 300 passengers, 6000 km range, take-off at 85 m/s, landing at 72 m/s` → Launch.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Interpretation | route panel: `AIRCRAFT OPTIMIZATION · interpretation confidence 70%` + rationale | routes elsewhere | re-read prompt; `demo-output/fallbacks/act1_airliner.png` |
| Researcher memo | CHIEF RESEARCHER: classification (2-parameter, smooth, steady) → strategy (ensemble; "the gradient is cheap and admissible") → rejected alternatives → admissibility → CHIEF ENGINEER "On it." | memo generic/absent | still frame `act1_airliner.png` |
| Compute audit | telemetry stack: `CAPACITY AVAILABLE · N requested / capacity M · cores free · memory · jobs · load` | panel missing | `act1_airliner.png` (panel bottom-left) |
| Design-space landscape | viewport: solved points coloured by objective, infeasible greyed (stall/range), optimum ringed, fog thinning | landscape absent | `act1_airliner.png` |
| Result + envelope | EVIDENCE: best feasible **L/D 18.4** at span 64 m, AR 13.7; envelope stated | number differs | expected 18.4 ± band |
| Honesty cap | **TREND ONLY** — conceptual sizing model, not a solved flow; model-form flagged | tier over-claims | inspect verdict reason |
| Report + certificate | REPORT tab: abstract/methods/results (TREND ONLY badge)/uncertainty/future-work + sealed-certificate link | report empty | `act1_airliner_report.png` |
| Autonomy counter | masthead `HUMAN TOUCHPOINTS · 1` | >1 with no steer | reset page |

Measured compute: **8.6 s** (well under 90 s; on-camera time is the narration
read-out, not compute — pace the transcript).

---

## ACT 2 — Real-CFD production floor (~2 min, mesh-cache dependent)

**Trigger (upload-driven):** write the objective, then Load-a-surface, then Launch —
`Solve the drag on this aircraft and paint the pressure field.` + upload `b52.stl`
(or `Show me the pressure field on this motorbike.` + `motorBike.obj`).

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Upload → run | surface renders in the viewport as supplied; objective stays natural language (no filename) | upload ignored | re-load surface; check note |
| Researcher memo | CHIEF RESEARCHER: single fixed body, steady RANS — measurement not optimisation, mesh-quality-gated → "On it." | absent | still frame |
| Mesh + gates | mesh built; non-orthogonality / skewness reported against the acceptance band | gate not shown | check monitor line |
| Cp-painted geometry | the body painted by solved surface pressure (coolwarm), legend in Pa | flat / unpainted | `field.ready` didn't fire — check solve |
| Envelope + tier | drag with settling envelope; **VALIDATED vs prior** where a reference exists, else TREND ONLY | envelope missing | inspect verdict |
| Certificate | sealed-certificate PDF link atop the report | absent | `/api/certificate/geometry-study` |
| **Worker-kill beat** | mid-sweep run `scripts/kill_worker.sh <n>` → transcript: "Worker N stopped responding mid-sweep — reprovisioning…" → `worker.killed` then `worker.reprovisioned` → mission completes with the **same numbers** | no recovery | see matched-numbers proof below |

**Worker-kill matched-numbers (proven, real OpenFOAM cylinder sweep):** clean vs
sabotaged (killed slot 3) — per-design Cd **identical**:

| D (m) | 0.7 | 0.8 | 0.9 | 1.0 | 1.1 | 1.2 | 1.3 | 1.4 |
|---|---|---|---|---|---|---|---|---|
| clean | 2.549 | 2.393 | 2.266 | 2.161 | 2.071 | 1.994 | 1.927 | 1.868 |
| sabotaged | 2.549 | 2.393 | 2.266 | 2.161 | 2.071 | 1.994 | 1.927 | 1.868 |

Winner identical (D = 1.4); `worker.killed`/`worker.reprovisioned` = 1 in the
sabotaged run, 0 clean.

**Timing / pre-warm:** a full external solve is the long pole (B-52 ≈ 8 min,
motorBike ≈ 18 min from a cold mesh). **Pre-warm before recording:** run the Act 2
body once during preflight so `snappyHexMesh` is cached; the on-camera run then
re-solves on the cached mesh, fitting the ~2 min slot. The worker-kill beat rides
the fast cylinder sweep (seconds), so it can run live without pre-warm.

---

## ACT 3 — Heart valve (research, ~90 s on camera)

**Trigger:** type, no upload —
`Optimize the valve opening angle to minimize pressure loss over the cardiac cycle` → Launch.

| Beat | Expected on screen | Failure signature | Fallback |
|---|---|---|---|
| Interpretation | route panel: `VALVE STUDY` + pulsatile-internal-flow rationale | routes elsewhere | `demo-output/fallbacks/act3_valve.png` |
| Periodicity + Womersley | CHIEF RESEARCHER: "pulsatile but periodic…" → **Womersley α ≈ 16.7 displayed** with the ruling (above strict limit 1, under screening ceiling 25 → admissible as a SCREEN, phase-interaction is model-form → TREND ONLY) | α not shown | `act3_valve.png` |
| Plan | k=3 phase points (weights 0.25 / 0.50 / 0.25), cycle-weighted pressure-loss objective, "backpropagation stays cheap at every phase point" | weights absent | still frame |
| Rejected / deferred | single snapshot rejected (cycle-blind); harmonic-balance + unsteady-FSI deferred to the agenda | not on record | check digest |
| Multi-point run | 4 angles × 3 phases; cycle-weighted loss per candidate with MC envelope; 35° infeasible (min-orifice) | run errors | inspect evidence |
| Result | best **1345 ± 421 Pa at 80°**, **TREND ONLY** | number differs | expected ~1345 Pa |
| Model-form honesty | reduced-order orifice model; phase-interaction neglected; leaflets fixed; Newtonian blood — all listed | list incomplete | inspect uncertainty channel |
| Research agenda | agenda panel shows 3 lines: harmonic-balance cycle solve, unsteady FSI, non-Newtonian blood (each scope + rough cost) | agenda empty | `agenda.updated` didn't fire |

Measured compute: **0.4 s** (reduced-order; on-camera time is narration). The real
steady internal-flow solve is the marked next step (not run) — say so on camera:
"a real internal-flow solve is what would move this off a screen."

---

## Timing table (measured vs target)

| Act | Target | Measured (compute) | On-camera driver | Note |
|---|---|---|---|---|
| 1 — airliner | ~90 s | 8.6 s | narration read-out | conceptual sizing, no solve |
| 2 — real CFD | ~2 min | solve-bound (B-52 ≈ 8 min cold) | the real solve | **pre-warm the mesh cache**; worker-kill beat is seconds |
| 3 — valve | ~90 s | 0.4 s | narration read-out | reduced-order screen, real solve is next step |

Acts 1 and 3 are compute-light — their length on camera is the paced transcript,
so they comfortably hit ~90 s. Act 2 is the only solve-bound act; pre-warming is
what makes it fit the slot.

---

## Fallback captures (still frames, `demo-output/fallbacks/`)

Real-run screenshots at 1920×1080, the still-frame fallback if a live beat
stalls. Full screen-recordings need a human operator (do one clean pass per act
into the same folder before demo day).

- `act1_airliner.png` — Act 1 launched: memo, compute-audit, landscape.
- `act1_airliner_report.png` — Act 1 report: results + TREND ONLY + certificate.
- `act3_valve.png` — Act 3 launched: Womersley memo, model-form, compute-audit.
- `dormant_wall.png` — the validation wall (open on the dormant screen).
- Act 2 still: capture during a pre-warmed B-52/motorBike run (painted field) and
  a worker-kill run; add before recording.
