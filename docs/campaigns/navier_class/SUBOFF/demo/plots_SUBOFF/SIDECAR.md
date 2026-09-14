# SIDECAR — SUBOFF drift-sweep demo plot folder (`plots_SUBOFF`)

Built 2026-09-14 from the A1h full-domain drift sweep with **zero solver compute** and
**nothing written into any graded tree**. Drawn with plot library **v2**: math only on
every figure, no titles, no verdict words, and the ParaView panels white-ground,
triad-free, one quarter-height colour bar, nothing written on the image.

## 🔴 THE ACT IS GRADED `NOT A RESULT`

`verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_GRADE/A1H_L1M_GRADE.json`,
written 2026-09-14T00:18:03Z by `cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py`:

> **`"verdict": "NOT A RESULT"`** — *"fitted points failing the strict completion rule:
> [-8, -4, 0, 4, 8]. There is no fit over fewer than the five registered points and no
> degradation to a shorter sweep."*

**All seven points fail, and they fail on every clause**, not on a technicality:

| β [deg] | rc | last `Time` | `endTime` dir | fields missing | complete |
|---|---|---|---|---|---|
| −12 | 1 | 2746 | none | 6 | **no** |
| −8 | 1 | 2791 | none | 6 | **no** |
| −4 | 1 | 2821 | none | 6 | **no** |
| 0 | 1 | 2881 | none | 6 | **no** |
| +4 | 1 | 2806 | none | 6 | **no** |
| +8 | 1 | 2836 | none | 6 | **no** |
| +12 | 1 | 2671 | none | 6 | **no** |

The comparator's own rule-3 plants all **PASS** (force reader, moment reader, age
guard, and a planted slope recovered to 1e-17 inside and outside the band), so this is
a **working instrument refusing**, not a broken one. **Every figure in this folder is a
picture of an incomplete solve.** Nothing here is a result, and nothing here may be
cited as one.

*cfd is applying the owner's §V `endTime` addendum and re-grading. If the verdict
changes, only this page changes — the figures are of the same iterations either way.*

## 🔴 FIVE ITEMS OF THE APPROVED LIST WERE NOT BUILT, AND THE REASON IS THE FROZEN
## REGISTRATION RATHER THAN A PREFERENCE

`SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md` §10, *"WHAT THIS CASE DOES NOT
CLAIM"*, read rather than recalled:

| asked for | why it is not here |
|---|---|
| **Z and M vs α** | This act is a **horizontal-plane drift sweep in β**. §10: *"No vertical-plane result: no `Z`, no `M`, no neutral point — that is A1g's, on a body this one does not have."* The run directories are `BETA_*`. **Drawn instead: `Y'` and `N'` vs β**, the registered channel. |
| **hull/fin split** | §10: *"No hull/fin split: there are no fins on this body."* The mesh agrees — the boundary file carries `hull`, `sail`, `inlet`, `outlet`, `farfield`, `symm`. **Drawn instead: the hull/SAIL split**, which the run's own `forcesHull` and `forcesSail` objects make possible. |
| **`Y_v'`/`N_v'` fit line, neutral point** | §10 forbids the neutral point outright, and **the fit does not exist**: the comparator refused to compute one and returned `NOT A RESULT`. A fit drawn here would be a number this lab was told to produce and its own instrument declined to. |
| **hull Cp vs Huang 1992** | `SUBOFF_R1_bare_hull_zero_incidence.md:17` places surface Cp vs Huang 1992 at rung **R2**, not this act, and no digitised Huang reference is on disk. |
| **family plot, coarse vs medium, with band** | §10: *"No grid convergence, no observed order, no GCI — single level, by construction."* |

## The graded channel is the HORIZONTAL plane, `Y'` and `N'`

Not "Z and M". A vertical-plane result belongs to A1g on a different body, and §9 of
this registration says this act produces **no Z, no M and no neutral point**.
Transcribed from §4.1, which derives the sign convention in full BEFORE compute:

> `Y' = − F_z,mesh / 101.500341` `N' = − M_y,mesh / 432.478763` `v' = sin β`

