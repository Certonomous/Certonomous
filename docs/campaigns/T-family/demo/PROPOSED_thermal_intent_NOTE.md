# The thermal display intent: design note for a patch that is NOT applied

**Status: PROPOSAL. NOT APPLIED. NOT LIVE.**
Prepared by the heat-transfer team, 2026-09-01. The patch it describes is
`docs/campaigns/T-family/demo/PROPOSED_thermal_intent.patch`, in this same
directory. Nothing under `sdk/` was written. The control-room server was
running at pid 654212 for the whole of this work and was not restarted,
stopped, signalled or otherwise touched.

**Who has to read this before it lands.** The heat-transfer supervisor reads
the patch as a diff (`SUPERVISION_CHARTER.md` §3 check 1), and then the cfd
team reviews it, because `sdk/chief_engineer/router.py` is shared control-room
tooling owned by neither team and its routing table governs every team's
prompts. Applying it is a human decision and restarting the server is a
separate human decision; neither was taken here.

**What it is for.** Sanaa ruled option 1 + 2 on 2026-09-01
(`etc/sessions/2026-09-01T0032Z_sanaa_thermal_acts_full_spec.md`, commit
`a3793b8f`). Option 2 is a thermal display mission: the GUI presents screens
A1 to A9 and C1 to C9 **from runs that have already landed**. Pure
presentation. No new solving. That constraint is what makes it achievable in
the time available and it is not relaxed anywhere in this patch.

---

## 1. The headline, because it changes who has to approve this

**The narrow edit is achievable, and it is narrower than anyone asked for: the
patch edits the refusal list ZERO times.**

`_OUT_OF_SCOPE_DOMAINS` is not touched. Not narrowed, not widened, not
reordered. Every prompt that reaches a refusal today reaches the same refusal
with the same wording after this patch.

That is possible because of a structural fact that has to be stated plainly,
since the brief this lane was given assumed the opposite:

> **The refusal list is consulted only when NOTHING routed.**

Measured. `out_of_scope_domain()` has exactly one caller in the whole
repository outside the tests: `server._explain_unparsed`
(`sdk/chief_engineer/server.py:821`, the domain read at `:827`). That function
is reached only from `_run_mission` (`:798`), which `_start_mission` selects
only when `WORKFLOWS.get(route.intent)` is `None`
(`sdk/chief_engineer/server.py:752-756`). A request that matches an intent with
a workflow entry never reaches the refusal list at all.

This is already visible in the shipped product and is not a new idea
introduced here. Driven through `classify()`, the prompt
`"Supersonic wedge at Mach 2.5, measure the oblique shock angle."` routes to
`supersonic-wedge` **and** `out_of_scope_domain()` returns
`"compressible or supersonic flow"` for it. The act runs. The refusal is
computed and discarded, because the lab has that act and the router says so by
routing. The thermal display intent uses exactly the same mechanism: the lab
has these two acts, the router says so by routing, and the refusal list is left
alone to keep refusing everything else.

**Consequence for approval.** This is not a request to weaken a shared
guardrail. The shared refusal list is byte-identical before and after. What is
being asked for is one new intent, one new workflow module and one entry in an
existing tuple.

---

## 2. Shape of the router, with line numbers

Read against `sdk/chief_engineer/router.py` as committed at the base of the
patch, 784 lines.

**How an intent is declared.** A module-level string constant, `:43-56` and
`:83-86, :94, :173`. The value is the wire name (`"geometry-study"`,
`"sobol-sensitivity"`); nothing else registers it.

**How an intent is matched.** One `re.Pattern` (or a small group of them) at
module level, and one scoring branch inside `classify()` (`:390-716`).
`classify` builds a `scores` dict through a local `add(intent, weight, why)`
(`:412-414`), picks `max(scores)` (`:562`), and derives confidence as that
intent's score over the sum of all scores (`:563-564`). Weights are the whole
priority mechanism and they are conventional, not enforced: 0.5 to 1.4 for
generic signals, 1.6 to 2.0 for a named body or a named method, 2.2 for the
Sobol decomposition. Every branch also has an entry in the `rationale` dict at
`:615-711`, and that dict is indexed with `[intent]`, so **an intent with no
rationale entry raises `KeyError` at classify time**. It is not optional.

