# K2bU3R3_D59 demo assets -- 3-D data centre rack row

**Case:** `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59`
**Mesh:** 137,000 cells, hexahedral, uniform h = 0.059 m
**Solver:** `buoyantBoussinesqPimpleFoam`, transient, adaptive dt, `endTime` 80 s
**Geometry:** room 3.6 x 3.5 x 2.7 m, four racks, **open row ends**
**Verdict:** **`GATE REACHED`**

Every figure in this directory carries that verdict burnt into the image.

## THE VERDICT IS `GATE REACHED` AND NEVER `PASS`

This is the single most important line in this file.

K2bU3R3's gate is a **survives/damps DISCRIMINATOR**. It asks which of two
behaviours occurred and answers SURVIVES, DAMPS or UNDECIDABLE:

* `p2p >= 0.30 K` **and** `ratio >= 0.8` -> SURVIVES
* `p2p <= 0.10 K` **or** `ratio <= 0.5` -> DAMPS

**There is no band for a value to lie inside**, and `PASS` is a value-in-band
term. It therefore does not apply to this gate at all. The verdict was
deliberately corrected away from `PASS` on **2026-09-09** under
`VERIFICATION_CHARTER` section 2, and any figure, caption, filename or table
here reading `PASS` would re-introduce exactly the defect that correction
removed.

**This is not left to whoever writes the caption.**
`scripts/demo3d_render_common.py` records `allowed_verdicts = {"GATE REACHED"}`
for this case, and `assert_stamp` **refuses** any stamp carrying `PASS` before a
single pixel is rendered. `scripts/selftest_demo3d_render.py` drives that
refusal in both arms -- the real stamp must be accepted and a forged `PASS`
stamp must be refused -- because a guard never shown catching anything is not a
control.

## The measured result

| Quantity | Value | Pre-registered meaning |
|---|---|---|
| final window 60-80 s peak-to-peak | **0.6058 K** | `<= 0.10 K` means DAMPS |
| preceding window 40-60 s peak-to-peak | 1.4414 K | reference for the ratio |
| **ratio** | **0.420** | **`<= 0.5` means DAMPS** |
| final window mean | 293.5306 K | reported |
| planted-zero control | armed; plant recovered | detection floor 1.234e-03 K, 81x below the 0.1 K DAMPS floor |
| outcome | DAMPS | the discriminator's answer |

The graded quantity is the mean of the four rack inlet temperatures. The ratio
0.420 clears the `<= 0.5` DAMPS threshold; the p2p itself does not clear the
`<= 0.10 K` arm, and the gate's OR is what carries the outcome.

`make_k2bU3R3_tables.py` imports the grade's **own** reader
(`analyse_k2bU3.series`) and refuses if its numbers do not reproduce
`K2bU3R3_GRADE.txt`. A plot disagreeing with the graded value of the same
quantity would be a second, unaccountable number wearing the authority of the
first.

## What the outcome does and does not say

The 3-D case **damps** the oscillation the 2-D slice sustained. Per the grade's
own outcome text: the 2-D finding **stands** as true of the 2-D slice -- it is
not retracted and it was not wrong. What changes is its **extrapolation**. The
figures say that and no more.

## Why the open row ends are the point

The rack row spans x = 0.6 to 3.0 m in a room 3.6 m long. The gaps at x < 0.6
and x > 3.0 are the **open row ends**: air leaving the hot aisle can travel
along x, round the end of the row, and re-enter the cold aisle.

**A two-dimensional slice cannot have that path at all.** It is the spanwise
freedom that only exists in 3-D, and it is why the 2-D result needed testing in
3-D rather than extrapolating. `K2bU3R3_open_row_ends` and
`K2bU3R3_recirculation` are the two figures that show it.

## The files

| File | What it is |
|---|---|
| `K2bU3R3_temperature_field.png/.pdf` | y-z plane at x = 1.5 m: cold aisle, rack row, hot aisle. The figure a 2-D slice could also produce |
| `K2bU3R3_open_row_ends.png/.pdf` | x-y plane at rack mid-height with in-plane velocity. **The row ends and the spanwise path** |
| `K2bU3R3_recirculation.png/.pdf` | streamlines seeded across the hot aisle, integrated both ways; the loop round the row ends |
| `K2bU3R3_mesh.png/.pdf` | hexahedral mesh crinkle-cut at x = 1.8 m. **The "it is not a wedge" figure**; the notch is the rack void |
| `K2bU3R3_rack_inlet_series.png/.pdf` + `.csv` | the graded series with both windows shaded and both p2p values |
| `K2bU3R3_gate.png/.pdf` + `.csv` | the gate: thresholds, measured values, controls, verdict |

## Reading the pictures

* Supply is 289 K; rack discharge sits about 12 K above it. The field at
  t = 80 s spans 289.00 to 307.04 K.
