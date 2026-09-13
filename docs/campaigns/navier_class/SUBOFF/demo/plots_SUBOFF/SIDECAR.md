# SIDECAR — SUBOFF drift-sweep demo plot folder (`plots_SUBOFF`)

Built 2026-09-13 from what was on disk at the time, with **zero solver compute** and
**nothing written into any run tree**. Drawn with plot library **v2**
(`docs/plot_orders/README_PLOT_LIBRARY_V2.md`): math only on every figure, no
titles, no verdict words, and the ParaView panels white-ground, triad-free,
one quarter-height colour bar, nothing written on the image.

## 🔴 THE WHOLE FOLDER IS `PENDING`

**All seven sweep points were STILL RUNNING** when this was built — between about
2,450 and 2,640 of a registered `endTime` 3000 — and the `SUBOFF_L1M_BETA_P00` and
`SUBOFF_L1M_MESH` rows of `demo3d_render_common.CASE_FACTS` own **exactly one
verdict word, `PENDING`**, so `assert_stamp` refuses a `PASS`, a `GATE FAIL` or a
`NOT A RESULT` on any figure of this act before a pixel is drawn.

**NO DERIVATIVE AND NO NEUTRAL POINT IS COMPUTED HERE, and neither will be until all
seven points land.** `Y_v'` and `N_v'` are least-squares slopes over the five points
`|β| ≤ 8` (registration §4.1); fitting them to unfinished points would be a number
that changes under its own feet. The `Y'` and `N'` against `β` figures show the
**preliminary window means only**, and they are labelled as the quantity, never as a
derivative.

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

## 🔴 A PRELIMINARY OBSERVATION THAT IS ESCALATED, NOT RESOLVED HERE

The preliminary window means (last 300 iterations of each point) are:

| β [deg] | v' | Y' | N' |
|---|---|---|---|
| −12 | −0.20791 | −1.9463e-04 | +5.4774e-04 |
| −8 | −0.13917 | −1.8194e-04 | +3.2193e-04 |
| −4 | −0.06976 | −9.830e-05 | +1.5492e-04 |
| 0 | 0 | **+1e-08** | **+1e-08** |
| +4 | +0.06976 | +9.829e-05 | −1.5492e-04 |
| +8 | +0.13917 | +1.8192e-04 | −3.2194e-04 |
| +12 | +0.20791 | +1.9443e-04 | −5.4774e-04 |

**The β = 0 symmetry check (§4.3) passes with enormous margin**: |Y'| and |N'| are
**1e-08** against a registered threshold of **1e-4**. The mirror seam is sound, and
that check is the one thing a half mesh could never have provided.

**Two things about the other six rows are stated plainly rather than smoothed.**

1. **The magnitude is about 25× below Roddy's line.** At β = +12°, `Y_v'·sin β`
   would be **−4.784e-03**; the measured value is **+1.94e-04**.
2. **The sign is the one §4.2 registered IN ADVANCE as evidence that the bookkeeping
   or the solve is inverted**, not as a bad answer to the physics question: β > 0
   gives `Y' > 0`, i.e. a positive `Y_v'`, which is anti-damping.

**A candidate mechanism, measured and named, and NOT a verdict.** The lateral
boundary condition in `0/U` is `farfield { type slip; }`. The inlet does impose the
cross-flow correctly — `BETA_p12`'s `SOLVE_MANIFEST.json` gives
`U_inlet_mesh = (3.2708140680, 0, 0.6952329922)` and `v_prime_sin_beta = 0.20791` —
but a slip lateral boundary constrains the flow to be tangential to those planes,
which is a route by which an imposed cross-flow is suppressed and the body sees
nearly axial flow. `Y'` at β = +12° has been **flat at 1.944e-04 since iteration
600**, so this is a converged small number rather than a transient one.

**This is a PRELIMINARY reading by a plotting lane on unfinished runs. It is
reported to the supervisor and is not graded, not fitted and not resolved here.** It
is written down now, before the sweep lands, so that it cannot later look like a
conclusion reached after seeing the answer.

## Per figure

| Figure | What it is | Source |
|---|---|---|
| `suboff_yprime_history.png` | `Y'` against iteration for all seven points | `BETA_*/postProcessing/forces/0/force.dat`, `total_z` |
| `suboff_nprime_history.png` | `N'` against iteration for all seven points | `BETA_*/postProcessing/forces/0/moment.dat`, `total_y` |
| `suboff_yprime_vs_beta.png` | preliminary `Y'` against β, with `Y_v'·sin β` and its ±4 % band | the seven force files + §5 |
| `suboff_nprime_vs_beta.png` | preliminary `N'` against β, with `N_v'·sin β` and the same ±4 % interval — **which is NOT a gate for `N_v'`** | the seven moment files + §5 |
| `suboff_residuals.png` + `_f10 … _f75` | the residual-evolution series on ONE set of axes, from the most advanced point | that point's `postProcessing/residuals/0/solverInfo.dat` |
| `suboff_l2_corner.png` | the L2 zero-incidence corner's drag history, 3000 iterations, `rc = 0`, finished 2026-09-13T17:21:32Z | `SUBOFF_A1/SOLVE_L2/postProcessing/forceCoeffs` |
| `suboff_mesh_l1m.png` | the **L1 mirror's own mesh** on hull and sail, 399,954 faces of a 6,537,226-cell domain | `MESH_FULL_L1M/constant/polyMesh` |
| ~~`suboff_p_surface.png`~~, ~~`suboff_umag_symmetry.png`~~, ~~`suboff_umag_wake.png`~~ | **NOT PRODUCIBLE YET — see below.** They are the first thing the final version adds | — |

## 🔴 NO FIELD PANEL EXISTS YET, AND THE GUARD IS WHAT STOPPED ONE BEING SHIPPED

The three field panels the brief asks for — surface pressure, the symmetry plane and
a wake cross-section — **could not be produced from disk, and blank pictures of them
were refused rather than written.**

**The measurement.** `purgeWrite 2` means the only fields on disk live in
`processor*/<t>`; nothing is reconstructed. Opened as a decomposed case, ParaView's
OpenFOAM reader **lists exactly one timestep, `t = 0.0`**, while correctly reporting
the mesh (6,537,226 cells, asserted) and the six field names (`k nut omega p U
yPlus`). Asking it for `t = 2700` therefore gets the **initial condition**, not the
solution — *a picture captioned as the latest time showing a uniform inlet field is
worse than no picture at all*, and it is exactly the kind of confident-looking wrong
image this lab refuses. Reconstructing the time directory would be **compute AND a
write into seven live graded trees**, so it was not done.

**And it was the GUARD that caught it, twice, not a reading of the log.** The first
run wrote two blank panels and the colour control PASSED on them — at 49.7x and then
at 459,558,697x — because the only ink on the frame was the colour bar, itself a
two-ended ramp, against an all-white negative arm whose spread was exactly zero. **A
ratio test cannot see a blank frame: 0.45 over nothing is still infinitely more than
nothing.** Two clauses now close that in every driver in this repository and both
REFUSE: the positive arm must cover at least 20,000 non-background pixels (the bar
alone is about 4,600), and the negative arm must not have a spread of exactly zero,
because a control that measures nothing is not a control (CLAUDE.md rule 3). The bar
is hidden for both arms. On the re-run the surface panel **refused at 0 pixels**, and
the image produced under the broken guard was **deleted, not shipped**.

`suboff_mesh_l1m.png` is unaffected: it is the mirror's own `constant/polyMesh` read
as a reconstructed case, 170,755 body pixels, and it needs no field at all.

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
