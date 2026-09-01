# Act D, compressible multipoint — act script and camera strings

**What this file is.** The stage by stage script for the Act D **compressible**
multipoint act: the NACA0012 section, one shape, three angles of attack, run on
`DARhoSimpleFoam` at Mach 0.288. It carries the exact strings that go on
screen, in the order DEMO MODE fixes, plus the figure titles and captions. The
companion one page result sheet is `ACT_D_compressible_multipoint_sheet.tex` in
this directory, and its face is swept by
`check_actD_compressible_sheet_face.py`.

**Subject discipline, and it matters more here than anywhere else in this
family.** Four different subjects are called Act D and their numbers must never
be merged. This one is the two dimensional NACA0012 on 4,032 cells, **compressible**,
where the optimiser ran and the gradient is checked at the final design point.
Its sibling `ACT_D_multipoint_optimisation_script.md` is the same geometry,
the same grid and a different physics: **incompressible**, at a Reynolds number
ten times lower and at three different angles. **The two acts share a grid and
share nothing else.** A number carried from one to the other is wrong.

**Every number below is read from the run root of the graded item**
`CURRICULUM-D19M-a1-naca0012-subsonic-multipoint`, graded 2026-09-01T08:30:34Z.
The per number provenance is the comment block at the head of the sheet's
`.tex`.

**The row on camera is the PATCHED row, and only that row.** The item grades
two rows on two builds of the mesh deformation library. Which build produced a
run is method, and the demo may withhold method; it may never misstate a
result, and it does not. The two rows are **not** a repeatability pair and must
never be shown as one. Table 6 of the sheet states that both builds run and
gives their combined measured cost, so no viewer can take this run's own
17.650 core-minutes for the item's 35.166.

---

## THE ONE RULE THAT BINDS EVERY BEAT OF THIS ACT

The frozen grade file states it itself, at `gates.G-OPT9.<ROW>._cl_travels`:

> CL is UNCONSTRAINED here — alpha is the operating point, so there is no DV to
> trim with. THE THREE-CL TRIPLE therefore travels with every weighted-drag
> number this item publishes. **A reduction at unstated lift is not a
> reportable number.**

Operationally, and this is the thing most likely to be got wrong on this act:

- **The string `25.985` never goes on screen alone.** Every camera string,
  table cell, caption and voice line that carries it carries a lift value or
  the word *lift* in the same frame.
- **The frame is the beat, not the sheet.** A viewer who sees the drag figure
  on one screen and the lift triple on the next has been shown a reduction at
  unstated lift.
- The sheet's face is checked for this three ways — the negative final lift
  value present, lift within a character window of every occurrence, and the
  column headers — each with a planted control that makes the check go red.
  **The act's own strings are checked by the same rule and by nothing weaker.**

And the second binding rule, from `gates.G-OPT9.<ROW>._improvement_grades_nothing`:

> `DAFOAM_CHARTER.md` section 9 forbids grading an optimisation by the size of
> its improvement. `drag_reduction_pct` is reported and is an input to the
> REGISTERED intermediate threshold only.

So the 25.985 per cent is never introduced as what this run achieves. It is
introduced as a figure that clears a threshold fixed before the run.

---

## Stage order, and what is on screen at each beat

DEMO MODE fixes the stages and the order. Progressive tense while a stage runs,
past tense nowhere. Short sentences. Results in tables. All plots latexified.

### 1. Prompt

```
Minimise the drag of this NACA0012 section averaged over three angles of
attack, 2.787, 4.787 and 6.787 degrees, weighted equally, at 100 m/s and
300 K. One shape serves all three. Verify the gradient at the final shape.
```

### 2. Restatement, confidence, and how cost is reported

```
Restating: one shared set of eight shape controls, one objective, the equally
weighted mean drag coefficient over three angles, compressible at Mach 0.288.
Confidence: the compressible gradient path on this section carries no separate
check of its own. What this run establishes is one check, at the shape the
optimiser hands back.
Cost: measured on this machine in processor-minutes, stage by stage, and
reported as the run goes.
```

No estimate figure goes on screen at this beat, at any beat. The cost the act
shows is the one this run's own clock produces.

### 3. The ceiling, said out loud before any result

**This beat has no counterpart in the incompressible act and it is not
optional.** It is the camera rendering of a verdict ceiling registered before
the run, and it belongs here, before evidence, not after it.

```
Two things this run does not settle, and both are fixed before it starts.
The compressible gradient this optimiser spends carries no separate check of
its own on this section.
One of the eight shape controls, the trailing edge pair, is set aside by name
before the run, whatever value it returns, and counts in no total you will see.
```

