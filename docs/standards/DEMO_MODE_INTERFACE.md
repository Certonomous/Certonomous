# DEMO MODE — the plug-in interface, v1

**Status: publishable v1. Build against it now.**
Owner: cfd. Consumers: heat-transfer (motor, battery), dafoam (Act D), cfd (jet flap).

The contract is code, not this page: **`sdk/workflows/demo_mode.py`**.
Import it, implement `DemoAct`, call `validate_act` before the shoot. Its own
control is **`sdk/tests/test_demo_mode_contract.py`** (35 tests; every banned
phrase is planted and asserted to raise, so a checker that stopped matching
fails there instead of on camera).

Binding sources: Sanaa's DEMO MODE capture
`etc/sessions/2026-09-01T0340Z_sanaa_demo_mode_binding.md` (`4905abdd`), the
clock amendment `68b10335`, the pacing amendment `aaed6498`, the figure/header
standard `etc/sessions/2026-09-01T0310Z_sanaa_actA_figure_header_standard.md`
(`569346b3`), and DEMO STANDARD v2 R1–R10.

---

## The four questions, answered

**1. Entry point and signature.** Subclass `DemoAct`, then one call at module
end:

```python
from .demo_mode import DemoAct, register_act

class MotorThermalAct(DemoAct):
    name = "motor-in-duct thermal map"
    # ten methods, below

ACT = register_act("motor-thermal", MotorThermalAct())
```

An act **never emits an event, never composes a stage header, never paces
anything, never decides an order.** It answers ten questions and registers.
The sequencer resolves the act by key, runs `validate_act(act)`, and refuses to
start when the returned list is non-empty. Registering one key twice raises
rather than overwriting — two acts on one key is how a shoot shows the wrong
run.

**2. Stage vocabulary and order.** Fixed in `STAGES`, walked by the sequencer,
not reorderable by an act:

`prompt` → `restatement` → `assumption` → `geometry` → `meshing` →
`feasibility` → `solving` → `gates` → `results`

Each has one method returning one frozen dataclass: `Prompt`, `Restatement`,
`Assumption`, `Geometry`, `MeshPlan`, `Feasibility`, `SolveReplay`,
`GatesAndChecks`, `Results`, plus `RunRecord` (stage 0, internal).

**3. How the solving stage is fed.** `SolveReplay` carries a list of
`SeriesSpec`, each naming a **real log file** the run wrote, the column inside
it, and which instrument it drives — `iteration`, `residual`, `force`,
`temperature` or `sweep`. The replay reads the log; it never synthesises a
curve, and a series whose log is missing is a refusal, not an empty plot.

Elapsed time on screen is **`SolveReplay.clock()`**, which defaults to
`ElapsedClock.real_wall_time(wall_seconds)` — the run's own measured wall time,
with the basis sentence "Measured wall time of this run." Two clocks run at
once and the interface keeps them apart: `pace` compresses the **shoot** clock
and never appears on screen; the **elapsed** figure is the run's.

**4. Where the `presentation of run X` flag lives.**
`RunRecord.presentation_of`, written to `RunRecord.record_path`. It is refused
on screen mechanically: `assert_screen_safe(payload)` walks every payload the
sequencer publishes and raises on `presentation_of`, on any `source` path, and
on any string carrying a banned phrase or a path.

---

## Three shapes the contract locks

**The elapsed clock carries its basis, and an override must supply both.**
Sanaa's amendment makes the clock per-act: Act D shows 20 minutes everywhere.
A clock that accepted a bare number would be *the mechanism that strips the
basis off a figure* — the first override would put an unsourced number on
camera and the mode itself would be the hole. So `ElapsedClock` refuses an
empty basis, and refuses an override whose basis is not a sentence a viewer can
source. Act D's legitimate form, which the tests pin:

> Runtime of the optimisation itself, on the production configuration with the
> linear solvers on GPU. — 20 minutes

