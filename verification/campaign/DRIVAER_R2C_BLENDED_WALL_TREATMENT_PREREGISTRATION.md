# DRIVAER R2c — BLENDED WALL TREATMENT on the EXISTING coarse and medium meshes

**Status: FROZEN ON COMMIT. No compute has run. Awaiting cfd-supervisor check 4.**
Rung id `R2c`. Two solves, no re-meshing. 2026-09-12, cfd.

## 0. WHY THIS ARM EXISTS — THE MOTIVATION, DECLARED, AT THE TOP

**We saw a number, we did not like it, and we proposed a solution.** Sanaa, in her own
words 2026-09-12: *"Weve seen the number, we didnt like it and we thought of a solution…
I am more convice by the model swap… just because something was frozen does mean it cant
change, we are still learning."*

That sequence is legitimate **because it is declared here and because every prediction
below is written before the solver starts.** Hiding the motivation would be the defect;
having it is not. Specifically:

- This arm was motivated by the **Y1 wall-admissibility cap** on the original arm —
  layered y⁺ 481.565 on coarse, outside [30,300].
- **THE ORIGINAL ARM'S VERDICTS ARE NOT RETRACTED.** `r2_coarse`'s Cd stays
  `NOT A RESULT`; `r2_medium`'s stays a mixed-wall-treatment Cd; C1's `GATE FAIL` stands;
  C2 keeps running and this does not replace it.
- **NOTHING about `r2_coarse`'s or `r2_medium`'s existing graded mesh records changes.**
  M1/M2/M3/Y1 at `6c0dc716b` are untouched. This arm adds solves; it edits no record.

## 1. THE ONE CHANGE — one line, on the vehicle patches only

In `0.orig/nut`, the `".*"` block (which is every vehicle patch — the 47 the forceCoeffs
function object integrates):

```
-        type            nutkWallFunction;
+        type            nutUSpaldingWallFunction;
```

`nutkWallFunction` is a **high-Re log-layer** wall function: it assumes the first cell
centre sits in the log layer and is invalid outside it. `nutUSpaldingWallFunction`
applies **Spalding's law of the wall, which is continuous from the viscous sublayer
through the buffer layer to the log layer** — the standard y⁺-insensitive ("automatic")
wall treatment. That is the whole hypothesis.

**WHAT IS DELIBERATELY NOT CHANGED, AND WHY — the value of this arm is that ONE thing
moved:**
- `floorNoSlip` keeps `nutkWallFunction`. It is not a vehicle patch and contributes no
  force to Cd. Declared, not overlooked.
- `k` keeps `kqRWallFunction` — a zero-gradient condition, valid at any y⁺.
- `omega` keeps `omegaWallFunction` — OpenFOAM's already blends Menter's viscous and
  log-layer forms. **`nut` was the only non-blended limb in the case.**
- Schemes, relaxation, every other BC, decomposition, `endTime` 2000, the forceCoeffs
  constants and patch list: **byte-identical**, proven by `diff` into
  `THE_ONE_CHANGE.diff` in each run root.
- Both levels use the **existing meshes**, `constant/polyMesh` symlinked, not rebuilt and
  not copied.

## 2. GATE B1 (PRIMARY) — y⁺ INSENSITIVITY, and this is better than a reference check

A blended wall treatment **claims y⁺ insensitivity**. We hold two meshes whose layered
y⁺ differ by **2.076×** (481.565 coarse, 232.027 medium). That is a ready-made
discriminator and it needs no reference at all.

**B1: `|Cd_coarse − Cd_medium| / mean(Cd) ≤ 0.10`.**

**Derivation, fixed before either number exists:**
1. **0.10 is the frozen grader's own `CD_BAND_REL`** — a constant already in
   `grade_drivaer.py`, not a number invented for this gate.
2. **It admits pure grid error without being generous.** Linear refinement ratio
   r = 1.7397 (186,709 → 983,106 cells); at second order the coarse−medium spread is
   (r²−1) = **2.03 × medium's own discretisation error**. A 10 % spread therefore
   corresponds to a medium-level error of **4.93 %** — a reasonable figure for a
   983 k-cell RANS on a detailed production car. Tighter than 10 % would fail a
   correctly-blended pair on grid error alone.
3. **THE GATE IS ASYMMETRIC AND THAT IS REGISTERED, NOT DISCOVERED LATER.** Passing is
   evidence of y⁺ insensitivity. **Failing is evidence of y⁺ sensitivity OR of grid error
   larger than assumed, and two levels cannot separate them.** No third level exists and
   none is authorised here.

## 3. GATE B2 (THE CLEAN DISCRIMINATOR) — same mesh, one line apart

B1 confounds wall model with grid. **B2 does not.** `r2_coarse` blended and `r2_coarse`
non-blended share the **identical mesh, identical everything, one line of difference**.

