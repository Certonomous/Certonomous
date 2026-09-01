# Act D, multipoint optimisation — act script and camera strings

**What this file is.** The stage by stage script for the Act D multipoint
optimisation act: the NACA0012 section, one shape, three angles of attack. It
carries the exact strings that go on screen, in the order DEMO MODE fixes, plus
the figure titles and captions. The companion one page result sheet is
`ACT_D_multipoint_optimisation_sheet.tex` in this directory.

**Subject discipline.** Three different subjects have been called Act D and
their numbers must never be merged. This one is the two dimensional NACA0012
section on 4,032 cells where **the optimiser ran** and the gradient is verified
**at the final design point**. It is not the reference wing act, and it is not
the earlier section act where no optimiser ran.

**Every number below is read from the run root of the graded item**
`CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation`, item verdict
`PASS`, chain `COMPLETE declared=7 executed=7`, all seven arms `rc=0`. The
per number provenance is the comment block at the head of the sheet's `.tex`,
and the extracted series is `cases/dafoam/ladder-a/A1_so3_demo_series.json`,
produced under a planted reader control by
`cases/dafoam/build_so3_demo_series.py`. Grid figures come from the run's own
`polyMesh` via `cases/dafoam/render_so3_mesh_figures.py`, which refuses rather
than draws if its cell count disagrees with the frozen grade.

**The row on camera is the PATCHED row, and only that row.** The item graded
two rows on two builds of the mesh deformation library and both are `PASS`.
Which build produced a run is method, and the demo may withhold method; it may
never misstate a result, and it does not. The two rows are **not** a
repeatability pair and must never be shown as one: their gradient components
diverge by up to 24.17 per cent.

**The face nonetheless states that both runs happen and both meet the limit.**
The two row rule is a rule about the verdict, not about the camera: a DAFoam
verdict is two rows, shipped and patched, or it is not a verdict about DAFoam.
So the sheet carries one extra table row, `Runs of this case, both inside the
limit — 2 of 2`, and a note saying the two runs do not return the same shape
and are therefore not a repeat of one another. The measured basis is the grade
file: worst relative error on the multipoint objective J is 0.189 per cent on
one row and 0.253 per cent on the other, both against a five per cent band,
four of four pairs each. **The second design never goes on screen and the two
percentages are never offered as an agreement pair.**

---

## Stage order, and what is on screen at each beat

DEMO MODE fixes the stages and the order. Progressive tense while a stage runs,
and no past tense anywhere on screen. Short sentences. Results in tables. All
plots latexified. Real geometry and its real grid only.

### 1. Prompt

Professional wording, what a competent engineer would type.

```
Minimise the drag of this NACA0012 section averaged over three angles of
attack, 3.139, 5.139 and 7.139 degrees, weighted equally, at 10 m/s. One shape
serves all three. Verify the gradient at the final shape.
```

### 2. Restatement, confidence, and how cost is reported

```
Restating: one shared set of eight shape controls, one objective, the equally
weighted mean drag coefficient over three angles.
Thickness, enclosed area and leading edge radius are held as constraints.
Confidence: the gradient path on this section is verified. The optimiser has
not run this problem before, so the iteration count is a budget, not a
promise.
Cost: measured on this machine in processor-minutes, stage by stage, and
reported as the run goes.
```

No estimate figure goes on screen at this beat. The cost the act shows is the
one the run's own clock produces, and it is shown as each stage finishes.

### 3. One user assumption check

The single assumption the act surfaces, and the one the result turns on.

```
One thing your request does not fix: lift.
Nothing constrains the lift coefficient here, so the optimiser is free to
trade lift for drag. It will.
Say the word and lift is held instead; the lift gradients are verified
already.
```

### 4. Falsifier and gate, emitted before any evidence

```
Hypothesis: the adjoint gradient drives a descent, and it is still the right
gradient at the shape the optimiser hands back.
Falsifier: at the final shape, the gradient disagrees with an independent
finite difference by more than five per cent on any checked control.
Gate: four controls, three step sizes each, agreement quoted where the result
stops moving. Five per cent, fixed before the run.
```

### 5. Geometry

The uploaded surface renders. It is the section the case is solved on.

```
NACA0012 section, chord 1 m, reference area 0.1 m squared.
```

### 6. Meshing

```
Meshing.
4,032 cells. Far field radius 18.6 m. First layer height 2.06 to 4.07 mm.
Wall treatment: a continuous wall function, valid across the whole near wall
range.
```

Table on screen, wall resolution:

| Quantity | Value |
|---|---|
| Cells | 4,032 |
| Wall faces | 126 |
| First layer height | 2.06 to 4.07 mm |
| Far field radius | 18.6 m |