with `½ρU²L_BP² = 101.500341` and `½ρU²L_BP³ = 432.478763` on
`L_BP = 4.2608602 m`, ρ = 1 kinematic, moment origin (2.013, 0, 0).

## The Roddy numbers are HIS MEASUREMENTS, not ours

From §5, Roddy 1990 DTRC/SHD-1298-08 Table 4, the hull-with-fairwater body named by
its geometry: **`Y_v' = −0.023008`, GATED at ±4 % on [−0.023928, −0.022088]**; and
**`N_v' = −0.015534`, REPORTED AND NOT GRADED** — §5 declines a tighter gate for
`N_v'` because the transferred band errs 13.8 % in our favour there, and gating it
would be fitting a gate to a known-favourable ground. **No reader may cite either
number as a Certonomous result.** On the figures they are drawn as the line
`Y_v'·sin β` (and `N_v'·sin β`) with the ±4 % interval as its band.

## 🔴 `NOT A RESULT` TWICE OVER, AND THE SECOND REASON IS PHYSICS

**Route one, completion.** All seven points were **STOPPED ON THE OWNER'S ORDER** to
free ranks, after a convergence check — **a deliberate stop, not a crash.** They were
healthy when they were stopped. That is why they fail the strict completion rule
(`rc = 1`, no `End`, no `endTime` directory, six fields missing), and it is the first
thing a viewer should be told, because "failed the completion rule" reads as breakage
and this was not breakage.

**Route two, and it is the one that matters: THE FIT IS INVERTED.** §4.2 of the frozen
registration pre-declared, before any number existed, that a **positive** fitted
`Y_v'` means *"the sign convention or the solve is wrong"*. The fit is

> **`Y_v' = +1.327616e-03` against Roddy's `−0.023008`** — inverted in sign and about
> **17× low** in magnitude.

**So A1h produced NO USABLE DERIVATIVE.** The act, if it shows this sweep, is showing
**a well-executed refusal rather than a measurement** — which is this laboratory's
product, but it must be chosen knowingly and not discovered on screen.

**AND THE MECHANISM IS MEASURED, AND IT SITS INSIDE THE FREEZE.** Line 139 of the
registration registers the `farfield` boundary as **`slip`**, on a domain reaching only
**±2.99 m around a 4.356 m body** — a closed duct, which cannot pass the cross-flow the
drift angle injects. The fingerprints are consistent with exactly that and with nothing
else:

* hull and sail disagree in **sign** (at β = +8: hull `F_z` −4.5431e-02 against sail
  +2.6967e-02);
* the hull's inverted force is **~103 % pressure**, with the viscous cross-flow term
  carrying the **correct** sign and **34× too small** to matter.

This lane first recorded the `slip` boundary as a *candidate* mechanism from the `0/U`
file while the runs were still going; the cfd supervisor has since measured the
decomposition above and it is theirs, not an inference of mine.

## What is CLEAN here, and it is worth saying plainly

Three measurements say the mesh and the solve are sound, so the inversion is not
numerical noise and not a seam artefact:

1. **The mesh is genuinely FULL, not a half model** — the mirrored L1, 6,537,226 cells,
   and the `symm` patch carries **nFaces 0**. A1h exists precisely to escape A1f's half
   mesh, where a `symmetryPlane` forbids the z-component a drift sweep needs.
2. **The β = 0 symmetry check passes at `|Y'| = 1.45e-09`** against a 1e-4 gate, and the
   ±β pairs are antisymmetric to about 0.1 %. That check is the one thing a half mesh
   could never have provided.
3. **The `k` bounding is benign clipping**, not a DrivAer-class failure: **0 cells at the
   bound** out of 6,537,226, excursion **0.82 % of the mean**, stationary for 2,300
   iterations. If bounding appears anywhere in these figures, that is its reading.

## Per figure

