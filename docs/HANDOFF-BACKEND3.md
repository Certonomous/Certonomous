# HANDOFF - BACKEND-3 (round-3 owner feedback)

Branch `feat/demo-acts`, merged from `main` first. Full suite green: **215
tests** (`cd sdk && python -m unittest discover -s tests`). Server tested on
port 8768; 8765 never touched.

Owner's four items, all done. Commits are per item and each is green.

## 1. A Certonomous certificate for every act (was: only geometry_study had one)
`build_certificate_v2` is now wired into three more workflows, each emitting
`certificate.ready` (so the GUI report shows the seal link via the existing
`injectCertificate`) and each wrapped in try/except exactly like geometry_study
so a certificate can never take down a good mission.

- **workflows/aircraft_optimization.py** - subject "300-passenger twin-aisle
  airliner, planform study", headline L/D +- 95% CI, solver
  "OpenVSP VSPAERO, vortex lattice" only when the finalists are actually solved
  (else "Conceptual drag-polar sizing model"), full three-channel table from the
  mission's `channels` (input MC, numerical grid-discreteness, model from the UQ
  airliner-anchors study where the fingerprint matches).
- **workflows/valve_study.py** - subject "Idealized trileaflet aortic valve,
  systolic configuration", cycle-weighted loss with the RSS-combined 95% band
  (`combine_expanded(...).combined_95`), three channels (input MC envelope,
  phase-quadrature numerical, correlation-family model) from the stored valve
  study.
- **workflows/race_study.py** - subject NACA 4412, the measured speedup and the
  path agreement as the headline results, three channels from the real race
  numbers (input ensemble + reduced-order surrogate residual).

Certificate subjects use the owner's exact comma-form phrasing (no em dash on
the sealed, on-camera document) and pass `geometry=<registry key>` so the seal
payload carries the proper slug. Tests: each workflow test asserts
`certificate.ready`, the human number, the dir, and the seal; valve adds a test
that a raising `build_certificate_v2` still returns rc 0 with no
`certificate.ready`.

## 2. P0 - prompt-named body resolution (the NACA-got-the-motorcycle bug)
Root cause confirmed: geometry-study only honored `params["surface"]` (an upload
or a literal `*.stl`); a body NAMED in the prompt fell to `DEFAULT_SURFACE`
motorBike. Fix is **router-level** (so the route panel reflects it):

- **chief_engineer/router.py** - `_NAMED_BODIES` maps prompt vocabulary
  (`naca 4412`/`4412`, `naca 0012`/`0012`, `b-52`/`b52`/`stratofortress`,
  `motorcycle`/`motorbike`) to staged surfaces; `resolve_named_body()` stages
  from `models/curriculum/<body>` if the file is missing (all four are already
  staged, so this is defensive). `classify()` sets `params["surface"]` when a
  known body is named and no file/literal was given, and adds a geometry-study
  evidence line. A recognized body with no staged surface sets
  `params["surface_unavailable"]` instead.
- **workflows/geometry_study.py** - when `surface_unavailable` is set and no
  surface resolved, the study states, on the record, that it will not solve a
  different body and pass it off, and stops - it never silently solves the
  default.

Router + workflow tests for every DEMO_RUNBOOK directive (B-52, motorcycle,
NACA 4412, NACA 0012, uploaded-literal-wins, unstaged-flagged), including that
the motorcycle directive STILL resolves to motorBike.obj and the race directive
(which also says "NACA 4412") still wins race-comparison.

## 3. Valve visuals
- `CANDIDATE_ANGLES` 4 -> 11 (30..80 deg, 5 deg steps): the three-leaflet valve
  visibly cycles open many more times; every candidate is a real reduced-order
  evaluation with its MC envelope; min-orifice still marks 30/35 deg infeasible;
  landscape/dispatch/trace scale up proportionally.
- Upper bound held at **80, not 85**, deliberately: the orifice grows
  monotonically, so 85 would win and move the headline off the runbook's 80 deg.
  Owner asked to "keep the winner physics consistent (same 80 deg region)", so
  the winner stays exactly 80 deg / 1327 Pa. (If you actually want it pushed to
  85, it's a one-line range change plus a runbook narration edit.)
- The systolic waveform PNG was NOT dropped in a merge: `waveform_figure(...)`
  runs and `announce_plot` emits `plot.ready` at plan time; verified on the live
  run (plot.ready = 1) and it leads the report figures (GUI collects
  `state.plots`).
- **UQ fingerprint**: checked `setup_fingerprint` - it has no candidate-set
  field, so changing `CANDIDATE_ANGLES` does not change the valve fingerprint;
  the stored `aortic-valve` study still matches (pending=False, numerical+model
  present). No study or fingerprint update needed, confirmed honestly in-code
  and on the run.

## 4. End-to-end verification -> demo-output/acts/round3/
Live run on :8768. See `demo-output/acts/round3/VERIFICATION.md`,
`summary.json`, the three `*.events.json`, the three sealed `*_certificate.pdf`
(+ extracted `*_certificate.txt` content proof), and
`valve_systolic_waveform.png`. Highlights:
- NACA directive (no upload) -> surface `naca4412_wing.stl`, report "Geometry
  study: NACA 4412 finite wing", cert C-2026-7069 subject "NACA 4412 finite
  wing", zero motorcycle mentions. P0 fixed end to end.
- Airliner cert C-2026-7080; valve cert C-2026-8945 (1327 Pa +- 441 Pa, 11
  candidates, waveform present).

## Merge risks / notes for other streams
- `control_room.html` belongs to GUI-3 tonight; I did **not** touch it. My GUI
  needs already exist: `certificate.ready` -> `injectCertificate` (seal link),
  `plot.ready` -> report figures, the denser candidate/landscape stream.
- Pre-existing cosmetic (not mine, out of scope): the geometry_study certificate
  double-prints "+- +-" because its report `envelope` already embeds "+-" and
  build_certificate_v2 adds one. My three new certificates split value/envelope
  and render cleanly ("1327 Pa +- 441 Pa"). Worth a one-line fix in
  geometry_study's results dict if you want it consistent.
- Setting `params["surface"]` on the race route (it also names "NACA 4412") is
  harmless - race_study ignores surface - and is correct on the route panel.
- One stray uncommitted binary `sdk/geometry/motorBike.obj` (a field-paint
  regeneration) was stashed before the merge to keep the tree clean; recover with
  `git stash list` if it's wanted.
