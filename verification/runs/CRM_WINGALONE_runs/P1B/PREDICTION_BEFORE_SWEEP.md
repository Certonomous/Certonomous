# P1B — PREDICTION, WRITTEN BEFORE THE SWEEP WAS RUN

**Written 2026-09-12, by a cfd `lab-lane`, BEFORE `band_sweep.py` was executed even once.**
This file exists so the prediction cannot be read back out of the answer.

## THE QUESTION

P1 graded `GATE FAIL` with `Y_SYMM_TOL = 1e-9`, achieving symmetry 13,312 against a registered
14,144. P2 reports the root plane is planar to **9.491133e-06 mesh-units** and that the count sits
on a **plateau of 14,144 across four decades of band (1e-3 to 1e0)**.

**This lane is re-deriving that plateau independently rather than registering a tolerance on a
cited table.**

## WHAT I PREDICT, BEFORE LOOKING

1. Faces with `|n_y| > 0.99`, counted within a band on each face's `max|y|`, will be
   **13,312 at 1e-9** and **14,144 across 1e-3, 1e-2, 1e-1 and 1e0**.
2. `max|y|` over the root-plane set on the plateau will be **9.491133e-06 mesh-units**.
3. The count will **rise again above 1e+1**, as far-field faces at y ~ 85 also carry y-normals.

## 🔴 WHAT RESULT WOULD HAVE MADE US LEAVE `Y_SYMM_TOL = 1e-9` ALONE

**This is the sentence the cfd-supervisor's ruling requires, and it is written here before the
measurement, not after it.**

**A. NO PLATEAU.** If the count crept monotonically with the band — 13,312 -> 13,728 -> 14,144 ->
14,900 -> ... with no flat interval — then **there is no natural stopping point, every tolerance is
a choice, and 1e-9 is as defensible as any other.** We would leave it alone and P1's `GATE FAIL`
would stand as a real geometric finding: the root plane genuinely is not planar. **A plateau is the
whole basis for calling this a measurement rather than a fit, and a plateau is a thing the data can
refuse to show.**

**B. A PLATEAU AT THE WRONG COUNT.** If the count were flat across four decades at any value other
than 14,144 — say a stable 13,900 — then the tolerance story and the independent block-topology
prediction **disagree**, and the right action is to investigate the disagreement, **never to move
the tolerance until the two routes agree.**

**C. A PLATEAU TOO COARSE TO BE PHYSICAL.** If `max|y|` on the plateau were large enough that a
`symmetryPlane` BC is ill-posed — a displacement comparable to a near-wall cell rather than
round-off — then **the defect is in the mesh and the repair is the mesh, not the tolerance.**

**Any one of A, B or C leaves `Y_SYMM_TOL = 1e-9` exactly where it is.**

## WHAT THIS FILE DOES NOT DO

It does not register the new tolerance — that is the addendum's, and the addendum is written only
if A, B and C are all refuted. It does not re-run P1. It does not alter P1's `GATE FAIL`, which
stays struck-but-legible under the supervisor's condition 1.
