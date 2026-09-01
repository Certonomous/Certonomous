# The jet-flap display screen: design note for a patch that is NOT applied

**Status: PROPOSAL. NOT APPLIED. NOT LIVE.**

Prepared by the cfd team, 2026-09-01, box clock (`date -u` read
`Tue Sep 1 01:37:30 UTC 2026` while this was written; every time below is that
clock). The patch it describes is
`docs/campaigns/JF1-jet-flap/demo/PROPOSED_jet_flap_intent.patch`, in this same
directory.

**Nothing under `sdk/` was written.** The control-room server was running at
pid 848778 with Sanaa in it for the whole of this work. It was not restarted,
stopped, signalled, or otherwise touched. No solver was started and no compute
was spent: every number below was read off calculations that were already
finished.

## Who has to read this before it lands

The cfd supervisor reads the patch as a diff, and reads
`sdk/workflows/_jf1_numbers.py` in particular, because that file is the one
that produces measured numbers. The heat-transfer team has a sibling proposal
against the same three router blobs
(`docs/campaigns/T-family/demo/PROPOSED_thermal_intent.patch`); the two touch
`sdk/chief_engineer/router.py` in different places but both must be applied
before either is filmed, and whoever applies the second one re-runs
`git apply --check`.

Applying the patch is a human decision. Restarting the server is a separate
human decision, and it is a single coordinated restart shared with the thermal
screens, carrying `CHIEF_ADAPTER=openfoam OPENFOAM_RUN_PREFIX=openfoam2606
CERTONOMOUS_SOLVE_RANKS=16`. Neither decision was taken here.

---

## 1. What this answers

Sanaa's Act B STOP order
(`etc/sessions/2026-09-01T0104Z_sanaa_actB_stop.md`, commit `d8ddfe62`) gave
two paths and asked which is achievable by 09:00Z. This note answers the
second path: a jet-flap screen that presents the real run tree rather than
the generic single-body study that was filmed by mistake.

Her requirements, and where each is met:

| She asked for | Where it is |
|---|---|
| 2D section | `flow_facts()` and `sweep_facts()` both read one-cell-deep cases; the spanwise page is shown as the cheap check |
| slot as jet inlet | `slot_faces()` reads the slot's mesh type per case and prints open or closed; it is not asserted in prose |
| Cμ sweep | five rows, read per case, in the lift table |
| y+ ≤ 1 | measured on both grids and put in the grid table, worst case quoted |
| the 20,000-iteration solution | the flow-picture grid, `20000`, read from the run tree |
| the actual mesh slice | the landed grid pages, which are the computational grid and not a surface tessellation |
| CL_aero and CL_total vs Cμ | separate columns, with the direct jet push as its own column between them |
| the published theory line | Williams, Butler and Wood, R&M 3304, equation (2) |

---

## 2. THE POLICY QUESTION THIS RAISED, AND HOW IT WAS RESOLVED

`sdk/chief_engineer/router.py:470-477` carries a standing policy, written
deliberately and in the router's own voice:

> ONERA M6 is deliberately NOT routed from the control room. Its primal
> plateaus above the solver's own convergence tolerance and the act honestly
> reports itself unconverged. The control room is a promotional surface and
> carries only cases that reach a clean result.

**Every calculation this screen presents is unconverged by the same standard.**
Not one of the five met the 1e-06 target set before it ran; the turbulence
equation imbalance at the last iteration runs from 3.457e-06 to 1.472e-04. On
the policy read literally, this act belongs off the control room exactly as M6
does. The lane that built this screen refused to resolve that itself and sent
it up, which was correct: an agent does not get to decide that a policy written
to protect a customer-facing surface does not apply to its own work.

**RESOLVED by the cfd supervisor, 2026-09-01, on Sanaa's own words rather than
on any agent's relay of them.** Two things she wrote, both read at the commits
that carry them:

- `etc/sessions/2026-09-01T0140Z_sanaa_demo_recap_five_items.md` at `f9b7a077`:
  *"all jet flap capabiltiies must appear in the demo"*. Her spelling is hers
  and is preserved.