**How a mission is registered, and its interface.** One row in `WORKFLOWS`
(`:749-784`), `{"module": "workflows.<name>", "output": "<wire-name>"}`. The
server imports that module by name and calls
`module.main(request=..., params=route.params, emit=record.bus.publish)`
(`sdk/chief_engineer/server.py:762-777`). That is the entire interface: a
module-level `main(request, params, emit)` returning an int. Everything else a
workflow does it does by emitting events.

**Where the refusal list sits relative to intent matching.** Strictly after,
and only on the fallback branch. Declared `:294-320`, read by
`out_of_scope_domain` `:321-326`, consulted only at
`sdk/chief_engineer/server.py:827` inside `_explain_unparsed`, reachable only
when `WORKFLOWS.get(route.intent)` is `None`. `classify()` itself never calls
it.

**The upload path, and why it is load-bearing here.** `apply_surface`
(`:727-745`) reroutes any intent not in `_SURFACE_KEEPS_ROUTE` (`:719-724`) to
`geometry-study` when a surface is uploaded. Sanaa's screens A1 and C1 are
upload-plus-prompt. Measured at HEAD: `"Thermal map of this motor in a duct."`
with `motor_in_duct.stl` uploaded classifies to `geometry-study` at confidence
0.99. Without the `_SURFACE_KEEPS_ROUTE` entry this patch adds, the thermal
prompt would put the incompressible aerodynamic chain on the motor. That is the
single easiest thing to miss in this change and it is why the entry is in the
patch.

**What a mission returns to the GUI to present a screen.** Nothing is returned.
Everything is emitted:

| Event | Payload | What the GUI does |
|---|---|---|
| `transcript.entry` | role, message, citations | a line in the paced feed |
| `transcript.table` | title, headers, rows, `table_id`, `append` | a compact table in the feed |
| `plot.ready` | `beat`, `file`, `title`, `url` | renders `<img src=url>`, `control_room.html:1650` |
| `field.ready` | `beat`, `file`, `label`, `url`, `bounds` | the 3D viewport |
| `geometry.ready` | `url`, `label` | the body in the viewport |
| `report.ready` | the `lab_report()` document | the report panel |
| `agenda.updated`, `result.verdict`, `solver.selected`, `mission.note` | as named | their own panels |

The helpers are in `sdk/workflows/__init__.py`: `announce_plot` `:58-65`,
`announce_geometry` `:68-81`, `emit_table` `:152-176`, `announce_field`
`:179-199`.

**The one constraint on figures.** `plot.ready` urls are served by
`server._serve_artifact` (`:392-397`), which requires a **`.png`** under
`<CERTONOMOUS_OUTPUT>/<beat>/`. The landed Act C figures are PDF and SVG only,
so the display mission resolves each figure to a PNG at present time (a PNG
beside the vector page if one exists, otherwise `pdftoppm` on the PDF) and
copies it into the mission output directory. That is a rendering step on a page
that already exists. It derives no number and starts no solver.

---

## 3. The narrowest edit, and what still refuses

The distinguisher is **the body, not the physics word**. The lab has landed
conjugate thermal runs for exactly two bodies and has no general thermal chain
the control room may point at an arbitrary body. So:

```
thermal vocabulary  AND  a body whose run has landed   ->  thermal-display
thermal vocabulary  AND  anything else                 ->  unchanged, today's route
```

Both conditions are required. `thermal_landed_body()` returns `(None, None)`
the moment either fails, the scoring branch adds nothing, and the request keeps
whatever it had. Adding a third body when its run lands is one row in
`_THERMAL_LANDED_BODIES` and one screen set in `workflows/thermal_display.py`.

**After the patch, the router still refuses** every prompt it refuses today,
because the refusal path is unchanged. Measured examples that still reach it:

- `"Do a thermal analysis of the motor and tell me the peak temperature."`
  Names a motor with no enclosure, so no landed body matches. Refused,
  `heat transfer or thermal analysis`.
