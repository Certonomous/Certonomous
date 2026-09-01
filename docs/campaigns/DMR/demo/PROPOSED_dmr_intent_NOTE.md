# The shock-reflection display intent: design note for a patch that is NOT applied

**Status: PROPOSAL. NOT APPLIED. NOT LIVE.**
Prepared by a cfd lane, 2026-09-01. The patch it describes is
`docs/campaigns/DMR/demo/PROPOSED_dmr_intent.patch`, in this same directory.
**Nothing under `sdk/` was written.** The control-room server was running at
pid 848778 for the whole of this work and was not restarted, stopped,
signalled or otherwise touched. **No solver was launched and no compute was
booked**: the benchmark this act presents was solved on 2026-08-07 and its
runs are complete on disk.

**Who has to read this before it lands.** The cfd supervisor reads the patch
as a diff (`SUPERVISION_CHARTER.md` §3 check 1), because
`sdk/chief_engineer/router.py` and `sdk/chief_engineer/scope.py` are shared
control-room tooling whose routing table governs every team's prompts.
Applying it is a human decision and restarting the server is a separate human
decision; neither was taken here. The server restart is explicitly one
coordinated cross-team batch and is not this lane's call.

**What it is for.** Sanaa ordered two further demo products on 2026-09-01
(`etc/sessions/2026-09-01T0245Z_sanaa_transonic_and_dmr_demos.md`): a
transonic 3D wing and the double Mach reflection. This is the second of those.
It is a **display mission**: the GUI presents a benchmark **from runs that
have already landed**. Pure presentation, no new solving. That constraint is
what makes it achievable tonight and it is not relaxed anywhere in this patch.

---

## 1. The headline

**The act cannot start a solver, and that is structural rather than
promised.** `workflows/dmr_display.py` imports no solver module, writes no
case directory, invokes no OpenFOAM binary and calls nothing that queues a
job. Its whole input is two JSON records and one PNG, all read with `json` and
`shutil`. A reviewer can establish this by reading its import block.

**The refusal list is not touched.** `_OUT_OF_SCOPE_DOMAINS` is not narrowed,
widened or reordered. As the thermal display note established and this lane
re-confirmed by driving `classify()`, the refusal list is consulted only when
NOTHING routed (`server._explain_unparsed`, reached only when
`WORKFLOWS.get(route.intent)` is `None`). A prompt that routes to an act never
reaches it.

**Nothing else reroutes.** Eighteen prompts covering every existing act were
driven through `classify()` before and after; every one of them keeps the
intent it has today. The table is in §4.

---

## 2. What the act puts on screen

The arc, in order:

1. **The ask.** A shock reflecting off a wall too steeply to stay attached.
   Stated as physics, with the one quantity in it that is known exactly.
2. **Confidence and price, before anything is shown.** The expectation, one
   percent of the distance travelled and the finer grid closer than the
   coarser; the statement that both were fixed before the first mesh was
   built; and the price set aside, 20 core-minutes.
3. **The cheap grid, then the fine one.** One table row per grid: solved
   position, exact position, difference, and the difference as a share of the
   distance the shock travelled.
4. **The picture.** Density contours at the final time, both grids.
5. **The result.** The verification sentence, the grid comparison, the bill,
   and the caveat box.

**The cost beat is the strongest line in the act and it is honest.** Estimated
20 core-minutes, used 2.4, a ratio of 0.12. The act says the estimate was the
honest one available at the time and that it was high. That is the lab saving
the operator compute, evidenced, which is one of the three ways DEMO STANDARD
v2 R9 permits the lab's intelligence to show.

**What the caveat box says, and where it stops.** The fine structure behind
the main shock — the second shock and the wall jet beneath it — is shown in
the picture and is **not among the quantities measured**. The box says exactly
that and stops. It does not discuss instruments, detectors, registrations or
repairs: R9 forbids all of it in user-visible text, and the intelligence shows
through the cost beat instead.

**Register compliance.** Every transcript line goes through
`workflows.check_wording`, which refuses an em dash and the banned on-camera
register. No case identifier, gate name, tier word, rule number or record
filename appears in any user-visible string; `res120` and `res60` exist in the
module only as lookup keys and reach nothing that renders.