- Her Act B STOP order at `d8ddfe62` requires a display mission presenting
  **the real JF1 run tree**, and itemises what that means: the blowing sweep,
  the mesh slice, the 20,000-iteration solution.

She ordered this act onto the GUI, and she ordered it knowing what it presents,
because she named the contents herself.

**The policy is NOT retired, and nobody here has the standing to retire it.**
Retiring a standard is reserved to Sanaa. What was ruled instead is narrower
and turns on what the comment actually governs. That comment is a code comment
written by a lab agent: it is not a charter clause, not a gate threshold, and
not a ruling of hers. It governs **gradeable solve missions**, where the
control room offers to solve something and report a graded result. This is a
**display mission** presenting finished feasibility runs under her direct
order, and it carries the honesty framing on its face: no verdict, movement
over the final 4,000 iterations in place of a tolerance, no discretisation
band, no percentage agreement with the published curve. The policy does not
reach that case, and it stays in force, untouched, for everything it does
reach.

A successor reading this patch beside that comment will ask exactly the
question this lane asked. This section is here so they get the answer instead
of the argument.

**What this does not change: the patch stays unapplied.** It is committed as a
reviewable proposal and goes live only in the one coordinated cross-team
restart, alongside the thermal screens, the scope-down fix and the GUI
curation. Nothing here applies to a server Sanaa is sitting in.

---

## 3. What the patch changes

Five hunks and two new files. Cut against, and verified identical to, the
blobs at `HEAD` when this was written:

| File | Blob | Change |
|---|---|---|
| `sdk/chief_engineer/router.py` | `40521dae` | one intent constant, one pattern pair, one scoring branch, one rationale entry, one `_SURFACE_KEEPS_ROUTE` entry, one `WORKFLOWS` row |
| `sdk/chief_engineer/scope.py` | `95253fdd` | one import name, one `CAPABILITIES` row |
| `sdk/chief_engineer/display_names.py` | `45e9756a` | two display-name rows |
| `sdk/workflows/_jf1_numbers.py` | new | a thin loader, no arithmetic |
| `sdk/workflows/jet_flap_display.py` | new | the screen |

`git apply --check -p1` passes.

**`_OUT_OF_SCOPE_DOMAINS` is not touched.** Not narrowed, not widened, not
reordered. The refusal list is consulted only on the fallback branch, when
`WORKFLOWS.get(route.intent)` is `None`, so an intent with a workflow entry
never reaches it. This is the same mechanism the thermal proposal established
and it is not a new idea here.

### 3a. Where the mission code belongs, as a proposal rather than a guess

The brief that produced this note flagged the location as a judgment call.
**The recommendation is that none of the screen belongs under
`sdk/chief_engineer/`.** That package is the control room's own machinery, and
every act in the product lives under `sdk/workflows/` as a module exposing
`main(request, params, emit)`. Putting a thirteenth act somewhere else would
make it the only one the server reaches differently.

So: the screen is `sdk/workflows/jet_flap_display.py` and its reader is reached
through `sdk/workflows/_jf1_numbers.py`, the leading underscore following the
existing helper convention in that directory (`_act_plots.py`,
`_mesh_quality.py`, `_exact_theory.py`).

**That loader holds no arithmetic.** The one implementation is committed at
`verification/runs/JF1_jet_flap/jf1_display_numbers.py`, beside the run tree it
reads, which is the established shape here: eleven generator modules already
live in that directory. The printed result sheet, the lift panel embedded in
that sheet, the standalone lift figure and the grid page all call the same
file. Two of those surfaces previously carried their own copy of the same
constant, the copies disagreed with the measurement and with each other, and
nothing raised because a constant never does. A second implementation inside
the patch would rebuild exactly that failure. What lands in `sdk/chief_engineer/` is only what has to:
the router needs to know the intent exists, the scope guard needs to know what
the intent can do, and the display-name table needs the body's name.

---

## 4. The measured before and after

