# HANDOFF-GUI3 — round-3 owner feedback (GUI items)

Branch `feat/gui-core`, merged from `main` (207 tests green). All five owner
items done, verified on a live airliner run with a worker kill. Proof stills in
`demo-output/gui-proof/round3/`.

## What changed, per item

### R1 — KPI regression: Agents / Workers were 0 through the run
Root cause: `roster.update` was applied to the KPI numerals immediately on
arrival, so during a replay (and any run where events outrun the reading pace)
the numerals raced straight to the idle end-state and read 0/0 the whole time,
while the paced transcript still narrated mid-run work.

Fix: `roster.update` now rides the SAME paced reveal queue as the transcript and
dispatch (`enqueue('roster', ...)` -> `renderRoster`). The Agents/Workers
numerals advance in lockstep with the narration they belong to, so nonzero
counts show throughout execution. Workers is the live provisioned count
(0 -> fan-out -> 0); Agents is a per-mission running high-water mark of non-idle
team members (so it reflects the team on the job, not a 0/1 flicker). Peak
values are held at completion (unchanged behaviour).
- Proof: `02-kpi-finalists.png` reads `1 AGENTS · 9 WORKERS` while the nine
  finalists solve; `01-kpi-screening.png` reads `12 WORKERS` during the sweep.

### R2 — remove "grows as candidates land" caption
Removed from the live-trace legend. Sibling caption "fog thins where evidence
exists" left as-is (not flagged); it lives in the landscape draw code, unchanged.

### R3 — no raw mission slug on camera
The workspace header no longer prints the `m-...` slug. It reads a neutral label
(`ACTIVE MISSION`) via `setMissionLabel(label, slug)`; the slug rides a hover
`title` only. Provenance surfaces (the sealed-certificate footer) still carry it.
Swept toasts/report/dispatch — none printed a slug.
- Proof: header reads `ACTIVE MISSION` in every mission still.

### R4 — worker-kill beat unmistakable
`worker.killed` / `worker.reprovisioned` now ride the paced queue with a forced
dwell (`KILL_DWELL_MS`), so the LOST state holds long enough to read.
- The dispatch lane for the struck slot flips to a distinct LOST colour (red).
- A prominent banner holds over the stage: "Worker 3 lost. Reprovisioning."
  then flips amber to "Fresh worker took over slot 3. Re-running its wing." and
  the lane returns to solving; the banner clears after the hand-off reads.
- Worker numbering aligned to 1-based across transcript, dispatch, and banner
  (backend `aircraft_optimization.py` / `shape_optimization.py` now say
  `Worker {index+1}`), so `kill_worker.sh 2` reads "Worker 3" everywhere.
- Register kept clean: no em dashes ("lost, reprovisioning", not "lost —").
- Proof: `03-kill-banner.png` (LOST) and `04-reprovisioned.png` (recovered).

### R5 — lab credentials redesign
- Counters row now shows ONLY the impressive-and-real tiles: `missions run`
  (24,076, live from the ledger) and `solver core-hours` (42.2). Dropped the
  knowledge-entries / experimental-anchors / benchmarks-active small-number
  tiles.
- New ACTIVE RESEARCH section (`renderResearch`), data-driven from
  `lab_stats.research_programs()`:
  - Closure-challenge benchmark: hardcoded public board (rank #4, overall
    0.0779, eight per-case targets), cited to
    `github.com/rmcconke/closure-challenge-benchmark`. Our entry: "baseline in
    training", target top 4. No invented "our score".
  - Discretization-uncertainty program: refinement ladders from
    `models/curriculum/uq-studies/*.json` — motorBike (measured, p 4.82),
    NACA 4412 (measured, p 4.63), B-52 (in progress: mesh did not refine).
  - Reduced-order speed program: measured 21.5x (NACA 4412), from
    `demo-output/website/benchmarks.json`.
  - Queued research: harmonic-balance cycle solve, unsteady FSI, non-Newtonian
    rheology (the valve agenda).
- Calibration suite stays as one collapsed row (unchanged).
- The dormant wall (`renderDormant`) shows the same reframed content.
- Proof: `05-credentials.png` (tab) and `06-dormant-wall.png` (standing by).

## Live-run facts (mission m-7fb294c5a61b, this machine)
- Routed aircraft-optimization; 96-wing sweep, 9 real vortex-lattice finalists.
- Worker kill armed on slot 2 -> `worker.killed`(seq 490)/`worker.reprovisioned`
  (seq 491); recovered winner L/D 19.7 (matches a clean run).
- Stills captured with `?mission=<id>&static=1&upto=N` (deterministic mid-flight
  frames): screening `upto=250`, finalists `upto=485`, LOST `upto=490`,
  recovered `upto=491`.

## Tests
`cd sdk && python -m unittest discover tests` -> 207 OK (was 206; +1 for
`research_programs`).

## Merge risk / notes for whoever integrates to main
- Only backend surface touched is additive: `lab_stats.research_programs()` and a
  `research` key on `/api/lab-stats`. The two workflow edits are string-only
  (worker numbering) and covered by existing recovery tests.
- `/api/lab-stats` counters read the mega-batch ledger. On a worktree without
  `demo-output/website/mega-batch/ledger.jsonl`, `missions_run` is 0. For the
  real numbers point `CERTONOMOUS_MEGABATCH_LEDGER` at the main-repo ledger (as
  the test server did). No blocker for main, which has the ledger.
- The kill banner lives inside `#stageWrap`; it is hidden during the race view
  (race hides the stage), which is correct — the kill beat rides the airliner
  act, not the race.
- No blockers.