---

## 3. Where the numbers and the picture come from

**The numbers.** `verification/runs/DMR_runs/<grid>/locator_result.json`, the
graded record written by the locator run, field `gateV`. The act reads
`x_measured`, `x_exact_at_row` and `error` and derives one thing only: the
error as a share of the distance travelled, where the distance is computed
from the configuration itself as `20 t / sqrt(3) = 2.309401` at `t = 0.2`
rather than carried as a magic number. It re-derives no shock position, no
error and no verdict.

**The picture is NEW, and this is a finding the supervisor should know about.**
The contour record retained with the runs,
`verification/runs/DMR_runs/dmr_density_contours_t0p2.png`, is a correct
scientific figure and is **not usable on camera**: its captions carry the run
directory names, the solver and flux-scheme names, the pre-registration
filename and the phrase "see results file". DEMO STANDARD v2 R5 forbids every
one of those. `figures/render_shock_field.py` in this directory re-renders the
same fields off disk with captions an engineer reads without a glossary. It
starts no solver: it reads three ASCII scalar fields per grid at the final
written time and draws contours.

**That renderer independently reproduces the record's own numbers**, which is
the strongest available check that it is reading the right fields correctly.
Over the structure range `x > 0.25` it measures a density maximum of **19.20**
on the coarse grid and **20.05** on the fine grid; `DMR_RESULTS.md` records
"the flow field proper tops at rho = 20.05" and the retained figure's own
panel captions read `[1.40, 19.20]` and `[1.40, 20.05]`. Nothing was copied
between the two readers.

**One trap the renderer caught, and it would have drawn a plausible wrong
picture.** These cases were solved on four ranks and reconstructed, and **the
reconstructed fields are not in x-fastest order**: a bare `reshape` slices the
field by rank and draws nonsense that still looks like contours. The renderer
therefore carries every value with its own cell centre, sorts on `(y, x)`, and
then asserts the result is a complete Cartesian lattice before drawing. The
first version of the reader raised on exactly this and was rewritten.

**The path is taken from the filesystem, never from the frozen record.** The
pre-registration cites `demo-output/website/campaign/DMR_runs/`, a directory
that no longer exists; an act wired from the record would find nothing. See
`verification/campaign/DMR_PREREGISTRATION_AMENDMENT_1_DRAFT.md`.

---

## 4. Shape of the router, and what was driven through it

Read against `sdk/chief_engineer/router.py` at blob
`40521daec147bf19d2f2ee8dfe059bd4da8cae5e`, 784 lines, and
`sdk/chief_engineer/scope.py` at blob
`95253fdd2866563444bbdee68b1f1c53f72a4053`, 175 lines. `git apply --check` on
the patch is the operative test of whether they still apply; it was clean at
the time of writing.

The patch makes six additions to `router.py` and two to `scope.py`. Every one
is additive: **no existing line is deleted or altered in either file** except
the `scope.py` import block, which gains one name.

| # | File | Where | What |
|---|---|---|---|
| 1 | `router.py` | module docstring | one paragraph naming the route |
| 2 | `router.py` | beside the compressible intent constants | `DOUBLE_MACH_REFLECTION = "double-mach-reflection"` |
| 3 | `router.py` | beside `_HYPERSONIC_CYLINDER` | two match patterns |
| 4 | `router.py` | `classify()`, before the hypersonic branch | one scoring branch at weight 2.2 |
| 5 | `router.py` | the rationale table | what the Chief Engineer says on routing |
| 6 | `router.py` | `WORKFLOWS` | one entry pointing at `workflows.dmr_display` |
| 7 | `scope.py` | import block | one name added |
| 8 | `scope.py` | `CAPABILITIES` | one row declaring `unsteady` and nothing else |

**Why weight 2.2.** The four steady compressible acts score 2.0. A prompt that
says "shock reflection off a wedge" names both, and the reflection is the more
specific reading: the wedge act grades an attached oblique shock and has
nothing to say about a Mach stem or a triple point. 2.2 also sits below the
thermal display proposal's 2.4, so the two cannot contend even in principle.

