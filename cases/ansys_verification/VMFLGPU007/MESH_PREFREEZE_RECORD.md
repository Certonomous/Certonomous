# VMFLGPU007 — MESH BUILT AND CHECKED BEFORE THE FREEZE (Ruling A)

**Written by `ansys-lane-opus` (lane R2), 2026-08-27.** The supervisor's Ruling A:
*"Registering a cell count nobody has observed is registering a guess, and the
birth-certificate check would then compare a real mesh against a number I made up. That is
not a control, it is a coincidence detector."* This file is the observation.

**This is legitimately pre-compute: no solver runs, no graded quantity is produced, and the
gate is untouched.** `blockMesh` and `checkMesh` build and inspect a mesh; they do not solve
and they compute nothing the gate reads.

**The mesh was built in a SCRATCH directory, NOT the run root.** Scratch path:
`/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/ansys-lane-r2/mesh/{L1,L2,L3}`
— temp only, and **not a handoff channel** (L-186): every number below is recorded *here*, in
the repository, because the scratch tree will be wiped. The run root
`verification/runs/ansys_verification/VMFLGPU007` **still does not exist on either box**, which
is what rule 4's age guard requires and what proves this case still has zero compute.

Built on the lab box with **OpenFOAM v2606** (`/usr/lib/openfoam/openfoam2606/etc/bashrc`),
CPU only, seconds of wall time.

## The registered levels

Placeholders in `case/system/blockMeshDict.template` are resolved by a generator that
**solves** for the grading so the first-cell height is exact, rather than being tuned by hand.
`simpleGrading`'s expansion ratio `G = (last cell)/(first cell)` over `n` cells gives a
geometric progression of ratio `r = G**(1/(n-1))` and `d1 = L(r-1)/(r**n - 1)`; `G` is found
by bisection and the achieved `d1` is asserted equal to `H1` to 1e-9 by an explicit branch
(never `assert` — `python3 -O` strips those).

**`H1 = 0.07 m` — THE FIRST-CELL HEIGHT AT EVERY WALL, HELD IDENTICAL AT ALL THREE LEVELS.**
This is the constant that makes this a mesh-sensitivity family and not a Roache triple
(Ruling B).

| level | NXI | NXD | NYU | NYL | GU | GUINV | GC | **MEASURED cells** |
|---|---|---|---|---|---|---|---|---|
| **L1** | 16 | 96 | 24 | 10 | 4.545613 | 0.219992 | 1.950522 | **3 648** |
| **L2** | 24 | 144 | 36 | 12 | 2.354314 | 0.424752 | 1.401442 | **7 776** |
| **L3** | 36 | 216 | 52 | 14 | 1.203850 | 0.830668 | 1.041071 | **16 128** |

Cell counts are `NXI·NYU + NXD·NYU + NXD·NYL`, **predicted before the run and then MEASURED
from `checkMesh`'s own `cells:` line — the two agree exactly at all three levels.** These
measured numbers are the birth-certificate targets.

## checkMesh — the pre-freeze fact

| level | rc | verdict | max non-orthogonality | max skewness | max aspect ratio | severe (`***`) |
|---|---|---|---|---|---|---|
| L1 | 0 | **Mesh OK.** | 0 | 1.14e-13 | 4.464286 | 0 |
| L2 | 0 | **Mesh OK.** | 0 | 1.36e-13 | 2.976191 | 0 |
| L3 | 0 | **Mesh OK.** | 0 | 2.52e-13 | 1.984127 | 0 |

**No level FAILS and no level WARNS**, so under Ruling A the freeze does not wait.
Non-orthogonality is exactly 0 and skewness is at machine epsilon because the blocks are
axis-aligned hexahedra; the aspect ratio *improves* with refinement (4.46 → 2.98 → 1.98) since
x is refined while the wall spacing is held.

**A triage recorded rather than buried:** `checkMesh` first exited **rc = 1** on all three
levels with `cannot find file ".../system/fvSchemes"`. That was **my harness, not the mesh** —
my minimal case carried only `controlDict`, and `checkMesh` loads `fvSchemes`/`fvSolution`. The
condition was cleared (the case's own `fvSchemes` copied in, `fvSolution` materialised from its
template) and the check **re-run**, not inferred green. The `Mesh OK` rows above are from the
re-run.

## The wall spacing: a defect in MY OWN first design, found before the freeze

The first family I generated used **`H1 = 0.03`**. It meshed cleanly and `checkMesh` said
`Mesh OK` on all three levels — **and it was wrong**, for a reason no mesh check can see.

From the manual's own properties (ρ = 1, μ = 1e-4, so ν = 1e-4) and the verified inlet
(u_max = 2.8, u_bulk = 2.570882, duct height 4H so D_h = 8H): Re_Dh = 205 671, Dean's smooth
2-D channel correlation `Cf = 0.073·Re^-0.25` gives Cf = 0.003428, τ_w = 0.011327 and
**u_τ = 0.106434 m/s**. The first-cell **centre** then sits at

