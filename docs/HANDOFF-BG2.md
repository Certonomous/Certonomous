# BG-2 handoff — website pipeline (branch `feat/website-pipeline`)

Overnight work on the website deliverables (NIGHT ORDERS section W + coordinator
v2/v3/v4.1 amendments). Everything below is real evaluations, honestly labelled.

## W1 — MEGA-BATCH (running all night) ⭐

A durable, resumable runner streaming REAL evaluations into a JSONL ledger.

- **Module:** `sdk/workflows/mega_batch.py` · **driver:** `sdk/scripts/run_mega_batch.ps1`
- **Ledger:** `demo-output/website/mega-batch/ledger.jsonl` (one JSON row per
  evaluation: `index, solver, label, design, metrics, wall_seconds, timestamp, ok`).
- **Mix (3-way interleave by index):** OpenFOAM 2D cylinder solves
  (`label=real-solve`), VSPAERO wing polars (`label=real-solve`), and
  reduced-order valve-cycle evaluations (`solver=reduced-order`,
  `label=reduced-order-eval` — honestly NOT a solve).
- **Crash-durable + resumable:** each design maps deterministically from its
  index; every row carries the index; on restart it reads the ledger and resumes
  from the next un-attempted index. Verified by test.
- **Compute treaty honoured:** 4 workers max; cylinder/wing cases written under
  `demo-output/website/mega-batch/work/` (NOT the WSL `study-*` dirs) and deleted
  per-solve to bound disk.

**How it's running:** launched in the background from `sdk/` with
```
OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606" OPENVSP_RUN_PREFIX="wsl -d Ubuntu --" \
  python -u -m workflows.mega_batch \
  --ledger ../demo-output/website/mega-batch/ledger.jsonl \
  --work-root ../demo-output/website/mega-batch/work --workers 4 --max-seconds 39600
```
Background task id `bypb2op7j`; live log at `demo-output/website/mega-batch/run.log`.
**To stop gracefully:** `New-Item demo-output/website/mega-batch/STOP` (finishes
in-flight solves, then exits). **To resume/relaunch:** re-run the command (or the
`.ps1` driver) — it picks up from the ledger.

**Count so far (checkpoint):** ~352 real evaluations (116 cylinder / 118 wing /
118 valve-ROM), ~0.83 solver core-hours, 0 failures. Throughput ~600–800/hr →
comfortably ≥1000 by morning. **Report the TRUE final count from the ledger** —
`wc -l demo-output/website/mega-batch/ledger.jsonl` or `python -m
chief_engineer.lab_stats`.

**Read the ledger:** `python -m chief_engineer.lab_stats` prints lifetime
counters + per-solver breakdown.

## W2 — BENCHMARKS PANEL

- **Generator:** `sdk/scripts/build_benchmarks.py` → `demo-output/website/benchmarks.json`
  + `demo-output/website/benchmarks.png` (four-panel house-standard figure,
  validated palette, titles/axes/units/annotations, screenshot-checked).
- Panels: real-evaluations-by-solver, mean wall time (log) + per-worker
  throughput, **closure-challenge target board** (rank #4, overall 0.0779, the 8
  per-case targets; our entry = "baseline in training — winners not yet beaten";
  NO fabricated "our score"), and the **reduced-order speed benchmark** (NACA
  4412) left as "pending measured run" until BG-1's measured numbers land.
- **Regenerate near end of shift** so it reflects the final ledger:
  `python sdk/scripts/build_benchmarks.py`. To fill the speed benchmark, edit the
  `_SPEED` dict in the generator with BG-1's measured `full_mc_core_min` /
  `reduced_core_min` / `speedup_x` (from `docs/HANDOFF-BG1.md`) and rerun.

## W3 — MOTORBIKE WEBSITE VIDEO STAGING (kit ready; capture blocked on ACT-FIXER)

- **Capture script:** `sdk/scripts/capture_motorbike_video.py` — uploads
  `sdk/geometry/motorBike.obj`, POSTs the mission on **port 8770**, watches the
  event stream, and captures five numbered 1920×1080 stills at the beat triggers
  (`mission.routed` → mesh-gate transcript line → `field.ready` → `result.verdict`
  → `certificate.ready`) into `demo-output/website/motorbike-video/`. Writes
  `capture-manifest.json`; skips (never fabricates) any beat that doesn't fire.
- **Shotlist:** `demo-output/website/motorbike-video/shotlist.md` — per-beat
  narration, bullet style, ≤14 words, method language.
- **Blocked:** I cannot run the motorBike solve (its WSL case dir is ACT-FIXER's,
  D2). **Once the motorBike act is green on port 8770, run:**
  `python sdk/scripts/capture_motorbike_video.py --geometry-path sdk/geometry/motorBike.obj --port 8770`.

## W4 — VALIDATION WALL REFRAME (product credential wall)

- **Generator:** `sdk/scripts/build_wall.py` → `demo-output/website/wall/wall.html`
  (self-contained, inline CSS, theme-aware, NO external CDNs) + `wall.json`.
- Leads with **lifetime counters** (missions run · solver core-hours · knowledge
  entries · experimental anchors · benchmarks active) — never a "4 of 8"
  fraction. The 8 canonical bodies collapse into ONE expandable "Calibration
  suite" row with measured-vs-reference, cited sources, honest tiers (v3-N3: no
  toy cases headline). Screenshot-verified.
- Reads the same records the server serves; `--server http://127.0.0.1:8770`
  fetches live instead of from disk.

## Coordinator amendments — status

- **v2-G2 (credentials header):** server endpoint **`GET /api/lab-stats`** landed
  (`sdk/chief_engineer/lab_stats.py`, wired in `server.py`) — durable
  `missions_run` counter that includes the mega-batch ledger. The
  control_room.html header reframe is delivered as a **proposal** (I did not edit
  GUI-1's file per the treaty): **`docs/CREDENTIALS_VIEW_PROPOSAL.md`**, with the
  working reference layout already built at `demo-output/website/wall/wall.html`.
  ⚠️ **GUI-1: apply the credentials-section diff from that proposal after your
  layout settles.**
- **v2-G5 / v3-N3 (collapse canonical bodies, no toy cases):** implemented in the
  wall asset + covered in the proposal for the live view.
- **v3-N2 (benchmarks content):** done (closure board + speed placeholders).
- **v4.1-W4 (certificate redesign):** see status below.

## Certificate redesign (v4.1 item 4) — STATUS

<!-- STATUS-CERT -->

## Tests

`cd sdk && python -m unittest discover tests` → **141 OK** (added
`tests/test_mega_batch.py`, 7 CI-safe tests covering the design stream,
valve run_task, ledger durability/resume, and lab-stats counters).

## Files touched / added
- `sdk/workflows/mega_batch.py` (new), `sdk/chief_engineer/lab_stats.py` (new)
- `sdk/chief_engineer/server.py` (added `/api/lab-stats`)
- `sdk/scripts/{run_mega_batch.ps1,build_benchmarks.py,build_wall.py,capture_motorbike_video.py}` (new)
- `sdk/tests/test_mega_batch.py` (new)
- `docs/CREDENTIALS_VIEW_PROPOSAL.md` (new), `docs/HANDOFF-BG2.md` (this file)
- `demo-output/website/**` (benchmarks, wall, motorbike-video kit) — artifacts
- `.gitignore` (mega-batch live/transient files)

**Not touched (per treaty):** `control_room.html`, `lab.py`, WSL `study-*` dirs.