**Why the second pattern requires a named surface.** The first pattern is the
benchmark's own vocabulary — double Mach reflection, Mach stem, triple point,
irregular reflection, Woodward-Colella — none of which can be typed about a
steady attached shock. The second catches the operator who does not know the
name and writes "a Mach 10 shock reflects off a wall". It requires the surface
to be named, because "the shock reflected at the corner" is a sentence written
about the steady wedge and that act keeps it.

**Why `CAPABILITIES` gains a row.** The benchmark is genuinely time resolved,
so declaring `unsteady` is a promise the run keeps. It declares nothing else,
so a prompt that asks this act to optimise a shape or report a temperature is
told so before the screen starts rather than after it finishes. Driven:
a prompt asking for both produces "You asked for a thermal solve and a design
search. This run cannot do that..." This row can be dropped independently of
the rest of the patch if the reviewer prefers the undeclared default.

### The eighteen prompts, before and after

Both columns are measured, not predicted: the before column was driven through
`classify()` at HEAD `48a9ae65` and the after column through the patched
overlay. Every prompt keeps its intent except the five that name the new act,
and all five of those fall through to `general-mission` today.

| Prompt | Before | After |
|---|---|---|
| Show me a double Mach reflection benchmark. | general-mission | **double-mach-reflection** |
| What happens when a Mach 10 shock reflects off a wall? | general-mission | **double-mach-reflection** |
| A strong shock reflecting off the ground... | general-mission | **double-mach-reflection** |
| I want a shock interaction benchmark. | general-mission | **double-mach-reflection** |
| Can you do the Woodward-Colella problem? | general-mission | **double-mach-reflection** |
| Supersonic wedge at Mach 2.5, oblique shock angle. | supersonic-wedge | supersonic-wedge |
| Hypersonic cylinder, shock standoff distance. | hypersonic-cylinder | hypersonic-cylinder |
| Diamond airfoil wave drag by shock expansion theory. | diamond-airfoil-wave-drag | diamond-airfoil-wave-drag |
| Supersonic cone, Taylor-Maccoll conical shock. | supersonic-cone | supersonic-cone |
| Vortex shedding behind a cylinder, Strouhal number. | cylinder-vortex-shedding | cylinder-vortex-shedding |
| Optimise this wing to cut drag by 20 percent. | adjoint-optimization | adjoint-optimization |
| Mesh and solve this motorbike STL, give me the drag. | geometry-study | geometry-study |
| Ahmed body at 25 degrees. | ahmed-body | ahmed-body |
| NASA hump separation bubble. | nasa-hump | nasa-hump |
| ONERA M6 wing at Mach 0.84. | geometry-study | geometry-study |
| Adjoint gradient with a finite difference check. | adjoint-optimization | adjoint-optimization |
| Sobol indices for the cylinder. | sobol-sensitivity | sobol-sensitivity |
| How sure are you about that drag number? | uncertainty-reduction | uncertainty-reduction |

**A pre-existing observation, not caused by this patch and not fixed by it:**
"ONERA M6 wing at Mach 0.84" routes to `geometry-study` rather than to the
`onera-m6` act, at HEAD, unchanged either way. That is the *other* new demo
product Sanaa ordered and whoever builds it needs to know.

---

## 5. What was tested, and the two controls

Testing was done in a **symlink overlay of the repository** whose only real
directories are patched copies of `chief_engineer/` and `workflows/`. Nothing
under `sdk/` in the repository was written at any point.

**The routing regression.** The eighteen prompts above, driven through
`classify()` in the overlay and in an unpatched control.

**The existing test suite.** `tests/test_scope_down.py` and
`tests/test_ahmed_routing.py` pass in the patched overlay: 26 passed, 5
subtests passed. A first attempt in a bare copy of the two packages showed 8
failures; a control run of the same tests in the same bare copy **without the
patch** showed the identical 8 failures, establishing them as missing repository
files rather than a regression. In the full overlay, both patched and at HEAD,
they pass.