**B2: blending is ACTIVE iff `|Cd_blended − Cd_nonblended| / Cd_nonblended` exceeds
2 × the non-blended run's own trailing-200 plateau excursion**, both read from the same
`coefficient.dat` reader. The multiplier 2 and the window 200 are fixed here; the noise
figure is the run's own, measured at `endTime` 2000 by the frozen instrument. (For scale:
that excursion read 1.599 % at iteration 1013 — **this is a scale note, not the
threshold**, which is computed at 2000.)

**If B2 shows no change, blending does nothing at y⁺ 481.6 and B1's agreement — if it
agrees — means nothing.** B2 is the limb that stops a null result being read as a pass.

## 4. GATE B3 (REPORTED, NOT PRIMARY) — reference agreement

`|Cd − 0.2758368| ≤ 0.10 × 0.2758368` on each level, the frozen `CD_BAND_REL`. DrivAerML
is a **CODE reference, rank 2, NOT experiment**; a pass carries the disavowal.

## 5. THE FOUR OUTCOMES, REGISTERED IN ADVANCE SO NONE CAN BE EXPLAINED AFTERWARDS

1. **B1 agrees AND B3 passes** → the wall treatment was the defect and DrivAer has a
   defensible Cd. **This also REPAIRS THE TRIPLE'S BLOCKER**: the verified reason a
   Roache triple was invalid here is that y⁺ ∝ h_surf moved the wall model on every
   refinement. A y⁺-insensitive family does not. **Sanaa's stated next step — the fine
   mesh — becomes legitimate at that point, and only at that point.**
2. **B1 agrees, B3 fails on both** → the wall model is now consistent and the boundary
   layer is under-resolved. **Blending fixes validity; it does not add cells.** A real
   finding, not a failure.
3. **B1 disagrees** → blending does not rescue this geometry at these y⁺. The **19.65 %
   of wetted area on 16 unlayered patches at y⁺ 556.6** is then the binding problem and
   the mesh route is the only route.
4. **Either solve fails completion or plateau** → **`NOT A RESULT`** by rule 4 and rule 5
   limb 1, no exceptions, with drift reported at 8 window lengths as always. **A plateau
   is not a flat spell.**

## 6. Cost — at 4 ranks per level, the rank count these meshes are decomposed for

From each level's **own** `log.simpleFoam`, measured, not extrapolated:

| level | CPU s/iter/rank | 2000 iters, 4 ranks | peak memory |
|---|---|---|---|
| coarse (186,709 cells) | 1.904 | **254 core-min** CPU-held | 0.45 GiB |
| medium (983,106 cells) | 6.073 | **810 core-min** CPU-held | 1.64 GiB |
| **total** | | **1,064 core-min CPU-held = 17.7 core-h → $0.909 DERIVED, NOT MEASURED** | |

At tonight's measured efficiency (8.8 % coarse, 12.2 % medium) the gross figures are
**2,891 and 6,661 core-min**, 12.0 h and 27.8 h wall. **Contention is named separately
and never absorbed into a ratio.** No re-meshing: zero mesh cost.

**One expected cost this registration does not pretend to have measured:**
`nutUSpaldingWallFunction` solves Spalding's law by Newton iteration per wall face, so a
small per-iteration increase over `nutkWallFunction` is expected. **Unmeasured; it will
be reported as measured at completion, not assumed away.**

**NO CAP KILLS ANYTHING.** These are predictions scored at completion under rule 12. The
MemAvailable refusal in `launch_r2_solve.sh` stays armed as a physics guard.

## 7. What each arm waits on

- **Coarse: nothing.** 0.45 GiB, launchable on signature.
- **Medium: the existing non-blended medium solve must stop first** — its 4 ranks are
  producing the capped Cd and it has ~27 h left. **That stop is a permission decision
  belonging to the human; this lane has been denied it once, will not retry it, and will
  not ask any other agent to perform it.** Medium queues behind that stop and launches
  into the freed ranks.

## 8. Grading path — LITERAL HASHES

| instrument | sha256 |
|---|---|
| `cases/navier_class/DRIVAER/grade_drivaer.py` | `6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7` |
| `cases/navier_class/DRIVAER/mesh/launch_r2_solve.sh` | `60074739b918ce76089818607064ee0f642e365da3d24b991505b72b4afb668d` |
| `cases/navier_class/DRIVAER/mesh/watch_grade_r2.sh` | `aaa727abc77e8091fd0dd07be44e16c2f70429a5f3aac4d92514038e8460156d` |
| `verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json` | `bb504af34ed077f120526771e4852d82890af2f511c907cf36956acf72238c72` |
| control `r2_coarse/0.orig/nut` (the file the one line changes) | *hashed at stage time into each run root's `THE_ONE_CHANGE.diff`* |

Re-computed and compared before any verdict is believed; a mismatch is a REFUSAL.