**NOT FOR CAMERA.** This beat said "Meshing, live", and that the real mesher
runs on the uploaded surface and the grid draws cell by cell. **None of the
three is what the stage does, and the script is corrected to the stage rather
than the stage to the script.** The shared sequencer refuses to point a live
mesher at a work directory that looks like a landed case tree, and this act's
run root is one: measured, both `FE-P` and `FE-S` under
`CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation` hold **both** of the
guard's tells, `system/controlDict` and `constant/turbulenceProperties`. So the
mesher does not run and the stage publishes `meshed: false`. That refusal is
correct — meshing there could destroy a graded run the age guard makes
unrepeatable — and this act does not work around it. The grid on screen is this
run's own `polyMesh`, rendered by `cases/dafoam/render_so3_mesh_figures.py`,
which refuses rather than draws if its cell count disagrees with the frozen
grade. The cell by cell draw is a separate renderer that is **not** delivered:
the stage publishes `drawn: false` unconditionally, and nothing on screen may
imply a draw that did not occur.

**Honest limit on this note.** No multipoint act is registered in the SDK —
`registered_acts()` returns `adjoint-wing`, `jet-flap`, `motor-thermal` and
`shock-reflection` — so no payload of this act was driven. What is measured is
the shared stage's own behaviour and the guard's predicate against this run
root's disk, not this act's emitted stage. The reference wing act, which **is**
built, was driven and does publish `meshed: false`.

### 7. Check before the budget

```
Geometry and grid: 10 seconds, before any optimiser time is committed.
Cost so far, 0.167 processor-minutes, measured on this machine.
```

### 8. Solving

Monitors advance at accelerated pace from the run's own series. The iteration
counter, the objective trace and the three drag and lift traces all move
together, and the elapsed clock moves with them.

```
Solving, major iteration 4 of 10.
Sweep point 2 of 3.
Objective 0.018430.
```

The objective trace fills in one major at a time, using the ten values in
Figure 3 of the sheet. The candidate table grows one row per major and is
never a run of transcript lines.

```
Optimal Solution Found.
Ten majors. The iteration budget is fifty.
```

### 9. Gates and checks

Tables, not prose. This is the planted control beat.

| Check | Result |
|---|---|
| Planted gradient error, 15 % | gate turns |
| Planted grid count, 4,039 | read back |
| Planted zero, seven quantities | all seven |
| Deliberately wrong step, 4 controls | 0 pass |
| Weighted sum identity, 4 controls | 9e-14 |

```
Each reader is shown a known false value before it is trusted. Each one sees
it.
The gradient check is driven at a deliberately unsuitable step to prove it can
fail. It fails there on every control, by 73 to 108 per cent.
```

Operating point statement:

```
Three angles registered at 1e-12 and read back with zero deviation.
Weights one third each, read back with zero deviation.
```

Grid statement:

```
One grid, 4,032 cells. No coefficient here carries a grid error bar.
```

### 10. Results

The sheet's tables and figures, in this order: Table 2, Figure 2, Table 3,
Figure 3, Table 4, Figure 4, Table 5, Table 6, limitations, uncertainty.

The headline, said in this order and never with the drag figure alone:

```
The weighted drag objective falls 16.2 per cent in ten majors.
Every lift coefficient falls with it, and at the lowest angle lift goes
negative.
This verifies the gradient and the optimiser. It is not a better aerofoil.
```

Cost line:

```
This run costs 14.2 minutes on one processor, 14.183 processor-minutes,
about one cent.
Geometry and grid 0.167, optimisation 6.950, endpoint gradient 2.533,
independent check 4.533.
Every one of those is a reading from this run's own clock.
```

Two-run statement, said with Table 4 on screen and never apart from it:

```
This case is solved twice, and each run is checked at its own final shape.
Both sit inside the five per cent limit.
The two runs do not return the same shape, so they are not a repeat of one
another, and one of them is on this sheet.
```

---

## Figure titles and captions, exactly as they go on screen

Titles at most ten words. Captions one line, at most twenty words. No paragraph
sits inside a figure; every explanation is in the sheet text beside it.

| Figure | Title | Caption |
|---|---|---|
| 1 | The grid the section is solved on | All 4,032 cells are drawn. The left view stops at about 5 m; the far field radius is 18.6 m. |
| 2 | Drag and lift at three angles of attack | Drag falls at every angle. Lift falls at every angle and turns negative at the lowest. |
| 3 | Objective against major iteration | Ten majors carry the objective from 0.0218060 to 0.0182832. The iteration budget is fifty. |
| 4 | Gradient check at the final shape | Every control sits inside the limit at all three steps. Table 4 is the middle step. |

Panel titles inside Figure 1: `Grid near the section` and `Grid at the leading
edge`.

---

## Numbers the act may quote, and the one rule that binds them

Every figure below is read from the graded run root. The drag reduction is
**never** quoted without the lift columns beside it: the grade file's own
`forbidden_readings` list forbids it, because lift is unconstrained in this
item.