* **The colour bar runs 289 to 305 K, which is narrower than the field.** A
  handful of cells on the rack outlet patches reach 307 K, and letting them set
  the scale flattens the room to one colour. Every temperature caption states
  both the colour-bar bounds and the field's true range, and the colour range is
  asserted before each render so a caption cannot quote a range the picture did
  not use.
* In `K2bU3R3_recirculation` the grey block is the rack row drawn as
  **geometry, not field**. The racks are voids in this mesh, so without it a
  reader sees a hole and cannot tell it is the hardware. Every caption showing
  it says so.

## Regenerating

```
xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview/render_k2bU3R3.py
python3           docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview/make_k2bU3R3_tables.py
```

The renders read the graded tree through a scratch case of symlinks, write
nothing into it, and prove it unchanged afterwards. **No solver is run.**

## What the renderers refuse

Each is a defect that actually occurred while these figures were made:

1. **a stamp carrying `PASS`** -- checked before any compute;
2. **a colour bar disagreeing with its own caption.** Adding a second
   representation re-scales the transfer function behind your back: the row-end
   figure came out with a bar running to 307 K while the aisle figure beside it
   ran to 301 K. The range is now re-applied and asserted immediately before
   each render;
3. **a mirrored view.** Looking from -x put the cold aisle on the right while
   the caption said left. The camera direction was corrected, not the caption;
4. **a mesh figure with no visible cut.** The first version looked at the uncut
   face and shipped a featureless solid block under a caption promising the rack
   void notch;
5. **a framing set by something other than this code** -- a hand-typed scale, or
   `ResetCamera`'s bounding sphere (5.70 m diagonal against a 2.7 m height, so
   axis views came out at half size), or the automatic reset a fresh view
   performs on its first render. Framing is now computed by projecting the room's
   eight corners and asserted afterwards;
6. **an empty, tiny or stale image**, and a caption glyph the font drops.

## DIMENSIONALITY EVIDENCE — read from the mesh that exists, not from any dict

Recorded 2026-09-10 by a heat-transfer `lab-lane` at the supervisor's standing
instruction, after the closure team offered three "genuinely 3-D" families that
were all one cell thick with `empty` spanwise patches. **Dimensionality is never
inferred from a cell count and never read from `blockMeshDict`.** The readings
below come from the built mesh.

**1. `log.checkMesh`, verbatim:**

| Case | `log.checkMesh` line |
|---|---|
| `K2bU3R3_D59` | `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` |

**2. Patch types in `constant/polyMesh/boundary`, counted by type:**
**10 `patch`** and **8 `wall`**; **zero `empty`**, **zero `wedge`**. An `empty`
or `wedge` patch would disqualify the 3-D claim outright.

**3. The cell-count ratio between grid levels — NOT AVAILABLE, and said so
rather than fabricated.** K2bU3R3 is a **single-mesh rung**: it asks whether the
2-D limit cycle survives at the one builder-feasible 59 mm module, and it
carries no grid ladder. There is no second level to take a ratio against, so
the third check cannot be applied here. It is not reported as passed.

**Verdict on "is genuinely 3-D": PASS**, on checks 1 and 2, which are readings
of the mesh itself. The bounding box corroborates: `(0 0 0) (3.6 3.5 2.7)` m —
three directions of order metres, and 137,000 hexahedra spanning them.

## POST-GRADING WRITES INTO THE GRADED TREE: NONE

Checked 2026-09-10. Nothing under
`verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59/` carries an mtime
later than the grade at 2026-09-07 19:42 UTC. The tree is clean.

*(The sibling directory `K2b_runs/K2b3D_probe/` — a pilot probe, not a graded
case — did receive a `VTK/` directory on 2026-09-10 17:46. It grades nothing
and no verdict rests on it. It is recorded here so the write is not mistaken
later for a write into `K2bU3R3_D59`, which it is not.)*

## RULE 4 RE-CONFIRMED TODAY, AND BY WHICH INSTRUMENT

Re-run 2026-09-10: `python3 scripts/mark_done_adaptive.py --preset k2bu3r3`
returned **rc 0, `DONE K2bU3R3_D59`**, with `--selftest` passing first. It
reported clause 1 derived from the solver log (End lines 1, `FOAM FATAL` 0, last
time 80 == `endTime` 80) and adaptive clause 5 as `n_exec = 995 == n_time = 995`.

**`scripts/mark_done_adaptive.py` is the instrument that certified this case** —
it is the writer of the `DONE.K2bU3R3_D59` marker's text, "strict completion
rule met (adaptive clause 5)". The case-specific
`K2b_runs/mark_done_k2bU3R3.py` is **NOT** that instrument and cannot be: see
the defect note filed with the heat-transfer supervisor on 2026-09-10.