- `"Nusselt number on the cooling channel."` Refused. This one is worth
  keeping: the Act C run does **not** resolve the coolant as a fluid region, so
  there is no Nusselt number to give and refusing is the honest answer.
- `"Simulate boiling in the coolant loop."` Refused, `heat transfer or thermal
  analysis`.
- `"Simulate how the cube melts in a fire."` Refused, `melting or phase change`.
- `"Model the combustion in the chamber."` Refused, `combustion or fire`.

**A known boundary the reviewers should rule on.** The Act A pattern requires
the enclosure word (`duct`, `enclosure`, `housing`, `cowling`) near `motor`.
A prompt that says only "the motor" does not route to the display act. That is
deliberate, because widening to a bare `motor` would capture "thermal analysis
of the motor in my rocket", which this lab cannot answer. If the filmed Act A
prompt will not name the duct, the pattern needs one more alternative and the
reviewers should say so before this lands rather than after.

---

## 4. The measured before and after, driven through `classify()`

Thirty probe prompts across aerodynamics, optimisation, uncertainty, closure,
deadline and thermal, driven through the router's own `classify()` and
`out_of_scope_domain()`. Both runs were made from the same scratch directory so
that the staged-geometry path resolution is identical in both and cancels; the
comparison is therefore of the patch and nothing else.

`dispatch` is what `server._start_mission` would do: **act** when the intent
has a `WORKFLOWS` entry, **refusal path** when it does not.

| Group | Prompt | Before | After | Changed |
|---|---|---|---|---|
| aero | Solve the drag on this aircraft and paint the pressure field. | geometry-study 0.67, act | geometry-study 0.67, act | no |
| aero | Run the motorbike geometry and report the forces with an envelope. | geometry-study 0.81, act | geometry-study 0.81, act | no |
| aero | Ahmed body with a 25 degree rear slant, grade the drag. | ahmed-body 0.80, act | ahmed-body 0.80, act | no |
| aero | Supersonic wedge at Mach 2.5, measure the oblique shock angle. | supersonic-wedge 0.99, act | supersonic-wedge 0.99, act | no |
| aero | Hypersonic cylinder shock standoff please. | hypersonic-cylinder 0.99, act | hypersonic-cylinder 0.99, act | no |
| aero | Vortex shedding off a cylinder, give me the Strouhal number. | cylinder-vortex-shedding 0.99, act | cylinder-vortex-shedding 0.99, act | no |
| aero | NASA wall-mounted hump: separation and reattachment. | nasa-hump 0.99, act | nasa-hump 0.99, act | no |
| opt | Cut the drag on the wing by at least 20 percent using the adjoint, and verify the gradient against finite differences. | adjoint-optimization 0.79, act | adjoint-optimization 0.79, act | no |
| opt | Maximise lift-to-drag for a 180 passenger airliner at cruise. | aircraft-optimization 0.70, act | aircraft-optimization 0.70, act | no |
| opt | Minimise the drag of this cylinder by changing its diameter. | shape-optimization 0.99, act | shape-optimization 0.99, act | no |
| opt | Which input owns the variance in the drag envelope? Sobol please. | sobol-sensitivity 0.99, act | sobol-sensitivity 0.99, act | no |
| uq | How confident are we in that drag number, and can we tighten the error bars? | uncertainty-reduction 0.99, act | uncertainty-reduction 0.99, act | no |
| closure | Run a k-omega SST RANS case on this duct and report the wall shear. | geometry-study 0.77, act | geometry-study 0.77, act | no |
| closure | Compare the LES and RANS closure on the periodic hill. | geometry-study 0.99, act | geometry-study 0.99, act | no |
| time | I need an answer in 30 minutes, trade fidelity for speed. | time-constrained 0.99, act | time-constrained 0.99, act | no |
| thermal A | Thermal map of this motor in a duct. | unseen-geometry 0.99, act | **thermal-display 0.77, act** | **YES** |
| thermal A | Run conjugate heat transfer on this motor-in-duct geometry. | unseen-geometry 0.58, act | **thermal-display 0.67, act** | **YES** |
| thermal A | Do a thermal analysis of the motor and tell me the peak temperature. | general-mission, refusal path | general-mission, refusal path | no |
| thermal A | Thermal management study: will the motor stay under 200 C in the duct? | unseen-geometry 0.99, act | **thermal-display 0.77, act** | **YES** |
| thermal A | What is the conduction path from the motor to the duct wall? | unseen-geometry 0.99, act | **thermal-display 0.77, act** | **YES** |
| thermal C | Show me the battery module thermal results, the per cell temperatures. | general-mission, refusal path | **thermal-display 0.99, act** | **YES** |
| thermal C | Conjugate heat transfer on this battery pack over the takeoff pulse. | general-mission, refusal path | **thermal-display 0.99, act** | **YES** |
| thermal C | Thermal analysis of the battery module: pack uniformity over time. | general-mission, refusal path | **thermal-display 0.99, act** | **YES** |
| thermal C | Nusselt number on the cooling channel. | general-mission, refusal path | general-mission, refusal path | no |
| refuse | Simulate how the cube melts in a fire. | refusal path, melting or phase change | refusal path, melting or phase change | no |
| refuse | Model the combustion in the chamber. | refusal path, combustion or fire | refusal path, combustion or fire | no |
| refuse | Run a conjugate heat transfer study on a rocket nozzle I am designing. | unseen-geometry 0.99, act | unseen-geometry 0.99, act | no |
| refuse | Do a thermal stress analysis of the turbine blade. | unseen-geometry 0.99, act | unseen-geometry 0.99, act | no |
| refuse | Model the heat transfer on the wing. | unseen-geometry 0.99, act | unseen-geometry 0.99, act | no |
| refuse | Simulate boiling in the coolant loop. | refusal path, heat transfer or thermal analysis | refusal path, heat transfer or thermal analysis | no |