**The whole SDK suite** was then run twice, in a patched overlay and in an
otherwise identical unpatched one, each stopping at the first failure. **The
two runs are identical: 204 passed, 20 subtests passed, 1 failed** (286 s
patched, 298 s unpatched). The single failure is
`tests/test_autostop_gate.py::test_the_tracked_gate_exists_and_is_the_reviewed_one`
and it is **pre-existing and nothing to do with this patch**: it also fails on
its own at HEAD in the repository itself, where it asserts the auto-stop
gate's clause 1 matches processes with `pgrep -x` while the tracked script
walks `/proc` instead. Reported here as a cross-team observation; not touched.

No solver process was spawned by either run, checked while they were in
flight.

**Control 1, planted perturbation.** A copy of the run tree was made and the
fine grid's measured shock position was moved by a known **+0.0500000**. The
screen followed by **+0.0500000** and the share-of-travel column moved from
**0.15%** to **2.31%**, which would have failed the one-percent criterion
visibly rather than hiding inside it. The act is reading disk.

**Control 2, planted absence.** The fine grid's record was removed. The act
showed **no row** for that grid, **named the empty path** on the record, and
drew nothing in its place. A gap is reported, never a zero.

**Both controls are filed and rerunnable**, at
`docs/campaigns/DMR/demo/plant_control.py`. It breaks the inputs on a copy,
never in the run tree, and it refuses with a return code of 2 and the message
"Nothing was tested" when the act is not on disk, so it cannot report a pass it
did not earn. Against the candidate module it returns 0 with both controls
green; against nothing at all it returns 2, which is the state it is in today
because the act has not landed.

---

## 5a. The promotional-surface clause, and why this act clears it

`router.py:470-477` states the rule that governs whether an act may reach the
control room at all: **"The control room is a promotional surface and carries
only cases that reach a clean result"**. It is written there as the reason
ONERA M6 is deliberately not routed — that act's primal plateaus above the
solver's own convergence tolerance and it honestly reports itself unconverged,
so its measurements and its documented failure live in the evidence record
instead, which is where a failure belongs.

**THE CLAUSE HAS SINCE BEEN RULED ON, AND THE RULING IS THE PRIMARY ANSWER
HERE.** The cfd supervisor ruled at `73c18156`, 2026-09-01, on the jet-flap
proposal: that comment is a code comment written by a lab agent, not a charter
clause and not a ruling of Sanaa's; it governs **gradeable solve missions**,
where the control room offers to solve something and report a graded result;
it does not reach a **display mission** presenting finished runs; and it is
**not retired** and stays in force for everything it does reach. This act is a
display mission, so on that ruling the clause does not reach it either.

That ruling is adopted here rather than re-argued. **What follows is an
independent second reason, and it is worth stating because it does not depend
on the ruling holding:** even read literally, as a clause that does reach every
act, this one clears it on the quantity it presents — and the position is
materially stronger than the jet-flap act's. Stated plainly so nobody has to
infer it:

- **Both rungs reached a clean result on the graded kinematics.** Gate V is
  `PASS` at both, 0.15% and 0.17% against a 1.0% tolerance, and the fine rung
  beat the coarse as predicted. Both runs satisfy the strict completion rule
  clause by clause, re-verified 2026-09-01: `rc = 0`, one `End` line, last
  `Time = 0.2` equal to the registered `endTime`, all ten writes present, all
  eight fields at 0.2, and the age guard holding on both.
- **The gate was frozen before the run and the ordering is provable.** The
  pre-registration was committed at `74797a57`, 2026-08-07T22:40:28Z; the
  primary rung's own `0/T` was written at 22:43:42Z.
- **The contrast with the jet-flap act.** Every JF1 run is gate NONE and its
  registration is an unfrozen draft, so that mission can claim no verdict and
  quotes movement over the final iterations in place of a convergence claim.
  This act presents a `PASS` on a frozen gate against an exact analytic
  solution. Whatever ruling Sanaa gives on the promotional surface, these two
  acts are not in the same position and should not be decided together by
  default.