| Angle, deg | C_D start | C_D final | C_L start | C_L final |
|---|---|---|---|---|
| 3.139 | 0.017239 | 0.016255 | 0.31190 | **-0.05676** |
| 5.139 | 0.020911 | 0.017470 | 0.49877 | 0.15320 |
| 7.139 | 0.027268 | 0.021125 | 0.66398 | 0.36119 |
| Weighted J | 0.0218060 | 0.0182832 | | |

| Quantity | Value |
|---|---|
| Optimiser | IPOPT |
| Majors taken | 10 |
| Iteration cap, registered | 50 |
| Tolerance, registered | 1e-5 |
| Terminal statement | Optimal Solution Found. |
| Line search cutbacks | 0 |
| Restoration iterations | 0 |
| Dual infeasibility, last major | 7.28e-6 |

| Shape control | Computed | Checked | Difference, % |
|---|---|---|---|
| Lower surface, x/c = 0.245 | -0.005589 | -0.005581 | 0.144 |
| Upper surface, x/c = 0.500 | +0.004554 | +0.004558 | 0.085 |
| Leading edge pair | -0.015521 | -0.015527 | 0.041 |
| Trailing edge pair | -0.001800 | -0.001796 | **0.253** |
| Limit, registered | | | 5.00 |
| Runs of this case, both inside the limit | | | 2 of 2 |

| Stage | Cost, core-min | Wall clock, s |
|---|---|---|
| Geometry and grid | 0.167 | 10 |
| Optimisation, 10 majors | 6.950 | 417 |
| Endpoint gradient | 2.533 | 152 |
| Independent check of it | 4.533 | 272 |
| Total | 14.183 | 851 |

Every compute figure the act quotes is measured. The per stage predictions and
their ratios stay off camera; the estimate against actual comparison for this
item is filed in `docs/COST_CALIBRATION.md` at ratio 0.126.

---

## NOT FOR CAMERA — four things a builder of this act must not do

1. **Do not borrow a feasibility probe from another run.** This run's own first
   stage is the 10 second geometry and grid arm, and that is what the
   pre-budget beat quotes. A separate 30 second alpha probe exists in a
   different run root, on a different item; putting its 35 seconds on this act's
   clock would put another run's number on this run's screen.

2. **Do not present the two graded rows as a repeatability pair.** Their
   gradient components diverge by up to 24.17 per cent. One row is on camera.

3. **Do not print any elapsed figure other than this run's own.** A standing
   capture directs the dafoam demo to show 20 minutes rather than 60. That
   instruction attaches to a 3,601 second figure on the reference wing act, not
   to this run. This act's measured path is 851 wall seconds, 14.2 minutes, and
   is therefore already under twenty; nothing here is invented and nothing
   contradicts that instruction. **Whether the 20 minute display figure is meant
   to extend to this act is referred upward and is not decided here.**

4. **Do not put a cost prediction on screen as what the run costs.** An earlier
   draft of this act quoted 114 core-minutes at the restatement beat and again
   at the cost beat. That figure is a sum of four per stage predictions, and
   this item's own registered cost prediction scored `MISS` by nearly a factor
   of eight. Every compute figure this act shows is now a reading: 0.167,
   6.950, 2.533 and 4.533 core-minutes, 14.183 in total, 851 wall seconds. The
   predictions and the ratios against them belong in the calibration ledger,
   not on camera.

## NOT FOR CAMERA — the registered predictions that missed

Four of this item's registered predictions scored `MISS`, and each one is a
finding rather than an embarrassment. None of them changes the item verdict:
predictions are scored, never composed into a verdict.

| Token | Registered | Measured | What it means |
|---|---|---|---|
| `P2_CL_at_alpha0_in_band` | HIT, lift at the middle angle in [0.45, 0.55] | **MISS** | The endpoint arm reads lift at the **final** shape, and it is 0.15320. The miss **is** the lift loss, measured by the instrument rather than argued. |
| `P6_SHIPPED_G5J_GATE_FAIL` | HIT, the shipped row's gradient gate fails | **MISS** | The shipped row **passed**. The defect this item expected to reproduce at the final design point did not reproduce here. |
| `P8_P_EVAL_at_least_one_evaluation_fails_per_F_arm` | HIT on both arms | **MISS** on both | 34 of 34 evaluations succeeded on each arm. Zero failures. The item was more robust than registered. |
| `P_COST_total_core_min_in_band` | band [60, 300] core-min, point 228.59 | **MISS**, 28.900 | The whole item cost an eighth of its estimate. The optimiser was priced at its 50 iteration cap and converged in 10 or 12. |

The cost calibration row for this item is already filed in
`docs/COST_CALIBRATION.md` and states the same ratio, 0.126.
