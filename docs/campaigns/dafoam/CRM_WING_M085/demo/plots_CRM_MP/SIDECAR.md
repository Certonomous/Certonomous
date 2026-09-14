# SIDECAR — CRM wing Mach 0.85, act folder (`plots_CRM_MP`)

Built 2026-09-14 with **zero solver compute** and nothing written into any run tree.
Plot library **v2**; ParaView per convention — white ground, no orientation triad, one
quarter-height colour bar titled by symbol and unit, **no text of any kind on any
image**. The words live in `README.md` and in the act.

**🔴 THE OPTIMISATION IS `PENDING`.** No design iteration has ever completed in this
item. Every figure is the **baseline** geometry of the published DAFoam `CRM_Wing`
tutorial at three trimmed lift conditions, M 0.8497, 579,072 cells. Nothing is
optimised, improved, or a before/after.

## 🔴 `cl06`'s CONVERGED FIELD IS STORED AT TIME `0.0001`, AND IT IS PROVEN CONVERGED

`mp04` and `mp05` were read at **t = 2000**; `mp06` at **t = 0.0001**. That asymmetry is
a flag, not a detail, so it was **proved from disk before the panel was drawn** rather
than taken on assurance.

| case | time | cells | wall-adjacent `p` min → max (Pa) | file mtime UTC |
|---|---|---|---|---|
| mp04 | 2000 | 29,137 | 98,997 → 120,020 | 01:33:59 |
| mp05 | 2000 | 29,137 | 98,044 → 120,269 | 01:38:34 |
| **mp06** | **0.0001** | **29,137** | **97,185 → 120,303** | **01:43:09** |
| mp06 | 0 | — | **uniform 101,325** | 01:11:51 |

*(internal field of `processor0`, one rank of twenty — a like-for-like slice, not the
whole wing)*

1. **The field is not the initial state.** `mp06/0.0001` is a *nonuniform* field with a
   23.1 kPa spread, and the spread widens monotonically with incidence across the three
   conditions — **21.0 / 22.2 / 23.1 kPa** at α = 1.32° / 2.11° / 2.88°, which is what
   rising angle of attack does. `mp06/0` is a **uniform 101,325 Pa** with no cell list
   at all. These are not the same object.
2. **The write came after the primal, not before it.** The three writes are strictly
   ordered **01:33:59 → 01:38:34 → 01:43:09**, four to five minutes apart — three
   sequential primals — and `cl06`'s is the **last**, **31 minutes after its own initial
   condition** at 01:11:51. An initial state cannot be written last.

**Why `2000` is absent for `cl06`:** the adjoint **renamed** the directory when it reset
the solver clock — DAFoam resets `runTime` for the adjoint and the converged state
travels with it. It is **not** `purgeWrite` (which is `0` in this case, so nothing is
deleted) and **not** a kill mid-write: the files inside carry the primal's own
completion timestamp and only the parent directory's mtime changed.

**The assertion was widened, but not to let a wrong timestep through.** The driver now
takes the latest non-zero time the reader offers and **refuses unless exactly one
non-zero time exists**, so an initial condition still cannot be drawn and labelled the
answer. That original refusal — *"t = 2000 is not among the reader's times [0.0001]"* —
is the only reason this was caught at all. **Treat any case directory of a live run as
mutable and re-check the reader's times immediately before each draw.**

## The panels

| Figure | What it is |
|---|---|
| `crm_mesh_wing.png` | the wing wall patch **as meshed** — all three conditions share this mesh |
| `crm_mesh_symmetry.png` | a symmetry-plane cut of the volume mesh, 14,144 cells in the plane |
| `crm_p_cl04.png`, `crm_p_cl05.png`, `crm_p_cl06.png` | wall pressure at the three conditions, **same camera, one shared colour range** |

**The shared range is the wall's, not the volume's, and that is a correction worth
recording.** `GetComponentRange` on the extracted surface first returned **40,803 to
153,352 Pa** — the volume's range, carrying the shock and the stagnation point — and
painting the wall on that ramp squeezed every panel into its middle third; the colour
control refused at **6.1× on an 8× floor**. The range is now **fetched from the wall
surface actually being drawn**, at the 2nd/98th percentile, the same display-window
convention every other folder here uses. Ends are clamped; nothing is removed from the
data. Measured controls after the fix: **11.9×, 13.3×, 15.1×** interior.

`p` is in **Pa** — `DARhoSimpleCFoam` is compressible — and the bar is titled from the
field's own `dimensions` header rather than assumed. **`C_p` is not written anywhere in
this tree** (the only function object is `forces`); if it is wanted it must be derived
in a Calculator from `p0 = 101325 Pa`, `T0 = 300 K`, `U0 = 295 m/s`,
`ρ = 1.17682 kg/m³`, `q = ½ρU² = 51,213 Pa`, **and the sidecar must then say it was
derived rather than written by the solver**.

## Read-only, on a live run

The three cases are read **decomposed** — nothing reconstructed, nothing written into
any tree — and each case's `constant/polyMesh` is fingerprint-asserted unchanged
afterwards. The adjoint is live and **does** touch these directories: it writes
`dRdWColoring_*.bin` into them and renames time directories. `mp04` and `mp05` are
expected to be renamed the same way in turn; nothing is destroyed, but **do not depend
on a time being called `2000`**.
