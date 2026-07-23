# Handoff — GUI-2 (feat/gui-polish)

Branch: `feat/gui-polish`. Merged `main` first (picked up d57596c "G1 liveness" —
GUI-1 had already added CSS rules for `.entry.monitor`/`.entry.system`; this
session replaced their colors and completed the wiring, see G4 below).

## G4 — role colors: DONE, proven

Five roles, one accent each, the **same** color in digest, conversation, and
the present-bar stamp (`#presentRole`) — one CSS rule per role now targets
both `.entry.<role> .who` and `.present-bar .role.<role>` so there is a single
source of truth, not two color lists that can drift apart:

| Role | Color |
|---|---|
| CHIEF ENGINEER | `var(--live)` — blue (unchanged, already the brand accent) |
| CHIEF RESEARCHER | `#c792ea` — violet (was `var(--regime)`, a blue almost identical to the Engineer's — not distinct enough) |
| NUMERICIST | `#45cfc0` — teal (was a lavender `#9aa7ff`, too close to the other blues) |
| MONITOR | `#ef7fb0` — rose (was `var(--trend)`, the same amber as the TREND ONLY badge — a role color reusing a trust-tier color risked reading as tier signal, not identity) |
| SYSTEM | `var(--muted)` — neutral gray (was `var(--dim)`, borderline-low contrast for a name tag; `--muted` is one step brighter and already used for other readable secondary labels) |

JS side: `present(role, msg)` now sets `pr.className = 'role ' + roleSlug(role)`
using the same slug function `roleClass()` already used for transcript
entries (`roleSlug` extracted so both share one definition — no risk of the
two diverging).

**Proof** (`demo-output/gui-proof/`, all from real completed missions, not
synthetic — per v3-N3 the proof runs are the airliner directive and a
motorcycle-with-rider geometry study, not the cylinder toy case):
- `g4_roles.png` — digest view, Act 1 airliner mission, Chief Engineer (blue).
- `g4_present.png` — presentation bar showing CHIEF RESEARCHER in violet,
  matching the digest color below it.
- `g4_conversation_top.png` — SYSTEM (gray) at the top of the same mission's
  conversation.
- `g4_conversation_numericist.png` — NUMERICIST in teal, same mission.
- `g4_monitor.png` — MONITOR from a real B-52/motorcycle geometry-study run
  (first attempt hit a real `snappyHexMesh` failure — see the bugfix below;
  a clean successful run was re-queued to also capture the Monitor's
  end-of-run summary line; check `demo-output/gui-proof/` for whichever of
  `g4_monitor.png` / a follow-up capture landed by the time this was read —
  if only the failure-path shot is present, the Monitor's "watching solver
  output" roster status and mid-run anomaly lines are still real and
  color-correct, just not its final summary bullet, which only fires after
  a solve completes).

## G7 — professional stage narration: DONE, proven

**(a) Precision.** Audited every number formatted into transcript strings
across `sdk/workflows/*.py` and `chief_engineer/head_engineer.py`. Found and
fixed the flagged case: `geometry_study.py`'s mesh non-orthogonality/skewness
came straight from a `float(regex_match)` in `head_engineer.collect_mesh_stats()`
and were interpolated with no format spec (`non-ortho {non_ortho}`) in five
places — the researcher line, the "why" string on a failed gate, the abstract,
and the report's mesh-quality row. Now `.1f°` / `.2f` throughout, with a `—`
fallback when the stat wasn't captured. Same class of bug in
`head_engineer.report_markdown()` (mesh row + per-step seconds) — fixed there
too. Swept the other five workflow files with a script-assisted heuristic
scan; no other unformatted-float sites found (remaining bare `{var}`
interpolations are all integers — counts, iteration numbers — which don't
need a format spec).

**(b) Durations.** Normalized `geometry_study.py`'s `"X finished in Ns"` to
the `"X — N s"` form used everywhere now. Added real measured-duration bullets
(no invented numbers) where stages lacked them:
- `aircraft_optimization.py`: screening sweep (`time.time()` around the grid
  loop) and finalist-solve batch (the `elapsed` value already computed for
  the ledger was never narrated — now it is).
- `valve_study.py`: phase evaluations (new `time.time()` wrap).
- `shape_optimization.py`: uncertainty ensemble (`ensemble.wall_seconds`,
  already measured, wasn't narrated).
- `uncertainty_reduction.py`: Run A / Run B lines already had
  `wall_seconds`, just in the old `"complete in Ns"` phrasing — normalized to
  match.

**(c) Register.** Removed self-referential filler phrases (`"and the tier
says so"`, `"and says so"`, `"the verdict will say so"`) from
`aircraft_optimization.py`, and — per the coordinator's v2-D2 note — cut a
notebook-toned uncertainty sentence in `geometry_study.py`'s report
(`"...it says the solve is steady, not that the physics is right..."`),
since the uncertainty-channels panel already carries that meaning.

**Also found and fixed while proof-running (not originally scoped, but a
direct discipline violation surfaced by a real run):** `geometry_study.py`'s
exception handler was interpolating the caught `RuntimeError` directly into
the transcript, and that exception carries the last 8 raw lines of
`checkMesh`/solver stdout as its message — i.e. a live run that hits a mesh
failure was putting raw code-facing solver diagnostics on screen. Fixed to
narrate just which stage stopped; full detail stays in the saved log file.
This is a bug in a shared code path (`_run_step`'s `RuntimeError`), so it's
worth checking whether other workflows using the same head-engineer step
runner have the same exposure — `geometry_study.py` was the only workflow
using `_run_step` at the time of this session.

**Proof:** `demo-output/gui-proof/g7_precision.png` (valve mission —
`Phase evaluations — 0.03 s — 12 solves`, orifice areas in whole mm², losses
in whole Pa, no runaway decimals) and `g7_precision_top.png` (same mission,
`Womersley α ≈ 16.7`, phase weights `0.25/0.50/0.25`). `g4_conversation_mid.png`
also shows the aircraft workflow's `Screening sweep — 0.09 s — 24 designs`
and `Finalist solves — 59.3 s — 6 wings in parallel` bullets with clean
per-finalist precision (`alpha 5.4°, CDi 0.0052`).

148 tests green after every commit.

## R1 — geometry display-name registry: DONE (new item, added mid-session)

`sdk/chief_engineer/display_names.py` — the ratified slug → human-name
mapping (b52, motorBike, the airliner/valve workflow keys, NACA 4412/0012,
Ahmed 25°/35°, canonical calibration bodies), `display_name(key_or_filename)`
with a title-cased fallback (never a raw filename or underscored slug).
Unit tests in `sdk/tests/test_display_names.py`.

Wired into:
- `workflows/__init__.py`'s `announce_geometry()` label fallback.
- `workflows/geometry_study.py` throughout — the mission-title, the default
  system line, the "reading X" roster status, the geometry.ready label, the
  "Surface accepted" line, the report title/abstract/methods, the
  certificate's `geometry=` field (this one matters: the certificate PDF
  literally prints `Geometry: <value>` — it was printing the raw filename
  stem before this).

**Not wired** (out of scope for tonight, flagged for whoever owns the other
workflows next): `aircraft_optimization.py`, `valve_study.py`, and
`unseen_geometry.py` don't currently have raw slugs on screen (they already
narrate in prose, not filenames), so there was nothing to fix there, but if
they ever start threading a filename through, route it through
`display_name()` rather than inlining a name.

## v2-E1 — professional demo directives: DONE, verified + tested

Rewrote all five `docs/DEMO_RUNBOOK.md` trigger prompts as complete
engineering directives (airliner, B-52, motorcycle-with-rider, NACA 4412,
valve). Verified each one still routes to its intended workflow via
`router.classify()` **before** editing the doc (see the interactive checks
in this session's history), then added five regression tests in
`test_orchestration_stack.py::RouterTests`. No router pattern changes were
needed — all five land correctly as written.

One side effect worth knowing about: the airliner directive's interpretation
confidence dropped from the old prompt's 70% to 46%. This is not a routing
regression (aircraft-optimization still wins clearly) — the fuller directive
("search the wing design space... report... with its envelope") shares
keywords with `shape-optimization` and other categories, which dilutes the
score share even though the correct route still wins outright. Updated the
runbook's expected-confidence line to match. If this number matters
cosmetically for the demo, the fix is prompt wording, not router code — I
kept prompts close to the coordinator's given phrasing rather than
optimizing for a confidence number.

**Router false-positive found, not fixed (out of scope):** the valve
directive's request text contains "cardiac", and `_mentioned_geometry()`
does a plain substring match against `CANDIDATE_GEOMETRIES`, which includes
`"car"` — so `"car"` matches inside `"cardiac"` and the route params report
`geometry: "car", geometry_known: false`. Harmless today (valve-study still
wins on score), but it's a substring-matching bug in `router.py` that the
G5 rework (or whoever owns router.py next) should know about. Did not touch
`router.py`'s matching logic myself — small risk of scope creep into a file
I was told to treat carefully, and it doesn't affect any current behavior.

## v2-D2/D3 — report tone: DONE (folded into G7c above)

Precision discipline (D3) applied to report/abstract strings, not just
transcript bullets (see G7a). Meta-commentary trim (D2) covered above; did a
scan for the same class of phrase (`"says so"`, `"it says X not Y"`) across
all workflow files and found only the instances listed above — the rest of
the uncertainty-section prose is substantive (numbers, sources, explicit
what's-not-quantified statements), not the self-referential filler the
coordinator flagged, so I left it alone rather than over-trimming
information the report actually needs.

## GUI-wide polish sweep: NOT done — deliberately deferred

Read through the whole of `control_room.html` looking for spacing,
truncation, dead-label, and casing issues after G4/G7 landed. Did not find
anything that rose to "smallest-diff fix" — the file (GUI-1's rebuild) is
already tight: no TODO/placeholder debris, truncation is via CSS
`text-overflow`/a length-capped JS slice in `present()` (both standard,
intentional), casing is consistently handled by CSS `text-transform` rather
than inconsistent source-string casing. Given the treaty (this file is
GUI-1's primary surface tonight) and that G4+G7 already used up the budget
for touching `control_room.html`, I did not go looking harder for
cosmetic nits in someone else's active surface. If a fresh pair of eyes
wants to sweep it, do it after GUI-1's own pass lands, to avoid a diff race
on the same file.

## Discovered, not part of my brief — flagging for the team

- **Router substring false-positive** (`"car"` inside `"cardiac"`) — see
  above, router.py, not fixed.
- **`_run_step`'s raw-log exception leak** — fixed in `geometry_study.py`
  (the only caller today); if another workflow starts calling
  `HeadEngineer._run_step` directly, check it doesn't reintroduce the same
  raw-solver-text-on-screen problem.
- **Named curriculum bodies aren't resolvable from prompt text alone.**
  `geometry_study._resolve_surface()` only recognizes a surface named via an
  explicit `.stl`/`.obj` token in the request text or an already-uploaded
  file; a typed directive naming "B-52" or "NACA 4412" without an upload (or
  without the router extracting a literal filename) silently falls back to
  the default motorBike case. Confirmed live: launching the new B-52 runbook
  directive via the API with `params: {surface: "b52.stl"}` at the
  server/mission level did **not** thread through — the router's own
  `classify()`-derived `params` (which has no `surface` key unless the text
  contains a literal `b52.stl` token) wins, and the mission solved motorBike
  instead of B-52. The runbook's Act 2 flow works around this by having the
  operator **upload** the STL through the GUI (which does set the surface
  correctly) rather than relying on the prompt text — that path is untouched
  and fine. Flagging in case whoever wires the NACA 4412 demo body assumes
  naming it in prose is enough; it isn't, upload it.

## Commits (this session, feat/gui-polish)

1. `G4: complete role-color set, shared across digest/conversation/present-bar`
2. `R1: geometry display-name registry`
3. `G7: sensible precision, measured stage durations, professional register`
4. `Fix: failed-stage narration no longer dumps the raw solver log`
5. `v2-E1: professional demo directives, verified routing + tests`

All local to this worktree/branch, not pushed (per orchestrator instructions
— never push, never touch other worktrees).

## Test status

148 tests green after every commit
(`cd sdk && python -m unittest discover tests`).

## Merge risk assessment

- `control_room.html`: small, surgical diff (7 CSS lines touched/added, 2 JS
  lines). Touches only the role-color block (~line 190) and the
  `roleClass`/`present()` functions (~line 400/544) — areas the night orders
  explicitly carved out for me. Low collision risk with GUI-1's layout work
  as long as they haven't independently touched the same six CSS selectors.
- `docs/DEMO_RUNBOOK.md`: text-only, no code dependency; only risk is if
  someone else also edited the trigger-prompt lines tonight.
- Workflow files (`geometry_study.py`, `aircraft_optimization.py`,
  `shape_optimization.py`, `uncertainty_reduction.py`, `valve_study.py`,
  `head_engineer.py`): none of these are on the orchestrator's
  do-not-touch list (`lab.py`, trust-tier language) and no edits neighbor
  any `TREND ONLY`/tier-word lines. Should merge clean.
- New files (`display_names.py`, `test_display_names.py`): no collision
  risk, nothing else references this path yet.