Thirty-three probe prompts across the jet act, blowing words without a
section, aerodynamics, optimisation, uncertainty, thermal and the unparseable,
driven through the router's own `classify()`, `apply_surface()` and
`out_of_scope_domain()`, once against the unmodified tree and once against the
patched one. `dispatch` is what `server._start_mission` would do: **act** when
the intent has a `WORKFLOWS` entry, **refusal path** when it does not.

**Six rows change. Every other row is byte-identical.**

| Prompt | Before | After |
|---|---|---|
| Blown wing: sweep the jet momentum and give me lift against blowing. | unseen-geometry 0.99 | jet-flap-display 0.74 |
| Airfoil with a blown slot at the trailing edge, show me the lift. | unseen-geometry 0.99 | jet-flap-display 0.74 |
| Jet flap aerofoil, what does the blowing do to the lift? | unseen-geometry 0.99 | jet-flap-display 0.74 |
| Circulation control wing, Cp along the chord please. | unseen-geometry 0.58 | jet-flap-display 0.62 |
| Trailing edge blowing on this section, sweep the momentum coefficient. | general-mission 0.30, refusal path | jet-flap-display 0.99 |
| Show me the supercirculation on a jet flapped wing. | unseen-geometry 0.99 | jet-flap-display 0.74 |

**The upload path, which is where the filmed failure actually happened:**

| Prompt plus surface | Before | After |
|---|---|---|
| "Airfoil blown slot." + `airfoil_blown_slot.stl` | **geometry-study 0.99** | jet-flap-display 0.74 |
| "Blown wing: sweep the jet momentum…" + `airfoil_blown_slot.stl` | **geometry-study 0.99** | jet-flap-display 0.74 |
| "Solve the drag on this aircraft." + `airliner.stl` | geometry-study 0.99 | geometry-study 0.99 |
| "Thermal map of this motor in a duct." + `motor_in_duct.stl` | geometry-study 0.99 | geometry-study 0.99 |

The first row is the failure Sanaa stopped: a blown-slot prompt with the
blown-slot surface, routed to the plain single-body chain. It is the
`_SURFACE_KEEPS_ROUTE` entry that fixes it, and that entry is the single
easiest hunk in this patch to leave out.

**Blowing vocabulary without a section still does not capture**, because both
patterns are required: "Circulation control in the plasma actuator loop.",
"Blown film cooling on a turbine disc.", "Jet engine noise at takeoff." and
"Model the combustion in the chamber." all keep the exact route and refusal
they had before.

### 4a. The scope guard, and the false positive it could have produced

`sdk/chief_engineer/scope.py` will scope a run down on camera if a prompt asks
for something the dispatched run cannot do. Registering this act **without**
declaring `BLOWING` would make the real blown-wing act announce, during the
blown-wing act, that it "solves the unblown baseline only". That is a false
positive in the humble direction on the lab's best result, and it is worse
than the defect it was written to fix.

The patch therefore declares it:

```python
    JET_FLAP_DISPLAY: frozenset({BLOWING}),
```

Measured rather than reasoned: `scope.unmet_asks()` returns `()` for every jet
prompt routed to this act, with and without an uploaded surface, and still
returns `('blowing',)` with the full scope-down sentence for a blowing prompt
that lands on `geometry-study`. The guard is silent where it should be and
loud where it should be.

---

## 5. The numbers, and the reader that produces them

Every number is read at present time from the landed run tree. Nothing is
hard-coded and nothing is copied from a figure.

**Grid resolution at the wall**

| Grid | Cells | Iterations | Wall cells | Largest wall spacing [wall units] | Cells across slot |
|---|---|---|---|---|---|
| Flow picture | 46,180 | 20,000 | 200 | 0.436 | 12 |
| Force calculations | 39,984 | 8,000 | 396 | 0.398 | 12 |

**Lift against blowing, one grid, five calculations**