### 4. One user assumption check

```
One thing your request does not fix: lift.
Nothing constrains the lift coefficient here, so the optimiser is free to
trade lift for drag. It will, and at the lowest angle it trades past zero.
Say the word and lift is held instead; the lift gradients agree to 0.019 per
cent already.
```

### 5. Falsifier and gate, emitted before any evidence

```
Hypothesis: the adjoint gradient drives a descent, and it is still the right
gradient at the shape the optimiser hands back.
Falsifier: at the final shape, the gradient disagrees with an independent
finite difference by more than five per cent on any checked control.
Gate: three controls, three step sizes each, agreement quoted where the
estimate stops moving. Five per cent, fixed before the run.
```

### 6. Geometry

```
NACA0012 section, chord 1 m, reference area 0.1 m squared.
```

### 7. Meshing

```
Meshing.
4,032 cells. Far field radius 18.6 m. First layer height 2.06 to 4.07 mm.
Wall treatment: a continuous wall function, valid across the whole near wall
range.
```

| Quantity | Value |
|---|---|
| Cells | 4,032 |
| Wall faces | 126 |
| First layer height | 2.06 to 4.07 mm |
| Far field radius | 18.6 m |

**NOT FOR CAMERA.** The shared stage sequencer refuses to point a live mesher
at a landed, graded run, and publishes `meshed: false` with a plain sentence
saying nothing is meshed. That refusal is correct and this act does not work
around it. The grid drawn here is this run's own `polyMesh`, byte identical to
the incompressible item's — six files md5 matched, recorded in the sheet's
provenance block — which is why the same figure is a true picture of both.

### 8. Check before the budget

```
Geometry and grid: 10 seconds, before any optimiser time is committed.
Cost so far, 0.167 processor-minutes, measured on this machine.
```

### 9. Solving

```
Solving, major iteration 4 of 10.
Sweep point 2 of 3.
```

```
Optimal Solution Found.
Ten majors. The iteration budget is forty.
```

**NOT FOR CAMERA, and it is a gap rather than a choice.** The frozen grade file
carries no objective per major series for this item, so there is no checked
trace to fill an objective monitor with. Filling it would mean a lane parsing
the optimiser log by hand, and a number from a reader that has not been shown
able to see a planted false value is not evidence. **What this act owes before
it can show a descent curve is a `build_d19m_demo_series.py` with a planted
reader control, modelled on `build_so3_demo_series.py`.** Until that exists the
solving beat advances the iteration counter and the sweep counter and shows no
objective trace, which is honest; inventing the curve is not.

### 10. Gates and checks

Tables, not prose. This is the planted control beat.

| Check | Result |
|---|---|
| Planted grid count, 4,039 | read back |
| Planted zero, 120 values | 2e-16 |
| Planted angle, one degree adrift | read back |
| Planted cost row, 6.384 processor-minutes | read back |
| Deliberately wrong step, 3 controls | 0 pass |
| Weighted sum identity, 8 controls | 8e-12 |

```
Each reader is shown a known false value before it is trusted. Each one sees
it.
The gradient check is driven at a deliberately unsuitable step to prove it can
fail. It fails there on every control, by 52 to 110 per cent.
```

```
Three angles registered at 1e-12 and read back with zero deviation.
Weights one third each, read back with zero deviation.
One grid, 4,032 cells. No coefficient here carries a grid error bar.
```

### 11. Results

The sheet's tables and figures, in this order: Table 2, Figure 2, Table 3,
Table 4, Table 5, Table 6, limitations, uncertainty.

**The headline, said in this order and never with the drag figure alone:**

```
The weighted drag objective falls 25.985 per cent, and lift falls with it:
from 0.29875, 0.50000 and 0.67366 to minus 0.15737, 0.07216 and 0.30540.
At the lowest angle the lift is negative.
That figure clears a two per cent threshold fixed before the run. It is not
what this run is judged on, and it is not a better aerofoil.
```

Gradient statement:

```
The gradient is checked at the final shape on three controls, and agrees to
0.16 per cent against a five per cent limit fixed before the run.
Agreement finer than two and a half to five per cent is at the resolution of
the comparison itself. That range is reported and is never used as a limit.
```

Cost line:

```
This run costs 1,059 seconds, 17.7 minutes on one core, 17.650
processor-minutes, about two cents.
Geometry and grid 0.167, optimisation 8.083, endpoint gradient 3.017,
independent check 6.383.
Both builds of this case together cost 35.166 processor-minutes.
Every one of those is a reading from this run's own clock.
```