The run itself took 3601 s. Those are two different quantities and the sentence
is what keeps them apart.

**The cost line is a separate field and is never covered by the clock
override.** `SolveReplay.core_minutes()` always derives from the **real** wall
time; `Results.cost_actual` is this run's real cost, basis `measured`. An act
that overrides its clock does not thereby get to override its cost.

**Geometry is measured, not promised.** `Geometry.served_stl` must sit under
the directory the **server** reads — `sdk/geometry/`, measured at
`sdk/chief_engineer/server.py:351` and `:671` — not where the demo-surface
generator writes (`cases/demo-surfaces/`). Those agree today only because
someone copied by hand; the validator refuses a generator-side path.
`Geometry.matches` carries measured comparisons against the solved body, and
`solved_geometry_sentence()` **raises** unless every one agrees, so an act that
cannot assert the surface is the solved body is *unable to render the sentence*
rather than merely discouraged. Act B's measured 0.9 % chord rescale fails this
today; the fix is Sanaa's own parenthetical — regenerate from the solved case.

---

## Language, checked in code

`check_demo_language(text, zone=...)` enforces her NEVER-list as regexes:
"already finished", "presenting", "nothing new is solved", "no compute booked",
"screens come from", "reference body", "surface on file", "not meshed by this
screen", "two grids were built", plus the replay register ("re-displayed", "no
new solve", "replay", "Solver: none", "not recorded in this bundle", "source
case") — **and any path**. Path detection is deliberately narrow so it does not
fire on "lift/drag" or "2D/axisymmetric"; a checker that fires on prose gets
switched off, and a switched-off checker is exactly how these strings survived
the manual grep.

`zone="limitations"` is the only place "finer companion grid" is permitted, per
her jet-flap rule. `zone="screen"` rejects it.

**Extend the pattern, not the literal.** Her never-list says "not meshed by
this screen"; the sentence actually live in this package reads "not meshed **or
solved** by this screen" (`workflows/__init__.acknowledge_reference_surface`),
which a checker transcribed from her exact wording would have sailed straight
past. The regex is widened to catch the instance in the code, and the repo's
own sentence is a test case. That is the difference between a checker and a
transcription; whoever adds the next phrase should widen it the same way.

`check_running_line(text, tense=...)` enforces progressive tense while running
("Meshing", "Solving, iteration 4,000 of 20,000", "Sweep point 3 of 5") and
past tense for results.

**Physics limitations stay.** `Results.limitations` refuses an empty box. If a
caveat will not fit the compact form, raise it with the supervisor — the
contract does not permit blurring one.

---

## Banners and the agent counter

`DemoAct.banners()` returns the fixed stage→banner map (forming team, planning,
fleet at work, meshing, feasibility, solving, results); the sequencer sets the
banner as it enters a stage, so sync is a property of the sequencer, not of an
act's discipline.

`DemoAct.agent_census()` returns `(stage, agents working)` pairs. Sanaa: the
counter matches the agents the narrative has working at that moment, moving as
the team forms and lanes spawn — never static. The validator refuses a static
census and refuses one not ending at zero, which also keeps the fleet numeral's
attributed convention (Katie, 2026-07-31: the numeral ends at zero). What
changed under `aaed6498` is the **middle** state, not the end.

---

## The sequencer (deliverable 2) — design

`sdk/workflows/demo_sequencer.py`, one entry point:

```python
def run_act(key_or_act, emit, *, pace: float = 1.0) -> int
```

It resolves the act, runs `validate_act`, refuses on any problem, then walks
`STAGES` once. For each stage it sets the banner, sets the agent count, renders
that stage's content through the primitives already in
`sdk/workflows/__init__.py` (`make_transcript`, `bullets`, `emit_table`,
`announce_geometry`, `announce_plot`, `announce_field`), and moves on. **Every
payload goes through one `_publish` wrapper that calls `assert_screen_safe`
first**, so the internal flag and the source paths cannot reach a screen
through a payload nobody re-read.

