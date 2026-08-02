# W1 — the TMR NACA 0012 item, and a repair path that does not exist

Approved item `agp-4369c99cdd7f`, **603 core-minutes** — the largest single
item in the approved W1 queue, 41% of its 1,463 core-minutes. Ruled 2026-08-02
at **0 core-minutes** of solver time; the two measurements below are array
arithmetic on a grid file and took seconds.

The item: *"Run the TMR 2D NACA 0012 airfoil case on the three coarsest
reference grid sizes at 0, 10, and 15 degrees and compare lift, drag, and
surface pressure against the published CFL3D and FUN3D values."* Nine rungs.

**Ruling: dismissed. Eight of the nine rungs do not reach a steady state under
this solver, the ninth supports no comparison claim by its own record, and the
time-accurate alternative is priced at 11,700 to 30,300 core-minutes for ONE
rung. The cheap repair path is refuted below.**

---

## 1. The item asks for an experiment that is already closed as unaffordable

`demo-output/website/tmr/naca0012_status.json` records the state in its own
first field: *"one rung measured; the remaining rungs do not reach a steady
state under this solver configuration."*

The one measured rung is alpha 10 on the 113x33 grid (3,584 cells): Cl
1.1164357439, Cd 0.0044948532678, tail spreads 4.6e-08 and 5.7e-08, 5,000
iterations, 95.2 s. Its own record refuses the comparison this item is built
on: *"Published values are finest-grid (897x257) only; a single coarse rung
supports no comparison claim and none is made."*

The rest is root-caused, by scheme substitution rather than by guess:

- Alpha 10 on 225x65 — a sustained force oscillation under second-order
  momentum advection at two relaxation levels (16,000 and 24,000 iteration
  budgets), swinging with a period of thousands of iterations and never
  decaying.
- Alpha 0 on 113x33 — the same oscillation, **antisymmetric, with Cl swings of
  0.3 on a symmetric case**.
- First-order momentum is perfectly steady and unusable (Cd 0.0229,
  overdiffused). TVD `limitedLinear` reduces the cycle to about 3e-4 around Cd
  0.0090 and never flattens over 15,000 iterations. *"The feedback lives in the
  wake and trailing-edge convection."*

And the time-accurate route has been priced, by a closure document written for
that purpose (`demo-output/website/tmr/C4_naca0012_closure.md`), whose headline
is *"the ~480 core-minute estimate is short by 1-3 orders of magnitude, for ONE
rung"*:

| | core-minutes |
| --- | --- |
| medium/alpha10 to 30 convective units | **11,700 – 30,300** |
| medium/alpha10 to "hundreds of convective units", the proposal's own stated requirement | **~117,000 – 303,000** |
| measured, 2026-07-26 cold start, reaching 0.925 units | 359.5 |
| measured, seeded from the steady field — **slower**, reaching 0.018 units | 59.9 |
| **this item's estimate, for nine rungs** | **603** |

The seeded restart being slower than the cold start is worth keeping: seeding
does not rescue it, because the impulsive adjustment from the steady seed is
itself the transient.

**This item is dismissed, not deferred.** Its estimate is short by two to three
orders of magnitude *per rung* and it asks for nine.

---

## 2. The repair path that would have rescued it, tested and refuted

There was one cheap way this could have gone differently, and it was worth an
hour to rule out because tonight's other W1 item is built on it.

`w1-bump-on-nasa-own-grids` exists because `plot3dToFoam` v2606 **damages** TMR
grids: on the 177x81 and 353x161 bump grids it duplicates the two bottom-corner
boundary faces, producing two open cells and two spurious 89.5-degree faces.
The fix was `W1_runs/p3d_to_polymesh.py`, a direct index-based converter. The
C4 closure lists mesh quality as its cause 2, citing *"max aspect ratio
26,446,226.94 on 1,822 cells, 170 severely non-orthogonal faces, and 'Failed 1
mesh checks'"* on the `plot3dToFoam`-converted 225x65 grid — the same converter,
the same symptom family. If that aspect ratio were conversion damage, the
NACA 0012 ladder would be unblocked by a converter already written and
validated.

**It is not. Both checks refute it.**

**The aspect ratio is NASA's own grid.** Computing cell edge ratios directly
from the published node array — no OpenFOAM, no converter — gives a maximum of
**2.645e+07**, against checkMesh's **26,446,226.94** on the converted mesh.
They are the same number. The worst cell sits at the downstream end of the wake
cut, streamwise edge **95.73** against wall-normal edge **3.62e-06**, which is
simply how a C-grid that extends to 500 chords while holding its wall spacing
is built. 580 cells exceed edge ratio 1e5 and 212 exceed 1e6; the median cell
is 12.1. CFL3D solves these same grids, with a compressible implicit scheme and
different numerical dissipation.

**And the conversion is sound, to the point.** checkMesh counts 29,152 points
where 225 x 65 x 2 = 29,250 nodes were read. The 98 missing are accounted for
exactly: walking inward from the wake cut, node `j` and node `nj-1-j` at the
wall are coincident to below 1e-12 for exactly **49** pairs per plane, and
49 x 2 = 98. The C-grid's wake cut is closed by merging exactly the points that
are coincident and nothing else.

So the NACA 0012's problem is not the bump's problem. The bump's converter
invented geometry; here the converter is faithful and the geometry is hostile
by design. **The repair does not transfer, and the dismissal stands.**

---

## 3. The successor nobody filed

`naca0012_status.json` names the honest next step in its own findings: *"a
time-accurate solve with averaged coefficients, **or a dissipation study**, is
the honest next step."* The first half is priced out above. The second half has
never been filed — no item anywhere in the docket asks it, on a search of every
proposal.

It is also cheap, and the measurement to price it is already on the record: the
alpha-0 coarse rung is 3,584 cells and ran 5,000 iterations in 95.2 s at one
rank. Filed today as **`w1-naca0012-dissipation-study`**.

**One thing it is not.** A dissipation study on a 3,584-cell airfoil at zero
incidence in attached flow is **below the hardness floor**, and it is filed
labelled that way. It qualifies under
`docs/charters/CASE_SELECTION_CHARTER.md` section 3 as an **instrument check** —
"a control whose answer is known independently of the thing being tested" — and
it is exactly that: first-order momentum is already known to be perfectly
steady and overdiffused, which is the control the other schemes are read
against. It is not a result, it never appears as one, and it is not filmed.
What it buys is a decision on a 603 core-minute item and a 150 core-minute one,
which is the only reason it is worth a night at all.

---

## 4. Two other items this touches and does not move

- **`tmr-naca0012-complete-ladders`** (W5, approved, 150 core-minutes) is the
  item the C4 closure was written against, and the same 11,700-to-30,300
  measurement prices it out on the same arithmetic. **W5 holds it; this note
  does not touch it**, and flags it only so the two are not ruled apart.
- **`w1-f5b-pitching-naca0012`** (W1, approved, 120 core-minutes) is a
  *pitching* NACA 0012 — dynamic stall, unsteady by construction and HARD on
  criterion 3. Nothing here bears on it: its whole point is the transient this
  item was trying to avoid.

---

## Related

- `demo-output/website/tmr/naca0012_status.json`, measured block and findings.
- `demo-output/website/tmr/C4_naca0012_closure.md` and `.json`, the pricing.
- `demo-output/website/campaign/W1_bump_nasa_grids.md` §2, the converter defect
  that does not transfer.
- `models/tmr/naca0012/grids/n0012_225-65.p3dfmt`, the grid measured in §2.