| `H1` | first-cell centre | **design y+** |
|---|---|---|
| 0.03 | 0.0150 | **16.0** — buffer layer, **invalid** |
| 0.05 | 0.0250 | 26.6 — still below the band |
| **0.07** | **0.0350** | **37.3 — inside 30..300** |

**The manual specifies standard k-ε with STANDARD WALL FUNCTIONS, which are valid only in the
log layer.** A mesh whose first cell sits at y+ ≈ 16 puts the wall treatment in the buffer
layer, where the log law it assumes does not hold — so the original family would have been
solving a slightly different model from the one the manual specifies, and every `Mesh OK`
would still have been true. **`H1` was therefore raised to 0.07 and all three levels rebuilt
and re-checked.** The table above is the rebuilt family. Recorded because a mesh that passes
every geometric check can still be wrong for the physics, and the freeze is where that has to
be caught.

**This is an ESTIMATE, not a measurement, and is labelled as one.** A realised y+ requires a
solve. The `yPlusFO` function object records the achieved y+ per write, and the comparator is
to read it and refuse a run outside a registered band. **Expected and not a defect:** y+ → 0
at separation and reattachment, because τ_w → 0 there by definition; any backward-facing step
under wall functions has this, and the registered band must be stated on the developed/attached
region, never as a global floor.

## A HARD LIMIT ON THIS FAMILY, which is Ruling B's own argument in numbers

Holding `H1` fixed while refining means the wall cell eventually becomes *larger* than the
uniform spacing, at which point no expansion ratio ≥ 1 can produce it. The generator
**refuses** rather than silently inverting the grading:

> `REFUSE: target first cell … >= uniform spacing … -- grading cannot be >1 and this level is not admissible`

L3 is already close to that wall: `GU = 1.2039` and `GC = 1.0411` are nearly uniform, because
block C's uniform spacing at NYL = 14 is 1/14 = 0.0714 against `H1 = 0.07`. **So L3 is
effectively the last admissible level of this family.** A fourth, finer level could only be
obtained by *reducing* `H1` — which would drop y+ below the log layer and **change the
turbulence model's wall treatment, i.e. change the case.**

**That is the concrete, measured reason this cannot be a Roache triple**, and it is stronger
than the general argument: it is not merely that refinement is unsystematic near the wall, but
that **systematic refinement of this family is arithmetically impossible** without abandoning
the wall treatment the manual specifies. The prereg registers a mesh-**sensitivity** family,
**no GCI and no observed order**, per Ruling B.

## What this record does NOT establish

- **No solver has run.** No velocity, no temperature, no Nusselt number, no residual exists.
- **No y+ has been measured** — the figure above is a correlation estimate, and is labelled so.
- **Nothing about the gate.** No band, limb, threshold, cap or label is set or moved here.
- The mesh has not been built in the run root and **must not be** before launch.

---

## The generator is DRIVEN too — and driving it caught a defect in one of its own guards

`resolve_blockmesh.py` is committed beside this case so the mesh is reproducible from the
frozen template and the registered level table, and so the launcher calls the same bytes the
freeze cites. Its refusals are driven, not described:

| arm | outcome |
|---|---|
| **CONTROL** — the three registered levels | all `rc = 0`, each printing the solved grading with `d1 == 0.070000000` at both wall families |
| **F1 — inadmissible level** (NYL = 20, which needs H1 < 0.05) | `rc = 1` — *"REFUSE: target first cell 0.07 >= uniform spacing 0.05 for L=1 n=20 -- grading cannot be >1 and this level is not admissible"* |
| **F2 — odd NYU** (51) | `rc = 1` — *"REFUSE: NYU must be even (two-sided grading splits it in half)"* |
| **F3 — unresolved placeholder** (`__GC__` typo'd to `__GC_TYPO__`) | `rc = 1` — *"REFUSE: unresolved placeholder(s) remain in the generated blockMeshDict: ['__GC_TYPO__']"* |

**F3 failed on its first drive, and that is why it is here.** The guard's regex was
`r"__[A-Z0-9]+__"`, whose character class **excludes the underscore**, so `__GC_TYPO__` did not
match: the guard passed, `rc = 0`, and an unresolved placeholder went straight into the
generated `blockMeshDict`. Repaired to `r"__[A-Z0-9_]+__"` and re-driven. A guard that only
ever sees well-formed input is not known to work.

**A second trap, recorded because it nearly fooled me.** On an earlier drive the F1 and F2 arms
both returned `rc = 1` and *looked* like clean refusals. They were not — they were a
`NameError` crash from a missing `import sys` I had truncated while assembling the file. **A
non-zero exit code is not evidence that the guard fired**; only the refusal *message* is. Both
arms above are quoted with their text for exactly that reason.

**Provenance closed:** the committed `resolve_blockmesh.py`, run on the committed
`blockMeshDict.template` at the L3 level, produces a `blockMeshDict` **byte-identical** (`cmp`)
to the one `checkMesh` returned `Mesh OK` on. The record above therefore describes the mesh
these committed bytes actually generate, not a mesh made by a script that has since drifted.