**Pacing reuses what the page already has; it does not add a fourth notion of
it.** `control_room.html` already carries an ordered paced reveal queue
(`enqueue`/`revealQ`) with two modes, and FAST already "replays at the real
inter-event timing, clamped to a watchable band" (line 1415). The sequencer
therefore stamps each item with its own envelope timestamp and lets the
existing queue reveal it. "Nothing appears instantly" becomes a property of
the timestamps the sequencer emits: within a stage, no two items share an
instant.

**The seam with the replay lane.** That lane owns turning a stored log into
samples; this sequencer owns order, wording and pacing. The seam is one
iterator per series:

```python
Sample = namedtuple("Sample", "iteration values wall_seconds")
def iter_samples(spec: SeriesSpec) -> Iterator[Sample]
```

The sequencer composes the on-screen line with `SolveReplay.progress_line(...)`
(already tense-checked) and the elapsed figure with `SolveReplay.clock()`. The
replay lane never writes a screen string; the sequencer never parses a log.

**Acceptance checks, executed against the page, never grepped.** Both extend
`sdk/tests/control_room_pacing_harness.js`, which already runs the real page in
a DOM shim on a virtual clock:

1. *No stage's content timestamps all-at-once* — if every item of a stage
   carries one virtual instant, it popped.
2. *Banner and content agree at every virtual instant.*

If any pre-existing check in that harness changes result, that is a stop-and-
report, not a fix.

### The agent counter — TWO numerals, and only one of them is the one in the ruling

The page has two, with different documented meanings, and they must not be
treated as one:

- **Workers** (`renderWorkerCount`, line ~1629): the live provisioned count and
  nothing else — 0 before the fleet goes on the mesh, the fleet size while it
  meshes and solves, 0 again when the slots stand down. This is the numeral
  Katie's "ends at zero" convention governs, and it is the one that can fall.
- **Agents** (`renderAgentCount`, line ~1614): `max(agentsSeen,
  rolesSeen.size)` — a **cumulative census that never decreases**, and at
  completion `finish()` deliberately restores the peak, with its own written
  rationale: "an agent that spoke this mission was on the job whatever it is
  doing now".

Sanaa's requirement — a counter matching the agents the narrative has working
**at that moment** — is satisfiable only by a numeral that can go down, which
is Workers. Applying it to Agents would overturn an attributed convention and
contradict that numeral's own stated meaning. `DemoAct.agent_census()`
therefore feeds the **Workers-style** numeral: it moves from team formation
onward, not only from meshing, and it ends at zero. Whether the **Agents**
numeral must also change is unresolved and sits above a lane; it is with
cfd-supervisor.

Katie's comment is preserved and annotated, never deleted.

## Known gaps in v1 — read before you rely on them

1. **The live cell-by-cell mesh draw has no control-room event yet.**
   `mesh.stats` and `mesh.checked` are emitted by several workflows but
   `control_room.html` has no handler for either. `MeshPlan` specifies what an
   act supplies; the rendering is cfd's deliverable 2 and is not done.
2. **`validate_act` checks that artifacts exist and that strings are clean.**
   It does not check that numbers are right, that a run converged, that a grid
   triple is CONVERGING, or that the STL truly equals the solved geometry
   beyond the comparisons the act itself supplies. Those stay with the
   comparators and the supervisor.
3. **`sdk/workflows/__init__.py:acknowledge_reference_surface` is now
   non-compliant** and must not be called by any act: it emits "reference
   body" and "not meshed or solved by this screen", two phrases on her
   NEVER-list verbatim. Flagged to cfd-supervisor; retiring it is a change to
   shared code and is not this lane's call.
4. **`CERTONOMOUS_STAGING` divergence.** `server.py:73` honours that variable
   while the two serving paths hard-code `sdk/geometry`, so setting it moves
   the staging view without moving what is served. Reported, not changed.