| Jet momentum | Slot | Lift on the wing surface | Direct jet push | Total lift | Published total lift | Movement over final 4,000 iterations | Turbulence equation imbalance |
|---|---|---|---|---|---|---|---|
| 0.00 | closed | 0.0001 | 0.0000 | 0.0001 | 0.0000 | 6.901e-07 | 3.457e-06 |
| 0.05 | open | 0.4057 | 0.0250 | 0.4307 | 0.4234 | 4.993e-07 | 5.941e-06 |
| 0.10 | open | 0.5488 | 0.0500 | 0.5988 | 0.6048 | 6.741e-07 | 2.550e-05 |
| 0.20 | open | 0.7440 | 0.1000 | 0.8440 | 0.8687 | 3.383e-05 | 4.572e-05 |
| 0.40 | open | 1.0100 | 0.2000 | 1.2100 | 1.2595 | 7.805e-06 | 1.472e-04 |

Sources, per column: cell counts from each case's `log.checkMesh`; wall
spacing from the `yPlus` field written at the final time, on the `airfoil`
patch; slot state and face count from `constant/polyMesh/boundary`; lift from
`postProcessing/forceCoeffs/0/coefficient.dat`; turbulence imbalance from the
last `Solving for k` line of `log.simpleFoam`; the published curve from
`verification/runs/JF1_jet_flap/artefacts_actB/jf1_theory_actB_numbers.json`.

### 5a. Three readers, three plants, and one that was blind

Every reader in `_jf1_numbers.py` is paired with a planted control (CLAUDE.md
rule 3) and **refuses** rather than degrading.

This is not decoration. The first draft of the wall reader looked for the
patch named `aerofoil`. The run tree spells it `airfoil`. The reader found no
patch, returned an empty list, and reported **y+ max as 0.0 on both grids**:
a number that would have gone on camera as proof of an exquisitely resolved
wall and which meant only that nothing had been read. The plant is what turned
that into a refusal instead of a result.

- `_plant_patch` writes `1.234e-03` into a copy of the real field, inside the
  named patch's block only, and reads it back through the same code path.
- `_plant_history` writes it into the last row's `Cl` field of a copy of the
  force history, which is the row the settling window is most sensitive to. A
  reader picking up `Cd` or `Cl(f)` by column-index drift will not see it.

Two readers carry no plant and this is recorded rather than waived:
`cell_count` and `last_k_residual` each read a single unambiguous token and
refuse on absence.

`last_k_residual` keeps the LAST `Solving for k` line of the run, and that is
safe for a reason worth stating deliberately rather than relying on by
accident. These cases run with `nNonOrthogonalCorrectors 1`, so pressure is
solved twice per iteration and the last match for `p` would be the second
corrector pass, not the iteration's residual. Measured on
`JF1_L1_BLOWN_CMU020_A0/log.simpleFoam`: 8,000 time steps, 8,000 `k` solves,
8,000 `omega` solves, 16,000 `p` solves. The immunity is a property of which
field is read, not of the code, so the function must not be generalised to `p`
by parameterising the field name.
- `assert_one_grid` is a refusal, not a comment: every table passes its cases
  through it, and a table spanning both grids raises instead of rendering.

### 5b. Why the settling window is 4,000 iterations and not 1,000

The screen quotes movement over the final 4,000 of 8,000 iterations. The
shorter window always reports less movement and is the flattering choice: on
the strongest-blowing row the half-range is 5.763e-06 over the last 1,000 and
7.805e-06 over the last 4,000, and on the Cμ = 0.20 row it is 2.901e-05
against 3.383e-05.

The reader refuses outright if fewer than 4,000 iterations exist, rather than
silently shortening the window to whatever is available.

---

## 6. Two defects found in already-signed assets, and both are now FIXED

Both were found by rebuilding the numbers from the run tree rather than
copying them. Both were confirmed by the supervisor's own independent
measurement rather than accepted on this lane's report, and both have since
been repaired in a separate pass that does not depend on this patch. The
repairs are described here because the patch's screen was built against the
corrected numbers.

### 6a. The result sheet's movement column does not match its own caption

`verification/runs/JF1_jet_flap/artefacts_actB/make_actB_sheet.py:34-36`
carries a hard-coded dictionary:

```python
# Movement of the lift coefficient over the last 4,000 iterations, rounded up to
# one significant figure.  A settling indicator, not a total uncertainty.
SETTLE_BAND = {0.00: 5e-07, 0.05: 5e-07, 0.10: 5e-07, 0.20: 9e-06, 0.40: 5e-06}
```

and the sheet prints that caption verbatim at
`blown_trailing_edge_result_sheet.tex:90`. Measured from
`postProcessing/forceCoeffs/0/coefficient.dat` for all five cases, the actual
half-range of lift over the final 4,000 iterations is:

| Jet momentum | Printed | Measured over final 4,000 | Understated by |
|---|---|---|---|
| 0.00 | 5e-07 | 6.901e-07 | 1.4x |
| 0.05 | 5e-07 | 4.993e-07 | matches |
| 0.10 | 5e-07 | 6.741e-07 | 1.3x |
| 0.20 | 9e-06 | 3.383e-05 | 3.8x |
| 0.40 | 5e-06 | 7.805e-06 | 1.6x |

Four of the five printed values are smaller than the quantity the caption
defines, and none of them is that quantity "rounded up to one significant
figure". Three alternative definitions were tested and none reproduces the
printed dictionary either: end-to-end drift over 4,000 iterations, end-to-end
drift over 1,000, and the standard deviation over the final 4,000.

The values are also smaller than the half-range over the final **1,000**
iterations for three rows, which no nested window can be: a wider window
cannot have a smaller range than a window inside it. Whatever produced the
dictionary, it was not either window on the committed histories.

**The "it was the shorter window" explanation is CLOSED, by measurement.**
Rounding the 1,000-iteration half-ranges up to one significant figure gives
6e-07, 5e-07, 7e-07, 3e-05, 6e-06. Four of the five printed values differ from
those too. The constants are wrong under BOTH windows, so no choice of window
rescues them. This lane and the supervisor computed both windows independently
and agreed to every digit.

**The sharpest argument is the rounding rule, and it needs no window at all.**
The caption promises "rounded UP to one significant figure". Rounding
6.901e-07 up to one significant figure gives 7e-07; the sheet printed 5e-07.
The values fail the operation the caption names, independently of which
movement definition anyone prefers.

This is a customer-facing sheet, it is asset 9 in `ACT_B_ASSETS.md`, and the
column is the sheet's only uncertainty column.

**FIXED.** The column is computed at render time from each case's force
history, through the one shared reader, and the caption now names the
operation exactly: "half the range it covered there, rounded up to one
significant figure". The dictionary was deliberately NOT replaced with better
constants. A constant wearing a measured caption is the defect class, and
better constants leave it in place for whoever next changes a run. The sheet
re-rendered at exactly one page, which was checked with `pdfinfo` rather than
assumed, and the replacement values are width-neutral by construction because
each is a single-digit mantissa times a power of ten, exactly like the values
it replaced.

### 6b. The sweep-grid page quotes one calculation's wall spacing as the sweep's

`artefacts/jet_flap_7_mesh_forcesweep.pdf` states "Near-wall spacing here:
smallest 0.021, average 0.123, largest 0.256". Those are the Cμ = 0.10
calculation's values exactly. Across all five calculations on that grid the
largest wall spacing is **0.398**, at the strongest blowing.

This one is imprecision rather than falsity: the page's actual claim, that
every wall cell is below the wall-resolved limit of 1, stays true at 0.398.
But a page captioned as the grid the five calculations ran on, quoting one of
the five, understates the worst case by 1.6x. The screen in this patch quotes
0.398.

**FIXED.** The page now reads the wall spacing of all five calculations and
states the rise with blowing, from 0.191 with the slot closed to 0.398 at the
strongest jet. The monotone rise is a better fact than the single number it
replaces. Anywhere 0.19 appears as this grid's resolution it is to be read as
0.398.

### 6c. One asset moved that was NOT defective, and the distinction is the point

The standalone lift figure always computed its error bars at render time and
they were honest for the window it used, the final 1,000 iterations. Its
window changed to the final 4,000, so its bars are now LARGER.