---

## Figure titles and captions, exactly as they go on screen

Titles at most ten words. Captions one line, at most twenty words.

| Figure | Title | Caption |
|---|---|---|
| 1 | The grid the section is solved on | All 4,032 cells are drawn. The left view stops at about 5 m; the far field radius is 18.6 m. |
| 2 | Drag and lift at three angles of attack | Lift falls at every angle and turns negative at the lowest, which is the price of the 25.985 per cent drag reduction. |

Panel titles inside Figure 1: `Grid near the section` and `Grid at the leading
edge`.

---

## Numbers the act may quote

Every figure below is read from the graded run root. **The drag reduction is
never quoted without the lift values in the same frame.**

| Angle, deg | C_D start | C_D final | C_L start | C_L final |
|---|---|---|---|---|
| 2.787 | 0.012653 | 0.011620 | 0.29875 | **-0.15737** |
| 4.787 | 0.016327 | 0.012052 | 0.50000 | 0.07216 |
| 6.787 | 0.022952 | 0.014766 | 0.67366 | 0.30540 |
| Weighted J | 0.0173107 | 0.0128125 | | |

| Quantity | Value |
|---|---|
| Optimiser | IPOPT |
| Majors taken | 10 |
| Rows in its own table | 11 |
| Iteration cap, registered | 40 |
| Minimum majors, registered | 5 |
| Improvement threshold, registered | 2 per cent |
| Terminal statement | Optimal Solution Found. |

| Shape control | Computed | Checked | Difference, % |
|---|---|---|---|
| Lower surface, x/c = 0.245 | -0.003382 | -0.003377 | 0.159 |
| Upper surface, x/c = 0.500 | +0.002508 | +0.002510 | 0.071 |
| Leading edge pair | -0.018664 | -0.018662 | 0.006 |
| All three, on the objective | | | 0.030 |
| All three, on lift | | | 0.019 |
| Limit, registered | | | 5.00 |
| Trailing edge pair | | | set aside before the run |

| Stage | Cost, core-min | Wall clock, s |
|---|---|---|
| Geometry and grid | 0.167 | 10 |
| Optimisation, 10 majors | 8.083 | 485 |
| Endpoint gradient | 3.017 | 181 |
| Independent check of it | 6.383 | 383 |
| This run, total | 17.650 | 1,059 |
| Both builds, together | 35.166 | 2,110 |

The internal unit is core-minutes and the screen word is processor-minutes;
the quantity is the same and the sequencer owns that substitution.

---

## NOT FOR CAMERA — five things a builder of this act must not do

1. **Do not quote 25.985 per cent without lift in the same frame.** This is the
   grade file's own forbidden reading and it is the single most likely error on
   this act. A drag reduction at unstated lift is not a reportable number.

2. **Do not carry a number, a y+ range or a Reynolds number across from the
   incompressible act.** Same grid, different physics. Its y+ is about 30 to
   60; this act's is about 250 to 490, because the speed is ten times higher.
   A viewer given the wrong one is wrong by roughly eight.

3. **Do not present the two graded rows as a repeatability pair.** One row is
   on camera and the other's combined cost is the only thing it contributes.

4. **Do not put a cost prediction on screen as what the run costs.** Every
   compute figure this act shows is a reading: 0.167, 8.083, 3.017 and 6.383
   processor-minutes, 17.650 for this run, 35.166 for both builds, 1,059 and
   2,110 wall seconds. The registered 34.10 point prediction and the 1.0313
   ratio against it belong in the calibration ledger, not on camera. **That
   exact defect was caught on this family once already, in four places.**

5. **Do not soften the ceiling into a footnote.** It is beat 3, before any
   evidence, and it is a band across the top of the sheet. A ceiling a viewer
   meets after the headline is a ceiling that has already failed.

## NOT FOR CAMERA — what this act still owes

- **A `build_d19m_demo_series.py` with a planted reader control**, without which
  the solving beat shows no objective trace (§9 above).
- **A D19M-named mesh render from D19M's own run root.** The current figure is
  correct — the grid files are byte identical — but its provenance rests on a
  hash comparison rather than on the figure's own path.
- **This item's row in `docs/COST_CALIBRATION.md`.** Rule 12 owes an
  estimate-versus-actual comparison at every process completion and **the row
  is not on disk**: 35.166 core-min measured against 34.10 registered, ratio
  1.0313, $0.030067 derived and not measured. Reported here as OWED; filing it
  is not a demo lane's act.