| Figure | What it is |
|---|---|
| `suboff_yprime_vs_beta.png`, `suboff_nprime_vs_beta.png` | preliminary window means against β, with Roddy's `Y_v'·sin β` (and `N_v'·sin β`) and the ±4 % interval as its band. **No fit line is drawn**, because no fit exists |
| `suboff_yprime_split_vs_beta.png`, `suboff_nprime_split_vs_beta.png` | the **hull / sail** split of each, from the run's own `forcesHull` and `forcesSail` |
| `suboff_yprime_history.png`, `suboff_nprime_history.png` | all seven points against iteration, on common axes |
| `suboff_history_b*.png` | each point's own `Y'` and `N'` history — seven figures, because the seven points stopped at seven different iterations |
| `suboff_residuals_b*_f10 … _f75`, `suboff_residuals_b*.png` | the residual-evolution series **per point**, five frames each on that point's own pinned axes |
| `suboff_residuals.png`, `_f10 … _f75` | the same series for the most advanced point, kept under the plain name |
| `suboff_l2_corner.png` | the L2 zero-incidence corner's drag history, 3000 iterations, `rc = 0`, finished 2026-09-13T17:21:32Z — **the only complete solve anywhere in this folder** |
| `suboff_mesh_l1m.png` | the **coarse mirror mesh** on hull and sail, 399,954 faces of a 6,537,226-cell domain |
| `suboff_mesh_sail_cut.png` | a cut through the sail, framed on it, showing the cells across it and the wall layers |
| `suboff_p_side_b*.png`, `suboff_p_top_b*.png` | surface pressure, side and from above, at β = 0, ±8, ±12 — one shared display window across all five |
| `suboff_umag_mid_b*.png` | `\|U\|` on the mid-depth plane y = 0, same five angles, one shared window |
| `suboff_wake_stern_b*.png` | cross-sections 0.30 m aft of the stern, at β = 0 and +12 |
| `suboff_wake_sail_bp12.png` | a cross-section aft of the sail at β = +12 |
| `suboff_streamlines_bp12.png` | streamlines over the sail at β = +12, coloured by speed |
| `suboff_q_bp12.png` | the Q-criterion iso-surface of the sail vortices at β = +12 |

## The field panels exist now, and NOTHING WAS RECONSTRUCTED

The brief allowed reconstructing each point's last written time into a symlinked
scratch. **It turned out to be unnecessary, which is strictly better**: ParaView reads
the DECOMPOSED case directly, read-only, once `CaseType` is set **and the pipeline
INFORMATION is refreshed**.

**That refresh is the whole bug behind the blank panels of the first attempt.**
Without it the reader reports `TimestepValues == [0.0]` on a case whose processor
directories plainly hold t = 2865 and 2880 — so a panel asked for "the latest time"
silently drew the initial condition, or nothing at all. The driver now calls
`Refresh()` and `UpdatePipelineInformation()`, takes the maximum time above zero, and
**asserts that time is in `TimestepValues` before a pixel is drawn**. The mesh is
asserted at 6,537,226 cells and every requested field asserted present on the same
read.

Each panel still carries the planted colour control at the 8x margin **and** the two
clauses added after the blank-frame failure: at least 20,000 non-background pixels on
the positive arm, and a negative arm whose spread is not exactly zero.

## Reading seven LIVE runs without disturbing them

`purgeWrite 2` means the only fields on disk live in `processor*/<t>`; **nothing is
reconstructed, and reconstructing would be compute AND a write into a live graded
tree**, so neither was done. The processor directories are symlinked into a scratch
root, the `.foam` stub is created THERE, and ParaView reads the decomposed case. The
time chosen is the latest that carries `U` **on every rank** — taking rank 0's latest
alone would read a directory another rank has not finished writing. The mesh identity
is still asserted against the 6,537,226-cell record, so a wrong mesh still refuses.

## What the final version, at about 01:00Z, will add

The seven points reach `endTime` 3000; the window means become final; `Y_v'` and
`N_v'` are fitted over `|β| ≤ 8` and graded against §5; the sign clause §4.2 is
applied by the comparator rather than observed by a plotting lane; and — once a
reconstructed time directory exists — **the three field panels are rendered for the
first time**, from a solution rather than from an initial condition.