**Seven rows change. All seven are thermal. All seven name a body whose run has
landed.** No aerodynamics, optimisation, uncertainty, closure or deadline
prompt changes intent or confidence. No currently-refused prompt becomes
accepted.

The upload path, separately:

| Prompt, with `motor_in_duct.stl` uploaded | Before | After |
|---|---|---|
| Thermal map of this motor in a duct. | geometry-study 0.99 | thermal-display 0.77, `thermal_screens=A` |
| Conjugate heat transfer on this battery pack over the takeoff pulse. | geometry-study 0.90 | thermal-display 0.99, `thermal_screens=C` |

### 4a. A correction to the measurement this lane was handed

The brief stated that `"Run conjugate heat transfer on this motor-in-duct"` is
**REFUSED** at HEAD. Driven through the dispatch path, it is not. It classifies
to `unseen-geometry`, which has a `WORKFLOWS` entry, so the server takes the
workflow branch and the refusal list is never read. `out_of_scope_domain()`
does return `"heat transfer or thermal analysis"` for that string, which is
almost certainly what was measured, but that return value is discarded for this
prompt. The distinction matters to the review: the change is smaller than the
brief assumed, because there was less refusal in place than it looked.

### 4b. A pre-existing defect this patch does not fix, and does not hide

Three probe prompts that **should** refuse do not refuse at HEAD, and still do
not after the patch, because they route to `unseen-geometry`:

- `"Run a conjugate heat transfer study on a rocket nozzle I am designing."`
- `"Do a thermal stress analysis of the turbine blade."`
- `"Model the heat transfer on the wing."`

Each names a candidate geometry (`nozzle`, `blade`, `wing`), which scores
`unseen-geometry` at 0.7, which has a workflow, which bypasses the refusal.
The `unseen-geometry` act then reasons about the nearest solved cases and
refuses to quote a magnitude, so the outcome is not dishonest, but it is not
the domain refusal the list was written to give either.

This is a defect in the refusal **architecture**, not in the refusal **list**:
the list is checked last instead of first. Repairing it means consulting
`out_of_scope_domain()` before dispatch rather than after failure, which would
change behaviour for every team and would need its own before-and-after. It is
raised here for the cfd and verification teams and is deliberately out of scope
for a patch whose job is to let a landed result be shown on screen.

---

## 5. The display mission, and how it degrades

`sdk/workflows/thermal_display.py`, new file in the patch.