- **What the act does NOT present.** The record also carries clauses that
  failed as registered, attributed in the record to the detector's geometry
  rather than to the flow. This act presents none of them, asserts nothing
  about the structure behind the main shock, and states the limit of its claim
  in the caveat box: the structure is shown and is not among the quantities
  measured. That handling was raised with the cfd supervisor and ruled on
  rather than decided quietly by the lane. **The caveat must never drift
  toward implying no measurement was attempted, and the act must never gain a
  sentence claiming the structure agrees with anything.** A future edit
  tempting either way goes back to the supervisor.

---

## 6. What this note does NOT claim

- **It does not claim the act has been seen in the control room.** It has been
  driven with a recording emit sink, not through a running server. The server
  was not restarted.
- **It does not claim a verdict for the benchmark.** The verdicts are
  `DMR_RESULTS.md`'s and are unchanged by anything here. The act presents the
  incident-shock kinematics result and the grid comparison; it presents no
  other graded quantity, and the caveat box says the structure behind the main
  shock is shown but not measured.
- **It does not claim the frozen record has been repaired.** The path defect is
  drafted as a dated amendment and is not applied.
- **It does not claim `F2_transonic_naca0012.md` has been examined.** It has
  not. It is reported to carry the same stale-path problem and is somebody's
  next job.

---

## 7. Conflict with the OTHER TWO display patches, and the order to apply them in

> **CORRECTION, 2026-09-01 02:1xZ, and it is against this section's own first
> version.** As committed at `39fa4564` this section described a TWO-way
> conflict with the thermal patch and closed with the sentence *"`scope.py` is
> touched by this patch and not by the thermal one, so there is no conflict
> there."* **That sentence was wrong within a minute of being written.** The
> jet-flap display proposal landed at `73c18156`, 02:05:37Z, twenty-seven
> seconds after my own commit; it touches `scope.py` **at the same two places
> this patch does**. The corrected section follows. The original claim is
> struck rather than deleted because the cfd supervisor was told it in a lane
> report and should be able to see exactly what was withdrawn.

**THREE display-mission patches are now pending against the same base**, all
cut against `router.py` blob `40521daec147bf19d2f2ee8dfe059bd4da8cae5e`:

| Patch | Filed at |
|---|---|
| Thermal | `docs/campaigns/T-family/demo/PROPOSED_thermal_intent.patch` |
| Jet flap | `docs/campaigns/JF1-jet-flap/demo/PROPOSED_jet_flap_intent.patch` |
| This one | `docs/campaigns/DMR/demo/PROPOSED_dmr_intent.patch` |

Each applies cleanly on its own at HEAD. **No two of them apply cleanly one
after the other.**

### Measured, not predicted

The jet-flap patch was applied to a throwaway copy of the three shared modules
and this patch was then offered on top. It **fails direct application at two
points**:

- `sdk/chief_engineer/router.py:781` — the `WORKFLOWS` table, where all three
  patches insert an entry.
- `sdk/chief_engineer/scope.py:33` — the `from .router import (...)` block,
  where both this patch and the jet-flap one add a name to the same two
  physical lines. Their `CAPABILITIES` row also anchors on the same
  `SUPERSONIC_WEDGE: frozenset(),` line this patch anchors on.

Against the thermal patch the overlaps are the **module docstring** (both
append a route paragraph after the `geometry-study` entry) and again the
**`WORKFLOWS` table**. Thermal does not touch `scope.py`.

**What was NOT measured, and is not claimed:** whether `git apply --3way`
resolves any of this cleanly. The throwaway used for the test lacked the base
blobs, so 3-way could not run there and fell back to direct application. The
real repository does hold blob `40521dae`, so 3-way has what it needs there,
but that was not run, because running it means applying a patch to the live
working tree and none of these three is approved.

### Consequence for whoever sequences the restart

All three are additive and none reads anything another writes, so this is
bookkeeping rather than a design collision. But it will not resolve itself:
**the second and third patches applied must be re-cut against the tree that
results from the first**, not applied blind. The order is free. The safest
route is to apply them in one sitting, re-cutting as you go, and to re-run each
act's own controls afterwards — for this act,
`docs/campaigns/DMR/demo/plant_control.py`, which returns 2 rather than a false
pass if the module is not where it expects.