That is the lab tightening a convention on itself, not a defect being
repaired: where two defensible definitions exist and one flatters the result,
take the one that reports more movement, and the range over the longer window
is the only choice that cannot hide an excursion inside it. The result sheet's
dictionary WAS defective. This figure was not. Blurring the two would waste
the distinction that makes the finding worth having.

Related, and worth stating because it was carried into this lane's brief as
established fact: the figure **0.19** for the sweep grid's y+ is the
*slot-closed reference* calculation's value. It is the smallest of the five
and understates the sweep maximum by 2.1x.

---

## 7. Compliance checks actually run

- **Banned-vocabulary sweep.** The screen's user-visible text, 7,381
  characters, swept with the same banned list and the same poisoned positive
  control the printed pages use (`vocab_sweep_jf1.py`). The control ran first
  and all 31 banned patterns were seen in the poison, so the reader is not
  blind. **One hit remains: `OpenFOAM`,** emitted in `solver.selected`.
  **It is not fixed here, deliberately.** Nine shipped acts emit exactly
  `"solver": "OpenFOAM"` and the control room renders it
  (`control_room.html:615, :843`), so the solver name is already on camera
  across the product. Silencing it in this one act would make it the odd one
  out. If it is a violation it is a fleet-wide one and the ruling should be
  fleet-wide.
- **The bibliographic locators were removed from what the screen says aloud.**
  The full citation carries "printed p.5 eq. (2), printed p.3 section 2", and
  "section 2" spoken on camera is indistinguishable from an internal rule
  number. The screen says the short form; `display_citation()` refuses to
  return it unless the authors, the report number and the year all appear in
  the full citation the reference file carries, so the short form cannot drift
  off the paper it claims.
- **The transcript wording doctrine** (`sdk/workflows/__init__.py:115-135`)
  passes: no dash, no banned register, every bullet capitalised. It is checked
  by `bullets()` at emit time, so a slip raises rather than reaching the
  screen.
- **No STL is announced to the viewport.** Sanaa's instruction is that any
  render must show the real computational mesh and not a surface tessellation,
  so the geometry beat is the grid page itself and `geometry.ready` is never
  emitted.

---

## 8. What this lane could not verify

- **That the screen renders correctly in the browser.** It was driven through
  `main()` with a stub emit and every event was inspected, but the running
  server was not touched and no page was loaded. The event names, payload
  shapes and figure URLs match the shipped helpers; that is agreement with the
  interface's contract, not a rendered screen.
- **That the patch still applies after the thermal proposal lands.** Both are
  cut against router blob `40521dae`. They touch different regions and are
  expected to compose, but that was not tested by applying both.
- **Whether the filmed prompt will be one of the six probed.** The prompts
  above are this lane's guesses at Sanaa's wording. If the Act B prompt is
  fixed, it should be driven through `classify()` before filming rather than
  assumed.
- **The provenance of the `SETTLE_BAND` constants in §6a.** What they are is
  measured and both candidate windows are now ruled out. Where the numbers
  actually came from is still not known, and the possibility that they were
  computed against an earlier state of the runs was not ruled out. That gap no
  longer affects the finding, because the caption's own rounding rule condemns
  them whatever their origin.

---

## 9. Compute

**Zero core-minutes.** No solver was started, no case was written to, and no
mesh was built. Every number was read from calculations that finished before
this lane began. The screen itself is a reader and spends nothing when it
runs, which is the property that makes it usable on camera.

The compute the screen *reports* is the compute those calculations already
cost: 117.4833 core-minutes actual against 56.8 core-minutes budgeted upfront
for the five force calculations, a ratio of 2.07, and 90.5 core-minutes
budgeted for the finer flow-picture grid. Those figures are carried from
`make_actB_sheet.py:24-32` and are stated by the screen as both actual and
estimate, per the cost-transparency rule. The dollar figure the screen shows
is derived at the owner-stated machine rate and is not measured; this box
cannot read its own billing.