It starts no solver, writes no case, queues no job, invokes no solver binary
and books no compute. It reads a screen bundle, puts figures and tables up, and
stops.

| Screen set | Body | Bundle it reads |
|---|---|---|
| `A` | the motor in a duct | `docs/campaigns/T-family/demo/figures_actA/acta_screen_data.json` |
| `C` | the battery module | `docs/campaigns/T-family/demo/figures/actc_screen_data.json` |

The Act C bundle landed at commit `8be3d8fc` alongside its figures. The Act A
folder is referenced by path and **is empty at the time of writing**; it is
being built by a sibling lane. The mission depends on no file existing.

**Order of the beats, and it is deliberate.** Provenance first (source case,
reader, mesh cells, geometry guard), then the planted-zero instrument checks
from the bundle, then the figures, then the tables, then the quantities. A
reader that could not see its own planted perturbation is therefore visible on
screen **before** any number is quoted, and if any check reports not-seen the
act says on the record that every number below it is unverified. The Act C
bundle carries two such checks, both `seen: true`, planting 1.0 K across all
960 cells at t = 900 s and 2.5 K into cell 137 at t = 300 s.

**How it degrades, measured, not asserted.** Dry-run against both screen sets,
with output redirected to a scratch directory so nothing was written into the
running server's artifact tree:

- Act C, bundle present: `rc=0`. Four `plot.ready` events, four
  `transcript.table` events, one `report.ready`, one `agenda.updated`. The four
  PNGs were produced from the landed PDFs and one was opened and read; it is
  the pack-uniformity page, legible, carrying its own printed note that no
  outlet coolant temperature exists in this configuration.
- Act A, bundle absent: `rc=1`. **Zero** `plot.ready` events, zero tables, no
  `report.ready`. The transcript names the exact path that was empty and states
  that nothing is drawn in its place and no number for that body appears
  anywhere below. No blank panel, no placeholder, no borrowed figure.

**What it refuses to invent.** The Act C run does not resolve the cooling
channels as a fluid region, so there is no coolant stream and no outlet
temperature. The bundle records that as a string beginning `NOT DEFINED`, the
mission surfaces every such string as its own transcript line, and the
uniformity figure prints the same statement on its face. The uncertainty column
says one mesh and one time step were run, so no discretisation error estimate
is available, and it carries that sentence rather than a number nobody
measured.

**House rules.** `sdk/tests/test_register.py` scans every module under
`workflows/` and `chief_engineer/` for em dashes, en dashes and self-grading
narration in user-visible strings. Run against the patched tree: 94 passed, 1
failed. The one failure is `test_no_prose_double_hyphen`, with **8 offenders,
every one of them in `workflows/rae2822_case9.py`**, which this patch does not
touch. The identical check run against the unpatched tree reports **the same 8
offenders**. The failure is pre-existing and neither the new workflow module
nor the router hunk contributes to it. `test_orchestration_stack.py`,
`test_ahmed_routing.py` and `test_sobol_mission.py` pass against the patched
tree.

---

## 6. The restart question. NOT PERFORMED.

Nothing below was executed. The server was inspected read-only through `/proc`
and `ss`; it was never signalled.

**The process.** pid **654212**, `python3 -u -m chief_engineer.server`, cwd
`/home/ubuntu/Certonomous/sdk`, parent pid 654211 (a detached bash, itself
parented to init), listening on **0.0.0.0:8765**, up since 2026-08-31 23:48:17,
RSS about 441 MB. It was started with these environment variables set, read
back from `/proc/654212/environ`:

    CHIEF_ADAPTER=openfoam
    CERTONOMOUS_SOLVE_RANKS=16

**The command.** Stop the process, then from `/home/ubuntu/Certonomous/sdk`:

    CHIEF_ADAPTER=openfoam CERTONOMOUS_SOLVE_RANKS=16 \
      setsid python3 -u -m chief_engineer.server >> <logfile> 2>&1 &

**Both environment variables are mandatory and both fail silently if dropped.**
Without `CHIEF_ADAPTER=openfoam`, `_backend_name()` returns `synthetic` and the
entire control room switches off the real solvers with no error on screen.
Without `CERTONOMOUS_SOLVE_RANKS=16` the rank count falls back to the default
of 1 (`head_engineer.py:1455`), so every solve runs serial. Neither shows up as
a failure; both show up as a demo that quietly stops being the thing it was.

**How long it is down.** Measured in a separate process, not by restarting
this one: importing `chief_engineer.server` takes **0.08 s**, and
`_rehydrate_missions()` reads the **765** persisted mission records under
`sdk/chief-engineer-runs/mission-state/` in **1.03 s**. So the server is
unavailable for **about 1.1 s of startup**, plus whatever wall time passes
between the operator's stop and start. The listening socket sets
`allow_reuse_address`, so the port is immediately rebindable. Honest caveat:
these are the two dominant startup terms measured on this box now; the true
stop-to-serving interval was not measured, because measuring it means
restarting the server.

**What in-flight state is lost.**

1. **Any mission that is queued or running is lost and is marked failed.**
   `_rehydrate_missions` (`server.py:209`) rewrites any record still in
   `queued` or `running` to `failed` with the reason
   `"Mission interrupted by a service restart. Existing evidence remains
   replayable."` and publishes `mission.failed` on its bus. Its worker thread
   is a daemon and dies with the process. A solve in progress does not resume.
2. **Every open SSE stream breaks.** Each viewer's `EventSource`
   (`control_room.html:739`) will attempt the browser's automatic reconnect;
   the page installs `src.onerror = () => {}`, so a viewer sees the feed pause
   silently rather than seeing an error. Events already written to the
   mission's event file are replayable to a reconnecting client.
3. **Completed missions survive.** Their state files and event files are on
   disk and are rehydrated, so their transcripts, tables and reports remain
   replayable.
4. **Mission ids survive; in-memory-only state does not.** There is no
   in-memory state a viewer depends on beyond the live stream.

**Recommendation.** Restart between Sanaa's sessions, with no mission running,
and confirm afterwards that `/health` reports `backend: openfoam-real-solvers`
rather than `openfoam-synthetic`. Scheduling that is the chief's call. This
lane did not do it and is not asking to.

---

## 7. What this lane could not verify

- **The exact filmed prompt wording.** No Act A or Act C prompt text exists on
  disk; `ACT_A_thermal_map_sheet.tex`, `ACT_C_battery_module_sheet.tex` and
  `README_SOURCES.md` carry no prompt. The patterns were designed against the
  phrasings in Sanaa's spec and the brief and are documented above so a
  reviewer can widen them deliberately rather than discover the gap on camera.
- **The Act A screens themselves.** `figures_actA/` was empty throughout. The
  mission's Act A path was exercised only in its absent-bundle form, which is
  the honest-degradation path and passed. The present-bundle path for Act A has
  never run against real Act A files and cannot be until they land. The bundle
  key names (`acta_screen_data.json`, and the four figure stems in
  `SCREEN_SETS["A"]`) are a **proposed contract with the sibling lane**, not an
  observed one; if that lane names its files differently, the table needs the
  matching names before Act A will show anything.
- **End-to-end behaviour through the running server.** The routing was driven
  through the real `classify()` and `apply_surface()`, and the mission was run
  directly with an isolated output root, but no request was ever put through
  pid 654212 and no patched server was started. Whether the GUI lays the four
  figures out acceptably on screen is unverified.
- **No verdict from the fixed vocabulary is claimed here.** This is a proposed
  change to tooling, not a graded run. There is no gate, no threshold and no
  pre-registration, so `PASS`, `GATE REACHED` and `GATE FAIL` do not apply and
  none is asserted.

## 8. Compute

No solver ran. No queue entry was made. No case was written. The compute
consumed by preparing this proposal was four `pdftoppm` page conversions and
one test-suite run, all on this box, all under a minute of single-core work;
against the lab's unit that is well under one core-minute. There was no
pre-registered estimate to calibrate against under rule 12 because no solver
run was proposed, and none is proposed by the patch either. The runs whose
results these screens present carry their own costs in their own records; this
mission books nothing against them and its `report.ready` states
`spent_core_minutes: 0.0` with the note `no solver ran on this request`.
